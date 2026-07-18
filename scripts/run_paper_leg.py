#!/usr/bin/env python3
"""Batch paper-leg settlement.

Two batches, both Tier 1 (data_gate.load_operational):

1. LEDGER batch — trades_log snapshot picks -> data/derived/paper_leg.parquet
   (rec_key = pick_date|SYMBOL|1; seq=1 ASSUMPTION, DECISIONS.md RULING 1).
2. REC-UNIVERSE batch — all rec-file recs in the live window, last generation
   per (data_date, symbol) -> data/derived/paper_leg_recs.parquet (real
   rec_key data_date|SYMBOL|seq). Feeds the RECONSTRUCTED overlay scope:
   inferred vetoes have no ledger row, so grading them needs the full
   universe settled (pre-log window ruling, DECISIONS.md).

OHLC: newest data/market/ohlc parquet (UNADJUSTED, amended RULING 4h), else
raw-snapshot backup CSV. Dividends from data/market/actions feed credits.

Settlement gate (Option 1 ruling): before writing, reconcile paper-leg entry
prices vs trades_log-recorded fills for entered trades and report the
distribution.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))
sys.path.insert(0, str(REPO / "scripts"))
import data_gate
import paper_leg

SNAPSHOT = REPO / "data" / "legacy_snapshot" / "trades_log_ee7ad13.csv"
RECS_DIR = REPO / "data" / "legacy_snapshot" / "recs"
OUT = REPO / "data" / "derived" / "paper_leg.parquet"
OUT_RECS = REPO / "data" / "derived" / "paper_leg_recs.parquet"


def _latest_ohlc_snapshot() -> str | None:
    """Newest sanctioned OHLC: data/market fetch first (amended RULING 2),
    else prices_eod_backup_*.csv from raw snapshots (RULING 3 amendment)."""
    market = sorted((REPO / "data" / "market" / "ohlc").glob("ohlc_*.parquet"))
    if market:
        return str(market[-1])
    raw_root = REPO / "data" / "sealed" / "raw"
    if not raw_root.is_dir():
        return None
    candidates = sorted(raw_root.glob("*/prices_eod_backup_*.csv"))
    return str(candidates[-1]) if candidates else None


def _latest_actions() -> str | None:
    acts = sorted((REPO / "data" / "market" / "actions").glob("actions_*.parquet"))
    return str(acts[-1]) if acts else None


def _read_any(path: str) -> pd.DataFrame:
    return pd.read_parquet(path) if path.endswith(".parquet") else pd.read_csv(path)


def load_settlement_ohlc(path: str, ledger: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Load snapshot OHLC through the Tier 1 door via the settlement join.

    The panel is restricted to rec symbols and live-window dates and tagged
    with the rec_keys it settles (rec_key-joinable shape) before passing
    data_gate.load_operational() — a generic panel would be rejected.
    """
    panel = _read_any(path)
    panel["date"] = pd.to_datetime(panel["date"])
    panel = panel.loc[panel["date"] >= data_gate.LIVE_WINDOW_START,
                      ["symbol", "date", "open", "high", "low", "close"]]
    keys = ledger[["symbol", "rec_key"]]
    joined = panel.merge(keys, on="symbol", how="inner")
    if joined.empty:
        return {}
    gated = data_gate.load_operational(joined, "date", source=path)
    return {s: g.sort_values("date").drop_duplicates("date")
            for s, g in gated.groupby("symbol")}


def load_rec_universe() -> pd.DataFrame:
    """Live-window rec universe, LAST generation per (data_date, symbol)
    (reconstruction ASSUMPTION, DECISIONS.md), Tier 1 gated."""
    from build_workspace import load_rec_files

    recs = load_rec_files(RECS_DIR)
    if recs.empty:
        return recs
    # The ledger's pick_date aligns with the rec's GENERATED date (a rec
    # generated on X enters X+1), so generated_date anchors both settlement
    # and reconstruction; rec_key keeps data_date|SYMBOL|seq (RULING 1).
    recs["pick_date"] = pd.to_datetime(recs["generated_date"])
    recs = recs.loc[recs["pick_date"] >= data_gate.LIVE_WINDOW_START]
    # One generated date can carry picks from several data dates; per
    # (generated_date, symbol) keep the freshest data_date (ASSUMPTION).
    recs = (recs.sort_values("data_date")
            .groupby(["pick_date", "symbol"], as_index=False).tail(1))
    recs = recs.rename(columns={"target_1": "t1", "target_2": "t2"})
    keep = recs[["rec_key", "pick_date", "symbol", "stop_loss", "t1", "t2"]]
    return data_gate.load_operational(keep, "pick_date", source=str(RECS_DIR) + "/")


def settle_batch(
    recs: pd.DataFrame,
    ohlc_by_symbol: dict[str, pd.DataFrame],
    div_by_symbol: dict[str, pd.DataFrame],
) -> pd.DataFrame:
    """Settle rows with rec_key/pick_date/symbol/stop_loss/t1/t2 columns."""
    rows = []
    for _, r in recs.iterrows():
        rec = {
            "rec_key": r["rec_key"], "pick_date": r["pick_date"],
            "stop_loss": r["stop_loss"], "t1": r["t1"], "t2": r.get("t2"),
        }
        ohlc = ohlc_by_symbol.get(r["symbol"])
        result, reason = None, None
        if not ohlc_by_symbol:
            reason = "no sanctioned OHLC coverage in the live window"
        elif ohlc is None:
            reason = "symbol absent from sanctioned OHLC source"
        else:
            entry = paper_leg.resolve_entry(rec, ohlc)
            if entry is None:
                reason = (f"no OHLC session after pick_date "
                          f"(coverage ends {ohlc['date'].max().date()})")
            else:
                result = paper_leg.settle(
                    {**rec, **entry}, ohlc, dividends=div_by_symbol.get(r["symbol"])
                )
                if result["exit_rule"] == "UNSETTLED":
                    reason = (f"position still open at end of OHLC coverage "
                              f"({result['sessions_held']} sessions held)")
        if result is None:
            result = {
                "rec_key": rec["rec_key"], "entry_date": None, "entry_price": None,
                "exit_date": None, "exit_price": None, "r_multiple": None,
                "dividend_credit": 0.0, "exit_rule": "UNSETTLED", "sessions_held": 0,
                "flag_ambiguous_same_bar": False, "flag_halt_carry": False,
                "flag_entry_assumed": False, "flag_ex_date": None,
            }
        result["unsettled_reason"] = reason
        result["symbol"] = r["symbol"]
        result["pick_date"] = r["pick_date"]
        result["stop_loss"] = float(r["stop_loss"])  # kept for fill-based R
        # True = system confirmed entry; False = AUTO_EXPIRED settled with an
        # assumed entry (separate ASSUMED_ENTRY scope); None = unknown (universe)
        result["system_entered"] = r.get("system_entered")
        rows.append(result)
    return pd.DataFrame(rows)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--snapshot", default=str(SNAPSHOT))
    ap.add_argument("--ohlc", default=_latest_ohlc_snapshot(),
                    help="CSV/parquet: symbol,date,open,high,low,close (UNADJUSTED)")
    args = ap.parse_args()

    raw = pd.read_csv(args.snapshot)
    ledger = data_gate.load_operational(raw, "pick_date", source=args.snapshot)
    ledger["rec_key"] = (
        ledger["pick_date"].dt.strftime("%Y-%m-%d") + "|" + ledger["symbol"].astype(str) + "|1"
    )
    ledger = ledger.rename(columns={"target_1": "t1", "target_2": "t2"})
    ledger["system_entered"] = ledger["exit_reason"] != "AUTO_EXPIRED_5_SESSIONS"

    universe = load_rec_universe()
    all_symbols = pd.concat([ledger[["symbol", "rec_key"]], universe[["symbol", "rec_key"]]])

    ohlc_by_symbol: dict[str, pd.DataFrame] = {}
    ohlc_max_date = None
    if args.ohlc:
        ohlc_by_symbol = load_settlement_ohlc(args.ohlc, all_symbols)
        if ohlc_by_symbol:
            ohlc_max_date = max(g["date"].max() for g in ohlc_by_symbol.values())

    actions_path = _latest_actions()
    div_by_symbol: dict[str, pd.DataFrame] = {}
    if actions_path:
        acts = pd.read_parquet(actions_path)
        div_by_symbol = {s: g for s, g in acts.groupby("symbol")}

    # ── Settlement gate (Option 1 ruling): entry reconciliation before writing.
    entered = ledger.loc[ledger["exit_reason"] != "AUTO_EXPIRED_5_SESSIONS"]
    divs = []
    for _, r in entered.iterrows():
        ohlc = ohlc_by_symbol.get(r["symbol"])
        if ohlc is None:
            continue
        e = paper_leg.resolve_entry({"pick_date": r["pick_date"]}, ohlc)
        if e is None:
            continue
        pct = (e["entry_price"] - float(r["entry_price"])) / float(r["entry_price"]) * 100
        divs.append({"rec_key": r["rec_key"], "ledger_fill": float(r["entry_price"]),
                     "paper_entry": e["entry_price"], "pct": pct})
    if divs:
        d = pd.DataFrame(divs)
        print(f"[gate] entry reconciliation, {len(d)} entered trades: "
              f"mean {d.pct.mean():+.2f}% | median {d.pct.median():+.2f}% | "
              f"min {d.pct.min():+.2f}% | max {d.pct.max():+.2f}%")
    else:
        print("[gate] entry reconciliation: no entered trades with OHLC coverage")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    print(f"[paper-leg] OHLC source: {args.ohlc or 'NONE'}"
          + (f" (coverage max {ohlc_max_date.date()})" if ohlc_max_date is not None else ""))

    out = settle_batch(ledger, ohlc_by_symbol, div_by_symbol)
    out.to_parquet(OUT, index=False)
    settled = (out["exit_rule"] != "UNSETTLED").sum()
    print(f"[paper-leg] ledger: {len(out)} recs -> {settled} settled -> {OUT}")
    for _, r in out.loc[out["exit_rule"] == "UNSETTLED"].iterrows():
        print(f"  UNSETTLED {r['rec_key']}: {r['unsettled_reason']}")

    if not universe.empty:
        out_u = settle_batch(universe, ohlc_by_symbol, div_by_symbol)
        out_u.to_parquet(OUT_RECS, index=False)
        settled_u = (out_u["exit_rule"] != "UNSETTLED").sum()
        print(f"[paper-leg] rec universe: {len(out_u)} recs -> {settled_u} settled -> {OUT_RECS}")
        for _, r in out_u.loc[out_u["exit_rule"] == "UNSETTLED"].iterrows():
            print(f"  UNSETTLED {r['rec_key']}: {r['unsettled_reason']}")


if __name__ == "__main__":
    main()

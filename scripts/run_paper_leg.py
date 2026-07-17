#!/usr/bin/env python3
"""Batch paper-leg settlement over the ledger snapshot.

Reads the fills/ledger snapshot (Tier 1, via data_gate.load_operational),
resolves entries per RULING 4a, settles each rec against daily OHLC if an
OHLC file is provided, and writes data/derived/paper_leg.parquet.

OHLC source: --ohlc <csv> with columns symbol,date,open,high,low,close
(ADJUSTED series — RULING 4h). Without it, recs are written as UNSETTLED;
no OHLC flat export exists in the sanctioned snapshot scope yet (the
production prices live in the DB, which is off-limits).

rec_key: pick_date|SYMBOL|1 for ledger rows (seq=1 ASSUMPTION — the ledger
does not record the generation; see governance/DECISIONS.md RULING 1).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))
import data_gate
import paper_leg

SNAPSHOT = REPO / "data" / "legacy_snapshot" / "trades_log_ee7ad13.csv"
OUT = REPO / "data" / "derived" / "paper_leg.parquet"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--snapshot", default=str(SNAPSHOT))
    ap.add_argument("--ohlc", default=None, help="CSV: symbol,date,open,high,low,close (adjusted)")
    args = ap.parse_args()

    raw = pd.read_csv(args.snapshot)
    ledger = data_gate.load_operational(raw, "pick_date", source=args.snapshot)
    ledger["rec_key"] = (
        ledger["pick_date"].dt.strftime("%Y-%m-%d") + "|" + ledger["symbol"].astype(str) + "|1"
    )

    ohlc_by_symbol: dict[str, pd.DataFrame] = {}
    if args.ohlc:
        panel = pd.read_csv(args.ohlc)
        panel["date"] = pd.to_datetime(panel["date"])
        ohlc_by_symbol = {s: g.sort_values("date") for s, g in panel.groupby("symbol")}

    rows = []
    for _, r in ledger.iterrows():
        rec = {
            "rec_key": r["rec_key"],
            "pick_date": r["pick_date"],
            "stop_loss": r["stop_loss"],
            "t1": r["target_1"],
            "t2": r.get("target_2"),
        }
        ohlc = ohlc_by_symbol.get(r["symbol"])
        result = None
        if ohlc is not None:
            entry = paper_leg.resolve_entry(rec, ohlc)
            if entry is not None:
                result = paper_leg.settle({**rec, **entry}, ohlc)
        if result is None:
            result = {
                "rec_key": rec["rec_key"], "entry_date": None, "entry_price": None,
                "exit_date": None, "exit_price": None, "r_multiple": None,
                "exit_rule": "UNSETTLED", "sessions_held": 0,
                "flag_ambiguous_same_bar": False, "flag_halt_carry": False,
                "flag_entry_assumed": False, "flag_ex_date": None,
            }
        result["symbol"] = r["symbol"]
        result["pick_date"] = r["pick_date"]
        rows.append(result)

    out = pd.DataFrame(rows)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    out.to_parquet(OUT, index=False)
    settled = (out["exit_rule"] != "UNSETTLED").sum()
    print(f"[paper-leg] {len(out)} recs -> {settled} settled, {len(out) - settled} unsettled -> {OUT}")


if __name__ == "__main__":
    main()

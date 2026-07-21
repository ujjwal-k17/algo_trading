#!/usr/bin/env python3
"""Independent OHLC + corporate-actions fetcher (amended RULING 4h / RULING 2).

Fetches UNADJUSTED daily OHLC (auto_adjust=False — the settlement basis that
replicates exit_manager's actual level checks) for exactly the symbols in the
ledger snapshot (not the whole universe), from the live-window start to date,
into data/market/ohlc/ as dated parquet — idempotent per day. Corporate
actions (dividends/splits) for the same symbols go to data/market/actions/,
feeding Ruling h's dividend-credit flags.

Source identity: production's own backup declares price_source=yfinance_adj;
fetching yfinance ourselves obtains production's source independently
(validated 2026-06-24: 250/250, 200 exact, 50 uniform-rescale adjustment-basis
diffs only — see DECISIONS.md).
"""

from __future__ import annotations

import datetime as dt
import sys
import warnings
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[1]
SNAPSHOT = REPO / "data" / "legacy_snapshot" / "trades_log_ee7ad13.csv"
OHLC_DIR = REPO / "data" / "market" / "ohlc"
ACTIONS_DIR = REPO / "data" / "market" / "actions"
START = "2026-06-29"  # live-window start (data_gate.LIVE_WINDOW_START)


def _rec_symbols_from(path: Path) -> set[str]:
    """Symbols out of one rec CSV. These files carry a provenance comment on
    line 1 and the header on line 2; `comment='#'` handles the '#'-prefixed
    form, `skiprows=1` the bare form. Both shapes exist in the corpus."""
    for kwargs in ({"comment": "#"}, {"skiprows": 1}):
        try:
            df = pd.read_csv(path, **kwargs)
        except Exception:
            continue
        if "symbol" in df.columns:
            return set(df["symbol"].dropna().unique())
    return set()


def ledger_symbols() -> list[str]:
    """Ledger symbols ∪ rec-file symbols (still rec-scoped, not the whole
    universe) — inferred-veto grading needs OHLC for recs absent from the
    ledger (pre-log window ruling, DECISIONS.md).

    Reads recs from BOTH `data/legacy_snapshot/recs/` (the frozen snapshot) and
    `data/sealed/raw/<date>/` (where the nightly ingest deposits new recs).
    Reading only the former froze the fetch universe at the snapshot date and
    silently excluded every rec generated after it — DIXON, picked 2026-07-16
    and held live, was never fetched at all (see DECISIONS.md 2026-07-21)."""
    syms = set(pd.read_csv(SNAPSHOT)["symbol"].unique())
    for root in (REPO / "data" / "legacy_snapshot" / "recs",
                 REPO / "data" / "sealed" / "raw"):
        for f in root.rglob("top5_report_data*.csv"):
            syms |= _rec_symbols_from(f)
    return sorted(s for s in syms if isinstance(s, str) and s.strip())


def validate_ohlc(ohlc: pd.DataFrame, expected: list[str]) -> tuple[pd.DataFrame, dict]:
    """Quality gate between fetch and write. Returns (clean_frame, report).

    TRAP 6: a non-empty row count proves nothing. The 2026-07-21 ingest wrote
    544 rows across the right 34 symbols over the right date range with EVERY
    symbol's newest close NaN — it passed every count-based check there was.

    Policy (ASSUMPTION, DECISIONS.md 2026-07-21): a row whose close is null is
    DROPPED, not written. A missing row is honest and `paper_leg`/`build_nav`
    already refuse to approximate over gaps; a NaN close masquerading as a
    fetched observation poisons them silently. Callers must treat a non-empty
    `dropped_null_close` as a signal to re-fetch, not as routine."""
    n_before = len(ohlc)
    null_close = ohlc["close"].isna()
    clean = ohlc.loc[~null_close].copy()
    missing = sorted(set(expected) - set(clean["symbol"].unique()))
    report = {
        "rows_in": n_before,
        "rows_out": len(clean),
        "dropped_null_close": int(null_close.sum()),
        "symbols_expected": len(expected),
        "symbols_present": int(clean["symbol"].nunique()),
        "symbols_missing": missing,
        "newest_date": (str(clean["date"].max())[:10] if len(clean) else None),
    }
    return clean, report


def main() -> None:
    warnings.filterwarnings("ignore")
    import yfinance as yf

    today = dt.date.today().isoformat()
    ohlc_out = OHLC_DIR / f"ohlc_{today}.parquet"
    actions_out = ACTIONS_DIR / f"actions_{today}.parquet"
    if ohlc_out.exists() and actions_out.exists():
        print(f"[fetch] {today} already fetched — idempotent, nothing to do")
        return

    symbols = ledger_symbols()
    tickers = [s + ".NS" for s in symbols]
    data = yf.download(
        tickers, start=START, auto_adjust=False, group_by="ticker",
        progress=False, threads=True,
    )
    frames = []
    for s, t in zip(symbols, tickers):
        try:
            df = data[t].dropna(how="all").reset_index()
        except KeyError:
            print(f"[fetch] WARNING: {s} missing from yfinance", file=sys.stderr)
            continue
        df = df.rename(columns=str.lower)[["date", "open", "high", "low", "close"]]
        df["symbol"] = s
        frames.append(df)
    ohlc = pd.concat(frames, ignore_index=True)

    ohlc, report = validate_ohlc(ohlc, symbols)
    for line in (
        f"[fetch] QUALITY rows {report['rows_in']} -> {report['rows_out']} "
        f"(dropped {report['dropped_null_close']} null-close)",
        f"[fetch] COVERAGE {report['symbols_present']}/{report['symbols_expected']} "
        f"symbols, newest {report['newest_date']}",
    ):
        print(line)
    if report["dropped_null_close"]:
        print(f"[fetch] WARNING: {report['dropped_null_close']} null-close rows dropped — "
              f"re-run to recover them (the file is written WITHOUT them)", file=sys.stderr)
    if report["symbols_missing"]:
        print(f"[fetch] WARNING: {len(report['symbols_missing'])} expected symbols absent: "
              f"{', '.join(report['symbols_missing'][:10])}"
              f"{' …' if len(report['symbols_missing']) > 10 else ''}", file=sys.stderr)
    if ohlc.empty:
        # Refuse to write an empty file over a good one; exit non-zero so
        # launchd records a failure and ingest_health() sees it (TRAP 6).
        print("[fetch] FATAL: no rows survived validation — nothing written", file=sys.stderr)
        raise SystemExit(2)

    OHLC_DIR.mkdir(parents=True, exist_ok=True)
    ohlc.to_parquet(ohlc_out, index=False)

    act_rows = []
    for s, t in zip(symbols, tickers):
        try:
            div = yf.Ticker(t).dividends
        except Exception as exc:
            print(f"[fetch] WARNING: actions failed for {s}: {exc}", file=sys.stderr)
            continue
        for ex_date, amount in div.items():
            if pd.Timestamp(ex_date).tz_localize(None) >= pd.Timestamp("2026-06-01"):
                act_rows.append({"symbol": s, "ex_date": pd.Timestamp(ex_date).tz_localize(None),
                                 "dividend": float(amount)})
    ACTIONS_DIR.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(act_rows, columns=["symbol", "ex_date", "dividend"]).to_parquet(
        actions_out, index=False
    )
    print(f"[fetch] {len(ohlc)} OHLC rows ({ohlc.symbol.nunique()} symbols, "
          f"{ohlc.date.min().date()} -> {ohlc.date.max().date()}) -> {ohlc_out}")
    print(f"[fetch] {len(act_rows)} dividend events -> {actions_out}")


if __name__ == "__main__":
    main()

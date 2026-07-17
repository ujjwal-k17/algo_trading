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


def ledger_symbols() -> list[str]:
    return sorted(pd.read_csv(SNAPSHOT)["symbol"].unique())


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

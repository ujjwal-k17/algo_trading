#!/usr/bin/env python3
"""PIT-clean ADJUSTED price panel for the SPEC-52WH-01 dev window (Stage 1, A4).

Fetches split/bonus-adjusted daily OHLC (yfinance auto_adjust=True — sanctioned
public source) for the PIT-universe symbols, dev window only, and gates every
row through ``data_gate.load`` (research door) before writing
data/workspace/price_panel_52wh.parquet. Adjusted series are used consistently
for BOTH close and the rolling 252d high — the nearness ratio distorts on
unadjusted highs (plan_52wh.md A4).

Distinct from src/fetch_ohlc.py, which fetches UNADJUSTED prices for Tier 1
settlement — do not mix the two bases.

Symbols come from the PIT store (all symbols carrying any mcap_rank row), or
--symbols FILE (one NSE symbol per line) until the A1 corpus lands.
Per-symbol raw pulls are cached under data/workspace/ohlc_adj/ — idempotent;
delete a symbol's parquet to force a refetch.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from src import data_gate, pit_universe  # noqa: E402

CACHE = REPO / "data" / "workspace" / "ohlc_adj"
PANEL = REPO / "data" / "workspace" / "price_panel_52wh.parquet"
DEV_START = "2015-01-01"  # >= 1y of highs before a 2016 first rebalance


def universe_symbols() -> list[str]:
    """Symbols that ever held mcap_rank <= 1000 in a research-visible list
    (habitat 201-1000 plus the Top-200 sensitivity bands; gate on
    announce_date keeps sealed-period lists out of the fetch set)."""
    store = pit_universe.load_store()
    ranks = data_gate.load(
        store.loc[store["field"] == "mcap_rank"], "announce_date"
    )
    ranks = ranks.loc[pd.to_numeric(ranks["value"], errors="coerce") <= 1000]
    return sorted(ranks["symbol"].dropna().unique())


def fetch_symbol(symbol: str) -> pd.DataFrame | None:
    """Adjusted OHLC for one symbol, dev window only, cached."""
    cached = CACHE / f"{symbol}.parquet"
    if cached.exists():
        return pd.read_parquet(cached)
    import time

    import yfinance as yf

    try:
        raw = yf.Ticker(f"{symbol}.NS").history(
            start=DEV_START,
            end=str(data_gate.SEAL_CUTOFF.date()),  # never pull sealed rows
            auto_adjust=True,
        )
    except Exception as e:  # one bad symbol must not kill a multi-hour run
        print(f"  FETCH ERROR {symbol}: {e}", flush=True)
        return None
    finally:
        time.sleep(0.15)  # polite pacing for thousands of sequential pulls
    if raw.empty:
        return None
    df = raw.reset_index()[["Date", "Open", "High", "Low", "Close", "Volume"]]
    df.columns = ["date", "open", "high", "low", "close", "volume"]
    df["date"] = pd.to_datetime(df["date"]).dt.tz_localize(None)
    df.insert(1, "symbol", symbol)
    CACHE.mkdir(parents=True, exist_ok=True)
    df.to_parquet(cached, index=False)
    return df


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--symbols", type=Path, help="file of NSE symbols, one per line")
    args = ap.parse_args()

    if args.symbols:
        symbols = [s.strip() for s in args.symbols.read_text().split() if s.strip()]
    else:
        symbols = universe_symbols()
    print(f"building adjusted panel for {len(symbols)} symbols")

    frames, missing = [], []
    for i, sym in enumerate(symbols, 1):
        df = fetch_symbol(sym)
        if df is None:
            missing.append(sym)
        else:
            frames.append(df)
        if i % 50 == 0:
            print(f"  {i}/{len(symbols)} fetched")
    if not frames:
        sys.exit("no data fetched")

    panel = data_gate.load(pd.concat(frames, ignore_index=True), "date")
    assert panel["date"].max() < data_gate.SEAL_CUTOFF  # gate-enforced
    panel.to_parquet(PANEL, index=False)
    print(
        f"wrote {len(panel)} rows, {panel['symbol'].nunique()} symbols, "
        f"{panel['date'].min().date()} → {panel['date'].max().date()} → {PANEL}"
    )
    # Auditable coverage record: names yfinance cannot serve (mostly delisted)
    # are a survivorship hole the eventual trial must disclose, not hide.
    missing_file = PANEL.with_name("price_panel_missing.txt")
    missing_file.write_text("\n".join(missing) + "\n" if missing else "")
    print(f"NO DATA for {len(missing)}/{len(symbols)} symbols → {missing_file}")


if __name__ == "__main__":
    main()

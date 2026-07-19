#!/usr/bin/env python3
"""Symbol rename map + panel recovery for the A4 survivorship caveat
(plan_52wh.md A4, SPEC-52WH-01).

215/1,412 fetch-set symbols are unservable by yfinance under their PIT-era
symbols; some are RENAMES (ZOMATO→ETERNAL) whose full price history Yahoo
serves under the CURRENT ticker. This script:

1. ingests NSE's public symbol-change master
   (https://nsearchives.nseindia.com/content/equities/symbolchange.csv,
   pre-downloaded to data/reference/rename/symbolchange.csv — public data,
   same class as the A1/A3 niftyindices pulls; no broker APIs);
2. resolves each missing symbol to its terminal ticker (chained renames
   followed, cycle-guarded);
3. fetches the dev-window ADJUSTED history under the terminal ticker and
   caches it under the ORIGINAL symbol (data/workspace/ohlc_adj/<OLD>.parquet)
   so PIT-store joins — which key on the symbol as listed at the time — work
   unchanged. The old-label series is TRUNCATED at the first rename's
   effective date: without truncation the same company is rankable under both
   labels at post-rename rebalance dates (AMFI's stale old-label rank row
   stays as-of visible), double-counting it in the cross-section;
4. writes data/reference/rename/rename_map.csv (audit record: every missing
   symbol, its mapping if any, and the fetch outcome).

Identity resolution only — the rename table carries no price/outcome
information, so using post-cutoff rename knowledge to label pre-cutoff prices
is plumbing, not look-ahead. Rerun scripts/build_price_panel.py afterwards to
rebuild the panel and refresh price_panel_missing.txt.
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from src import data_gate  # noqa: E402

RENAME_DIR = REPO / "data" / "reference" / "rename"
SYMBOLCHANGE = RENAME_DIR / "symbolchange.csv"
RENAME_MAP = RENAME_DIR / "rename_map.csv"
CACHE = REPO / "data" / "workspace" / "ohlc_adj"
MISSING = REPO / "data" / "workspace" / "price_panel_missing.txt"
DEV_START = "2015-01-01"  # keep identical to build_price_panel.DEV_START


def load_edges() -> pd.DataFrame:
    """NSE master as (old, new, effective) edges; headerless CSV."""
    raw = pd.read_csv(
        SYMBOLCHANGE, header=None, names=["company", "old", "new", "effective"],
        skipinitialspace=True,
    )
    raw["old"] = raw["old"].str.strip()
    raw["new"] = raw["new"].str.strip()
    raw["effective"] = pd.to_datetime(raw["effective"], format="%d-%b-%Y")
    return raw.sort_values("effective")


def terminal_symbol(sym: str, forward: dict[str, tuple[str, pd.Timestamp]]):
    """Follow rename chains to the current ticker; (None, [], None) if sym was
    never renamed. Returns (terminal, chain, first_effective) where chain
    lists each hop old->new@date and first_effective is when ``sym`` itself
    ceased trading under its old label (the truncation point)."""
    chain, seen, cur, first_eff = [], {sym}, sym, None
    while cur in forward:
        nxt, eff = forward[cur]
        if nxt in seen:  # symbol reuse cycle — stop at last resolved hop
            break
        if first_eff is None:
            first_eff = eff
        chain.append(f"{cur}->{nxt}@{eff.date()}")
        seen.add(nxt)
        cur = nxt
    return (cur, chain, first_eff) if chain else (None, [], None)


def fetch_as(old: str, ticker: str, end: pd.Timestamp) -> bool:
    """Adjusted OHLC for ``ticker`` up to ``end`` (min of seal cutoff and the
    old label's rename effective date), cached under ``old``'s identity.
    Mirrors build_price_panel.fetch_symbol (window, columns, auto_adjust) so
    the rebuilt panel is basis-consistent."""
    cached = CACHE / f"{old}.parquet"
    if cached.exists():
        return True
    if end <= pd.Timestamp(DEV_START):
        return False  # old label died before the dev window — nothing to recover
    import yfinance as yf

    try:
        raw = yf.Ticker(f"{ticker}.NS").history(
            start=DEV_START,
            end=str(end.date()),  # never past the seal cutoff or the rename
            auto_adjust=True,
        )
    except Exception as e:
        print(f"  FETCH ERROR {old} (as {ticker}): {e}", flush=True)
        return False
    finally:
        time.sleep(0.15)
    if raw.empty:
        return False
    df = raw.reset_index()[["Date", "Open", "High", "Low", "Close", "Volume"]]
    df.columns = ["date", "open", "high", "low", "close", "volume"]
    df["date"] = pd.to_datetime(df["date"]).dt.tz_localize(None)
    df.insert(1, "symbol", old)  # PIT identity: the symbol as listed at the time
    CACHE.mkdir(parents=True, exist_ok=True)
    df.to_parquet(cached, index=False)
    return True


def main() -> None:
    # Rerun-safe scope: the current missing list PLUS every symbol a prior run
    # already mapped (panel rebuilds shrink the missing file as names recover).
    missing = {s for s in MISSING.read_text().split() if s.strip()}
    if RENAME_MAP.exists():
        missing |= set(pd.read_csv(RENAME_MAP)["old_symbol"])
    missing = sorted(missing)
    edges = load_edges()
    # Last rename FROM each symbol wins (duplicates are rare symbol reuses).
    forward = {
        r.old: (r.new, r.effective) for r in edges.itertuples() if r.old != r.new
    }
    print(f"{len(missing)} missing symbols, {len(forward)} rename edges")

    rows, recovered = [], 0
    for sym in missing:
        term, chain, first_eff = terminal_symbol(sym, forward)
        if term is None:
            rows.append({"old_symbol": sym, "terminal_symbol": "", "chain": "",
                         "truncated_at": "", "outcome": "NO_RENAME_FOUND"})
            continue
        end = min(pd.Timestamp(data_gate.SEAL_CUTOFF), first_eff)
        ok = fetch_as(sym, term, end)
        recovered += ok
        rows.append({
            "old_symbol": sym, "terminal_symbol": term,
            "chain": " ".join(chain),
            "truncated_at": str(end.date()) if first_eff < data_gate.SEAL_CUTOFF else "",
            "outcome": "RECOVERED" if ok else "RENAMED_BUT_UNSERVABLE",
        })
        print(f"  {sym} -> {term}: {'ok' if ok else 'still no data'}")

    report = pd.DataFrame(rows)
    report.to_csv(RENAME_MAP, index=False)
    n_mapped = (report["terminal_symbol"] != "").sum()
    print(
        f"\n{n_mapped}/{len(missing)} missing symbols have a rename; "
        f"{recovered} recovered into {CACHE}\nreport -> {RENAME_MAP}\n"
        "now rerun scripts/build_price_panel.py to rebuild the panel "
        "and refresh price_panel_missing.txt"
    )


if __name__ == "__main__":
    main()

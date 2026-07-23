#!/usr/bin/env python3
"""Build the canonical PIT constituent store from staged A1 corpus files.

Reads normalized staging CSVs from data/reference/pit/staging/*.csv — columns
(symbol, field, effective_date, announce_date, value, source) with
``source_file`` accepted as an alias for ``source`` — validates them against
the pit_universe schema, de-duplicates, and writes
data/reference/pit/pit_universe.parquet.

Then prints the A1 coverage report: earliest date per field, the half-year
gap list for mcap_rank, and whether any gap exceeds the pre-committed
2-quarter threshold that triggers the F&O-eligible fallback (plan_52wh.md A1).

Raw-source normalization (AMFI xlsx parsing, NSE press-release extraction)
happens UPSTREAM of staging/ — this script enforces schema and provenance,
it does not guess at messy formats. The store retains full history including
post-cutoff rows; the seal gate applies at read time inside
``src.pit_universe`` as-of queries (binding rule 4).
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from src import pit_universe  # noqa: E402

STAGING = REPO / "data" / "reference" / "pit" / "staging"


def load_staging() -> pd.DataFrame:
    files = sorted(STAGING.glob("*.csv"))
    if not files:
        sys.exit(
            f"no staging CSVs in {STAGING} — stage the A1 corpus first "
            "(see data/reference/pit/COVERAGE.md and plan_52wh.md A1)"
        )
    frames = []
    for f in files:
        df = pd.read_csv(f)
        if "source" not in df.columns and "source_file" in df.columns:
            df = df.rename(columns={"source_file": "source"})
        try:
            frames.append(pit_universe.validate(df))
        except ValueError as e:
            sys.exit(f"{f.name}: {e}")
        print(f"  staged {f.name}: {len(df)} rows")
    merged = pd.concat(frames, ignore_index=True)
    merged = deduplicate(merged)
    return merged.sort_values(
        ["field", "effective_date", "announce_date", "symbol"]
    ).reset_index(drop=True)


def deduplicate(merged: pd.DataFrame) -> pd.DataFrame:
    """Collapse identical assertions, and SAY what was collapsed (TRAP 6).

    The key is ``(symbol, field, effective_date, announce_date, value)`` —
    deliberately not ``isin``, because the store's identity is the symbol. That
    is safe for a NAMED symbol (two rows agreeing on all five fields are the
    same assertion) but NOT for a blank one: two DIFFERENT companies with no
    ticker and the same rounded market cap collapse into one row. Before the
    2026-07-22 habitat fix that silently destroyed 22,710 rows and printed only
    a bare count, which nothing read.

    So: a dropped row with a named symbol is a HARD STOP (it means two symbols
    genuinely disagree about what is being asserted, or the staging halves have
    drifted), while dropped blank-symbol rows are reported per field with their
    distinct-ISIN count so the loss is disclosed rather than inferred.
    """
    key = [c for c in pit_universe.SCHEMA if c != "source"]
    dropped = merged.loc[merged.duplicated(subset=key, keep="first")]
    out = merged.drop_duplicates(subset=key)
    if dropped.empty:
        print("  de-dup: no duplicate rows")
        return out
    named = dropped.loc[dropped["symbol"].notna() & (dropped["symbol"] != "")]
    blank = dropped.loc[~dropped.index.isin(named.index)]
    print(f"  de-dup: dropped {len(dropped)} duplicate rows "
          f"({len(named)} named-symbol, {len(blank)} blank-symbol)")
    for field, grp in blank.groupby("field"):
        isins = grp["isin"].nunique() if "isin" in grp.columns else "n/a"
        print(f"    WARNING blank-symbol rows lost, {field}: {len(grp)} rows, "
              f"{isins} distinct ISINs — different companies sharing a rounded "
              f"value collapse under a NA key (see analysis/"
              f"habitat_defect_verification.md §6)")
    if not named.empty:
        sample = named.head(5).to_string(index=False)
        sys.exit(
            f"build_pit_universe: {len(named)} NAMED-symbol rows were dropped as "
            f"duplicates. That is never benign — two staged rows assert the same "
            f"(symbol, field, effective_date, announce_date, value) from "
            f"different sources, or the staging halves have drifted apart.\n"
            f"{sample}"
        )
    return out


def half_year(ts: pd.Timestamp) -> str:
    return f"{ts.year}H{1 if ts.month <= 6 else 2}"


def coverage_report(store: pd.DataFrame) -> None:
    print("\n=== PIT coverage (A1) ===")
    for field, grp in store.groupby("field"):
        print(
            f"{field}: {len(grp)} rows, {grp['symbol'].nunique()} symbols, "
            f"effective {grp['effective_date'].min().date()} → "
            f"{grp['effective_date'].max().date()}"
        )
    ranks = store.loc[store["field"] == "mcap_rank"]
    if ranks.empty:
        print("mcap_rank: ABSENT — ranks 201-1000 habitat cannot be built yet")
        return
    have = {half_year(ts) for ts in ranks["effective_date"]}
    lo, hi = ranks["effective_date"].min(), ranks["effective_date"].max()
    expected = []
    y, h = lo.year, 1 if lo.month <= 6 else 2
    while (y, h) <= (hi.year, 1 if hi.month <= 6 else 2):
        expected.append(f"{y}H{h}")
        y, h = (y, 2) if h == 1 else (y + 1, 1)
    gaps = [p for p in expected if p not in have]
    print(f"mcap_rank half-years present: {sorted(have)}")
    if gaps:
        print(f"mcap_rank GAPS: {gaps}")
        run = max_consecutive(gaps, expected)
        if run >= 2:  # 2 half-years > 2 quarters
            print(
                f"  longest gap run = {run} half-years (> 2 quarters) — "
                "pre-committed fallback applies: F&O-eligible universe "
                "(plan_52wh.md A1)"
            )
    else:
        print("mcap_rank: no half-year gaps")


def max_consecutive(gaps: list[str], expected: list[str]) -> int:
    longest = run = 0
    for p in expected:
        run = run + 1 if p in gaps else 0
        longest = max(longest, run)
    return longest


def main() -> None:
    store = load_staging()
    pit_universe.PIT_STORE.parent.mkdir(parents=True, exist_ok=True)
    store.to_parquet(pit_universe.PIT_STORE, index=False)
    print(f"\nwrote {len(store)} rows → {pit_universe.PIT_STORE}")
    coverage_report(store)


if __name__ == "__main__":
    main()

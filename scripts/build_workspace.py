#!/usr/bin/env python3
"""Build the gated research workspace from raw snapshots.

Reads the latest raw snapshot day under data/sealed/raw/, routes EVERYTHING
through src/data_gate.load(), and writes only the gated (pre-cutoff) result as
parquet into data/workspace/.

By design, current operational snapshots are entirely post-cutoff, so these
parquets are typically EMPTY — that is the seal working, not a bug. Post-cutoff
rows exist only under data/sealed/ (never committed). Operational analysis of
forward data goes through data_gate.load_operational() (Tier 1) instead.

Also computes rec_key = data_date|SYMBOL|seq (RULING 1) before gating, so any
future pre-cutoff rec data lands workspace-side already keyed.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))
import data_gate

RAW_ROOT = REPO / "data" / "sealed" / "raw"
WORKSPACE = REPO / "data" / "workspace"

_REC_NAME = re.compile(
    r"top5_report_data(?P<data_date>\d{4}-\d{2}-\d{2})_generated(?P<gen_date>\d{4}-\d{2}-\d{2})\.csv$"
)


def load_rec_files(raw_day: Path) -> pd.DataFrame:
    """Parse all rec CSVs in a snapshot dir and assign rec_key (RULING 1)."""
    frames = []
    for f in sorted(raw_day.glob("top5_report_data*_generated*.csv")):
        m = _REC_NAME.search(f.name)
        if not m:
            continue
        try:
            df = pd.read_csv(f, comment="#")
        except pd.errors.EmptyDataError:
            continue  # some re-generations have zero picks (comment line only)
        if df.empty:
            continue
        df["data_date"] = m["data_date"]
        df["generated_date"] = m["gen_date"]
        frames.append(df)
    if not frames:
        return pd.DataFrame()
    recs = pd.concat(frames, ignore_index=True)
    # seq: 1-based ordinal of the generation per data_date, ordered by generated_date
    gen_rank = (
        recs.groupby("data_date")["generated_date"]
        .transform(lambda s: s.map({g: i + 1 for i, g in enumerate(sorted(s.unique()))}))
    )
    recs["seq"] = gen_rank.astype(int)
    recs["rec_key"] = (
        recs["data_date"] + "|" + recs["symbol"].astype(str) + "|" + recs["seq"].astype(str)
    )
    return recs


def main() -> None:
    days = sorted(d for d in RAW_ROOT.iterdir() if d.is_dir()) if RAW_ROOT.is_dir() else []
    if not days:
        print("[workspace] no raw snapshots found — nothing to build")
        return
    raw_day = days[-1]
    WORKSPACE.mkdir(parents=True, exist_ok=True)

    recs = load_rec_files(raw_day)
    if not recs.empty:
        gated = data_gate.load(recs, "data_date")
        gated.to_parquet(WORKSPACE / "recs.parquet", index=False)
        print(f"[workspace] recs: {len(recs)} raw -> {len(gated)} gated rows")

    fills_path = raw_day / "trades_log.csv"
    if fills_path.exists():
        fills = pd.read_csv(fills_path)
        gated = data_gate.load(fills, "pick_date")
        gated.to_parquet(WORKSPACE / "fills.parquet", index=False)
        print(f"[workspace] fills: {len(fills)} raw -> {len(gated)} gated rows")


if __name__ == "__main__":
    main()

"""PIT constituent store (SPEC-52WH-01 Stage 1, plan_52wh.md).

qlib-style point-in-time rows ``(symbol, field, effective_date, announce_date,
value, source)``. Two visibility clocks per row:

- ``announce_date`` — when the information became public knowledge. An as-of
  query at date t sees ONLY rows with ``announce_date <= t`` (no look-ahead).
- ``effective_date`` — when the state change takes force (index reconstitution
  effective date; AMFI list period end).

Every as-of query routes the frame through ``data_gate.load`` on
``announce_date`` (binding rule 4): rows announced on/after the seal cutoff
are structurally invisible to research regardless of the query date, unless
``FINAL_TEST=1`` (which burns the family's single sealed test).

Fields:
- ``mcap_rank`` — integer market-cap rank (AMFI semi-annual lists).
- ``index_member:<NAME>`` — 1 = added / member, 0 = dropped (NSE index
  change releases), e.g. ``index_member:NIFTY500``.

Features only — no price or return data lives here.
"""

from __future__ import annotations

import re
from pathlib import Path

import pandas as pd

from src import data_gate

REPO = Path(__file__).resolve().parents[1]
PIT_STORE = REPO / "data" / "reference" / "pit" / "pit_universe.parquet"

SCHEMA = ("symbol", "field", "effective_date", "announce_date", "value", "source")

# Provenance columns carried through when present (never required). isin
# matters because recent AMFI lists have ~3% blank NSE symbols — joins on
# post-2025 periods should use it (data/reference/pit/COVERAGE.md §6).
OPTIONAL_COLS = ("isin",)

_RANK_FIELD = "mcap_rank"
_RANK_BAND_RE = re.compile(r"^\s*(\d+)\s*-\s*(\d+)\s*$")


def validate(frame: pd.DataFrame) -> pd.DataFrame:
    """Schema check + date parsing. Returns a copy; raises ValueError on
    missing columns. Does NOT gate — use the as-of queries for research access."""
    missing = [c for c in SCHEMA if c not in frame.columns]
    if missing:
        raise ValueError(f"pit_universe: missing columns {missing} (schema {SCHEMA})")
    keep = list(SCHEMA) + [c for c in OPTIONAL_COLS if c in frame.columns]
    out = frame.loc[:, keep].copy()
    out["effective_date"] = pd.to_datetime(out["effective_date"])
    out["announce_date"] = pd.to_datetime(out["announce_date"])
    if out["announce_date"].isna().any() or out["effective_date"].isna().any():
        raise ValueError("pit_universe: unparseable effective/announce dates present")
    return out


def _visible(frame: pd.DataFrame, date) -> pd.DataFrame:
    """Rows knowable and in force at ``date``, seal-gated on announce_date."""
    gated = data_gate.load(validate(frame), "announce_date")
    date = pd.Timestamp(date)
    vis = gated.loc[
        (gated["announce_date"] <= date) & (gated["effective_date"] <= date)
    ]
    return vis.sort_values(["effective_date", "announce_date"], kind="stable")


def snapshot_as_of(frame: pd.DataFrame, date, field: str) -> pd.Series:
    """Latest visible ``value`` per symbol for ``field`` as of ``date``.

    A row is visible only if announced AND effective on or before ``date``;
    among visible rows the one with the latest (effective_date, announce_date)
    wins. Symbols with no visible row are absent (pre-announcement state).
    """
    vis = _visible(frame, date)
    vis = vis.loc[vis["field"] == field]
    if vis.empty:
        return pd.Series(dtype=object, name=field)
    last = vis.groupby("symbol", sort=True).tail(1)
    return last.set_index("symbol")["value"].rename(field)


def universe_as_of(frame: pd.DataFrame, date, band) -> list[str]:
    """Symbols in ``band`` as of ``date`` (announce- and effective-visible only).

    ``band`` forms:
    - ``(lo, hi)`` or ``"201-1000"`` — inclusive ``mcap_rank`` range.
    - an index name, e.g. ``"NIFTY500"`` — membership via the
      ``index_member:<NAME>`` field (latest visible row must be truthy).
    """
    if isinstance(band, (tuple, list)):
        lo, hi = int(band[0]), int(band[1])
        return _rank_band(frame, date, lo, hi)
    m = _RANK_BAND_RE.match(str(band))
    if m:
        return _rank_band(frame, date, int(m.group(1)), int(m.group(2)))
    snap = snapshot_as_of(frame, date, f"index_member:{band}")
    member = pd.to_numeric(snap, errors="raise") == 1
    return sorted(snap.index[member])


def _rank_band(frame: pd.DataFrame, date, lo: int, hi: int) -> list[str]:
    if lo > hi:
        raise ValueError(f"pit_universe: empty rank band {lo}-{hi}")
    snap = pd.to_numeric(snapshot_as_of(frame, date, _RANK_FIELD), errors="raise")
    return sorted(snap.index[(snap >= lo) & (snap <= hi)])


def load_store(path: Path | str = PIT_STORE) -> pd.DataFrame:
    """Read the canonical parquet store (validated, NOT yet as-of filtered).
    Research access happens through the as-of queries, which gate."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(
            f"PIT store not found at {path} — run scripts/build_pit_universe.py "
            "once the A1 corpus is staged (plan_52wh.md)"
        )
    return validate(pd.read_parquet(path))

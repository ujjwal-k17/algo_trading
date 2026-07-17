"""The ONLY sanctioned data door for this workspace.

Every DataFrame used in research must pass through :func:`load` before any
analysis, feature construction, or plotting. The gate enforces the sealed
holdout declared in ``governance/SEAL.md``: rows dated 2024-07-17 or later are
stripped unless the environment variable ``FINAL_TEST=1`` is set — and setting
it burns the signal family's single pre-registered final test.

Loading raw files with post-2024-07-17 rows directly in notebooks or scripts
is a seal violation.
"""

from __future__ import annotations

import os
import sys

import pandas as pd

SEAL_CUTOFF = pd.Timestamp("2024-07-17")

# First ledger date: min(pick_date) in data/legacy_snapshot/trades_log_ee7ad13.csv
# (RULING 2, governance/DECISIONS.md — the ruling's 2026-06-20 placeholder
# adjusted to the exact first ledger date found in the snapshot).
LIVE_WINDOW_START = pd.Timestamp("2026-06-29")

# Admissible Tier 1 sources (RULING 2; data/derived/ added for paper-leg
# output per DECISIONS.md ASSUMPTION).
_OPERATIONAL_SOURCES = (
    "data/legacy_snapshot/",
    "governance/overlay_log.csv",
    "data/derived/",
    # AMENDMENT to RULING 3 (DECISIONS.md): snapshot OHLC backups are the
    # sanctioned settlement source; admissible solely via the settlement
    # join — the rec_key shape rule below still applies.
    "data/sealed/raw/",
)

_TIER1_NOTICE = (
    "Tier 1 forward data — sanctioned for settlement/monitoring/pre-registered "
    "A/B only; design iteration on this data burns it as evidence."
)

_FINAL_TEST_WARNING = """
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
!!  FINAL_TEST=1 — SEALED HOLDOUT IS OPEN                               !!
!!                                                                      !!
!!  You are reading data from the sealed range (>= 2024-07-17).         !!
!!  This BURNS the single pre-registered final test for this signal     !!
!!  family. There is no second test and no reset (governance/SEAL.md).  !!
!!  If this run is not the pre-registered final test, STOP NOW —        !!
!!  the family's test is already invalidated by this peek.              !!
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
"""


def load(df: pd.DataFrame, date_col: str) -> pd.DataFrame:
    """Gate a DataFrame through the sealed-holdout cutoff.

    This is the ONLY sanctioned data door: all research data access must go
    through here (governance/SEAL.md, rule 3).

    Parses ``df[date_col]`` to datetimes, then — unless the environment
    variable ``FINAL_TEST`` is set to ``"1"`` — strips every row dated on or
    after 2024-07-17. With ``FINAL_TEST=1`` the full frame is returned and a
    loud warning is printed, because that read consumes the signal family's
    one final test.

    Args:
        df: Input DataFrame containing a date column.
        date_col: Name of the column holding row dates.

    Returns:
        A new DataFrame (input is never mutated) with parsed dates and, in
        default mode, only rows strictly before 2024-07-17.
    """
    out = df.copy()
    out[date_col] = pd.to_datetime(out[date_col])
    if os.environ.get("FINAL_TEST") == "1":
        print(_FINAL_TEST_WARNING, file=sys.stderr, flush=True)
        return out
    return out.loc[out[date_col] < SEAL_CUTOFF].reset_index(drop=True)


def load_operational(df: pd.DataFrame, date_col: str, source: str) -> pd.DataFrame:
    """Tier 1 door for forward operational data (RULING 2, look-don't-tune).

    Admits ONLY rec/fill/overlay/paper-leg-derived data dated on or after the
    live-window start (2026-06-29 — first ledger date, see LIVE_WINDOW_START).
    Validates by SHAPE and SOURCE, not intent:

    - ``source`` must lie under ``data/legacy_snapshot/``, be
      ``governance/overlay_log.csv``, or lie under ``data/derived/``.
    - The frame must be rec_key-joinable: a ``rec_key`` column, or ``symbol``
      plus a pick/data date column. A generic OHLC panel is rejected even if
      its dates qualify; post-cutoff OHLC is admissible only when joined to
      specific rec dates for settlement (i.e. it carries rec keys).
    - Rows dated before the seal cutoff (historical/research tier) or in the
      seal gap [2024-07-17, 2026-06-29) are rejected outright.

    Args:
        df: Input DataFrame.
        date_col: Name of the column holding row dates.
        source: Path the data originated from (validated against the
            admissible-source list).

    Returns:
        A new DataFrame with parsed dates. Raises ValueError on any violation.

    Prints the standing Tier 1 notice on every successful load.
    """
    src = str(source).replace("\\", "/")
    if not any(allowed in src for allowed in _OPERATIONAL_SOURCES):
        raise ValueError(
            f"load_operational: inadmissible source {source!r} — Tier 1 accepts "
            f"only {_OPERATIONAL_SOURCES}"
        )

    cols = set(df.columns)
    lower = {c.lower() for c in cols}
    joinable = "rec_key" in lower or (
        "symbol" in lower
        and any(c in lower for c in ("pick_date", "data_date", "rec_date"))
    )
    if not joinable:
        ohlc_shaped = {"open", "high", "low", "close"} <= lower
        raise ValueError(
            "load_operational: frame is not rec_key-joinable"
            + (
                " (generic OHLC panel — post-cutoff OHLC is admissible only "
                "joined to specific rec dates for settlement)"
                if ohlc_shaped
                else " (need rec_key, or symbol + pick/data date column)"
            )
        )

    out = df.copy()
    out[date_col] = pd.to_datetime(out[date_col])
    dates = out[date_col].dropna()
    if (dates < SEAL_CUTOFF).any():
        raise ValueError(
            "load_operational: pre-cutoff (historical) dates present — that is "
            "research-tier data; use load()"
        )
    if (dates < LIVE_WINDOW_START).any():
        raise ValueError(
            f"load_operational: dates in the seal gap [{SEAL_CUTOFF.date()}, "
            f"{LIVE_WINDOW_START.date()}) are sealed holdout and inadmissible"
        )
    print(_TIER1_NOTICE, file=sys.stderr, flush=True)
    return out

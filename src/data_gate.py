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

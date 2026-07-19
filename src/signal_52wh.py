"""52-week-high nearness signal (SPEC-52WH-01 Stage 2, plan_52wh.md).

``nearness = close / rolling_max(high, 252)`` — the expression string below is
the canonical artifact that will be hash-frozen in the spec; it runs through
``src.expr`` and nothing else. Cross-sectional rank is taken WITHIN the PIT
universe as of the rebalance date, then mapped to bucket labels Q1..Qn:
Q1 = far-from-high (the catastrophic bucket the negative screen excludes,
Raju 2023), Qn = nearest-to-high.

Pure functions, features only: no return columns are computed, joined, or
accepted here. Outcome contact exists only in the trial runner, post-freeze.
"""

from __future__ import annotations

import math

import pandas as pd

from src import expr

NEARNESS_EXPR = "close / rolling_max(high, 252)"
N_BUCKETS = 5


def nearness_panel(
    panel: pd.DataFrame, *, date_col: str = "date", symbol_col: str = "symbol"
) -> pd.DataFrame:
    """Wide (date x symbol) nearness frame; NaN until 252 highs exist."""
    return expr.evaluate(
        NEARNESS_EXPR, panel, date_col=date_col, symbol_col=symbol_col
    )


def rank_row(row: pd.Series, universe, *, n_buckets: int = N_BUCKETS) -> pd.DataFrame:
    """Cross-sectional rank + buckets for one date's nearness row.

    Extracted from ``signal_at`` so a walk-forward run can evaluate the
    nearness panel ONCE and rank each rebalance date off it, instead of
    recomputing a 252-day rolling max per date. Both paths share this code —
    the trial runner cannot silently drift from the canonical ranking
    (asserted in tests/test_signal_52wh.py).
    """
    if n_buckets < 2:
        raise ValueError("n_buckets must be >= 2")
    row = row.loc[row.index.isin(set(universe))].dropna()
    out = row.rename("nearness").to_frame()
    out["cs_rank"] = out["nearness"].rank(pct=True)
    # -1e-9 guards float noise: a pct of exactly k/n must land in Qk, not Qk+1.
    out["bucket"] = [
        f"Q{min(n_buckets, max(1, math.ceil(p * n_buckets - 1e-9)))}"
        for p in out["cs_rank"]
    ]
    out.index.name = "symbol"
    return out.sort_values("cs_rank")


def signal_at(
    panel: pd.DataFrame,
    universe: list[str],
    date,
    *,
    n_buckets: int = N_BUCKETS,
    date_col: str = "date",
    symbol_col: str = "symbol",
) -> pd.DataFrame:
    """Nearness, cross-sectional rank, and bucket per universe symbol at ``date``.

    Only symbols in ``universe`` with a defined nearness (>= 252 observed highs
    by ``date``) are ranked; the rest are silently absent — the caller's
    coverage report, not this function, accounts for them. Ranks use only
    data at or before ``date`` (rolling max and close are trailing), so
    appending post-``date`` rows never changes the output.

    Returns a frame indexed by symbol: ``nearness``, ``cs_rank`` (percentile
    in (0, 1]), ``bucket`` (Q1 = farthest from high .. Qn = nearest).
    """
    date = pd.Timestamp(date)
    wide = nearness_panel(panel, date_col=date_col, symbol_col=symbol_col)
    if date not in wide.index:
        raise ValueError(f"no panel row at {date.date()} — not a trading date?")
    return rank_row(wide.loc[date], universe, n_buckets=n_buckets)

"""Rebalance calendar and turnover accounting (SPEC-52WH-01 Stage 3,
plan_52wh.md).

Quarterly is the spec default (slow decay: ~84% of the 52WH premium survives
a 6-month hold, research.md Part 4); monthly and semi-annual are the
pre-registered sensitivities. Turnover here is WEIGHT arithmetic only — the
rupee cost of a rebalance is ``costs_in`` applied to traded value inside the
trial runner, post-freeze. No prices, no returns, no outcome contact.

Convention: ``turnover()`` is ONE-WAY — sum(|delta w|) / 2, the fraction of
the book traded each way. The spec's «300%/yr budget is stated one-way;
traded value for costing is 2x one-way turnover x book value.
"""

from __future__ import annotations

import pandas as pd

FREQS = ("M", "Q", "H")  # monthly, quarterly (spec default), semi-annual
DEFAULT_FREQ = "Q"


def rebalance_dates(trading_dates, freq: str = DEFAULT_FREQ) -> pd.DatetimeIndex:
    """Last trading date of each calendar period covered by ``trading_dates``.

    ``trading_dates`` is any iterable of dates (e.g. the price panel's date
    column); the calendar is derived from it, so holidays need no separate
    source. NOTE: the final period is included even if ``trading_dates`` ends
    mid-period (the dev window ends 2024-07-16, mid-quarter) — whether that
    partial-period date is a valid rebalance is the trial runner's call.
    """
    if freq not in FREQS:
        raise ValueError(f"freq must be one of {FREQS}, got {freq!r}")
    dates = pd.DatetimeIndex(pd.to_datetime(list(trading_dates))).unique().sort_values()
    if dates.empty:
        raise ValueError("trading_dates is empty")
    if freq == "H":
        keys = [(d.year, 1 if d.month <= 6 else 2) for d in dates]
    else:
        keys = dates.to_period(freq)
    last_per_period = pd.Series(dates, index=keys).groupby(level=0).last()
    return pd.DatetimeIndex(last_per_period.values, name="rebalance_date")


def _weights(w, name: str) -> pd.Series:
    if w is None:
        s = pd.Series(dtype=float)
    elif isinstance(w, pd.Series):
        s = w.astype(float)
    else:
        s = pd.Series(dict(w), dtype=float)
    if s.index.has_duplicates:
        raise ValueError(f"{name} has duplicate symbols")
    if s.isna().any():
        raise ValueError(f"{name} has undefined weights")
    return s


def trades(prev, new) -> pd.Series:
    """Weight deltas (new - prev) over the union of both books, sorted by
    symbol. Positive = buy, negative = sell. ``None`` = empty book (inception
    or full liquidation)."""
    p = _weights(prev, "prev")
    n = _weights(new, "new")
    union = p.index.union(n.index).sort_values()
    delta = n.reindex(union, fill_value=0.0) - p.reindex(union, fill_value=0.0)
    return delta.rename("delta_weight")


def turnover(prev, new) -> float:
    """One-way turnover: sum(|delta w|) / 2. Full replacement of a fully
    invested book = 1.0; no change = 0.0; inception from cash = 0.5."""
    return float(trades(prev, new).abs().sum()) / 2.0

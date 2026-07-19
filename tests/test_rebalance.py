"""Acceptance tests for src/rebalance.py (Stage 3, plan_52wh.md): turnover on
a synthetic book matches hand calc; the calendar picks the last trading day
per period from the supplied dates alone."""

import pandas as pd
import pytest

from src import rebalance

# A synthetic trading calendar: business days for one full year plus a stub
# ending mid-quarter (like the dev window ending 2024-07-16).
YEAR = pd.bdate_range("2020-01-01", "2020-12-31")
STUB = pd.bdate_range("2021-01-01", "2021-02-10")


def test_quarterly_calendar_last_trading_day_per_quarter():
    out = rebalance.rebalance_dates(YEAR, "Q")
    assert [d.date().isoformat() for d in out] == [
        "2020-03-31", "2020-06-30", "2020-09-30", "2020-12-31",
    ]


def test_monthly_and_semiannual_counts():
    assert len(rebalance.rebalance_dates(YEAR, "M")) == 12
    half = rebalance.rebalance_dates(YEAR, "H")
    assert [d.date().isoformat() for d in half] == ["2020-06-30", "2020-12-31"]


def test_calendar_respects_holidays_in_supplied_dates():
    # Drop the last business day of Q1: previous trading day becomes the mark.
    dates = YEAR[YEAR != pd.Timestamp("2020-03-31")]
    out = rebalance.rebalance_dates(dates, "Q")
    assert out[0] == pd.Timestamp("2020-03-30")


def test_partial_final_period_is_included():
    out = rebalance.rebalance_dates(list(YEAR) + list(STUB), "Q")
    assert out[-1] == pd.Timestamp("2021-02-10")  # documented behaviour


def test_calendar_input_validation():
    with pytest.raises(ValueError, match="freq"):
        rebalance.rebalance_dates(YEAR, "W")
    with pytest.raises(ValueError, match="empty"):
        rebalance.rebalance_dates([], "Q")


def test_turnover_hand_calc():
    prev = {"A": 0.5, "B": 0.5}
    # Sell B (0.5), buy C (0.3), trim A to 0.4, hold 0.3 cash.
    new = {"A": 0.4, "C": 0.3}
    # |dA| + |dB| + |dC| = 0.1 + 0.5 + 0.3 = 0.9 -> one-way 0.45.
    assert rebalance.turnover(prev, new) == pytest.approx(0.45)


def test_turnover_extremes():
    book = {"A": 0.5, "B": 0.5}
    assert rebalance.turnover(book, book) == 0.0
    assert rebalance.turnover(book, {"C": 0.5, "D": 0.5}) == pytest.approx(1.0)
    assert rebalance.turnover(None, book) == pytest.approx(0.5)  # inception
    assert rebalance.turnover(book, None) == pytest.approx(0.5)  # liquidation


def test_trades_are_signed_deltas_over_union():
    out = rebalance.trades({"A": 0.5, "B": 0.5}, {"A": 0.4, "C": 0.3})
    assert list(out.index) == ["A", "B", "C"]
    assert out.tolist() == pytest.approx([-0.1, -0.5, 0.3])


def test_trades_input_validation():
    with pytest.raises(ValueError, match="duplicate"):
        rebalance.trades(pd.Series([0.5, 0.5], index=["A", "A"]), {"B": 1.0})
    with pytest.raises(ValueError, match="undefined"):
        rebalance.trades({"A": float("nan")}, {"B": 1.0})

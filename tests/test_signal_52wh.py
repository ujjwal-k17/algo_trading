"""Acceptance tests for src/signal_52wh.py (Stage 2, plan_52wh.md): signal at
date t is unchanged when post-t rows are appended (no look-ahead); Q1 = the
far-from-high bucket; universe restriction and short-history exclusion."""

import pandas as pd
import pytest

from src import signal_52wh

N = 253  # one row more than the 252 window
DATES = pd.bdate_range("2020-01-01", periods=N)
T = DATES[-1]

# close as a fraction of a flat 100 high → nearness is the fraction itself.
FRACS = {"V": 20, "W": 40, "X": 60, "Y": 80, "Z": 100}


def panel(symbols=FRACS) -> pd.DataFrame:
    rows = [
        {"date": d, "symbol": s, "close": c, "high": 100}
        for s, c in symbols.items()
        for d in DATES
    ]
    return pd.DataFrame(rows)


def test_nearness_values_ranks_and_buckets():
    out = signal_52wh.signal_at(panel(), list(FRACS), T)
    assert out.loc["V", "nearness"] == pytest.approx(0.20)
    assert out.loc["Z", "nearness"] == pytest.approx(1.00)
    # 5 symbols, 5 buckets: exactly one per bucket, Q1 = farthest from high.
    assert list(out.index) == ["V", "W", "X", "Y", "Z"]
    assert list(out["bucket"]) == ["Q1", "Q2", "Q3", "Q4", "Q5"]


def test_no_look_ahead_on_appended_rows():
    base = signal_52wh.signal_at(panel(), list(FRACS), T)
    future = pd.DataFrame(
        {"date": d, "symbol": s, "close": 1000, "high": 2000}
        for s in FRACS
        for d in pd.bdate_range(T + pd.Timedelta(days=1), periods=5)
    )
    extended = pd.concat([panel(), future], ignore_index=True)
    pd.testing.assert_frame_equal(
        signal_52wh.signal_at(extended, list(FRACS), T), base
    )


def test_rank_is_within_universe_only():
    out = signal_52wh.signal_at(panel(), ["V", "Z"], T)
    assert list(out.index) == ["V", "Z"]
    # V is now rank 1/2 → pct 0.5 → Q3 of 5, not the Q1 it gets in the
    # full universe: ranks are relative to the PIT universe as-of the date.
    assert list(out["bucket"]) == ["Q3", "Q5"]


def test_short_history_symbol_excluded():
    short = pd.DataFrame(
        {"date": d, "symbol": "NEW", "close": 90, "high": 100}
        for d in DATES[-100:]
    )
    out = signal_52wh.signal_at(
        pd.concat([panel(), short], ignore_index=True), list(FRACS) + ["NEW"], T
    )
    assert "NEW" not in out.index  # < 252 highs → no defined nearness
    assert list(out.index) == ["V", "W", "X", "Y", "Z"]


def test_missing_trading_date_raises():
    with pytest.raises(ValueError, match="not a trading date"):
        signal_52wh.signal_at(panel(), list(FRACS), T + pd.Timedelta(days=1))


def test_bucket_count_validation():
    with pytest.raises(ValueError, match="n_buckets"):
        signal_52wh.signal_at(panel(), list(FRACS), T, n_buckets=1)


def test_signal_frame_has_no_outcome_columns():
    # Features only (contamination wall): no return-like columns may exist.
    out = signal_52wh.signal_at(panel(), list(FRACS), T)
    assert set(out.columns) == {"nearness", "cs_rank", "bucket"}


def test_canonical_expression_string_unchanged():
    # The string is the artifact that gets hash-frozen (plan_52wh.md B1/B2).
    assert signal_52wh.NEARNESS_EXPR == "close / rolling_max(high, 252)"

"""Acceptance tests for src/expr.py (Stage 2, plan_52wh.md B1): evaluation vs
hand-computed frames; any unknown token is a hard error — no silent prose."""

import numpy as np
import pandas as pd
import pytest

from src.expr import ExprError, evaluate

DATES = pd.bdate_range("2020-01-01", periods=5)


def panel() -> pd.DataFrame:
    rows = []
    for sym, closes, highs in [
        ("X", [10, 12, 11, 13, 9], [11, 12, 12, 14, 10]),
        ("Y", [20, 18, 22, 21, 25], [21, 19, 23, 22, 26]),
    ]:
        for d, c, h in zip(DATES, closes, highs):
            rows.append({"date": d, "symbol": sym, "close": c, "high": h})
    return pd.DataFrame(rows)


def test_field_lookup_is_the_pivot():
    wide = evaluate("close", panel())
    assert list(wide.columns) == ["X", "Y"]
    assert wide.loc[DATES[3], "X"] == 13
    assert wide.loc[DATES[4], "Y"] == 25


def test_ref_shifts_per_symbol():
    wide = evaluate("ref(close, 1)", panel())
    assert np.isnan(wide.loc[DATES[0], "X"])
    assert wide.loc[DATES[1], "X"] == 10
    assert wide.loc[DATES[4], "Y"] == 21


def test_rolling_max_full_window_required():
    wide = evaluate("rolling_max(high, 3)", panel())
    assert np.isnan(wide.loc[DATES[1], "X"])  # only 2 obs
    assert wide.loc[DATES[2], "X"] == 12  # max(11, 12, 12)
    assert wide.loc[DATES[4], "X"] == 14  # max(12, 14, 10)
    assert wide.loc[DATES[4], "Y"] == 26


def test_cs_rank_percentile_per_date():
    wide = evaluate("cs_rank(close)", panel())
    assert wide.loc[DATES[0], "X"] == 0.5  # 10 < 20
    assert wide.loc[DATES[0], "Y"] == 1.0


def test_arithmetic_nearness_hand_check():
    wide = evaluate("close / rolling_max(high, 3)", panel())
    assert wide.loc[DATES[4], "X"] == pytest.approx(9 / 14)
    assert np.isnan(wide.loc[DATES[1], "Y"])


def test_constants_and_unary_minus():
    wide = evaluate("-close + close * 2", panel())
    pd.testing.assert_frame_equal(wide, evaluate("close", panel()))


@pytest.mark.parametrize(
    "bad",
    [
        "volume_weighted(close)",          # unknown function
        "typo_field / close",              # unknown field
        "close ** 2",                      # operator outside grammar
        "close > 1",                       # comparison
        "close.shift(1)",                  # attribute access
        "__import__('os')",                # not in the registry
        "lambda: 1",                       # lambda
        "rolling_max(high, n=3)",          # keyword args
        "rolling_max(high, 2.5)",          # non-int window
        "rolling_max(3, high)",            # swapped arg kinds
        "ref(close)",                      # arity
        "1 + 2",                           # reduces to a scalar
        "close / 'x'",                     # non-numeric literal
    ],
)
def test_unknown_tokens_hard_error(bad):
    with pytest.raises(ExprError):
        evaluate(bad, panel())


def test_duplicate_rows_rejected():
    dup = pd.concat([panel(), panel().head(1)], ignore_index=True)
    with pytest.raises(ExprError, match="duplicate"):
        evaluate("close", dup)


def test_missing_panel_columns_rejected():
    with pytest.raises(ExprError, match="missing required column"):
        evaluate("close", panel().drop(columns=["symbol"]))

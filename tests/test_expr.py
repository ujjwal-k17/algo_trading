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
        # "close > 1" was here until 2026-07-20: comparison was deliberately
        # moved INTO the grammar by the SPEC-SRA-01 §6 extension. Covered now by
        # test_comparison_against_scalar_literal and the NaN-preservation tests.
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


# --- SPEC-SRA-01 §6 grammar extension: rolling moments + NaN-preserving compare ---

def vol_panel() -> pd.DataFrame:
    """Panel with a volume column and a deliberate NaN hole in X's close."""
    rows = []
    spec = [
        ("X", [10.0, 12.0, np.nan, 13.0, 9.0], [100, 200, 300, 400, 500]),
        ("Y", [20.0, 18.0, 22.0, 21.0, 25.0], [50, 60, 70, 80, 90]),
    ]
    for sym, closes, vols in spec:
        for d, c, v in zip(DATES, closes, vols):
            rows.append({"date": d, "symbol": sym, "close": c, "volume": float(v)})
    return pd.DataFrame(rows)


def test_rolling_mean_full_window_required():
    wide = evaluate("rolling_mean(volume, 3)", vol_panel())
    assert np.isnan(wide.loc[DATES[1], "Y"])          # only 2 obs
    assert wide.loc[DATES[2], "Y"] == pytest.approx(60.0)   # (50+60+70)/3
    assert wide.loc[DATES[4], "Y"] == pytest.approx(80.0)   # (70+80+90)/3


def test_rolling_sum_full_window_required():
    wide = evaluate("rolling_sum(volume, 2)", vol_panel())
    assert np.isnan(wide.loc[DATES[0], "X"])
    assert wide.loc[DATES[1], "X"] == pytest.approx(300.0)
    assert wide.loc[DATES[4], "Y"] == pytest.approx(170.0)


def test_rolling_std_is_sample_ddof1():
    wide = evaluate("rolling_std(volume, 3)", vol_panel())
    # Y volumes 50,60,70 -> sample std (ddof=1) = 10.0; population would be ~8.165
    assert wide.loc[DATES[2], "Y"] == pytest.approx(10.0)


def test_one_nan_blocks_the_whole_rolling_window():
    """TRAP 1, pinned as a test: min_periods=n means a single hole propagates.

    This is the documented, deliberate behaviour — the guard belongs upstream in
    the panel builder, not in a loosened min_periods here.
    """
    wide = evaluate("rolling_mean(close, 2)", vol_panel())
    assert np.isnan(wide.loc[DATES[2], "X"])   # the hole itself
    assert np.isnan(wide.loc[DATES[3], "X"])   # window still contains the hole
    assert wide.loc[DATES[4], "X"] == pytest.approx(11.0)  # (13+9)/2, clear of it


def test_comparison_returns_float_indicator():
    wide = evaluate("close > ref(close, 1)", vol_panel())
    assert wide.loc[DATES[1], "X"] == 1.0    # 12 > 10
    assert wide.loc[DATES[1], "Y"] == 0.0    # 18 < 20
    assert wide.dtypes.unique().tolist() == [np.dtype("float64")]


def test_comparison_preserves_nan_rather_than_collapsing_to_false():
    """The whole point: NaN > NaN is False in pandas; here it must stay NaN.

    Collapsing to 0.0 would silently promote a missing observation into a real
    'did not go up' data point — the TRAP 1 failure mode in a different costume.
    """
    wide = evaluate("close > ref(close, 1)", vol_panel())
    assert np.isnan(wide.loc[DATES[2], "X"])   # close is NaN
    assert np.isnan(wide.loc[DATES[3], "X"])   # prior close is NaN
    assert wide.loc[DATES[4], "X"] == 0.0      # 9 < 13, both known


def test_comparison_against_scalar_literal():
    wide = evaluate("volume > 100", vol_panel())
    assert wide.loc[DATES[0], "X"] == 0.0
    assert wide.loc[DATES[1], "X"] == 1.0


def test_all_comparison_operators_in_grammar():
    for op, at_d1_X in [(">", 1.0), ("<", 0.0), (">=", 1.0), ("<=", 0.0)]:
        wide = evaluate(f"close {op} ref(close, 1)", vol_panel())
        assert wide.loc[DATES[1], "X"] == at_d1_X, op


def test_sra_feature_8_down_day_absorption_composes():
    """The spec's most complex expression must actually evaluate end to end."""
    expr = "rolling_sum((close>ref(close,1)) * volume, 3) / rolling_sum(volume, 3)"
    wide = evaluate(expr, vol_panel())
    # Y: up-days at d1? 18<20 no; d2 22>18 yes; d3 21<22 no -> (0*60+70*1+0*80)/210
    assert wide.loc[DATES[3], "Y"] == pytest.approx(70.0 / 210.0)
    # a volume-share ratio is bounded in [0, 1] wherever it is defined at all
    defined = wide.stack().dropna()
    assert not defined.empty
    assert ((defined >= 0.0) & (defined <= 1.0)).all()
    # X stays NaN throughout: its close hole never clears a 3-window in 5 sessions
    assert wide["X"].isna().all()


def test_chained_comparison_is_rejected():
    with pytest.raises(ExprError, match="chained"):
        evaluate("ref(close,1) < close < volume", vol_panel())


def test_equality_operators_are_outside_the_grammar():
    with pytest.raises(ExprError, match="unsupported comparison"):
        evaluate("close == volume", vol_panel())


def test_comparison_of_two_scalars_is_rejected():
    with pytest.raises(ExprError, match="at least one field"):
        evaluate("1 > 2", vol_panel())


def test_new_rolling_funcs_still_reject_non_int_windows():
    for fn in ("rolling_mean", "rolling_std", "rolling_sum"):
        with pytest.raises(ExprError, match="must be an int"):
            evaluate(f"{fn}(volume, close)", vol_panel())

import math

import numpy as np
import pandas as pd
import pytest

from src import metrics


def test_annualized_return_compounds():
    # 1% per period for 252 periods -> 1.01**252 - 1
    r = pd.Series([0.01] * 252)
    assert metrics.annualized_return(r) == pytest.approx(1.01**252 - 1, rel=1e-9)


def test_sharpe_matches_hand_calc():
    rng = np.random.default_rng(0)
    r = pd.Series(rng.normal(0.0005, 0.01, 2000))
    expected = r.mean() / r.std(ddof=1) * math.sqrt(252)
    assert metrics.sharpe(r) == pytest.approx(expected)


def test_max_drawdown_on_known_path():
    # +10% then -50% then +10%: trough is 1.1*0.5 = 0.55 vs peak 1.1 -> -50%
    assert metrics.max_drawdown(pd.Series([0.10, -0.50, 0.10])) == pytest.approx(-0.50)


def test_zero_vol_series_does_not_divide_by_zero():
    assert metrics.sharpe(pd.Series([0.001] * 10)) == 0.0
    assert metrics.information_ratio(pd.Series([0.01] * 10), pd.Series([0.01] * 10)) == 0.0


def test_information_ratio_is_zero_against_itself():
    rng = np.random.default_rng(1)
    r = pd.Series(rng.normal(0, 0.01, 500))
    assert metrics.information_ratio(r, r) == 0.0


def test_norm_ppf_round_trips():
    for p in (0.01, 0.25, 0.5, 0.975, 0.999):
        assert metrics._norm_cdf(metrics._norm_ppf(p)) == pytest.approx(p, abs=1e-6)


def test_expected_max_sharpe_rises_with_trial_count():
    a = metrics.expected_max_sharpe(10, 0.5)
    b = metrics.expected_max_sharpe(100, 0.5)
    assert 0 < a < b, "searching more strategies must raise the bar"


def test_deflated_sharpe_punishes_selection():
    """Same returns, more trials searched -> lower confidence. The whole point."""
    rng = np.random.default_rng(2)
    r = pd.Series(rng.normal(0.0006, 0.01, 1500))
    few = metrics.deflated_sharpe(r, n_trials=2, trial_sr_std=0.5)
    many = metrics.deflated_sharpe(r, n_trials=60, trial_sr_std=0.5)
    assert few["dsr"] > many["dsr"]
    assert many["sr0"] > few["sr0"]


def test_deflated_sharpe_reports_nan_rather_than_a_flattering_number():
    """Extreme higher moments must surface as 'undefined', never as a high DSR."""
    r = pd.Series([0.0] * 200 + [5.0])  # one enormous outlier: huge skew/kurtosis
    res = metrics.deflated_sharpe(r, n_trials=10, trial_sr_std=0.5)
    assert math.isnan(res["dsr"]) or 0.0 <= res["dsr"] <= 1.0
    if math.isnan(res["dsr"]):
        assert "undefined" in res["note"]


def test_stationary_bootstrap_indices_are_in_range_and_blocky():
    rng = np.random.default_rng(3)
    idx = metrics.stationary_bootstrap_indices(500, 20.0, rng)
    assert idx.min() >= 0 and idx.max() < 500 and idx.size == 500
    # With mean block 20, consecutive-index steps should dominate over iid draws.
    consecutive = np.mean(np.diff(idx) == 1)
    assert consecutive > 0.7


def test_spa_does_not_reject_pure_noise():
    """No model beats the benchmark -> large p-value."""
    rng = np.random.default_rng(4)
    d = pd.DataFrame(rng.normal(0, 0.01, (800, 5)))
    out = metrics.hansen_spa(d, n_boot=200, seed=1)
    assert out["p_value"] > 0.10


def test_spa_rejects_a_genuinely_superior_model():
    rng = np.random.default_rng(5)
    d = pd.DataFrame(rng.normal(0, 0.01, (800, 5)))
    d[3] += 0.004  # a large, persistent edge
    out = metrics.hansen_spa(d, n_boot=200, seed=1)
    assert out["p_value"] < 0.05
    assert out["best_model"] == 3


def test_spa_is_harder_to_pass_with_more_searched_models():
    """Data-snooping correction: the same winner among more candidates is weaker."""
    rng = np.random.default_rng(6)
    base = rng.normal(0, 0.01, (600, 1)) + 0.0016
    noise = rng.normal(0, 0.01, (600, 24))
    lonely = metrics.hansen_spa(pd.DataFrame(base), n_boot=300, seed=2)["p_value"]
    crowded = metrics.hansen_spa(
        pd.DataFrame(np.hstack([base, noise])), n_boot=300, seed=2
    )["p_value"]
    assert crowded >= lonely


def test_summary_includes_benchmark_block_only_when_given():
    r = pd.Series(np.random.default_rng(7).normal(0, 0.01, 300))
    assert "information_ratio" not in metrics.summary(r)
    assert "information_ratio" in metrics.summary(r, benchmark=r * 0.5)

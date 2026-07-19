"""Runner scoring + kill-line tests.

Deliberately synthetic: executing the engine against the real panel would be
outcome contact, i.e. an unregistered trial, which is the exact thing the gate
exists to prevent. So the scoring path is proven on constructed return series
whose verdict is known in advance.
"""

import importlib.util
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

_spec = importlib.util.spec_from_file_location(
    "run_trial_52wh", REPO / "scripts" / "run_trial_52wh.py"
)
runner = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(runner)

from src import backtest_52wh  # noqa: E402


def _arm(label, net, gross=None, turnover=0.05, n_rebal=24):
    idx = net.index
    rebal_idx = idx[:: max(1, len(idx) // n_rebal)]
    return backtest_52wh.BacktestResult(
        label=label,
        gross_returns=(gross if gross is not None else net).rename(f"{label}_gross"),
        net_returns=net.rename(f"{label}_net"),
        turnover=pd.Series(turnover, index=rebal_idx),
        costs=pd.Series(0.0004, index=rebal_idx),
        n_holdings=pd.Series(400, index=rebal_idx, dtype="Int64"),
        diagnostics={"frozen_symbol_days": 7},
    )


def _result(screened, unscreened):
    return {
        "arms": {"screened": _arm("screened", screened),
                 "unscreened": _arm("unscreened", unscreened)},
        "schedule": pd.DataFrame(),
        "params": {"band": "201-1000", "freq": "Q"},
    }


def _series(n, mu, sigma, seed):
    idx = pd.bdate_range("2018-01-01", periods=n)
    return pd.Series(np.random.default_rng(seed).normal(mu, sigma, n), index=idx)


def test_kill_line_fires_when_the_screen_adds_nothing():
    """A screen with no edge must be declared DEAD, mechanically."""
    bench = _series(1500, 0.0004, 0.010, 1)
    unscreened = bench + _series(1500, 0.0000, 0.004, 2)
    screened = unscreened - 0.00005  # strictly worse after costs
    out = runner.score(_result(screened, unscreened), bench, n_trials=55, trial_sr_std=0.5)
    assert out["kill_line"]["verdict"] == "DEAD"
    assert out["kill_line"]["reasons"]


def test_kill_line_survives_a_genuinely_strong_screen():
    bench = _series(1500, 0.0002, 0.010, 3)
    unscreened = bench + _series(1500, 0.0000, 0.003, 4)
    # A real increment is noisy; a constant one is degenerate (see the
    # degenerate test below) and cannot be studentized by SPA.
    screened = unscreened + 0.0006 + _series(1500, 0.0, 0.0015, 10)
    out = runner.score(_result(screened, unscreened), bench, n_trials=55, trial_sr_std=0.5)
    assert out["kill_line"]["verdict"] == "SURVIVES"
    assert out["increment"]["ir_delta"] > 0
    assert out["inference"]["spa_screen_vs_unscreened"]["p_value"] < 0.10


def test_degenerate_spa_withholds_the_verdict_instead_of_killing():
    """A riskless (zero-variance) increment must not be reported as DEAD — that
    would blame the strategy for what is really a modelling artifact."""
    bench = _series(1200, 0.0002, 0.010, 11)
    unscreened = bench + _series(1200, 0.0, 0.003, 12)
    screened = unscreened + 0.0006  # exactly constant differential
    out = runner.score(_result(screened, unscreened), bench, n_trials=55, trial_sr_std=0.5)
    assert out["kill_line"]["verdict"] == "INCONCLUSIVE"
    assert out["inference"]["spa_screen_vs_unscreened"]["degenerate_models"] == [0]


def test_turnover_bust_kills_even_with_alpha():
    """Spec §5: a variant that busts the budget is dead regardless of gross."""
    bench = _series(1200, 0.0002, 0.010, 5)
    unscreened = bench + _series(1200, 0.0, 0.003, 6)
    screened = unscreened + 0.0006
    res = _result(screened, unscreened)
    # 60 rebalances a year at 100% one-way each
    idx = screened.index[::20]
    res["arms"]["screened"].turnover = pd.Series(1.0, index=idx)
    out = runner.score(res, bench, n_trials=55, trial_sr_std=0.5)
    assert out["kill_line"]["verdict"] == "DEAD"
    assert any("turnover" in r for r in out["kill_line"]["reasons"])


def test_score_reports_both_arms_and_the_increment():
    bench = _series(900, 0.0003, 0.010, 7)
    out = runner.score(
        _result(bench + 0.0001, bench), bench, n_trials=55, trial_sr_std=0.5
    )
    assert set(out["arms"]) == {"screened", "unscreened"}
    for arm in out["arms"].values():
        assert "information_ratio" in arm["net"]
        assert arm["frozen_symbol_days"] == 7
    assert "ir_delta" in out["increment"]
    assert out["n_trials_charged"] == 55


def test_cumulative_trial_count_excludes_bookkeeping_rows():
    """Freeze/convention/result rows are not trials — they must not inflate DSR."""
    n = runner.cumulative_trial_count()
    assert n >= runner.INHERITED_TRIALS
    # FREEZE-52WH-0001 carries data_tier 'n/a' and must be excluded.
    assert n == runner.INHERITED_TRIALS + sum(
        1 for r in runner.spec_guard.register_rows()
        if r["data_tier"] not in ("n/a", "")
        and not r["trial_id"].startswith(("INHERITED-", "CONVENTION-"))
        and not r["trial_id"].endswith("-RESULT")
    )


def test_deflation_bar_rises_with_the_register_count():
    bench = _series(1200, 0.0002, 0.010, 8)
    unscreened = bench + _series(1200, 0.0, 0.003, 9)
    screened = unscreened + 0.0003
    res = _result(screened, unscreened)
    few = runner.score(res, bench, n_trials=2, trial_sr_std=0.5)
    many = runner.score(_result(screened, unscreened), bench, n_trials=200, trial_sr_std=0.5)
    assert (few["inference"]["deflated_sharpe_screened_active"]["dsr"]
            > many["inference"]["deflated_sharpe_screened_active"]["dsr"])

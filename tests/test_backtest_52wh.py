"""Stage 5 engine tests. Synthetic panels only — no real price data is touched
here, so the build stays outcome-blind until C1 is authorized."""

import numpy as np
import pandas as pd
import pytest

from src import backtest_52wh, rebalance, spec_guard

REAL_STAMP = {"spec_id": "SPEC-52WH-01", "trial_id": "FREEZE-52WH-0001"}


def _panel(symbols, n_days=400, seed=0, start="2017-01-02"):
    """Long OHLC panel on business days with a mild upward drift per symbol."""
    rng = np.random.default_rng(seed)
    dates = pd.bdate_range(start, periods=n_days)
    rows = []
    for i, sym in enumerate(symbols):
        steps = rng.normal(0.0004 + i * 0.0002, 0.012, n_days)
        close = 100 * np.cumprod(1 + steps)
        rows.append(pd.DataFrame({
            "date": dates, "symbol": sym, "open": close, "high": close * 1.01,
            "low": close * 0.99, "close": close, "volume": 10_000,
        }))
    return pd.concat(rows, ignore_index=True)


def _pit_store(symbols, effective="2016-12-31", announce="2017-01-25"):
    return pd.DataFrame({
        "symbol": symbols,
        "field": "mcap_rank",
        "effective_date": pd.Timestamp(effective),
        "announce_date": pd.Timestamp(announce),
        "value": range(201, 201 + len(symbols)),
        "source": "synthetic",
    })


# --- the governance door -----------------------------------------------------

def test_engine_refuses_without_a_stamp():
    syms = [f"S{i}" for i in range(10)]
    with pytest.raises(spec_guard.SpecGuardError, match="provenance stamp"):
        backtest_52wh.run_walk_forward(
            _panel(syms), _pit_store(syms), stamp={}, verbose=False
        )


def test_engine_refuses_a_forged_stamp():
    """A hand-built dict naming an unregistered trial must not open the door."""
    syms = [f"S{i}" for i in range(10)]
    forged = {"spec_id": "SPEC-52WH-01", "trial_id": "NOT-REGISTERED",
              "spec_sha256": "deadbeef"}
    with pytest.raises(spec_guard.SpecGuardError):
        backtest_52wh.run_walk_forward(
            _panel(syms), _pit_store(syms), stamp=forged, verbose=False
        )


def test_market_cap_weighting_is_blocked_not_faked():
    syms = [f"S{i}" for i in range(10)]
    with pytest.raises(NotImplementedError, match="(?i)absolute mcap"):
        backtest_52wh.run_walk_forward(
            _panel(syms), _pit_store(syms), stamp=REAL_STAMP,
            weighting="MW", verbose=False,
        )


# --- mechanics ---------------------------------------------------------------

def _run(symbols, **kw):
    kw.setdefault("verbose", False)
    kw.setdefault("band", "201-1000")
    return backtest_52wh.run_walk_forward(
        _panel(symbols, n_days=kw.pop("n_days", 900)),
        _pit_store(symbols), stamp=REAL_STAMP, **kw,
    )


def test_runs_and_produces_two_aligned_arms():
    out = _run([f"S{i}" for i in range(20)])
    a, b = out["arms"]["screened"], out["arms"]["unscreened"]
    assert a.net_returns.index.equals(b.net_returns.index)
    assert len(a.net_returns) > 100
    assert not out["schedule"].empty


def test_screen_excludes_the_bottom_bucket():
    out = _run([f"S{i}" for i in range(20)])
    sched = out["schedule"]
    # Q1 of 5 buckets over ~20 ranked names -> roughly a fifth removed.
    assert (sched["screened_holdings"] < sched["tradeable"]).all()


def test_net_returns_are_below_gross_whenever_trading_happens():
    out = _run([f"S{i}" for i in range(20)])
    for arm in out["arms"].values():
        assert (arm.costs > 0).any(), "a rebalance must cost something"
        diff = arm.gross_returns - arm.net_returns
        assert (diff >= -1e-12).all(), "costs may never improve a return"
        assert diff.sum() == pytest.approx(arm.costs.sum(), rel=1e-9)


def test_no_lookahead_appending_future_rows_leaves_history_unchanged():
    """The decisive test: extending the panel must not alter earlier returns."""
    syms = [f"S{i}" for i in range(15)]
    # Slice the SAME panel — a same-seed regeneration at a different length
    # advances the RNG differently per symbol and would not be prefix-identical.
    long = _panel(syms, n_days=1000, seed=3)
    keep = sorted(long["date"].unique())[:800]
    short = long.loc[long["date"].isin(set(keep))]
    store = _pit_store(syms)
    a = backtest_52wh.run_walk_forward(short, store, stamp=REAL_STAMP, verbose=False)
    b = backtest_52wh.run_walk_forward(long, store, stamp=REAL_STAMP, verbose=False)
    common = a["arms"]["screened"].net_returns.index.intersection(
        b["arms"]["screened"].net_returns.index
    )
    # Compare only dates strictly before the short panel's final rebalance, since
    # the short run's last partial period is a stub the long run reschedules.
    cutoff = a["arms"]["screened"].turnover.index[-1]
    common = common[common < cutoff]
    assert len(common) > 50
    pd.testing.assert_series_equal(
        a["arms"]["screened"].net_returns.loc[common],
        b["arms"]["screened"].net_returns.loc[common],
    )


def test_execution_lags_the_signal_by_one_session():
    out = _run([f"S{i}" for i in range(12)])
    sched = out["schedule"]
    assert (sched["exec_date"] > sched["signal_date"]).all()


def test_turnover_is_one_way_and_inception_is_a_half():
    out = _run([f"S{i}" for i in range(12)])
    first = out["arms"]["unscreened"].turnover.iloc[0]
    assert first == pytest.approx(0.5), "inception from cash is 0.5 one-way"
    assert (out["arms"]["unscreened"].turnover <= 1.0 + 1e-9).all()


def test_frozen_symbol_days_are_counted_not_hidden():
    syms = [f"S{i}" for i in range(12)]
    panel = _panel(syms, n_days=900)
    # Delist one name partway: drop its rows after a date.
    cut = panel["date"].quantile(0.8)
    panel = panel.loc[~((panel["symbol"] == "S3") & (panel["date"] > cut))]
    out = backtest_52wh.run_walk_forward(
        panel, _pit_store(syms), stamp=REAL_STAMP, verbose=False
    )
    total_frozen = sum(a.diagnostics["frozen_symbol_days"] for a in out["arms"].values())
    assert total_frozen > 0, "a delisting must surface in the diagnostics"


def test_quarterly_schedule_matches_the_rebalance_calendar():
    syms = [f"S{i}" for i in range(12)]
    panel = _panel(syms, n_days=900)
    out = backtest_52wh.run_walk_forward(
        panel, _pit_store(syms), stamp=REAL_STAMP, freq="Q", verbose=False
    )
    expected = set(rebalance.rebalance_dates(panel["date"].unique(), "Q"))
    assert set(out["schedule"]["signal_date"]).issubset(expected)


def test_annual_turnover_is_reported_for_the_spec_budget():
    out = _run([f"S{i}" for i in range(20)])
    at = out["arms"]["screened"].annual_turnover
    assert at > 0 and at < 3.0, "quarterly screen churn should sit under the 300% budget"


def test_monthly_rebalancing_costs_more_than_quarterly():
    syms = [f"S{i}" for i in range(20)]
    panel = _panel(syms, n_days=900)
    store = _pit_store(syms)
    q = backtest_52wh.run_walk_forward(panel, store, stamp=REAL_STAMP, freq="Q", verbose=False)
    m = backtest_52wh.run_walk_forward(panel, store, stamp=REAL_STAMP, freq="M", verbose=False)
    assert (m["arms"]["screened"].costs.sum()
            > q["arms"]["screened"].costs.sum()), "more rebalances, more friction"


def test_higher_slippage_strictly_lowers_net_returns():
    syms = [f"S{i}" for i in range(20)]
    panel = _panel(syms, n_days=900)
    store = _pit_store(syms)
    cheap = backtest_52wh.run_walk_forward(
        panel, store, stamp=REAL_STAMP, slippage_per_side=0.0005, verbose=False)
    dear = backtest_52wh.run_walk_forward(
        panel, store, stamp=REAL_STAMP, slippage_per_side=0.0050, verbose=False)
    assert (dear["arms"]["screened"].net_returns.sum()
            < cheap["arms"]["screened"].net_returns.sum())

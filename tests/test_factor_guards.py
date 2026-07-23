"""Tests for src/factor_guards.py — the Brent/WTI corrupted-bar guards."""

import numpy as np
import pandas as pd
import pytest

from src.factor_guards import (
    FactorGuardError,
    assert_comoving_divergence,
    assert_return_agreement,
)


def _pair(n=60, noise=0.001, seed=7):
    """Two co-moving price series: shared random walk + small idio noise."""
    rng = np.random.default_rng(seed)
    idx = pd.bdate_range("2026-01-01", periods=n)
    common = rng.normal(0, 0.01, n).cumsum()
    a = pd.Series(100 * np.exp(common), index=idx)
    b = pd.Series(80 * np.exp(common + rng.normal(0, noise, n).cumsum()), index=idx)
    return a, b


class TestReturnAgreement:
    def test_same_series_two_sources_passes(self):
        a, _ = _pair()
        b = a * 1.0001  # constant scale = identical returns
        corr = assert_return_agreement(a, b, "A", "B")
        assert corr > 0.999

    def test_disagreeing_sources_raise(self):
        a, _ = _pair()
        rng = np.random.default_rng(1)
        b = pd.Series(
            100 * np.exp(rng.normal(0, 0.01, len(a)).cumsum()), index=a.index
        )
        with pytest.raises(FactorGuardError, match="disagree"):
            assert_return_agreement(a, b, "A", "B")

    def test_hollow_overlap_raises(self):
        a, b = _pair()
        with pytest.raises(FactorGuardError, match="hollow"):
            assert_return_agreement(a.iloc[:5], b.iloc[:5], "A", "B")


class TestComovingDivergence:
    def test_clean_pair_passes_and_returns_series(self):
        a, b = _pair()
        div = assert_comoving_divergence(a, b, "BRENT", "WTI")
        assert isinstance(div, pd.Series)
        assert (div <= 0.05).all()

    def test_single_corrupted_bar_raises_and_names_the_date(self):
        # reproduce the 2026-07-23 shape: one bar decoupling ~14%
        a, b = _pair()
        a.iloc[-1] *= np.exp(-0.074)
        b.iloc[-1] *= np.exp(+0.064)
        with pytest.raises(FactorGuardError) as exc:
            assert_comoving_divergence(a, b, "BRENT", "WTI")
        msg = str(exc.value)
        assert "corrupted/unsettled" in msg
        assert str(a.index[-1].date()) in msg

    def test_missing_dates_are_not_forward_filled(self):
        # a gap in one leg must shrink the intersection, not fabricate a return
        a, b = _pair()
        a_gappy = a.drop(a.index[30])
        div = assert_comoving_divergence(a_gappy, b, "BRENT", "WTI")
        # the dropped date and its successor both vanish from the tested set
        assert a.index[30] not in div.index

    def test_hollow_overlap_raises(self):
        a, b = _pair()
        with pytest.raises(FactorGuardError, match="hollow"):
            assert_comoving_divergence(a.iloc[:10], b.iloc[-10:], "A", "B")

    def test_tail_scope_tolerates_real_historical_decoupling(self):
        # Apr-2020 shape: a genuine large divergence deep in history must NOT
        # trip a tail-scoped guard (the guard's own base-rate check, TRAP 10)
        a, b = _pair()
        a.iloc[20] *= np.exp(-0.20)  # real super-contango-style day
        div = assert_comoving_divergence(a, b, "BRENT", "WTI", tail_bars=5)
        assert div.max() > 0.05  # reported, not gated

    def test_tail_scope_still_catches_corrupted_last_bar(self):
        a, b = _pair()
        a.iloc[20] *= np.exp(-0.20)  # real historical decoupling present
        a.iloc[-1] *= np.exp(-0.074)  # AND a corrupted fresh bar
        b.iloc[-1] *= np.exp(+0.064)
        with pytest.raises(FactorGuardError, match="last 5 bars"):
            assert_comoving_divergence(a, b, "BRENT", "WTI", tail_bars=5)

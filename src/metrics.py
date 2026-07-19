"""Performance statistics and multiple-testing inference (SPEC-52WH-01 §7, Stage 5).

In-repo by decision: the qlib rejection stands, and an external backtest
framework would put the inference layer outside the governance trail. Two
families live here:

* descriptive — annualized return/vol, Sharpe, information ratio vs a
  benchmark, max drawdown, skew (the spec's -1.5-skew crash profile is the
  risk being managed);
* inferential — Deflated Sharpe Ratio (Bailey & Lopez de Prado 2014) and
  Hansen's (2005) SPA test with a Politis-Romano stationary bootstrap, both
  charged against the register's CUMULATIVE trial count. That count is the
  point: 51+ inherited trials mean a nominally significant Sharpe here is
  mostly selection, and these two tests are what say so out loud.

Nothing in this module knows about 52WH specifically — it takes return series.
"""

from __future__ import annotations

import math

import numpy as np
import pandas as pd

TRADING_DAYS = 252
EULER_MASCHERONI = 0.5772156649015329

# A constant series has a floating-point std of ~1e-19, not 0, so an `== 0`
# guard lets Sharpe explode to ~1e16 instead of reporting 0. Any daily vol
# below this is degenerate, not a strategy.
_VOL_EPS = 1e-12


def _clean(returns) -> np.ndarray:
    r = pd.Series(returns, dtype=float).dropna().to_numpy()
    if r.size < 2:
        raise ValueError("need at least 2 return observations")
    return r


def annualized_return(returns, periods: int = TRADING_DAYS) -> float:
    """Geometric (CAGR-style) annualization — compounding matters over 6+ years."""
    r = _clean(returns)
    growth = float(np.prod(1.0 + r))
    if growth <= 0:
        return -1.0
    return growth ** (periods / r.size) - 1.0


def annualized_vol(returns, periods: int = TRADING_DAYS) -> float:
    return float(np.std(_clean(returns), ddof=1) * math.sqrt(periods))


def sharpe(returns, rf: float = 0.0, periods: int = TRADING_DAYS) -> float:
    """Annualized Sharpe on arithmetic excess returns. ``rf`` is per-period."""
    r = _clean(returns) - rf
    sd = float(np.std(r, ddof=1))
    if sd < _VOL_EPS:
        return 0.0
    return float(np.mean(r)) / sd * math.sqrt(periods)


def information_ratio(returns, benchmark, periods: int = TRADING_DAYS) -> float:
    """Annualized active return / tracking error. Both series must be aligned."""
    a = pd.Series(returns, dtype=float)
    b = pd.Series(benchmark, dtype=float)
    active = (a - b).dropna()
    if active.size < 2:
        raise ValueError("need at least 2 aligned observations for an IR")
    te = float(active.std(ddof=1))
    if te < _VOL_EPS:
        return 0.0
    return float(active.mean()) / te * math.sqrt(periods)


def max_drawdown(returns) -> float:
    """Most negative peak-to-trough fraction of the compounded curve (<= 0)."""
    curve = np.cumprod(1.0 + _clean(returns))
    return float((curve / np.maximum.accumulate(curve) - 1.0).min())


def skew(returns) -> float:
    r = _clean(returns)
    sd = float(np.std(r, ddof=0))
    if sd < _VOL_EPS:
        return 0.0
    return float(np.mean(((r - r.mean()) / sd) ** 3))


def kurtosis(returns) -> float:
    """NON-excess kurtosis (normal = 3) — the convention DSR expects."""
    r = _clean(returns)
    sd = float(np.std(r, ddof=0))
    if sd < _VOL_EPS:
        return 3.0
    return float(np.mean(((r - r.mean()) / sd) ** 4))


def _norm_cdf(x: float) -> float:
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def _norm_ppf(p: float) -> float:
    """Acklam's inverse-normal approximation (|err| < 1.15e-9) — avoids a scipy
    dependency for the two quantile lookups DSR needs."""
    if not 0.0 < p < 1.0:
        raise ValueError("p must be in (0, 1)")
    a = [-3.969683028665376e+01, 2.209460984245205e+02, -2.759285104469687e+02,
         1.383577518672690e+02, -3.066479806614716e+01, 2.506628277459239e+00]
    b = [-5.447609879822406e+01, 1.615858368580409e+02, -1.556989798598866e+02,
         6.680131188771972e+01, -1.328068155288572e+01]
    c = [-7.784894002430293e-03, -3.223964580411365e-01, -2.400758277161838e+00,
         -2.549732539343734e+00, 4.374664141464968e+00, 2.938163982698783e+00]
    d = [7.784695709041462e-03, 3.224671290700398e-01, 2.445134137142996e+00,
         3.754408661907416e+00]
    plow, phigh = 0.02425, 1 - 0.02425
    if p < plow:
        q = math.sqrt(-2 * math.log(p))
        return (((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5]) / \
               ((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1)
    if p > phigh:
        q = math.sqrt(-2 * math.log(1 - p))
        return -(((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5]) / \
                ((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1)
    q = p - 0.5
    r = q * q
    return (((((a[0]*r+a[1])*r+a[2])*r+a[3])*r+a[4])*r+a[5])*q / \
           (((((b[0]*r+b[1])*r+b[2])*r+b[3])*r+b[4])*r+1)


def expected_max_sharpe(n_trials: int, trial_sr_std: float,
                        periods: int = TRADING_DAYS) -> float:
    """The Sharpe an untalented researcher expects from the BEST of ``n_trials``.

    Bailey & Lopez de Prado's SR0 benchmark. ``trial_sr_std`` is the
    cross-trial standard deviation of ANNUALIZED Sharpes; the return is
    annualized too.

    ASSUMPTION to state in any write-up: the legacy register records trial
    COUNTS, not each trial's Sharpe, so ``trial_sr_std`` is supplied by the
    caller rather than measured. It is the single most consequential input
    here — a larger dispersion of attempted strategies raises the bar.
    """
    if n_trials < 1:
        raise ValueError("n_trials must be >= 1")
    if trial_sr_std <= 0:
        raise ValueError("trial_sr_std must be > 0")
    if n_trials == 1:
        return 0.0
    t = float(n_trials)
    g = EULER_MASCHERONI
    return trial_sr_std * (
        (1 - g) * _norm_ppf(1 - 1 / t) + g * _norm_ppf(1 - 1 / (t * math.e))
    )


def deflated_sharpe(returns, n_trials: int, trial_sr_std: float,
                    periods: int = TRADING_DAYS) -> dict:
    """Probability the observed Sharpe beats the best-of-N-trials null.

    Returns ``sharpe``, ``sr0`` (the deflation benchmark), ``dsr`` (a
    probability — NOT a p-value; low dsr = the result is explainable by
    selection), and the higher-moment inputs. Corrects for non-normality:
    negative skew and fat tails inflate a naive Sharpe, and this family's
    whole risk story is negative skew.
    """
    r = _clean(returns)
    n = r.size
    sr_ann = sharpe(r, periods=periods)
    sr0_ann = expected_max_sharpe(n_trials, trial_sr_std, periods=periods)
    # DSR arithmetic is in per-period units; annualization is a sqrt(periods) scale.
    sr = sr_ann / math.sqrt(periods)
    sr0 = sr0_ann / math.sqrt(periods)
    g3, g4 = skew(r), kurtosis(r)
    denom = 1.0 - g3 * sr + (g4 - 1.0) / 4.0 * sr * sr
    if denom <= 0:
        # Higher moments overwhelm the estimator — report undefined, never a
        # flattering number.
        return {"sharpe": sr_ann, "sr0": sr0_ann, "dsr": float("nan"),
                "skew": g3, "kurtosis": g4, "n_obs": n, "n_trials": n_trials,
                "note": "DSR undefined: non-positive variance term"}
    z = (sr - sr0) * math.sqrt(n - 1) / math.sqrt(denom)
    return {"sharpe": sr_ann, "sr0": sr0_ann, "dsr": _norm_cdf(z),
            "skew": g3, "kurtosis": g4, "n_obs": n, "n_trials": n_trials,
            "note": ""}


def stationary_bootstrap_indices(n: int, block_mean: float, rng) -> np.ndarray:
    """Politis-Romano stationary bootstrap: geometric blocks, circular wrap.

    Preserves the serial dependence that makes naive iid resampling
    overstate significance in return series.
    """
    if n < 1:
        raise ValueError("n must be >= 1")
    if block_mean < 1:
        raise ValueError("block_mean must be >= 1")
    p = 1.0 / block_mean
    idx = np.empty(n, dtype=np.int64)
    cur = rng.integers(0, n)
    for i in range(n):
        if i > 0 and rng.random() < p:
            cur = rng.integers(0, n)
        idx[i] = cur
        cur = (cur + 1) % n
    return idx


def hansen_spa(loss_differentials, n_boot: int = 1000, block_mean: float = 10.0,
               seed: int = 0) -> dict:
    """Hansen (2005) Superior Predictive Ability p-value.

    ``loss_differentials`` is (n_obs x n_models): column k holds d_k,t, the
    per-period OUTPERFORMANCE of model k over the benchmark (higher = better;
    pass excess returns directly). H0: no model beats the benchmark. A large
    p-value means the best model's edge is indistinguishable from luck GIVEN
    that we searched over all the columns.

    Recentering uses Hansen's consistent threshold, which is what makes this
    test less conservative than Reality Check: models with sufficiently
    negative means are recentered to zero rather than dragging the null down.
    """
    d = np.asarray(pd.DataFrame(loss_differentials).dropna(), dtype=float)
    if d.ndim != 2 or d.shape[0] < 2 or d.shape[1] < 1:
        raise ValueError("loss_differentials must be (n_obs >= 2) x (n_models >= 1)")
    n, k = d.shape
    rng = np.random.default_rng(seed)

    dbar = d.mean(axis=0)
    raw_omega = d.std(axis=0, ddof=1)
    # A zero-variance column cannot be bootstrapped: every resample reproduces
    # its mean, so its studentized statistic is undefined. Setting omega to inf
    # makes it unwinnable, which is the safe direction — but a zero-variance
    # POSITIVE mean is a riskless edge, and silently reporting p=1.0 ("dead")
    # for it would hide a modelling error rather than surface one. Flag it.
    degenerate = raw_omega < _VOL_EPS
    omega = np.where(degenerate, np.inf, raw_omega)
    degenerate_positive = [int(i) for i in np.flatnonzero(degenerate & (dbar > 0))]

    t_stat = np.sqrt(n) * dbar / omega
    observed = max(0.0, float(t_stat.max()))

    # Hansen's consistent recentering threshold.
    threshold = -omega * math.sqrt(2.0 * math.log(math.log(n)) / n)
    keep = dbar >= threshold
    centered = d - np.where(keep, dbar, 0.0)

    boot = np.empty(n_boot)
    for b in range(n_boot):
        idx = stationary_bootstrap_indices(n, block_mean, rng)
        zbar = centered[idx].mean(axis=0)
        boot[b] = max(0.0, float((np.sqrt(n) * zbar / omega).max()))

    return {
        "p_value": float((boot >= observed).mean()),
        "statistic": observed,
        "n_obs": n,
        "n_models": k,
        "n_boot": n_boot,
        "block_mean": block_mean,
        "best_model": int(np.argmax(t_stat)),
        "degenerate_models": degenerate_positive,
        "note": (
            f"columns {degenerate_positive} have zero variance with a positive "
            "mean — a riskless edge SPA cannot studentize. The p-value below is "
            "NOT evidence against them; check the return construction."
            if degenerate_positive else ""
        ),
    }


def summary(returns, benchmark=None, periods: int = TRADING_DAYS) -> dict:
    """Descriptive block for a return series; IR/active only when a benchmark
    is supplied. No inference here — that is a deliberate call the caller makes."""
    out = {
        "ann_return": annualized_return(returns, periods),
        "ann_vol": annualized_vol(returns, periods),
        "sharpe": sharpe(returns, periods=periods),
        "max_drawdown": max_drawdown(returns),
        "skew": skew(returns),
        "kurtosis": kurtosis(returns),
        "n_obs": int(pd.Series(returns, dtype=float).dropna().size),
    }
    if benchmark is not None:
        aligned = pd.concat(
            [pd.Series(returns, dtype=float), pd.Series(benchmark, dtype=float)],
            axis=1, join="inner",
        ).dropna()
        out["information_ratio"] = information_ratio(aligned.iloc[:, 0], aligned.iloc[:, 1], periods)
        out["ann_active_return"] = (
            annualized_return(aligned.iloc[:, 0], periods)
            - annualized_return(aligned.iloc[:, 1], periods)
        )
        out["tracking_error"] = float(
            (aligned.iloc[:, 0] - aligned.iloc[:, 1]).std(ddof=1) * math.sqrt(periods)
        )
    return out

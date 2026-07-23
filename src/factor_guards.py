"""Data-quality guards for co-moving factor series (TRAP 6 / TRAP 8 family).

Origin: 2026-07-23. A monitoring look pulled Brent (BZ=F) and WTI (CL=F) and
the unsettled same-day bars printed Brent -7.4% against WTI +6.4% — a ~14%
same-day decoupling of two near-perfectly co-moving grades, physically
implausible and caught only by eyeball. Registered in
DIAG-MACROBETA-0001-FWDLOOK. These guards make that catch structural: a
pipeline that ingests near-cointegrated series must FAIL LOUDLY on a
divergence like that, never average over it or pass it downstream.

Guards, both raising FactorGuardError (never warn-and-continue):

- ``assert_return_agreement`` — two series that are the SAME quantity from
  two sources (INR=X vs USDINR=X) must agree to a correlation floor.
  Generalises the inline check in scripts/diag_macro_beta.py.
- ``assert_comoving_divergence`` — two series that are DISTINCT but
  near-cointegrated (Brent vs WTI) must not diverge beyond a per-day cap.

Alignment is by exact index intersection only — no forward fill; a date
missing either leg is simply not tested (the overlap floor catches a hollow
intersection).
"""

from __future__ import annotations

import numpy as np
import pandas as pd


class FactorGuardError(RuntimeError):
    """A co-moving-series guard failed. Do not catch and continue."""


def _log_returns_aligned(
    a: pd.Series, b: pd.Series, min_overlap: int
) -> pd.DataFrame:
    both = pd.concat(
        [np.log(a.astype(float)).diff(), np.log(b.astype(float)).diff()],
        axis=1,
        join="inner",
        keys=["a", "b"],
    ).dropna()
    if len(both) < min_overlap:
        raise FactorGuardError(
            f"co-moving guard: only {len(both)} overlapping return "
            f"observations (< {min_overlap}) — refusing to certify agreement "
            f"on a hollow intersection"
        )
    return both


def assert_return_agreement(
    a: pd.Series,
    b: pd.Series,
    name_a: str,
    name_b: str,
    *,
    min_corr: float = 0.99,
    min_overlap: int = 20,
) -> float:
    """Two sources of the SAME series must agree; returns the correlation.

    Raises FactorGuardError if log-return correlation <= min_corr or the
    overlap is below min_overlap rows.
    """
    both = _log_returns_aligned(a, b, min_overlap)
    corr = float(both["a"].corr(both["b"]))
    if not corr > min_corr:
        raise FactorGuardError(
            f"{name_a} vs {name_b}: log-return corr {corr:.5f} <= "
            f"{min_corr} over {len(both)} obs — same-quantity sources "
            f"disagree; do not proceed on either"
        )
    return corr


def assert_comoving_divergence(
    a: pd.Series,
    b: pd.Series,
    name_a: str,
    name_b: str,
    *,
    max_abs_divergence: float = 0.05,
    min_overlap: int = 20,
    tail_bars: int | None = None,
) -> pd.Series:
    """Near-cointegrated pair (e.g. Brent/WTI) same-day divergence cap.

    Checks |r_a - r_b| per overlapping day; raises FactorGuardError listing
    every offending date if any exceeds max_abs_divergence (default 5%,
    log-return points — the 2026-07-23 corrupted bars measured ~0.14).
    Returns the FULL per-day divergence series for inspection/reporting.

    ``tail_bars``: if set, the hard cap applies only to the LAST N return
    observations — the unsettled-bar zone of a fresh pull, where corruption
    actually occurs. This scoping was forced by the guard's own base-rate
    check before adoption (TRAP 8/10): over the 2015–2024 dev window the
    REAL Brent/WTI divergence exceeds 5% on 30 days, peaking at 0.2672 on
    2020-04-22 (the WTI negative-price / super-contango episode) — genuine
    decoupling, not corruption. A full-history hard cap therefore rejects
    valid data; callers scanning settled history should pass ``tail_bars``
    (or treat the returned series as a report, not a gate).
    """
    both = _log_returns_aligned(a, b, min_overlap)
    div = (both["a"] - both["b"]).abs()
    checked = div.iloc[-tail_bars:] if tail_bars is not None else div
    bad = checked[checked > max_abs_divergence]
    if len(bad):
        detail = ", ".join(
            f"{idx.date() if hasattr(idx, 'date') else idx}={v:.4f}"
            for idx, v in bad.items()
        )
        scope = (
            f"in the last {tail_bars} bars" if tail_bars is not None else "in the series"
        )
        raise FactorGuardError(
            f"{name_a} vs {name_b}: same-day divergence exceeds "
            f"{max_abs_divergence:.2%} on {len(bad)} day(s) {scope} "
            f"[{detail}] — probable corrupted/unsettled bar(s); drop or "
            f"re-fetch before any downstream use"
        )
    return div

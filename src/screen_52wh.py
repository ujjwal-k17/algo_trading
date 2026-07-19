"""52-week-high negative screen (SPEC-52WH-01 Stage 3, plan_52wh.md).

The implementable edge (research.md Part 4, Raju 2023) is NOT holding the
near-high bucket — it is NEVER holding the far-from-high bucket (Q1 CAPM
alpha ~ -2.4%/mo). This module applies that screen to any candidate book:
a set difference plus renormalized weights, nothing more. The optional
tilt weighting is a diagnostic, explicitly not the hypothesis.

Outcome-blind by construction: the only admissible signal input is the
feature frame emitted by ``signal_52wh.signal_at`` — any unexpected column
in it is a hard error, so an outcome column cannot even ride through this
module by accident. No return data is computed, joined, or accepted.
"""

from __future__ import annotations

from collections.abc import Mapping

import pandas as pd

# The full schema of signal_52wh.signal_at output. A stricter-than-needed
# whitelist is the structural contamination wall: a frame carrying any other
# column (e.g. a return joined upstream) is rejected, not silently passed.
_SIGNAL_COLS = {"nearness", "cs_rank", "bucket"}

EXCLUDE_BUCKETS_DEFAULT = ("Q1",)

_STATUSES = ("kept", "excluded", "unranked")


def _validate_signal(signal: pd.DataFrame) -> pd.DataFrame:
    if "bucket" not in signal.columns:
        raise ValueError("signal frame is missing 'bucket' — not signal_52wh output?")
    extra = set(signal.columns) - _SIGNAL_COLS
    if extra:
        raise ValueError(
            f"signal frame has unexpected columns {sorted(extra)} — "
            "only signal_52wh feature columns are admissible (outcome-blind wall)"
        )
    if signal.index.has_duplicates:
        raise ValueError("signal frame has duplicate symbols")
    return signal


def _book_weights(book) -> pd.Series:
    """Book as weights: a mapping/Series is taken verbatim; a plain list of
    symbols becomes an equal-weight book."""
    if isinstance(book, pd.Series):
        w = book.astype(float)
    elif isinstance(book, Mapping):
        w = pd.Series(book, dtype=float)
    else:
        symbols = list(book)
        if len(symbols) != len(set(symbols)):
            raise ValueError("book has duplicate symbols")
        w = pd.Series(1.0 / len(symbols) if symbols else 0.0, index=symbols)
    if w.index.has_duplicates:
        raise ValueError("book has duplicate symbols")
    if w.empty:
        raise ValueError("book is empty")
    if w.isna().any() or (w < 0).any():
        raise ValueError("book weights must be non-negative and defined (long-only)")
    return w


def screen_book(
    signal: pd.DataFrame,
    book,
    *,
    exclude_buckets: tuple[str, ...] = EXCLUDE_BUCKETS_DEFAULT,
    unranked_policy: str = "keep",
) -> pd.DataFrame:
    """Apply the negative screen to a candidate ``book``.

    ``signal`` is the frame from ``signal_52wh.signal_at`` (index = symbol,
    columns nearness / cs_rank / bucket). ``book`` is a list of symbols
    (equal-weighted) or a symbol -> weight mapping/Series.

    ``unranked_policy`` decides names with no defined nearness (< 252
    observed highs, or outside the ranked universe): ``"keep"`` (default —
    the screen only asserts far-from-high names underperform; unknown is
    not far-from-high) or ``"drop"`` (conservative variant).

    Returns a frame indexed by book symbol: ``bucket`` (NA when unranked),
    ``status`` (kept / excluded / unranked), ``weight_in`` (input weight),
    ``weight_out`` (renormalized over surviving names; 0 when screened out).
    Feature columns only — no return data exists in this schema.
    """
    if unranked_policy not in ("keep", "drop"):
        raise ValueError(f"unranked_policy must be 'keep' or 'drop', got {unranked_policy!r}")
    signal = _validate_signal(signal)
    weights = _book_weights(book)

    bucket = signal["bucket"].reindex(weights.index)
    status = pd.Series("kept", index=weights.index)
    status[bucket.isna()] = "unranked"
    status[bucket.isin(exclude_buckets)] = "excluded"

    survives = (status == "kept") | (
        (status == "unranked") & (unranked_policy == "keep")
    )
    surviving_total = weights[survives].sum()
    weight_out = pd.Series(0.0, index=weights.index)
    if surviving_total > 0:
        weight_out[survives] = weights[survives] / surviving_total

    out = pd.DataFrame(
        {
            "bucket": bucket,
            "status": status,
            "weight_in": weights,
            "weight_out": weight_out,
        }
    )
    out.index.name = "symbol"
    return out


def screened_symbols(
    signal: pd.DataFrame,
    universe,
    *,
    exclude_buckets: tuple[str, ...] = EXCLUDE_BUCKETS_DEFAULT,
    unranked_policy: str = "keep",
) -> list[str]:
    """Set-difference form: the symbols of ``universe`` that survive the
    screen, sorted. Convenience wrapper over ``screen_book``."""
    out = screen_book(
        signal,
        list(universe),
        exclude_buckets=exclude_buckets,
        unranked_policy=unranked_policy,
    )
    return sorted(out.index[out["weight_out"] > 0])


def tilt_weights(
    signal: pd.DataFrame,
    *,
    exclude_buckets: tuple[str, ...] = EXCLUDE_BUCKETS_DEFAULT,
) -> pd.Series:
    """DIAGNOSTIC long-tilt weights: cs_rank-proportional over the surviving
    ranked names, normalized to 1. The long-only top-bucket-as-alpha claim is
    explicitly NOT the hypothesis (research.md Part 4) — this exists only to
    measure the tilt increment alongside the screen, never as the strategy.
    """
    signal = _validate_signal(signal)
    keep = signal.loc[~signal["bucket"].isin(exclude_buckets), "cs_rank"]
    if keep.empty:
        return pd.Series(dtype=float, name="tilt_weight")
    w = keep / keep.sum()
    return w.rename("tilt_weight").sort_values(ascending=False)

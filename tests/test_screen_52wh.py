"""Acceptance tests for src/screen_52wh.py (Stage 3, plan_52wh.md): screen
output is a set difference + weights; zero return columns in its schema; the
outcome-blind wall rejects frames carrying anything beyond feature columns."""

import pandas as pd
import pytest

from src import screen_52wh


def signal(buckets: dict) -> pd.DataFrame:
    """Feature frame shaped like signal_52wh.signal_at output."""
    n = len(buckets)
    out = pd.DataFrame(
        {
            "nearness": [(i + 1) / n for i in range(n)],
            "cs_rank": [(i + 1) / n for i in range(n)],
            "bucket": list(buckets.values()),
        },
        index=list(buckets.keys()),
    )
    out.index.name = "symbol"
    return out


SIG = signal({"A": "Q1", "B": "Q2", "C": "Q3", "D": "Q4", "E": "Q5"})


def test_screen_drops_far_from_high_and_renormalizes():
    out = screen_52wh.screen_book(SIG, ["A", "B", "C", "E"])
    assert out.loc["A", "status"] == "excluded"
    assert out.loc["A", "weight_out"] == 0.0
    kept = out.loc[out["status"] == "kept"]
    assert list(kept.index) == ["B", "C", "E"]
    assert kept["weight_out"].sum() == pytest.approx(1.0)
    assert kept["weight_out"].tolist() == pytest.approx([1 / 3] * 3)


def test_weighted_book_renormalizes_proportionally():
    out = screen_52wh.screen_book(SIG, {"A": 0.5, "B": 0.3, "C": 0.2})
    # A (Q1, weight 0.5) screened out; survivors keep 0.3:0.2 proportions.
    assert out.loc["B", "weight_out"] == pytest.approx(0.6)
    assert out.loc["C", "weight_out"] == pytest.approx(0.4)


def test_exclude_buckets_parameter_widens_screen():
    out = screen_52wh.screen_book(
        SIG, list(SIG.index), exclude_buckets=("Q1", "Q2")
    )
    assert set(out.index[out["status"] == "excluded"]) == {"A", "B"}


def test_unranked_keep_vs_drop():
    book = ["B", "NEW"]  # NEW has no defined nearness (absent from signal)
    kept = screen_52wh.screen_book(SIG, book)
    assert kept.loc["NEW", "status"] == "unranked"
    assert kept.loc["NEW", "weight_out"] == pytest.approx(0.5)
    dropped = screen_52wh.screen_book(SIG, book, unranked_policy="drop")
    assert dropped.loc["NEW", "weight_out"] == 0.0
    assert dropped.loc["B", "weight_out"] == pytest.approx(1.0)


def test_all_excluded_book_gets_zero_weights():
    out = screen_52wh.screen_book(SIG, ["A"], unranked_policy="drop")
    assert out["weight_out"].tolist() == [0.0]


def test_screened_symbols_is_a_set_difference():
    assert screen_52wh.screened_symbols(SIG, ["E", "A", "C"]) == ["C", "E"]


def test_tilt_weights_are_rank_proportional_diagnostic():
    w = screen_52wh.tilt_weights(SIG)
    assert "A" not in w.index  # Q1 excluded before tilting
    assert w.sum() == pytest.approx(1.0)
    assert w.index[0] == "E"  # nearest-to-high gets the largest weight
    assert w.loc["E"] > w.loc["B"]


def test_outcome_column_in_signal_is_a_hard_error():
    # Contamination wall: a return column cannot ride through the screen.
    contaminated = SIG.assign(fwd_return=0.1)
    with pytest.raises(ValueError, match="outcome-blind"):
        screen_52wh.screen_book(contaminated, ["B"])


def test_output_schema_has_no_return_columns():
    out = screen_52wh.screen_book(SIG, list(SIG.index))
    assert set(out.columns) == {"bucket", "status", "weight_in", "weight_out"}


def test_invalid_inputs_raise():
    with pytest.raises(ValueError, match="empty"):
        screen_52wh.screen_book(SIG, [])
    with pytest.raises(ValueError, match="duplicate"):
        screen_52wh.screen_book(SIG, ["B", "B"])
    with pytest.raises(ValueError, match="non-negative"):
        screen_52wh.screen_book(SIG, {"B": -0.5, "C": 1.5})
    with pytest.raises(ValueError, match="unranked_policy"):
        screen_52wh.screen_book(SIG, ["B"], unranked_policy="maybe")
    with pytest.raises(ValueError, match="bucket"):
        screen_52wh.screen_book(SIG.drop(columns=["bucket"]), ["B"])

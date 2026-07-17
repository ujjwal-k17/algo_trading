"""Tests for the overlay-alpha join: veto, reduce, correction (last-per-key)."""

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import overlay_alpha

PAPER = pd.DataFrame(
    {
        "rec_key": ["2026-07-01|AAA|1", "2026-07-01|BBB|1", "2026-07-02|CCC|1"],
        "exit_date": pd.to_datetime(["2026-07-03", "2026-07-06", "2026-07-08"]),
        "r_multiple": [2.0, -1.0, 1.5],
        "flag_ambiguous_same_bar": [False, False, True],
    }
)


def _overlay(rows):
    return pd.DataFrame(rows, columns=["ts_local", "rec_key", "decision", "executed_size", "reason"])


def test_veto_join_contributes_zero_executed_r():
    ov = _overlay([("2026-07-01 09:30:00", "2026-07-01|AAA|1", "VETO", 0, "skip")])
    j = overlay_alpha.join_overlay(PAPER, ov)
    row = j.iloc[0]
    assert row["recommended_r"] == 2.0 and row["executed_r"] == 0.0
    assert row["delta_r"] == -2.0  # veto of a winner costs the overlay


def test_reduce_join_scales_by_size():
    ov = _overlay([("2026-07-01 09:30:00", "2026-07-01|BBB|1", "REDUCE", 0.5, "half size")])
    row = overlay_alpha.join_overlay(PAPER, ov).iloc[0]
    assert row["executed_r"] == -0.5 and row["delta_r"] == 0.5  # reducing a loser helps


def test_correction_row_last_per_key_wins():
    ov = _overlay(
        [
            ("2026-07-01 09:30:00", "2026-07-01|AAA|1", "VETO", 0, "fat finger"),
            ("2026-07-01 09:31:00", "2026-07-01|AAA|1", "EXECUTE", 1, "correction: meant execute"),
        ]
    )
    j = overlay_alpha.join_overlay(PAPER, ov)
    assert len(j) == 1
    assert j.iloc[0]["decision"] == "EXECUTE" and j.iloc[0]["executed_r"] == 2.0


def test_weekly_summary_reports_all_and_ex_ambiguous():
    ov = _overlay(
        [
            ("2026-07-01 09:30:00", "2026-07-01|AAA|1", "EXECUTE", 1, "take"),
            ("2026-07-02 09:30:00", "2026-07-02|CCC|1", "EXECUTE", 1, "take"),
        ]
    )
    summary = overlay_alpha.weekly_summary(overlay_alpha.join_overlay(PAPER, ov))
    scopes = set(summary["scope"])
    assert scopes == {"all", "ex_ambiguous"}
    wk = summary[summary["week"] == "2026-W28"]  # CCC exits 2026-07-08, flagged ambiguous
    assert wk[wk.scope == "all"].n_trades.iloc[0] == 1
    # no significance columns by design
    assert not any("p_value" in c or "t_stat" in c for c in summary.columns)

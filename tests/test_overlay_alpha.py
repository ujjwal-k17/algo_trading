"""Tests for the overlay-alpha join: veto, reduce, correction (last-per-key)."""

import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import overlay_alpha

PAPER = pd.DataFrame(
    {
        "rec_key": ["2026-07-01|AAA|1", "2026-07-01|BBB|1", "2026-07-02|CCC|1"],
        "pick_date": pd.to_datetime(["2026-07-01", "2026-07-01", "2026-07-02"]),
        "symbol": ["AAA", "BBB", "CCC"],
        "entry_price": [100.0, 100.0, 100.0],
        "stop_loss": [95.0, 95.0, 95.0],
        "exit_date": pd.to_datetime(["2026-07-03", "2026-07-06", "2026-07-08"]),
        "exit_price": [110.0, 95.0, 107.5],
        "r_multiple": [2.0, -1.0, 1.5],
        "dividend_credit": [0.0, 0.0, 0.0],
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


def test_reconcile_fills_executed_only_with_divergence():
    ov = _overlay([
        ("2026-07-01 09:30:00", "2026-07-01|AAA|1", "EXECUTE", 1, "take"),
        ("2026-07-01 09:31:00", "2026-07-01|BBB|1", "VETO", 0, "skip"),
    ])
    ledger = pd.DataFrame({"pick_date": ["2026-07-01", "2026-07-01"],
                           "symbol": ["AAA", "BBB"], "exit_price": [109.45, 95.0]})
    rec = overlay_alpha.reconcile_fills(overlay_alpha.join_overlay(PAPER, ov), ledger)
    assert len(rec) == 1  # veto excluded
    assert rec.iloc[0]["pct_divergence"] == pytest.approx(0.5025, abs=1e-3)


def test_fill_based_executed_r_prefers_actual_exit():
    # fills basis (pre-log ruling): executed R from the recorded fill, not paper exit
    ov = _overlay([("2026-07-01 09:30:00", "2026-07-01|AAA|1", "EXECUTE", 1, "take")])
    ledger = pd.DataFrame({"pick_date": ["2026-07-01"], "symbol": ["AAA"],
                           "exit_price": [108.0]})
    j = overlay_alpha.join_overlay(PAPER, ov, ledger=ledger)
    row = j.iloc[0]
    assert bool(row["fill_based"])
    assert row["executed_r"] == pytest.approx((108.0 - 100.0) / 5.0)  # 1.6, not 2.0
    assert row["recommended_r"] == 2.0  # paper leg unchanged


def test_reconstruct_overlay_infers_execute_veto_and_excludes_system():
    universe = pd.DataFrame({
        "rec_key": ["2026-07-01|AAA|1", "2026-07-01|BBB|1", "2026-07-01|CCC|1"],
        "pick_date": pd.to_datetime(["2026-07-01"] * 3),
        "symbol": ["AAA", "BBB", "CCC"],
    })
    ledger = pd.DataFrame({
        "pick_date": ["2026-07-01", "2026-07-01"], "symbol": ["AAA", "BBB"],
        "exit_reason": [None, "AUTO_EXPIRED_5_SESSIONS"],
    })
    recon, n_sys = overlay_alpha.reconstruct_overlay(universe, ledger)
    by_key = dict(zip(recon.rec_key, recon.decision))
    assert by_key == {"2026-07-01|AAA|1": "EXECUTE", "2026-07-01|CCC|1": "VETO"}
    assert n_sys == 1  # BBB: system entry-gate expiry, not user discretion


def test_weekly_summary_rejects_mixed_provenance():
    ov = _overlay([("2026-07-01 09:30:00", "2026-07-01|AAA|1", "EXECUTE", 1, "take")])
    a = overlay_alpha.join_overlay(PAPER, ov, provenance="DECISION_TIME")
    b = overlay_alpha.join_overlay(PAPER, ov, provenance="RECONSTRUCTED")
    with pytest.raises(ValueError, match="never be merged"):
        overlay_alpha.weekly_summary(pd.concat([a, b]))


def test_assumed_entry_scope_separated_headline_is_entered():
    # 2026-07-18 ruling: gate-respecting figure is the headline; assumed-entry
    # (AUTO_EXPIRED settled via assumed entry) reports separately.
    ov = _overlay([
        ("2026-07-01 09:30:00", "2026-07-01|AAA|1", "EXECUTE", 1, "take"),
        ("2026-07-01 09:31:00", "2026-07-01|BBB|1", "EXECUTE", 1, "take"),
    ])
    paper = PAPER.assign(system_entered=[True, False, True])
    s = overlay_alpha.weekly_summary(overlay_alpha.join_overlay(paper, ov))
    scopes = set(s["scope"])
    assert "entered" in scopes and "assumed_entry" in scopes and "all" not in scopes
    wk27 = s[s.week == "2026-W27"]
    assert wk27[wk27.scope == "entered"].recommended_r_sum.iloc[0] == 2.0   # AAA (exit 07-03)
    wk28 = s[s.week == "2026-W28"]
    assert wk28[wk28.scope == "assumed_entry"].recommended_r_sum.iloc[0] == -1.0  # BBB (exit 07-06)

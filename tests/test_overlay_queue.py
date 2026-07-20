"""Tests for src/overlay_queue.py and scripts/overlay_today.py.

Every test runs against fixtures in tmp_path. The real
governance/overlay_log.csv is never written by these tests, and one test
asserts it still holds zero data rows.
"""

import subprocess
import sys
from pathlib import Path

import pandas as pd
import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))
sys.path.insert(0, str(REPO / "scripts"))
import overlay_queue as oq  # noqa: E402

HEADER = "ts_local,rec_key,decision,executed_size,reason\n"

REC_COLS = (
    "rank,symbol,company_name,sector,close,stop_loss,stop_method,stop_pct,"
    "target_1,target_1_pct,target_2,target_2_pct,rr_t1,rr_t2,conviction\n"
)


def _rec_file(d: Path, data_date: str, gen_date: str, symbols: list[str]) -> Path:
    f = d / f"top5_report_data{data_date}_generated{gen_date}.csv"
    body = "".join(
        f"{i + 1},{s},{s} Ltd,Sector,100.0,95.0,ATR,5.0,110.0,10.0,120.0,20.0,2.0,4.0,60\n"
        for i, s in enumerate(symbols)
    )
    f.write_text(f"# Data as of: {data_date} | Generated: {gen_date}\n" + REC_COLS + body)
    return f


# ---------------------------------------------------------------- rec_key


def test_rec_key_uses_data_date_symbol_seq(tmp_path):
    _rec_file(tmp_path, "2026-06-29", "2026-06-29", ["AAA"])
    _rec_file(tmp_path, "2026-06-29", "2026-06-30", ["AAA"])
    recs = oq.load_rec_corpus(sorted(tmp_path.glob("top5_*.csv")))
    assert set(recs["rec_key"]) == {"2026-06-29|AAA|1", "2026-06-29|AAA|2"}


def test_rec_key_matches_build_workspace_seq_logic(tmp_path):
    """The queue must key recs identically to the settlement path, or the
    A/B join on rec_key silently misses rows."""
    from build_workspace import load_rec_files

    for gen in ("2026-06-29", "2026-06-30", "2026-07-01"):
        _rec_file(tmp_path, "2026-06-29", gen, ["AAA", "BBB"])
    ours = oq.load_rec_corpus(sorted(tmp_path.glob("top5_*.csv")))
    theirs = load_rec_files(tmp_path)
    assert sorted(ours["rec_key"]) == sorted(theirs["rec_key"])


def test_empty_rec_file_skipped(tmp_path):
    f = tmp_path / "top5_report_data2026-06-29_generated2026-06-29.csv"
    f.write_text("# Data as of: 2026-06-29 | Generated: 2026-06-29\n")
    assert oq.load_rec_corpus([f]).empty


# ------------------------------------------------------- outcome blindness


@pytest.mark.parametrize(
    "col", ["r_multiple", "exit_price", "pnl", "realized_r", "outcome", "nav", "fill_price"]
)
def test_outcome_columns_are_a_hard_error(col):
    df = pd.DataFrame({"rec_key": ["2026-06-29|A|1"], col: [1.0]})
    with pytest.raises(oq.OutcomeContactError):
        oq.assert_outcome_blind(df)


def test_stop_loss_is_not_treated_as_an_outcome():
    """stop_loss is a decision-time LEVEL, not a realised loss."""
    oq.assert_outcome_blind(
        pd.DataFrame({"rec_key": ["2026-06-29|A|1"], "stop_loss": [95.0], "stop_pct": [5.0]})
    )


def test_live_window_recs_exposes_only_decision_time_fields(tmp_path, monkeypatch):
    _rec_file(tmp_path, "2026-06-29", "2026-06-29", ["AAA", "BBB"])
    monkeypatch.setattr(oq, "RECS_DIR", tmp_path)
    monkeypatch.setattr(oq, "RAW_ROOT", tmp_path / "nonexistent")
    out = oq.live_window_recs()
    assert set(out.columns) <= set(oq.DECISION_TIME_FIELDS)
    oq.assert_outcome_blind(out)


def test_command_lines_refuse_outcome_bearing_frame():
    df = pd.DataFrame({"rec_key": ["2026-06-29|A|1"], "r_multiple": [2.0]})
    with pytest.raises(oq.OutcomeContactError):
        oq.command_lines(df)


# ------------------------------------------------------------- the gate


def test_pre_live_window_recs_are_filtered_out(tmp_path, monkeypatch):
    """A rec generated before the live-window start would be rejected by the
    Tier 1 door; the queue must drop it, not raise."""
    _rec_file(tmp_path, "2026-06-18", "2026-06-19", ["OLD"])
    _rec_file(tmp_path, "2026-06-29", "2026-06-29", ["NEW"])
    monkeypatch.setattr(oq, "RECS_DIR", tmp_path)
    monkeypatch.setattr(oq, "RAW_ROOT", tmp_path / "nonexistent")
    out = oq.live_window_recs()
    assert list(out["symbol"]) == ["NEW"]


def test_last_generation_per_pick_date_symbol_wins(tmp_path, monkeypatch):
    _rec_file(tmp_path, "2026-06-29", "2026-06-30", ["AAA"])
    _rec_file(tmp_path, "2026-06-30", "2026-06-30", ["AAA"])
    monkeypatch.setattr(oq, "RECS_DIR", tmp_path)
    monkeypatch.setattr(oq, "RAW_ROOT", tmp_path / "nonexistent")
    out = oq.live_window_recs()
    assert len(out) == 1 and out.iloc[0]["data_date"] == "2026-06-30"


# ----------------------------------------------------------- logged keys


def test_logged_keys_empty_for_header_only_log(tmp_path):
    log = tmp_path / "log.csv"
    log.write_text(HEADER)
    assert oq.logged_keys(log) == {}


def test_logged_keys_takes_last_row_per_key(tmp_path):
    log = tmp_path / "log.csv"
    log.write_text(
        HEADER
        + '2026-06-29 10:00:00,2026-06-29|AAA|1,VETO,0,"nope"\n'
        + '2026-06-29 10:05:00,2026-06-29|AAA|1,REDUCE,0.5,"correction: meant reduce"\n'
        + '2026-06-29 10:06:00,2026-06-29|BBB|1,EXECUTE,1,"clean"\n'
    )
    assert oq.logged_keys(log) == {
        "2026-06-29|AAA|1": "REDUCE",
        "2026-06-29|BBB|1": "EXECUTE",
    }


def test_logged_keys_missing_file_is_empty(tmp_path):
    assert oq.logged_keys(tmp_path / "absent.csv") == {}


# --------------------------------------------------------------- backlog


def test_backlog_counts_and_is_idempotent(tmp_path, monkeypatch):
    _rec_file(tmp_path, "2026-06-29", "2026-06-29", ["AAA", "BBB"])
    _rec_file(tmp_path, "2026-06-30", "2026-06-30", ["CCC"])
    monkeypatch.setattr(oq, "RECS_DIR", tmp_path)
    monkeypatch.setattr(oq, "RAW_ROOT", tmp_path / "nonexistent")
    log = tmp_path / "log.csv"
    log.write_text(HEADER + '2026-06-29 10:00:00,2026-06-29|AAA|1,VETO,0,"nope"\n')

    recs = oq.live_window_recs()
    first = oq.backlog(recs, log)
    second = oq.backlog(recs, log)
    assert first["n_total"] == 3 and first["n_logged"] == 1 and first["n_unlogged"] == 2
    assert first["oldest_unlogged"] == "2026-06-29"
    assert second["n_unlogged"] == first["n_unlogged"]  # idempotent: pure read
    assert log.read_text().count("\n") == 2  # backlog wrote nothing


def test_command_lines_cover_every_unlogged_rec(tmp_path, monkeypatch):
    _rec_file(tmp_path, "2026-06-29", "2026-06-29", ["AAA", "BBB"])
    monkeypatch.setattr(oq, "RECS_DIR", tmp_path)
    monkeypatch.setattr(oq, "RAW_ROOT", tmp_path / "nonexistent")
    log = tmp_path / "log.csv"
    log.write_text(HEADER)
    lines = oq.command_lines(oq.backlog(oq.live_window_recs(), log)["unlogged"])
    assert len(lines) == 2
    assert all(ln.startswith("overlay '2026-06-29|") for ln in lines)
    assert all(oq.REC_KEY_RE.match(ln.split("'")[1]) for ln in lines)


# ------------------------------------------------------------ the CLI


def test_cli_runs_and_never_writes_the_real_log(tmp_path):
    real = REPO / "governance" / "overlay_log.csv"
    before = real.read_text()
    r = subprocess.run(
        [str(REPO / ".venv" / "bin" / "python"), str(REPO / "scripts" / "overlay_today.py"),
         "--all", "--commands"],
        capture_output=True, text=True,
    )
    assert r.returncode == 0
    assert real.read_text() == before  # byte-identical


def test_real_overlay_log_has_zero_data_rows():
    """Guard rail. If tooling ever seeds this file, this test fails loudly.

    The log records the operator's OWN decisions and is the object of
    AB_PREREG analyses 2-4; a generated row would be indistinguishable from a
    genuine one and would silently corrupt the study.
    """
    lines = (REPO / "governance" / "overlay_log.csv").read_text().splitlines()
    assert lines[0] == "ts_local,rec_key,decision,executed_size,reason"
    assert [ln for ln in lines[1:] if ln.strip()] == []


# --- ingest health -----------------------------------------------------------

class TestLastExpectedSnapshotDay:
    """Weekend-aware: a Monday must not demand a Sunday snapshot."""

    def test_weekday_is_itself(self):
        # 2026-07-20 is a Monday
        d = pd.Timestamp("2026-07-20")
        assert oq.last_expected_snapshot_day(d) == d

    def test_saturday_rolls_back_to_friday(self):
        assert oq.last_expected_snapshot_day(
            pd.Timestamp("2026-07-18")
        ) == pd.Timestamp("2026-07-17")

    def test_sunday_rolls_back_to_friday(self):
        assert oq.last_expected_snapshot_day(
            pd.Timestamp("2026-07-19")
        ) == pd.Timestamp("2026-07-17")

    def test_monday_does_not_demand_a_weekend_snapshot(self):
        """The regression that would make this warn every Monday."""
        monday = pd.Timestamp("2026-07-20")
        assert oq.last_expected_snapshot_day(monday).weekday() < 5


class TestNewestPopulatedSnapshot:
    """Empty dated dirs were the actual TCC symptom — they must not count."""

    def test_empty_directories_are_not_populated(self, tmp_path, monkeypatch):
        root = tmp_path / "raw"
        (root / "2026-07-17").mkdir(parents=True)
        (root / "2026-07-17" / "rec.csv").write_text("x")
        for empty in ("2026-07-18", "2026-07-19", "2026-07-20"):
            (root / empty).mkdir()
        monkeypatch.setattr(oq, "RAW_ROOT", root)
        assert oq.newest_populated_snapshot() == pd.Timestamp("2026-07-17")

    def test_no_directories_returns_nat(self, tmp_path, monkeypatch):
        monkeypatch.setattr(oq, "RAW_ROOT", tmp_path / "missing")
        assert oq.newest_populated_snapshot() is pd.NaT

    def test_non_date_directory_names_are_ignored(self, tmp_path, monkeypatch):
        root = tmp_path / "raw"
        (root / "scratch").mkdir(parents=True)
        (root / "scratch" / "f").write_text("x")
        (root / "2026-07-17").mkdir()
        (root / "2026-07-17" / "rec.csv").write_text("x")
        monkeypatch.setattr(oq, "RAW_ROOT", root)
        assert oq.newest_populated_snapshot() == pd.Timestamp("2026-07-17")


class TestIngestHealth:
    def test_nonzero_exit_is_reported(self, tmp_path, monkeypatch):
        """Exit 23 is the real failure this was written for."""
        root = tmp_path / "raw"
        (root / "2026-07-20").mkdir(parents=True)
        (root / "2026-07-20" / "rec.csv").write_text("x")
        monkeypatch.setattr(oq, "RAW_ROOT", root)
        monkeypatch.setattr(oq, "_launchd_exit_status", lambda *a, **k: 23)
        warnings = oq.ingest_health(pd.Timestamp("2026-07-20"))
        assert any("23" in w for w in warnings)
        assert any("Full Disk Access" in w for w in warnings)

    def test_healthy_state_is_silent(self, tmp_path, monkeypatch):
        root = tmp_path / "raw"
        (root / "2026-07-20").mkdir(parents=True)
        (root / "2026-07-20" / "rec.csv").write_text("x")
        monkeypatch.setattr(oq, "RAW_ROOT", root)
        monkeypatch.setattr(oq, "_launchd_exit_status", lambda *a, **k: 0)
        assert oq.ingest_health(pd.Timestamp("2026-07-20")) == []

    def test_stale_populated_snapshot_warns_even_when_exit_is_zero(
        self, tmp_path, monkeypatch
    ):
        """The exact shape of the outage: dirs exist, exit looks fine, no data."""
        root = tmp_path / "raw"
        (root / "2026-07-15").mkdir(parents=True)
        (root / "2026-07-15" / "rec.csv").write_text("x")
        (root / "2026-07-20").mkdir()  # created but empty
        monkeypatch.setattr(oq, "RAW_ROOT", root)
        monkeypatch.setattr(oq, "_launchd_exit_status", lambda *a, **k: 0)
        warnings = oq.ingest_health(pd.Timestamp("2026-07-20"))
        assert any("2026-07-15" in w for w in warnings)

    def test_weekend_run_does_not_warn(self, tmp_path, monkeypatch):
        """Friday data, checked on Sunday, is healthy — not 2 days stale."""
        root = tmp_path / "raw"
        (root / "2026-07-17").mkdir(parents=True)
        (root / "2026-07-17" / "rec.csv").write_text("x")
        monkeypatch.setattr(oq, "RAW_ROOT", root)
        monkeypatch.setattr(oq, "_launchd_exit_status", lambda *a, **k: 0)
        assert oq.ingest_health(pd.Timestamp("2026-07-19")) == []

    def test_unloaded_job_is_reported(self, tmp_path, monkeypatch):
        root = tmp_path / "raw"
        (root / "2026-07-20").mkdir(parents=True)
        (root / "2026-07-20" / "rec.csv").write_text("x")
        monkeypatch.setattr(oq, "RAW_ROOT", root)
        monkeypatch.setattr(oq, "_launchd_exit_status", lambda *a, **k: None)
        assert any("not loaded" in w for w in oq.ingest_health(pd.Timestamp("2026-07-20")))

    def test_launchctl_failure_never_raises(self, monkeypatch):
        """A broken diagnostic must not break the tool it reports on."""
        def boom(*a, **k):
            raise OSError("launchctl missing")
        monkeypatch.setattr("subprocess.run", boom)
        assert oq._launchd_exit_status() is None

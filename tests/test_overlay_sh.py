"""Tests for scripts/overlay.sh: valid append, invalid decision, 5-column schema,
and ingest idempotency per day."""

import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
HEADER = "ts_local,rec_key,decision,executed_size,reason\n"


def _overlay(tmp_log: Path, *args: str) -> subprocess.CompletedProcess:
    cmd = f'source "{REPO}/scripts/overlay.sh"; overlay ' + " ".join(f"'{a}'" for a in args)
    return subprocess.run(
        ["zsh", "-c", cmd], env={"OVERLAY_LOG": str(tmp_log), "PATH": "/usr/bin:/bin"},
        capture_output=True, text=True,
    )


def test_appends_valid_row_and_echoes_it(tmp_path):
    log = tmp_path / "log.csv"
    log.write_text(HEADER)
    r = _overlay(log, "2026-07-17|AJANTPHARM|1", "EXECUTE", "1", "clean setup")
    assert r.returncode == 0
    lines = log.read_text().splitlines()
    assert len(lines) == 2 and lines[1].endswith('|AJANTPHARM|1,EXECUTE,1,"clean setup"')
    assert r.stdout.strip() == lines[1]  # echoes the appended line
    assert len(lines[1].split(",", 4)) == 5  # exactly 5 columns


def test_rejects_invalid_decision(tmp_path):
    log = tmp_path / "log.csv"
    log.write_text(HEADER)
    r = _overlay(log, "2026-07-17|X|1", "HOLD", "1", "nope")
    assert r.returncode != 0 and "invalid decision" in r.stderr
    assert log.read_text() == HEADER  # nothing appended


def test_rejects_malformed_rec_key(tmp_path):
    log = tmp_path / "log.csv"
    log.write_text(HEADER)
    for bad in ("AJANTPHARM", "2026-07-17|AJANTPHARM", "17-07-2026|X|1", "2026-07-17||1"):
        r = _overlay(log, bad, "EXECUTE", "1", "reason")
        assert r.returncode != 0, bad
        assert "rec_key" in r.stderr, bad
    assert log.read_text() == HEADER


def test_rejects_non_integer_seq(tmp_path):
    log = tmp_path / "log.csv"
    log.write_text(HEADER)
    r = _overlay(log, "2026-07-17|X|first", "EXECUTE", "1", "reason")
    assert r.returncode != 0 and "seq" in r.stderr
    assert log.read_text() == HEADER


def test_rejects_size_out_of_range_and_non_numeric(tmp_path):
    log = tmp_path / "log.csv"
    log.write_text(HEADER)
    for bad in ("1.5", "2", "-1", "abc", "0.1.2"):
        r = _overlay(log, "2026-07-17|X|1", "REDUCE", bad, "reason")
        assert r.returncode != 0, bad
    assert log.read_text() == HEADER


def test_size_above_one_is_rejected_as_sizing_up(tmp_path):
    """The overlay is execute/veto/reduce only — never add, never size up."""
    log = tmp_path / "log.csv"
    log.write_text(HEADER)
    r = _overlay(log, "2026-07-17|X|1", "EXECUTE", "1.25", "bigger")
    assert r.returncode != 0 and "never size up" in r.stderr


def test_verb_and_size_must_cohere(tmp_path):
    log = tmp_path / "log.csv"
    log.write_text(HEADER)
    cases = [("EXECUTE", "0.5"), ("VETO", "1"), ("VETO", "0.5"),
             ("REDUCE", "0"), ("REDUCE", "1")]
    for verb, size in cases:
        r = _overlay(log, "2026-07-17|X|1", verb, size, "reason")
        assert r.returncode != 0, (verb, size)
        assert verb in r.stderr, (verb, size)
    assert log.read_text() == HEADER


def test_accepts_valid_veto_and_reduce(tmp_path):
    log = tmp_path / "log.csv"
    log.write_text(HEADER)
    assert _overlay(log, "2026-07-17|AAA|1", "VETO", "0", "earnings tomorrow").returncode == 0
    assert _overlay(log, "2026-07-17|BBB|1", "REDUCE", "0.5", "half size").returncode == 0
    assert len(log.read_text().splitlines()) == 3


def test_rejects_empty_reason(tmp_path):
    log = tmp_path / "log.csv"
    log.write_text(HEADER)
    r = _overlay(log, "2026-07-17|X|1", "EXECUTE", "1", "   ")
    assert r.returncode != 0 and "reason" in r.stderr
    assert log.read_text() == HEADER


def test_duplicate_key_blocked_unless_marked_correction(tmp_path):
    """Analysis takes the LAST row per rec_key, so an accidental re-log would
    silently override a real decision. Corrections must be explicit."""
    log = tmp_path / "log.csv"
    log.write_text(HEADER)
    assert _overlay(log, "2026-07-17|AAA|1", "EXECUTE", "1", "taking it").returncode == 0

    dup = _overlay(log, "2026-07-17|AAA|1", "VETO", "0", "changed my mind")
    assert dup.returncode != 0 and "already has a logged decision" in dup.stderr
    assert len(log.read_text().splitlines()) == 2  # nothing appended

    fix = _overlay(log, "2026-07-17|AAA|1", "VETO", "0", "correction: meant VETO")
    assert fix.returncode == 0
    lines = log.read_text().splitlines()
    assert len(lines) == 3 and "VETO" in lines[2]


def test_reason_with_commas_and_quotes_is_csv_safe(tmp_path):
    import csv
    import io

    log = tmp_path / "log.csv"
    log.write_text(HEADER)
    reason = 'gap up, "too extended" now'
    assert _overlay(log, "2026-07-17|AAA|1", "VETO", "0", reason).returncode == 0
    rows = list(csv.reader(io.StringIO(log.read_text())))
    assert len(rows[1]) == 5 and rows[1][4] == reason


def test_missing_log_is_not_created(tmp_path):
    """The tool must never conjure a log file — the real one is governed."""
    log = tmp_path / "absent.csv"
    r = _overlay(log, "2026-07-17|AAA|1", "EXECUTE", "1", "reason")
    assert r.returncode != 0 and not log.exists()


def test_overlay_today_helper_is_defined(tmp_path):
    r = subprocess.run(
        ["zsh", "-c", f'source "{REPO}/scripts/overlay.sh"; type overlay_today'],
        env={"PATH": "/usr/bin:/bin"}, capture_output=True, text=True,
    )
    assert r.returncode == 0 and "overlay_today" in r.stdout


def test_ingest_idempotent_per_day(tmp_path):
    src = tmp_path / "src"
    src.mkdir()
    (src / "trades_log.csv").write_text("a,b\n1,2\n")
    (src / "evening.log").write_text("excluded\n")
    dest_root = tmp_path / "raw"
    env = {
        "INGEST_SRC": str(src), "INGEST_DEST_ROOT": str(dest_root),
        "INGEST_DAY": "2026-07-17", "PATH": "/usr/bin:/bin", "INGEST_SKIP_FETCH": "1",
    }
    script = str(REPO / "scripts" / "ingest_snapshot.sh")
    for _ in range(2):  # second run must be a no-op, not an error or overwrite
        r = subprocess.run(["sh", script], env=env, capture_output=True, text=True)
        assert r.returncode == 0
    day = dest_root / "2026-07-17"
    assert sorted(p.name for p in day.iterdir()) == ["trades_log.csv"]  # scope filter works
    mtime = (day / "trades_log.csv").stat().st_mtime
    (src / "trades_log.csv").write_text("a,b\n1,2\n3,4\n")
    subprocess.run(["sh", script], env=env, capture_output=True, text=True)
    assert (day / "trades_log.csv").stat().st_mtime == mtime  # never overwritten

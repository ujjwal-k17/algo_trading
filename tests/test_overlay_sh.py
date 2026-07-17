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


def test_ingest_idempotent_per_day(tmp_path):
    src = tmp_path / "src"
    src.mkdir()
    (src / "trades_log.csv").write_text("a,b\n1,2\n")
    (src / "evening.log").write_text("excluded\n")
    dest_root = tmp_path / "raw"
    env = {
        "INGEST_SRC": str(src), "INGEST_DEST_ROOT": str(dest_root),
        "INGEST_DAY": "2026-07-17", "PATH": "/usr/bin:/bin",
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

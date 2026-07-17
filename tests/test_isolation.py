"""Isolation verification suite — re-run anytime with:

    .venv/bin/python -m pytest tests/test_isolation.py -v

Programmatically verifies the workspace's governance invariants:
frozen legacy clone, seal commit integrity, data-gate behavior, workspace
cleanliness, overlay-log schema, and the production deny-list.
"""

import json
import os
import subprocess
import sys
from pathlib import Path

import pandas as pd
import pytest

REPO = Path(__file__).resolve().parents[1]
CLONE = Path.home() / "vendor" / "legacy-engine"
PROD = "/Users/ujjwalkejriwal/Desktop/AI Apps/NSE_Stock_Picks"

sys.path.insert(0, str(REPO / "src"))
import data_gate


def _git(*args: str) -> str:
    out = subprocess.run(
        ["git", "-C", str(REPO), *args], capture_output=True, text=True, check=True
    )
    return out.stdout.strip()


# 1 ── Legacy clone is frozen: no write permission bits anywhere ──────────────

def test_legacy_clone_has_no_write_bits():
    assert CLONE.is_dir(), f"frozen clone missing at {CLONE}"
    offenders = []
    for root, dirs, files in os.walk(CLONE):
        for name in dirs + files:
            p = Path(root) / name
            if p.is_symlink():
                continue
            if p.stat().st_mode & 0o222:
                offenders.append(str(p))
    assert not offenders, f"writable paths in frozen clone: {offenders[:10]}"


# 2 ── Recorded seal SHA matches the commit that sealed SEAL.md ───────────────

def test_seal_commit_sha_matches_git_history():
    recorded = (REPO / "governance" / "SEAL_COMMIT_SHA.txt").read_text().strip()
    touched = _git("log", "--format=%H", "--", "governance/SEAL.md").splitlines()
    added = _git(
        "log", "--diff-filter=A", "--format=%H", "--", "governance/SEAL.md"
    ).splitlines()
    assert added == [recorded], (
        f"SEAL.md was first committed in {added}, but SEAL_COMMIT_SHA.txt says {recorded}"
    )
    assert touched == [recorded], (
        f"SEAL.md has been modified after sealing — commits touching it: {touched}"
    )


# 3 ── data_gate strips post-cutoff rows by default ───────────────────────────

def test_data_gate_strips_post_cutoff_by_default(monkeypatch):
    monkeypatch.delenv("FINAL_TEST", raising=False)
    df = pd.DataFrame(
        {"date": ["2024-07-16", "2024-07-17", "2026-01-01"], "x": [1, 2, 3]}
    )
    out = data_gate.load(df, "date")
    assert list(out["x"]) == [1]
    assert out["date"].max() < data_gate.SEAL_CUTOFF


# 4 ── data/workspace contains zero post-cutoff rows ──────────────────────────

def test_workspace_has_zero_post_cutoff_rows():
    ws = REPO / "data" / "workspace"
    if not ws.is_dir():
        pytest.skip("data/workspace does not exist yet (ingest not built) — vacuously clean")
    for pq in ws.rglob("*.parquet"):
        df = pd.read_parquet(pq)
        for col in df.columns:
            s = df[col]
            if not pd.api.types.is_datetime64_any_dtype(s):
                if "date" not in col.lower():
                    continue
                s = pd.to_datetime(s, errors="coerce")
            bad = s.dropna() >= data_gate.SEAL_CUTOFF
            assert not bad.any(), f"{pq}: column {col!r} has post-cutoff rows"


# 5 ── overlay_log.csv: exactly 5 columns, only valid decisions ───────────────

def test_overlay_log_schema_and_decisions():
    log = pd.read_csv(REPO / "governance" / "overlay_log.csv")
    assert list(log.columns) == [
        "ts_local", "rec_key", "decision", "executed_size", "reason",
    ], f"overlay_log.csv columns drifted: {list(log.columns)}"
    invalid = set(log["decision"].dropna()) - {"EXECUTE", "VETO", "REDUCE"}
    assert not invalid, f"invalid decision values: {invalid}"


# 6 ── deny-list covers the production tree ───────────────────────────────────

def test_settings_deny_list_covers_production():
    settings = json.loads((REPO / ".claude" / "settings.json").read_text())
    deny = settings["permissions"]["deny"]
    for tool in ("Write", "Edit"):
        assert any(
            rule.startswith(f"{tool}(") and PROD in rule for rule in deny
        ), f"no {tool} deny rule covering {PROD}"

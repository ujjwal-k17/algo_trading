import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))
import spec_guard


def _fake_specs(tmp_path, monkeypatch, text="spec body\n", recorded=None):
    """Point the guard at a throwaway specs dir so tests never touch the real one."""
    specs = tmp_path / "specs"
    specs.mkdir()
    spec = specs / "SPEC-TEST-01.md"
    spec.write_text(text)
    if recorded is not None:
        (specs / "SPEC-TEST-01.sha256").write_text(recorded)
    monkeypatch.setattr(spec_guard, "SPECS_DIR", specs)
    return specs, spec


def test_unfrozen_spec_is_refused(tmp_path, monkeypatch):
    _fake_specs(tmp_path, monkeypatch, recorded=None)
    with pytest.raises(spec_guard.SpecGuardError, match="NOT FROZEN"):
        spec_guard.verify_frozen("SPEC-TEST-01")


def test_frozen_spec_verifies(tmp_path, monkeypatch):
    _, spec = _fake_specs(tmp_path, monkeypatch)
    good = spec_guard.sha256_of(spec)
    (spec.parent / "SPEC-TEST-01.sha256").write_text(good + "\n")
    assert spec_guard.verify_frozen("SPEC-TEST-01") == good


def test_altered_frozen_spec_is_refused(tmp_path, monkeypatch):
    _, spec = _fake_specs(tmp_path, monkeypatch)
    (spec.parent / "SPEC-TEST-01.sha256").write_text(spec_guard.sha256_of(spec) + "\n")
    spec.write_text("spec body with a quietly relaxed kill line\n")
    with pytest.raises(spec_guard.SpecGuardError, match="HASH MISMATCH"):
        spec_guard.verify_frozen("SPEC-TEST-01")


def test_unregistered_trial_is_refused():
    with pytest.raises(spec_guard.SpecGuardError, match="no register row"):
        spec_guard.require_trial_row("C1-52WH-NEVER-REGISTERED")


def test_real_spec_52wh_is_frozen_and_registered():
    """The B3 freeze itself: live hash matches, register row exists, they agree."""
    live = spec_guard.verify_frozen("SPEC-52WH-01")
    row = spec_guard.require_trial_row("FREEZE-52WH-0001")
    assert live in row["notes"], "register row must cite the hash it froze"
    assert "FROZEN" in spec_guard.spec_path("SPEC-52WH-01").read_text()


def test_preflight_returns_provenance_stamp():
    stamp = spec_guard.preflight("SPEC-52WH-01", "FREEZE-52WH-0001")
    assert stamp["spec_sha256"] == spec_guard.verify_frozen("SPEC-52WH-01")
    assert stamp["trial_id"] == "FREEZE-52WH-0001"

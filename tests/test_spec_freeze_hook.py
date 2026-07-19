"""The commit-time half of Stage 4 enforcement (the run-time half is test_spec_guard)."""

import hashlib
import shutil
import subprocess
from pathlib import Path

HOOK = Path(__file__).resolve().parents[1] / ".githooks" / "pre-commit"


def _git(repo: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True)


def _make_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init")
    _git(repo, "config", "user.email", "test@test.local")
    _git(repo, "config", "user.name", "Test")
    _git(repo, "config", "core.hooksPath", ".githooks")
    (repo / ".githooks").mkdir()
    shutil.copy(HOOK, repo / ".githooks" / "pre-commit")
    (repo / ".githooks" / "pre-commit").chmod(0o755)
    (repo / "governance" / "specs").mkdir(parents=True)
    return repo


def _write_spec(repo: Path, text: str) -> Path:
    spec = repo / "governance" / "specs" / "SPEC-X-01.md"
    spec.write_text(text)
    return spec


def _freeze(repo: Path, spec: Path) -> Path:
    rec = spec.with_suffix(".sha256")
    rec.write_text(hashlib.sha256(spec.read_bytes()).hexdigest() + "\n")
    return rec


def test_draft_spec_is_freely_editable_until_frozen(tmp_path):
    repo = _make_repo(tmp_path)
    spec = _write_spec(repo, "draft v1\n")
    _git(repo, "add", "-A")
    assert _git(repo, "commit", "-m", "draft").returncode == 0

    spec.write_text("draft v2 — still unfrozen\n")
    _git(repo, "add", "-A")
    assert _git(repo, "commit", "-m", "revise draft").returncode == 0


def test_freeze_commit_is_allowed_then_spec_is_immutable(tmp_path):
    repo = _make_repo(tmp_path)
    spec = _write_spec(repo, "spec text\n")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-m", "draft")

    _freeze(repo, spec)
    _git(repo, "add", "-A")
    assert _git(repo, "commit", "-m", "freeze").returncode == 0  # freeze commit OK

    spec.write_text("spec text with a relaxed kill line\n")
    _git(repo, "add", "-A")
    result = _git(repo, "commit", "-m", "tamper")
    assert result.returncode != 0
    assert "FROZEN" in result.stderr


def test_recorded_hash_cannot_be_rewritten_or_deleted(tmp_path):
    repo = _make_repo(tmp_path)
    spec = _write_spec(repo, "spec text\n")
    rec = _freeze(repo, spec)
    _git(repo, "add", "-A")
    _git(repo, "commit", "-m", "freeze")

    # rewriting the hash would unfreeze the spec
    rec.write_text("0" * 64 + "\n")
    _git(repo, "add", "-A")
    assert _git(repo, "commit", "-m", "rewrite hash").returncode != 0

    _git(repo, "checkout", "--", ".")
    rec.unlink()
    _git(repo, "add", "-A")
    result = _git(repo, "commit", "-m", "delete hash")
    assert result.returncode != 0
    assert "unfreeze" in result.stderr


def test_freeze_commit_with_wrong_hash_is_blocked(tmp_path):
    repo = _make_repo(tmp_path)
    spec = _write_spec(repo, "spec text\n")
    spec.with_suffix(".sha256").write_text("f" * 64 + "\n")
    _git(repo, "add", "-A")
    result = _git(repo, "commit", "-m", "bad freeze")
    assert result.returncode != 0
    assert "mismatch" in result.stderr


def test_freeze_and_edit_in_the_same_commit_is_blocked(tmp_path):
    """The obvious hole: freeze a spec whose recorded hash covers different text."""
    repo = _make_repo(tmp_path)
    spec = _write_spec(repo, "spec text\n")
    _freeze(repo, spec)
    spec.write_text("different text than the hash covers\n")
    _git(repo, "add", "-A")
    result = _git(repo, "commit", "-m", "sneaky freeze")
    assert result.returncode != 0
    assert "mismatch" in result.stderr

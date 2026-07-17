import shutil
import subprocess
from pathlib import Path

HOOK = Path(__file__).resolve().parents[1] / ".githooks" / "pre-commit"


def _git(repo: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", "-C", str(repo), *args], capture_output=True, text=True
    )


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
    return repo


def test_hook_allows_first_seal_commit_then_blocks_edits(tmp_path):
    repo = _make_repo(tmp_path)
    (repo / "governance").mkdir()
    (repo / "governance" / "SEAL.md").write_text("sealed v1\n")
    _git(repo, "add", "-A")
    assert _git(repo, "commit", "-m", "seal").returncode == 0  # first commit OK

    (repo / "governance" / "SEAL.md").write_text("tampered\n")
    _git(repo, "add", "governance/SEAL.md")
    result = _git(repo, "commit", "-m", "tamper")
    assert result.returncode != 0
    assert "BLOCKED" in result.stderr

    # repo must still be committable for legitimate files after the block
    _git(repo, "restore", "--staged", "governance/SEAL.md")
    _git(repo, "checkout", "--", "governance/SEAL.md")
    (repo / "ok.txt").write_text("fine\n")
    _git(repo, "add", "ok.txt")
    assert _git(repo, "commit", "-m", "ok").returncode == 0


def test_hook_blocks_sealed_data_dir(tmp_path):
    repo = _make_repo(tmp_path)
    (repo / "data" / "sealed").mkdir(parents=True)
    (repo / "data" / "sealed" / "holdout.csv").write_text("date,x\n")
    _git(repo, "add", "-A")
    result = _git(repo, "commit", "-m", "leak")
    assert result.returncode != 0
    assert "data/sealed/" in result.stderr

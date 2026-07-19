"""Frozen-spec enforcement (plan_52wh.md Stage 4).

Trial accounting is structural here, not disciplinary. Nothing that joins
returns to signals may run unless:

  1. the spec file's live sha256 equals the hash recorded beside it, and
  2. a register row for the trial exists in research_register_v2.csv.

The pre-commit hook enforces (1) at commit time; this module enforces both at
RUN time, which is the moment that actually matters — a spec edited in the
working tree and never committed would sail past the hook.
"""

from __future__ import annotations

import csv
import hashlib
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SPECS_DIR = REPO_ROOT / "governance" / "specs"
REGISTER = REPO_ROOT / "governance" / "research_register_v2.csv"


class SpecGuardError(RuntimeError):
    """A trial was attempted against an unfrozen, altered, or unregistered spec."""


def spec_path(spec_id: str) -> Path:
    return SPECS_DIR / f"{spec_id}.md"


def hash_path(spec_id: str) -> Path:
    return SPECS_DIR / f"{spec_id}.sha256"


def sha256_of(path: Path) -> str:
    """Hash raw bytes — not decoded text, so line endings cannot drift the hash."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_frozen(spec_id: str) -> str:
    """Return the verified hash of ``spec_id``, or raise ``SpecGuardError``."""
    spec = spec_path(spec_id)
    recorded_file = hash_path(spec_id)

    if not spec.exists():
        raise SpecGuardError(f"spec not found: {spec}")
    if not recorded_file.exists():
        raise SpecGuardError(
            f"{spec_id} is NOT FROZEN — no {recorded_file.name}. "
            "Outcome contact before hash-freeze is a governance breach "
            "(governance/SEAL_COMPANION.md, plan_52wh.md B3)."
        )

    recorded = recorded_file.read_text().split()[0].strip()
    actual = sha256_of(spec)
    if recorded != actual:
        raise SpecGuardError(
            f"{spec_id} HASH MISMATCH — the frozen spec has been altered.\n"
            f"  recorded: {recorded}\n"
            f"  actual:   {actual}\n"
            "A frozen spec is immutable; changes require a new versioned spec."
        )
    return actual


def register_rows(family: str | None = None) -> list[dict[str, str]]:
    with REGISTER.open(newline="") as fh:
        rows = list(csv.DictReader(fh))
    if family is not None:
        rows = [r for r in rows if r.get("family") == family]
    return rows


def require_trial_row(trial_id: str) -> dict[str, str]:
    """Return the register row pre-registering ``trial_id``, or raise.

    Pre-registration means the row exists BEFORE the run. The runner never
    writes this row for you — that would make the check circular.
    """
    for row in register_rows():
        if row.get("trial_id") == trial_id:
            return row
    raise SpecGuardError(
        f"no register row for trial_id={trial_id!r} in {REGISTER.name}.\n"
        "Every trial is pre-registered before it runs (CONTAMINATION_POLICY.md "
        "AMENDMENT A: if in doubt, it is a trial). Append the row, commit it, "
        "then re-run."
    )


def preflight(spec_id: str, trial_id: str) -> dict[str, str]:
    """Full gate for any outcome-touching run. Returns a provenance stamp."""
    spec_hash = verify_frozen(spec_id)
    row = require_trial_row(trial_id)
    return {
        "spec_id": spec_id,
        "spec_sha256": spec_hash,
        "trial_id": trial_id,
        "trial_description": row.get("description", ""),
        "data_tier": row.get("data_tier", ""),
    }

#!/usr/bin/env python3
"""SPEC-52WH-01 trial runner — the ONLY place returns are joined to signals.

Stages 1-3 (`pit_universe`, `expr`, `signal_52wh`, `screen_52wh`, `rebalance`)
are features-only by construction: outcome contact exists nowhere in them. This
script is the single door through which that wall is crossed, and it does not
open unless the governance preconditions hold:

  1. `governance/specs/SPEC-52WH-01.md` live sha256 == recorded hash (B3 freeze), and
  2. the named trial_id is already pre-registered in research_register_v2.csv.

Both are checked BEFORE any panel is read, so a failed preflight cannot leak a
glance at outcomes. On completion the run appends a result reference to the
register (append-only, never an edit).

STATUS: preflight gate is live (Stage 4). The walk-forward engine is Stage 5 and
is NOT built — `--engine` runs therefore stop after preflight with exit code 3.
`--preflight-only` is the sanctioned way to test the gate itself; it touches no
price data at all.
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))
import spec_guard

SPEC_ID = "SPEC-52WH-01"
REGISTER = REPO / "governance" / "research_register_v2.csv"

_BANNER = """
------------------------------------------------------------------------
SPEC-52WH-01 TRIAL RUNNER — outcome contact begins past this point.
  spec_id     : {spec_id}
  spec_sha256 : {spec_sha256}
  trial_id    : {trial_id}
  data_tier   : {data_tier}
  description : {trial_description}
Dev data only (< 2024-07-17, research door). The sealed holdout is NOT
opened here: the family's single final test is a separate Phase D
pre-registration and requires FINAL_TEST=1 (which burns it).
------------------------------------------------------------------------
"""


def append_register_note(trial_id: str, note: str) -> None:
    """Append-only: results are new rows, never edits to the pre-registered row."""
    with REGISTER.open(newline="") as fh:
        fieldnames = next(csv.reader(fh))
    with REGISTER.open("a", newline="") as fh:
        csv.DictWriter(fh, fieldnames=fieldnames).writerow(
            {
                "trial_id": f"{trial_id}-RESULT",
                "date": "",  # stamped by the caller at completion
                "family": "SPEC_52WH",
                "description": note,
                "data_tier": "dev",
                "result": "see notes",
                "notes": note,
            }
        )


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--trial-id",
        required=True,
        help="pre-registered trial_id in research_register_v2.csv (e.g. C1-52WH-0001)",
    )
    ap.add_argument(
        "--preflight-only",
        action="store_true",
        help="verify the freeze + register gate and exit; touches no price data",
    )
    args = ap.parse_args()

    try:
        stamp = spec_guard.preflight(SPEC_ID, args.trial_id)
    except spec_guard.SpecGuardError as exc:
        print(f"[REFUSED] {exc}", file=sys.stderr)
        return 2

    print(_BANNER.format(**stamp))

    if args.preflight_only:
        print("[preflight] gate PASSED — no data touched (--preflight-only).")
        return 0

    print(
        "[STOP] Stage 5 walk-forward engine is not built yet "
        "(plan_52wh.md Stage 5). Preflight passed; nothing was computed.",
        file=sys.stderr,
    )
    return 3


if __name__ == "__main__":
    raise SystemExit(main())

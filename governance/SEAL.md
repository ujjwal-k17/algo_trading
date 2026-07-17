# SEALED HOLDOUT DECLARATION (SEAL v1)

**Status: SEALED upon first commit. This file must never be edited. Any change
to the seal requires a new file `SEAL_v2.md`; this file stays untouched forever.**

## Sealed range

- **Sealed (holdout) data:** all dates from **2024-07-17 (inclusive) through all
  future dates**. No development activity may touch this range.
- **Development data:** strictly **before 2024-07-17**.

## Rules

1. **One final test per signal family, ever.** Each signal family gets exactly one
   pre-registered final test against the sealed range. The pre-registration (family,
   hypothesis, exact procedure, acceptance criteria) must be recorded in
   `governance/research_register_v2.csv` *before* the test is run.
2. **Any peek invalidates.** Any access to sealed-range data outside that single
   pre-registered final test — including "just looking", debugging against it,
   plotting it, or leaking it through a fitted artifact — permanently invalidates
   the final test for that signal family. There is no reset.
3. **One door.** All data access goes through `src/data_gate.py::load()`. The gate
   strips sealed-range rows by default and opens only under `FINAL_TEST=1`, which
   burns the family's single test.
4. **Amendments.** This file is immutable once committed (enforced by the
   pre-commit hook in `.githooks/pre-commit`). Changes to the seal policy require
   creating `SEAL_v2.md` as a new file; v2 must reference v1 and state what changed
   and why.

## Enforcement

- `src/data_gate.py` — the only sanctioned data door (cutoff 2024-07-17).
- `.githooks/pre-commit` — blocks any staged modification to this file after its
  first commit, and blocks committing anything under `data/sealed/`.
- `governance/SEAL_COMMIT_SHA.txt` — records the commit SHA that sealed this file.

Declared: 2026-07-17

# SETUP OF RECORD — alpha-research workspace

Snapshot of everything that exists, as of 2026-07-17.

**Re-verify anytime:**

```sh
cd ~/alpha-research && .venv/bin/python -m pytest tests/test_isolation.py -v
```

## SHAs

| What | SHA |
|---|---|
| Seal commit (`governance/SEAL.md` sealed here, recorded in `governance/SEAL_COMMIT_SHA.txt`) | `b7e4224c311034ca57aa46e9ab38c46f75ce63cc` |
| Legacy engine pin (production HEAD at clone time, `governance/LEGACY_PIN.md`) | `ee7ad13228244f4f27e3d2d839baf70897ff24fe` |
| Workspace commits | `223f360` rules+deny-list → `b7e4224` seal → `216577f` seal SHA record → `612b0cd` legacy pin |

## Paths

| Path | What it is |
|---|---|
| `~/alpha-research` | this repo (git, hooks at `.githooks/`, activated via `git config core.hooksPath .githooks` — required once per fresh clone) |
| `/Users/ujjwalkejriwal/Desktop/AI Apps/NSE_Stock_Picks` | LIVE production — off-limits (CLAUDE.md rule 1; `.claude/settings.json` deny-list blocks Write/Edit/NotebookEdit) |
| `~/vendor/legacy-engine` | frozen clone, detached at `ee7ad13`, `chmod -R a-w`, cloned `--no-hardlinks`; import-only via PYTHONPATH in `.venv/bin/activate` |
| `~/alpha-research/data/legacy_snapshot/trades_log_ee7ad13.csv` | fills snapshot copied from the frozen clone (gitignored) |
| `~/alpha-research/data/sealed/` | post-cutoff raw data (gitignored + pre-commit-blocked; populated by future ingest) |
| `~/alpha-research/data/workspace/` | NOT YET BUILT — gated parquet output of future `scripts/build_workspace.py` |
| `~/alpha-research/.venv` | python 3.14, pandas 3.0.3, pytest 9.1.1, pyarrow 25.0.0 |

## Governance artifacts

- `CLAUDE.md` — 8 binding rules (production isolation, snapshot-only ledger, no broker calls, data-gate-only access, seal immutability, append-only overlay log, import-only clone, stop-and-ask).
- `governance/SEAL.md` — sealed range 2024-07-17 → future; one pre-registered final test per family; immutable (pre-commit enforced, `tests/test_isolation.py::test_seal_commit_sha_matches_git_history` verifies history).
- `governance/research_register_v2.csv` — trial register; opening balance ~51 legacy trials (`INHERITED-0000`).
- `governance/overlay_log.csv` — append-only, exactly `ts_local,rec_key,decision,executed_size,reason`; decisions ∈ {EXECUTE, VETO, REDUCE}; header only so far.
- `governance/LEGACY_PIN.md` — clone pin record.
- `governance/SOP_OF_RECORD.md` — DRAFT derived SOP (uncommitted pending open-question answers).
- `src/data_gate.py` — the only sanctioned data door; strips rows ≥ 2024-07-17 unless `FINAL_TEST=1` (loud burn warning).
- `.githooks/pre-commit` — blocks SEAL.md edits post-seal and any `data/sealed/` commit.
- Tests: `tests/test_data_gate.py`, `tests/test_seal_hook.py`, `tests/test_isolation.py`.

## Pending (awaiting user decisions)

1. Overlay `rec_key` confirmation (proposed `data_date|generated_date|symbol`) → then `scripts/overlay.sh`, `governance/README_overlay.md`, overlay pytest.
2. Snapshot ingest: safe-to-copy markup + legacy cron times → then `scripts/ingest_snapshot.sh`, `scripts/build_workspace.py`, launchd plist, tests.
3. Paper-leg engine: answers to the 9 open questions in `governance/SOP_OF_RECORD.md` §7 (incl. the operational-data-tier governance ruling).

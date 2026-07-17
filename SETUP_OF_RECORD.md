# SETUP OF RECORD — alpha-research workspace

Snapshot of everything that exists, as of 2026-07-17 (post decision-closure).

**Re-verify anytime:**

```sh
cd ~/alpha-research && .venv/bin/python -m pytest tests/ -v
```

(34 tests: isolation, seal hook, both gate doors, overlay shell, ingest
idempotency, paper-leg conventions, overlay-alpha join.)

## SHAs

| What | SHA |
|---|---|
| Seal commit (`governance/SEAL.md`, recorded in `governance/SEAL_COMMIT_SHA.txt`) | `b7e4224c311034ca57aa46e9ab38c46f75ce63cc` |
| Legacy engine pin (production HEAD at clone time, `governance/LEGACY_PIN.md`) | `ee7ad13228244f4f27e3d2d839baf70897ff24fe` |
| Workspace commits | `223f360` rules → `b7e4224` seal → `216577f` SHA record → `612b0cd` legacy pin → `ffd45eb` isolation suite → `b70e928` decision closure → (this commit) settlement unblock |

## Paths

| Path | What it is |
|---|---|
| `~/alpha-research` | this repo (hooks: `git config core.hooksPath .githooks`, once per fresh clone) |
| `/Users/ujjwalkejriwal/Desktop/AI Apps/NSE_Stock_Picks` | LIVE production — off-limits (CLAUDE.md rule 1 + settings deny-list) |
| `~/vendor/legacy-engine` | frozen clone at `ee7ad13`, `chmod -R a-w`, no hardlinks; import-only via PYTHONPATH |
| `data/legacy_snapshot/` | Tier 1 snapshots from the FROZEN CLONE (gitignored): `trades_log_ee7ad13.csv` (ledger, 25 picks, first date 2026-06-29), `recs/` (23 rec CSVs) |
| `data/sealed/raw/YYYY-MM-DD/` | nightly production-output snapshots (gitignored + hook-blocked); first snapshot 2026-07-17, 84 files |
| `data/workspace/` | gated pre-cutoff parquet from `scripts/build_workspace.py` — currently 0 rows by design (all operational data is post-cutoff) |
| `data/derived/paper_leg.parquet` | paper-leg settlements (gitignored); 25 recs, all UNSETTLED pending an OHLC source |
| `~/Library/LaunchAgents/com.alpha.ingest.plist` | nightly ingest at **01:00** (installed + loaded; source copy in `scripts/`) |
| `.venv` | python 3.14, pandas 3.0.3, pytest 9.1.1, pyarrow 25.0.0 |

## Governance artifacts

- `CLAUDE.md` — 8 binding rules.
- `governance/SEAL.md` (immutable) + `governance/SEAL_COMPANION.md` (Tier 1 look-don't-tune addendum; live window starts **2026-06-29**).
- `governance/DECISIONS.md` — RULINGS 1–4 with FACT/ASSUMPTION tags.
- `governance/SOP_OF_RECORD.md` — **CONFIRMED**; rules cited to clone code, §7 resolutions, §8 realism principle.
- `governance/research_register_v2.csv` — ~51 inherited trials (`INHERITED-0000`).
- `governance/overlay_log.csv` — append-only 5-column log; `governance/README_overlay.md` — rec_key `data_date|SYMBOL|seq` + correction convention.
- `governance/LEGACY_PIN.md`, `governance/SEAL_COMMIT_SHA.txt`.
- `src/data_gate.py` — two doors: `load()` (research, strips ≥ 2024-07-17) and `load_operational()` (Tier 1, ≥ 2026-06-29, source+shape validated).
- `src/paper_leg.py` (pure SOP settlement), `src/overlay_alpha.py` (join + weekly summary, all/ex-ambiguous scopes).
- `scripts/`: `overlay.sh`, `ingest_snapshot.sh`, `build_workspace.py`, `run_paper_leg.py`, `com.alpha.ingest.plist`.
- `.githooks/pre-commit` — SEAL.md immutability + `data/sealed/` block.

## Genuinely open items

1. **OHLC coverage (the one real blocker).** OHLC backups are now IN ingest
   scope (RULING 3 amendment) and the settlement + NAV pipelines are fully
   wired through the Tier 1 door — but the only backup production has written
   is a SINGLE-DAY universe snapshot (2026-06-24, before the live window;
   `price_source=yfinance_adj`, so it is an adjusted series — assumption
   falsified from the file) and the nifty backup is empty. Until production
   writes a multi-day backup: `paper_leg.parquet` = 25/25 UNSETTLED (per-row
   reasons in `unsettled_reason`), `build_nav.py` refuses with the exact
   missing inputs (closes for 11 held symbols, 2026-06-29 → 2026-07-17).
2. **Adjustment cross-check vs yfinance** — deferred: needs ≥1 settled trade.
3. **Ex-date flags (RULING 4h)** — 25/25 not-evaluated; needs corporate-action
   data alongside OHLC.
4. **T1 partial-exit check.** Paper leg uses full-exit-at-T1 (DB semantics,
   FACT) per the residual realism ruling; if the desk actually trades the
   50%-partial the alerts describe, say so — that becomes a SOP v2 change.

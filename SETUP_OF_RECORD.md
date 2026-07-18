# SETUP OF RECORD — alpha-research workspace

Snapshot of everything that exists, as of 2026-07-17 (post decision-closure).

**Re-verify anytime:**

```sh
cd ~/alpha-research && .venv/bin/python -m pytest tests/ -v
```

(42 tests: isolation, seal hook, both gate doors, overlay shell, ingest
idempotency, paper-leg conventions incl. dividend credits, overlay-alpha join,
fill-basis preference, RECONSTRUCTED-scope inference + never-merge guard.)

## SHAs

| What | SHA |
|---|---|
| Seal commit (`governance/SEAL.md`, recorded in `governance/SEAL_COMMIT_SHA.txt`) | `b7e4224c311034ca57aa46e9ab38c46f75ce63cc` |
| Legacy engine pin (production HEAD at clone time, `governance/LEGACY_PIN.md`) | `ee7ad13228244f4f27e3d2d839baf70897ff24fe` |
| Workspace commits | `223f360` rules → `b7e4224` seal → `216577f` SHA record → `612b0cd` legacy pin → `ffd45eb` isolation suite → `b70e928` decision closure → `5da00b9` settlement unblock → `1abf750` independent OHLC + settled batch → `df2bfa5` pre-log scope + fills → (this commit) governance closure |

## Paths

| Path | What it is |
|---|---|
| `~/alpha-research` | this repo (hooks: `git config core.hooksPath .githooks`, once per fresh clone) |
| `/Users/ujjwalkejriwal/Desktop/AI Apps/NSE_Stock_Picks` | LIVE production — off-limits (CLAUDE.md rule 1 + settings deny-list) |
| `~/vendor/legacy-engine` | frozen clone at `ee7ad13`, `chmod -R a-w`, no hardlinks; import-only via PYTHONPATH |
| `data/legacy_snapshot/` | Tier 1 snapshots from the FROZEN CLONE (gitignored): `trades_log_ee7ad13.csv` (ledger, 25 picks, first date 2026-06-29), `recs/` (23 rec CSVs) |
| `data/sealed/raw/YYYY-MM-DD/` | nightly production-output snapshots (gitignored + hook-blocked); first snapshot 2026-07-17, 84 files |
| `data/workspace/` | gated pre-cutoff parquet from `scripts/build_workspace.py` — currently 0 rows by design (all operational data is post-cutoff) |
| `data/market/ohlc/`, `data/market/actions/` | independent UNADJUSTED yfinance fetches (gitignored), ledger symbols only, dated parquet, idempotent; refreshed nightly by the ingest agent |
| `data/derived/paper_leg.parquet` | paper-leg settlements (gitignored); 25/25 settled. **Scoped per 2026-07-18 ruling: ENTERED (gate-respecting headline) 11 recs = −1.32R; ASSUMED_ENTRY (AUTO_EXPIRED, counterfactual) 14 recs = +6.50R — never merged** |
| `data/derived/nav.parquet` | DERIVED daily NAV (gitignored): 15 marks 2026-06-29→07-17, unadjusted closes + dividend accrual, −0.70% |
| `data/derived/paper_leg_recs.parquet` | rec-UNIVERSE settlements (18 recs, generated-date anchored, real `data_date\|SYM\|seq` keys) — feeds the RECONSTRUCTED overlay scope |
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

## Governance now in force (2026-07-18 closure)

- `governance/CONTAMINATION_POLICY.md`: outcome-blind trial rule (A) + pool
  eligibility (B); referenced from register CONVENTION-0001. PEAD CAR study
  reclassified as SPEC-PEAD-01's single Tier 2 trial, runs only post hash-freeze.
- AMENDMENT C: Silver ML engine = Tier 3-adjacent (INHERITED-SILVER-0001,
  ESTIMATE ≥8 trials); SPEC-AG-01 stays Tier 2 on carry features only.
- `governance/AB_PREREG.md`: four legacy A/B analyses pre-registered, read
  date 2026-09-27; peek-then-act = logged breach.
- PIT fallback pre-committed (NIFTY100 → F&O-eligible on >2-quarter gap).
- weekly_summary scopes: ENTERED headline / ASSUMED_ENTRY / RECONSTRUCTED —
  all mutually unmergeable.

## Genuinely open items

1. **Overlay log still empty** — analyses 2–4 of AB_PREREG have n = 0 until
   decision-time logging starts. Most time-sensitive item in the program.
2. **Data-sprint unknowns** (per slate register): NIFTY100 PIT constituent
   depth; exchange filing-timestamp corpus; MCX bhavcopy bulk history;
   statutory cost verification vs current contract note; TRI download depth.
3. **Fill-basis starved**: no exit fills in trades_log yet; activates
   automatically.

(T1 semantics resolved 2026-07-18: FULL exit at T1, CONFIRMED-BY-OPERATOR —
SOP_OF_RECORD §7.1.)

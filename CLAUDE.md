# alpha-research — Quantitative Research Workspace

## BINDING RULES

The following rules are **binding on every session in this project**. They are not
suggestions or defaults — they may not be overridden by task instructions, convenience,
or apparent necessity.

1. **Production system is off-limits.** NEVER write to, edit, delete, or run git
   commands that modify anything under
   `/Users/ujjwalkejriwal/Desktop/AI Apps/NSE_Stock_Picks`
   (a production trading system with live cron jobs). Read-only access to it is
   permitted ONLY for:
   - reading its HEAD SHA, and
   - cloning from it.

2. **No direct ledger access.** NEVER read the production ledger database directly.
   Consume only snapshot files under `~/alpha-research/data/legacy_snapshot/`.

3. **No live broker calls.** NEVER make live broker API calls or invoke any
   Kite Connect session/token-generation code path.

4. **All data access goes through the data gate.** All research data access must go
   through `src/data_gate.py`. Never load raw files with post-2024-07-17 rows
   directly in notebooks or scripts.

5. **The seal is immutable.** The file `governance/SEAL.md`, once committed, must
   never be edited. Changes require a new `SEAL_v2.md`.

6. **The overlay log is append-only.** `governance/overlay_log.csv` is append-only;
   corrections are new rows, never edits.

7. **Legacy clone is import-only.** The frozen clone at `~/vendor/legacy-engine`
   (see `governance/LEGACY_PIN.md`) is on `PYTHONPATH` for imports only.
   Never `pip install -e` the clone; never modify it or move its HEAD.

8. **When in doubt, STOP.** If any task appears to require violating these rules,
   STOP and ask the user instead of proceeding.

---

## PROJECT CONTEXT (for every session — read before acting)

### What this workspace is

Quantitative research program targeting an eventual ₹100 Cr AUM fund
(PMS → AIF Cat III path). A prior daily mid-cap momentum system (the
"legacy engine") was KILLED as a fund candidate — real gross alpha
(~18.5%/yr, t≈2.95) fully consumed by friction at 1.6 round-trips/day.
It still runs in production on low capital with a discretionary overlay
(execute/veto/reduce — never add, never size up) for a 60–90 day window
from 2026-06-29. This repo is the isolated research workspace: it measures
that A/B, and develops new Tier 2 strategy families.

### Architecture (two data doors, three report scopes)

- `src/data_gate.py` — the ONLY sanctioned data access:
  - `load(df, date_col)` — research door; strips rows ≥ 2024-07-17 (seal
    cutoff) unless `FINAL_TEST=1` (which burns the family's single test).
  - `load_operational(df, date_col, source)` — Tier 1 forward door; accepts
    only rows ≥ 2026-06-29 (live-window start) from admissible sources
    (`data/legacy_snapshot/`, `governance/overlay_log.csv`, `data/derived/`,
    `data/sealed/raw/`, `data/market/`) with rec_key-joinable shape; generic
    OHLC panels rejected; prints the look-don't-tune notice.
- `src/paper_leg.py` — pure SOP settlement engine (rules in
  `governance/SOP_OF_RECORD.md`, all cited to the frozen clone or
  operator-confirmed). Full exit at T1 (CONFIRMED-BY-OPERATOR). Unadjusted
  prices for level checks; dividends credited (`flag_ex_date`).
- `src/overlay_alpha.py` — overlay vs paper join. Report scopes are NEVER
  merged (enforced in code): provenance DECISION_TIME vs RECONSTRUCTED;
  settlement scopes ENTERED (headline) vs ASSUMED_ENTRY.
- `scripts/` — `overlay.sh` (decision logger, sourced from .zshrc),
  `ingest_snapshot.sh` (nightly 01:00 launchd `com.alpha.ingest`: rsync
  production outputs → `data/sealed/raw/YYYY-MM-DD/`, then yfinance fetch),
  `run_paper_leg.py` (ledger + rec-universe settlement batches),
  `build_nav.py` (DERIVED NAV; refuses to approximate),
  `build_workspace.py` (gated pre-cutoff parquet).
- `.githooks/pre-commit` — SEAL.md immutable after first commit;
  `data/sealed/` never committed. Fresh clones must run:
  `git config core.hooksPath .githooks`.

### Key facts and pins

- Seal commit `b7e4224c311034ca57aa46e9ab38c46f75ce63cc`; cutoff 2024-07-17.
- Legacy engine frozen clone: `~/vendor/legacy-engine` @
  `ee7ad13228244f4f27e3d2d839baf70897ff24fe`, chmod -R a-w, no hardlinks,
  import-only (costs.py etc. via PYTHONPATH in `.venv/bin/activate`).
- rec_key = `data_date|SYMBOL|seq` (seq = generation ordinal; ledger rows
  use seq=1). Ledger pick_date aligns with the rec's GENERATED date.
- Trial register `governance/research_register_v2.csv`: append-only;
  opening balance ~51 legacy trials + Silver ML engine ESTIMATE ≥8
  (Tier 3-adjacent). Outcome-conditional analysis = a trial
  (`governance/CONTAMINATION_POLICY.md`).
- A/B pre-registration: `governance/AB_PREREG.md`, read date 2026-09-27.
  Peek-then-act = logged breach. A green legacy tape earns at most ONE
  forward re-test; the cost-based kill verdict stands regardless.
- Settlement basis: unadjusted yfinance OHLC (validated vs production's own
  backup: 250/250, divergences = adjustment-basis only). Fills > ledger
  entry_price for executed comparisons (ledger records rec-close, not fills).

### Current state (2026-07-18)

- Paper leg: 25/25 ledger recs settled — ENTERED (gate-respecting headline)
  11 recs = −1.32R; ASSUMED_ENTRY 14 recs = +6.50R (tradeability audit:
  12/14 in-zone/trigger-unconfirmed, 2/14 gap-away, no demotion).
  Rec universe: 18/18 settled. NAV: 15 daily marks, −0.70%.
- Overlay log EMPTY — decision-time logging is the most time-sensitive item;
  AB_PREREG analyses 2–4 have n=0 without it. Reconstruction found zero
  inferable vetoes (production ledgers every rec).
- Advancing candidates (Tier 2): SPEC-QFM-01 (fundamental deltas, shadow
  slot 1), SPEC-PEAD-01 (earnings drift, shadow slot 2 — its CAR study is
  its one Tier 2 trial, post hash-freeze only), SPEC-AG-01 (MCX Silver
  carry, queued; ML engine must never feed it).
- Open: data-sprint unknowns (PIT constituents, filing timestamps, MCX
  history, statutory cost verification); fill-basis starved until
  trades_log records exits.

### Environment

`.venv`: python 3.14, pandas 3.0.3, pytest 9.1.1, pyarrow 25.0.0,
yfinance 1.5.1. Run tests: `.venv/bin/python -m pytest tests/ -q` (42).
Full inventory: `SETUP_OF_RECORD.md`. Decisions log: `governance/DECISIONS.md`.

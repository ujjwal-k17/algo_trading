# DECISIONS — signed rulings and their implementation

Each entry: date, ruling, what was decided, rationale, and per-convention tags —
**FACT** (derived from code/data, cited) vs **ASSUMPTION** (convention chosen).

---

## 2026-07-17 — RULING 1: rec_key = `data_date|SYMBOL|seq`

**Branch applied: #2 (versioning found).**
- FACT: no native rec/pick ID exists anywhere in the rec CSV columns (inspected
  all 28 `top5_report_data*_generated*.csv` headers) or `picks_log` schema.
- FACT: re-issue/versioning exists — the same data date is regenerated on later
  dates with materially different picks (data 2026-06-25 has 6 generations,
  2026-06-25 → 2026-07-01, with differing symbol sets). Re-issues are
  cross-day, not intraday, but they are versioning; branch 2 applies.
- Format: `data_date|SYMBOL|seq` where **seq = 1-based ordinal of that data
  date's generation, ordered by generated-date in the filename**
  (ASSUMPTION: numbering convention; ordering itself is FACT from filenames).
- ASSUMPTION: rows sourced from `trades_log.csv` (which records only
  `pick_date`, no generation) get `seq=1`; the ledger tracks the acted-on
  generation.

## 2026-07-17 — RULING 2: operational data tier (Tier 1, look-don't-tune)

- Live-window start: **2026-06-29** — FACT: the earliest ledger date is
  `min(pick_date) = 2026-06-29` in `data/legacy_snapshot/trades_log_ee7ad13.csv`
  (the ruling's 2026-06-20 placeholder adjusted per its own instruction).
- `src/data_gate.load_operational(df, date_col, source)` accepts only rows
  ≥ 2026-06-29 from admissible sources with rec_key-joinable shape; rejects
  seal-gap dates (2024-07-17 ≤ d < 2026-06-29), pre-cutoff dates, generic
  OHLC panels, and non-admissible sources.
- ASSUMPTION: admissible sources are `data/legacy_snapshot/`,
  `governance/overlay_log.csv`, **and `data/derived/`** — the ruling names
  paper-leg-derived data as Tier 1, and paper-leg output lives in
  `data/derived/`, so that path is included.
- Look-don't-tune companion note: `governance/SEAL_COMPANION.md` (SEAL.md
  itself untouched, per seal rule).

## 2026-07-17 — RULING 3: ingest scope + schedule

**Scope applied to the discovered `output/` tree — INCLUDE:**
`top5_report*.csv|.md` (recommendations, all generations), `top20_*.csv`
(wider candidate list), `candle_verdicts_*.json` (entry-confirmation verdicts —
fills-adjacent, the entry oracle), `trades_log.csv` +
`open_positions_migrated_*.csv` (fills/ledger exports), `daily_assessment.md`
(daily assessment), `macro_context.json` (score history).
**EXCLUDE:** `logs/`, `charts/`, all `*.db` (`backtest_3yr.db` — live-DB rule),
`instrument_tokens.json` (token file), `.env`/configs/code, PDFs (human
reports), `backtest_*` artifacts (historical research data, wrong tier),
`prices_eod_backup_*.csv` / `nifty_backup_*.csv` (generic OHLC panels —
inadmissible in Tier 1 by shape; historical market data belongs to the
research tier via its own pipeline), `universe_meta.json`, `asm_list.json`,
`results_*.json`, `held_news_state.json`, `brand_trends.json` (state/config).
- FACT: NAV/equity history exists only inside the live SQLite DB
  (`observer.py:1075` `update_system_equity`) — no flat export exists, and DB
  files may not be read. NAV ingest therefore stays an open item until
  production exports a flat file.

**Schedule** — FACT: there is no user crontab (`crontab -l` = none); the legacy
schedule is launchd agents `com.nse.*`: 08:00 (kiterefresh; weeklydigest Sat),
08:45 (macromorning), 09:00 (preopen), 09:20 (candle), 09:45 (thirtymin),
16:30 (evening), 17:00 Mon–Fri (performance_weekly), 21:15 (fiirescrape),
21:30 (systemcheck; one-off observemonday 2026-07-06).
- Chosen ingest slot: **01:00 IST** (`com.alpha.ingest`). Clears every legacy
  start time by ≥ 3h30m, and clears observed long *runs* too (systemcheck has
  finished as late as 23:36 by file mtimes).

## 2026-07-17 — RULING 4: SOP conventions (see SOP_OF_RECORD.md §7 for full text)

- (a) Entry per clone code (FACT); fill price when unrecorded = next-session
  open (ASSUMPTION, per ruling).
- (b) Same-bar T1+SL: SL-first (ASSUMPTION, conservative-standard — also
  matches the code's check order, `exit_manager.py:111` before `:127`), and
  every such trade FLAGGED; overlay-alpha reports with and without flagged.
- (c) Gap open beyond SL: exit at open (ASSUMPTION, realism > code-faithful
  level fill).
- (d) Gap open beyond T1: exit at open (ASSUMPTION, realism). Extended to T2
  gaps by the same logic (residual principle, ASSUMPTION).
- (e) Time exit: close of final holding day; holiday/halt → next session's
  close (ASSUMPTION). Holding = 5 sessions, entry day = Day 1 (FACT:
  `market_calendar.py:170-178`, `picks_log.py:44-56`).
- (f) Halted/limit-locked: carry to first available price, FLAG (ASSUMPTION).
- (g) Full fill at rec size — the paper leg is a counterfactual of the SOP,
  not of liquidity (ASSUMPTION, recorded as caveat in SOP_OF_RECORD.md).
- (h) Adjusted price series; FLAG recs whose window spans an ex-date
  (ASSUMPTION; flag is data-dependent — set when corporate-action data is
  supplied, otherwise recorded as not-evaluated).
- (i) Residual principle: REALISM, biased in neither direction (stated in
  SOP_OF_RECORD.md §8).
- **Q1 (T1 semantics), resolved via residual principle:** paper leg exits
  **fully at T1** — FACT: that is what the engine's DB records
  (`exit_manager.py:127-134,161-168`); the 50%-partial language exists only in
  the human alert text (`:220-227`). ASSUMPTION: choosing DB semantics over
  alert semantics. If the desk actually trades partials, say so and this
  becomes a v2 change.

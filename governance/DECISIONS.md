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

## 2026-07-17 — AMENDMENT to RULING 3: OHLC backups enter ingest scope

**Rationale: settlement source; original exclusion was scope collateral.**
- `prices_eod_backup_*.csv` and `nifty_backup_*.csv` are ADDED to the ingest
  include list. They are production data outputs and the sanctioned settlement
  source for the paper leg. The `.db`/`.sqlite` exclusion stands untouched.
- Mechanics: snapshot OHLC under `data/sealed/raw/` is admissible to
  `data_gate.load_operational()` **solely via the settlement join** (rows must
  carry rec_key — the shape rule is unchanged; `data/sealed/raw/` added to the
  admissible-source list under this amendment). ASSUMPTION: source-list
  mechanics; the sanction itself is the amendment (FACT of the ruling).
- ASSUMPTION (to verify): the broker OHLC backup is UNADJUSTED — checked
  against the file and cross-checked vs an adjusted source; findings reported
  in-session before any source switch.

## 2026-07-17 — AMENDMENT to RULING 4h + RULING 2 (Option 1 ruling, settlement basis)

Context (FACT): validation of yfinance vs production's 2026-06-24 backup —
250/250 fetched, 200 exact (≤0.001%), 50 divergent >0.05% with IDENTICAL
diffs across all four OHLC fields (uniform rescale = adjustment-basis drift
from ex-dates after 2026-06-24, not data error). Source identity established.

- **Ruling h AMENDED — unadjusted prices for all level comparisons.**
  Fetch with `auto_adjust=False`. Rationale: realism principle — replicates
  `exit_manager.py`'s actual check, which compares fixed rec levels against
  that day's actual traded prices (no future adjustments exist at check time).
  Rec levels stay exactly as recorded — no rescaling.
- Cash dividends with ex-date inside a holding window are CREDITED to that
  trade's P&L/R (holder entered before ex-date and still held on it).
  `flag_ex_date` is retained as the dividend-credit marker (True = credited,
  False = evaluated & none, None = actions data unavailable).
- NAV: unadjusted closes + dividend accrual, same basis.
- Adjusted-basis re-validation of 2026-06-24 SKIPPED per ruling; the
  settlement gate instead reconciles paper-leg entry prices vs the fills
  recorded in trades_log for entered trades, reported before paper_leg.parquet
  is written.
- **RULING 2 AMENDED:** `data/market/` (independent yfinance fetches: `ohlc/`,
  `actions/`) added to `load_operational()`'s admissible sources — same shape
  rules (settlement joins on rec keys; generic research panels still rejected).

## 2026-07-17 — Adjustment integrity + NAV (closure findings)

- FACT (from the file itself): `prices_eod_backup_20260624.csv` self-declares
  `price_source = yfinance_adj` on all 250 rows — the backup is an ADJUSTED
  series, falsifying the "unadjusted broker data" ASSUMPTION. No source switch
  needed or made.
- FACT: the backup is a SINGLE-DAY universe snapshot (250 symbols, all rows
  2026-06-24 — before the live window starts 2026-06-29), and
  `nifty_backup_20260624.csv` is EMPTY (header only). Settlement therefore
  remains blocked: 0 of 25 paper-leg rows settle; every row's reason recorded
  in `paper_leg.parquet.unsettled_reason`.
- Cross-check of 5 settled trades vs yfinance: NOT PERFORMED — zero settled
  trades exist to check. Deferred until first settlements.
- RULING 4h ex-date flags: 25/25 rows carry `flag_ex_date = None`
  (not-evaluated — no corporate-action data supplied yet), 0 flagged.
- **NAV — DERIVED, never from the DB.** `scripts/build_nav.py` marks
  positions at close (5-slot convention, FACT observer.py:1060-1073) and
  REFUSES to approximate when closes are missing. Current status: refused —
  missing daily closes for 11 held symbols across 2026-06-29 → 2026-07-17;
  the only sanctioned OHLC is the single pre-live-window day above.
  `data/derived/nav.parquet` will exist as soon as a multi-day adjusted OHLC
  export enters the ingest (already in scope per the RULING 3 amendment).

## 2026-07-18 — Tradeability audit of the 14 ASSUMED_ENTRY recs (operator-ordered)

Run under the Tier 1 settlement/monitoring sanction as QA of a settlement
convention on the burned family — directional only, no significance claims,
not signal research; not logged as a trial.

Method: each expired rec's assumed-entry OPEN tested against its entry_type's
own gate geometry from the clone (`preopen_check.py`): CONDITIONAL skip-floor
= hold_level(close×0.995) − 1%; W&W requires gap ≥ +0.5% (none present in the
14); all 14 are CONDITIONAL variants. Caveats: (a) the true gate is the
9:20/9:45 candle close + volume ratio — open is the daily-data proxy,
consistent with the paper leg's own entry convention; (b) volume confirmation
is unobservable from daily bars, hence "trigger unconfirmed", not "would have
confirmed"; (c) 3 recs are "CONDITIONAL (expiry day — stricter)" approximated
with standard geometry — the stricter rule's exact terms were not extracted.

**Finding: 2/14 OUTSIDE the zone (never executable as assumed) — both
MOTHERSON expiry-day recs gapping −1.8%/−2.3%, both −1R. 12/14 INSIDE the
zone with the trigger simply unconfirmed, netting +8.50R.**

**Consequence: majority are NOT gap-aways → the conditional annotation
("materially non-executable — selection-biased") and demotion below
RECONSTRUCTED do NOT apply. ASSUMED_ENTRY scope reporting unchanged.**
Directional observation (burned family, n=12, no claim): the positive skew of
ASSUMED_ENTRY is not price-unreachability — excluding the two unreachable
rows RAISES the scope to +8.50R. The recs the system declined were mostly
in-zone but failed candle/volume confirmation; if anything, the confirmation
gate — not the price zone — is what rejected the profitable counterfactuals.

## 2026-07-18 — GOVERNANCE AMENDMENTS A/B/C + PIT fallback pre-commitment

- **AMENDMENT A (outcome-blind trial rule)** adopted verbatim in
  `governance/CONTAMINATION_POLICY.md`; referenced from the register
  (CONVENTION-0001). **Consequence:** the PEAD CAR event-study is RECLASSIFIED
  as SPEC-PEAD-01's single Tier 2 trial (it observes outcomes conditional on
  the signal) and may run only after that spec's hash is frozen. The earlier
  slate's description of it as a "zero-trial diagnostic" is superseded.
- **AMENDMENT B (pool eligibility)** adopted verbatim in the same policy: the
  pooled program NAV test admits only sleeves that individually survived their
  shadow stage; pooling never resurrects a killed or unfinished sleeve.
- **AMENDMENT C (Silver tier split):** the existing Silver ML forecasting
  engine (SARIMAX/GARCH/LightGBM/Kalman) is **Tier 3-adjacent** — its model
  fitting constituted unregistered outcome iteration. SPEC-AG-01 remains
  Tier 2 strictly on carry/term-structure/seasonality features. The ML
  engine's forecasts must NEVER be merged into, or used to filter, SPEC-AG-01.
  Inherited-trial note logged (INHERITED-SILVER-0001): ESTIMATE ≥8 trials,
  basis = 4 model families × ≥2 fit/tune cycles, exact count unrecorded.
- **PIT fallback pre-commitment (fixed before any constituent data is
  inspected):** "If NIFTY100 PIT constituent history has any gap > 2
  consecutive quarters in the development window, SPEC-QFM-01 switches to the
  F&O-eligible PIT universe, logged as a spec clarification, not a
  variant/trial."
- **Assumed-entry audit consequence:** paper rows settled from AUTO_EXPIRED
  recs (system entry gate never confirmed; entry assumed at next open) are
  reported in a separate ASSUMED_ENTRY scope; the gate-respecting (entered)
  figure is the weekly_summary headline. Like RECONSTRUCTED, scopes are never
  merged.
- **T1 semantics: RESOLVED 2026-07-18 — operator answered FULL exit at T1.**
  SOP_OF_RECORD Q1 marked CONFIRMED-BY-OPERATOR; the paper leg's
  full-exit-at-T1 convention is now operator-confirmed fact, not an inference.
  No SOP v2, no engine change.

## 2026-07-17 — RULING: pre-log window (RECONSTRUCTED scope) + fills basis

- `overlay_log.csv` stays EMPTY for trades before its first real entry — no
  backfilled decisions.
- For 2026-06-29 → first-log-date, overlay_alpha derives executed/veto sets by
  joining trades_log against the rec universe directly: a rec with a matching
  ENTERED trade → EXECUTE (size 1); a rec with NO matching trade → inferred
  VETO (size 0). Reported under provenance **RECONSTRUCTED** — never merged
  with the DECISION_TIME scope (`weekly_summary` raises on mixed provenance).
- ASSUMPTION: recs whose matching trades_log row is `AUTO_EXPIRED_5_SESSIONS`
  are SYSTEM_NO_ENTRY (entry gate failed — no user discretion involved);
  excluded from overlay grading, count reported.
- ASSUMPTION: where a (data_date, symbol) has multiple generations, the LAST
  generation is taken as the acted-on rec for reconstruction.
- ASSUMPTION: REDUCE cannot be inferred from the ledger (no size data);
  reconstruction is binary EXECUTE/VETO.
- **Fills basis (FACT-driven):** where actual fill prices exist, overlay
  comparisons use FILLS, not ledger entry_price — entry reconciliation showed
  the ledger records rec-close while real fills print at open; the +0.33% mean
  is a measurement artifact, not overlay skill. Implemented: fill-based
  executed R wherever trades_log carries an actual exit price; paper values
  otherwise. To grade inferred vetoes, the paper leg settles the full rec
  universe (data/derived/paper_leg_recs.parquet) alongside the ledger batch.

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

## 2026-07-19 — RULING 5: A2 cost stack closed on web-verified schedule

- FACT: statutory components verified from primary/published sources
  (2026-07-19): STT delivery 0.10% buy AND sell, intraday 0.025% sell only;
  NSE cash exchange outflow 0.00307%/side (₹306.99 txn + ₹0.01 IPFT = ₹307/cr,
  circular NSE/FA/73061 dt 2026-02-27 effective 2026-03-01, filed at
  governance/evidence/NSE_FA_73061_transaction_charges_effective_2026-03-01.pdf);
  SEBI turnover fee ₹10/cr/side +18% GST; stamp duty buy-side only, delivery
  0.015% / intraday 0.003%; GST 18% on (brokerage + exchange txn + SEBI + DP).
  Cross-checked Zerodha vs Upstox published schedules; the one divergence
  (exchange charge) resolved by the NSE circular — Upstox page stale.
- ASSUMPTION (operator, 2026-07-19): the web-verified discount-broker schedule
  equals what the actual contract note bills — brokerage delivery ₹0, intraday
  min(0.03%, ₹20)/order; DP on delivery sell ₹15.34/scrip/day (GST-inclusive).
  Contract-note line-by-line reconciliation WAIVED by operator. If a real
  contract note later diverges, src/costs_in.py constants get a correction and
  any trial run on the old constants is rerun before its result is cited.
- Slippage is NOT part of this ruling — it stays an explicit separate
  parameter (literature floor ≥0.05–0.10%/side; higher for mcap ranks
  201–1000), never baked into the statutory constants.
- Consequence: open unknown #4 (statutory cost verification) is CLOSED;
  src/costs_in.py is buildable and its acceptance test is the worked
  round-trip recomputation, not contract-note reconciliation.

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

## 2026-07-19 — RULING 6: hash-freeze consumes no shadow slot (B3 executed)

- The gating question at B3 was whether freezing SPEC-52WH-01 jumps the queue,
  since 52WH sits behind SPEC-QFM-01 / SPEC-PEAD-01 (shadow cap 2) and
  SPEC-AG-01.
- FACT: the cap-2 constraint is written against the **shadow-book stage**
  (CONTAMINATION_POLICY.md AMENDMENT B: pooling admits only sleeves that
  individually survived their shadow-book stage; SPEC-52WH-01 §10 and
  plan_52wh.md Phase D gate the sealed test on a slot opening). No governance
  document conditions a *spec freeze* on slot availability.
- FACT: plan_52wh.md B3 as written already said "pre-cutoff development may
  proceed, no slot-jumping" — freezing is the precondition for that pre-cutoff
  development (Phase C), not a step past it.
- RULING: freezing makes the text binding and unlocks outcome contact on **dev
  data < 2024-07-17 only**. It consumes no shadow slot. QFM + PEAD retain both;
  AG-01 remains ahead of 52WH in the queue for the slot itself. Phase D sealed
  pre-registration for 52WH still requires a slot to open.
- Consequence: SPEC-52WH-01 frozen at sha256
  4b58f285255db1b35bdf831aaaaa16aae6bde8bbf38987a501194bf89ddbbefc, register
  row FREEZE-52WH-0001. The freeze row is explicitly NOT a trial (no outcome
  observed); Phase C trials get their own rows and their own count toward the
  register's cumulative total for SPA/deflated-Sharpe deflation.
- ASSUMPTION flagged for the operator: if the intended reading of the cap was
  ever "no family may even freeze until a slot frees", say so — the freeze
  would then need a v2 spec to unwind, since a frozen spec cannot be edited.

## 2026-07-20 — RULING 7: trial_sr_std is NOT reconstructable; SPA gates, DSR reports

Context: the Deflated Sharpe Ratio deflates an observed Sharpe against SR0, the
Sharpe the best of N trials reaches by luck. SR0 = trial_sr_std x m(N), where
m(52) = 2.2913. SR0 scales LINEARLY with trial_sr_std but only logarithmically
with N — one more trial moves the bar 0.32%, doubling the trial count moves it
11%, doubling the dispersion moves it 100%. The dispersion is therefore the
dominant input, and C1-52WH-0001 used trial_sr_std = 0.5 as an operator-facing
ASSUMPTION with no measured basis.

- ATTEMPTED (2026-07-20): reconstruct the dispersion from legacy artifacts.
  Sources read (read-only, frozen clone ~/vendor/legacy-engine): build_tracker.md
  Runs 1-10 reported Sharpes, and output/backtest_run7/run8_*_equity.csv daily
  equity curves. Curves gated through data_gate.load (research door) to the
  pre-cutoff window 2023-07-04 -> 2024-07-16, 254 sessions, active Sharpe
  computed vs NIFTY 500 TRI.
- FACT: only THREE distinct variants exist. backtest_run7_equity.csv is
  byte-identical to run8_S1 (abs Sharpe 3.344513 both) — a duplicate, not a
  data point. Measured active Sharpes: S1 1.414, S2 2.230, S3 0.897.
- FACT: point estimate std(ddof=1) = 0.672; chi-square 95% CI on that standard
  deviation at df=2 is **[0.35, 4.22]**. At the upper end SR0 would be 9.68,
  which is absurd on its face. The estimate is uninformative.
- FACT (structural, independent of sample size): S1/S2/S3 are three tweaks of
  ONE system (live config; + entry filters; + expectancy geometry). DSR's null
  concerns dispersion across the BREADTH of the search. Variants of one family
  scatter far less than 51 genuinely different ideas, so this measurement
  answers the wrong question and answers it too low.
- FACT: only written-up runs carry Sharpes; abandoned explorations left none.
  The recorded sample is selected on completeness, truncating the left tail.
- FACT: the gated window is one year of a violent mid-cap bull (absolute
  Sharpes 2.9-4.2) — regime-inflated, not a stable estimate.
- RULING: trial_sr_std is NOT measurable from this program's artifacts. The
  reconstruction route is CLOSED; do not repeat this archaeology.
- RULING: **SPA is the gate; DSR is reported, not gating.** Hansen SPA
  bootstraps the actual return series and does not depend on trial_sr_std at
  all, so it is robust to exactly the uncertainty above. SPEC-52WH-01 §8 already
  gates on SPA p and net IR — that was correct as frozen, and the DSR floor
  floated on 2026-07-19 is WITHDRAWN: hard-coding an unmeasurable constant into
  a binding kill line would have been a mistake. No SPEC-52WH-02 is needed.
- ROBUST FINDING that survives the parameter uncertainty: across the whole
  informative range (0.35 -> 0.67), SR0 lands between 0.80 and 1.54.
  C1-52WH-0001's screened active Sharpe of 0.349 sits below ALL of them. The
  qualitative warning about that result holds even though its precise DSR
  (0.025) does not.
- Note on discipline: the adopted dispersion was pre-committed BEFORE computing
  it, precisely because calibrating it after seeing whether it helps a family is
  the contamination this policy exists to prevent. The measured point estimate
  (0.672) came out HIGHER than the 0.5 assumed, i.e. the evidence cut AGAINST
  the family under test.
- OPEN (operator decision, not yet taken): the pre-registered DSR REPORTING
  band. Proposed 0.35 / 0.50 / 0.70 — the informative part of the CI with the
  original assumption as midpoint — reported in every trial write-up while SPA
  gates. Until the operator sets it, trials report DSR at 0.5 and cite this
  ruling for the caveat.

## 2026-07-20 — RULING 8: unlogged rec = accepted recommendation (DEFAULT_EXECUTE)

**Operator ruling.** Standing policy: if the operator logs no overlay decision
for a rec, the decision was to accept the system's recommendation as issued —
EXECUTE at full slot size. Silence is an affirmative default, not an absence.

- FACT: the overlay is veto/reduce only. There is no action the operator can
  take that is BOTH silent AND different from the recommendation, so silence is
  behaviourally indistinguishable from accept-as-issued at the decision layer.
- FACT: the decision layer is separate from the entry layer. A rec the operator
  accepted may still never enter (`AUTO_EXPIRED_5_SESSIONS`, 14 of 25 in
  `trades_log_ee7ad13.csv`). RULING 8 speaks ONLY to the decision; entry
  outcomes continue to be graded as SYSTEM_NO_ENTRY where the gate did not fire.
- Implemented: `overlay_alpha.default_execute_overlay()`, provenance
  **`DEFAULT_EXECUTE`**. `weekly_summary` raises on ANY mixed provenance, so the
  scope cannot be merged with DECISION_TIME or RECONSTRUCTED by accident.

**Scope limit (binding).** DEFAULT_EXECUTE is NOT decision-time evidence.
An inferred row cannot distinguish "reviewed and accepted" from "never looked",
and AB_PREREG analyses 2-4 admit the DECISION_TIME scope only. RULING 8 does not
amend AB_PREREG and does not move the 2026-09-27 read date. The default scope is
reported BESIDE the pre-registered analyses, never inside them.

**Nothing is written to `overlay_log.csv`.** The log remains a record of
decisions the operator actually entered. The file is append-only, so
materialising inferred rows would irreversibly destroy the ability to ask which
decisions were affirmed — while the inference itself is cheap and reproducible
at analysis time. ASSUMPTION: this is the operator's intent; if the operator
instead wants inferred rows materialised, that is a new ruling.

**Consequence the operator accepted, recorded here so it is not re-litigated:**
under RULING 8 an unlogged day yields EXECUTE rows, so analyses 3 (veto quality)
and 4 (reduce efficacy) gain NOTHING from silence — they need affirmative VETO
and REDUCE rows and will stay at n=0 without them. RULING 8 removes the cost of
a missed EXECUTE day; it does not remove the need to log an intervention on the
day it is made.

## 2026-07-20 — Legacy variant scopes (outcome-blind) + production verification

Two operator-proposed variants were scoped OUTCOME-BLIND. **No trial was spent;
no backtest was run; no return, IR, Sharpe or hit-rate was computed.** Both
verdicts below are design/feasibility findings, not results, and neither is
charged against the register's trial count.

### VARIANT A — remove the 5-session time exit; 5 -> 10 slots; hold to signal

**Verdict: testable after a ~7-13 day build, but MISAIMED as specified.**

- FACT (arithmetic, `src/costs_in.py` + RULING 5, no outcome data): one delivery
  round trip costs **0.23782%** of a Rs.1,00,000 slot (buy Rs.118.74 / sell
  Rs.119.08 incl. DP Rs.15.34). With every slot filled and average holding
  period H sessions, book drag = `(252/H) x 0.23782%`.
- FACT (consequence): drag is a function of **H alone and is INDEPENDENT of slot
  count** — 5 slots at H=5 and 10 slots at H=5 both drag **11.99%/yr**. The
  5->10 change buys diversification, **not** friction relief. Drag is exactly
  proportional to 1/H, so **H=15 sessions cuts friction to one third** at every
  slippage level (11.99% -> 4.00% statutory-only; 17.03% -> 5.68% at the 0.05%
  floor).
- FACT: the kill cited 1.6 round-trips/day against a NOMINAL 5-day timer, which
  implies realised **H ~= 3.1 sessions**. Turnover ran ~60% hotter than the
  timer, i.e. **SL/T2/T1 were the binding exits and the timer rarely fired.**
  ASSUMPTION: the cause is early target/stop hits (the gap itself is FACT).
- **Therefore removing the timer raises the CEILING on H; it does not set H.**
  The lever that actually moves H is the target/stop levels — a different and
  larger axis than the one proposed.
- FACT: machinery exists. `~/vendor/legacy-engine/backtest_multiyear.py`
  generates ranked picks for arbitrary past dates (`day_ranking` applies an
  as-of filter before scoring); `SLOTS`/`HOLD_SESS` are two constants and three
  existing harnesses already import-and-override them. Build items: repo-side
  loader replacing the sqlite `load_bt` (rule 2), an UNADJUSTED dev-window panel
  (RULING 4h level-check basis) or a ruling accepting adjusted, universe +
  industry map, cost accounting (the harness has none), TRAP 1/6 coverage
  assertions.
- FACT: `SWEEP_HOLDING.md` (2026-07-14) already swept `HOLD_SESS` in
  {1,3,5,10,20} at a cost of 5 trials, with `SLOTS=5` fixed throughout. Its
  results were deliberately NOT read (outcome contact, unauthorized). The
  10-slot interaction is genuinely unswept.
- FACT: the frozen clone's own CLAUDE.md declares Signal-1 CLOSED and classes
  exit/universe/cost changes on that chassis as VARIANT-OF-CLOSED-SIGNAL absent
  a signed classification. **OPEN — operator classification required before any
  build.**
- Queues behind OPEN OPERATOR DECISION 2 (habitat defect), same as C1 attempt 2.

### VARIANT B — raise vision weight / lower technical weight in the top-5 scoring

**Verdict: NOT TESTABLE AS SPECIFIED, and NOT CITABLE EVEN IF RUN. Recorded as a
disclosed dead end (TRAP 4: a disclosed gap is an asset; an invented number is a
liability at due diligence).**

- FACT: no dev-window (< 2024-07-17) vision scores exist anywhere accessible. A
  repo-wide content grep for `vision_score` across `data/` returned ZERO files.
  Earliest vision-adjacent artifact is **2026-06-18** — inside the Tier 1
  look-don't-tune window. Dev-window coverage is zero, not sparse.
- Four INDEPENDENT disqualifiers on the regenerate-scores-now route, any one
  sufficient:
  1. **Memorisation is unfalsifiable in this design.** A model trained past the
     dev window scoring a historical chart may know the outcome; no detection
     test of citable strength was identifiable. (Placebo-on-synthetic tests a
     different distribution; symbol masking fails on recognisable index-wide
     event shapes; a beats-baseline test is itself outcome-conditional = a
     trial.)
  2. **The renderer leaks and has no as-of mode.** `charts.py` stamps
     `today_ist()` into the chart TITLE (the model reads the date off the
     image), and `render_chart` unconditionally takes the last N sessions with
     no as-of parameter. An as-of render requires modifying the frozen clone
     (FORBIDDEN, rule 7) or reimplementing it — at which point the study
     measures a different system. Mitigating FACT: MAs are computed on full
     history then reindexed, so indicator warmup does NOT leak forward.
  3. **The model pin is a mutable alias** (`claude-sonnet-4-6`), not a dated
     snapshot — the study is not reproducible, which matters at PMS
     registration.
  4. **Non-determinism over a step function** — `compute_vision_score` maps
     categoricals through a fixed rule table, so one flipped category moves the
     score 25 points. Discontinuous, not smooth noise.
- FACT (undercuts the operator's stated rationale): vision is NOT an independent
  read of the chart. `vision.py:59-86` feeds the model the technical metrics
  (RSI-14, ADX, price-vs-SMA50/200, ROC-21, dist-from-52w-high, vol-vs-avg20)
  alongside the image, and the prompt instructs it to reconcile against them
  with hardcoded rules. The docstring records WHY: unconstrained pixel-only
  reads produced STAGE_MISCLASSIFIED x4 and RESISTANCE_MISREAD x6 — **the
  unanchored vision read was WORSE, and anchoring to technicals was the fix.**
- Precedent applies: `research_register_v2.csv` INHERITED-SILVER-0001 (ESTIMATE
  >=8 trials, AMENDMENT C) bars the Silver ML engine's forecasts from feeding
  SPEC-AG-01 for contamination by unregistered outcome iteration. Pretraining on
  the outcome period is a stronger and less auditable contamination.

### Production verification (operator-run, read-only, HEAD 8e4e6f7)

- FACT: the top-5 is a **gate cascade**, not the head of a weighted sum. Vision
  is absent from the top-20 stage entirely (`composite_score`, five 0.20 TA
  weights, selects the 20; vision is called ON the 20 afterwards). Live weights
  are `_FINAL_WEIGHTS_V2` (ta 0.40 / vision 0.10 / fundamental 0.20 / catalyst
  0.15 / quality 0.10 / reversal_rs 0.05). An LLM binary veto on
  `include_in_top5 == "no"` is a strictly more powerful lever than the 0.10
  weight. Macro modifier is 0.70-1.155 (1.10 base stacking with 1.05 TAILWIND),
  applied inside `compute_final_scores` before the sort.
- FACT: the dead-`config.FINAL_WEIGHTS` defect was REAL at clone pin ee7ad13 and
  was FIXED in production on 2026-07-18 (commit f67fc20) — the symbol was
  deleted, not left dead. **No config-vs-live divergence exists at HEAD**, and
  `backtest_multiyear.py:42` imports `_FINAL_WEIGHTS_V2` from `final_score`, so
  harness and production share one dict.
- FACT: `run_phase2.py:699-714`'s `blended = 0.80*composite + 0.20*vision` is
  **display-only** — read three times inside a 20-line block, never attached to
  `top20`, never persisted, never reaching selection. But it prints as
  "Interim re-rank: TA 80% + Vision 20%" with `new_rank` and up/down arrows,
  asserting a re-rank that never happens, at weights contradicting the live
  40/10-of-six, over a two-factor number that ignores fundamentals, catalyst,
  quality, reversal-RS and the macro modifier. Same shape as the gap #74
  red_flags defect: not a wrong computation, a human-facing number contradicting
  the live one.
- **CLOSED 2026-07-20 (was OPEN/UNKNOWN) — human-facing only, NOT model-input
  contamination.** TRACED: `observe_monday.py:40-47`'s `evening_log_since_start`
  returns RAW unfiltered text (`rfind` anchor, slice to EOF, no end bound), and
  the misleading table IS inside the returned string (verified empirically:
  anchor at `evening.log:3416`, header at `:4068`). But its single caller
  (`:59`) only regex-mines for counters/source tags and renders a Telegram
  message — no `anthropic` import, no prompt construction, absent from the
  repo-wide LLM call-site grep. All four `evening.log` readers are non-LLM;
  every `client.messages.create` is fed from DB rows, charts or DataFrames,
  never log text. `observe_monday.py` is additionally hard-gated to
  `TARGET_DATE = "2026-07-06"` and `sys.exit(0)`s otherwise, so it currently
  no-ops.
- FACT (previously ASSUMPTION, now TRACED): the block DOES execute on the
  scheduled path — plist -> `guarded_run.py` (dup2 fds -> execv) ->
  `run_evening.py` -> `run_phase2.__main__` -> `main()`; lines 692-714 sit at
  plain function-body indentation with no flag or verbose gate. Empirically
  `grep -c "Interim re-rank" logs/evening.log` = 3, one per run (16/17/20 Jul),
  each within minutes of the 16:30 trigger. It is written to disk nightly.
- **LATENT RISK (recorded; not a defect today).** The contamination boundary is
  BEHAVIOURAL, not structural: the raw slice CONTAINS the misleading table and
  is safe only because the current caller happens to regex-mine it. Any future
  path that pipes `evening_log_since_start()` output into a prompt would
  contaminate a model with a stated weighting (80/20 over two factors) that
  contradicts live scoring (40/10 of six) — silently, in this program's
  characteristic shape (TRAP 6). The durable fixes are upstream and cheap:
  correct the printed label, or stop printing the block. Hardening the consumer
  would leave the trap armed for the next one.
- FACT: daily artifacts do NOT carry `vision_score` or `composite_score` —
  `top5_report_data*.csv` has `final_score` only; `vision_support`/`_resist` are
  price LEVELS, not scores. Both live in sqlite alone.
  **RECOMMENDED (outcome-blind, no trial): persist both per candidate into the
  sealed snapshot going forward.** That is the difference between being able to
  ask the Variant B question in 12 months and not. It also unlocks the free
  rank-perturbation diagnostic (how often the top-5 set changes under a weight
  delta) permitted by CONTAMINATION_POLICY.md.
- Doc drift, NOT corrected (production is off-limits to this repo):
  `SYSTEM_MASTER_REFERENCE.md:502-503, 1291-1292` and `AUDIT.md:35` still
  describe `config.FINAL_WEIGHTS` as existing-but-dead — false at HEAD.
  `Context.md:319` is correct. This stale documentation is the likely source of
  the clone-derived error above.

## 2026-07-20 — RULING 9: clone-derived claims about PRODUCTION require HEAD check

`~/vendor/legacy-engine` is pinned at ee7ad13 and is a SNAPSHOT as well as an
import-only source. A claim read out of the clone is a claim about the pin, not
about the running system.

**Binding:** any assertion that production currently behaves in some way, when
sourced from the clone, must be verified against production HEAD by the operator
(read-only) before it is acted on, cited, or written up as fact. Verified
2026-07-20 at cost: a real-at-pin defect was reported as live five days after it
had been fixed upstream.

Corollary: production DOCUMENTATION can be stale in the same way and is not
evidence of current behaviour — see the `SYSTEM_MASTER_REFERENCE.md` /
`AUDIT.md` drift recorded above. Prefer reading the code at HEAD.

## 2026-07-20 — Pillar scores now persisted (production, operator-run) + a correction

**DONE (production, operator-executed, read-only from this repo's side):**
`vision_score` and `composite_score` appended to `top5_report_data*.csv`
(header 30 -> 32 cols, prior column order byte-identical, new cols last).
Verified by RUNNING `save_reports()` into a scratch dir against live values —
8/8 assertions, real data (NAUKRI 84.0/0.754, LLOYDSME 81.0/0.779,
RADICO 100.0/0.858), stub-vision rows write 50.0 not empty. Committed
separately from the display-only fix; not pushed; no restart needed (both
files are re-read per scheduled invocation).

- **CORRECTION to the 2026-07-20 Variant B entry.** That entry states both
  scores "live in sqlite alone". FACT (traced at HEAD): **`composite_score` is
  persisted in NO table at all** — computed in-memory by `score.get_top_n` and
  discarded. It is not a sqlite-to-CSV move; this is the FIRST time that pillar
  has been written down anywhere. Consequence: every historical `final_score`
  in the archive is permanently unattributable to its TA component. The gap is
  closed forward-only.
- FACT: `top20_*.csv` deliberately NOT modified — (i) dormant (newest
  2026-07-01, writer `main.py` appears in no launchd plist, not a daily
  artifact); (ii) `vision_score` genuinely out of scope there — `get_top_n(20)`
  runs BEFORE the vision step; (iii) it already carries `composite_score` at
  col 5, so appending would have yielded a duplicate header that `pd.read_csv`
  mangles to `composite_score.1`. The scope premise in the change request was
  wrong on all three counts; reporting back beat plumbing.
- FACT: **no tests exist for the report writer** — no `test_*.py` anywhere in
  the production repo, nothing in `patches/` referencing `save_reports`. The
  dry-run harness lives at `scratchpad/dryrun_report_csv.py`, uninstalled.
  OPEN (operator): whether to keep it as the first regression guard for that
  writer. Note the asymmetry — THIS repo enforces 233 tests; the production
  system that trades real capital has none.
- Also fixed: the `run_phase2.py` "Interim re-rank: TA 80% + Vision 20%"
  display-only block (separate commit).

**What this unlocks (outcome-blind, no trial, no spec):** once these columns
accumulate, the rank-perturbation diagnostic — how often the top-5 SET changes
under a weight delta — becomes runnable under CONTAMINATION_POLICY.md's free
list. That is the cheap answer to the Variant B question, and it now has a
clock running rather than being unanswerable.

## 2026-07-20 — VARIANT C scope (outcome-blind): vision-LLM on all 250 to select the top 20

Third operator-proposed variant, scoped OUTCOME-BLIND. **No trial spent, no
backtest, no return computed, no LLM call made.** All code claims are from clone
pin ee7ad13 — **RULING 9 applies; verify at production HEAD before acting.**

**Verdict: (d) NOT MEANINGFUL AS PHRASED.** Three independently sufficient
reasons.

1. **"Confidence in the 20" names nothing measurable.** FACT: `conviction` is an
   LLM free-text output field (`synthesis.py:72`), not a computed quantity, and
   is produced ONLY by `run_synthesis(top20, ...)` (`run_phase2.py:886`) — i.e.
   on the top-20, AFTER selection. Names 21-250 have none, and running vision on
   250 would not create one (vision and synthesis are separate steps, separate
   models, separate outputs). FACT: the quantity that selects the 20 is
   `composite_score` (`score.py:169-181`), a weighted sum of five PERCENTILE
   RANKS — an ordering statistic with no confidence semantics: the #1 name
   scores ~1.0 whether the day's opportunity set is excellent or uniformly
   terrible. Restated as an outcome claim it becomes a TRIAL; restated as
   set-overlap it becomes FREE (see below).
2. **Structurally there is almost nothing new to add.** FACT: decomposing
   `compute_vision_score` (`vision.py:141-176`) — `stage` 5-65 pts,
   `trend`+strength 0-12, `breakout`x`volume_confirmation` 0-15, `ma_structure`
   5, `pattern_confidence` 3. Every term except `pattern_confidence` is
   derivable from the seven metrics `vision.py:79-85` hands the model, and all
   seven already sit inside `composite_score`. Worse, the prompt HARDCODES two
   of them: rule 1 (`:43-46`) forces the stage classification from SMA50/ROC-21
   arithmetic; rule 3 (`:51-54`) makes `volume_confirmation` a literal 1.2x
   threshold on a supplied number. **97 of 100 points carry no information not
   already in the screen being replaced.** `key_support`/`key_resistance` are
   genuinely pixel-derived but contribute ZERO to `vision_score` (never read by
   `compute_vision_score`) — they are a data-quality flag via
   `check_sr_vs_features`. At 20->5 vision sits alongside fundamentals,
   catalyst, quality, reversal_rs; at 250->20 there is nothing else in the mix.
3. **Untestable on dev data.** All four Variant B disqualifiers hold; #2
   (renderer leak) and #4 (step-function non-determinism) get WORSE at 250 —
   #4 especially: today a 25-point stage jitter perturbs a 0.10 weight inside a
   six-factor blend; under the proposal it would perturb WHICH NAMES REACH THE
   20, promoting jitter from a nudge to a gate. NEW disqualifier #5: `charts/`
   holds 306 files, ALL dated >= 2026-06-18 — every chart in existence is inside
   the Tier 1 window. A dev-window study needs ~575k as-of renders from a
   renderer with no as-of mode (vs ~46k for Variant B). Blocked ~12.5x harder.

**Cost if run forward anyway (FACT on volume, ASSUMPTION on the 12s/call
constant):** 24 -> 254 API calls/evening (the 4-stock sample pass is NOT
deduplicated — `syms[:4]` are analysed twice); ~20 -> 250 chart renders (charts
are rendered lazily INSIDE vision, `vision.py:284-289`; `main.py step5_charts`
is never called on the scheduled path); vision step ~5min -> ~51min (range
34-76); evening run ends ~17:38-18:20, ~3h inside the 21:30 window — **latency
is NOT the blocker**; ~10x LLM spend (rupee figure UNKNOWN, pricing not
verified). The loop is strictly serial (`vision.py:406-419`), `delay_sec=1.5`,
with zero hits for retry/backoff/concurrency.

**LIVE DEFECT FOUND (independent of this variant, actionable now).**
`vision.py:361-363` catches `anthropic.APIError` and returns
`_chart_unavailable_result(symbol)` -> **`vision_score = 50.0`** — a neutral
score stored as if it were a real reading, with no raised exception, no counter,
and no print on that path (the `[CHART_UNAVAILABLE]` print at `:297` is only on
the no-chart path). ASSUMPTION (SDK-version dependent, one line to check):
`RateLimitError` subclasses `APIStatusError` subclasses `APIError` — if so, a
429 today is silently swallowed into a neutral 50. `synthesis.py:397-407`
ALREADY does this correctly (RateLimitError -> 30s wait -> one retry); vision
simply lacks it. This is TRAP 6 in its exact historical shape and is live at 24
calls/evening TODAY. **Fix regardless of whether the 250 idea proceeds.**

**Also flagged:** doc/code mismatch at `final_score.py:549-557` — the comment
justifying the 68 tier-1 bar cites "fund>=68 picks: +0.117R vs +0.064R"
(2026-06-28 backtest) while the code reads `conviction_raw`/`conviction`. Not
material to this scope; worth an operator glance.

**The FREE question, which may end the matter without any of the above:**
set-overlap / churn — how much does the top-20 SET actually change when vision
is added as a 250-stage input (Jaccard overlap + rank displacement)? Outcome-
blind, explicitly free under CONTAMINATION_POLICY.md, no trial, no spec. If
overlap is ~95%, the hypothesis is answered at zero cost. **Prerequisite:**
persist per-symbol `composite_score` + the five sub-scores (`score_trend`,
`score_momentum`, `score_rs`, `score_volume`, `score_breakout`) for ALL ~250
names into the sealed snapshot — extending the top-5 persistence completed
2026-07-20 to the full universe.

**Forward route (c), if ever wanted:** disqualifiers 1 and 2 dissolve
forward (a same-day chart has no outcome to memorise and needs no as-of mode);
**3 and 4 survive** — pin a DATED model snapshot before capture begins, and
pre-commit the jitter mitigation. **The hard constraint: the counterfactual arm
does not exist and cannot be backfilled** — comparing the two rankings needs
BOTH on the same evening, and a chart rendered later is a different chart. That
is a capture-design decision that must be made BEFORE capture starts. Any
vision-informed arm must stay SHADOW-ONLY for the whole window; the moment it
touches live selection there is no counterfactual left to measure. Realised-
outcome comparison IS a trial and needs a hash-frozen spec + register row in the
same commit, pre-registering metric, arms, horizon, SPA gate (RULING 7), and the
model-snapshot pin.

## 2026-07-20 — VERIFIED AT PRODUCTION HEAD: vision fabricates readings on API failure

Operator-run read-only verification of the VARIANT C finding. **CONFIRMED, and
broader than scoped.** RULING 9 discharged for this claim.

- FACT (`vision.py:361-363`): `except anthropic.APIError as e: print(f"API-ERR:
  {e}"); return _chart_unavailable_result(symbol)` -> `vision_score = 50.0`.
- FACT (`anthropic` 0.111.0, MRO printed): `RateLimitError` -> `APIStatusError`
  -> `APIError`. So the handler catches **far more than 429**:
  `APIConnectionError`, `APITimeoutError`, `InternalServerError` (500),
  `OverloadedError` (529), `AuthenticationError`, `BadRequestError`, and
  out-of-credit. **Every one becomes a fabricated neutral 50.**
- FACT: **it fired 105 times.** `grep -rc "API-ERR" logs/` = 105, all
  `Error code: 400 — "Your credit balance is too low to access the Anthropic
  API"`, on **2026-07-06 ~16:48 IST** — two consecutive batches (4 stocks then
  17), 100% failure, every stock fabricating a 50. Not a 429 in this instance,
  but it routes through the identical handler: mechanism confirmed end to end.
- FACT — **no live recommendation was scored on a swallowed error.** The
  picks_log join returns zero rows across all affected dates. Nearest miss:
  DIXON carried a stub 50 on 07-15 and was picked rank 3 on 07-16, but its
  07-16 row is a genuine 100.0. **NOTE: 2026-07-06 is day 8 of the live window
  (started 2026-06-29), i.e. Tier 1 A/B data. The A/B is intact — but only just,
  and only by luck of which names were affected.**
- Two CORRECTIONS to the clone-derived scope: (i) there IS a print
  (`API-ERR: {e}` at `:362`) — stdout is not literally silent; (ii)
  `[CHART_UNAVAILABLE]` is NOT no-chart-only — the instance at `vision.py:417`
  keys off `if r.get("stage")` and the stub sets `stage=None`, so it fires on
  both paths. Nothing PERSISTS or AGGREGATES either signal, which is the actual
  defect.

**Three aggravations beyond the original claim:**
1. **The DB erases the evidence.** A unique index on `(symbol, date)` plus
   `INSERT OR REPLACE` means a later successful run overwrites the stub. Only
   **7** stub-50s survive DB-wide against 105 known occurrences. **The residue
   is not the incidence** — any audit from the DB systematically under-counts.
2. **The two stub paths are byte-identical in storage.** No-chart and API-error
   return the same dict, so even those 7 survivors cannot be attributed to a
   cause. The question is unanswerable as built.
3. **Both `system_check` canaries FILTER stubs out rather than counting them**
   (`:96-98` reports "chart-unavailable stubs only" as info; `:129` filters
   `stage IS NOT NULL`). **The health check actively looks away** — it is
   designed to suppress the signal it exists to catch, and therefore reports
   green through a 100%-failure batch.

**The bug in one sentence: `synthesis.py:400-426` returns ABSENCE (typed
`RateLimitError` -> log -> sleep(30) -> one retry -> `None` on failure); vision
returns a FABRICATED READING.** Absence is recoverable; a fabricated 50 is
indistinguishable from data.

**Authorized fix (operator-confirmed):** mirror synthesis's typed-exception
retry exactly; add a per-run failure counter split by cause; AND make the two
stub paths distinguishable in storage — without the last, the counter dies at
end-of-run and the DB stays unattributable, reproducing aggravation 1.
Successful readings must be byte-identical to today.

**New general lesson (candidate TRAP 8): THE RESIDUE IS NOT THE INCIDENCE.**
Where a store overwrites in place (`INSERT OR REPLACE`, last-write-wins,
idempotent upserts), the surviving rows are a biased sample of what happened —
biased precisely AGAINST transient failures, because those are the ones a later
successful run replaces. Count events at the time they occur; never infer
incidence from a mutable store's residue. Compounding: a health check that
FILTERS anomalies to reduce noise converts this from under-counting into
reporting green.

## 2026-07-20 — VARIANT D scope (outcome-blind): options-implied signals for breakout detection

Fourth operator hypothesis scoped OUTCOME-BLIND, and the first that is a NEW
signal family rather than a legacy variant. **No trial spent, no backtest, no
return computed, no exchange endpoint touched, no data fetched.**

**Verdict: (d) NOT WORTH PURSUING as a standalone family. Disclosed dead end
(TRAP 4).** Note the reasons are INDEPENDENT OF DATA ACCESS — obtaining the data
would not rescue it, which is why this is (d) and not (c).

1. **The premise as phrased is a tautology.** `dC = D*dS + (1/2)G*(dS)^2 +
   vega*dIV + theta*dt`. Correlation of option price with spot IS delta — a
   deterministic function of spot, strike, time and sigma. A deep-ITM call
   correlates ~+1 by construction. The matrix would encode MONEYNESS and nothing
   else, and would drift across the expiry cycle from vega/theta — a spurious
   time-varying artifact of contract mechanics. **Same failure mode as VARIANT
   B** (a component fed the very inputs it was meant to independently confirm).
2. **The genuinely independent quantities are options-market FLOW / price-of-
   risk measures, not price-correlation measures** — IV change, IV spread, skew,
   term structure, OI/dOI, PCR, options-volume/stock-volume (O/S). The
   correlation framing captures precisely the DERIVABLE half.
3. **The best modern evidence says the headline predictors are an artifact.**
   Muravyev, Pearson & Pollet (2025, JFE 172): IV spread and skew predict
   returns because they PROXY FOR THE STOCK BORROW FEE, omitted from the IV
   calculation; predictability falls >=2/3 when high-borrow-fee stocks are
   excluded. Muravyev, Pearson & Broussard (2013, JFE 107:259-283) tested
   "options lead spot" directly on tick data: on put-call-parity disagreements
   **the OPTION quotes adjusted, not the stock quotes**; options' information
   share ~6.25%. Cremers & Weinbaum (2010, JFQA 45) reports decay WITHIN its own
   sample. Xing/Zhang/Zhao (2010, JFQA 45) smirk: weekly-to-monthly.
4. **The mechanism does not transplant to India.** Both surviving explanations
   (Johnson & So 2012 JFE 106; MPP 2025) are SHORT-SALE-COST stories. India bans
   naked short selling in the cash market; SLB is thin. ASSUMPTION: suppressing
   the borrow-fee channel attenuates the artifact — **which removes the artifact
   and the alpha together.** Nothing here creates an Indian edge.
5. **FRICTION kills it independently and unfixably.** All documented effects are
   WEEKLY (Cremers-Weinbaum 50bp/wk; Johnson-So 0.34%/wk = 19.3%/yr LONG-SHORT
   gross, long-only half ~10%). Drag at H=5 = **11.99%/yr** statutory,
   **17.03%/yr** at the 0.05%/side floor. Same shape as the legacy kill.
   **Unfixable by construction: the signal's informativeness IS its decay rate**
   — you cannot make this family low-turnover without destroying the signal.
   Directly contradicts the roadmap's "new families must be low-turnover by
   design."
6. **Universe mismatch.** F&O eligibility (SEBI/HO/MRD/MRD-PoD-2/P/CIR/2024/116,
   2024-08-30) = top-500 mcap + liquidity floors; current count **~185-208**
   names (sources disagree — a RANGE, not a point). Habitat is mcap ranks
   **201-1000**. Thin intersection, and F&O membership is time-varying +
   survivorship-biased — a PIT F&O panel would be a fresh A1-scale build.
7. **No usable Indian evidence.** Searched four query formulations; found no
   peer-reviewed cross-sectional single-stock NSE study with net-of-cost
   results. What exists is index-level, short-sample or descriptive. A Springer
   (2024) chapter reports the call-put ratio effect **does NOT hold** for Indian
   index options. Evidence vacuum, not a search failure.

**Data (FACT, no fetch performed):** NSE F&O bhavcopy carries settlement price,
OI and volume but **NOT implied volatility** — IV must be computed, so you own
the discount-rate, dividend and (per MPP 2025) **borrow-fee assumptions that are
the whole ballgame**, and the Indian borrow fee is effectively unobservable
historically. **You would be computing the contaminated version with no way to
decontaminate it.** Depth is ample (archive from 200301; F&O-UDiFF format change
2024-07-08, nine days before the seal cutoff) — depth is NOT the constraint, the
universe is. **Gated by OPEN OPERATOR DECISION 1** (NSE ToU prohibits automated
collection).

**Queue position: FIFTH.** Would have to displace SPEC-SRA-01, the weakest thing
queued — and it is weaker: same friction null PLUS universe mismatch PLUS a data
blocker PLUS two top-journal papers against the mechanism. It displaces nothing.
As a CONDITIONING LAYER the only coherent story is a negative/veto screen (adds
zero turnover to a host book), but it can speak about ~185-208 names only and
the IV-term-structure variant is largely an earnings-date marker — i.e.
re-litigating SPEC-PEAD-01's territory with worse data.

**NO cheap diagnostic is proposed, deliberately.** The obvious free one —
correlate option prices with spot — IS the tautology in (1) and would return a
spuriously impressive number. There is no cheap test that separates signal from
delta without first building the full per-strike IV surface, which is the
expensive part and is ToU-blocked.

**The ONE bounded action:** fold NSE per-strike options history into the Accord
Fintech (ACE Datafeed) enquiry that OPEN OPERATOR DECISION 1 already
contemplates — **third independent surfacing** of that vendor in this program;
it self-describes as an authorised NSE/BSE/MCX/NCDEX vendor selling historical
derivatives data. NSE also has a named paid historical-EOD product (unlike the
BSE case, where the Rs.9L/yr feed was verified real-time-only). One extra line in
an email already likely to be sent. **This does NOT resurrect the hypothesis** —
reasons 1-6 are independent of data access — but a licensed NSE history route is
a durable capability asset regardless.

**Stated gaps (TRAP 6 discipline, NOT silently omitted):** NSE paid-EOD SKU list
/ depth / price — page fetch TIMED OUT, UNKNOWN. Whether Accord or NSE sells
per-strike option-chain history vs futures/index only — UNKNOWN. F&O constituent
count is a range (182/185/~208). **MPP 2025 full text returned HTTP 403; the
"two-thirds" decay figure is SINGLE-SOURCED from a RePEc listing plus a
University of Illinois Gies press summary and MUST be re-verified from the paper
before being cited in any spec.**

## 2026-07-21 — RULING 10: Tier 1 OHLC ingest quality gate (null closes + coverage)

Two defects found in `data/market/` while monitoring live positions RADICO and
DIXON. Both are in THIS repo's nightly ingest (`com.alpha.ingest` ->
`scripts/ingest_snapshot.sh` -> `src/fetch_ohlc.py`), not production.

**Defect 1 — every newest close was NaN.** FACT: `ohlc_2026-07-21.parquet` held
544 rows across the correct 34 symbols over the correct date range, with **34 of
34 symbols carrying a NaN close on the newest bar** (open/high/low all present).
`ohlc_2026-07-20.parquet` had the same 2026-07-20 close populated correctly, so
the data existed publicly — the 01:00 run captured it defectively (ASSUMPTION:
yfinance's most recent daily bar is provisional at 01:00 IST). `dropna(how="all")`
only drops rows where EVERY field is null, so these survived; the summary print
reported row count, symbol count and date range — never null CONTENT. **The
settlement path reads exactly this file** (`scripts/run_paper_leg.py:43`,
"newest data/market fetch first"), as does NAV.

**Defect 2 — the fetch universe was frozen.** FACT: `ledger_symbols()` read recs
only from `data/legacy_snapshot/recs/`, whose newest file is dated **2026-07-10**.
The nightly ingest deposits new recs under `data/sealed/raw/<date>/`, which was
never read. Any symbol first recommended after the snapshot date was therefore
never fetched: **DIXON — picked 2026-07-16 and held live for three sessions —
had no OHLC in the store at all.** Both monitoring agents had to bypass the
store and fetch from yfinance to answer basic questions about live positions.

**RULING (binding):**
- A row whose `close` is null is **DROPPED, never written**. ASSUMPTION, and the
  reasoning: a missing row is honest and `paper_leg`/`build_nav` already REFUSE
  to approximate over gaps (by design); a NaN close masquerading as a fetched
  observation poisons them silently. Absence is recoverable; fabricated data is
  not — the same principle as the vision `synthesis`-vs-`vision` distinction
  recorded 2026-07-20.
- Every fetch **reports quality and coverage explicitly** — rows in/out, rows
  dropped, symbols present/expected, symbols missing by name, newest date — and
  warns to stderr on any drop or any missing symbol. A fetch where nothing
  survives validation **exits 2**, so launchd records a failure rather than
  writing an empty file over a good one.
- The fetch universe reads recs from **both** `data/legacy_snapshot/recs/` and
  `data/sealed/raw/`, so the live rec stream extends it automatically.

**Implemented + tested:** `src/fetch_ohlc.py` (`validate_ohlc`,
`_rec_symbols_from`, extended `ledger_symbols`), `tests/test_fetch_ohlc_quality.py`
(8 tests, incl. a live-store guard asserting the newest ingest has zero null
closes, and a source-path pin that fails if `data/sealed/raw/` is dropped from
the search). Suite 233 -> 241.

**Data repaired:** the defective `ohlc_2026-07-21.parquet` was backed up out of
tree and re-fetched under the new gate — **731 rows, 43/43 symbols, 0 null
closes, newest 2026-07-21** (previously 544 rows, 34 symbols, 34 null closes,
newest 2026-07-20). DIXON now present (2026-07-21 close 14,118.00, matching an
independent yfinance fetch exactly). `data/market/` is derived, re-fetchable and
explicitly idempotent-per-day, so a defective daily parquet is repairable by
re-fetch — this is NOT the append-only `data/sealed/raw/` corpus and no evidence
was overwritten.

**This is the fourth instance of the program's characteristic failure in one
day** (TRAP 6): a correctly-named, correctly-sized, correctly-dated artifact
that is silently empty of the one field that matters, passing a health check
that only ever looked at the container. `overlay_queue.ingest_health()` reports
green for exactly this file — it verifies a non-empty dated directory exists,
not that the closes inside it are non-null. **Guarding the container is not
guarding the content.**

## 2026-07-22 — RULINGS 11 and 12 adopted, with a PROVENANCE NOTE

**These two rulings were drafted and adopted by the AI assistant, not authored
by the operator.** The operator's instruction was "Take decisions as you think
is right" (2026-07-22), following "Go" on an outcome-blind Tier 2 analysis pass.
That is a genuine delegation and these rulings are in force — but the
distinction is recorded because this file is a due-diligence artifact, and a
reader at registration is entitled to know which rulings carry a human author
and which do not.

Both are **conservative in direction** (they stop work; neither authorises
spending, data acquisition, a trial, a slot, or a sealed test), both rest on
outcome-blind analysis with the arithmetic shown, and both are reversible by a
superseding ruling. Full working and full ruling text:
`analysis/SRA_friction_hurdle.md`, `analysis/AG01_circularity.md`,
`analysis/proposed_rulings_2026-07-22.md`.

**If the operator disagrees with either, supersede it — do not edit it.**

- **RULING 11 — SPEC-SRA-01 KILLED as a ₹100 Cr fund candidate.** Not to be
  hash-frozen; `src/expr.py` NOT to be extended for it; `signal_sra.py` /
  `run_trial_sra.py` not to be built; Stage S0 not to be run. Two independent
  kills: capacity (₹5 Cr position vs the spec's own ₹2 Cr/day ADV floor = 250%
  of a day's volume, 25 sessions to enter a 5-session hold) and net expectancy
  (needs 1.15×–6.06× the legacy system's entire gross alpha depending on
  slippage). NO TRIAL SPENT, no slot held or released. **Kill scope is narrow:**
  the capacity kill vanishes at ₹1–5 Cr, so a small-capital variant remains open
  via a NEW versioned spec — never an edit to SPEC-SRA-01.
- **RULING 12 — SPEC-AG-01 demoted below SPEC-52WH-01; MCX depth spike
  RE-SCOPED, not cancelled.** Decisive reason is statistical power, not the
  circularity: the one design that escapes the circularity yields ~48–114
  independent roll episodes over the whole dev window, which will not clear a
  SPA gate charged against 52+ trials. Spike resequenced to lead with MCXCCL's
  published DSP methodology (documentary, no endpoint touched, settles the
  circularity to FACT either way). Two new blockers recorded: AG-01 has no cost
  stack (RULING 5 is NSE cash-equity only), and AMENDMENT C bites hardest on the
  seasonality fallback. NO TRIAL SPENT.

## 2026-07-22 — RULING 13: microstructure diagnostic door (opening-bar volume share)

Operator-authorized 2026-07-22. Full draft and reasoning:
`analysis/proposed_ruling_13_2026-07-22.md`. **Unlike RULINGS 11 and 12, this
ruling authorizes outcome contact and SPENDS A TRIAL.**

- **FACT — the defect under test.** `preopen_check.py:420` and `:462` (frozen
  clone) compute `v_rat = round((vol * 75) / avg_vol, 2)`, where `vol` is the
  single 9:15–9:20 bar and `avg_vol` is `get_avg_volume_20d` — a 20-session
  mean of DAILY volume. `synthesis.py:51-57` gates on `1.0x` / `1.2x`. The `75`
  is the bar count of a 375-minute session (verified: yfinance returns exactly
  75 bars/session). The extrapolation is valid ONLY if intraday volume is
  uniform across the session, which it is not. Writing `s` for the opening
  bar's true share of daily volume, `volume_ratio = s × 75 × (today_vol /
  avg20_vol)`, so the `≥1.2` gate actually tests `today_relative_volume ≥
  1.2 / (75 × s)`. At `s = 1/75` that is the intended "1.2× normal volume"; at
  any larger `s` the gate loosens proportionally and may be near-vacuous.
  **`s` has never been measured in this program.**

- **FACT — neither existing door admits the measurement, and the outcome
  conditioning is NOT the reason.** `load()` strips every row ≥ 2024-07-17.
  `load_operational()` rejects three separate ways: a 250-name intraday panel
  is not rec_key-joinable and trips the explicit "generic OHLC panel"
  rejection (`data_gate.py:128-137`); ~half the reachable window
  (2026-05-23 → 06-28) is in the seal gap (`:148-153`); and `data/workspace/`
  is not an admissible source. Dropping the up-day filter would change none of
  the three. A ruling is required to measure `s` in ANY form.

- **FACT — the horizon is 60 days and is permanent.** Probed 2026-07-22:
  yfinance serves 5-minute bars for the last 60 calendar days only ("The
  requested range must be within the last 60 days"; Jan/Mar/Apr 2026 returned
  0 rows). Reachable window ≈ 2026-05-23 → 2026-07-22, ~40 sessions. Deeper
  intraday exists only via Kite Connect, which **BINDING RULE 3 forbids**;
  this ruling does not disturb that. The operator's "last 6 months" is not
  obtainable by any sanctioned route.

- **RULING 13a — narrow diagnostic door.** Post-cutoff 5-minute OHLCV for the
  250-name system universe may be fetched from yfinance and analysed **for
  volume-share statistics only**. Door opens for this measurement and closes
  on completion. `load()` / `load_operational()` are NOT amended; the carve-out
  lives in the calling script.

- **RULING 13b — no return is ever a measured quantity.** Dependent variable is
  `s = first_5min_volume / full_day_volume`, a pure volume share. Price enters
  ONLY as a sample filter (15:30 price > 09:20 price, where the 09:20 price is
  the close of the 9:15–9:20 bar). No return is averaged, regressed, attributed
  or reported. Any extension beyond a volume share requires a NEW ruling.

- **RULING 13c — the conditioning is disclosed, not reclassified.** Selecting
  on up-sessions IS outcome-conditional under `CONTAMINATION_POLICY.md`. It is
  authorized because the operator specified it, and booked as a spent trial
  rather than argued into the free-diagnostic bucket.

- **RULING 13d — MEASUREMENT ONLY; no live change before 2026-09-27.** This
  authorizes measuring `s`. It does NOT authorize altering the `75`, the `1.2`,
  or any other live recommendation parameter. The recommended leg is the
  instrument under measurement in `AB_PREREG.md` through the 2026-09-27 read
  date; re-tuning it mid-window would change the instrument mid-experiment and
  corrupt analyses 1–4. Acting on the result is a SEPARATE decision, on or
  after the read date.

- **RULING 13e — mandatory coverage assertions (TRAP 1 / TRAP 6).** The run
  must report and the write-up must disclose: symbols fetched of 250; sessions
  retained; bars/session (expect 75) with sub-quorum sessions dropped and
  counted; placeholder rows (flat OHLC + zero volume) dropped and counted;
  sessions failing the 09:15 bar-date check. The 09:15 bar is located by IST
  clock time, never by position — mirroring the clone's own "NOT guessing
  iloc[0]" discipline. A zero exit code and a non-empty row count are not
  evidence.

- **RULING 13f — reporting.** Report the operator-specified volume-weighted
  mean (equivalently the pooled `Σfirst5 / Σfull_day`) AND the unweighted mean,
  median, decile spread, an all-sessions control, and a liquidity-quintile
  breakdown. Index membership is not carried in the EOD snapshot, so 2026-06-24
  turnover quintiles stand in for index tier (ASSUMPTION, disclosed).

- **Caveats carried into any write-up.** (a) Universe membership is the
  2026-06-24 snapshot applied to the whole window, so May sessions use
  marginally forward-looking membership — immaterial for a volume share.
  (b) Window contains no reconstitution (March done, September pending) but
  does contain expiry days, which concentrate volume. (c) ~40 sessions is
  short and `s` may vary with regime: this is an estimate, not a constant.

- **TRIAL ACCOUNTING — ONE TRIAL SPENT.** Register row
  `DIAG-VOLSHARE-0001`; cumulative count 51 inherited + C1-52WH-0001 + this
  = **53**. Charged against the **legacy** daily mid-cap momentum family,
  already KILLED as a fund candidate — that family has no remaining sealed
  test, so the contamination has no target. **NO shadow slot consumed** (QFM
  and PEAD keep both; AG-01 and 52WH unaffected). **`FINAL_TEST` NOT set and
  must not be** — no Tier 2 holdout is opened. Per the CLAUDE.md trial-economics
  corollary a marginal trial moves the deflation bar ~0.3%; the scarce
  resources are the 2 shadow slots and the single sealed test per family,
  neither of which is touched.

- **Runner.** `scripts/diag_open_volume_share.py`, which hard-fails unless
  "RULING 13" appears in this file (TRAP 7: a check that fails loudly beats an
  instruction that can be silently skipped).

## 2026-07-22 — VERIFIED AT PRODUCTION HEAD: both volume projections are live and miscalibrated

RULING 9 check performed for the DIAG-VOLSHARE-0001 finding. **FACT — HEADS
DIFFER:** production HEAD = `5c099d77044579a48e254c04b475a01c33b5f142`; pinned
clone (`~/vendor/legacy-engine`, `LEGACY_PIN.md`) =
`ee7ad13228244f4f27e3d2d839baf70897ff24fe`. Verified by `git clone
--no-hardlinks` of production into the session scratchpad (BINDING RULE 1
permits cloning); production HEAD re-read after the clone and UNCHANGED.
`preopen_check.py` DIFFERS between the two. Scratchpad clone deleted after use.

- **FACT — the `× 75` projection is unchanged at production HEAD**
  (`preopen_check.py:433` and `:475`), as is the `candle_time="09:15"` default
  (`:450`) and the clock-time bar lookup (`:423`). The DIAG-VOLSHARE-0001
  measurement therefore applies to the LIVE system, not merely to the frozen
  clone.

- **FACT — the entry-path thresholds are NOT the 1.0/1.2 in `synthesis.py`.**
  Production HEAD refactored them into named constants (gap #91):
  `VOL_GATE_CONDITIONAL = 1.0`, `VOL_GATE_BREAKOUT = 1.5`, `VOL_GATE_WAIT = 2.0`
  (`preopen_check.py:46-57`), enforced at `:623`, `:666`, `:696`, `:811` and
  printed by `report.py`. `synthesis.py`'s 1.0/1.2 is the LLM synthesis
  discipline rule — a DIFFERENT layer. Any write-up must not conflate them.

- **FACT — a SECOND projection with the identical defect.** The 9:45 path
  projects the 30-minute bar by `× 12.5` (`preopen_check.py:523`, `:568`;
  `observer.py:608`). Measured on the same 250-name / 6,686 up-session panel:
  first-30-minute share = **13.20% median / 17.64% volume-weighted**, versus
  the **8.00%** that `× 12.5` assumes — an overstatement of **1.65×–2.21×**.
  Correct multiplier ≈ 5.7–7.6, not 12.5. `observer.py:493` already recorded
  "Nothing has ever checked the projection"; this checks it.

- **FACT — net effect on the live gates** (using s = 4.14% median / 5.82%
  vol-weighted at 9:20, and s30 = 13.20% / 17.64% at 9:45). Figures are the
  relative volume a name must ACTUALLY run at to pass:

  | gate | nominal | 9:20 (×75) | 9:45 (×12.5) |
  |---|---|---|---|
  | CONDITIONAL | 1.0× | 0.23–0.32× | 0.45–0.61× |
  | BREAKOUT | 1.5× | 0.34–0.48× | 0.68–0.91× |
  | WAIT (gap-up) | 2.0× | 0.46–0.65× | 0.91–1.21× |

  Every 9:20 gate, including the strictest, passes names running at HALF
  normal volume or less. The 9:45 gates are materially closer to their
  nominal intent.

- **FACT — no zero-volume guard exists at production HEAD.** Grep for a
  `vol == 0` / falsy-volume check in `preopen_check.py` returns nothing. So the
  yfinance-fallback failure mode stands: yfinance reports ZERO volume for the
  09:15–09:20 bar in 97.65% of sessions (measured, 14,197 sessions), giving
  `volume_ratio = 0.0`, which fails every gate — an all-veto whenever the Kite
  path is unavailable. **ASSUMPTION (unverified):** that the Kite path is
  normally available, so this is latent rather than continuously active.
  Verifying it needs the ledger's recorded `volume_ratio` values, which is a
  separate read.

- **SCOPE.** This entry records FACTS only. RULING 13d stands: no live
  parameter may change before the 2026-09-27 AB_PREREG read date.

## 2026-07-23 — INCIDENT: inadvertent read of quarantined SWEEP_HOLDING.md

- FACT: during a subagent's outcome-blind feasibility memo on post-breakout
  entry (`analysis/breakout_entry_feasibility.md`), the agent ran
  `head -60 ~/vendor/legacy-engine/SWEEP_HOLDING.md` while characterizing the
  legacy entry rule for §1. That file's "DECISION TABLE" carries the legacy
  system's **net-of-cost results by holding period** — the same artifact this
  file's 2026-07-20 VARIANT-A entry (the `SWEEP_HOLDING.md` FACT bullet, above)
  records as "deliberately NOT read (outcome contact, unauthorized)." The read
  crossed an explicitly-drawn quarantine line. It is disclosed here, not
  retracted.

- FACT — severity is bounded. The quarantined data belongs to the LEGACY
  family, which was KILLED as a fund candidate and retains no sealed test
  (RULING 13's own reasoning; `SEAL.md` §2). No sealed test was burned and no
  shadow slot was touched by the read.

- FACT — the numbers were not propagated. The memo does not cite, quote, or
  reason from the net-by-holding-period figures. Its entire §5 friction hurdle
  is derived from `src/costs_in.py` constants (RULING 5) alone; the crossing is
  flagged in the memo's own header (`analysis/breakout_entry_feasibility.md`
  lines 113–121). Independent verification: grep of the memo shows no
  SWEEP_HOLDING outcome value.

- ASSUMPTION (cannot be certified) — the residual hazard is forward and
  prose-level, not citational. The quarantine exists so that a future
  holding-period choice (`HOLD_SESS`) cannot be made after seeing which H paid
  off. The agent's read exposed exactly that table, and the memo's §5.5 reasons
  about holding period. The memo's *hurdle* is outcome-blind cost arithmetic and
  its verdict (C — DO NOT BUILD) is independently carried by Raju 2023
  (long near-high leg t = −0.91), the gross-alpha ≈ gross-cost identity, and the
  short-horizon reversal literature — none of which require SWEEP_HOLDING. But
  it cannot be certified that the memo's prose was wholly un-anchored by the
  glimpsed numbers. Recorded as a known, un-eliminable doubt rather than a
  false all-clear.

- SCOPE. This entry records an incident as FACT; it changes no ruling and
  authorizes nothing. `HOLD_SESS`/the 10-slot interaction remains genuinely
  unswept and quarantined (VARIANT-A entry stands). No future holding-period
  decision may cite this memo's §5.5 as its basis. RULING 13d is untouched.

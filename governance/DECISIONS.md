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

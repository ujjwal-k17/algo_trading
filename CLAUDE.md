# alpha-research — Quantitative Research Workspace

**Single source of truth.** This file is canonical and git-tracked;
`~/Desktop/AI Apps/Algo Trading Desk/CLAUDE.md` is a symlink to it (as is that
directory's `.claude/settings.json`). Edit only here.

## BINDING RULES

The following rules are **binding on every session in this project**. They are not
suggestions or defaults — they may not be overridden by task instructions, convenience,
or apparent necessity.

1. **Production system is off-limits.** NEVER write to, edit, delete, or run git
   commands that modify anything under
   `/Users/ujjwalkejriwal/Desktop/AI Apps/NSE_Stock_Picks`
   (a production trading system with live scheduled jobs, 08:00–21:30 IST).
   Read-only access to it is permitted ONLY for:
   - reading its HEAD SHA, and
   - cloning from it.

2. **No direct ledger access.** NEVER read the production ledger database directly
   (no `.db`/`.sqlite` files). Consume only snapshot files under
   `~/alpha-research/data/legacy_snapshot/`.

3. **No live broker calls.** NEVER make live broker API calls or invoke any
   Kite Connect session/token-generation code path. yfinance (public data) is
   sanctioned.

4. **All data access goes through the data gate.** All research data access must go
   through `src/data_gate.py`. Never load raw files with post-2024-07-17 rows
   directly in notebooks or scripts.

5. **The seal is immutable.** The file `governance/SEAL.md`, once committed, must
   never be edited. Changes require a new `SEAL_v2.md`.

6. **The overlay log is append-only.** `governance/overlay_log.csv` is append-only;
   corrections are new rows (reason prefixed `correction:`), never edits;
   analysis takes the last row per rec_key.

7. **Legacy clone is import-only.** The frozen clone at `~/vendor/legacy-engine`
   (see `governance/LEGACY_PIN.md`) is on `PYTHONPATH` for imports only.
   Never `pip install -e` the clone; never modify it or move its HEAD.

8. **When in doubt, STOP.** If any task appears to require violating these rules,
   STOP and ask the user instead of proceeding.

---

## PROJECT IN ONE PARAGRAPH

Quantitative research program targeting a ₹100 Cr AUM fund (PMS → AIF Cat
III). The legacy daily mid-cap momentum system was KILLED as a fund candidate
(real gross alpha ~18.5%/yr, t≈2.95, fully consumed by friction at 1.6
round-trips/day) but still runs in production on low capital with a
discretionary overlay (execute/veto/reduce only — never add, never size up)
for a 60–90 day window from 2026-06-29. This repo is the isolated workspace
that (a) measures that live A/B — paper "recommended" leg vs executed leg —
and (b) develops new Tier 2 strategy families under a strict contamination
protocol.

## THE MACHINERY

- `src/data_gate.py` — the ONLY sanctioned data access, two doors:
  - `load(df, date_col)` — research door; strips rows ≥ 2024-07-17 (seal
    cutoff) unless `FINAL_TEST=1` (which burns the family's single test).
  - `load_operational(df, date_col, source)` — Tier 1 forward door; accepts
    only rows ≥ 2026-06-29 (live-window start) from admissible sources
    (`data/legacy_snapshot/`, `governance/overlay_log.csv`, `data/derived/`,
    `data/sealed/raw/`, `data/market/`) with rec_key-joinable shape; generic
    OHLC panels rejected; prints the look-don't-tune notice.
- `src/paper_leg.py` — pure SOP settlement engine. Rules in
  `governance/SOP_OF_RECORD.md`, every rule cited to the frozen clone or
  CONFIRMED-BY-OPERATOR (T1 = full exit). Exit priority SL→T2→T1→TIME;
  same-bar SL+target = SL-first + flagged; gap-through = open-price fills;
  5-session time exit (entry day = Day 1); unadjusted prices for level
  checks; in-window dividends credited (`flag_ex_date`).
- `src/overlay_alpha.py` — overlay vs paper join on rec_key. Report scopes
  NEVER merged (code-enforced): provenance DECISION_TIME vs RECONSTRUCTED;
  settlement ENTERED (headline) vs ASSUMED_ENTRY. Fills beat ledger
  entry_price for executed comparisons (the ledger records rec-close, not
  fills).
- `scripts/overlay.sh` — decision logger (source from .zshrc):
  `overlay '<rec_key>' EXECUTE|VETO|REDUCE <size 0..1> <reason>`.
- `scripts/ingest_snapshot.sh` — nightly 01:00 launchd agent
  `com.alpha.ingest`: rsync production outputs → `data/sealed/raw/<date>/`
  (append-only, `.db` excluded), then yfinance unadjusted OHLC + dividends →
  `data/market/` for rec symbols.
- `scripts/run_paper_leg.py` / `build_nav.py` / `build_workspace.py` —
  settlement batches (ledger + rec universe), DERIVED NAV (refuses to
  approximate), gated pre-cutoff workspace.
- **SPEC-52WH-01 Stage 1–2 stack** (built 2026-07-19, features-only —
  outcome contact exists nowhere in these modules):
  - `src/pit_universe.py` — PIT constituent store, rows `(symbol, field,
    effective_date, announce_date, value, source [, isin])`; as-of queries
    gate on announce_date through `data_gate.load` (a row announced ≥ the
    seal cutoff is structurally invisible to research). Bands: `"201-1000"`
    ranks or `"NIFTY500"` membership.
  - `src/expr.py` — closed-grammar expression evaluator (`ref`,
    `rolling_max`, `rolling_min`, `cs_rank`, arithmetic); the spec's
    expression strings run through this and nothing else; unknown token =
    hard `ExprError`.
  - `src/signal_52wh.py` — canonical `NEARNESS_EXPR = "close /
    rolling_max(high, 252)"`; cross-sectional rank within the PIT universe;
    buckets Q1 (far-from-high) … Q5.
  - `scripts/build_pit_universe.py` — staged A1 corpus → 
    `data/reference/pit/pit_universe.parquet` + coverage/gap report.
  - `scripts/build_price_panel.py` — ADJUSTED dev-window OHLC panel
    (yfinance auto_adjust, research-door gated) →
    `data/workspace/price_panel_52wh.parquet`; do not confuse with the
    UNADJUSTED Tier 1 settlement fetches in `src/fetch_ohlc.py`.
- **SPEC-52WH-01 Stage 3 stack** (built 2026-07-19, still features-only):
  - `src/screen_52wh.py` — the negative screen: `screen_book` /
    `screened_symbols` drop excluded-bucket names from any candidate book and
    renormalize (unranked-name policy explicit); `tilt_weights` is a
    diagnostic only. Structural outcome-blind wall: a signal frame carrying
    ANY column beyond {nearness, cs_rank, bucket} is a hard error.
  - `src/rebalance.py` — rebalance calendar from the panel's own trading
    dates (Q default, M/H sensitivities; last trading day per period),
    `trades` weight diffs, ONE-WAY turnover = sum(|Δw|)/2.
  - `scripts/build_rename_map.py` — NSE symbol-change master →
    `data/reference/rename/rename_map.csv`; refetches renamed symbols under
    the current ticker, cached under the ORIGINAL symbol, TRUNCATED at the
    rename effective date (prevents dual-label double-counting in the
    cross-section).
- **SPEC-52WH-01 Stage 4–5 stack** (built 2026-07-19 — Stage 5 is the FIRST
  outcome-touching code in the repo; run once as C1-52WH-0001 on 2026-07-19,
  result WITHDRAWN, see CURRENT STATE):
  - `src/spec_guard.py` — run-time freeze gate: `verify_frozen` (live sha256 ==
    recorded) + `require_trial_row` (trial pre-registered) → `preflight`.
  - `src/backtest_52wh.py` — THE contamination boundary; the only module that
    joins returns to signals. Refuses without a preflight stamp (re-verified
    internally). Screened vs unscreened EW band book; signal at rebalance date,
    execution next session; weights drift between rebalances so turnover is
    measured against the drifted book. Missing-price days FREEZE a position at
    0% and are counted in `frozen_symbol_days` — conservative for the
    unscreened control, so it understates the screen's benefit.
    `weighting="MW"` raises `NotImplementedError`: the PIT store kept
    `mcap_rank` only, so spec §7's EW-vs-MW sensitivity is BLOCKED until AMFI's
    absolute avg-mcap column is re-ingested (no rank proxy — that would be an
    invented number).
  - `src/metrics.py` — IR/Sharpe/maxDD/skew + Deflated Sharpe and Hansen SPA
    (Politis–Romano stationary bootstrap), charged against the register's
    cumulative trial count. No scipy (Acklam inverse-normal).
  - `scripts/run_trial_52wh.py` — the C1 door: research-door panel → walk-forward
    → NIFTY500 TRI scoring → §8 kill line → `data/derived/trials/52wh/` →
    append-only register result row. Sensitivities are flags.
- `.githooks/pre-commit` — SEAL.md immutability + `data/sealed/` commit block +
  frozen-spec immutability (spec edits AND recorded-hash rewrites/deletions).
  Fresh clones must run: `git config core.hooksPath .githooks`.

## KEY FACTS AND PINS

- Seal commit `b7e4224c311034ca57aa46e9ab38c46f75ce63cc`; cutoff 2024-07-17.
- Frozen clone `~/vendor/legacy-engine` @
  `ee7ad13228244f4f27e3d2d839baf70897ff24fe`, chmod -R a-w, no hardlinks;
  imports via PYTHONPATH in `.venv/bin/activate` (e.g. `costs.py`).
- rec_key = `data_date|SYMBOL|seq` (seq = generation ordinal; ledger rows use
  seq=1). The ledger's pick_date aligns with the rec's GENERATED date.
- Settlement basis: unadjusted yfinance OHLC — validated vs production's own
  backup (250/250 fetched; all divergences adjustment-basis only; the backup
  self-declares `price_source=yfinance_adj`).

## GOVERNANCE STACK (governance/)

- `SEAL.md` (immutable) + `SEAL_COMPANION.md`: dev data < 2024-07-17; sealed
  holdout ≥ cutoff; ONE pre-registered final test per signal family, ever;
  peek = family burned. Tier 1 forward data = look-don't-tune.
- `CONTAMINATION_POLICY.md`: any outcome-conditional analysis IS a trial
  (only outcome-blind diagnostics are free); pooled NAV test admits
  shadow-survivors only.
- `research_register_v2.csv` (append-only): ~51 inherited legacy trials +
  Silver ML engine ESTIMATE ≥8 (Tier 3-adjacent; its forecasts must never
  feed SPEC-AG-01).
- `AB_PREREG.md`: four pre-registered legacy A/B analyses (recommended-leg
  NAV alpha vs TRI; overlay-alpha decision-time only; veto quality; reduce
  efficacy). READ DATE 2026-09-27. Peek-then-act = logged breach. A green
  tape earns at most ONE forward re-test — the cost-based kill verdict
  stands regardless.
- `DECISIONS.md`: every ruling with FACT/ASSUMPTION tags — the audit trail.
  Live rulings: 1 rec_key · 2 Tier 1 look-don't-tune · 3 ingest scope · 4 SOP
  conventions · 5 cost stack · 6 freeze consumes no shadow slot · 7 inference
  doctrine (below).
- **INFERENCE DOCTRINE (RULING 7, binding).** **Hansen SPA gates; Deflated
  Sharpe reports.** SPA bootstraps the actual return series and depends on no
  unmeasurable constant. DSR's `SR0 = trial_sr_std × m(N)` scales LINEARLY with
  the dispersion but only logarithmically with trial count — `m(52)=2.29`, and
  one more trial moves the bar 0.32% while doubling the dispersion moves it
  100%. `trial_sr_std` is UNMEASURABLE here (reconstruction from legacy
  artifacts gave 3 distinct variants, 95% CI [0.35, 4.22]) and that route is
  CLOSED. Report DSR at 0.5 with the RULING 7 caveat until the operator sets
  the reporting band (proposed 0.35/0.50/0.70 — still PENDING). Never write a
  DSR floor into a frozen kill line.
- **TRIAL ECONOMICS (corollary, and counter-intuitive).** A marginal trial is
  CHEAP — it moves the deflation bar ~0.3%. The genuinely scarce resources are
  the **2 shadow slots** and the **single sealed test per family, ever**. Do
  not refuse a useful dev-data trial to "save trials"; do guard the slots and
  the sealed test absolutely.
- `specs/`: per-family frozen specs. A spec is BINDING only once its `sha256`
  is recorded alongside it and its register row exists (same commit); until
  then the file carries a DRAFT banner and may be edited freely. After freeze,
  changes require a new versioned spec, never an edit — the SEAL_v2 pattern.
  Currently: `SPEC-52WH-01.md` (**FROZEN 2026-07-19**, sha256 `4b58f285…`,
  register row `FREEZE-52WH-0001`). Enforced twice over: `.githooks/pre-commit`
  blocks post-freeze edits AND blocks rewriting/deleting a recorded hash (else
  a spec reopens by deleting its hash); `src/spec_guard.py` re-verifies at run
  time, since an uncommitted working-tree edit never meets the hook.
- `SOP_OF_RECORD.md`, `LEGACY_PIN.md`, `README_overlay.md`; repo-root
  `SETUP_OF_RECORD.md` = full inventory + open items.

## CURRENT STATE (as of 2026-07-20)

- Paper leg 25/25 settled: **ENTERED (gate-respecting headline) 11 recs =
  −1.32R**; ASSUMED_ENTRY 14 recs = +6.50R (tradeability audit: 12/14
  in-zone but volume-trigger unconfirmed, 2/14 gap-away; no demotion).
  Rec universe 18/18 settled. NAV: 15 daily marks, −0.70% since 2026-06-29.
- **Overlay log EMPTY — most time-sensitive item in the program.** Still 0
  data rows as of 2026-07-20: **21 of the 60–90 day live window already
  elapsed** (started 2026-06-29), i.e. a quarter to a third of the observable
  period gone. AB_PREREG analyses 2–4 have n=0 until decision-time logging
  starts; reconstruction proved zero vetoes are inferable (production ledgers
  every rec). Lost days are unrecoverable and the read date (2026-09-27) does
  not move. Cost to fix: one `overlay '<rec_key>' ...` call per live rec.
  Nothing in the Tier 2 pipeline outranks this.
- Advancing Tier 2 candidates: SPEC-QFM-01 (fundamental deltas, shadow slot
  1), SPEC-PEAD-01 (earnings drift, slot 2 — its CAR study is its one Tier 2
  trial, only after spec hash-freeze), SPEC-AG-01 (MCX Silver carry, queued
  behind the 2-shadow cap), SPEC-52WH-01 (52-week-high negative screen,
  queued behind AG-01). PIT fallback pre-committed (NIFTY100 →
  F&O-eligible on >2-quarter gap).
- **SPEC-52WH-01** (from the 2026-07-18 external-research session): the
  breakout family reframed around the cross-sectional 52-week-high effect
  (Raju 2023 — long leg alone does NOT beat index; the edge is a NEGATIVE
  screen: never hold far-from-high names). Habitat mcap ranks 201–1000;
  quarterly rebalance (slow decay); regime overlay mandatory (−1.5 skew);
  conditioning list closed at 5 (regime, volume-confirm, extension,
  earnings-proximity, LODR event-exit). Kill line: net IR ≤ 0 or SPA p >
  0.10 net → dead. Notes: `research.md` (outcome-blind, frozen record);
  execution + module blueprint: `plan_52wh.md` (living).
  **SPEC FROZEN 2026-07-19 (B3) + Stage 4 enforcement built** — see GOVERNANCE
  STACK above. Freezing consumed NO shadow slot (the cap-2 gate is Phase D's
  sealed test, not the freeze); QFM + PEAD hold both slots, AG-01 still queued
  ahead of 52WH. Outcome contact is now unlocked for **dev data < 2024-07-17
  only**, via `scripts/run_trial_52wh.py` and nowhere else.
  **Phase A (data groundwork) CLOSED 2026-07-19 — A1–A4 all done** and
  Stage 1–3 modules built + tested (see THE MACHINERY). **Phase B CLOSED, Stages 4-5 BUILT,
  C1 ATTEMPT 1 RUN AND WITHDRAWN (2026-07-19/20).** `C1-52WH-0001` was
  pre-registered and executed; its result (screened net IR +0.349, increment
  +0.168, SPA p 0.034, SURVIVES) is **WITHDRAWN AND UNCITABLE** — 33 yfinance
  holiday-placeholder dates (132 rows of 2.48M) NaN-blocked `rolling_max`'s
  `min_periods=252`, pushing first defined nearness to 2018-10-26 instead of
  2016-01-08, so the walk-forward started 2018-04 and its first three
  rebalances screened NOTHING (both arms identical for ~6 months, including
  the opening leg of the 2018-2020 drawdown the spec requires). Register row
  `C1-52WH-0001-DEFECT`; the trial is spent, not reclaimed. Fixed:
  `drop_non_trading_dates` quorum filter + a signal-starvation hard stop in
  `backtest_52wh`. **Next 52WH step: C1 ATTEMPT 2 — rebuild the panel, then a
  NEW `C1-52WH-0002` row (NOT yet authorized).** Key facts:
  PIT habitat reconstructable from announce-safe **2018-01-25** (AMFI lists
  18/18 periods 2017H2→2026H1, zero gaps; announce = period_end + 25d
  ASSUMED, flagged per row; F&O fallback never triggers pre-cutoff);
  adjusted panel 2015-01-01→2024-07-16, **1,310 symbols** (rename map
  2026-07-19 recovered 113 of the 215 yfinance-unservable names, old-label
  series truncated at rename effective date to prevent dual-label
  double-counting), split spot-checks passed. RESIDUAL CAVEAT: 102/1,412
  (7.2%) still unservable, skewed toward delistings — the C1 write-up must
  argue the survivorship hole's direction (details in `plan_52wh.md` A4).
- Open unknowns (was five, now FOUR): exchange filing-timestamp corpus
  (serves PEAD + 52WH event-exit); MCX bhavcopy history; **absolute market cap
  in the PIT store** (the A1 ingest kept `mcap_rank` only and dropped AMFI's
  avg-mcap column, so spec §7's EW-vs-MW sensitivity is BLOCKED — re-ingest
  before claiming it; no rank proxy); **`trial_sr_std` is UNMEASURABLE** and
  will stay open by ruling, not by neglect (RULING 7: only 3 distinct legacy
  variants recoverable, 95% CI [0.35, 4.22] — reconstruction CLOSED; SPA gates,
  DSR reports; the reporting band is an open operator decision). CLOSED
  2026-07-19: statutory cost stack (RULING 5, `governance/DECISIONS.md`;
  constants in `src/costs_in.py`; broker lines rest on an operator
  ASSUMPTION — contract-note reconciliation waived; slippage remains a
  separate explicit parameter); PIT constituent depth (A1 — corpus +
  store under `data/reference/pit/`, COVERAGE.md there); TRI depth (A3 —
  six daily TRI series incl. NIFTY500 TRI from 1995 under
  `data/reference/tri/`; Nifty200 Momentum 30 launched 2020-08-25, its
  pre-launch history is vendor-backfilled — flag in any use).

## TRAPS (paid for in real trials — do not re-learn these)

1. **A handful of bad rows can silently destroy years of signal.** 33 yfinance
   holiday placeholders (flat OHLC, volume 0) for 4 symbols — 132 rows of
   2.48M, 0.005% — NaN-poisoned the wide pivot for EVERY other symbol, and
   `expr._rolling_max` uses `min_periods=252`, so one NaN blocks the whole
   trailing window. First defined nearness moved 2016-01-08 → 2018-10-26 and
   C1-52WH-0001 ran three rebalances screening NOTHING. Guards now:
   `build_price_panel.drop_non_trading_dates` (quorum filter) and a
   signal-starvation hard stop in `backtest_52wh` (`min_ranked_frac`).
   **General rule: after any panel rebuild, check signal COVERAGE by date
   before trusting a result — row counts look fine when coverage is dead.**
2. **Audit the run BEFORE reading its headline.** The C1 schedule printed
   `ranked 0` three times; the number was on screen and got read past because
   the verdict line was more interesting. Read diagnostics first, verdict last.
3. **Fix inference parameters BEFORE outcome contact, in writing.** Choosing
   `trial_sr_std` after seeing whether it helps a family is precisely the
   contamination the policy exists to stop. When it was pre-committed, the
   measured value came out HIGHER than assumed — i.e. against the family under
   test. That is the discipline working.
4. **Never proxy a blocked sensitivity.** Spec §7 wants EW-vs-MW; the PIT store
   lacks absolute mcap, so `backtest_52wh` RAISES rather than substituting a
   rank-derived proxy. A disclosed gap is an asset; an invented number is a
   liability at due diligence.
5. **A withdrawn result is still a spent trial.** C1-52WH-0001 is not
   reclaimable. The register is append-only — corrections are new rows.

## ROADMAP (the path to the fund)

Phase 1 — live window (2026-06-29 → read date 2026-09-27):
1. **Start decision-time overlay logging NOW** — most urgent; AB_PREREG
   analyses 2–4 have n=0 until it starts and lost days are unrecoverable.
2. Keep nightly ingest + settlement + NAV running untouched.
3. Read the four A/B analyses ONCE on 2026-09-27. Prize = validated
   measurement stack + verdict on overlay skill; legacy kill stands.

Phase 2 — Tier 2 pipeline (parallel):
4. Close the remaining data unknowns (four; see SETUP_OF_RECORD.md). Three of
   the original five closed 2026-07-19 — PIT depth, cost stack, TRI depth.
5. Every candidate is judged NET of the RULING 5 friction stack with an
   explicit turnover budget and a separate slippage parameter. (Contract-note
   reconciliation is operator-WAIVED, not pending — RULING 5.)
6. Hash-freeze specs BEFORE outcome contact; develop pre-cutoff only; spend
   each family's single sealed test only when earned. Most families die —
   that is the protocol working. SPA gates every verdict (RULING 7).
7. **Immediate 52WH decisions queued for the operator:** (a) the DSR reporting
   band, (b) C1 ATTEMPT 2 authorization — rebuild the panel with the quorum
   filter, then a new `C1-52WH-0002` row; expected gain ~2 extra years of
   walk-forward (from ~2016 vs 2018-04) and a clean 2018-2020 crash leg.

Phase 3 — survivor to fund:
8. Sealed-test survivor → operational-door paper/forward trading → small
   live capital on the same A/B measurement stack.
9. Capacity analysis at ₹100 Cr (must survive its own footprint) → PMS
   registration + auditable track record → AIF Cat III. The governance
   trail is a due-diligence asset — keep it pristine.

Bottleneck lesson: gross alpha was never the constraint; friction was.
New families must be low-turnover by design.

Standing caution on 52WH specifically: the family's own evidence base says the
long leg does NOT beat the index — the edge is the negative screen, and the
spec frames it as a layer composable into QFM/PEAD, not a standalone book.
Before spending more on it as a solo family, ask whether its best use is inside
another selection engine.

## ENVIRONMENT

`.venv`: python 3.14, pandas 3.0.3, pytest 9.1.1, pyarrow 25.0.0,
yfinance 1.5.1 (+ openpyxl, pypdf for A1 corpus parsing). Tests:
`.venv/bin/python -m pytest tests/ -q` (155 passing as of 2026-07-20).
Data dirs (`data/sealed/`, `data/legacy_snapshot/`, `data/market/`,
`data/derived/`, `data/reference/`, plus the bulk 52WH panel artifacts
under `data/workspace/`) are gitignored — never push data. Remote:
https://github.com/ujjwal-k17/algo_trading.

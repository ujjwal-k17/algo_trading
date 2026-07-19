# plan_52wh.md — Executable Plan: SPEC-52WH-01 (52-Week-High Screen Family)

**Status:** Execution plan derived from `research.md` (2026-07-18 session). NOT a frozen
spec. Everything in Phases A–B is outcome-blind under `CONTAMINATION_POLICY.md`;
Phase C tasks are registered trials. **Created:** 2026-07-19.

**Standing priority note:** nothing here displaces the program's most time-sensitive
item — the overlay log is still EMPTY and AB_PREREG analyses 2–4 have n = 0 until
decision-time logging starts. `overlay '<rec_key>' ...` on every live rec comes first,
every trading day.

---

## What the evidence forced (one paragraph)

The original breakout idea — detect single-name chart breakouts, block failure
patterns — is dead on the literature: intraday ORB on NSE is noise (p≈0.5), chart
rules die net of costs (SPA p≈0.69), Darvas/VCP is not evidence. The survivor is the
cross-sectional 52-week-high effect (Raju 2023, India, 19y), but its long leg alone
does NOT beat the index — the entire premium is the catastrophic underperformance of
far-from-high stocks (Q1 α ≈ −2.4%/mo). Therefore SPEC-52WH-01 is redesigned as a
**negative screen / tilt layer** (never hold far-from-52wk-high names) composed with
another selection engine, not a standalone long strategy. Effect is strongest in
mcap ranks 201–1000, decays slowly (~84% survives a 6m hold → quarterly rebalance),
and carries −1.5 skew (regime overlay is necessary, not optional). Our value-add is
the net-of-cost test the paper never ran.

---

## Phase A — Data groundwork (outcome-blind, no register entries needed)

Order matters: A1/A2/A3 are the blocking unknowns; A4 is build work that can start now.

- [x] **A1. PIT constituent corpus — ACQUIRED + STORE BUILT 2026-07-19.**
      Corpus under `data/reference/pit/` (gitignored; manifest.csv + COVERAGE.md):
      AMFI avg-mcap lists **18/18 semi-annual periods 2017H2 → 2026H1, zero gaps**
      (2017H2 is the first list AMFI ever published — hard floor); 164 NSE/
      niftyindices index-change press releases 2015-01-21 → 2026-07-17 (PDFs
      archived; per-symbol add/drop extraction NOT yet parsed — four layout
      generations); current constituent lists for 8 indices. Canonical store:
      `staging/amfi_mcap_rank.csv` (89,895 rows) →
      `scripts/build_pit_universe.py` → `pit_universe.parquet` (89,891 rows,
      5,738 symbols), queried via `src/pit_universe.py` as-of helpers (gated on
      announce_date; verified: last research-visible list is 2023H2, announced
      2024-01-25). **Earliest reliable PIT date for the 201–1000 habitat:
      announce-safe 2018-01-25** (effective 2017-12-31). Announce dates are
      ASSUMED period_end + 25 calendar days (conservative vs all observed
      publications; flagged `announce_basis` per row). F&O fallback never
      triggers 2018 → cutoff. Caveats (COVERAGE.md §6): ~3% blank NSE symbols
      in 2025H2/2026H1 top-1000 — join on ISIN (carried in the store) for
      post-2025 periods; Wayback full-constituent anchors mostly unavailable
      (pre-2019 NOT_FOUND, 2020+ throttle-blocked, retryable) so the
      index-membership route to ~Apr-2016 stays unvalidated.
- [x] **A2. Statutory cost stack — CLOSED 2026-07-19** (open unknown #4) per
      RULING 5 in `governance/DECISIONS.md`: statutory lines FACT-verified from
      primary sources; broker lines closed on operator ASSUMPTION that the
      web-verified schedule equals the contract note (reconciliation waived; a
      later-diverging contract note triggers correction + rerun of affected
      trials). Constants live in `src/costs_in.py`. Verified stack, NSE cash
      equity, discount-broker retail schedule:
      - STT: delivery 0.10% buy AND sell; intraday 0.025% sell only.
      - NSE exchange txn charge: 0.00307%/side (₹306.99 txn + ₹0.01 IPFT = ₹307/cr;
        circular NSE/FA/73061 dt 2026-02-27, effective 2026-03-01, filed at
        `governance/evidence/NSE_FA_73061_transaction_charges_effective_2026-03-01.pdf`).
      - SEBI turnover fee: ₹10/cr (0.0001%)/side, +18% GST.
      - Stamp duty (buy side only): delivery 0.015%; intraday 0.003%.
      - GST 18% on (brokerage + exchange txn + SEBI + DP fees).
      - Brokerage (Zerodha schedule): delivery ₹0; intraday min(0.03%, ₹20)/order.
      - DP charge on delivery sell: ₹15.34/scrip/day (Zerodha/CDSL; Upstox ₹20) —
        broker-dependent, flat per scrip so ~0% at fund size.
      - Worked round trip per ₹1L/side: DELIVERY ≈ ₹237.8 ≈ **0.238%** (statutory-only
        ex-DP ex-brokerage ≈ 0.2225%); INTRADAY ≈ ₹82.7 ≈ **0.083%**. Slippage NOT
        included — keep 0.05–0.10%+/side (more in the 201–1000 band) as a separate
        parameter. Caveat: retail discount-broker basis; PMS/institutional
        brokerage differs — revisit constants at the Phase 3 (fund-vehicle)
        transition; C3 capacity analysis should stress higher friction.
- [x] **A3. TRI depth — CLOSED 2026-07-19** (open unknown #5). Six daily TRI
      series downloaded from niftyindices.com (204 chunked requests, zero
      blocks) into `data/reference/tri/` (raw/ + manifest.csv + COVERAGE.md;
      gitignored): NIFTY 500 TRI from 1995-01-01 (primary benchmark),
      NIFTY 100 TRI from 2003, Nifty Alpha 50 TRI from 2003-12-31, Nifty200
      Momentum 30 / Midcap 150 / Smallcap 250 TRI from 2005-04-01 — all to
      2026-07-17, no gaps > 5 trading days. VERDICT: every series covers
      2015-01-01 onward; 2018–2020 and 2022 drawdowns fully inside all six.
      BACKFILL FLAGS (must accompany any later use): Nifty200 Momentum 30
      launched 2020-08-25 (its entire pre-Aug-2020 history, incl. the
      2018–2020 crash, is vendor back-computed); Alpha 50 launched 2012-11-19;
      Midcap 150 / Smallcap 250 launched 2016-04-01; NIFTY 100 launched
      2005-12-01. Bonus: source also returns a net-TRI (`NTR_Value`) column,
      full history. Coverage-only check — no returns computed (outcome-blind).
- [x] **A4. PIT-clean adjusted price panel — BUILT 2026-07-19**
      (`scripts/build_price_panel.py` → `data/workspace/price_panel_52wh.parquet`):
      2,298,250 rows, 1,197 symbols, 2015-01-01 → 2024-07-16, gated through the
      research door (max date < cutoff verified). Fetch set = 1,412 symbols ever
      holding research-visible mcap_rank ≤ 1000; per-symbol cache in
      `data/workspace/ohlc_adj/`. Adjustment spot-checks passed: IRCTC 1:5
      (2021-10-28) and NESTLEIND 1:10 (2024-01-05) splits show no price cliffs.
      Integration smoke (features only): 2020-07-01 habitat = 725 PIT symbols,
      580 with defined nearness, buckets balanced 116×5.
      **Survivorship hole NARROWED 2026-07-19 — rename map built**
      (`scripts/build_rename_map.py`; NSE symbol-change master →
      `data/reference/rename/rename_map.csv`): of the 215 unservable symbols,
      120 had renames, **113 recovered** (fetched under the current ticker,
      cached under the ORIGINAL symbol so PIT joins work; ZOMATO→ETERNAL,
      TATAGLOBAL→TATACONSUM, chains followed). Recovered old-label series are
      **truncated at the rename effective date** — otherwise the same company
      is rankable under both labels post-rename (stale AMFI old-label rank
      stays as-of visible) and double-counts in the cross-section; verified
      TATAGLOBAL ends 2020-02-26, WELSPUNIND 2023-12-13. Also caught
      BAJAJAUTO as a one-off AMFI spelling artifact of BAJAJ-AUTO (2020H2
      list only) — correctly refused, no duplicate. Rebuilt panel: 2,479,338
      rows, **1,310 symbols**; smoke 2020-07-01 habitat ranked coverage
      580 → 626 of 725; buckets balanced 125×4+126.
      **RESIDUAL CAVEAT for the C1 write-up: 102/1,412 (7.2%, was 15%) still
      unservable** (95 no rename found + 7 renamed-but-unservable, mostly
      merger absorptions e.g. BHUSANSTL→TATASTLBSL) — skews toward delistings,
      plausibly the far-from-high bucket the screen bets against, i.e. the
      hole likely UNDERSTATES the effect; must be argued in the write-up with
      the then-current `price_panel_missing.txt`, not assumed.

## Phase B — Spec authoring & freeze (still outcome-blind)

- [x] **B1. Minimal expression evaluator — DONE 2026-07-19** (`src/expr.py`,
      `tests/test_expr.py`): closed grammar `ref` / `rolling_max` / `rolling_min` /
      `cs_rank` / arithmetic over long panels; unknown token = hard `ExprError`.
      Built alongside the rest of Stage 1–2 on synthetic frames:
      `src/pit_universe.py` (+ `scripts/build_pit_universe.py` ingester),
      `src/signal_52wh.py`, `scripts/build_price_panel.py` — all with
      no-look-ahead acceptance tests (suite 42 → 88 passing).
- [x] **B2. Spec text DRAFTED 2026-07-19** → `governance/specs/SPEC-52WH-01.md`
      (status DRAFT — binding only at B3; editable until the hash is recorded).
      Contains, verbatim as
      expression strings + parameters:
      - Signal: `close / rolling_max(high, 252)`, cross-sectional rank.
      - Role: **negative screen** (exclude bottom quintile/quartile
        "far-from-high" names from any book) + long-tilt diagnostic; the
        long-only top-bucket-as-alpha claim is explicitly NOT the hypothesis.
      - Universe: PIT ranks 201–1000 primary; NIFTY500 and Top-200 as sensitivity
        bands (capacity vs strength trade-off documented up front).
      - Rebalance: quarterly default (monthly and semi-annual as pre-registered
        sensitivities), turnover budget « 300%/yr.
      - Conditioning layer, closed list of 5 (one registered trial each): regime
        de-risking overlay (online rule only, e.g. index vs long MA), volume
        confirmation at entry, extension filter, earnings-proximity exclusion,
        event-exit rule (added 2026-07-19): intra-quarter exit triggered ONLY by
        a closed, pre-registered category list of SEBI LODR Reg 30 exchange
        disclosures (regulatory ban/action on core product, auditor resignation,
        fraud/default disclosure, promoter arrest), optionally with a same-day
        price co-trigger. Mechanical and PIT-clean — no "massive news" judgment
        calls. Pre-stated null: the quarterly screen's built-in ejection already
        captures this; the rule must beat waiting-for-rebalance NET of exit
        costs at panic prices and added turnover, or it dies. Data dependency
        shared with SPEC-PEAD-01 (open unknown #2, exchange filing-timestamp
        corpus).
      - Scoring: net-of-cost information ratio vs NIFTY500 TRI + factor-index
        overlap test; EW vs MW and liquidity-band sensitivity to separate premium
        from illiquidity mirage.
      - Kill line (pre-committed): net IR ≤ 0, or SPA/RC p > 0.10 net of costs →
        family dead. No "works gross" survivorship.
- [x] **B3. Spec HASH-FROZEN 2026-07-19.**
      `sha256 4b58f285255db1b35bdf831aaaaa16aae6bde8bbf38987a501194bf89ddbbefc`
      recorded in `governance/specs/SPEC-52WH-01.sha256`; register row
      `FREEZE-52WH-0001` added in the same commit; spec banner flipped
      DRAFT → FROZEN (that edit is inside the hashed text). The spec is now
      immutable — changes require `SPEC-52WH-02.md`, never an edit.
      **Queue ruling (recorded here because it was the gating question):** the
      shadow cap of 2 gates the *shadow-book / sealed-test* stage (Phase D,
      spec §10), not the freeze. Freezing consumes no slot — it only makes the
      text binding and unlocks Phase C outcome contact on **dev data
      < 2024-07-17**, which B3 always permitted ("pre-cutoff development may
      proceed"). QFM + PEAD keep both shadow slots; AG-01 stays queued ahead of
      52WH for the slot itself. No slot-jumping occurred.

## Phase C — Pre-cutoff development (registered trials, post-freeze only)

- [ ] **C1. Primary walk-forward** on dev data < 2024-07-17, spanning ≥ one full
      bull-bear cycle (2018–2020 crash and 2022 drawdown included), net of the A2
      cost stack at spec'd turnover, deflated Sharpe / SPA against the register's
      trial count. Screen framing: does excluding the far-from-high bucket improve
      a NIFTY500-band book's net IR / maxDD?
- [ ] **C2. The five conditioning trials**, one register row each, scored on net
      expectancy impact — not hit rate. The volume-confirmation trial doubles as
      the first rigorous Indian false-breakout-rate measurement (novel evidence);
      the event-exit trial is small-n by nature (rare events) — its register row
      must state the event count so the inference is honest about power.
- [ ] **C3. Capacity/footprint analysis at ₹100 Cr** in the 201–1000 band (ADV
      participation at spec'd turnover). A screen that only works where we can't
      deploy fails Phase 3 regardless of alpha.

## Phase D — Gate to sealed test

- [ ] Only if C1–C3 clear the kill line AND a shadow slot opens: pre-register the
      family's single sealed test (≥ 2024-07-17 holdout) per `SEAL.md`. One test,
      ever; peek = family burned. Most families die — that is the protocol working.

---

## Implementation blueprint (module-level, added 2026-07-19)

Build order below respects the contamination wall: Stages 1–3 compute **features
only** (no returns joined, no outcome contact) and are outcome-blind free work.
The returns join and any performance number exist only inside the trial runner
(Stage 5), which refuses to run without a frozen-spec hash match.

### Stage 1 — Data layer

| Artifact | What it does | Acceptance |
|---|---|---|
| `src/pit_universe.py` | PIT constituent store, qlib-style rows `(symbol, field, effective_date, announce_date, value, source)`; `universe_as_of(date, band)` returns only rows with `announce_date <= date`. | pytest: as-of query returns pre-announcement state; synthetic look-ahead row is invisible. |
| `scripts/build_pit_universe.py` | Ingests NSE index-change releases + AMFI semi-annual mcap rank lists into `data/reference/pit/` (gitignored) with a source manifest. | Coverage report: earliest reliable date per band; gap list vs the pre-committed F&O fallback. |
| `scripts/build_price_panel.py` | Adjusted OHLC panel for the dev window via `data_gate.load()` (research door only); split/bonus-adjusted consistently for close AND rolling high. | Panel rows all < 2024-07-17 (gate-enforced); adjustment spot-checks on known corporate actions. |

### Stage 2 — Signal layer

| Artifact | What it does | Acceptance |
|---|---|---|
| `src/expr.py` | Minimal expression evaluator over gate-emitted frames: `Ref`, `RollingMax`, `CSRank`, arithmetic. The spec's expression strings run through this and nothing else. | pytest vs hand-computed frames; unknown token → hard error (no silent prose rules). |
| `src/signal_52wh.py` | `nearness = close / rolling_max(high, 252)` at each rebalance date; cross-sectional rank within the PIT universe as-of that date; emits bucket labels (Q1–Q5). Pure function, features only. | No-look-ahead test: signal at date t unchanged when post-t rows are appended. |

### Stage 3 — Screen & portfolio layer (still outcome-blind) — BUILT 2026-07-19

| Artifact | What it does | Acceptance |
|---|---|---|
| `src/screen_52wh.py` ✅ | Applies the negative screen: given any candidate book/universe band, drops far-from-high bucket names (`screen_book` / `screened_symbols`); `tilt_weights` as diagnostic only. Unranked-name policy explicit (`keep` default / `drop` sensitivity). | DONE: set difference + weights; zero return columns in schema; a signal frame carrying ANY non-feature column (e.g. a joined return) is a hard error — the outcome-blind wall is structural. `tests/test_screen_52wh.py` (10). |
| `src/costs_in.py` ✅ | Cost stack per RULING 5 (Phase A2): brokerage, STT, exchange, stamp, GST, SEBI per leg; slippage a separate named parameter. | DONE 2026-07-19 (built with A2): `tests/test_costs_in.py`. |
| `src/rebalance.py` ✅ | Rebalance calendar (Q default, M/H sensitivities; last trading day per period from the panel's own dates — partial final period included, trial runner decides), `trades` diff, ONE-WAY turnover = sum(\|Δw\|)/2. | DONE: turnover on a synthetic book matches hand calc; calendar respects supplied holidays. `tests/test_rebalance.py` (9). |

### Stage 4 — Governance enforcement — BUILT 2026-07-19

Two independent halves: the hook is commit-time, the guard is run-time. Neither
alone is sufficient — a spec edited in the working tree and never committed
sails past the hook, so the runner re-verifies at the moment of outcome contact.

| Artifact | What it enforces | Acceptance |
|---|---|---|
| `.githooks/pre-commit` (extended) ✅ | A spec is FROZEN once its sibling `.sha256` is in HEAD; later edits blocked (SEAL.md pattern — the freeze commit itself is the allowed escape). Recorded hashes are themselves immutable: rewriting OR deleting one is blocked, else a spec reopens by deleting its hash. A freeze commit's staged hash must match the staged spec bytes, so freeze-and-edit in one commit is caught. | DONE: `tests/test_spec_freeze_hook.py` (6) — draft freely editable, freeze allowed, post-freeze edit blocked, hash rewrite/delete blocked, wrong-hash freeze blocked, same-commit freeze+edit blocked. |
| `src/spec_guard.py` ✅ | Run-time gate: `verify_frozen` (live sha256 of raw bytes == recorded) + `require_trial_row` (trial pre-registered) → `preflight` returns a provenance stamp. The runner never writes its own register row — that would make the check circular. | DONE: `tests/test_spec_guard.py` (6), incl. a live assertion that the real SPEC-52WH-01 is frozen and its register row cites the same hash. |
| `scripts/run_trial_52wh.py` ✅ | The ONLY place returns join signals. Preflight runs BEFORE any panel is read, so a failed gate cannot leak a glance at outcomes. Exit 2 = refused, 3 = Stage 5 engine not built. | DONE: verified live — unregistered trial refused (2); registered preflight passes (0); tampering with the real spec by one comment line → HASH MISMATCH refusal. |

### Stage 5 — Trial harness (post-freeze only)

- Walk-forward engine: expanding/rolling windows over dev data incl. 2018–2020 and
  2022; net returns via `costs_in.py` at realised turnover; IR vs NIFTY500 TRI;
  maxDD; EW-vs-MW and liquidity-band sensitivity.
- Inference: stationary-bootstrap Hansen SPA + deflated Sharpe implemented
  in-repo against the register's trial count (no external backtest framework —
  qlib rejection stands).
- Outputs to `data/derived/trials/52wh/` (gitignored); summary tables cited into
  `DECISIONS.md` with FACT tags.

### Sequencing & dependencies

1. Parallel now: A2 cost verification (needs a current contract note from the
   operator — external blocker) · A3 TRI depth checks · Stage 1 PIT ingestion
   (long pole).
2. Stage 2–3 code can be built and tested on synthetic frames immediately —
   they never touch outcomes.
3. Stage 4 freeze happens only when Stage 1–3 exist and the spec text is final.
4. Stage 5 runs after freeze; C2 conditioning trials each reuse the same runner
   with one added expression, one register row each.
5. Tests extend the existing suite (`tests/`, currently 42 passing); every new
   module ships with its no-look-ahead test.

## Explicit non-goals (evidence-based, do not resurrect)

Intraday ORB / intraday alert engines; single-name chart-pattern rules as primary
alpha; Darvas/VCP imports; offline change-point methods (PELT/Bai-Perron) as live
signals; DL price-level prediction; automated factor mining. The 10-item
event-breakout blocker list belongs, if anywhere, to a future SPEC-PEAD-01
entry-timing overlay — not to this family.

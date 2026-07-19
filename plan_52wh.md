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
      **OPEN CAVEAT — survivorship hole: 215/1,412 symbols (15%) unservable by
      yfinance** (`data/workspace/price_panel_missing.txt`) — mostly delisted
      (VIJAYABANK, WABCOINDIA…) but some are RENAMES recoverable via a symbol-
      map (e.g. ZOMATO→ETERNAL, WELSPUNIND→WELSPUNLIV). Before C1: build a
      rename map to recover what's recoverable, and the trial write-up must
      quantify the remaining hole's direction (missing names skew toward
      delistings — plausibly the far-from-high bucket the screen bets against,
      i.e. the hole likely UNDERSTATES the effect but must be argued, not
      assumed).

## Phase B — Spec authoring & freeze (still outcome-blind)

- [x] **B1. Minimal expression evaluator — DONE 2026-07-19** (`src/expr.py`,
      `tests/test_expr.py`): closed grammar `ref` / `rolling_max` / `rolling_min` /
      `cs_rank` / arithmetic over long panels; unknown token = hard `ExprError`.
      Built alongside the rest of Stage 1–2 on synthetic frames:
      `src/pit_universe.py` (+ `scripts/build_pit_universe.py` ingester),
      `src/signal_52wh.py`, `scripts/build_price_panel.py` — all with
      no-look-ahead acceptance tests (suite 42 → 88 passing).
- [ ] **B2. Write SPEC-52WH-01 as a frozen spec document** containing, verbatim as
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
- [ ] **B3. Hash-freeze the spec, enter it in `research_register_v2.csv`.** Only
      after B3 may any expression touch outcome data. Queue position: behind
      SPEC-QFM-01 / SPEC-PEAD-01 (shadow cap 2) and SPEC-AG-01 — pre-cutoff
      development may proceed, no slot-jumping.

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

### Stage 3 — Screen & portfolio layer (still outcome-blind)

| Artifact | What it does | Acceptance |
|---|---|---|
| `src/screen_52wh.py` | Applies the negative screen: given any candidate book/universe band, drops far-from-high bucket names; optional tilt weights as diagnostic. | Screen output is a set difference + weights; zero return columns in its schema. |
| `src/costs_in.py` | Cost stack from the verified contract note (Phase A2): brokerage, STT, exchange, stamp, GST, SEBI, slippage parameter — per leg. | Constants cross-checked line-by-line against the filed contract note; literature floor kept as a named fallback. |
| `src/rebalance.py` | Quarterly rebalance calendar, holdings diff → turnover computation. | Turnover on a synthetic book matches hand calc. |

### Stage 4 — Governance enforcement

- `governance/specs/SPEC-52WH-01.md`: expression strings + universe + rebalance +
  conditioning list + scoring + kill line. Freeze = commit + record
  `sha256` in `governance/specs/SPEC-52WH-01.sha256`; register row added in the
  same commit.
- Extend `.githooks/pre-commit`: any edit to a spec file with a recorded hash is
  blocked (same pattern as SEAL.md immutability).
- `scripts/run_trial_52wh.py` (the ONLY place returns are joined to signals):
  refuses to start unless (a) the spec file's live hash equals the recorded hash,
  and (b) a register row for this trial exists; appends its result reference to
  the register on completion. This makes trial accounting structural, not
  disciplinary.

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

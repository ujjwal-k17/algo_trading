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

- [ ] **A1. PIT constituent corpus — now to NIFTY500 / ranks-201–1000 depth.**
      Raju's size table moved the target habitat from NIFTY100 to ranks 201–1000, so
      open unknown #1 widens. Sources to exhaust: NSE index change press releases,
      AMFI semi-annual mcap rank lists (published since 2018), NSE indexogram
      archives. Deliverable: `(symbol, rank_band/index, effective_date, source)`
      table with an as-of query helper — qlib-style PIT schema
      `(instrument, field, period, announce_date, value)`.
      Fallback already pre-committed: F&O-eligible universe on >2-quarter gap.
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
- [ ] **A3. TRI depth** (open unknown #5): NIFTY500 TRI, NIFTY100 TRI, Nifty200
      Momentum 30, Nifty Alpha 50 — how far back each series goes, from NSE/index
      vendor downloads. Benchmarks must cover the full dev window incl. 2018–2020
      and 2022 drawdowns.
- [ ] **A4. PIT-clean adjusted price panel builder** for the dev window
      (< 2024-07-17), through `src/data_gate.py` research door only. Split/bonus-
      adjusted series used consistently for both close and rolling 252d high (the
      ratio distorts on unadjusted highs). Output: gated parquet under
      `data/workspace/`. yfinance is sanctioned; no broker calls.

## Phase B — Spec authoring & freeze (still outcome-blind)

- [ ] **B1. Minimal expression evaluator** over gate-emitted frames (qlib lesson:
      signal rules as expression strings, not prose — the string is the artifact
      that gets hashed). Small: `Ref`, `RollingMax`, cross-sectional `Rank` suffice.
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

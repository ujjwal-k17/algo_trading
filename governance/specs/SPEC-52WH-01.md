# SPEC-52WH-01 — 52-Week-High Negative Screen (frozen spec)

**Status: FROZEN (B3, 2026-07-19).** This document is BINDING. Its `sha256` is
recorded in `governance/specs/SPEC-52WH-01.sha256` and its register row
(`FREEZE-52WH-0001`) was added in the same commit. Any edit to this file is now
blocked by `.githooks/pre-commit`; changes require a new versioned spec
(`SPEC-52WH-02.md`) — the SEAL_v2 pattern, never an edit. `scripts/run_trial_52wh.py`
refuses to run unless this file's live hash equals the recorded hash.

Outcome contact is unlocked for **dev data < 2024-07-17 only** (Phase C). The
sealed holdout remains untouched: the family's single final test is pre-registered
separately at Phase D and requires an open shadow slot (cap 2 — currently QFM +
PEAD, with AG-01 queued ahead). Freezing consumes no shadow slot.

Evidence base: `research.md` Part 4 (Raju 2023, SSRN 4587697 — deep read
2026-07-18) and the 2026-07-18 breakout-literature review. Drafted 2026-07-19.

---

## 1. Hypothesis (what is claimed, and what is explicitly not)

**H1 (the family):** In the Indian mid-cap habitat, portfolios that structurally
exclude far-from-52-week-high names earn a higher net-of-cost information ratio
than the same portfolios without the exclusion. The anomaly is the catastrophic
underperformance of the far-from-high bucket (Raju: Q1 CAPM α ≈ −2.4%/mo), i.e.
the realisable edge for a long-only book is a **negative screen**.

**Explicitly NOT the hypothesis:** that a long-only near-high (top-bucket)
portfolio beats the index. The paper's own tables kill that claim (Q5 vs
NIFTY100 TRI t = −0.91; no Quartile-4 portfolio outperforms). Any tilt result
(§6) is reported as a diagnostic, never as the family's alpha claim.

## 2. Signal (expression strings — verbatim, closed grammar of `src/expr.py`)

- Nearness: `close / rolling_max(high, 252)`
  (canonical constant `NEARNESS_EXPR` in `src/signal_52wh.py`)
- Cross-sectional rank: percentile rank of nearness WITHIN the PIT universe
  as of the rebalance date (`signal_52wh.signal_at`, `cs_rank` ∈ (0, 1]).
- Buckets: `N_BUCKETS = 5` equal-count quantile buckets, Q1 = farthest from
  high … Q5 = nearest. Symbols with < 252 observed highs have no defined
  nearness and are unranked.
- Prices: split/bonus-ADJUSTED series used consistently for BOTH close and
  rolling high (`data/workspace/price_panel_52wh.parquet`; unadjusted highs
  distort the ratio after corporate actions).

## 3. Screen rule (the deliverable)

- **Exclusion set: Q1** (bottom quintile of nearness). `screen_52wh.screen_book`
  with `exclude_buckets=("Q1",)`.
- Pre-registered sensitivity: Q1+Q2 exclusion (bottom two quintiles).
- Unranked names (insufficient history): **kept** (`unranked_policy="keep"`) —
  the screen asserts only that far-from-high names underperform; unknown is not
  far-from-high. `"drop"` is a pre-registered sensitivity.
- Surviving weights renormalize proportionally over survivors.
- Candidate book for C1: the equal-weighted universe band itself (the screen's
  effect on a naive EW band book); composition with QFM/PEAD selection engines
  is future work under those specs, not this trial.

## 4. Universe

- **Primary habitat: PIT mcap ranks 201–1000** (`pit_universe.universe_as_of`,
  band `"201-1000"`) — the effect's strongest habitat (Raju: 501–1000 Q4−Q1
  Sharpe 1.72 vs Top-200 0.52).
- Sensitivity bands (capacity-vs-strength trade-off, pre-registered):
  `"NIFTY500"` membership; Top-200 (`"1-200"`).
- PIT source: AMFI semi-annual mcap lists, announce-gated (announce =
  period_end + 25 calendar days, ASSUMED, flagged per row). Earliest
  announce-safe date: 2018-01-25. Pre-committed fallback on a >2-quarter gap:
  NIFTY100 → F&O-eligible (never triggers pre-cutoff).
- Known holes, disclosed not hidden: 215/1,412 fetch symbols initially
  unservable by yfinance; renames recovered via
  `data/reference/rename/rename_map.csv` (NSE symbol-change master); the
  residual unrecoverable set skews toward delistings — plausibly the very
  far-from-high names the screen bets against, so the hole likely UNDERSTATES
  the screen's benefit. The C1 write-up must argue this direction explicitly
  with the then-current residual list.

## 5. Rebalance & turnover

- **Quarterly rebalance (default)** — last trading day per quarter from the
  panel's own calendar (`rebalance.rebalance_dates(dates, "Q")`); signal
  computed as of that date, positions effective from the next session.
- Pre-registered sensitivities: monthly (`"M"`), semi-annual (`"H"`).
- **Turnover budget: < 300%/yr one-way** (`rebalance.turnover` convention:
  sum(|Δw|)/2 per rebalance). Expected order: quarterly screen churn well
  under budget; a variant that busts the budget is dead regardless of gross.

## 6. Conditioning layer — CLOSED list of 5 (one registered trial each)

No additions without a spec amendment BEFORE the relevant trial (which is a new
hash — SEAL_v2-style, never an edit). Each scored on **net expectancy impact**,
not hit rate:

1. **Regime de-risking overlay** (mandatory candidate, not optional decoration —
   long-short skew −1.49): online-computable rule only, e.g. index vs long MA;
   must improve Sharpe/maxDD net of switching costs.
2. **Volume confirmation at entry** — doubles as the first rigorous Indian
   false-breakout-rate measurement.
3. **Extension filter** — exclude names too far ABOVE the reference level
   (buying exhaustion).
4. **Earnings-proximity exclusion** — binary event risk, not signal.
5. **LODR event-exit** — intra-quarter exit triggered ONLY by a closed category
   list of SEBI LODR Reg 30 disclosures (regulatory ban/action on core product,
   auditor resignation, fraud/default disclosure, promoter arrest), optionally
   with a same-day price co-trigger. Mechanical and PIT-clean. Pre-stated null:
   quarterly ejection already captures this; the rule must beat
   waiting-for-rebalance NET of panic-price exit costs and added turnover.
   Depends on the exchange filing-timestamp corpus (open unknown, shared with
   SPEC-PEAD-01); its register row must state the event count (small-n honesty).

## 7. Scoring

- **Headline: net-of-cost information ratio vs NIFTY500 TRI**
  (`data/reference/tri/`, from 1995) of screened-vs-unscreened band book.
- Costs: `src/costs_in.py` delivery stack (statutory FACT + broker ASSUMPTION
  per RULING 5) at realised turnover, PLUS explicit slippage parameter ≥
  0.05–0.10%/side, higher stress for ranks 201–1000. No gross-only reporting.
- Factor-overlap test vs Nifty200 Momentum 30 TRI and Nifty Alpha 50 TRI ("is
  this just investable momentum?"). Flag: Momentum 30 pre-2020-08-25 history is
  vendor-backfilled.
- EW vs MW and liquidity-band sensitivity — separate premium from illiquidity
  mirage (Raju's EW-flattered results).
- MaxDD and skew of screened vs unscreened book (the −1.5-skew crash profile
  is the risk being managed).
- Walk-forward over dev data < 2024-07-17 spanning the 2018–2020 crash and
  2022 drawdown; inference via deflated Sharpe / Hansen SPA against the
  register's cumulative trial count (in-repo implementation; no external
  backtest framework).

## 8. Kill line (pre-committed, no renegotiation)

**Net IR ≤ 0, or SPA/RC p > 0.10 net of costs → family dead.** No
"works gross" survivorship. C3 capacity failure at ₹100 Cr in the deployable
band (ADV participation at spec'd turnover) kills independently of alpha.

## 9. Machinery bindings (Stages 1–3, built and tested pre-freeze)

| Component | Module | Role |
|---|---|---|
| Expression evaluator | `src/expr.py` | the ONLY interpreter for §2 strings |
| PIT universe | `src/pit_universe.py` | announce-gated as-of membership |
| Signal | `src/signal_52wh.py` | nearness, cs_rank, buckets (features only) |
| Screen | `src/screen_52wh.py` | §3 rule; outcome columns structurally rejected |
| Calendar/turnover | `src/rebalance.py` | §5 dates and one-way turnover |
| Costs | `src/costs_in.py` | §7 cost stack |
| Trial runner | `scripts/run_trial_52wh.py` (Stage 5, NOT YET BUILT) | the only place returns join signals; refuses to run without hash match + register row |

## 10. Trial plan after freeze

C1 primary walk-forward (screen on/off, primary band) → C2 the five
conditioning trials (§6, one register row each) → C3 capacity/footprint at
₹100 Cr. Only if C1–C3 clear §8 AND a shadow slot opens (cap 2, currently
QFM + PEAD; AG-01 queued ahead): pre-register the single sealed test per
`SEAL.md`. One test, ever; peek = family burned.

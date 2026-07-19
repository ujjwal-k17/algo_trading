# research.md — External Research Learnings & Breakout Family Design Notes

**Status:** Working research notes. NOT a frozen spec. Nothing in this file has touched
repo outcome data; all evidence below is external literature / external codebase review.
Under `CONTAMINATION_POLICY.md`, reading external research is outcome-blind and free.
The moment any hypothesis here is tested against our own data, it becomes a registered
trial in `research_register_v2.csv`.

**Created:** 2026-07-18
**Inputs:** (1) Review of microsoft/qlib (v0.9.7, ~46k stars); (2) multi-paper literature
review on breakout detection with an Indian-equities lens (user-supplied synthesis,
2026-07-18); (3) full read of Raju (2023) SSRN 4587697 PDF (see Part 4, 2026-07-18).

---

## Part 1 — Learnings from microsoft/qlib

### Adopt (ideas, not the framework)

1. **Point-in-time database schema.** Qlib's PIT layer stores fundamentals as
   `(instrument, field, fiscal_period, announce_date, value)` and resolves queries
   as-of a date — only what was knowable then. This is the right template for two of
   our five open unknowns: the NIFTY100 PIT constituent corpus and the exchange
   filing-timestamp corpus. Directly serves SPEC-QFM-01 and SPEC-PEAD-01.

2. **Declarative factor expressions as freezable specs.** Qlib defines factors as
   expression strings (`Ref($close, 20) < $close`, rolling ops, cross-sectional
   ranks). For us the value is governance, not convenience: an expression string is
   exactly the artifact to hash-freeze. Signal rules in future specs should be
   written as unambiguous expressions, not prose. A minimal evaluator over
   gate-emitted frames is small work and hardens the freeze.

3. **Alpha158 as a *closed vocabulary*, not a mine.** Their 158-factor catalog is a
   useful checklist for writing well-defined pre-registered features. Reading the
   menu is free; running all 158 against outcomes is 158 trials. The catalog is
   consulted during spec-writing, then closed before outcome contact.

4. **Model-zoo lesson.** Across 25+ SOTA models on the same data, deep models beat
   LightGBM by small, run-unstable margins. Model sophistication is not where edge
   comes from; hypothesis and data quality are. If a family ever earns an ML fitting
   stage, it gets ONE pre-registered model (almost certainly LightGBM).

### Reject

- **RD-Agent / automated factor mining** — industrial-scale multiple testing with no
  trial accounting; the exact anti-pattern our seal exists to prevent.
- **Model zoo as shopping list** — 25 models on one dataset = 25 trials.
- **Qlib's backtest/cost engine** — flat-rate, China conventions; our friction
  modeling (verified contract note + impact) must be stricter.
- **Direct dependency** — Python 3.8–3.12 / pandas ≤2.x vs our 3.14 / pandas 3.0;
  and its data layer would be a second door around `src/data_gate.py`. Any
  qlib-style tooling we build consumes gate-emitted frames only.

---

## Part 2 — Learnings from the breakout literature review (Indian-equities lens)

### The hierarchy of evidence, condensed

| Signal class | India evidence | Verdict |
|---|---|---|
| 52-week-high cross-sectional (George-Hwang 2004; Raju 2023 India, Oct 2004–Aug 2023) | Robust, India-specific, ~19y sample; beats academic momentum with weaker reversals | **Only breakout-adjacent survivor** |
| Intraday ORB (Wang-Gangwar 2025, NSE) | Bootstrap p ≈ 0.45–0.50 — indistinguishable from noise | Dead |
| Chart-rule breakouts generally (Heyman-Inghelbrecht-Pauwels, 34 EMs) | India's best rule: p≈0.00 gross → Hansen SPA p≈0.69 net of costs | Dead net of costs |
| Darvas box / VCP (vendor + one 2025 midcap paper) | Hindsight-selected multibaggers, no costs, no significance tests | Not evidence |
| Donchian / volume-confirmed false-breakout rates in India | **No rigorous study exists** | Genuine gap (absence, not negative) |
| Structural breaks / regime (Bai-Perron, Markov-switching, HMM) | Robust for *dating* regimes; tradeable-signal claims (HMM+MC Sharpe 1.05) are in-sample, cost-free | Use defensively (risk overlay), not as alpha |
| CNN chart-image (Jiang-Kelly-Xiu 2023) | Value-weighted Sharpe ~0.5; India only via transfer test; EW Sharpes lean on illiquid names | Real but modest; no India standalone |
| Indian LSTM/DL price-prediction papers | >90% "accuracy" = level-prediction autocorrelation / leakage red flags | Discount entirely |

### Principles extracted

1. **Where the statistics are done properly, edges are real but modest** — fractions
   of a percent per month, value-weighted Sharpes ~0.5. Where returns look
   spectacular, the statistics were never computed. This matches our own legacy
   kill: gross alpha real, friction decisive.
2. **The durable "new-high" edge lives at the monthly cross-sectional horizon**, not
   at intraday/event chart level. Market maturity governs TA survival (Hsu-Kuan
   2005); India behaves like a maturing market where naive rules are arbitraged.
3. **Data-snooping correction is non-negotiable.** White Reality Check / Hansen SPA /
   deflated Sharpe. Sullivan-Timmermann-White: the best in-sample rule died in the
   10-year post-sample. Kill threshold adopted from the review: **SPA/RC p > 0.10
   net of costs → rule abandoned.**
4. **Volume confirmation: validate, don't assume.** Vendor "60–70% success" claims
   are unaudited; no rigorous Indian false-breakout-rate study exists. If we measure
   it, we produce novel evidence — as a registered trial.
5. **Regime detection is a risk overlay.** Offline break-daters (Bai-Perron, PELT)
   have full-sample look-ahead; only online methods are candidate real-time inputs.
   An overlay must improve Sharpe/maxDD of an existing strategy net of switching
   costs, or it's curve-fit.
6. **Cost floor for any India backtest:** ₹20/order discount brokerage + STT +
   exchange fees + GST, plus ≥0.05–0.10% slippage large-caps (more for mid/small).
   To be superseded by our verified contract-note cost stack (open item #4).

---

## Part 3 — Design direction: SPEC-52WH-01 (draft direction, pre-freeze)

**Reframe forced by the evidence:** the original idea ("detect single-name chart
breakouts, block the failure patterns") is the part the literature kills. The
survivor is the cross-sectional 52-week-high effect. The family is therefore
redesigned around it.

### Core signal (to be frozen as expression strings)

- **Universe:** NIFTY100, PIT constituents (fallback already pre-committed:
  F&O-eligible on >2-quarter gap). Depends on open unknown #1.
- **Signal:** nearness to 52-week high = `close / rolling_max(high, 252)`,
  cross-sectionally ranked monthly.
- **Portfolio:** long top decile/quintile (long-only for PMS realism; long-short as
  diagnostic), monthly rebalance, size-controlled weighting.
- **Turnover budget:** target well under ~300%/yr — orders of magnitude below the
  legacy 1.6 RT/day. Low-turnover-by-design is the point.
- **Benchmark:** NIFTY500 TRI, plus NSE's Nifty200 Momentum 30 and Nifty Alpha 50
  factor indices (the "is this just investable-index momentum?" test). Depends on
  open unknown #5 (TRI depth).

### Pre-registered conditioning layer (small, closed list)

Each is ONE registered trial on pre-cutoff data, scored on net expectancy impact,
not hit rate:

1. Regime overlay (defensive de-risking only — online-detectable rule, e.g. index
   vs long MA; must improve Sharpe/maxDD net of switching costs).
2. Volume confirmation at rebalance entry (novel India measurement; validate, don't
   assume).
3. Extension filter (exclude names too far above the reference level — buying
   exhaustion).
4. Earnings-proximity exclusion (binary event risk, not signal).

The 10-item event-breakout blocker list from earlier discussions is NOT part of this
family. If ever tested, it belongs to a separate entry-timing overlay for
SPEC-PEAD-01 (breakout-confirmed entries on positions carrying independent edge).

### Statistical bar (pre-committed)

- Walk-forward on dev data (< 2024-07-17) spanning ≥ one full bull-bear cycle —
  the 2018–2020 and 2022 drawdowns are pre-cutoff and must be included.
- Net of the verified cost stack at the spec'd turnover.
- Multiple-testing correction across all specification choices (deflated Sharpe or
  SPA against the trial count in the register).
- **Kill line: net-of-cost information ratio ≤ 0, or SPA/RC p > 0.10 net → family
  dead. No "works gross" survivorship.**

### Process & queue position

1. This file is research notes. Next artifact = frozen spec (expression strings +
   universe + rebalance rules + conditioning list + scoring + kill line), hashed
   BEFORE any outcome contact with our data.
2. Family enters `research_register_v2.csv` at spec-freeze.
3. Shadow-slot cap (2) currently held by SPEC-QFM-01 and SPEC-PEAD-01; SPEC-AG-01
   already queued. SPEC-52WH-01 queues behind — pre-cutoff development may proceed,
   but no slot-jumping.
4. Blocking dependencies (open unknowns): PIT constituents (#1), statutory cost
   verification (#4), TRI depth (#5).

### What we explicitly will NOT build (evidence-based rejections, logged here)

- Intraday ORB or any human-in-loop intraday alert engine (Wang-Gangwar p≈0.5;
  friction arithmetic; legacy kill).
- Single-name chart-pattern rules as primary alpha (SPA p≈0.69 net in India).
- Darvas/VCP as imported "known edges" (no evidence survives scrutiny).
- Offline change-point methods (PELT/Bai-Perron) as live entry signals (look-ahead).
- DL price-level prediction (leakage-driven accuracy mirages).
- Automated factor mining à la RD-Agent (contamination machine).

---

## Part 4 — Deep read: Raju (2023), "The 52-Week High Effect and Momentum Investing:
## Evidence from India" (SSRN 4587697, full PDF, read 2026-07-18)

Sample: Oct 2004–Aug 2023 (227 months), 4,331 NSE/BSE firms (Worldscope/Datastream,
includes delisted → survivorship handled). Metric: `52w = close(t-1) / 52wk_high(t-1)`,
monthly quintile/quartile sorts. Factors from Invespar India library. **No transaction
costs anywhere in the paper.**

### Headline numbers (annualised excess over risk-free unless noted)

| Portfolio | Return | Sharpe | Notes |
|---|---|---|---|
| EW Q5 (near high, long-only) | +8.06% | 0.34 | vs NIFTY100 TRI +8.20%, Sharpe 0.37 — t-value −0.91: **does NOT beat index** |
| EW Q1 (far from high) | −16.41% | −0.44 | CAPM α −2.36%/mo*** — the real anomaly |
| EW Q5−Q1 long-short | +21.56% | 1.12 | CAPM α +2.26%/mo***; skew −1.49 |
| MW Q5−Q1 | +20.39% | 0.67 | paper: "all performance comes from the short leg… more theoretical than realisable" given India shorting constraints |
| WML52W factor (EW / MW) | 13.55% / 14.09% W−L | 0.83 / 0.75 | FF6 α ≈ 1.0%/mo***; ~20% of returns unexplained by FF5+momentum |

### The finding that changes our plan: THE LONG LEG ALONE HAS NO EDGE

Across every construction in the paper — EW/MW quintiles, size-controlled quartiles,
FF 2x3 winners — **no long-only "near-high" portfolio significantly beats NIFTY100
TRI** (Q5 t −0.91; Top-200 Qu4 t −1.49; EW Winner t −0.49; "None of the Quartile 4
portfolios outperforms the Nifty 100"). Long-leg CAPM alphas are ≈0 (only
not-significantly-negative); FF6 long-leg alphas are significantly NEGATIVE. The
entire published premium is the catastrophic underperformance of far-from-high
stocks (Q1: −16% to −26%/yr, α −2.4 to −3.2%/mo). Anchoring mispricing shows up as
losers-keep-losing, not winners-keep-winning.

### Size structure — effect lives in mid-caps, not large caps

Q4−Q1 spread by size rank (EW, Oct 2006–Aug 2023): Top 200 = 11.25%/yr (Sharpe
0.52); 201–500 = 21.70% (1.04); **501–1000 = 31.15% (1.72)**; 1000+ = 19.52% (1.15).
Effect is weakest exactly in the Top-200/NIFTY100 habitat we had penciled in for
SPEC-52WH-01, strongest in the 201–1000 band (the legacy system's mid-cap habitat —
consistent with our own prior that Indian mid-caps are where inefficiency lives).

### Decay — the friction-friendly fact

Mean monthly return of WML52W by holding period (EW): 1m 1.18% → 3m 1.11% → 6m
0.99% → 12m 0.76% → 24m 0.60%; FF6 intercepts stay significant through 24m.
Academic momentum decays much faster (0.81% → 0.51% → 0.33% by 12m). ~84% of the
premium survives a 6-month hold → **quarterly/semi-annual rebalance retains most of
the effect at a fraction of the turnover.** India shows long-term reversals (unlike
George-Hwang US), but weaker than academic momentum.

### Risk profile

Strong negative skew everywhere that matters (Q5 −1.28; long-short −1.49 to −1.81)
→ momentum-crash behaviour; a defensive regime overlay has a genuine job. WML52W
correlates −0.60/−0.62 with the market factor and 0.78–0.81 with academic momentum
(distinct but related; FF6 α ~1%/mo confirms distinctness). EW consistently beats
MW → part of the paper's premium leans on small/illiquid names; capacity caution.

### Implications — revisions to the Part 3 design direction

1. **Long-only top-quintile as primary alpha is dead on the paper's own tables.**
   A long-only PMS cannot short Q1, and the long leg alone ≈ index. REFRAME:
   the implementable edge for a long-only book is the SHORT leg used as a
   **negative screen** — never hold far-from-52wk-high stocks. Avoiding Q1/Q2
   (α −2.4%/mo names) inside whatever book we run is the realisable fraction of
   the anomaly. 52WH becomes a screen/tilt layer, likely composed with another
   selection engine (QFM/PEAD candidates), not a standalone strategy.
2. **Universe revision:** effect strongest in ranks 201–1000. NIFTY100-only
   implementation sits in the weakest habitat. The PIT constituent unknown now
   extends to NIFTY500 (or ranks-by-mcap) depth, not just NIFTY100. Capacity at
   ₹100 Cr in the 201–1000 band needs explicit footprint analysis.
3. **Rebalance revision:** quarterly (or slower) rebalance is now the default —
   slow decay means we keep ~84–94% of gross premium at 6m/3m holds while cutting
   turnover ~3–6x vs monthly. Low-turnover-by-design, per the bottleneck lesson.
4. **Regime overlay confirmed as necessary**, not optional: −1.5 skew is exactly
   the crash profile a de-risking overlay exists for.
5. **Our value-add is the net-of-cost test the paper never ran** — plus EW-vs-MW
   and liquidity-band sensitivity to separate real premium from illiquidity mirage.
6. Data note: metric needs only prices (52wk high + monthly closes) — cheap to
   build PIT-clean; must use split/bonus-adjusted series consistently for the
   ratio (unadjusted highs would distort post-corporate-action).
7. Honest-prior update: paper is gross-only, EW-flattered, working-paper status.
   Expected realisable long-only increment over index from the screen version:
   low single digits %/yr before costs — meaningful for a fund, nowhere near the
   headline 21.6%/1.12-Sharpe long-short numbers, which are not implementable.

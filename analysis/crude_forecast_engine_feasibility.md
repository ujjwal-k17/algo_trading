# Crude-Oil Forecast Engine → Indian Equity Direction — Feasibility / Scoping Memo

**Question (operator, 2026-07-23):** Can we build a crude-oil price-forecasting
engine and chain it onto the crude betas that `DIAG-MACROBETA-0001`
(`analysis/macro_beta_diagnostic.md`) just validated — paints NEG
(ASIANPAINT / BERGEPAINT / PIDILITIND), E&P POS (ONGC / OIL / HINDOILEXP / VEDL)
— to forecast the *direction* of those stocks, framed by the requester as a
">95% accurate" crude engine?

---

## GOVERNANCE HEADER (read first)

- **OUTCOME-BLIND feasibility / scoping memo.** Literature, data-source
  assessment, friction arithmetic, and single-series characterisation of crude's
  OWN time-series properties only. Under `CONTAMINATION_POLICY.md` AMENDMENT A,
  "correlation and cointegration structure" and "cost tables" are explicitly
  free.
- **NO TRIAL SPENT.** Cumulative trial count stays at **53**. No stock return is
  conditioned on any crude forecast anywhere in this memo — no backtest, no CAR,
  no hit-rate, no conditional/forward stock return, no spread, no Sharpe/IR. The
  moment a stock return is conditioned on a crude signal it is a TRIAL under
  AMENDMENT A, and **this memo authorizes none.**
- **NO SHADOW SLOT consumed.** Both shadow slots are held (QFM, PEAD); AG-01
  (a commodity carry family) and 52WH are queued ahead of any new family. This
  memo does not draft a spec, does not freeze a hash, and does not create a
  register family.
- **NO broker/Kite call** (BINDING RULE 3); **no scraping** of exchange or any
  other site (this session's web-search budget was also exhausted before this
  memo — see §6 note); **no production contact** (BINDING RULE 1);
  **FINAL_TEST never set.**
- **Relationship to the register:** builds on `DIAG-MACROBETA-0001` /
  `-RESULT` (2026-07-23, crude betas validated, no trial spent) and on
  `DIAG-BREAKOUT-ENTRY-0001` (2026-07-23, DO-NOT-BUILD, same friction-hurdle
  logic). A proposed **text-only** register row is offered in §11 for the
  operator to enter — this memo does **not** write it.

---

## VERDICT (stated first, argued below)

**DO NOT BUILD a crude-oil forecasting engine to drive an Indian-equity
directional book.** Three independent walls each defeat it on their own; together
they are decisive.

1. **The ">95% accurate" premise is false and must be rejected outright** (§1).
   No public crude model achieves anything remotely like that; the honest
   short-horizon directional number is *barely above a coin flip once you strip
   the free win of predicting "up" in a bull regime*. A forecaster who believes
   95% is measuring in-sample or fooling themselves on a benchmark. Debunking
   this is the memo's first job, not an aside.

2. **The validated betas are an EXPOSURE, not an alpha** — the macro memo said
   this in its own §11, and it is the load-bearing point. A tradeable stock
   signal here needs TWO things at once: (a) future crude direction forecastable
   with real edge *over the futures curve*, and (b) that edge surviving
   transmission to the stock net of friction. The macro memo established the
   betas (the transmission channel exists). It said nothing — and was not
   allowed to say anything — about (a), which is the hard half.

3. **The double tax kills whatever edge (a) might yield** (§7). The stock
   captures only β_oil ≈ 0.05–0.11 of the crude move (market-adjusted), so the
   crude edge is scaled DOWN ~10–20× before it meets a round-trip friction floor
   of **~32 bps** (statutory ~22.4 bps, ~89% irreducible STT, plus a 5 bps/side
   slippage floor) that is **not scaled at all**. Break-even requires forecasting
   a **3–6% NET directional crude move per round trip** on the best-beta names —
   roughly **2 standard deviations of *expected* (not realised) daily crude
   move**. That is not a hurdle; it is a wall.

**Strongest evidence FOR (stated fairly):** the crude betas are unusually clean
and economically coherent (sign test 76.9%, p=6.4×10⁻⁵; paints and E&P survive
FDR + sub-period stability + Huber + shock-exclusion). The transmission channel
is as real as this program has ever measured. *If* crude were forecastable with
edge, these are exactly the names through which it would show up.

**Strongest evidence AGAINST:** that "if" is false in the way that matters. Crude
is among the most liquid, most-researched instruments on earth; the academic and
practitioner consensus is that the no-change random walk and the futures curve
are extremely hard to beat out-of-sample at the horizons an equity book could
act on. And even granting a forecast edge, the double tax (§7) means it must be
enormous to reach a stock P&L — while the *strictly better* place to express any
crude view is crude futures directly (β = 1, no attenuation), which is a
commodity strategy (**AG-01's territory**), not this repo's equity mandate.

**The one legitimate use of the validated betas is what the macro memo already
named:** RISK MANAGEMENT / HEDGING / factor-neutralisation, and as a CONDITIONING
INPUT for someone who already holds a macro view — **not** an autonomous
directional oracle. The four-decade crude analyst persona is valuable *as that
conditioning input*, not as a ">95%" engine.

**A narrow defensible research path exists but is NOT worth a slot now** (§10):
it is a commodity-futures forecasting question (AG-01 space), it must beat the
curve+random-walk benchmark rather than zero, and it inherits every AG-01 data
blocker. Nothing about it justifies displacing QFM, PEAD, or AG-01.

---

## 1. The ">95% accurate" premise — debunked up front, unhedged

I bring the domain view of a crude analyst: OPEC+ quota mechanics and spare
capacity, OECD/US commercial inventory cycles (EIA weekly petroleum status /
API), refinery utilisation and crack spreads, the futures term structure
(contango/backwardation and roll yield), positioning (CFTC COT managed-money net
length), the USD/crude relationship, and geopolitical supply shocks. That
knowledge is real and useful. **The ">95% directional accuracy" claim is not, and
no honest practitioner makes it.** Stated plainly:

- **No public crude model achieves ~95% directional accuracy at any horizon an
  equity book could trade.** Crude short-horizon direction is close to a random
  walk. This is not a niche opinion; it is the mainstream real-time-forecasting
  finding (§4, Baumeister–Kilian; Alquist–Kilian–Vigfusson). [FACT — literature
  consensus; specific papers **unverified at source this session**, see §6 note.]

- **A "95%" belief is one of three things, all measurement errors:**
  1. **In-sample fit** — the model saw the answer. Out-of-sample it collapses.
  2. **The free bull-regime win** — in a trending market, predicting "up" every
     day is right ~55% for zero skill. Crude has long directional regimes
     (2020–2022), so a naive "up" call *looks* accurate over a chosen window.
     This is a benchmark illusion, not forecasting. [FACT — arithmetic of a
     biased base rate.]
  3. **Misremembering / narrative recall** — remembering the calls that worked,
     forgetting the ones that didn't; the geopolitical events that "obviously"
     moved crude are obvious *only in hindsight* (§5).

- **The correct scoreboard is not "% right"; it is "% right vs the futures curve
  and the no-change random walk, out-of-sample, net of cost."** Against *that*
  bar, the honest edge for public information is small, unstable, and
  horizon-specific — the opposite of 95%.

This program's cardinal sin is the **invented number** (TRAP 4) and its
characteristic failure is **silence dressed as a clean result** (TRAP 6). "95%
accurate" is an invented number. Treating it as the thing to debunk — not the
thing to assume — is where the credibility of this memo comes from. **Refused.**

---

## 2. The double-prediction problem

A tradeable equity signal on this chain needs **two independent things to hold at
once**:

> **(a)** future crude *direction* is forecastable with edge **over the futures
> curve + random walk**, out-of-sample, net; **AND**
> **(b)** that edge survives *transmission* into the stock, net of friction and
> beta attenuation.

`DIAG-MACROBETA-0001` settled the *existence of the transmission channel* — the
betas are real, clean, and economically coherent. It settled **nothing about
(a)**, and §11 of that memo said so explicitly: *"a contemporaneous beta is an
EXPOSURE, not an alpha… untradable unless crude itself is predictable — a
separate and much harder claim this diagnostic does NOT address and is NOT
authorized to address."*

This memo is about **(a)** and the **transmission economics**. The requester's
framing skips (a) entirely — it assumes a ">95%" crude oracle and asks only how
to wire it to stocks. **(a) is the whole difficulty, and it is close to
impossible at the level claimed.** Even a *modest, real* (a) is then taxed twice
by (b) before it reaches a P&L (§7).

---

## 3. The lagged-beta result is NOT predictability — confront it head-on

The macro memo found the **lagged** crude spec (SPEC-L1: market at *t*, oil at
*t−1*) **stronger and broader** than the contemporaneous spec — 16 FDR survivors
vs 6, and a wider, cleaner economic list. A naive reader will see "yesterday's
crude predicts today's stock" and call it a forecasting edge. **It is not. It is
a clock artifact.**

- **Mechanism (non-synchronous timing).** NSE closes 15:30 IST. Brent/WTI settle
  *afterwards* (ICE/NYMEX run into the evening and overnight IST). So a chunk of
  "yesterday's" crude move is information that became public **after** the Indian
  cash market had already closed. The Indian stock cannot have reflected it
  yesterday; it reflects it at **today's open**. The lagged beta is the stock
  **catching up to already-public crude information**, not anyone forecasting the
  future. [FACT — exchange session times + the macro memo's own reading, §6/§9.]

- **The tell in the data.** Contemporaneous-vs-L1 crude-beta cross-sectional
  correlation is only **0.24** (macro memo §6) — the two are related but far from
  identical, exactly what a timing-overlap story predicts. And **SPEC-L2** (market
  *also* lagged) inflates the *whole* cross-section (t̄ = +1.097, macro memo §4):
  once you stop controlling contemporaneous market variance, lagged-oil just
  absorbs broad overnight/reversal structure. That is the artifact made visible —
  a warning, not a finding.

- **Why "catching up" is not a crude-forecasting engine.** Forecasting the chain
  the operator asked for requires predicting **tomorrow's crude move** and then
  the stock. The lag result requires predicting **nothing** — the crude move has
  *already happened and is public* by the time the Indian market opens. These are
  categorically different. Conflating them is precisely the error the memo must
  block.

- **What small, real thing the timing gap might be — and why even that is not
  ours.** The gap *is* a genuine micro-opportunity: at the NSE open, Indian
  crude-sensitive names must reprice to the overnight Brent move. But:
  (i) it is an **overnight-gap / opening-auction** phenomenon, not a
  crude-forecast; you are trading a *known* input, competing on **latency**, not
  insight;
  (ii) it is exactly the kind of stale-price drift that is **first to be
  arbitraged** — market-makers and index-arb desks close NSE opening gaps to
  global overnight moves as a matter of course;
  (iii) at β ≈ 0.08 the *expected* open-gap on a paints name from a 1% overnight
  Brent move is ~8 bps — **below the ~32 bps round-trip friction floor** (§7).
  So even the real thing is friction-dominated for anyone paying the retail/PMS
  statutory stack. This is a HFT-adjacent latency game, not a research family for
  a ₹100 Cr equity book, and it is **not authorized to be measured here** (any
  conditional open-gap return is a trial).

---

## 4. Efficient-markets baseline — you must beat the curve, not zero

Crude futures are one of the deepest markets on earth. OPEC+ decisions, EIA/API
inventory prints, and known geopolitics are priced **within minutes**. The
forecastable component of the *level* is therefore the **surprise relative to
consensus**, which is by construction small, and hard, and mostly not knowable
ahead of the print.

Two consequences the engine cannot escape:

- **The futures curve is the market's own risk-neutral forecast**, and it is
  **hard to beat out-of-sample.** The real-time forecasting literature (§6)
  finds the no-change random walk and the futures curve are stubborn benchmarks;
  models that beat them in-sample routinely fail to do so in true out-of-sample
  real time. [FACT — literature consensus, sources unverified this session.]

- **Therefore the engine must beat curve + random walk, not beat zero.** A model
  that is "right 55% of the time" is worthless if the curve is right 54% — the
  *increment* is what pays, and the increment is tiny and unstable. Any spec that
  scores a crude engine against "% directional right" rather than "increment over
  the curve, out-of-sample, net" is measuring the bull-regime illusion of §1.

This mirrors the program's own repeated lesson: **gross alpha was never the
constraint; the benchmark and the friction were** (killed legacy system; SRA;
`DIAG-BREAKOUT-ENTRY-0001`). A crude engine faces the *toughest possible*
benchmark (a liquid, arbitraged, curve-anchored market) before friction even
enters.

---

## 5. The unstructured-input trap — geopolitics and refinery news

The persona's most seductive inputs — "geopolitical factors," "refinery shutdown
news," OPEC headline-reading — are **exactly the data this program treats with
most suspicion**, for reasons the program has already paid to learn:

- **Look-ahead by hindsight.** You know which geopolitical events "mattered" only
  *after* the price moved. Building a signal on "supply shocks move crude" is
  unfalsifiable narrative: every large move gets a story attached post hoc, and
  the stories that *didn't* move price are forgotten. This is TRAP 6 (silence)
  wearing a geopolitical costume.

- **Point-in-time is the whole game, and it is the program's discipline already.**
  A refinery-outage or OPEC-headline signal is real **only if timestamped to when
  it became PUBLIC**, not when it physically happened or when a newswire
  retroactively flagged it as important. This is precisely the
  **filing-timestamp discipline** the program already enforces for Indian
  corporate announcements: BSE `DissemDT` ("became public at") vs `DT_TM`
  (submission), the Reg-30 hand-mapping, the ISIN join (see CURRENT STATE, OPEN
  OPERATOR DECISION 1). A crude news-signal without an audited public-time stamp
  is a look-ahead engine by construction — the same reason SRA Stage 2 and PEAD's
  CAR study are **blocked on the ToU ruling**. A crude-news engine would need its
  *own* equivalent PIT news corpus, which does not exist here and cannot be
  scraped (BINDING RULE, and the exchange-ToU blocker by analogy).

- **Narrative ≠ falsifiable signal.** The macro memo's own map deliberately
  *excluded* names whose story could be told either way (RELIANCE,
  specialty-chemicals, high-USD-debt metals) precisely to avoid "an unfalsifiable
  map in which every chemical name confirms the theory." A geopolitical crude
  engine is the unfalsifiable-map failure mode at the factor level.

**Conclusion:** the persona's qualitative inputs are a **conditioning aid for a
human who already holds a view** (§9), not a machine signal. As an autonomous,
backtestable engine input they are look-ahead-prone and un-PIT-able with the data
this program is allowed to touch.

---

## 6. Literature pass (tiered) — crude predictability, the curve, and oil→equity transmission

**Tiering** (per `analysis/QFM_literature_prior.md` convention): **[PR]**
peer-reviewed · **[WP]** working paper / preprint · **[VM]** vendor / broker /
practitioner marketing (**systematically biased toward positive claims** — never
cited as evidence for an effect).

**SESSION-HONESTY NOTE (TRAP 4 / "unverified").** This session's web-search and
web-fetch budget was **exhausted before this memo** (200/200 WebSearch used), and
the session scratchpad contains **no crude-specific PDFs** (it holds the QFM/PEAD
momentum corpus — Jegadeesh-Titman, Novy-Marx, Green-Hand-Zhang, Hou-Xue-Zhang,
TSM, Nagel — none on oil forecasting). **I therefore opened NO crude source this
session.** Every citation below is from domain knowledge and marked
**[unverified at source this session]**. The *directions* of these findings are
textbook and I am confident in them; I am deliberately NOT quoting specific
coefficients, R², or p-values I cannot re-open, because an unverifiable number is
exactly the invented number TRAP 4 forbids. Any spec built on this family must
re-fetch and read these sources digit-by-digit before freeze.

### 6.1 Crude predictability and the random-walk / curve benchmark

- **[PR] Alquist, Kilian & Vigfusson — "Forecasting the Price of Oil"** (Handbook
  of Economic Forecasting, 2013). Canonical survey. Core finding: the **no-change
  random walk is a stubborn benchmark**; most structural and futures-based models
  fail to beat it consistently out-of-sample at short horizons; where they help,
  it is modest, horizon-specific, and unstable. [unverified at source this
  session]
- **[PR] Baumeister & Kilian — real-time oil-price forecasting** (e.g.
  *J. Business & Economic Statistics* 2012/2015 and related). Emphasises the gulf
  between in-sample fit and **real-time out-of-sample** performance; some
  gains from combining models / inventories exist but are small and fragile.
  Directly refutes the ">95%" premise. [unverified at source this session]
- **[PR/WP] The futures curve as predictor.** The oil futures curve is the
  market's risk-neutral forecast; the consensus is it is **hard to beat** and is
  itself only a weak predictor of the subsequent spot change (roll yield /
  risk-premium debates). Any engine must beat *the curve*, not zero (§4).
  [unverified at source this session]

### 6.2 Oil → stock-return transmission (index level)

- **[PR] Driesprong, Jacobsen & Maat — "Striking Oil: Another Puzzle?"**
  (*J. Financial Economics*, 2008). The on-point paper: **oil price changes
  predict stock-market returns at the INDEX level** (a lagged, under-reaction
  effect across many countries). Two cautions that make it *weaker*, not
  stronger, support for the operator's idea: (i) it is a **market-timing** result
  (predict the index), not a cross-sectional stock-picking edge; (ii) subsequent
  work debates whether it **survives** out-of-sample, transaction costs, and data
  snooping — the standard fate of a predictive-regression anomaly. And critically
  it is the **lagged / under-reaction** channel — i.e. the *stock catching up to
  a past oil move* (§3), **not** a forecast of future oil. [unverified at source
  this session]
- **[PR/WP] Are oil betas priced?** The asset-pricing literature is **mixed** on
  whether an oil-exposure factor earns a risk premium; results are
  sample/specification-dependent. A priced, robust, tradeable oil factor in
  equities is **not** an established fact. [unverified at source this session]

### 6.3 India-specific oil–equity evidence

- **[WP/PR, thin]** Indian studies (oil-price ↔ Nifty / sectoral indices, often
  VAR / cointegration / GARCH) generally find **contemporaneous linkage and
  volatility spillover**, consistent with the macro memo's *exposure* finding,
  but **little credible out-of-sample directional predictability** net of cost.
  The literature here is thinner and lower-tier than the US/global work.
  [unverified at source this session — treat as directional prior only.]

**What the literature does NOT provide:** a single credible, out-of-sample,
cost-surviving demonstration that a public crude forecast picks the direction of
individual equities net of friction. The closest positive result (Driesprong et
al.) is an index-timing under-reaction effect — the §3 "catching up," not the §2
"(a) forecast future crude" — and is itself contested.

---

## 7. The double tax — friction + beta attenuation (the decisive arithmetic)

Any directional stock strategy pays **two** costs the crude forecast does not:

**Tax 1 — statutory friction (RULING 5, `src/costs_in.py`), not scaled by beta.**
Computed this session from the verified cost stack, delivery product, per round
trip (buy + sell, DP on the sell leg):

| Component | Round-trip cost |
|---|---:|
| **STT** (0.10% each side, delivery) | **20.0 bps** |
| Exchange txn + SEBI + stamp + GST + DP | ~2.4 bps |
| **Statutory total** | **~22.4 bps** |
| + Slippage floor (5 bps/side, liquid large-caps) | +10.0 bps |
| **Round-trip floor used here** | **~32 bps** |

STT is **~89% of the statutory total and is irreducible** — it is a government
tax on turned-over notional, identical to the wall that killed the legacy system
(gross ~18.5%/yr ≈ statutory cost ~19.7%/yr at 1.6 RT/day) and that returned the
`DIAG-BREAKOUT-ENTRY-0001` DO-NOT-BUILD. Ranks 201–1000 would carry a *higher*
slippage floor; the 32 bps here is the **generous** case (paints and large E&P
are liquid). [FACT — `costs_in.py`, RULING 5.]

**Tax 2 — beta attenuation, which scales the *edge* down but not the *cost*.**
The stock captures only **β_oil** of the crude move (market-adjusted). Using the
macro memo's validated STABLE / FDR betas:

| Name | β_oil (SPEC-C) | Break-even |E[crude move]| per round trip |
|---|---:|---:|
| HINDOILEXP | +0.110 | **2.95%** |
| BERGEPAINT | −0.089 | **3.64%** |
| VEDL | +0.086 | **3.77%** |
| ONGC | +0.082 | **3.95%** |
| ASIANPAINT | −0.080 | **4.05%** |
| PIDILITIND | −0.064 | **5.06%** |
| OIL | +0.052 | **6.23%** |

*Break-even = 32 bps ÷ β_oil = the NET, directional, above-benchmark crude move
the engine must forecast per round trip just to cover cost, before earning a
single basis point.* [FACT — arithmetic; betas from `macro_beta_diagnostic.md`
§6; friction from `costs_in.py`.]

**Read that against reality.** Daily Brent log-return σ ≈ ~2% (regime-dependent).
So on the **best-beta** name (HINDOILEXP) break-even needs a **~1.5σ expected
daily move**; on the flagship-clean paints pair it needs **~2σ of *expected*
(not realised) signed crude move per round trip.** An *expected* 2σ directional
move is not a forecast edge — it is a fantasy. The best real crude models
struggle to beat the curve by a *fraction of a σ* out-of-sample (§4, §6). **The
edge required to clear the double tax is one to two orders of magnitude larger
than the edge that plausibly exists.**

**The attenuation is the killer, and it is structural.** Expressing a crude view
through a stock is a **10–20× levered-DOWN, fully-taxed** vehicle: you pay 100%
of the friction on 100% of the notional to capture 5–11 cents on the dollar of
the crude move. There is no parameter tuning that escapes it — it is β < 0.11
meeting a fixed cost floor.

**The strictly-better expression makes the point.** The *same* crude directional
view expressed in **crude futures directly** has **β = 1** (it *is* crude) and a
far smaller friction/turnover profile (futures, no 20-bps STT-on-notional). If a
crude forecast edge existed, you would trade it in crude futures, not in a paints
stock — capturing 100% of the move instead of 8%. **That is a commodity
strategy** (MCX / term-structure — **SPEC-AG-01's territory**), **not an equity
overlay**, and it falls outside this repo's equity mandate. The equity chain is
the single *worst* place to express a crude view.

---

## 8. Crude as a single series — outcome-blind, FACTOR-only characterisation

This is the only quantitative work AMENDMENT A permits here: characterising
crude's OWN time-series predictability, conditioning **NO** stock return. I did
**not** run new computations against repo data this session (the study would be
purely on public Brent/WTI series and is optional); I report the **known
literature properties** of the series, flagged as such. Any future computation
here must stay strictly on the crude series — the instant a stock return is
conditioned on a crude signal, it is a TRIAL.

- **Return autocorrelation ≈ 0 at daily/weekly horizons.** Crude log returns show
  little exploitable linear autocorrelation short-horizon — the random-walk
  result. [FACT — literature; §6.]
- **Variance ratio ≈ 1 short-horizon.** Consistent with a near-random-walk in
  levels; mild mean-reversion appears only at long (multi-month/annual) horizons
  where an equity day-trade cannot act and where the futures curve already
  encodes the risk-neutral expectation. [FACT — literature; §6.]
- **Volatility IS forecastable; direction is NOT.** GARCH-family volatility
  clustering is strong and real — but **volatility is not direction**. A vol
  forecast sizes/hedges a position; it does not tell you which way crude goes.
  This is the honest, defensible crude-predictability finding, and it points at
  **risk management**, not directional alpha. [FACT — literature.]
- **The curve slope (contango/backwardation) has only a weak, contested relation
  to subsequent spot** — it is a risk-premium / roll-yield object, largely priced.
  [FACT — literature; §6.1.]

**Factor-only verdict:** crude's *level direction* is close to unforecastable
short-horizon by public information; its *volatility* is forecastable. The
forecastable part (vol) is the hedging/risk part, not the directional-alpha part
the operator asked for. This is the single-series confirmation of §1 and §4.

---

## 9. Relationship to the program (macro memo, killed legacy, AG-01, exposure-not-alpha)

- **To `macro_beta_diagnostic.md`.** This memo is the honest completion of that
  memo's §11 caveat. The macro memo validated the *exposure* and explicitly
  refused the *alpha* claim. This memo confirms the alpha claim fails — not
  because the betas are weak (they are strong) but because **the crude forecast
  half (§2 (a)) does not exist at the level claimed, and the double tax (§7)
  would kill even a modest edge.** The two memos agree: the betas are a
  **hedging / risk / conditioning** tool.

- **To the killed legacy system.** Same terminal diagnosis, different entry point.
  Legacy: real gross alpha (~18.5%/yr) **fully consumed by friction** at high
  turnover. Here: the crude→equity chain would have to *manufacture* a gross edge
  that the literature says is not there, and then survive the *same* STT wall.
  "Gross alpha was never the constraint; friction was" applies twice over.

- **To SPEC-AG-01 (MCX Silver / commodity carry).** This is where any legitimate
  crude directional view belongs — a **commodity** family, expressed in the
  commodity, β = 1, no equity-attenuation. AG-01 is a *carry / term-structure*
  family, not a directional-forecast family, and it is **already demoted and
  queued behind the 2-shadow cap** (RULING 12), with its own unresolved data
  blockers (MCX depth spike; the settlement-price circularity; the ToU ruling).
  A crude *directional-forecast* engine would be a *new* commodity family behind
  even AG-01 — and it inherits AG-01's every blocker plus the far harder
  "beat-the-curve" bar. **It does not jump the queue; it joins the back of it, if
  at all.**

- **Exposure-not-alpha, restated as the deliverable.** The four-decade crude
  analyst persona's real product is a **conditioning input** — a well-reasoned
  macro view that a *human* portfolio manager (who already holds a book) can use
  to tilt hedges or size risk. It is **not** an autonomous, backtestable,
  ">95%-accurate" signal generator, and this program's protocol (PIT,
  falsifiability, SPA-gated trials) is built precisely to reject the latter
  framing.

---

## 10. Is there ANY narrow defensible path? (Yes, but not here and not now)

Being fair rather than dismissive: a defensible research question *does* exist —
but it is **not** the operator's equity-overlay engine.

- **What it is:** a **crude (or crude-curve) directional/return forecasting study
  in the commodity itself**, scored **out-of-sample against the futures curve +
  no-change random walk**, at a **horizon slow enough to matter** (weekly/monthly,
  where mild mean-reversion and inventory/positioning signals have their best —
  still small — shot), expressed in **crude futures** (AG-01 space), net of
  commodity friction.
- **Benchmark it must beat:** curve + random walk, out-of-sample, net — **not
  zero, not "% right."** Pre-stated null: *a public-information crude forecast
  does not beat the curve out-of-sample net of cost* (the honest prior is that
  this null survives).
- **Governance path before any return may be observed** (none of which this memo
  authorizes): (1) a **drafted spec** with that pre-stated null and a
  curve-relative scoring rule; (2) **hash-freeze** (`spec_guard`); (3) a **shadow
  slot** — **both are currently held (QFM, PEAD)**; (4) a **registered trial**,
  SPA-gated (RULING 7). And it belongs in the **AG-01 / commodity** track, behind
  AG-01's own blockers, not in the equity pipeline.
- **Why not now:** it displaces nothing it could beat. QFM and PEAD hold the
  slots; AG-01 is ahead of it in the commodity queue; the equity-overlay version
  is dead on §7 arithmetic. The **equity chain specifically is refused**; the
  commodity version is *parked behind AG-01*, not endorsed.

**This memo authorizes none of the above.** It scopes the path only so the "no"
is a reasoned position, not a reflex.

---

## 11. Proposed register row (TEXT ONLY — operator to enter; this memo does NOT write it)

Consistent with the `DIAG-BREAKOUT-ENTRY-0001` precedent (an outcome-blind
DO-NOT-BUILD scoping row, no trial spent). Suggested fields:

```
trial_id:    DIAG-CRUDE-FORECAST-0001
date:        2026-07-23
family:      MACRO_EXPOSURE   (same family as DIAG-MACROBETA-0001; NOT a new spec family, consumes NO shadow slot)
description: Feasibility/scoping of a crude-oil directional forecast engine chained onto the DIAG-MACROBETA-0001 crude betas to trade Indian equity direction (operator question 2026-07-23, ">95% accurate" framing).
data_tier:   n/a
result:      DO-NOT-BUILD (equity overlay); commodity-futures version PARKED behind SPEC-AG-01.
notes:       OUTCOME-BLIND, NO TRIAL SPENT (cumulative trial count UNCHANGED at 53), NO SHADOW SLOT, no repo outcome data conditioned on any crude signal, no spec drafted, no hash frozen, no broker/Kite call, no scraping (web-search budget exhausted; NO crude source opened this session - all citations marked unverified-at-source). Analysis: analysis/crude_forecast_engine_feasibility.md. FINDINGS: (1) the ">95% accurate" premise is REJECTED - no public crude model achieves it; short-horizon crude direction ~ random walk; a 95% belief = in-sample fit, the free bull-regime "up" call, or hindsight recall (TRAP 4 invented number). (2) DIAG-MACROBETA-0001's betas are EXPOSURE not alpha (its own §11); a tradeable chain needs BOTH (a) crude direction forecastable OVER THE FUTURES CURVE out-of-sample AND (b) survival of transmission net of friction - the macro memo settled only the transmission channel, not (a). (3) The stronger LAGGED crude beta (SPEC-L1 16 survivors vs SPEC-C 6) is NOT predictability - it is the non-synchronous-timing signature (NSE closes 15:30 IST before Brent settles), the stock CATCHING UP to already-public crude news at the next open; C-vs-L1 beta corr only 0.24; the tiny real open-gap opportunity is a latency game, friction-dominated (~8 bps expected gap at beta 0.08 vs ~32 bps round-trip), and NOT ours. (4) DOUBLE TAX: stock captures only beta_oil 0.05-0.11 of the crude move while paying an unscaled ~32 bps round-trip floor (statutory 22.4 bps, ~89% irreducible STT, per costs_in.py/RULING 5, + 5 bps/side slippage); break-even needs a NET directional crude move of 2.95% (HINDOILEXP) to 6.23% (OIL) per round trip - ~1.5-2 sigma of EXPECTED daily crude move - one-to-two orders of magnitude above any plausible edge. (5) A crude view is STRICTLY BETTER expressed in crude futures (beta=1, no attenuation) = SPEC-AG-01 commodity territory, not equity. (6) Literature (Alquist-Kilian-Vigfusson; Baumeister-Kilian real-time; Driesprong-Jacobsen-Maat index-level oil->stock UNDER-REACTION, contested OOS; oil-beta-priced debate MIXED; India oil-equity thin) - all UNVERIFIED AT SOURCE this session, directions only, no numbers quoted. LEGITIMATE USE of the betas = risk management/hedging/factor-neutralisation + conditioning input for an existing macro view (crude vol IS forecastable; crude DIRECTION is not). Any narrow defensible path = crude/curve OOS forecasting in the commodity itself, scored vs curve+random-walk, weekly/monthly, in AG-01 space behind AG-01's blockers - requires drafted spec + pre-stated null + hash-freeze + a shadow slot (BOTH HELD) + a registered SPA-gated trial; THIS MEMO AUTHORIZES NONE OF IT.
```

---

## 12. Open items that must close BEFORE any crude spec could be drafted

1. **DSR reporting band** (RULING 7, proposed 0.35/0.50/0.70 — still PENDING):
   any future scoring inherits this.
2. **A shadow slot must free up.** Both are held (QFM, PEAD). A commodity crude
   family also queues behind **AG-01**.
3. **AG-01's own blockers first** (this family sits behind it): MCX depth spike;
   the **settlement-price circularity** (no independent settle column — measuring
   MCXCCL's own carry assumption); the **exchange-ToU ruling** (OPEN OPERATOR
   DECISION 1).
4. **A PIT crude-news corpus** would be required for any "geopolitics / refinery"
   input — public-time-stamped, falsifiable, un-scrapeable here (§5). Does not
   exist; likely infeasible under current rules.
5. **Re-fetch and read every §6 source digit-by-digit** before freeze — nothing
   in §6 was opened this session; all citations are directional priors only
   (TRAP 4).
6. **A curve+random-walk out-of-sample benchmark harness** would have to be built
   and pre-registered — scoring "% right" is the bull-regime illusion (§1, §4).

---

## 13. Verdict (recap)

**DO NOT BUILD the equity-overlay crude forecast engine.** The ">95%" premise is
false (§1); the validated betas are exposure, not alpha (§2, and the macro memo's
own §11); the stronger *lagged* beta is timing catch-up, not forecasting (§3);
crude must beat the *curve* not zero and barely can (§4, §6); the qualitative
geopolitical inputs are look-ahead-prone and un-PIT-able here (§5); and the
**double tax** (β-attenuation × unscaled ~32 bps friction) demands a 3–6%
per-round-trip crude edge that does not exist (§7, §8). The legitimate product of
the validated betas — and of the crude-analyst persona — is
**hedging / risk / factor-neutralisation and human conditioning**, not an
autonomous directional oracle. Any genuine crude directional view belongs in
**crude futures (AG-01 space)**, behind AG-01's own queue and blockers, not in an
Indian-equity book.

**NO TRIAL SPENT. Cumulative trial count unchanged at 53. No shadow slot. No spec
drafted. No repo outcome data conditioned on any signal. No broker call. No
scraping.**

# SPEC-AG-01 — is a carry / term-structure study on MCX Silver viable in principle?

**Date:** 2026-07-21
**Status:** DESK ANALYSIS. Outcome-blind. **No trial spent, no backtest, no return
series computed, no MCX endpoint touched, no data fetched from any exchange.**
**No governance file edited.** Written against facts already recorded in
`CLAUDE.md` / `governance/DECISIONS.md` plus general public knowledge of
commodity-futures microstructure.

**Conventions:** claims are tagged **FACT** (recorded in this repo or a primary
source), **ASSUMPTION** (reasoned, unverified), or **UNKNOWN** (explicitly not
established). Per TRAP 6, gaps are stated, never silently omitted.

---

## 0. VERDICT (read this first, per TRAP 2)

**SPEC-AG-01 as conceived — a carry / term-structure study built on MCX bhavcopy
`Close` across contract months — is NOT VIABLE AS SPECIFIED.**

It fails on **two logically independent grounds**, and only one of them is the
circularity the operator flagged:

- **(A) Circularity — UNRESOLVED, and cheaply resolvable.** Whether the far-month
  mark is trade-derived or model-derived is currently an ASSUMPTION in `CLAUDE.md`
  ("MCXCCL *may* mark an illiquid far month FROM the spread"), not a FACT. It can
  be settled to FACT **for free, from published methodology documents, without
  touching a data endpoint**. Nobody has done this. It is the highest-value next
  action in this file.
- **(B) Statistical power — FATAL EVEN IF (A) RESOLVES FAVOURABLY.** The one design
  that cleanly escapes the circularity (§3.ii, the roll-window traded spread)
  yields an effective sample of roughly **48–114 independent roll episodes** over
  the entire 2015→2024-07-16 development window, against a deflation charge of
  52+ cumulative trials and a Hansen SPA gate that will correctly see through the
  within-episode autocorrelation. **(B) does not depend on (A) at all.** A perfect
  answer to the circularity question probably does not save the family.

**Ground (B) is the more important finding and it is new.** The circularity is
the interesting problem; the sample size is the disqualifying one.

**On the depth spike: DO NOT CANCEL — RE-SCOPE, RE-ORDER, RE-GATE.** Cancelling
would kill the family on an ASSUMPTION, which is the same governance error as
proceeding on one. But the spike as currently specified ("one browser-driven
fetch of a 2015 and a 2010 date") verifies the **wrong thing**, and the thing it
verifies is worth ~22% on a t-statistic while the unverified thing is binary and
existential. Full recommendation in §5. Net effect: the re-scoped spike is
**cheaper** than the original (1–2 dates, not a depth sweep, and the 2010 fetch
is dropped), and it comes **after** two free steps and after the ToU ruling.

---

## 1. THE CIRCULARITY, STATED PRECISELY

### 1.1 What is being inferred

Let `F_t^(T)` be the true (unobserved) fair futures price at date `t` for the
contract expiring `T`. The cost-of-carry identity:

```
F_t^(T) = S_t · exp( (r_t + u_t − y_t) · (T − t) )
```

with `r` = financing rate, `u` = storage + insurance + (for India) the import-duty
/ GST / freight parity wedge, `y` = convenience yield. Silver is a hybrid
precious/industrial metal, so `y` is not pinned at zero and *is* the economically
interesting quantity — the thing a carry study wants to extract.

The study's target is the term-structure slope between two listed months:

```
c_t = ln( F_t^(T2) / F_t^(T1) ) / (T2 − T1)          [annualised implied carry]
```

and then some signal built on `c_t` (its level, its change, its deviation from a
fitted fair carry, its seasonality).

### 1.2 What is actually observed

The study never sees `F`. It sees `P_t^(T)` — the bhavcopy `Close` column, which
per **FACT** (`CLAUDE.md`) is *the only mark in the file; there is no settlement-price
column*. The mark-generating process has (at least) two regimes:

- **Traded regime:** the contract traded with two-sided flow near the close, so
  `P_t^(T) = F_t^(T) + ε_t`, `ε` = microstructure noise (bid-ask bounce, last-trade
  timing). Contains information.
- **Non-traded regime:** the contract did not trade, but a mark must still be
  published for margining and mark-to-market. The clearing corporation computes
  one. The standard construction (**ASSUMPTION**, this is the thing §5 says to
  verify) is

  ```
  P_t^(T2) = P_t^(T*) · exp( ĉ_t · (T2 − T*) )
  ```

  where `T*` is the active month and `ĉ_t` is **the clearing corporation's own
  carry parameter** — a theoretical basis, or the last observed traded spread
  carried forward.

### 1.3 The exact point of tautology

Substitute the non-traded mark into the study's estimator:

```
ĉ_t^obs = ln( P_t^(T2) / P_t^(T1) ) / (T2 − T1)
        = ln( P_t^(T1) · exp(ĉ_t·(T2−T1)) / P_t^(T1) ) / (T2 − T1)
        ≡ ĉ_t
```

The identity is **algebraic, not approximate**. Under the non-traded regime the
study recovers the exchange's input parameter from the exchange's own output,
exactly, with zero residual. The estimator is not noisy — it is *empty*.

**Why this is dangerous rather than obviously wrong:** the resulting series will
be beautifully behaved — smooth, low-variance, strongly autocorrelated,
economically plausible in level. It will *look like the best-measured quantity in
the program*. And it will not be exactly constant either, because `ĉ_t` itself
moves — with policy rates, with import duty, with the last liquid spread — so it
will exhibit genuine time variation and will correlate weakly with real
macro variables. **A regression on it returns a non-zero R².** That R² measures
MCXCCL's operational marking policy. This is the program's characteristic failure
mode (**TRAP 6: the failure is SILENCE, not error**) in its purest form: an
impressive number, produced by a pipeline that ran cleanly, measuring nothing.

### 1.4 The part that is worse than the binary framing

The circularity is **not** a clean two-regime switch. Define `λ_t^(T) ∈ [0,1]` as
the weight of genuine trade information in the mark. Then

```
ĉ_t^obs = λ_t · c_t^true + (1 − λ_t) · ĉ_t^model + noise
```

Three properties of `λ`, in ascending order of severity:

1. **`λ` is unobservable from the bhavcopy.** The file does not say how the mark
   was made.
2. **`λ` is time-varying.**
3. **`λ` is ENDOGENOUS TO THE SIGNAL.** Far-month liquidity collapses precisely in
   stressed, dislocated, high-carry-volatility states — i.e. `λ → 0` exactly when
   `c^true` is doing something interesting, and `λ → 1` in quiet markets when
   carry is doing nothing. The measurement error is therefore not classical, not
   mean-zero, and **systematically pulls the observed series toward the model in
   exactly the states the study exists to detect.**

Consequence: a finding of the form *"carry mean-reverts"* or *"carry dislocations
correct"* is partially the statement *"MCXCCL's mark reverts to its model when
volume dries up."* Property 3 is the reason a simple errors-in-variables
correction cannot rescue this: there is no attenuation factor to divide out,
because the contamination is state-dependent.

### 1.5 A second, independent measurement defect: asynchrony

Separate from the derivation problem, and additive to it. MCX runs a long session
(to ~23:30/23:55 IST). **`Close` is a last-trade price, not a closing-window VWAP**
(**FACT** as recorded: no settlement column; **ASSUMPTION** that `Close` = last
traded price rather than a computed daily settlement — see §5 step 1, this is a
documentary question). For a *spread* between two contracts:

- leg A's last trade may be at 23:25,
- leg B's last trade may be at 19:40 or on a previous session,

and the measured spread absorbs the entire spot move between those two stamps.
For silver, an intraday move of 0.5–1.5% is unremarkable; an annualised carry is
of order a few percent. **The asynchrony noise can exceed the signal by an order
of magnitude, and it is not mean-zero** (it is a function of intraday drift and of
which leg is stale, which is itself a liquidity variable). This defect afflicts
even genuinely-traded contract pairs and is invisible to any volume filter.

---

## 2. IS IT SEPARABLE? ASSESSING THE PROPOSED FLAG

The flag recorded in `CLAUDE.md`:

> flag `volume==0 AND close==PCP` (stale) separately from `volume==0 AND
> close!=PCP` (spread-derived, not independent evidence)

**Assessment: it does not partition. It is a necessary lower bound on
contamination, not a classifier.** It correctly identifies contamination it can
prove; it cannot certify the complement as clean. Its true output is
`{provably not independent}` vs `{unknown}` — never `{independent}`.

### 2.1 What it fails to catch (false "clean")

**(a) THIN GENUINE VOLUME — and specifically, calendar-spread execution. This is
the most important miss.**
A contract trades 5 lots. Non-zero volume, so it passes both arms of the filter.
But on any exchange offering calendar-spread order entry (**ASSUMPTION** that MCX
does for silver — unverified, and see §5), a spread trade is executed *as a
spread* and then **reported as two outright legs, with the far leg's printed price
constructed as near-price + negotiated spread.** The printed far-month price is
then not an independent price-discovery event; it is arithmetic on the near price.

This is the circularity **reappearing inside genuine, non-zero volume**, and
**no volume threshold at any level catches it**, because the contamination is not
monotone in volume — a heavily-traded roll week is *dominated* by spread trades.
The proposed flag is blind here by construction.

*(Note the sign flip in §3.ii: once you stop treating the far outright as the
observation and treat the traded spread itself as the observation, this same
mechanism becomes the salvage rather than the defect.)*

**(b) A single print with non-zero volume.** `open == high == low == close` with
`volume > 0` means one trade, not a price *range* — no two-sided discovery, no
information about where the other side was. The proposed filter passes it. This
repo has already paid for exactly this shape: **the C1-52WH-0001 defect was 33
yfinance holiday placeholders with flat OHLC and volume 0** (TRAP 1). Same
fingerprint, non-zero volume.

**(c) Stale marks carrying non-zero volume.** A contract trades once at 10:05 and
never again; the 23:30 `Close` is that 10:05 print. Volume > 0, `close != PCP`,
and the filter calls it clean — but the mark is stale in the only sense that
matters (it is not contemporaneous with the other leg). Volume > 0 does **not**
mean the mark is current. This is §1.5 wearing the filter's blind spot.

**(d) Jobber quoting off theoretical carry.** An arbitrageur quotes the far month
at spot + their own cost of carry and gets hit. Volume > 0, genuinely traded, and
economically this *is* a market price — arguably the honest one. But it is one or
two participants' funding cost, not a market-wide equilibrium. Philosophically
admissible; it has a hard **capacity** consequence (§4.4) that must be disclosed
rather than assumed away.

### 2.2 What it mis-labels (false "spread-derived")

**(e) `volume==0 AND close!=PCP` need not be spread-derived.** The mark may be
rolled forward from the *spot / near-month move* rather than from an inter-month
spread — i.e. `P_t^(T2) = P_{t−1}^(T2) · (S_t / S_{t−1})`. That also produces
`close != PCP`. It is a **different** contamination and, for a carry study, a
**worse** one: it holds the implied carry *exactly constant by construction*, so
the study would conclude "carry is remarkably stable" as a pure artifact. The
proposed label is wrong about the mechanism, which matters because the two demand
different diagnostics.

**(f) The `close == PCP` "stale" bucket is the SAFE one.** If the mark is
unchanged, the *change* is exactly zero and any change-based estimator can
identify and discard it trivially. The dangerous buckets are (a) and (c) —
non-zero volume, moving marks, no independent information.

### 2.3 Free diagnostics that DO discriminate

All of these are outcome-blind, therefore **free** under `CONTAMINATION_POLICY.md`
AMENDMENT A (timestamp/PIT audits, capacity math). None requires a return series.

1. **The cross-contract common-implied-rate test — decisive, needs ONE date.**
   Compute `ĉ` between the near month and *each* far month listed on a single day.
   If the far months are traded, the implied rates will disperse (different
   liquidity, different roll pressure, different rounding). **If three or more far
   months share a single common implied rate to within a tick, that is the
   signature of one model parameter generating all of them.** This converts §1's
   epistemics into a one-day empirical test. It is the single highest-information
   observation available and it requires no depth at all.
2. **Open Interest, not volume, as the relevance filter.** The bhavcopy carries OI
   (**ASSUMPTION** — verify per §5). OI is strictly better than volume for this
   job: a contract with OI ≈ 0 has no economic stake and its mark is irrelevant; a
   contract with meaningful OI and zero volume is *precisely* the case that forces
   the exchange to model. OI also yields the only non-arbitrary definition of the
   active pair (§2.4) and of the roll window (OI migration date).
3. **Number of trades**, if available. Volume 500 in one print and volume 500
   across 60 prints are different animals and the proposed filter cannot tell them
   apart. This field is a likely vendor-only extra (§6).
4. **Rounding-residue structure.** A model-derived mark lands on a tick-rounded
   model value; a traded price lands where the book was. Histogram of the last
   digit differs. Weak individually, free, and corroborative.
5. **Piecewise-constant runs.** Does `ĉ_t^obs` hold a literally identical value
   across a run of sessions and then jump? That is a re-marking schedule, not
   carry news.

### 2.4 Is a volume threshold defensible, and how to pre-register it?

**A volume threshold is defensible ONLY as a RELEVANCE / TRADEABILITY filter,
never as a CONTAMINATION filter.** §2.1(a) and (c) show contamination is not
monotone in volume in the way a contamination filter would require. Using it as
one would be exactly the invented-number liability the program forbids (TRAP 4).

If a threshold is used for tradeability, pre-register it from a source that
**cannot be tuned on outcomes**, in this order of preference:

1. **Best — a scale-free RANK rule, no threshold at all:** *"the two listed
   contracts with the highest open interest on date t."* No level to tune; it
   survives the SILVER / SILVERM / SILVER100 contract-size regime changes without a
   units decision (§4); and it is the natural definition of "the active pair."
2. **Second — anchor the level to CAPACITY, an economic constant fixed before
   any data is seen:** required daily volume = (intended sleeve notional) /
   (contract value) / (acceptable participation rate). This is derived from the
   *fund's* size, not from the *data's* distribution. It is unfalsifiable-by-tuning
   because changing it means changing the fund.
3. **Third — an exchange-published liquidity criterion**, if one exists
   (**UNKNOWN**).

And, regardless of choice:

- **Pre-register a SENSITIVITY LADDER in the spec** (e.g. ×0.5, ×1, ×2) with a
  requirement to report every rung. A threshold that works at exactly one setting
  is visibly fragile, and this makes the fragility unhideable. Per the program's
  own **TRIAL ECONOMICS corollary**, each rung is a cheap marginal trial (~0.3% on
  the deflation bar) — there is no economic excuse for omitting the ladder.
- **The specific trap to name in writing (TRAP 3):** it is possible to believe
  you are outcome-blind while tuning the threshold on *series smoothness*, on
  *autocorrelation*, or on *how clean the carry curve looks*. Those are
  outcome-adjacent. Fix the threshold before contact, in the spec, in writing —
  the one time this program pre-committed an inference parameter, the measured
  value came out **against** the family under test. That is the discipline working.

---

## 3. IS THERE A SALVAGEABLE STUDY?

Assessed against two questions: **does it escape the circularity**, and **what
does it cost in power**? Power is quantified against the dev window
2015-01-01 → 2024-07-16 = **9.54 years** (`CLAUDE.md`: 2015 is the defensible
floor; the seal cutoff is 2024-07-17).

**Expiry-count ASSUMPTION used throughout, flagged because it drives every N
below:** MCX SILVER (30 kg) is understood to list ~5 expiries/year (Mar, May, Jul,
Sep, Dec). **UNVERIFIED.** If the cycle is monthly, multiply the episode counts by
~2.4. Both figures are carried as a range rather than a point, per the
`F&O-count` precedent in DECISIONS.md (2026-07-20).

### (i) Restrict to the two most active contract months

**Escapes: PARTIALLY, and only during part of the year.**

Gains: removes the pure-model far months, which is the largest single win.
Does **not** remove: the calendar-spread execution channel §2.1(a); the asynchrony
channel §1.5; and — critically — **outside the roll window the second contract is
itself thin**, so "two most active" silently degrades to "front month + a modelled
second month" while the selection rule continues to return two contracts every
single day. **This is TRAP 6 in a new suit: the rule always succeeds, so it always
looks like it worked.** `C1-52WH-0001` printed `ranked 0` three times and nobody
read it.

**Mandatory guard, by direct analogy to `backtest_52wh.min_ranked_frac`:** report
per date the second leg's volume, OI and trade count, and **hard-stop** when the
fraction of dates with a genuinely two-sided second leg falls below a
pre-registered floor. Not a warning — a raised exception.

Power cost: the term structure collapses to a **single slope point**. All
curvature hypotheses die here. Usable sample shrinks toward the roll windows —
see (ii).

**Verdict: survives only as (ii) plus a starvation guard. Not independently useful.**

### (ii) Near-month roll only, where volume is genuinely two-sided — **THE STRONGEST SURVIVOR**

**Escapes: YES, and cleanly — but only under a reframing that must be made
explicit.**

The reframing is the analytic core of this memo. During the roll, both legs trade
with real two-sided flow *and the calendar spread is itself heavily traded*. So:

> **Measure the traded calendar SPREAD as the observation. Do not measure the
> ratio of two outright marks.**

This inverts §2.1(a). If the spread is a directly quoted and traded instrument,
then **it is an independent market observation in its own right, and it remains
one regardless of whether the far outright print was constructed from it.** The
derivation runs *from* the spread *to* the outright, not the reverse — so
observing the spread is observing a price, not recovering a model parameter. The
circularity is genuinely, not cosmetically, escaped.

**Hard dependency, and this is what the spike must actually check (§5):** you
cannot obtain traded-spread prices from a bhavcopy unless **MCX publishes
calendar-spread instruments as their own rows with their own volume and OI**.
**UNKNOWN.** If spreads are only ever reported as two decomposed legs, you are
back to inferring the spread from two asynchronous outright marks and (ii)
degrades to (i).

Power cost — **this is where the family dies even in its best case**:

| quantity | ~5 expiries/yr | ~12 expiries/yr |
|---|---|---|
| roll episodes over 9.54 yrs | **~48** | **~114** |
| sessions per episode with two-sided second leg (ASSUMPTION ~10–15) | ~480–720 | ~1,140–1,710 |
| **effective independent observations** | **~48** | **~114** |

The daily observations within one roll window are near-perfectly autocorrelated —
carry is a slow, near-deterministic function of time-to-expiry and rates — so the
raw session count is **not** the sample size. The **roll episode** is the unit of
independent information.

The good news, governance-wise: `src/metrics.py`'s Hansen SPA uses a
**Politis–Romano stationary bootstrap**, which will *see* that autocorrelation and
price it correctly. The program's own inference machinery will not be fooled by
the session count. That is good news for the register and bad news for AG-01: a
family with ~48 independent observations, charged against 52+ cumulative trials,
needs an enormous effect to clear SPA at p ≤ 0.10 net of friction.

**Second confound to pre-register, not a defect:** roll-window spreads embed
**roll pressure** (the documented index-roll / calendar-roll effect) as well as
cost-of-carry. These are different economic phenomena that happen to be measured
at the same moment. The spec must state which one is the hypothesis before
contact.

**Verdict: SURVIVES the circularity. Probably dies on N.**

### (iii) Reframe from carry-LEVEL to carry-CHANGE

**Escapes: NO — not alone, and it can make things strictly worse.**

Differencing removes a *constant* model bias. MCXCCL's model bias is **not
constant** — it moves with policy rates, with import duty, and with the last
observed spread. Worse, differencing a model-generated series produces a
characteristic signature: **long runs of near-zero change punctuated by jumps on
the sessions when the model input is refreshed.** Those jumps are **re-marking
events, not carry news**, and a change-based signal keys on exactly them.

The variance decomposition runs the wrong way: true daily carry change is *small*,
the re-mark jump is *large*, so differencing **raises** the artifact's share of
total variance. This is the design most likely to produce a spectacular,
completely spurious result.

The flip side is real and should be recorded: carry **change** is the correct
economic *target* — the carry *level* is dominated by the deterministic `r + u`
term and by India's duty/GST parity wedge, neither of which is tradeable alpha. So
**(ii) + (iii) composed is the coherent design; (iii) applied to raw bhavcopy
marks is a trap.**

**Verdict: survives ONLY as a transform applied to (ii)'s output. Never on raw marks.**

### (iv) Seasonality on active-contract prices alone, no term structure

**Escapes the circularity: YES, completely.** The front contract's `Close` is a
traded price. Nothing is derived. Clean.

**But it is no longer SPEC-AG-01.** It is a single-series commodity
seasonality/momentum study. Say that plainly rather than letting the family
survive under its old name with a different hypothesis — that substitution is how
specs quietly become unfalsifiable.

And it inherits three problems, the third of which is disqualifying:

1. **Splice hazard.** A continuous front-month series requires a roll and an
   adjustment convention (ratio- vs difference-adjusted vs unadjusted), and these
   give different answers. `CLAUDE.md`'s **never splice SILVERM across Feb-2012**
   is a *specific instance* of this general hazard, which should tell you the
   general hazard is live. Convention must be pre-registered.
2. **N is not merely small, it is unusable.** A monthly seasonal over 9.54 years
   has **9 or 10 observations per calendar month.** That is not a testable
   hypothesis; it is a picture. Every published commodity-seasonality result at
   this sample size is data mining, and SPA against 52+ cumulative trials will —
   correctly — kill it. **(iv) escapes the circularity by adopting a design that
   cannot clear the program's own inference bar.**
3. **AMENDMENT C bites hardest here, and this is the disqualifying point.** The
   Tier 3-adjacent Silver ML engine (`INHERITED-SILVER-0001`, **ESTIMATE ≥8
   unregistered trials**, four model families × ≥2 fit/tune cycles) was fitted **on
   this very series.** A seasonality study on MCX silver front-month prices is not
   merely adjacent to a contaminated engine — it is *the same data the engine
   already iterated over*. AMENDMENT C forbids merging the engine's forecasts;
   it cannot un-contaminate the **operator's priors about which seasonal patterns
   exist in MCX silver**, which is precisely what those ≥8 trials purchased. Any
   (iv) design must charge deflation against 52 + ≥8 silver-specific + an
   unrecorded number of informal looks.

**Verdict: escapes the circularity and is nonetheless the WORST-positioned design
in the program** — clean measurement, unusable sample, and the heaviest prior
contamination of anything on the queue. Additionally: silver is dominated by a
single global driver (COMEX silver × USDINR, plus duty), so an "MCX silver
seasonality" study is substantially **a USDINR-and-import-duty study wearing a
silver hat**. The genuinely Indian component lives in the *basis* — which is the
contaminated object from §1. Circular again, one order removed.

### (v) Abandon term structure entirely

**Escapes: trivially yes.** AG-01 dies as a carry family.

Cost: the family. But the correct question is what the queue slot is worth, and
here there is a **positive externality worth naming as a decision consequence**:

**AG-01 currently sits AHEAD of SPEC-52WH-01 in the queue while having no frozen
spec, no data, an unresolved ToU blocker, no cost stack (§4.3) and — per this
memo — a power problem.** 52WH has a fully built Stage 1–5 stack, a frozen spec,
a diagnosed defect with committed fixes, and a pending authorised decision (C1
attempt 2). **Leaving AG-01 ahead in the queue is costing the program real time
for an option with a low probability of ever being exercised.**

**Verdict: the null is more attractive than it looks, and it is free.**

### Ranked summary

| design | escapes circularity? | effective N | verdict |
|---|---|---|---|
| (ii) roll-window **traded spread** | **YES** (conditional on spread rows existing) | ~48–114 episodes | best-in-class; probably dies on N |
| (i) two most active months | partially | ≈ (ii) | only as (ii) + starvation guard |
| (iii) carry-change | **NO** alone; amplifies artifact | ≈ (ii) | only as a transform of (ii) |
| (iv) seasonality, no term structure | YES | ~9–10 obs/month | fails power **and** AMENDMENT C |
| (v) abandon | trivially | — | free; unblocks 52WH's queue position |

---

## 4. RESPECTING THE RECORDED CONSTRAINTS

### 4.1 Contract and units constraints — and one that bites *specifically* on a spread study

- **SILVER (30 kg) is the clean spine.** Correct, and (ii) reinforces it: the spine
  should be whichever contract carries the two-sided roll, and concentrating on
  one contract family avoids cross-family unit reconciliation entirely.
- **Never splice SILVERM across Feb-2012.** Respected — and §3(iv).1 notes this is
  an instance of a general hazard, not a one-off.
- **SILVER100 quotes per 10 g (100×).** **This constraint is far more dangerous in a
  spread study than in a level study.** A units mismatch between two *legs* of a
  spread does not shift a level by a known factor — it produces a spread that is
  wrong by ~100×, which will present as an *enormous, thrilling carry signal*.
  **Required guard:** assert at load that every leg of a constructed spread shares
  quote basis **and** lot size, and **hard-fail** otherwise. Per TRAP 6, this must
  raise, not warn.
- **Exclude 30 Mar – 30 Apr 2020**, and **disclose the direction of the exclusion —
  it is not neutral.** That window is COVID-era truncated/suspended MCX sessions,
  and simultaneously the period when global precious-metals carry *genuinely*
  dislocated (the London/COMEX EFP blow-out). So the exclusion removes both the
  bad data **and** the single most informative carry event in the dev window. The
  write-up must say so; a silently-applied exclusion that removes the hard cases
  flatters the family.
- **Contract master 2004–2027 is a MASTER, not price depth.** The master says which
  contracts *existed*. Depth of retrievable *prices* is the **UNKNOWN**, and per §5
  it is the less important unknown.

### 4.2 AMENDMENT C — and an enforcement gap

`AMENDMENT C` bars the Silver ML engine's forecasts from being merged into or used
to filter SPEC-AG-01. Respected throughout: nothing in this memo uses, cites or
assumes any output of that engine.

**Enforcement gap, flagged not resolved:** if the ML engine's feature set already
included carry / term-structure inputs, then AG-01's features are not merely
*adjacent* to a contaminated engine — they may be a **subset of what that engine
already iterated on across ≥8 trials**, which would materially change AG-01's
correct deflation charge. Establishing this is a free, outcome-blind check
(*read a feature list, run nothing*), **but I have not performed it**: the engine
is not in the frozen clone (`~/vendor/legacy-engine` contains only a chart file
matching `MCX`), and if it lives in the production tree it is off-limits under
**BINDING RULE 1**, which permits read access only for the HEAD SHA and for
cloning. **This is an operator question, not an agent action.**

### 4.3 A constraint that is NOT yet recorded: AG-01 has no cost stack

**FACT:** `src/costs_in.py` is an **NSE cash-equity** stack (STT, DP charges,
delivery/intraday stamp duty, NSE transaction charges). **RULING 5 does not cover
commodity futures.** MCX futures carry a structurally different friction set —
CTT on the sell side of non-agri futures, MCX transaction charges, GST, a
different stamp schedule, no DP charge, plus **roll costs and margin funding**,
which for a carry trade are not incidental but *are the trade*.

This matters disproportionately here: **a carry edge is measured in a few basis
points of an annualised spread.** Friction is proportionally enormous relative to
signal, far more so than in the equity families. Per the roadmap's own bottleneck
lesson — *gross alpha was never the constraint; friction was* — **a commodity
friction stack is a prerequisite for AG-01, not a downstream detail, and it does
not exist.** Add it to the family's blockers.

### 4.4 Capacity — free under the policy, and potentially decisive on its own

`CONTAMINATION_POLICY.md` AMENDMENT A lists **capacity math** as an explicitly
free, outcome-blind diagnostic. It should be run **before** anything else is
spent, and it may kill the family without any of §1–§3 mattering:

> The fund target is **₹100 Cr**. A calendar-spread position must be expressible in
> the *second* contract's open interest. If MCX silver's second-month OI is small
> (§2.1(d): the far-month price may be set by one or two jobbers), then **a ₹100 Cr
> book cannot express this trade at all**, and the family fails Phase 3's "must
> survive its own footprint" test regardless of whether the signal is real.

Aggregate MCX silver turnover and OI figures appear in **published exchange
reports and press releases** — documentary sources, not scraped endpoints — so a
first-cut bound is obtainable without touching MCX's data infrastructure or
pre-empting the ToU ruling.

---

## 5. THE DEPTH SPIKE — DECISION

**Recommendation: DO NOT CANCEL. RE-SCOPE, RE-ORDER, RE-GATE.**
Net effect: **cheaper than the original spike, later in the sequence, and
answering the question that actually decides the family.**

### 5.1 Why not cancel

`CLAUDE.md` states MCXCCL **"may"** mark an illiquid far month from the spread.
That is an **ASSUMPTION**. Killing a family on an unverified assumption is the
same class of governance error as advancing one on an unverified assumption, and
this program's whole method is the FACT/ASSUMPTION distinction. Further, §3.ii is
a coherent design that genuinely escapes the circularity — so by the task's own
framing, a salvageable design exists and depth is not automatically irrelevant.

### 5.2 Why the spike as specified is the wrong test

The current spec — *"one browser-driven fetch of a 2015 and a 2010 date"* — answers
**"do bytes come back?"**. That is the **least** valuable question available, and it
is precisely the shape TRAP 6 warns about: *a successful exit code, a parsed file
and a non-empty row count prove nothing.*

Quantify the value of the question it *does* answer. Depth's entire contribution is
extending the sample:

- floor 2015 → **~48 roll episodes** (√48 = 6.93)
- best case, depth reaches 2010 → 14.5 yrs → **~72 episodes** (√72 = 8.49)

A **perfect** depth result therefore buys **~22% on the t-statistic** (~18% off the
standard error). **A family that is marginal at N=48 is still marginal at N=72.**
Meanwhile the circularity question is **binary and existential**. The current spike
spends real engineering on the ~22% question and none on the existential one.

### 5.3 Two FREE steps that must come FIRST

**STEP 1 — Read the published methodology. Zero cost, no endpoint, decisive.**
MCX / MCXCCL publish contract specifications, bye-laws and business rules, and
circulars covering **Daily Settlement Price computation**. **Reading a published
document is not automated data collection** and is a materially different ToU
question from scraping a data endpoint.

This single document settles §1 to FACT, in whichever direction:

- If DSP for a non-traded contract is defined as *"theoretical price based on cost
  of carry"* → **circularity CONFIRMED as FACT.** Designs (i) and (iii) die
  outright; (ii) survives.
- If it is defined as *"last 30-minute VWAP, else the previous DSP"* (a
  carry-forward) → the far-month contamination is the **stale** kind, which is
  **detectable and discardable** — **materially better news than `CLAUDE.md`
  currently assumes**, and it would upgrade (i) from "partially" to "mostly".

Also documentary, also free, and separately important: **what exactly is the
bhavcopy `Close` column?** Since there is no settlement column, the study would be
using `Close` as a *proxy* for the mark — but `Close` (last trade) and DSP
(computed) are **different objects**, and for a far month they can differ by days.
The file specification answers this.

**I have NOT verified any of the above.** Per the instruction not to fetch from
MCX, and because the ToU ruling is unresolved, no document was retrieved. This is
a disclosed gap, and it is the cheapest gap in this memo to close.

**STEP 2 — Rule OPEN OPERATOR DECISION 1 (exchange ToU) BEFORE any fetch.**
Non-negotiable. And note the asymmetry already recorded: **of the three exchanges,
MCX is the one with the clearest commercial-licensing posture** (`CLAUDE.md`: "MCX
licenses its data commercially"). It is therefore the **worst** candidate for a
fetch-first-ask-later spike. Executing the spike ahead of the ruling would
pre-empt exactly the decision it feeds — which is the reason this analysis was
commissioned as a desk exercise in the first place.

### 5.4 The re-scoped spike, if authorised — what it must verify FOR DESIGN (ii)

Ordered by information value. **Items 1–4 need ONE OR TWO DATES, not a depth
sweep** — so this is *less* fetching and *less* ToU exposure than the original.

1. **Does the bhavcopy publish CALENDAR-SPREAD instruments as their own rows,
   with their own volume and OI?**
   **The single highest-value fact in this entire memo.** YES ⇒ design (ii)
   measures a directly traded instrument and the circularity is fully escaped.
   NO ⇒ (ii) degrades to (i) and the family is on life support.
2. **Does the bhavcopy carry OPEN INTEREST per contract?**
   Without OI, (ii)'s active-pair selection rule (§2.4, the preferred rank rule)
   cannot be pre-registered at all.
3. **The cross-contract common-implied-rate test (§2.3.1).** One date with ≥3
   listed far months. A single shared implied rate across all of them is a
   decisive fingerprint of a model mark.
4. **On 2–3 known roll-window dates: is there genuine two-sided volume in the
   second contract, and how many sessions per episode clear a capacity-derived
   threshold?** **This yields the effective N directly — and N is what kills or
   saves the family (§3.ii).**
5. **Only then, depth** — and *depth for design (ii)* means **"how far back do roll
   windows with two-sided second-leg volume extend"**, not "how far back does a
   file exist." A file that parses cleanly but whose second leg never traded is
   worth nothing.
6. **DROP the 2010 fetch.** 2015 is the recorded defensible floor; §5.2 shows the
   marginal value of reaching 2010 is ~22% on a t-statistic. It doubles ToU
   exposure for a date outside the study window.

### 5.5 Pre-commit the kill line BEFORE the spike (TRAP 3)

Write this into the spec **before** anything is fetched, so the answer cannot be
negotiated after the fact:

> **AG-01 KILL LINE (pre-spike).** If (a) the published DSP methodology confirms
> theoretical-carry marking for non-traded contracts, **AND** (b) the bhavcopy
> exposes no traded calendar-spread rows, **AND** (c) fewer than **[K]** roll
> episodes per year show at least **[V]** sessions of two-sided second-leg volume
> at the capacity-derived threshold — then **SPEC-AG-01 is DEAD**, removed from the
> queue, and logged as a disclosed dead end.

`[K]` and `[V]` must be numbers, chosen before the spike, from capacity arithmetic
(§2.4) and from the N-requirement implied by the SPA gate — **not** from what the
data turns out to offer. This applies the program's own pre-registration
discipline to a **data-acquisition** decision rather than to a backtest, which is
a natural and, as far as I can see, novel extension of it here.

### 5.6 Sequencing

```
1. Capacity math from published aggregates      FREE, outcome-blind, may kill outright
2. Read MCXCCL DSP methodology + file spec      FREE, documentary, settles §1 to FACT
3. OPERATOR: rule ODD 1 (exchange ToU)          BLOCKING — no fetch before this
4. OPERATOR: pre-commit the §5.5 kill line      BEFORE the spike, in writing
5. Re-scoped spike, items 1–5 of §5.4           1–2 dates; drop 2010
6. Only if all above survive: freeze SPEC-AG-01, incl. a commodity cost stack (§4.3)
```

Steps 1 and 2 are free and unblocked **today**. Step 3 is already an open operator
decision on the program's list. **Steps 1–2 should happen regardless of what is
decided about AG-01**, because they cost nothing and they convert two standing
ASSUMPTIONs into FACTs.

---

## 6. WOULD A LICENSED VENDOR (ACCORD FINTECH / ACE DATAFEED) SOLVE THIS?

**Precise answer: a licence solves ACCESS and ToU. It does not solve CIRCULARITY.
These are different problems and conflating them would waste money.**

### 6.1 What a licence cannot do

Circularity is a property of **how the number was created by the exchange**, not of
**who sells it to you**. Accord redistributes MCX's official EOD data. It cannot
manufacture a settlement price MCX never computed, and it cannot manufacture a
trade that never happened. **If the far-month mark is model-derived, every
vendor's copy of it is the same model-derived number.**

The thesis sentence for this whole section:

> **The binding constraint on AG-01 is not data availability — it is market
> microstructure. MCX silver's term structure past the second contract is not
> traded, and no vendor sells trades that were never made.**

### 6.2 What a licence genuinely could do — three things, and they are not trivial

1. **Fields the public bhavcopy omits.** A commercial feed may carry a **separate
   DSP column distinct from `Close`**, **open interest**, **number of trades**, and
   possibly a **settlement-type / derivation flag**. Of these, **number of trades is
   the single most valuable missing diagnostic** — it is exactly what §2.1(b) shows
   the proposed volume flag cannot see. A derivation flag, if it exists, would
   close §1 outright. Several of §2's holes close with these fields.
2. **It removes the ToU blocker and the Akamai/Playwright engineering entirely**,
   across **BSE announcements + NSE options + MCX simultaneously** — and Accord has
   now surfaced **independently in three separate research passes** (BSE
   filing-timestamp scoping; VARIANT D / NSE options, DECISIONS.md 2026-07-20; and
   MCX). That convergence is itself evidence.
3. **Intraday / tick data, if offered.** This would be an upgrade **in kind, not in
   degree**: it permits a **synchronous** spread construction (killing the §1.5
   asynchrony defect) and direct identification of spread trades. Likely the
   expensive tier, but it is the only route that fixes §1.5 at all.

### 6.3 The bounded action

Fold **three specific questions** into the Accord enquiry that **OPEN OPERATOR
DECISION 1 already contemplates** — cost is three lines in an email that is likely
to be sent anyway:

- (a) Is there a **settlement/DSP field separate from `Close`**, and is there any
  **flag indicating a derived vs traded mark**?
- (b) Are **open interest** and **number of trades** supplied per contract per day?
- (c) Are **calendar-spread instruments** carried as their own rows, and is any
  **intraday/tick** history available for MCX?

This mirrors the VARIANT D precedent exactly (`DECISIONS.md`, 2026-07-20: *"one
extra line in an email already likely to be sent… this does NOT resurrect the
hypothesis"*). **It does not resurrect AG-01** — ground (B), the power problem, is
independent of data source and no vendor can sell more roll episodes than the
calendar contains — **but a licensed multi-exchange history route is a durable
capability asset regardless**, and it is now the third independent argument for
making that enquiry.

---

## 7. A GENERAL LESSON WORTH RECORDING (candidate trap — offered, NOT written into governance)

**Low-turnover families are friction-survivable and evidence-starved by the same
property.**

AG-01 is *shaped* correctly for this program. A carry/roll signal trades ~5–12
round trips per year, which is exactly what the roadmap demands after the legacy
kill (*"new families must be low-turnover by design"*). That is why it is tempting.

But the very low frequency that makes it friction-survivable makes it
**statistically unidentifiable within a fixed development window**. The seal fixes
the dev window; you cannot buy more of it at any price. **A signal that fires 5
times a year has ~48 independent observations in 9.5 years — and 48 observations
cannot clear a SPA gate charged against 52+ cumulative trials except for an
enormous effect.**

The corollary for the pipeline: **for any candidate family, compute the effective
independent-observation count BEFORE committing to data acquisition.** It is free,
outcome-blind, arithmetic, and it would have flagged AG-01 before the MCX ingest
was ever scoped. This sits naturally alongside the existing **TRIAL ECONOMICS**
corollary — trials are cheap, *slots and sealed tests* are scarce — and adds:
**independent observations are scarcer than all of them, and unlike trials they
cannot be bought.**

I have deliberately **not** written this into `governance/DECISIONS.md` or the
TRAPS list. It is offered for the operator to adopt, amend or reject.

---

## 8. WHAT THIS ANALYSIS DID NOT ESTABLISH (TRAP 6 discipline)

Stated explicitly so none of it is mistaken for settled:

- **UNKNOWN — MCXCCL's actual DSP methodology for non-traded contracts.** The
  central question. Free to resolve from published documents (§5.3 step 1). **Not
  resolved here** — no MCX resource was accessed, per instruction and per the
  unresolved ToU ruling.
- **UNKNOWN — what the bhavcopy `Close` column actually is** (last trade vs
  computed settlement), and whether the file carries **OI**, **number of trades**,
  or **calendar-spread rows**. All three drive §2, §3.ii and §5.4.
- **ASSUMPTION — MCX SILVER lists ~5 expiries/year.** Drives every N in §3. If
  monthly, multiply episode counts by ~2.4. Carried as a range throughout, never
  as a point.
- **ASSUMPTION — ~10–15 sessions per roll episode with a two-sided second leg.**
  Plausible, unverified; item 4 of §5.4 measures it directly.
- **ASSUMPTION — MCX offers calendar-spread order entry for silver.** Underpins
  both §2.1(a) (as a defect) and §3.ii (as the salvage).
- **NOT CHECKED — whether the Silver ML engine's feature set already included
  carry/term-structure inputs** (§4.2). Free and outcome-blind in principle, but
  the engine is not in the frozen clone and any production-tree copy is barred by
  **BINDING RULE 1**. **Operator question.**
- **NOT ESTABLISHED — MCX silver second-month open interest**, hence the §4.4
  capacity bound. Obtainable from published aggregates; not attempted here.
- **NOT BUILT — a commodity-futures friction stack** (§4.3). `src/costs_in.py` is
  NSE cash equity only; RULING 5 does not reach MCX.

---

## 9. RECOMMENDATION IN ONE PARAGRAPH

SPEC-AG-01 is **not viable as specified**, and the decisive reason is **not** the
circularity — it is that the only design which escapes the circularity (§3.ii, the
roll-window traded spread) has an effective sample of roughly **48–114 independent
roll episodes**, which will not clear a SPA gate charged against 52+ cumulative
trials, net of a commodity friction stack that does not yet exist. **Do not cancel
the depth spike outright, but do not run it as specified either**: depth is worth
~22% on a t-statistic while the unresolved circularity is binary, so run the two
**free** steps first (capacity math from published aggregates; read MCXCCL's
published DSP methodology and bhavcopy file spec — both documentary, neither
touching a data endpoint), then obtain the **ToU ruling**, then **pre-commit a kill
line**, and only then run a **re-scoped, cheaper spike** whose first question is
*"does the bhavcopy publish traded calendar-spread rows with their own volume and
OI?"* rather than *"do bytes come back from 2010?"*. Add the three MCX field
questions to the Accord enquiry already contemplated — **a licence solves access,
not circularity, and cannot create roll episodes the calendar never contained.**
In the meantime, **move AG-01 behind SPEC-52WH-01 in the queue**: it has no frozen
spec, no data, no cost stack, an unresolved ToU blocker and now a disclosed power
problem, while 52WH has a built stack and a decision waiting.

# Block-Trade Detection — feasibility memo (outcome-blind, pre-spec)

**Question put by the operator (2026-07-23):** *is it possible to know when a large
block purchase of shares has been made?* Hypothesis: positive momentum begins
because a big investor or an HFT makes a purchase with volume significant enough to
push the price up; can we detect that immediately and capture the subsequent upside?

**Date:** 2026-07-23.
**Status:** DIAGNOSTIC, NOT A TRIAL. **Outcome-blind. No trial spent. No shadow slot
consumed. No repo outcome data touched.** No price panel was loaded for outcome
measurement; no return, CAR, post-block return, hit rate or conditional performance
summary was computed; no `data_gate` outcome call was made; no backtest was run.
**No spec is drafted and none is proposed for drafting. No exchange endpoint was
scraped or fetched** (OPEN OPERATOR DECISION 1 — exchange ToU — is unresolved; NSE
explicitly prohibits automated collection). `governance/research_register_v2.csv`
was **read, not written** — a register row is *proposed as text* at the end for the
operator to append.

**Scope split (from the brief).** Two questions are bundled and treated
differently:
- **"Can we OBSERVE a large block purchase in time to act?"** — a data-availability,
  legal and microstructure question. **This is FREE and it is this memo's
  assignment.**
- **"Does it predict returns / can we capture the upside?"** — conditional return
  measurement. AMENDMENT A (`governance/CONTAMINATION_POLICY.md`) names event studies
  and conditional return plots as a **TRIAL** requiring a hash-frozen spec, a
  pre-registered register row and a shadow slot. Both slots are held (QFM, PEAD).
  **This memo does NOT spend a trial or a slot and computes not a single post-event
  return.** The return-capture economics live in the sibling memo
  `analysis/breakout_entry_feasibility.md` — cross-referenced, not redone.

**Source tiers** (the `analysis/QFM_literature_prior.md` convention), marked on
every external citation:
- **[PR]** peer-reviewed journal article.
- **[WP]** working paper / preprint / dissertation — not refereed.
- **[VM]** vendor / broker / screener / practitioner marketing — **systematically
  biased toward positive results**; used only to characterise the information
  environment, **never as evidence for an effect.** The order-flow / "smart-money" /
  "block-deal-tracker" space is saturated with [VM] and is treated ruthlessly.

**FACT / ASSUMPTION tags** on every material input, per repo convention.
**"unverified"** means no primary source was opened stating it — TRAP 4: *a disclosed
gap is an asset; an invented number is a liability at due diligence.*

---

## VERDICT (stated first, argued after)

> ## **(C) NOT OBSERVABLE IN TIME TO ACT — the immediacy premise fails on data and law before any return question is reached.**

The immediacy premise — *detect the block, act on it, capture the upside* —
requires three things to hold at once: **(a) observability** (a lawful data route
carries the block-purchase event), **(b) latency** (it carries it fast enough to act
before the move is spent), and **(c) meaning** (the observed event is actually the
*start* of informed accumulation, not its end, and is actually a *purchase* in a
sense that predicts anything). This memo finds that **all three fail**, in that
order of decisiveness:

1. **LATENCY kills it first and cheaply.** Every lawful route this program can hold
   is **post-close** — bulk deals are disseminated by the exchange *after market
   hours the same day* (SEBI circular SEBI/MRD/SE/Cir-7/2004; see §2), and block
   deals are executed in **separate windows** whose consolidated disclosure is a
   published report, not a real-time actionable tape. A block knowable only that
   evening cannot be "captured immediately." The only routes that carry
   near-real-time signed order flow are **tick-by-tick feeds and Level-2 order books
   behind a broker/exchange licence — i.e. Kite Connect, which BINDING RULE 3
   forbids**, or an unlicensed/commercial feed the program does not hold.

2. **MEANING kills it independently, so obtaining the data would not rescue it.**
   In a continuous double-auction *every trade has a buyer and a seller* — "a large
   purchase" is not a well-defined observable without aggressor-side
   identification, which is not recoverable from OHLCV bar data (§3, §5). And the
   microstructure literature says a block large enough to *visibly push price* is
   precisely the execution outcome institutions pay VWAP/TWAP/dark-pool machinery to
   AVOID (§5) — so a *detectable* block is a *self-selected* sample of failed or
   deliberately-loud executions, and a *visible* print is more likely the END of
   informed accumulation (adverse selection) than its start.

3. **This is not a new idea in this repo — it is already shipped, and already found
   miscalibrated.** The legacy production engine implements exactly "detect a volume
   surge on the opening candle and act immediately": `preopen_check.py:653-661`
   enters on *"close > entry_price AND `volume_ratio >= 1.5`"* evaluated on the
   09:15–09:20 bar (§1). Its confirmation gate is the very one **RULING 13** found
   **mislabelled by ~2.95×** because it extrapolates a front-loaded opening bar as if
   intraday volume were uniform. The operator's hypothesis, in its only lawfully
   implementable form here, is a live instrument this program has already measured
   and found to mean something other than its label.

**The honest kill line:** *the only real-time route is a forbidden or unlicensed
data feed; the lawful routes (bulk/block/SAST/FII-DII/MF-holdings) are all
post-close or slower; and even with the data, a visible block is the wrong sign of
the wrong quantity.* The immediacy premise fails on **law and latency before any
return could be measured** — which makes this a cheap kill: **no trial need be spent
to reach it.**

**Dev-window substrate check (may end the question on its own).** A *pre-2024-07-17*
study of intraday block prints has **no substrate at all** in this program:
yfinance serves 5-minute bars for the **last ~60 calendar days only** (FACT, probed
under RULING 13; Jan/Mar/Apr 2026 returned 0 rows), and BINDING RULE 3 forbids the
Kite path that alone reaches deeper history. There is **no lawful intraday tape in
the dev window** on which any block-detection signal could even be constructed, let
alone validated under the seal protocol. Detection built on intraday order flow is
therefore not merely unproven here — it is **unbuildable and untestable with the
data this program lawfully holds.** (Cross-ref: `DIAG-VOLSHARE-0001`'s own register
note, *"deeper history needs Kite = BINDING RULE 3, refused."*)

The three-part argument follows.

---

## 1. The live instance: this hypothesis is already shipped in production

The operator's hypothesis is not abstract in this program. The **legacy production
engine — the daily mid-cap momentum system this program KILLED as a fund candidate**
(real gross alpha ~18.5%/yr, t≈2.95, consumed by friction at 1.6 round-trips/day) —
already implements "detect a volume surge on the opening candle and act
immediately."

**FACT (frozen clone `~/vendor/legacy-engine` @ `ee7ad132`, verified this session):**
`preopen_check.py:653-661`, the `BREAKOUT` entry branch, fires a `BUY` verdict when

> `candle_close > entry_price AND volume_ratio >= 1.5`

evaluated on the **09:15–09:20 opening bar**, with reason string *"Breakout confirmed
— close ₹X above ₹Y with N× vol. Enter now."* That is the operator's question —
*a purchase with volume significant enough to push price, detected and acted on
immediately* — implemented, shipped, and running today.

**Three facts about this instance carry the whole detection question:**

1. **Its "volume significance" test is the RULING 13 gate, and it is mislabelled by
   ~2.95×.** `volume_ratio` is computed `(vol × 75) / avg20` (`preopen_check.py:420`,
   `:462`), projecting the single opening bar to a full day *as if intraday volume
   were uniform*. It is not — NSE volume is front-loaded; the measured first-5-min
   share `s ≈ 4.0%` (median, four independent routes: `DIAG-VOLSHARE-0001-RESULT`,
   `-0002-REFINE`) versus the `1/75 = 1.33%` the ×75 implies. **The nominal 1.5×
   "volume-confirmed breakout" gate really demands only ~0.51× of the 20-day average
   opening bar** (RULING 13; VERIFIED AT PRODUCTION HEAD `5c099d77`). So the live
   system's answer to "is this volume significant enough to signal a big buyer?" is
   computed on a denominator that overstates the opening bar's representativeness ~3×.
   **The detection threshold does not mean what its label says** — a direct,
   already-paid-for demonstration of this memo's §5 "signed volume ≠ buying pressure"
   objection.

2. **Its data path is Kite Connect — forbidden to THIS program.** The live gate's
   `volume_ratio` input comes from Kite candle data (`get_kite_client`,
   `preopen_check.py:51`; the `candle_verdicts_*.json` that `DIAG-VOLSHARE-0002` reads
   are Kite-sourced). **BINDING RULE 3 forbids this program from making that call.**
   The alpha-research workspace cannot even *reconstruct* the live gate's own input in
   real time, let alone build a richer block-detection feed on the same substrate. The
   production system may run it; the *research* program may not.

3. **It is a breakout-entry rule, and the return-capture verdict on it already
   exists.** Whether entering on that confirmed breakout captures upside is the
   subject of the sibling memo `analysis/breakout_entry_feasibility.md`, whose verdict
   is **(C) DO NOT BUILD** — the friction hurdle (≈62 bps gross/round-trip to break
   even at a 5-session hold) exceeds documented post-breakout drift, and the India
   52-week-high evidence (Raju 2023) says the tradeable leg is the *short* leg, not
   buying the breakout. **This memo does not re-litigate that** — it establishes only
   the prior question: *can the block/surge even be observed in time, lawfully, and
   does it mean what the hypothesis assumes?*

**Takeaway for detection:** the one form of this hypothesis that is lawfully
implementable in this program's data universe — an opening-bar volume-surge gate —
already exists in the killed legacy system, and this program has already measured its
central quantity (`volume_ratio`) and found the "significance" label off by ~3×. That
is the strongest possible evidence that the naive "big volume ⇒ big buyer ⇒ momentum"
inference is fragile.

---

## 2. Data routes — what carries a "block purchase", and WHEN it becomes public

The decisive column is **publication latency**. A route that reveals a block only
after the close cannot satisfy "detect immediately and capture the upside," no matter
how clean the data. Every route below is assessed from **public regulatory
documentation and prior repo research only — no exchange endpoint was fetched.**
Where a specific figure could not be re-verified from a primary source this session
(web-search budget was exhausted by sibling agents; one SEBI URL returned a hard 404),
it is tagged **ASSUMPTION** and left open rather than asserted (TRAP 4).

### 2.1 Data-route table

| # | Route | What it contains | **Publication latency** | Legal position | Cost | Earliest usable date |
|---|-------|------------------|-------------------------|----------------|------|----------------------|
| 1 | **SEBI/NSE/BSE bulk-deal disclosure** | Client name, scrip, qty, avg price, buy/sell — any client whose *aggregate* day trades in a scrip exceed **0.5% of listed shares** | **END OF DAY**, after market hours (SEBI/MRD/SE/Cir-7/2004) — *FACT (regulation), latency is by design not accident* | Public exchange disclosure; free to read. Automated collection gated by **OPEN OPERATOR DECISION 1** | Free (published) | ~2004 (post-circular) |
| 2 | **SEBI/NSE/BSE block-deal disclosure** | Trades in the two block windows: min order value **₹10 cr**, price band **±1%**, windows **08:45–09:00** and **14:05–14:20** *(ASSUMPTION on exact figures — see §2.2)* | **Window trades disclosed same day; consolidated report published post-session** — NOT a real-time actionable tape *(ASSUMPTION on real-time granularity)* | Public disclosure; automated collection gated by OPEN OPERATOR DECISION 1 | Free (published) | ~2017 revision; earlier window pre-2017 |
| 3 | **Tick-by-tick / Level-2 order book** | Full depth, per-order, timestamped — the *only* route that could identify a large aggressor near real time | **Real time** (this is the whole point) | Requires broker/exchange licence. **Kite Connect = BINDING RULE 3 FORBIDDEN.** Commercial TBT feed = licensed/paid, program does not hold | Kite: forbidden. Licensed TBT: material, unpriced here | N/A to this program |
| 4 | **Trade classification from OHLCV** (Lee-Ready / tick rule) | Attempt to *infer* buyer/seller-initiated from bar data | N/A — inference, not disclosure | Free (public prices) | Free | — but see §3: **not recoverable from bars** |
| 5 | **FII/DII aggregate provisional flows** | Exchange-wide net buy/sell by FII and DII, **aggregate — no stock, no direction per name** | **END OF DAY** (provisional, post-close); SEBI/NSDL detail with further lag | Public | Free | Long history |
| 6 | **SAST / insider (PIT) disclosures** | Substantial-acquisition (SAST ≥5% and each ±2% thereafter) and designated-person insider trades | **T+1 to T+2 business days** (disclosure-deadline latency) *(ASSUMPTION on exact deadline)* | Public regulatory filing | Free | Regulation-era |
| 7 | **Mutual-fund monthly holdings** | Scheme-level portfolio holdings | **~7–10 days after month-end** *(ASSUMPTION on exact lag)* | Public (AMFI/AMC) | Free | Long history |
| 8 | **Accord Fintech (ACE Datafeed)** | Authorised NSE/BSE/MCX vendor; may package bulk/block/corporate-action/derivatives history | Vendor-dependent; **historical, not a real-time actionable block tape** *(ASSUMPTION — not verified)* | Licensed vendor — would *resolve* the ToU question for what it covers | Commercial, unpriced here | Vendor-dependent |

### 2.2 What is FACT vs ASSUMPTION in the table

- **FACT (well-established regulation, high confidence):**
  - **Bulk deals are disseminated by exchanges *after market hours the same day*** —
    the operative SEBI instrument is **SEBI/MRD/SE/Cir-7/2004 (14 Jan 2004)**, which
    requires brokers to disclose bulk-deal details and exchanges to disseminate them
    **on the same day after market hours.** This is the single most decisive fact in
    the memo: the bulk-deal route is **end-of-day by regulatory design.**
  - **Bulk-deal threshold = 0.5% of the number of listed shares of the company**,
    aggregated per client per scrip per day.
  - **Block deals execute in dedicated windows on a separate order book** with a
    minimum order value and a tight price band, precisely so large trades do NOT
    walk the continuous book — i.e. the mechanism is *designed to suppress* the
    visible price impact the hypothesis wants to detect.
  - **FII/DII provisional flows are exchange-wide aggregates published post-close** —
    they carry no per-stock, per-direction attribution and cannot localise a block.
  - **Level-2 / tick-by-tick real-time flow requires the Kite path or a licensed
    feed** — the Kite path is BINDING RULE 3 forbidden.

- **ASSUMPTION (could not re-verify from a primary source this session; web-search
  budget exhausted, one SEBI circular URL 404'd):**
  - Exact block-deal window times (08:45–09:00 / 14:05–14:20), the ₹10 cr minimum
    order value (raised from ₹5 cr in the 2017 revision), and the ±1% band. These are
    my recollection of the current framework; **flagged ASSUMPTION and to be
    confirmed against the live SEBI circular before any spec cites them.**
  - Whether block-deal *dissemination* has any intraday/near-real-time granularity vs
    a purely post-session consolidated report. **Even under the most favourable
    ASSUMPTION (some intraday dissemination), a ±1%-band separate-window print is a
    completed institutional cross, not the *start* of an accumulation you could front
    — see §5.**
  - SAST/insider disclosure deadlines (T+1/T+2) and MF-holdings lag (~7–10 days).
  - Everything about Accord Fintech (ACE Datafeed) coverage, latency and price —
    **entirely unverified**; carried only because it surfaced independently in three
    prior repo research passes as an authorised vendor, and one enquiry could both
    price a licensed route and dissolve the ToU blocker for the historical (not
    real-time) portion.

### 2.3 The latency verdict, stated plainly

**Routes 1, 5, 6, 7 are post-close to multi-day.** Route 2 (block deals) is at best
same-day-consolidated and structurally a *completed cross*, not a leading signal.
**Route 3 — the only genuinely real-time route — is forbidden (Kite) or unheld
(licensed TBT).** Route 4 does not exist as a disclosure at all and, per §3, cannot
be reconstructed from bars. **There is no lawful real-time route to a block-purchase
signal in this program's data universe.** The "capture it immediately" premise fails
on latency and law before the microstructure objections in §5 are even reached.

---

## 3. Trade classification without quotes — what OHLCV can and cannot recover

The hypothesis assumes "a large purchase" is an observable event. In a continuous
double-auction it is not, without **aggressor-side identification** — knowing which
side *initiated* (crossed the spread). The standard tools for that are:

- **Lee & Ready (1991) [PR]** — classify a trade as buyer- or seller-initiated by
  comparing the trade price to the prevailing **bid/ask midpoint** (quote rule),
  with a **tick-rule** tiebreak. *Requires the quote (bid/ask) series.*
- **The tick rule** — sign a trade by whether it printed above (buy) or below (sell)
  the previous *trade* price. *Requires the trade-by-trade (tick) series.*
- **Bulk-Volume Classification / VPIN (Easley, López de Prado, O'Hara 2012) [PR]** —
  sign *volume* over short bars using a distributional (probit of standardised price
  change) rule. *Requires intraday trade sequence and has been sharply criticised
  (§5).* 

**FACT — none of these is computable from this program's lawful data.** OHLCV bar
data carries open, high, low, close and *total* volume. It carries **no bid/ask
quote** (kills Lee-Ready) and **no intra-bar trade sequence** (kills the tick rule
and BVC). A 5-minute bar's volume is the *sum* of buyer- and seller-initiated volume
with the sign already destroyed. **Signed order flow — the crux of "a purchase" — is
not recoverable from bar data.** This is not a resolution problem that a finer bar
fixes; it is an information-content problem. The lawful substrate (60-day yfinance
5-minute bars) is *unsigned by construction.*

The one thing OHLCV *does* carry is **unsigned volume** — which is exactly what the
legacy `volume_ratio` gate uses, and exactly why that gate can only ever say "volume
was high," never "buyers were aggressive." RULING 13 showed even the *magnitude* read
off that unsigned volume was mislabelled ~3×. So the lawful data supports, at most, an
**unsigned volume-surge detector** — which is the legacy breakout gate, already built,
already measured, already found wanting.

---

## 4. FII/DII, SAST/insider, MF holdings — aggregation and lag rule everything out

Even setting aside real-time detection, could a *slower* institutional-flow signal
stand in for "a big investor bought"? Each candidate fails on **aggregation level or
publication lag**, independently of the ToU blocker:

- **FII/DII provisional flows [FACT]:** exchange-wide **aggregate** net buy/sell,
  published **post-close**. No stock, no per-name direction. Cannot localise a block
  to a name; cannot be acted on intraday. Useful for regime/breadth context only —
  and this program already treats a regime overlay as mandatory in SPEC-52WH-01, so
  it is not new signal.
- **SAST (≥5% and each ±2% thereafter) and PIT insider disclosures [FACT on
  existence; ASSUMPTION on exact deadline]:** these are the closest thing to "a named
  large buyer," but they are **T+1/T+2 filings** — by the time the disclosure is
  public, the acquisition is complete and any price impact largely realised. This is
  the adverse-selection problem (§5) in regulatory-latency form: you learn who bought
  *after* they are done buying.
- **Mutual-fund monthly holdings [FACT on existence; ASSUMPTION on lag]:** scheme
  portfolios published **~7–10 days after month-end** — a multi-week lag on a
  point-in-time snapshot that cannot even tell you *when* in the month the position
  was built. Useless for immediacy; usable only as a slow ownership-drift feature,
  which is QFM/PEAD-adjacent territory, not a block detector.

**None of these is a real-time block-purchase signal.** They are slow ownership
diagnostics. The hypothesis as posed — *detect the purchase as it pushes price, act
immediately* — has no lawful data route among them.

---

## 5. The microstructure critique — why the premise is wrong even with perfect data

This is the intellectual core. Suppose, counterfactually, the program *did* hold a
real-time signed tape. The hypothesis would still be built on premises that market
microstructure research largely contradicts. Four objections, in descending force.

### 5.1 Institutions deliberately hide — a *detectable* block is a self-selected sample

Large orders are executed by **VWAP / TWAP / implementation-shortfall algorithms**
that slice a parent order into many child orders across hours or days, and routed to
**block windows and off-book venues**, *specifically to minimise visible price
impact* (Almgren & Chriss 2000, *Optimal execution of portfolio transactions* [PR];
Bertsimas & Lo 1998 [PR]). The entire multi-billion-dollar execution-services
industry exists to make institutional buying **invisible**.

The consequence for detection is fatal by selection: a block **large enough to
visibly push price in a single detectable event** is close to the exact failure mode
these algorithms are paid to avoid. So the set of blocks you *could* detect is a
**biased sample** — botched executions, deliberately loud liquidity-demanding trades
(e.g. an index-rebalance cross, a forced unwind), or trades where the counterparty
*wanted* to be seen. **Conditioning on visibility selects against the informed,
patient buyer the hypothesis imagines.** [This is a logical/selection argument, not a
measured result — no return was computed.]

### 5.2 A visible print is more likely the END of accumulation than the start (adverse selection)

The hypothesis assumes the visible move is the *beginning* of informed buying, with
upside still to capture. Microstructure says the opposite is the base case. In
**Kyle (1985) [PR]**, the informed trader optimally trades *gradually* to hide in
noise-trader volume; the price impact is the market maker's Bayesian update, and by
the time cumulative impact is large, **the informed trader's information is largely
already in the price.** In the **Glosten-Milgrom (1985) [PR]** framework, every
executed trade moves the quote *because* the market maker treats it as possibly
informed — so the impact you observe is the market *already* pricing the information,
not a lag you can exploit.

Empirically, the **block-trade literature** decomposes price impact into a
**permanent** component (information) and a **temporary** component (liquidity /
inventory):
- **Holthausen, Leftwich & Mayers (1987, 1990) [PR]** and **Keim & Madhavan (1996)
  [PR]**: block trades show a **permanent** price move (which does *not* reverse — so
  it is not free to capture; it is already in the price by the time you see the
  print) **plus a temporary** move that **reverses.**
- **Kraus & Stoll (1972) [PR]**: documented the price-reversal (temporary-impact)
  pattern around blocks decades ago.

The temporary component is the trap. A naive "buy when you see the big buy" rule
systematically buys **into the temporary impact**, i.e. near the local top of the
liquidity-driven overshoot, and then **holds through the mean-reversion** of that
temporary component. Framed in the program's own terms (Kyle's λ decomposition;
Almgren-Chriss temporary vs permanent impact): **the naive strategy is a systematic
buyer of the reversion.** The permanent part — the only part with predictive content
— is already impounded before the print is observable.

### 5.3 The HFT limb is self-defeating on latency

If, as the hypothesis's second clause proposes, an **HFT** initiated the move, the
HFT's horizon is **microseconds to seconds** and its edge is *co-location, direct
market-data feeds, and order-book microstructure* — a domain measured in
sub-millisecond latency. This program's realistic position in that arms race is
**last**: it holds 5-minute bars from a *retail, end-of-day-oriented* public feed
(yfinance), with no co-location, no direct feed, no order-book access (Kite forbidden).
By the time a 5-minute bar has *closed* and been *fetched*, any HFT-initiated move is
**hundreds of thousands of the HFT's decision-cycles old.** The "remaining upside"
after an HFT move is, by the HFT's own construction, already gone — that is *why*
they traded. **A retail-latency system cannot capture an HFT-latency signal; the two
clauses of the hypothesis are mutually inconsistent about horizon.**

### 5.4 Signed volume ≠ buying pressure — "a large purchase" is under-defined

In a continuous double-auction **every trade has a buyer and a seller.** A print of
100,000 shares is simultaneously a 100,000-share purchase and a 100,000-share sale;
"a large purchase" only means something once you identify the **aggressor** (who
crossed the spread) — and §3 established that aggressor identity is **not recoverable
from OHLCV.** Even *with* signed data, aggressor-signed volume is a noisy proxy for
"informed buying pressure":
- **PIN (Easley, Kiefer, O'Hara & Paperman 1996) [PR]** and **VPIN (Easley, López de
  Prado & O'Hara 2012) [PR]** attempt to distil order flow into a probability of
  informed trading — but **VPIN has been sharply criticised**: Andersen & Bondarenko
  (2014, *VPIN and the flash crash*) [PR] argue VPIN is largely a **mechanical
  function of volatility and the bulk-classification choice**, with little genuine
  toxicity content and no established predictive value out of sample. Relying on a
  signed-flow toxicity measure as a "big buyer" detector imports an actively
  contested construct.

**Net:** "a large purchase pushing price" conflates (i) unsigned volume — all this
program can see, and mislabelled ~3× at that (RULING 13); (ii) aggressor-signed
volume — unobservable here and a noisy proxy even where observable; and (iii)
*informed* buying pressure — a latent quantity the best measures struggle to
recover. The hypothesis treats these as one thing. They are not.

### 5.5 The [VM] information environment — treated ruthlessly

The retail-facing web is saturated with **[VM]** "smart-money flow," "order-flow
imbalance," "delivery-percentage spike," "bulk/block-deal tracker" and
"institutional-buying-alert" products. Per the source-tier convention these are
**systematically biased toward positive results** and are used here **only to
characterise the information environment, never as evidence.** Their existence tells
us two things and no more: (a) there is strong retail *demand* for exactly this
hypothesis (which is itself a mild contrarian signal — a widely-sold "edge" is
unlikely to be an edge), and (b) the *delivery-percentage* and *bulk-deal-tracker*
framings are the same post-close, unsigned, or aggregated data assessed in §2–§4,
repackaged. No [VM] product here surmounts the latency, signing, or selection
problems above. **India-specific peer-reviewed microstructure evidence on
block-trade impact and its temporary/permanent decomposition was not located this
session (web-search budget exhausted) — flagged as an evidence gap, not a null
(TRAP 4/TRAP 6). The mechanism arguments above are venue-general and do not depend on
an India-specific citation, but a spec would need the India evidence before relying on
any effect size.**

---

## 6. If it were ever pursued — what it would take (and why the gate is high)

For completeness, and to be explicit that this is a *kill on observability*, not an
oversight: to move any block-detection idea from this memo to a measured result would
require, in order:

1. **A lawful real-time (or near-real-time) signed-flow route** — which does not
   currently exist for this program. Kite is BINDING RULE 3 forbidden; a licensed TBT
   feed is unheld and unpriced; the Accord/ACE route is unverified and, even if it
   exists, is **historical, not a real-time actionable tape** (ASSUMPTION). **This
   step is currently blocked outright.**
2. **A dev-window intraday substrate** to develop against pre-2024-07-17 — which
   **does not exist** (60-day yfinance horizon; §Verdict). Without it there is nothing
   to build or seal-test on. **Also blocked outright.**
3. Only then: a **hash-frozen spec** with a pre-registered kill line, a **register
   row**, and a **shadow slot** — and **both slots are held (QFM, PEAD)**, with AG-01
   and 52WH already queued behind them. A block-detection family would be *at best*
   sixth in line, behind families that do not share its two fatal data blockers.
4. Only then could any **post-event return** be measured — the trial this memo is
   forbidden to spend and deliberately did not.

Steps 1 and 2 are hard blockers with no line of sight to resolution under the binding
rules. **The correct action is not to queue this behind QFM/PEAD but to record it as
observability-killed.**

## 7. Open items and blockers

- **BLOCKER (hard, binding):** no lawful real-time signed-flow route — Kite is
  BINDING RULE 3 forbidden; licensed TBT unheld.
- **BLOCKER (hard, structural):** no dev-window intraday substrate — 60-day yfinance
  horizon is permanent; deeper history needs Kite.
- **Rides on OPEN OPERATOR DECISION 1 (exchange ToU):** automated collection of even
  the *post-close* bulk/block-deal disclosures (Routes 1–2) is gated by the
  unresolved NSE/BSE/MCX ToU ruling. This does **not** change the verdict — those
  routes are latency-killed regardless — but note that the lawful *post-close* data
  cannot even be systematically ingested until DECISION 1 resolves.
- **Rides on the Accord Fintech (ACE Datafeed) enquiry** already contemplated under
  DECISION 1 and `analysis/accord_fintech_enquiry.md`: one enquiry could price a
  licensed route and confirm whether any near-real-time or historical block feed is
  even offered. **Fourth independent surfacing of that vendor in this program** —
  fold block/bulk-deal history into the existing enquiry; do not open a new workstream.
- **ASSUMPTIONS to verify before any spec cites them:** exact block-deal window times,
  ₹10 cr minimum, ±1% band (SEBI circular, 404'd this session); SAST/PIT disclosure
  deadlines; MF-holdings lag; all Accord/ACE coverage and latency claims. Every one is
  a disclosed gap, not an invented number (TRAP 4).

## 8. Proposed register row (TEXT ONLY — operator to append; this memo did NOT write it)

Per the brief, `governance/research_register_v2.csv` was **not written** (a concurrent
agent is appending to it). The proposed row, for the operator to append verbatim if
they concur:

```
BLOCK-DETECT-SCOPE-0001,2026-07-23,LEGACY,"Feasibility scope: can a large block PURCHASE be detected in time to act, from data this program lawfully holds? (operator hypothesis: big-buyer/HFT volume surge starts momentum)",scope-diagnostic,"KILLED ON OBSERVABILITY — not a trial","OUTCOME-BLIND, NO TRIAL SPENT, NO SHADOW SLOT, NO REPO OUTCOME DATA, NO SCRAPING, NO SPEC. Verdict (C): no lawful real-time signed-flow route exists — Kite=BINDING RULE 3 forbidden, licensed TBT unheld; all lawful routes (bulk-deal EOD per SEBI/MRD/SE/Cir-7/2004, block-deal separate-window consolidated, FII/DII aggregate EOD, SAST/PIT T+1/T+2, MF holdings monthly+lag) are post-close or slower; signed order flow NOT recoverable from OHLCV (Lee-Ready/tick rule need quotes/ticks). No dev-window intraday substrate (60-day yfinance horizon). Microstructure: institutions hide (Almgren-Chriss), a visible print is likelier the END of accumulation than the start (Kyle 1985, Holthausen-Leftwich-Mayers, Keim-Madhavan permanent/temporary decomposition => naive rule buys the reversion), HFT limb self-defeating on retail latency, signed volume != buying pressure. Live instance already shipped: legacy preopen_check.py:653-661 breakout gate, whose volume_ratio is RULING 13 mislabelled ~2.95x. Return-capture economics: see analysis/breakout_entry_feasibility.md (verdict C). Cumulative trial count UNCHANGED (no trial spent). Cross-ref DECISION 1 (exchange ToU) + Accord/ACE enquiry."
```

**Note on trial accounting:** this row records a **scope/kill, not a trial** — the
cumulative trial count (53 as of 2026-07-22) is **unchanged**. No outcome was
observed; the kill is on observability and law, reached with zero outcome contact.

---

## 9. Cross-references

- **`analysis/breakout_entry_feasibility.md`** — the sibling memo owning the
  *return-capture* economics of post-breakout entry (verdict **(C) DO NOT BUILD**;
  ~62 bps/round-trip friction hurdle; Raju 2023 says the tradeable leg is the short
  leg). This memo owns **detection/observability**; that memo owns **capture**.
- **RULING 13** (`governance/DECISIONS.md`; `analysis/proposed_ruling_13_2026-07-22.md`)
  and register rows **`DIAG-VOLSHARE-0001` / `-0002-REFINE`** — the opening-bar
  volume-share measurement that shows the live "volume significance" gate is
  mislabelled ~2.95×.
- **OPEN OPERATOR DECISION 1** (exchange ToU) and **`analysis/accord_fintech_enquiry.md`**
  — the licensed-vendor route that could price any real block feed and dissolve the
  post-close ingest blocker.
- **BINDING RULE 3** — the forbidden Kite path, which is the *only* real-time route.

**End of memo.** Outcome-blind; no trial spent; no repo outcome data touched; no
scraping performed; no spec drafted; register row proposed as text only.

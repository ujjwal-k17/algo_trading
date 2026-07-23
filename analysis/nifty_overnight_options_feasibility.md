# NIFTY50 Overnight-Gap Direction → Index-Option Trade — Feasibility / Scoping Memo

**Question (operator, 2026-07-23):** At 15:15 IST on any given day, using market
trends + macro factors, can we predict the DIRECTION of the NIFTY50 open the next
morning (9:15) — and how much money could be made buying a NIFTY index call/put at
15:15 and selling at the next open?

**Scope split:** this memo OWNS the NIFTY **index-option** case and the shared
overnight-options microstructure / friction core. A sibling memo,
`analysis/single_stock_overnight_options_feasibility.md`, carries the
single-stock-option case on the same trade and cross-references this core.

---

## GOVERNANCE HEADER (read first)

- **OUTCOME-BLIND feasibility / scoping memo.** Data-availability assessment,
  options-microstructure and friction ARITHMETIC from public contract
  specifications and first principles, and external literature only. Under
  `CONTAMINATION_POLICY.md` AMENDMENT A, "cost tables" and reading external
  research are explicitly free.
- **THE REFRAME ENFORCED.** "How much money could be made" is a strategy-P&L /
  conditional-return question. AMENDMENT A is verbatim: *"Any analysis that
  observes strategy or signal outcomes conditional on the signal — including
  event-study CARs, conditional return plots, and 'sanity check' performance
  summaries — is a TRIAL."* Answering the P&L question with data would therefore
  be a TRIAL, requiring a hash-frozen spec, a pre-registered register row and a
  shadow slot. **Both slots are held (QFM, PEAD); AG-01 and 52WH are queued.**
  This memo spends none of that. It is a FEASIBILITY memo, not a backtest.
- **NO TRIAL SPENT.** Cumulative trial count stays at **53** (count the register,
  do not trust the number — the file has grown to 14 rows but the recent additions
  are all outcome-blind and spend no trial). No option return, no straddle return,
  no direction hit-rate, no gap-prediction accuracy, no conditional/forward return,
  no Sharpe/IR is computed from data anywhere in this memo.
- **NO SHADOW SLOT consumed.** No spec drafted, no hash frozen, no register family
  created. `governance/research_register_v2.csv` is not written.
- **NO broker/Kite call** (BINDING RULE 3); **no scraping** of NSE/BSE
  option-chain endpoints (ToU unresolved — OPEN OPERATOR DECISION 1); **no
  production contact** (BINDING RULE 1); **FINAL_TEST never set**; all reasoning
  is on public contract specs and literature, no repo outcome data conditioned on
  any signal.
- **Session-honesty note (TRAP 4).** This session's web-search/fetch budget was
  exhausted before this memo (the sibling crude memo, same session, records
  200/200 WebSearch used), and the scratchpad holds only the momentum equity
  corpus — **no overnight-options or VRP PDFs.** Every literature citation below
  is from domain knowledge and marked **[unverified at source this session]**. I
  quote directions, never coefficients I cannot re-open. No premium, spread or
  gap NUMBER is fabricated; every quantitative input carries a FACT / ASSUMPTION /
  unverified tag and, where it is an order-of-magnitude placeholder, a range.

---

## VERDICT (stated first, argued below)

**DO NOT BUILD, and — decisively — IT CANNOT BE TESTED IN THIS WORKSPACE WITH
LAWFUL DATA.** Three walls stand, and any one of them is on its own sufficient.

1. **The data wall is decisive and comes first (§1).** There is NO options data of
   any kind in this repo — no option-price series, no IV surface, no option chain —
   and none is lawfully obtainable (Kite forbidden by BINDING RULE 3; NSE/BSE
   option history would be a scrape under the unresolved ToU, OPEN OPERATOR
   DECISION 1). Separately, a "15:15 → 9:15" study is **intraday by construction**,
   and the DIAG-VOLSHARE work already established the repo has **no lawful
   pre-cutoff intraday substrate** (yfinance ≈ 60 days of 5-minute bars; deeper
   history needs Kite). And there is no pre-cutoff options data at all, so even the
   DEVELOPMENT stage the seal requires (`< 2024-07-17`) is unsupported. **This trade
   cannot be measured here without violating a binding rule. That finding is
   complete and sufficient on its own.**

2. **The trade as specified is the losing side of a well-documented trade (§4).**
   Buying an ATM/near-ATM index option at 15:15 and selling at 9:15 is, structurally:
   (a) paying **overnight theta** across a non-trading period the option is priced
   to decay through; (b) being **long the overnight variance risk premium** —
   overnight implied vol systematically exceeds realised gap magnitude, so overnight
   option BUYERS lose on average (the profitable side is SHORT premium, which is
   unlimited-risk and contradicts the operator's "small capital, no big risk"); (c)
   crossing the **bid-ask spread twice**; and, if directional, (d) needing to first
   **predict direction AND** clear the premium+spread. The break-even (§4.5) requires
   a favorable overnight move far larger than the typical gap.

3. **Even a PERFECT open forecast is not an edge, and the forecast can't be made at
   15:15 anyway (§2–§3).** The overnight gap is dominated by information that arrives
   *after* 15:15 — the US cash session, overnight crude/FX/Asia, and above all **GIFT
   Nifty**, the near-24h offshore future that by ~9:00 IST essentially pins the NSE
   open. A forecast made at 15:15 is structurally handicapped: you are forecasting
   across the very window that carries the information. And the NSE open mechanically
   prints where GIFT Nifty already is — public, priced, not a tradeable surprise.
   Reading GIFT at 9:00 is not alpha; and by the time the option itself is tradeable
   (9:15), the open is already known and the option has already repriced.

**This is the highest-turnover shape possible — a DAILY round trip (§5)** — the
exact friction-dominated design the program has killed repeatedly (legacy system;
breakout; crude), and the ROADMAP's standing rule is that new families must be
**low-turnover by design**.

**Strongest evidence FOR (stated fairly).** Overnight gaps are real, non-trivial in
magnitude, and *partly* driven by identifiable, already-public global inputs
(US close, crude, FX, GIFT Nifty) — the same non-synchronous-timing channel
`macro_beta_diagnostic.md` measured in the cross-section. So there IS overnight-gap
structure. If any 15:15-actionable predictability existed, this is where it would
live, and the underlying (index futures) would be a far cleaner vehicle than options.

**Strongest evidence AGAINST.** (i) The predictable part of the gap arrives *after*
15:15, so the 15:15 forecast is handicapped by construction (§2); (ii) the tradeable
residual at 9:15 is already public via GIFT Nifty and is a latency game, not
research alpha (§3); (iii) the option wrapper is a documented systematic loser for
the overnight long buyer — theta + VRP + double spread (§4); and (iv) even in the
*underlying*, the crude memo's arithmetic (~8 bps expected open-gap on a β≈0.08 name
vs a ~32 bps round-trip floor) shows the gap is friction-dominated — and **option
friction is multiples higher** than the underlying's.

**The only defensible reframing is a different, risk-asymmetric strategy the operator
did not ask for** — harvesting the overnight variance risk premium by SELLING
premium — which violates "small capital, no big risk" and carries a full,
unmet governance path (§9). **This memo authorizes none of it.**

---

## 1. THE DATA WALL — established first, because it is probably decisive

### 1.1 Options data: there is NONE in this repo, and none is lawfully obtainable

Confirmed by inspection of every data directory:

- `data/reference/` holds PIT constituents (`pit/`), the six daily TRI series
  (`tri/`), and the rename master (`rename/`) — **no options.**
- `data/workspace/` holds the 52WH **ADJUSTED equity** price panel
  (`price_panel_52wh.parquet`, 1,312 per-symbol `ohlc_adj/*.parquet`) plus recs /
  fills — **no options.**
- `data/market/` holds five days of daily **equity** OHLC; `data/sealed/raw/`
  holds production EOD **equity** backups plus a `nifty_backup_*.csv` (a daily
  **index level** backup, not intraday, not options); `data/legacy_snapshot/`,
  `data/derived/` — **no options anywhere.**
- A repo-wide search for `option` / `iv` / `straddle` / `chain` returns only
  equity *symbol names* that happen to contain those substrings (DIVISLAB,
  PRIVISCL, UNIVCABLES, …). **There is no option-price series, no implied-vol
  surface, and no option chain in this workspace.** [FACT — inspection,
  2026-07-23.]

Valuing the trade requires exactly what is absent: the **option price at 15:15**
(the buy) and the **option price at 9:15 the next morning** (the sell). Neither
exists here. And neither is obtainable under the binding rules:

- **Historical NIFTY option prices via Kite Connect are forbidden** — BINDING RULE
  3 (no live broker calls, no Kite session/token path). This is the same wall the
  DIAG-VOLSHARE work hit for intraday equity volume.
- **NSE/BSE option bhavcopy / option-chain history would be a scrape** under an
  **unresolved Terms-of-Use** (OPEN OPERATOR DECISION 1 — NSE explicitly prohibits
  automated collection; BSE unverified). The same ToU blocker that freezes SRA
  Stage 2 and PEAD's CAR study freezes any option-history collection here. [FACT —
  CLAUDE.md OPEN OPERATOR DECISION 1.]

### 1.2 Intraday timestamps: no lawful pre-cutoff substrate

The trade is **intraday by construction** — it is defined by two clock times, 15:15
and 09:15. The repo has no lawful intraday history to support it:

- DIAG-VOLSHARE established that **yfinance provides only ≈ 60 days of 5-minute
  bars** (the study window was ~2026-04-30 → 2026-07-22, ~57 sessions), and that
  **deeper intraday history requires Kite = BINDING RULE 3, refused.** [FACT —
  register rows `DIAG-VOLSHARE-0001` / `-0002-REFINE`.]
- A "15:15 snapshot → 9:15 open" study needs *years* of intraday history to say
  anything about a daily-frequency edge. The 60-day window is (i) far too short and
  (ii) **entirely post-cutoff** (2026, well after the 2024-07-17 seal), so it is
  not even development data — it is Tier 1 look-don't-tune forward data.

### 1.3 Seal discipline: the development stage itself is unsupported

The seal requires any family be *developed* on dev data strictly **before
2024-07-17**, reserving the post-cutoff range for a single pre-registered final
test. There is **no pre-cutoff options data and no pre-cutoff intraday substrate**
in this workspace. So this family cannot even reach the development stage lawfully,
let alone a sealed test. [FACT — `SEAL.md`; §1.1–1.2 above.]

### 1.4 Data-wall conclusion

**This trade cannot be tested in this workspace with lawful data.** That is not a
partial finding to be worked around — it is a complete and sufficient answer to the
"how much money could be made" question: *we cannot know from here, and cannot
lawfully find out from here.* Everything below (§2–§9) explains why, even with
perfect data, the specific trade is structurally a loser — so the data wall is not
merely blocking a good idea; it is blocking an idea that the structure already
condemns.

---

## 2. The 15:15 handicap — you forecast across the window that carries the news

The overnight gap (close-to-open) is dominated by information that arrives **after**
the NSE cash session closes (15:30 IST) and, critically, **after 15:15**:

- **The US cash session.** SPX/Nasdaq trade 19:00–01:30 IST (roughly). The prior
  US night is the single largest driver of the Indian open. At 15:15 IST it has
  **not happened yet.** [FACT — session times.]
- **Overnight crude, FX, and Asian markets.** Brent/WTI settle after the NSE close;
  USD/INR and Asian equities move overnight. This is precisely the
  **non-synchronous-timing** channel `macro_beta_diagnostic.md` measured: the
  *lagged* crude beta (SPEC-L1) was **stronger and broader** than the
  contemporaneous one (16 FDR survivors vs 6), because "NSE closes 15:30 IST while
  Brent settles afterwards, so yesterday's crude move is partly news the Indian
  market prices at today's **open**." The macro memo's finding is the mechanism of
  the overnight gap: **stocks (and the index) catch up at the open to global moves
  that became public overnight.** [FACT — `macro_beta_diagnostic.md` §6/§9.]
- **GIFT Nifty (the offshore Nifty future).** Trades nearly around the clock across
  two sessions; by ~9:00 IST it has absorbed the US close and Asia, and it
  **essentially pins the NSE open** (§3). At 15:15 the prior day it has barely begun
  to price the overnight information.

So a forecast made at **15:15 is structurally handicapped versus one made at 9:00.**
You are being asked to forecast the gap *across the very window that carries the
information that determines it.* Whatever is knowable at 15:15 (the day's own trend,
current macro levels) is, almost by definition, the part **already in the 15:30
close** — the residual overnight move is what is *new*, and the new part is the
post-15:15 flow you cannot see. This is the same conceptual point the crude memo
made about the lagged beta being *catch-up, not forecasting*: the information exists,
but it becomes public **after** the moment you must act.

**Relation to `macro_beta_diagnostic.md`.** That memo is the load-bearing prior
here in two directions at once. It CONFIRMS the overnight gap has real, identifiable
structure (the global-catch-up channel is measurable). And it CONDEMNS the 15:15
trade, because the structure it found is precisely information that arrives *after
the close* — i.e. after 15:15 — which the memo was careful to label an
**EXPOSURE, not an alpha**, tradeable only if the driver (crude, FX, US) is itself
forecastable at 15:15, which it is not.

---

## 3. Even a PERFECT open forecast is not a tradeable edge

Grant, counterfactually, a perfect 9:15 NIFTY-open forecast made at 15:15. It still
does not pay, for a structural reason:

- **The NSE open mechanically prints near GIFT Nifty**, which by ~9:00 IST is
  public and has already priced the overnight information. The open is therefore
  **not a tradeable surprise** — it is the resolution of information that anyone
  watching GIFT Nifty already sees. [FACT — GIFT Nifty is a continuously-quoted,
  publicly-observable offshore future; the NSE pre-open auction (9:00–9:08) converges
  to it. General market structure; specific convergence statistics **unverified at
  source this session** — no number is asserted.]
- **Reading GIFT Nifty at 9:00 is not alpha.** It is a public price. A strategy whose
  "forecast" is "look at GIFT Nifty" has no informational edge — it is competing on
  *latency* to act on a known input, an HFT-adjacent game, not a research family for
  a ₹100 Cr book. This is the identical conclusion the crude memo reached about the
  overnight open-gap being "a latency game, competing on **latency, not insight**…
  first to be arbitraged" (crude memo §3). [FACT — cross-reference.]
- **The option cannot even be sold into the 9:00 information.** To "sell at the next
  open (9:15)" you transact when NIFTY options begin trading (≈9:15/9:16), by which
  point the index has already gapped and the option has already **repriced to the new
  level AND the new (lower) overnight-uncertainty-resolved IV** (§4.3). There is no
  window in which you hold a stale option against fresh public information — the whole
  point of an opening auction is to remove exactly that.

So the "perfect forecast" branch collapses: the only forecast that would pay
(knowing the 9:15 open at 15:15) is unattainable because the information is
post-15:15; and the attainable version (reading GIFT at 9:00) forecasts a public
price with no surprise left to trade.

---

## 4. The options wrapper is a systematic loser for the overnight LONG buyer

This is the intellectual core, and it holds **independently of any forecast skill**.
Even granting a fair coin on direction — or perfect data — the *wrapper* the operator
specified (buy an option at 15:15, sell at 9:15) is documented to lose on average.
Four charges, then the break-even.

### 4.1 Charge A — overnight theta (time decay across a non-trading window)

An option's extrinsic value decays with time. The ~18 clock hours from 15:15 to 9:15
the next morning include a full **non-trading overnight period the option is priced to
decay through.** For a short-dated NIFTY weekly (the liquid instrument), a large share
of the remaining extrinsic value is theta, and holding it overnight *pays that decay in
full while the market is closed.* The long buyer is **short nothing and long theta-bleed** —
the position loses value from the mere passage of the night, before the index moves at
all. [FACT — definition of theta; the *magnitude* is instrument-specific and
**unverified** here, see §4.5.]

### 4.2 Charge B — the overnight variance risk premium (the decisive one)

Options are priced off **implied** volatility; the gap that actually occurs is
**realised** overnight variance. The documented, robust empirical regularity is that
**overnight implied vol systematically exceeds the realised overnight gap magnitude** —
i.e. the option is priced for a bigger night than the night usually delivers. The direct
consequence: **overnight option BUYERS lose on average, and the profitable side is SHORT
overnight premium.** This is the variance risk premium (VRP) applied to the specific
close-to-open window. [FACT — direction is the mainstream VRP finding, §7; the
overnight-specific version is Muravyev–Ni type evidence, **[unverified at source this
session]**; no coefficient asserted.]

Two things follow immediately, both fatal to the operator's framing:

1. **The trade the operator described is the LOSING side of a documented trade.** Long
   overnight premium is, on average, a negative-expectancy position *before any friction
   or any forecast error.*
2. **The winning side (short premium) is not what was asked for.** Selling overnight
   options harvests the VRP but is a **large-/unlimited-risk** position (a single gap
   through the strike is a multiple-of-premium loss). That contradicts the operator's
   stated "small capital, no big risk" constraint. See §9 — it is a different strategy
   with a different risk signature and a full unmet governance path.

### 4.3 Charge C — the double bid-ask spread AND the overnight IV crush

- **You cross the spread twice:** buy at the ask at 15:15, sell at the bid at 9:15. For
  liquid ATM NIFTY weeklies the spread is tight in absolute index points but **material
  relative to a typical overnight P&L**; for anything off-ATM or in a far weekly it
  widens fast. [FACT — spreads are crossed twice; magnitude **unverified**, §4.5.]
- **IV crush compounds it for a correct directional call.** Suppose you correctly buy a
  call and the index gaps UP. At 9:15 the option gains on **delta** — but the overnight
  uncertainty has now *resolved*, so implied vol falls, and the position **loses on
  vega**. This is the well-known retail experience of "the index gapped my way and my
  call barely moved": delta gain net of IV crush and theta. The favorable-direction
  payoff is smaller than a naive delta calculation implies. [FACT — vega/IV mechanics.]

### 4.4 Charge D — the directional double-condition (for a single call OR put)

A single directional option needs **two** things at once: (i) predict the **direction**
correctly, and (ii) have the favorable move **exceed premium decay + spread**. A
straddle (buy both) removes (i) but **doubles the premium and doubles the theta** and is
the *pure* long-VRP position of §4.2 — the canonical losing side. So the operator faces a
dilemma with no good horn: single-leg = must forecast direction across the window that
hides the information (§2); straddle = pay double to sit on the documented losing side of
the VRP.

### 4.5 The break-even condition (symbolic — NO number fabricated)

For a **single ATM directional** option, with Δ ≈ 0.5, the overnight P&L in index
points is approximately

> **P&L ≈ Δ·G_favorable − Θ_overnight − IVcrush − 2·(½·spread) − charges**

where `G_favorable` is the *signed, correctly-predicted* overnight move (points),
`Θ_overnight` the overnight theta, `IVcrush` the vega loss from overnight-uncertainty
resolution, `spread` the option bid-ask, and `charges` the statutory/brokerage stack
(§4.6). Break-even requires

> **Δ·|G| > Θ_overnight + IVcrush + spread + charges**, i.e.
> **|G| > (Θ_overnight + IVcrush + spread + charges) / Δ ≈ 2·(Θ_overnight + IVcrush + spread + charges)** at Δ≈0.5.

**The load-bearing comparison is:** *expected |overnight gap|* (LHS) versus *(overnight
premium decay + IV crush + 2×½-spread + charges)* (RHS), **both in index points.**

I will **not** fabricate the two magnitudes — doing so is TRAP 4, and neither an option
premium series nor a gap series is lawfully available here (§1). What can be stated
honestly:

- **[ASSUMPTION / order-of-magnitude, flagged]** NIFTY overnight gaps are *typically* a
  few tenths of a percent of the index in magnitude, with a fat tail on event nights;
  the *median* night is small. The premium + theta + spread of a short-dated ATM weekly
  is a *comparable* order of magnitude to a typical gap, which is exactly why the trade
  is marginal-to-negative even before the VRP tilt. **These are ranges I cannot pin
  without an options data source and an index intraday series — both barred here (§1).
  No specific premium, gap or spread number is asserted.**
- **[FACT, structural]** The VRP result (§4.2) says the RHS *embeds a premium over* the
  expected LHS by construction. So `E[Δ·|G|] < E[Θ_overnight + IVcrush + …]` for the
  *straddle* (direction-agnostic) case **before friction** — the expected break-even is
  not merely unmet, it is unmet by design of how the option was priced.

### 4.6 Option friction is structurally HIGHER than the equity friction the program measured

The crude memo established the **equity delivery** round-trip floor at **~32 bps**
(statutory ~22.4 bps, ~89% irreducible STT on notional, + ~5 bps/side slippage; RULING 5,
`src/costs_in.py`) and showed the underlying open-gap (~8 bps expected at β≈0.08) is
**already friction-dominated.** The options stack is a *different and generally heavier*
tax on the small overnight P&L:

- **STT on options is charged on the SELL-side premium** (not notional), plus exchange
  transaction charges, SEBI turnover fee, stamp duty, GST on (brokerage + txn charges),
  and brokerage per leg. **[ASSUMPTION — the exact option STT/txn rates are NOT in
  `costs_in.py`, which is the equity-delivery stack; the option rates are unverified at
  source this session and are deliberately not quoted.]**
- **The dominant option cost is the twice-crossed bid-ask spread**, which for a small
  overnight P&L is large in *relative* terms — the same lesson as equities, amplified,
  because the option's expected overnight move is a *fraction* of the index gap (Δ<1) yet
  the spread is paid in full.
- **Net:** whatever the precise option rates, the friction-to-expected-P&L ratio is
  **worse** than the equity case the program already judges unviable, because the numerator
  (spread + theta + charges) is comparable to the equity case while the denominator (the
  option's overnight P&L) is the *attenuated, VRP-taxed* gap. The crude memo's "~8 bps vs
  ~32 bps" underlying result is the *optimistic* bound; the option wrapper is worse.

**Conclusion of §4:** independent of forecast skill and independent of the data wall, the
specified trade is a negative-expectancy structure — long theta, long the VRP, twice
across the spread, and (single-leg) contingent on a direction call made across the
information window. **The wrapper loses on average.**

---

## 5. Turnover — the highest-turnover shape the program keeps killing

This is a **DAILY round trip** — buy every afternoon, sell every morning. It is the
**highest-turnover design possible**, and turnover-driven friction is this program's
single most-repeated cause of death:

- **The killed legacy system:** real gross alpha ~18.5%/yr (t≈2.95) **fully consumed by
  friction at 1.6 round-trips/day.** "Gross alpha was never the constraint; friction
  was." [FACT — CLAUDE.md.]
- **`DIAG-BREAKOUT-ENTRY-0001` (2026-07-23):** DO-NOT-BUILD on the same friction-hurdle
  logic. [FACT — crude memo §1/§9 cross-reference.]
- **The crude-forecast memo (2026-07-23):** DO-NOT-BUILD; the overnight open-gap is a
  friction-dominated latency game. [FACT — `crude_forecast_engine_feasibility.md`.]

The ROADMAP's standing rule is explicit: *"New families must be low-turnover by
design."* A daily-round-trip overnight-options book is the **antithesis** of that rule,
and it stacks the *heaviest* friction wrapper (options) on the *highest* turnover
(daily) — the two worst choices simultaneously. Nothing about the friction verdict is
new here; the trade simply re-presents the program's oldest killed shape in a more
expensive costume.

---

## 6. Is there ANY real 15:15-knowable predictability? (Small, post-hoc, not ours)

Being fair rather than dismissive — is *any* part of the next open forecastable at 15:15?

- **A little, and it is the part already in the close.** The day's own trend/close level
  is knowable at 15:15, but it is (nearly) fully reflected in the 15:30 print. The
  *incremental* overnight move is what is new, and §2 showed the new part is post-15:15
  flow (US, crude, FX, GIFT) — **not** knowable at 15:15.
- **The macro-factor levels are knowable at 15:15**, and `macro_beta_diagnostic.md`
  established real, economically-coherent index/stock loadings on crude and USD/INR. But
  a *level* known at 15:15 is not a *change* forecast: the overnight *move* in those
  factors is what drives the gap, and that move happens after 15:15. A beta is an
  **exposure, not an alpha** (macro memo §11) — it tells you the gap's *sensitivity*,
  not its *sign*.
- **GIFT Nifty is the one genuinely predictive input — but it predicts at ~9:00, not
  15:15**, and predicting a *public price with no surprise left* is a latency game, not
  research alpha (§3).

So the honest answer: **the 15:15-knowable predictability of the next open is small, is
mostly the already-priced close, and the genuinely predictive information (overnight
global flow, crystallised in GIFT Nifty) arrives after 15:15 and is public before the
option is tradeable.** There is no 15:15 informational edge to build a family on — and
even if there were, §4 shows the option wrapper would tax it away. (Confirming *any* of
this quantitatively — even the gap distribution conditioned on a 15:15 signal — would be
a TRIAL under AMENDMENT A and is **not** done here.)

---

## 7. Literature pass (tiered — [PR]/[WP]/[VM]; all [unverified at source this session])

**Tiering** (per `analysis/QFM_literature_prior.md`): **[PR]** peer-reviewed · **[WP]**
working paper / preprint · **[VM]** vendor / broker / practitioner marketing
(**systematically biased toward positive claims**; never cited as evidence for an
effect). **SESSION-HONESTY (TRAP 4):** web budget exhausted before this memo; scratchpad
holds only the momentum equity corpus (Jegadeesh-Titman, Novy-Marx, TSM, Nagel, GHZ, HXZ)
— **no overnight-options or VRP PDFs.** I opened **no source**; every citation is domain
knowledge, directions only, **no coefficient quoted**. Any spec must re-fetch and read
these digit-by-digit before freeze.

### 7.1 Overnight vs intraday return decomposition
- **[PR] Lou, Polk & Skouras — "A tug of war: Overnight versus intraday expected returns"**
  (*J. Financial Economics*, 2019). Overnight and intraday returns have **systematically
  different, even opposing, drivers** (institutional vs retail clienteles). Establishes
  the overnight window is a distinct return regime — but as a *cross-sectional* return
  pattern, **not** a 15:15-actionable index-open forecast. [unverified this session]
- **[PR] Bogousslavsky — "The cross-section of intraday and overnight returns"** (*JFE*,
  ~2021). Overnight returns carry a large share of several anomalies; timing/clientele
  effects. Again cross-sectional, not a directional open-forecast. [unverified]
- **[PR] Cliff, Cooper & Gulen; and the "overnight drift" literature** (e.g. Boyarchenko/
  Larsen/Whelan-style intraday pattern work). The documented regularity is an *average*
  positive overnight drift concentrated in specific windows — a **risk-premium/clientele**
  phenomenon, **not** a conditional 15:15→9:15 direction signal, and it is an *average
  tilt*, not something an option's theta+VRP+spread survives. [unverified]
- **[WP] Lachance — overnight/"night trading" returns.** Same theme: overnight is a
  distinct, largely risk-premium-driven regime. [unverified]

### 7.2 Variance risk premium and overnight straddle returns (the core adverse evidence)
- **[PR] Carr & Wu — "Variance Risk Premiums"** (*Review of Financial Studies*, 2009).
  The VRP is **negative and large**: option *buyers* pay a premium; sellers earn it. The
  foundational result behind §4.2. [unverified]
- **[PR] Bakshi & Kapadia — delta-hedged option returns** (*RFS*, 2003). Delta-hedged
  (direction-stripped) long-option positions earn **negative** average returns — a direct
  measure that being long options/vol loses on average. [unverified]
- **[PR/WP] Muravyev & Ni — overnight vs intraday option returns** ("Why do option
  returns change sign from day to night?"). The **on-point** paper: option returns differ
  systematically **overnight vs intraday**, and the **overnight** leg is where long-option
  positions do **worst** — the specific evidence that the operator's overnight-long is the
  losing leg. [unverified — treat as the single most important citation to re-open before
  any spec.]
- **[PR] Coval & Shumway — "Expected option returns"** (*J. Finance*, 2001). Long option
  positions carry negative expected returns consistent with a priced volatility factor.
  [unverified]
- **[VM] — the "sell options for daily/overnight income" ecosystem.** This space is
  **saturated** with vendor marketing. Treated ruthlessly: it is directionally *correct*
  that the earning side is SHORT premium (consistent with the [PR] VRP evidence), but it
  **systematically hides the tail risk** (a gap through the strike) that makes the earning
  side violate "small capital, no big risk." Cited only to characterise the environment,
  **never** as evidence. [VM]

### 7.3 Index-open predictability from offshore futures
- **[VM/practitioner, thin academic]** That **SGX/GIFT Nifty pins the NSE open** is
  well-established practitioner knowledge and the basis of routine "GIFT Nifty indicates a
  gap-up/down open" commentary. Formal peer-reviewed treatment is thin; the point is
  market-structure, not anomaly. Reinforces §3 (the open is public before it is
  tradeable), it does **not** provide a tradeable 15:15 edge. [unverified]

### 7.4 India-specific NIFTY overnight-gap evidence
- **[WP/PR, thin]** Indian studies of overnight gaps / global-cue spillover (SGX Nifty,
  US markets → Nifty open; volatility spillover, GARCH/VAR) generally find
  **contemporaneous linkage and volatility spillover driven by global cues**, consistent
  with §2's non-synchronous-timing channel, but **no credible out-of-sample directional
  gap-prediction net of cost.** Thinner and lower-tier than the US work. [unverified —
  directional prior only.]

**What the literature does NOT provide:** any credible, out-of-sample, cost-surviving
demonstration that a **15:15-conditioned** signal predicts the NIFTY open direction *and*
that a **long overnight option** monetises it. The strongest, most on-point body of work
(VRP; overnight option returns; delta-hedged option returns) says the **opposite** — the
overnight long-option side is the documented loser.

---

## 8. Relationship to the program

- **To `macro_beta_diagnostic.md`.** That memo IS the mechanism of the overnight gap
  (global catch-up at the open) and simultaneously its condemnation: the structure it
  measured is post-15:15, already-public information — an **exposure, not an alpha**. It
  tells you the gap's sensitivity to crude/FX, not its sign, and not at 15:15.
- **To `crude_forecast_engine_feasibility.md`.** Same session, same terminal logic. That
  memo already ruled the overnight open-gap a **friction-dominated latency game** (~8 bps
  expected gap vs ~32 bps round-trip in the *underlying*), competing on latency not
  insight, and "not ours." This memo wraps that same gap in an **options** structure that
  is *heavier* on friction and *negative-expectancy by construction* (VRP), so the crude
  memo's "no" carries over a fortiori.
- **To the killed legacy system.** Same diagnosis, worst-case parameters: highest possible
  turnover (daily) × heaviest wrapper (options) × the friction wall that killed a
  genuinely-positive-gross-alpha system. "Gross alpha was never the constraint; friction
  was" — and here there is no established gross alpha to begin with.
- **To the DIAG-VOLSHARE intraday-data limit.** DIAG-VOLSHARE is the precedent that
  **fixed the intraday data boundary**: yfinance ≈ 60 days of 5-minute bars, deeper needs
  Kite = refused. This memo inherits that boundary directly — a 15:15→9:15 study is
  intraday, and the substrate does not lawfully exist (§1.2).
- **To the shadow-slot state.** Both slots are held (QFM, PEAD); AG-01 and 52WH are
  queued. An overnight-options family would be a **new family behind all of them**, with a
  weaker prior than any of them and a barred data path. It does not jump the queue; it
  does not join it.

---

## 9. The only defensible reframing — and why it is refused here

If one insists on a defensible version, it is **not** the operator's trade. It is the
**opposite side**: a **short-overnight-premium (VRP-harvest)** strategy — systematically
SELLING the overnight option/straddle to earn the variance risk premium (§4.2, §7.2). It
is defensible *because* the [PR] evidence says that side has positive expectancy. But:

- **It is a different strategy the operator did not ask for**, with an inverted risk
  signature: many small wins punctuated by rare large losses when the index gaps through
  the strike — **large/near-unlimited tail risk** that **violates the operator's "small
  capital, no big risk"** constraint. The [VM] ecosystem sells exactly this while hiding
  exactly that tail (§7.2).
- **Its full governance path is entirely unmet**, and this memo authorizes none of it:
  1. a **drafted spec** with a **pre-stated null** (the honest null: *a short-overnight-
     premium book does not survive its own tail + friction net of cost*);
  2. **hash-freeze** (`src/spec_guard.py`) — no spec exists;
  3. a **shadow slot** — **both are held (QFM, PEAD)**; AG-01/52WH queued ahead;
  4. a **registered, SPA-gated trial** (RULING 7 — Hansen SPA gates, DSR reports);
  5. **a lawful options data source** — which **does not exist** under the binding rules
     (§1: Kite forbidden, exchange scrape ToU-blocked). Even the defensible reframing hits
     the same data wall.
  6. an explicit **tail-risk / margin / capacity** treatment, because the whole point of
     the strategy is that its risk lives in the tail, not the mean.

**This is named only so the "no" is a reasoned position, not a reflex. It is not
endorsed, not queued, and not authorized.**

---

## 10. Proposed register row (TEXT ONLY — operator to enter; this memo does NOT write it)

Consistent with the `DIAG-BREAKOUT-ENTRY-0001` / `DIAG-CRUDE-FORECAST-0001` precedent
(outcome-blind DO-NOT-BUILD scoping rows, no trial spent).

```
trial_id:    DIAG-OVERNIGHT-OPT-NIFTY-0001
date:        2026-07-23
family:      n/a (outcome-blind feasibility; NOT a spec family; consumes NO shadow slot)
description: Feasibility/scoping of a 15:15-IST NIFTY-open direction forecast monetised by buying a NIFTY index call/put at 15:15 and selling at the 9:15 next open (operator question 2026-07-23). Sibling: single-stock version DIAG-OVERNIGHT-OPT-STOCK-0001.
data_tier:   n/a
result:      DO-NOT-BUILD; and CANNOT BE TESTED HERE (no options data + no lawful pre-cutoff intraday substrate).
notes:       OUTCOME-BLIND, NO TRIAL SPENT (cumulative trial count UNCHANGED at 53), NO SHADOW SLOT, no repo outcome data conditioned on any signal, no spec drafted, no hash frozen, no broker/Kite call, no NSE/BSE option-chain scrape, FINAL_TEST never set; web budget exhausted (NO source opened this session, all literature marked unverified-at-source). Analysis: analysis/nifty_overnight_options_feasibility.md. FINDINGS: (1) DATA WALL, decisive: ZERO options data of any kind in the repo (no option-price series, no IV surface, no chain - confirmed by inspection); none lawfully obtainable (Kite = BINDING RULE 3; NSE/BSE option history = scrape under unresolved ToU OPEN OPERATOR DECISION 1). Trade is intraday by construction; DIAG-VOLSHARE fixed the intraday boundary (yfinance ~60d 5-min, deeper needs Kite, refused) and there is NO pre-cutoff options data so even SEAL-required development (<2024-07-17) is unsupported. Cannot be tested here with lawful data. (2) The 15:15 forecast is structurally handicapped: the overnight gap is dominated by POST-15:15 information (US cash session, overnight crude/FX/Asia, and GIFT Nifty which by ~9:00 IST pins the NSE open) - you forecast across the very window that carries the info; this is macro_beta_diagnostic's non-synchronous-timing channel (stocks catch up at the open to already-public global moves) = EXPOSURE not alpha. (3) Even a PERFECT open forecast is not an edge: the NSE open mechanically prints near GIFT Nifty (public, priced, no surprise); reading GIFT at 9:00 is latency not alpha; and the option only trades at ~9:15 already repriced to the new level + crushed IV. (4) The WRAPPER loses on average independent of skill: long overnight THETA + long the overnight VARIANCE RISK PREMIUM (overnight IV > realised gap => overnight option BUYERS lose on average; winning side is SHORT premium = unlimited risk, violates 'small capital no big risk') + DOUBLE bid-ask spread + IV crush; single-leg also needs a correct direction call. Break-even: E|overnight gap| in index points vs (theta + IV crush + 2x half-spread + charges) - both marked ASSUMPTION/unverified, NO premium/gap/spread number fabricated (TRAP 4); VRP makes the straddle break-even unmet BY CONSTRUCTION before friction. (5) Option friction is structurally HIGHER than the equity ~32bps floor (RULING 5/costs_in.py is equity-delivery only; option STT-on-premium/txn/spread NOT quoted, unverified) applied to the crude memo's already-friction-dominated ~8bps-gap underlying result. (6) DAILY round trip = highest-turnover shape, heaviest wrapper - the exact friction-dominated design the program has killed (legacy, breakout, crude); ROADMAP requires low-turnover by design. (7) Literature (Carr-Wu VRP; Bakshi-Kapadia delta-hedged; Muravyev-Ni overnight option returns; Coval-Shumway; Lou-Polk-Skouras / Bogousslavsky overnight-vs-intraday; SGX/GIFT-Nifty pins open; India global-cue spillover) - ALL UNVERIFIED AT SOURCE, directions only - the on-point body says the overnight LONG-option side is the documented LOSER; the [VM] 'sell-options-for-income' space is saturated and hides tail risk. Only defensible reframing = SHORT-overnight-premium VRP harvest = a DIFFERENT, large-tail-risk strategy the operator did not ask for, violating 'no big risk', with a full unmet governance path (spec + pre-stated null + hash-freeze + shadow slot [BOTH HELD] + registered SPA-gated trial + a LAWFUL options data source that does not exist here); THIS MEMO AUTHORIZES NONE OF IT.
```

---

## 11. Open items that must close BEFORE any overnight-options spec could be drafted

1. **A lawful options data source** — the gating blocker. No option-price/IV history
   exists in-repo and none is lawfully obtainable (Kite barred; exchange scrape
   ToU-blocked). This depends on **OPEN OPERATOR DECISION 1** (exchange ToU) and/or an
   authorised vendor (the CLAUDE.md notes **Accord Fintech / ACE Datafeed** surfaced as an
   authorised BSE/MCX vendor — an equivalent for option history would have to be sourced,
   licensed, and PIT-audited). Until this closes, *nothing* — not even development — is
   possible.
2. **A lawful pre-cutoff INTRADAY index substrate** (15:15 and 9:15 marks) for the
   underlying signal side — same Kite/ToU wall as DIAG-VOLSHARE.
3. **Option-specific friction constants** — `costs_in.py` is the equity-delivery stack;
   option STT-on-premium, exchange txn, stamp, GST-on-charges and a realistic
   **bid-ask-spread model** would need to be sourced and pre-registered (RULING 5 analogue
   for F&O). None are quoted in this memo.
4. **DSR reporting band** (RULING 7, proposed 0.35/0.50/0.70 — still PENDING) — any future
   scoring inherits it.
5. **A shadow slot must free up** — both held (QFM, PEAD); AG-01 and 52WH queued ahead.
6. **If the reframing (short premium) were ever pursued**, an explicit tail-risk / margin /
   capacity treatment and a curve/benchmark-relative scoring rule — because its expectancy
   lives in the tail, not the mean (§9).

---

## 12. Verdict (recap)

**DO NOT BUILD, and it CANNOT BE TESTED in this workspace with lawful data.** The data
wall alone (§1 — no options data, no lawful pre-cutoff intraday substrate, no development
data) is a complete and sufficient answer. Beyond it: the 15:15 forecast is handicapped by
the post-15:15 arrival of the information that determines the gap (§2); even a perfect open
forecast is not a tradeable surprise, because the open is pinned by public GIFT Nifty (§3);
the long-overnight-option wrapper is a documented systematic loser — theta + variance risk
premium + double spread + IV crush, with a break-even that exceeds the typical gap and, for
the straddle, is unmet *by construction* (§4); the option friction stack is heavier than the
equity ~32 bps floor already judged unviable (§4.6); and it is the highest-turnover,
heaviest-wrapper version of the exact design the program keeps killing (§5). The only
15:15-knowable predictability is small, already in the close, and public-before-tradeable
(§6); the literature's most on-point body says the overnight long-option side is the loser
(§7). The one defensible reframing (short-premium VRP harvest) is a different, large-tail-
risk strategy the operator did not ask for and did not consent to the risk of, with a full
unmet governance path (§9).

**NO TRIAL SPENT. Cumulative trial count unchanged at 53. No shadow slot. No spec drafted.
No repo outcome data conditioned on any signal. No broker/Kite call. No option-chain
scraping. No number fabricated.**


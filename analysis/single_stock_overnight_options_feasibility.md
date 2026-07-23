# Single-Stock Overnight Options — Feasibility / Scoping Memo

**Question (operator, 2026-07-23):** For any stock other than the NIFTY index
that has listed options, can we leverage the infrastructure this program has
already built to make money from options on a 12–24 hour (overnight) timeframe —
with **small capital only** and **no big risk**?

**Sibling memo:** `analysis/nifty_overnight_options_feasibility.md` OWNS the NIFTY
index-option case and the **shared overnight-options-microstructure core** (theta
decay, the overnight variance-risk-premium, the double bid-ask spread, why the
long overnight buyer is the losing side, the 15:15 / GIFT-Nifty timing handicap).
**This memo does not reproduce that core; it cross-references it** and adds only
the three things that make *single-stock* options **strictly worse** than the
index case the sibling already rules out.

---

## GOVERNANCE HEADER (read first)

- **OUTCOME-BLIND feasibility / scoping memo.** Infrastructure inventory, options
  market-structure and friction ARITHMETIC from public contract specs and first
  principles, and free external literature only. Under
  `CONTAMINATION_POLICY.md` AMENDMENT A, "cost tables" and market-structure /
  correlation characterisation are explicitly free; **no option or strategy
  return is conditioned on any signal anywhere in this memo.**
- **"Make money from options" is a TRIAL, and this memo does not run it.** A
  conditional/performance summary of any option position (straddle return,
  directional hit-rate, Sharpe, hit-rate) is, under AMENDMENT A, a **TRIAL**
  requiring a hash-frozen spec, a pre-registered register row and a shadow slot.
  **Both shadow slots are held (QFM, PEAD); AG-01 and 52WH are queued.** This
  memo spends **NO TRIAL** (cumulative trial count stays at **53**), consumes
  **NO SHADOW SLOT**, drafts **NO SPEC**, freezes **NO HASH**.
- **FORBIDDEN and not done:** any backtest; any option P&L / straddle /
  directional / hit-rate / Sharpe from data; any conditional or forward return;
  any price-panel load for outcome measurement; any live broker/Kite call
  (BINDING RULE 3); any scraping of NSE/BSE option-chain endpoints (exchange ToU
  unresolved — OPEN OPERATOR DECISION 1); writing to
  `governance/research_register_v2.csv`; setting `FINAL_TEST`.
- **Register:** `research_register_v2.csv` was **read, not written**. A
  **text-only** proposed row is offered in §9 for the operator to append.
- **Source tiers** (`analysis/QFM_literature_prior.md` convention), on every
  external citation: **[PR]** peer-reviewed · **[WP]** working paper / preprint ·
  **[VM]** vendor / broker / practitioner marketing (**systematically biased
  toward positive claims** — never cited as evidence for an effect).
- **SESSION-HONESTY NOTE (TRAP 4).** This session's WebSearch budget is
  **exhausted (200/200)** and the scratchpad holds **no options PDFs** (only the
  QFM/PEAD momentum corpus). **I opened NO options source this session.** Every
  literature citation below is domain knowledge, marked
  **[unverified at source this session]**; I quote **no** spread, premium, IV,
  coefficient or liquidity number I cannot re-open. Directions of findings are
  textbook and I am confident in them; precise figures are deliberately withheld
  (a disclosed gap is an asset; an invented number is a liability — TRAP 4).
- **FACT / ASSUMPTION / unverified** tags on every material input.

---

## VERDICT (stated first, argued below)

> ## **DO-NOT-BUILD / CANNOT-ASSESS-HERE.** Four independent walls, each decisive on its own; together, conclusive.

1. **There is NO options infrastructure to "leverage."** The blunt finding, and
   the centrepiece (§2): every module this program has built is **equity-only**.
   There is **no options data gate, no options data of any kind in the repo, no
   options pricing, no IV / greeks anywhere, no options settlement engine, and no
   options cost model** — `costs_in.py` is a cash-equity STT stack and options
   STT is charged on a **different base at a different rate** (§2.6). "Leverage
   the infra" is **not available**, because the infra does not speak options.
   Confirmed by direct source audit: a grep of `src/` for
   `option|implied.?vol|greek|vega|theta|delta.?hedge|strike|straddle` returns
   **only** the Python word `Optional`, `OPTIONAL_COLS`, and "Option 1 ruling" —
   **zero** options-instrument handling. [FACT — audited this session.]

2. **Single-stock options are STRICTLY WORSE than the index case the sibling
   already kills** (§1). NIFTY has the deepest, most liquid option book in the
   market; single-stock options are **monthly-expiry only** (no weeklies), listed
   on a **limited universe (~180–190 underlyings, ASSUMPTION)**, with liquidity
   concentrated in the **near-month ATM strike** and negligible open interest
   away from it for many names. The "double bid-ask spread" tax the sibling
   describes for the index is **multiples larger** here, and the overnight tails
   are **fatter** (idiosyncratic single-name gap risk: earnings, block deals,
   corporate-action news). Everything wrong with the index case is more wrong for
   a single name.

3. **"Small capital, no big risk" is incompatible with the only positive-
   expectancy side** (§3). The overnight variance-risk-premium accrues to the
   option **SELLER** (short premium) — a large / unlimited-tail position, the
   **opposite** of "no big risk." The **long-premium** side the operator's
   framing implies ("buy a call/put overnight") is the **documented net loser**
   (delta-hedged option returns are on average negative — §4). And single-stock
   overnight options carry **fatter idiosyncratic tails** than the index, so both
   sides are worse: the seller's tail is fatter (larger blow-up) and the buyer
   pays a **steeper theta+spread tax** for it. **"Sell overnight premium for safe
   income" and "small capital, no big risk" cannot both hold.**

4. **It is UNTESTABLE in this repo** (§5). No options data of any kind exists
   here; the seal protocol needs dev data **< 2024-07-17** and **no pre-cutoff
   options substrate exists**; the only lawful equity intraday tape is yfinance's
   ~60-day 5-minute horizon (the Kite path that reaches deeper is BINDING RULE 3
   forbidden — see `DIAG-VOLSHARE`, `block_trade_detection_feasibility.md`), and
   there is **no option analogue at all**. The question cannot be measured here
   even if the governance slots were free.

**Strongest evidence FOR (stated fairly):** a *long straddle bought specifically
into a scheduled single-stock earnings event* is the one framing with a studied
academic rationale (§4.3) and a genuinely **defined-risk, small-capital** shape
(max loss = premium paid). If any narrow options idea survives scrutiny, it is
this one. **But** it is (i) an **EVENT** strategy that overlaps **SPEC-PEAD-01**
(earnings-drift, holding **shadow slot 2**), (ii) still requires an options data
source, an options cost/greeks model this repo lacks, and (iii) is authorised by
**nothing** in this memo — it needs a drafted spec + pre-stated null + hash-freeze
+ a shadow slot (both held) + a registered SPA-gated trial.

**Strongest evidence AGAINST:** the whole edifice. There is no infra to leverage,
the instrument is less liquid and higher-tailed than the index the sibling
already rejects, the profitable side violates the risk constraint, the loser side
violates the profit goal, and none of it is testable here. The operator's own two
constraints — *small capital* and *no big risk* — are the constraints that a
short-premium income book violates and a long-premium book satisfies only by
being the documented net loser after theta and a doubled single-name spread.

---

## 1. Why single-stock options are STRICTLY WORSE than NIFTY (distinct contribution #1)

The sibling memo rules out the **NIFTY** overnight-option case on the shared
microstructure core. This memo's job is to show the single-stock case inherits
**all** of that and adds three structural handicaps. NIFTY is the best-case
instrument for the operator's idea; a single stock is materially worse on every
axis that matters.

### 1.1 The universe is small and the products are coarser

- **Limited underlying universe.** Only a curated set of stocks has listed
  options at all — the NSE F&O eligibility list, of order **~180–190 underlyings**
  as of recent revisions. [ASSUMPTION — the count is revised semi-annually on
  liquidity criteria and was **not re-verified this session**; treat as
  order-of-magnitude, not precision. A stock outside this list has **no options
  to trade** regardless of the strategy.]
- **Monthly expiry only — no stock weeklies.** Single-stock options in India are
  **monthly-expiry** contracts; the weekly-expiry product exists (and after the
  SEBI 2024 expiry-rationalisation, exists only in a **single index** per
  exchange). [FACT on the structural point — stock options are monthly;
  **ASSUMPTION** on the exact post-2024 index-weekly detail, unverified this
  session.] This matters directly for a **12–24 hour** trade: with a monthly
  contract, an overnight hold sits on an option whose **time-to-expiry is
  weeks**, so a one-night move is a small fraction of the option's life and the
  position is dominated by **vega and spread**, not by the overnight directional
  move the operator wants. The index-weekly gives a sharper overnight instrument;
  the stock monthly does not.

### 1.2 Liquidity is concentrated and thin — the double spread is multiples larger

The sibling establishes that an overnight option round-trip pays the **bid-ask
spread twice** (in and out), on top of theta. For single stocks that tax is
**multiples larger** than for NIFTY, for structural reasons:

- **Liquidity clusters at the near-month ATM strike.** For many F&O stocks, open
  interest and tight quotes exist only around the **at-the-money strike of the
  near month**; strikes even a few increments away, and the next expiry, are
  **thinly quoted or quote-only** (market-maker quotes with wide spreads and
  little resting depth). [ASSUMPTION — the *direction* is textbook single-stock
  option microstructure; specific spread widths **unverified this session** and
  deliberately not quoted, TRAP 4.]
- **Wide relative spreads on the option.** Because the option premium is a small
  number and single-name option flow is a fraction of index flow, the **relative**
  bid-ask spread on a single-stock option is wide — wider than the underlying
  cash spread and wider than the corresponding NIFTY-option spread. A 12–24h hold
  cannot amortise a wide entry+exit spread the way a multi-week hold might. [FACT
  on mechanism; magnitudes unverified.]
- **The tax is paid on BOTH legs and is not scaled by the small overnight edge.**
  This is the same structural killer as the equity friction wall the program has
  hit repeatedly (killed legacy system; `DIAG-BREAKOUT-ENTRY-0001`;
  `crude_forecast_engine_feasibility.md` §7): a **fixed, unscaled** round-trip
  cost meeting a **small** expected edge. Here the fixed cost (doubled option
  spread + theta over one night) is *larger* than the index case and the edge is
  no larger — often smaller, because a single name's overnight variance risk
  premium is noisier than the index's.

### 1.3 The tails are fatter — idiosyncratic single-name gap risk

An index gaps overnight on macro news; a **single stock** gaps overnight on all
of that **plus** idiosyncratic events the index averages away:

- **Scheduled earnings** (the one place a long-premium overnight bet has a
  rationale — §4.3 — but also the largest overnight gap source).
- **Block / bulk deals** disclosed post-close (cross-ref
  `analysis/block_trade_detection_feasibility.md`: bulk deals are disseminated
  **after market hours the same day**, so a stock can gap the next morning on a
  block print you learn about only that evening).
- **Corporate-action and Reg-30 news** (the PIT filing-timestamp corpus the
  program has scoped but cannot yet ingest — OPEN OPERATOR DECISION 1).

The consequence cuts **both ways and worsens both sides**: for the option
**seller**, the fatter single-name tail means a **larger blow-up** on a bad night
(directly contradicting "no big risk"); for the option **buyer**, the fatter tail
is *priced in* as a higher single-name implied vol, so the buyer pays **more
theta and a wider spread** for the same nominal exposure. Single-name overnight
options are the **worst of both**: a seller carries a bigger tail than the index
seller, and a buyer pays a steeper carry than the index buyer.

**§1 verdict:** on universe breadth, product granularity, liquidity/spread, and
tail fatness, single-stock overnight options are **strictly dominated** by the
NIFTY case — which the sibling memo already rejects. If the index version does not
clear the bar, the single-stock version cannot.

---

## 2. The infrastructure audit — what we have vs what options need (CENTREPIECE, distinct contribution #2)

The operator's phrase is "leverage the infrastructure this program has already
built." So the load-bearing question is not "would options work" (it is a trial we
cannot run) but **"is any of our infra actually usable for options?"** The honest
answer, module by module, is **no — the infra is equity-only and options need a
different stack that does not exist here.**

### 2.1 What the program's infrastructure actually is (all equity)

| Module | What it does | Instrument | Usable for an options book? |
|---|---|---|---|
| `src/data_gate.py` | The only sanctioned data door: research door (`load`, strips rows ≥ 2024-07-17) + Tier 1 forward door (`load_operational`) | **Equity** rec/ledger/OHLC rows, rec_key-joinable | **No.** Gates equity panels by date; has no concept of an option contract (underlying, strike, expiry, right, IV). Would reject an option chain as a "generic panel." |
| `src/paper_leg.py` | SOP settlement engine for **equity recs** — SL→T2→T1→TIME exit priority, gap-through open-fills, 5-session time exit, unadjusted prices, dividend crediting | **Equity** cash | **No.** Settles a long cash-equity position against OHLC levels. An option needs expiry settlement, exercise/assignment, intrinsic vs premium, and a pricing model — none present. |
| `src/overlay_alpha.py`, `scripts/overlay.sh`, `overlay_queue.py` | The live A/B measurement stack (paper "recommended" leg vs executed leg, rec_key join) | **Equity** recs | **No.** Measures the equity overlay; nothing about it maps to an option position. |
| 52WH stack (`pit_universe`, `expr`, `signal_52wh`, `screen_52wh`, `rebalance`, `backtest_52wh`, `build_price_panel`) | PIT constituent store, expression grammar, 52-week-high cross-sectional screen, rebalance calendar, EW backtest, **adjusted equity OHLC panel** | **Equity** prices/fundamentals | **No.** The panel is spot equity OHLC. There is no options chain, no IV surface, no greeks, no expiry dimension. |
| `src/costs_in.py` | Verified **cash-equity** statutory cost stack (STT, exchange txn, SEBI, stamp, GST, DP), RULING 5 | **Cash equity** | **No — and actively misleading if reused.** See §2.6: options STT is a **different rate on a different base**, and none of the option-specific costs are modelled. |
| `src/fetch_ohlc.py`, `scripts/ingest_snapshot.sh` | Unadjusted Tier 1 settlement OHLC fetch (yfinance) + nightly rsync of production equity outputs | **Equity** OHLC | **No.** yfinance serves equity OHLC, not option chains; the ingest rsyncs the equity production system. |
| `src/metrics.py`, `src/spec_guard.py` | IR/Sharpe/DSR/Hansen-SPA scoring; run-time freeze gate | **Instrument-agnostic** stats/governance | **Partially reusable** — the *statistics and governance plumbing* (SPA gate, freeze gate, DSR reporting) would carry over to **any** family, including an options one. This is the **only** part of the stack that is not equity-specific — and it is the generic scoring layer, not options machinery. |

### 2.2 What an options strategy would additionally need — none of which exists here

1. **An options data source** — historical option chains (per underlying, per
   strike, per expiry, per right) with **bid/ask** (not just last), open interest,
   and volume, timestamped. **Not in the repo; not fetchable from yfinance;
   not scrapeable (exchange ToU, OPEN OPERATOR DECISION 1); Kite forbidden
   (BINDING RULE 3).**
2. **An implied-volatility surface** and a **pricing/greeks model**
   (Black-Scholes-Merton or better, per-name IV, delta/gamma/vega/theta). **No IV
   or greek is computed anywhere in `src/` (grep-confirmed).**
3. **An options settlement / P&L engine** — expiry handling, exercise/assignment,
   overnight mark-to-market on premium, path from entry premium to exit premium.
   `paper_leg.py` settles **cash** positions and cannot represent this.
4. **An options cost model** — options STT, brokerage per lot, exchange
   transaction charges on premium turnover, stamp, GST, and (critically for an
   overnight straddle) the **bid-ask spread as the dominant cost**. `costs_in.py`
   models **none** of this correctly for options (§2.6).
5. **A liquidity / tradeability filter** specific to options — which
   underlying/strike/expiry is actually quotable at a tradeable spread on a given
   night. No such data and no such filter exist.

### 2.3 The blunt finding (do not soften)

**NONE of this program's infrastructure handles options.** It is an **equity**
research and measurement stack end to end: an equity data gate, an equity
settlement engine, an equity 52WH panel, an equity overlay/A-B stack, an
equity cost model. The **only** reusable component is the **instrument-agnostic
statistics/governance layer** (`metrics.py` SPA/DSR, `spec_guard.py` freeze) —
which is the scoring plumbing every family shares, **not** anything that makes
options tractable. "Leverage the infra we've created" is therefore **not
available for options**: the infra is equity-only, and an options book would have
to build a **new** data gate, pricing model, settlement engine, and cost model
from scratch — after first acquiring options data the program cannot lawfully
obtain here.

### 2.4 Corollary — this is the same wall as the sibling and the block-trade memo

The data barrier is identical in shape to the ones already documented:
`block_trade_detection_feasibility.md` (no lawful intraday tape; Kite forbidden;
60-day yfinance horizon) and `crude_forecast_engine_feasibility.md` (no PIT news
corpus). Options add a **new** missing layer on top — the entire derivatives
data/pricing/settlement stack — that none of those memos even needed to reach,
because equity data at least *exists* in the repo. **Options data does not exist
here at all.**

### 2.5 What WOULD carry over (being fair)

To not overstate: if, hypothetically, an options data source and pricing model
were built, the program's **governance and scoring discipline** would transfer
cleanly — SPA-gated verdicts (RULING 7), the DSR reporting caveat, the
hash-freeze/`spec_guard` protocol, the outcome-blind→trial contamination boundary,
the register accounting. That is real and valuable. But it is the **wrapper**, not
the **engine**: it tells you how to *score and govern* an options trial honestly;
it does nothing to *construct* the option position, price it, settle it, or cost
it. The engine is 100% missing.

### 2.6 The cost-stack trap — `costs_in.py` is EQUITY and options STT is different

A specific, concrete warning, because reusing `costs_in.py` for options would be
an **invented number** (TRAP 4):

- `costs_in.py` models **cash-equity** STT as **0.10% on turnover, each side, on
  delivery** (`STT_DELIVERY = 0.001`) — a tax on **traded value (notional)**.
- **Options STT is charged on a different base at a different rate.** For an
  option **sale**, STT is levied on the **option premium** (not the notional);
  for an option that is **exercised**, STT is levied on the **settlement /
  intrinsic value**. The rates were **revised upward in the Oct-2024 finance
  changes**. [ASSUMPTION on the exact current rates — **unverified this
  session**, deliberately not quoted (TRAP 4). The **structural** point is
  certain: options STT ≠ equity STT, in both **rate** and **base**.]
- **Consequence:** every rupee figure `costs_in.py` would produce for an option
  is **wrong** — wrong base (notional vs premium), wrong rate, and missing the
  **dominant** options cost entirely: the **bid-ask spread paid twice**, which for
  a thin single-name overnight option can dwarf all statutory charges combined.
  The equity cost stack is not a starting point for options; it is a source of
  false precision.

**§2 verdict:** the honest infra audit is **little-to-none usable**. The engine an
options book needs — data gate, IV/greeks, settlement, cost model — **does not
exist in this repo**, and the one equity module that *looks* reusable
(`costs_in.py`) is actively wrong for options. Only the generic governance/scoring
layer carries over. "Leverage the infra" is not an available path.

---

## 3. "Small capital, no big risk" contradicts the only profitable side (distinct contribution #3)

The operator sets two constraints — **small capital** and **no big risk** — and one
goal — **make money**. Overnight options cannot satisfy all three at once, because
the side that *earns* the overnight premium is the side that *carries the tail*.

### 3.1 The overnight variance risk premium accrues to the SELLER

The structural source of positive expectancy in overnight options is the
**variance risk premium**: implied volatility is, on average, **richer** than
subsequently-realised volatility, so the **option seller** (short premium) earns a
premium for bearing variance/gap risk. [FACT — the variance-risk-premium is one of
the most robust findings in the options literature; §4. Direction certain,
magnitudes unverified this session.] The sibling memo develops this for the index;
the mechanism is identical for a single name, only with a **fatter tail** (§1.3).

- **Short premium = large / unbounded tail.** A naked short call has unbounded
  loss; a short put loses down to zero. Even defined-risk short structures (spreads)
  cap the loss but **cap the income to a thin credit** and still lose their **max**
  on a bad overnight gap. On a **single name**, that gap can be an earnings surprise
  or a block-deal-driven move — precisely the fat tail of §1.3. **This is the
  opposite of "no big risk."** It is the classic "picking up pennies in front of a
  steamroller" profile: many small overnight credits punctuated by rare large
  single-name gap losses.

### 3.2 The long-premium side (what the operator's framing implies) is the documented net loser

"Buy a call/put overnight and make money on the move" is the **long-premium** side.
It satisfies "no big risk" (max loss = premium paid, small capital) — but it is the
**documented net loser**: delta-hedged option returns are on average **negative**
(§4.1), because the long buyer **pays** the variance risk premium and **bleeds
theta**, and overnight specifically the buyer pays the **doubled spread** (§1.2) on
a small expected move. **It satisfies the risk constraint by being the side with
negative expected return.**

### 3.3 The contradiction, stated plainly

| Side | Overnight expectancy | Risk profile | Capital | Satisfies operator? |
|---|---|---|---|---|
| **Short premium** (sell) | **Positive** (earns VRP) | **Large / unbounded tail** — worse for single names | Margin, not "small" | **Fails "no big risk"** |
| **Long premium** (buy) | **Negative** (pays VRP + theta + doubled spread) | Defined, small (premium) | Small ✓ | **Fails "make money"** |

**There is no configuration that is simultaneously positive-expectancy AND
no-big-risk AND small-capital in overnight options — and single names make the
short side's tail fatter and the long side's carry steeper.** The operator's three
requirements are mutually exclusive on this instrument. This is not a tuning
problem; it is the structure of the variance risk premium.

### 3.4 The one narrow exception, and why it is not free

The **long straddle into a scheduled earnings event** (§4.3) is the single framing
that is *both* small-capital *and* defined-risk (max loss = premium) *and* has an
academic rationale for **positive** expectancy — because IV can be **underpriced**
relative to the earnings jump, so the long straddle is not always paying a
premium; it may be *buying* a cheap jump. **But**: (i) it is an **EVENT** strategy,
not a generic overnight trade — it only exists on the ~4 earnings nights per name
per year; (ii) it overlaps **SPEC-PEAD-01** (shadow slot 2); (iii) the effect is
**thin and cost-sensitive** — the same doubled single-name spread and IV-crush
timing that make it hard; and (iv) it is **authorised by nothing here.** It is a
lead for a *future spec*, not a live path.

---

## 4. Literature pass (tiered) — [unverified at source this session]

Per the SESSION-HONESTY NOTE, **no source was opened**; directions are textbook,
numbers are withheld. The sibling memo owns the shared overnight-VRP core; this
section covers the **single-stock** and **event** literature specifically.

### 4.1 Single-stock option returns and the equity-option variance risk premium

- **[PR] Bakshi & Kapadia (2003), *Delta-hedged option returns and the negative
  market volatility risk premium*** (Review of Financial Studies). The canonical
  result: **delta-hedged option returns are on average negative**, evidence of a
  **negative** volatility risk premium — i.e. option **buyers pay** and **sellers
  earn** on average. Directly underwrites §3: the profitable side is the seller's,
  the buyer's side is the documented net loser. [unverified at source this
  session]
- **[PR] Cao & Han, *Cross-section of option returns and stock volatility***
  (Journal of Financial Economics). Finds delta-hedged single-stock option returns
  decrease with the underlying's **idiosyncratic volatility** — high-idio-vol
  single names (exactly the fat-tail names of §1.3) have **more negative**
  option-buyer returns. Reinforces that single-name option buying is worse than
  index option buying. [unverified at source this session]
- **[PR] Goyal & Saretto, *Cross-section of stock option returns and stock return
  volatility*** (Journal of Financial Economics). A large cross-sectional
  option-return literature exists — and note it is a **cross-sectional
  option-selection** result (a portfolio sorted on implied-vs-realised vol), **not**
  an overnight directional bet; it needs a full option chain and IV surface the
  repo lacks. [unverified at source this session]
- **[PR] Bakshi, Kapadia & Madan (2003)** — risk-neutral skewness/kurtosis from
  option prices; single-name option-implied distributions are **more skewed and
  fat-tailed** than the index's, consistent with §1.3. [unverified at source this
  session]

### 4.2 Overnight vs intraday in single stocks

- **[PR] Lou, Polk & Skouras (2019), *A tug of war: Overnight versus intraday
  expected returns*** (Journal of Financial Economics). Documents that several
  equity return **factors** load very differently overnight vs intraday. This is an
  **equity-return** decomposition (not an options result) and is relevant only as
  context: an "overnight" edge in the **underlying** does not translate into an
  options edge once theta and the **doubled option spread** are paid (§1.2). The
  existence of overnight/intraday structure in the stock is **not** an options
  strategy. [unverified at source this session]
- **[WP] Overnight-return / "night moves" literature (e.g. Bogousslavsky).**
  Overnight returns carry a distinct risk/return profile; again an equity, not an
  options, finding — cited to pre-empt the inference that "stocks move overnight" ⇒
  "buy overnight options." The move must clear theta + doubled spread, and §1.2
  says it usually cannot for a single-name option. [unverified at source this
  session]

### 4.3 The earnings-announcement straddle — the one studied long-premium rationale

- **[PR/WP] Straddles around earnings announcements (e.g. Gao, Xing & Zhang,
  *Anticipating uncertainty: straddles around earnings announcements*).** The one
  place a **long** overnight/pre-event straddle has a documented rationale: implied
  vol can be **underpriced** relative to the realised earnings jump, so a straddle
  bought before the announcement and held over it can earn positive average returns
  — *before costs*. Two cautions that make it **weaker**, not stronger, support:
  (i) the effect is **thin and highly cost-sensitive** — the single-name option
  spread (§1.2) and the post-announcement **IV crush** eat much of it; (ii) it is
  an **EVENT** strategy (only around scheduled earnings), which is **SPEC-PEAD-01
  territory** — earnings drift — already holding **shadow slot 2**. [unverified at
  source this session]

### 4.4 India single-stock option microstructure

- **[WP/thin, evidence gap]** India-specific peer-reviewed evidence on
  **single-stock option liquidity, bid-ask spreads, and OI concentration** was
  **not located this session** (WebSearch budget exhausted). The structural claims
  in §1 (monthly-only stock expiries, ATM-concentrated liquidity, ~180–190
  underlyings) are market-structure facts/assumptions, not effect-size claims, and
  do not depend on an India citation — but a spec would need the India microstructure
  evidence, with real measured spreads, before relying on any of it. **Flagged as
  an evidence gap, not a null (TRAP 6).** [unverified at source this session]

- **[VM] The retail options-tips / "option-buying signal" ecosystem** is enormous
  and, per the tier convention, **systematically biased toward positive claims** —
  used here only to note that strong retail *demand* for "buy overnight options and
  win" is itself a mild contrarian tell, never as evidence.

**What the literature does NOT provide:** any credible, out-of-sample,
cost-surviving demonstration that a **long** single-stock overnight option position
makes money net of the doubled spread and theta. The robust findings (Bakshi-Kapadia,
Cao-Han) point the **other way** — the buyer loses on average; the earner is the
seller, whose tail (fatter for single names) violates "no big risk."

---

## 5. The data + seal wall (brief — the sibling owns the general form)

- **No options data of any kind exists in the repo** — no chains, no IV, no greeks,
  nothing. §2 established this.
- **No lawful pre-cutoff options substrate.** The seal protocol requires dev data
  **< 2024-07-17** (`SEAL.md`); there is **no pre-cutoff options data** anywhere
  here, and no lawful way to acquire it: yfinance serves ~60 days of equity 5-min
  bars and **no option chains** (FACT, probed under RULING 13 /
  `block_trade_detection_feasibility.md`); the Kite path that could reach option
  data is **BINDING RULE 3 forbidden**; scraping NSE/BSE option-chain endpoints is
  blocked by the unresolved exchange ToU (**OPEN OPERATOR DECISION 1**).
- **Therefore single-stock overnight options are untestable here** for the same
  reasons as the index case (sibling memo) **plus** the data-depth/liquidity
  problem is **worse** for single names. There is no substrate to develop against,
  nothing to hash-freeze a spec around, and no sealed test could ever be run.

---

## 6. Cross-references

- **`analysis/nifty_overnight_options_feasibility.md`** (sibling) — OWNS the NIFTY
  index-option case and the **shared overnight-options-microstructure core** (theta,
  overnight VRP, double spread, long-buyer-loses, 15:15/GIFT-Nifty timing). Read it
  for the shared mechanics; this memo adds only the single-stock-specific handicaps.
- **`analysis/block_trade_detection_feasibility.md`** — the single-name **overnight
  gap** source (bulk deals disseminated post-close ⇒ next-morning gaps), and the
  same no-lawful-intraday-tape / Kite-forbidden data wall. Directly feeds §1.3 and §5.
- **`analysis/macro_beta_diagnostic.md`** — establishes that even validated
  single-name **exposures** (crude/USDINR betas) are **exposure, not alpha** (its
  §11); by the same logic, an overnight IV/beta exposure on a single name is not a
  tradeable edge absent a forecast the repo cannot supply.
- **`SPEC-PEAD-01`** (draft, **holds shadow slot 2**) — the earnings-drift family
  that the one narrow options exception (§3.4 / §4.3, the earnings straddle)
  **overlaps**. Any earnings-event options idea is PEAD-adjacent and would compete
  for that slot, not open a new one.
- **`crude_forecast_engine_feasibility.md` / `DIAG-BREAKOUT-ENTRY-0001`** — the
  program's repeated lesson that a **fixed, unscaled friction cost meeting a small
  edge** is the killer; §1.2 is the options-spread instance of the same wall.
- **RULING 5 / `costs_in.py`** — the **equity** cost stack that §2.6 shows is wrong
  for options (different STT base and rate; missing the dominant spread cost).

---

## 7. What a good answer to the operator is

**Do not build, and it cannot be assessed here.** In one paragraph for the
operator: *We have no options infrastructure to leverage — every module we built is
equity-only (data gate, settlement, panel, overlay, cost model), and the only
reusable piece is the generic SPA/DSR/freeze governance plumbing, which scores a
trial but does not construct, price, settle, or cost an option. Single-stock
options are less liquid and higher-tailed than the NIFTY index the sibling memo
already rules out — monthly-only, ~180–190 names, liquidity stuck at the near-month
ATM strike, and a doubled bid-ask spread that is multiples larger than the index's.
"Small capital, no big risk" is incompatible with the only positive-expectancy side:
the overnight premium is earned by the seller, who carries a fat single-name gap
tail (the opposite of "no big risk"), while the buyer's side you're implying is the
documented net loser after theta and the doubled spread. And it is untestable here —
no options data exists in the repo, none is lawfully obtainable (Kite forbidden,
scraping ToU-blocked, yfinance has no chains), and the seal needs pre-2024-07-17 dev
data that does not exist for options. The one framing with any merit — a defined-risk
long straddle bought into a scheduled earnings event — is an EVENT strategy that
overlaps SPEC-PEAD-01 (slot held), still needs an options data + greeks + cost stack
we do not have, and is authorised by nothing here.*

---

## 8. Open items — what would have to close before an options spec could even be drafted

1. **An options data source** with historical chains + **bid/ask** + OI + volume,
   PIT-timestamped. Does not exist here; not lawfully obtainable (Kite forbidden,
   ToU-blocked scraping). The **Accord Fintech (ACE Datafeed)** enquiry already
   contemplated under OPEN OPERATOR DECISION 1 /
   `analysis/accord_fintech_enquiry.md` should ask whether a **licensed historical
   options-chain** feed is even offered — fold it into that existing enquiry, do
   not open a new workstream.
2. **An options pricing / IV / greeks model** (BSM or better, per-name IV surface)
   — none in `src/`.
3. **An options settlement / P&L engine** (expiry, exercise/assignment, overnight
   premium mark) — `paper_leg.py` is cash-equity only.
4. **A correct options cost model** — options STT (premium/settlement base, revised
   rates), exchange charges on premium, and above all the **bid-ask spread as the
   dominant cost**. `costs_in.py` is wrong for options (§2.6).
5. **A dev-window (< 2024-07-17) options substrate** to develop and seal-test
   against — none exists and none is lawfully obtainable.
6. **A shadow slot** — both held (QFM, PEAD); an earnings-options idea overlaps
   PEAD's slot rather than opening a new one. AG-01 and 52WH are queued ahead.
7. **The DSR reporting band** (RULING 7, proposed 0.35/0.50/0.70 — PENDING) and the
   **exchange ToU ruling** (OPEN OPERATOR DECISION 1) — both inherited by any
   future options work.
8. **Re-verify every §1/§2.6/§4 figure at source** before any spec cites it —
   nothing was opened this session; the ~180–190 underlyings count, the options STT
   rates, the expiry structure, and every literature number are directional priors
   only (TRAP 4).

---

## 9. Proposed register row (TEXT ONLY — operator to append; this memo did NOT write it)

Consistent with the `DIAG-BREAKOUT-ENTRY-0001` / `BLOCK-DETECT-SCOPE-0001` /
`DIAG-CRUDE-FORECAST-0001` precedent (outcome-blind DO-NOT-BUILD scoping rows, no
trial spent). For the operator to append verbatim if they concur:

```
SS-OPTIONS-OVERNIGHT-SCOPE-0001,2026-07-23,LEGACY,"Feasibility scope: can single-stock (non-NIFTY) listed options be traded overnight (12-24h) for money with SMALL CAPITAL and NO BIG RISK, leveraging existing program infrastructure? (operator question 2026-07-23)",scope-diagnostic,"DO-NOT-BUILD / CANNOT-ASSESS-HERE — not a trial","OUTCOME-BLIND, NO TRIAL SPENT (cumulative trial count UNCHANGED at 53), NO SHADOW SLOT, NO REPO OUTCOME DATA conditioned on any signal, NO SPEC DRAFTED, NO HASH FROZEN, NO BROKER/KITE CALL, NO SCRAPING (WebSearch budget exhausted; NO options source opened - all literature marked unverified-at-source). Analysis: analysis/single_stock_overnight_options_feasibility.md. FINDINGS: (1) NO OPTIONS INFRASTRUCTURE to leverage - grep-confirmed zero options handling in src/ (data_gate/paper_leg/panel/overlay/costs_in are all EQUITY-only; only the generic metrics.py SPA/DSR + spec_guard governance layer is instrument-agnostic, and that is scoring plumbing, not options machinery); options need a data gate + IV/greeks + settlement engine + cost model that DO NOT EXIST here; costs_in.py is WRONG for options (options STT is a different rate on a different base - premium/settlement not notional - and it omits the dominant bid-ask-spread cost). (2) SINGLE-STOCK STRICTLY WORSE than the NIFTY index case (sibling analysis/nifty_overnight_options_feasibility.md already rules the index out): monthly-expiry-only (no stock weeklies), ~180-190 underlyings (ASSUMPTION), liquidity concentrated at near-month ATM, doubled bid-ask spread MULTIPLES larger, and FATTER idiosyncratic overnight gap tails (earnings, block deals per block_trade_detection_feasibility.md, Reg-30 news). (3) 'SMALL CAPITAL / NO BIG RISK' incompatible with the only positive-expectancy side: overnight variance risk premium accrues to the SELLER (large/unbounded tail, worse for single names = fails 'no big risk'); the LONG-premium side the operator implies is the documented net loser (delta-hedged option returns negative - Bakshi-Kapadia; worse at high idio-vol - Cao-Han = fails 'make money'). (4) UNTESTABLE here: no options data in repo, none lawfully obtainable (Kite=BINDING RULE 3, scraping=ToU OPEN DECISION 1, yfinance has no chains), seal needs pre-2024-07-17 dev data that does not exist for options. NARROW EXCEPTION noted only: a defined-risk long straddle INTO a scheduled earnings event (Gao-Xing-Zhang) is small-capital + defined-risk + has a rationale, BUT is an EVENT strategy overlapping SPEC-PEAD-01 (shadow slot 2 HELD), still needs an options data+greeks+cost stack this repo lacks, and is authorized by NOTHING here. Literature (Bakshi-Kapadia; Cao-Han; Goyal-Saretto; Bakshi-Kapadia-Madan; Lou-Polk-Skouras; Gao-Xing-Zhang) UNVERIFIED AT SOURCE this session. Cross-ref sibling nifty options memo, block_trade_detection_feasibility.md, macro_beta_diagnostic.md (exposure!=alpha), SPEC-PEAD-01, RULING 5/costs_in.py, OPEN OPERATOR DECISION 1 + Accord/ACE enquiry (ask re licensed historical options-chain feed)."
```

**Trial accounting:** this row records a **scope/kill, not a trial** — cumulative
trial count (**53**) is **unchanged**. No outcome was observed; the kill is on
infrastructure, instrument structure, the risk/return contradiction, and
untestability, reached with zero outcome contact.

---

## 10. Verdict (recap)

**DO-NOT-BUILD / CANNOT-ASSESS-HERE.** (1) There is **no options infrastructure to
leverage** — the stack is equity-only end to end; only the generic
governance/scoring layer transfers, and `costs_in.py` is actively wrong for options
(§2). (2) Single-stock options are **strictly worse** than the NIFTY index case the
sibling already rejects — thinner, coarser, more spread-taxed, fatter-tailed (§1).
(3) **"Small capital, no big risk" is incompatible with the only profitable side** —
the seller earns the overnight premium but carries the fat single-name tail; the
buyer is safe but is the documented net loser (§3, §4). (4) It is **untestable
here** — no options data exists or is lawfully obtainable, and no pre-cutoff options
substrate exists for the seal protocol (§5). The one defensible narrow framing — a
long earnings straddle — is an **EVENT** strategy overlapping **SPEC-PEAD-01**, still
needs an options stack this repo lacks, and is **authorised by nothing** in this
memo.

**NO TRIAL SPENT. Cumulative trial count unchanged at 53. No shadow slot. No spec
drafted. No hash frozen. No repo outcome data conditioned on any signal. No broker
call. No scraping.**

**End of memo.** Outcome-blind; no trial spent; no repo outcome data touched; no
options source opened this session; no spec drafted; register row proposed as text
only.


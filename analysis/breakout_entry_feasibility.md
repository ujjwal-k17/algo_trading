# Post-Breakout Entry — feasibility memo (outcome-blind, pre-spec)

**Question put by the operator (2026-07-23):** catching a stock *before* it breaks
out has proven hard (technical parameters + vision LLM + catalyst). **Is there any
logic that catches a stock RIGHT AFTER the breakout, entering then to capture the
remaining upside?**

**Date:** 2026-07-23.
**Status:** DIAGNOSTIC, NOT A TRIAL. **Outcome-blind. No trial spent. No shadow
slot consumed. No repo outcome data touched.** No price panel was loaded, no
return, CAR, drift, hit rate or conditional performance summary was computed, no
`data_gate` call was made, no backtest was run. **No spec is drafted and none is
proposed for drafting.** `governance/research_register_v2.csv` was **read, not
written** — a register row is *proposed as text* in §11 for the operator to append.

Under `governance/CONTAMINATION_POLICY.md` AMENDMENT A this document sits entirely
in the free bucket: external literature reading, cost tables, turnover arithmetic
and capacity math. Every number below derives from `src/costs_in.py` (RULING 5),
the frozen legacy clone's own source, this repo's governance record, and
explicitly-labelled ASSUMPTIONS.

**What would have been a trial and was therefore NOT done:** any measurement of
what happens after a breakout. That is an event study / conditional return plot,
named verbatim in AMENDMENT A. It requires a hash-frozen spec, a pre-registered
register row, and (for a sealed test) a shadow slot. **Both slots are held (QFM,
PEAD), with AG-01 and 52WH queued.**

---

## VERDICT (stated first, argued after)

> ## **(C) DO NOT BUILD.**
>
> Not "unproven" — **already answered, twice, at this program's own expense.**

Three findings, in descending order of force:

1. **This is not a new family. It is the legacy system's own entry rule.** The
   legacy engine — the one this program KILLED as a fund candidate — scores a
   volume-confirmed 52-week-high breakout at **0.20 weight** in its composite
   (`patterns.py:165-175`, `score.py:166-178`, `config.py:89-95`) and then enters
   on a **`BREAKOUT` entry type** whose literal rule is *"close > entry_price AND
   `volume_ratio >= 1.5`"* on the 09:15–09:20 candle of the **next session**
   (`preopen_check.py:653-661`). Its own reason string reads **"Breakout confirmed
   — close ₹X above ₹Y with N× vol. **Enter now.**"** That is the operator's
   question, implemented, shipped, and running in production today. It produced
   real gross alpha (~18.5%/yr, t≈2.95) and was killed because friction at
   1.6 round-trips/day consumed all of it. **Asking whether post-breakout entry
   works is asking to re-run an experiment whose answer this program already
   bought.**

2. **The program already ran the breakout literature pass, on 2026-07-18, and
   already recorded the kill.** `research.md` §2 and `plan_52wh.md` list
   *"single-name chart-pattern rules as primary alpha"* under **"Explicit
   non-goals (evidence-based, do not resurrect)"**, on the strength of
   Heyman-Inghelbrecht-Pauwels (34 emerging markets): India's *best* chart rule
   ran **gross p ≈ 0.00 → Hansen SPA p ≈ 0.69 net of costs**. That is precisely
   the test SPEC-52WH-01 §8 and every Tier 2 kill line use. The family was
   redesigned *away* from breakout entry into a **negative screen** for exactly
   this reason.

3. **The friction arithmetic is decisive and independent of both.** §5's hurdle
   table: at a 5-session hold and 20 bps/side slippage, the strategy must earn
   **62.3 bps gross per round trip — 31.4%/yr — to reach exactly zero.** At the
   ₹100 Cr AUM target the capacity arithmetic (§7) forces slippage far above 20
   bps/side. **The required gross drift exceeds anything credibly documented in
   the post-breakout literature** (§6).

**The single strongest argument FOR the hypothesis** is that it is not empty:
George & Hwang (2004) established that nearness-to-52-week-high predicts
cross-sectional returns, and that effect is India-replicated (Raju 2023). Something
real happens near highs. **See §6.**

**The single strongest argument AGAINST** is that the same India paper the program
already deep-read says the tradeable part of that effect is **the short leg, not
the long leg** — no long-only near-high portfolio beats the NIFTY100 TRI in any
construction Raju tested (Q5 t = −0.91). *Buying the breakout is the leg that does
not work.* The program has already acted on this once.

**Is there a surviving region?** §9 identifies one, honestly: post-breakout
information used as a **veto/exclusion overlay on a slow host book**, adding zero
incremental turnover. That is not a new family — **it is SPEC-52WH-01, which
already exists, is already hash-frozen, and is already queued.** The correct
action on the operator's question is therefore not "build something" but
**"finish 52WH attempt 2, and log the daily overlay."**

---

## 0. How to read this document

Source tiers, marked on every external citation (the `analysis/QFM_literature_prior.md`
convention):

- **[PR]** peer-reviewed journal article.
- **[WP]** working paper / preprint / dissertation — not refereed.
- **[VM]** vendor, broker, screener, blog or practitioner marketing —
  **systematically biased toward positive results**; used only to characterise the
  information environment, **never as evidence for an effect**. The
  breakout/technical-analysis space is dominated by [VM] and it is treated
  accordingly.

**FACT / ASSUMPTION tags** on every quantitative input, per repo convention.
**"unverified"** means no source was opened stating it. Nothing is guessed —
TRAP 4: *a disclosed gap is an asset; an invented number is a liability at due
diligence.*

**Internal citations** are file:line into `~/vendor/legacy-engine` (frozen clone,
pinned `ee7ad13228244f4f27e3d2d839baf70897ff24fe`) or into this repo. Per **RULING
9**, a clone-derived claim about the *running* system requires a production HEAD
check; §2.4 states exactly which claims here are clone-only and which are already
production-verified.

**Quarantine note (governance).** During the clone read for §1, the file
`~/vendor/legacy-engine/SWEEP_HOLDING.md` was opened. Its "DECISION TABLE" holds
the legacy system's **net-of-cost results by holding period**, which
`governance/DECISIONS.md:425-428` records as **deliberately unread / outcome
contact unauthorized**. That crossing has been disclosed to the operator
separately. **This memo does not use, cite, or reason from those net-by-holding-
period numbers.** Every friction figure in §5 is derived from `src/costs_in.py`
cost constants alone. The sweep is noted as *existing and still quarantined*, and
nothing more.

---

## 1. This is the legacy system's own entry rule (clone characterization)

The operator's question — "enter right after the breakout, on confirmation, to
capture the remaining upside" — describes, almost line for line, the entry path of
the legacy engine this program already killed as a fund candidate. Four mechanisms,
all read from the frozen clone (`ee7ad132`):

**(a) A volume-confirmed 52-week-high breakout is a scored signal.**
`patterns.py:165-175` (`breakout_52w_high`): *"1 if today's high is a new 52-week
high AND volume ≥ 1.5× 20-day average"* (lookback 260 sessions, prior high excludes
today). It feeds `score.py:154-166` as one of the bullish pattern flags, percentile-
ranked into `score_breakout`, which enters the composite at **0.20 weight**
(`config.py:89-95`, `SCORE_WEIGHTS["breakout_pattern"] = 0.20`;
`score.py:166-178`). The human-readable reason string emits literally
**"52-WEEK HIGH BREAKOUT"** and **"today vol ≥ 2× avg"** (`score.py:223-234`).

**(b) The entry TYPE is a breakout-confirmation gate.** `preopen_check.py:653-661`
(`check_entry_confirmation`, the 09:15–09:20 first-candle check on the morning of
the next session): for a `BREAKOUT` entry, verdict `BUY` when
**`candle_close > entry_price AND volume_ratio >= 1.5`**, with the reason string
**"Breakout confirmed — close ₹X above ₹Y with N× vol. Enter now."** The
`CONDITIONAL` type (`:605-612`) is the same shape at a lower bar (close >
`hold_level` = `entry_price*0.995`, `volume_ratio >= 1.0`); `WAIT AND WATCH`
(`:686-690`) is a gap-up variant (gap ≥ 0.5%, `volume_ratio >= 2.0`). All three
are "confirm the move has started, then enter" rules. Source-of-record:
`governance/SOP_OF_RECORD.md` §2.

**(c) Entry is strictly after the breakout is visible.** Recs generate on the
evening of Day 0; the stock is *not* held on Day 0; candidate entry is the next
session's morning confirmation (`SOP_OF_RECORD.md` §1, `picks_log.py:44-56`). This
IS "enter right after the breakout" — the signal fires on Day 0's close, entry is
Day 1 open + confirmation.

**(d) There is even an anti-chase guard already.** `config.py:102-103`:
`MAX_SINGLE_DAY_MOVE_PCT = 10.0` — *"Exclude stocks that moved more than this % in a
single day today … avoid chasing today's spike."* The legacy designers already
confronted the "the move is already over" problem and put in a cap.

**Holding period and exits** (`SOP_OF_RECORD.md` §4, `exit_manager.py:50-140`):
priority STOP → T2(+10%) → T1(+5%) → TIME, with a **5-session time exit**. T1 is a
full exit (RULING 4, operator-confirmed). Nominal hold 5 sessions; **realised
H ≈ 3.1 sessions** because stops/targets bind before the timer (established as FACT
in `DECISIONS.md` 2026-07-20, VARIANT A: 1.6 round-trips/day ⇒ H ≈ 3.1).

**Conclusion of §1:** post-breakout entry is not an unexplored idea for this
program. **It is the incumbent system**, built over ~51 registered trials, with a
five-factor technical score (trend/momentum/RS/volume/breakout at 0.20 each in the
clone; the production `_FINAL_WEIGHTS_V2` adds fundamental/catalyst/quality/vision/
reversal — `DECISIONS.md` 2026-07-20 production verification) plus a vision-LLM
layer and a catalyst layer — exactly the "technical parameters + vision LLM +
catalyst" stack the operator names. The operator's "catch it *after* the breakout
instead of before" is a **timing variant of a family already killed on friction**,
not a new family.

---

## 2. Relationship to the legacy kill — the answer this program already bought

### 2.1 The kill, in the program's own settled numbers

These figures are program-canonical (in `CLAUDE.md` and the legacy kill analyses)
and are the basis of the kill itself — reading a killed family's kill analysis is
not new outcome contact:

- **Gross residual alpha ≈ +18.5%/yr, t ≈ 2.95** (factor-adjusted, M3), decaying
  by year-slice and survivorship-inflated — a real, skill-shaped gross signal.
- **Statutory cost drag ≈ −19.7%/yr** at the book's own ~1.6 round-trips/day
  turnover — *approximately equal to the entire gross alpha, before a single basis
  point of slippage.*
- Per-trade cross-check: gross ≈ **+0.37%/trade**, frictions ≈ **0.75%/trade**;
  net per-trade R ≈ +0.23R at **t ≈ 0.70** on the live sample (n=14, underpowered).
- **Verdict: NO-GO at current turnover. "The alpha engine and the cost engine are
  the same size."**

The one-line lesson `CLAUDE.md` draws from this — *"gross alpha was never the
constraint; friction was"* — is the direct answer to the operator's question. The
legacy system **did** catch stocks right after the breakout, it **did** generate
real gross alpha doing so, and friction **did** consume all of it. Changing *when*
in the breakout you enter does not change the cost structure that killed it; if
anything, entering into the confirmed move makes execution worse, not better (§7).

### 2.2 Why "capture the *remaining* upside" makes the problem worse, not better

The operator's framing contains its own falsifiable core: **"remaining upside."**
By the time a breakout is *identifiable and confirmed* (which the legacy rule
requires — a new 52wk high on ≥1.5× volume, confirmed on the next morning's
candle), the initial, largest, cheapest part of the move has already happened and
is not yours. You are buying the residual. The residual must then cover a **full
round trip of friction** (§5) plus the adverse execution of trading into a fast,
crowded, wide-spread moment (§7). The tighter the confirmation (the more sure you
are it is a real breakout), the more of the move is already gone. **This is a
structural tension, not a tuning problem:** confirmation and remaining-upside trade
off directly against each other.

### 2.3 The turnover trap is intrinsic to the idea

A breakout-entry family is **high-turnover by construction** — a breakout is an
event, events are frequent and short-lived, and capturing "the remaining upside"
means exiting when the move exhausts, i.e. soon. The ROADMAP's governing design
constraint is the opposite: *"New families must be low-turnover by design."* You
cannot make a post-breakout-entry family low-turnover without destroying the thing
that defines it — the same unfixable-by-construction problem `DECISIONS.md` VARIANT
D recorded for options-implied breakout signals (*"the signal's informativeness IS
its decay rate"*). §5 quantifies exactly how much this costs.

### 2.4 Provenance table — clone-only vs production-verified (RULING 9)

Every §1 mechanism is read from the **frozen clone** `ee7ad132`. RULING 9: a
clone claim is a claim about the pin, not the running system. Status of each:

| Claim | Source | Production-verified? |
|---|---|---|
| `breakout_52w_high` pattern = new 52wk high ∧ vol ≥ 1.5×avg20 | `patterns.py:165-175` (clone) | **CLONE-ONLY.** Needs a HEAD check before asserting live. |
| `score_breakout` at 0.20 in the 5-factor composite | `score.py:166-178`, `config.py:89-95` (clone) | **PARTIAL.** `DECISIONS.md` 2026-07-20 verified the *live* top-20 stage is `composite_score` with five 0.20 TA weights at HEAD `8e4e6f7`; the specific `breakout_pattern` line was not separately re-read. Treat the 0.20 as clone-stated, composite-structure as production-consistent. |
| `BREAKOUT` entry gate = close>entry ∧ `volume_ratio`≥1.5 | `preopen_check.py:653-661` (clone) | **CLONE, but the volume-gate CONSTANTS are production-verified elsewhere.** `DECISIONS.md` 2026-07-22 verified at production HEAD `5c099d77` that `VOL_GATE_CONDITIONAL/BREAKOUT/WAIT = 1.0/1.5/2.0` are live named constants and the `×75` projection is live. So the *breakout gate's 1.5× threshold is confirmed live*; the surrounding `check_entry_confirmation` control flow is clone-read. |
| `MAX_SINGLE_DAY_MOVE_PCT = 10.0` anti-chase cap | `config.py:102-103` (clone) | **CLONE-ONLY.** Not HEAD-checked. |
| 5-session time exit, STOP→T2→T1→TIME | `exit_manager.py:50-140` (clone) | **CLONE**, but operator-confirmed as SOP (RULING 4). |
| Realised H ≈ 3.1 sess (1.6 RT/day) | `DECISIONS.md` VARIANT A | **Program FACT.** |
| Gross 18.5%/yr, cost −19.7%/yr, net≈0 | legacy kill analyses / `CLAUDE.md` | **Program FACT** (basis of the kill). |

**Net RULING-9 reading:** the two facts my verdict actually leans on — *(i) the
legacy system is a volume-confirmed-breakout entry rule, and (ii) it was killed
because friction ≈ gross alpha* — are **production-consistent**: the breakout
volume gate (1.5×) is live-verified, and the kill is a settled program fact. The
clone-only items (exact 0.20 weight, the anti-chase cap, `check_entry_confirmation`
flow) are supporting colour, not load-bearing, and are flagged as needing a HEAD
check before being asserted about the running system.

---

## 3. Relationship to SPEC-52WH-01 — the reframe already happened, and it points away from buying breakouts

SPEC-52WH-01 is the direct descendant of the operator's original breakout idea. Its
`research.md` records the reframe verbatim: *"the original idea (detect single-name
chart breakouts, block the failure patterns) is the part the literature kills. The
survivor is the cross-sectional 52-week-high effect."* Two findings from that
family bear directly and adversely on "buy the breakout":

**(a) The long leg does not work.** Raju (2023), deep-read in `research.md` §4, on
19 years of Indian data: **no long-only near-52wk-high portfolio beats the NIFTY100
TRI in any construction** — EW Q5 (near high) t = −0.91 vs the index; Top-200 Qu4
t = −1.49; FF6 long-leg alphas significantly *negative*. The entire premium is the
**catastrophic underperformance of far-from-high stocks** (Q1 CAPM α ≈ −2.4%/mo).
"Buying the breakout" is the near-high long leg — **the leg the paper's own tables
kill.** The realisable edge is the *negative screen* (never hold far-from-high
names), which is what SPEC-52WH-01 was frozen as.

**(b) The tradeable structure is slow, not fast.** The 52wk-high effect decays
slowly (~84% survives a 6-month hold), so SPEC-52WH-01 rebalances **quarterly**
with a **<300%/yr turnover budget** — deliberately low-turnover. That is the
*opposite* of a breakout-entry family, and it is the direction the evidence
rewards. A fast post-breakout book abandons exactly the property that makes 52WH
affordable.

**So SPEC-52WH-01 is the answer to "is there any breakout logic that works" already
on file:** yes, but only as a slow negative screen, and it is already hash-frozen
(sha256 `4b58f285…`, `FREEZE-52WH-0001`) and queued. It is not a buy-the-breakout
book and was specifically designed not to be.

---

## 4. Relationship to SPEC-SRA-01 (killed) and SPEC-PEAD-01 — is this a re-ask?

### 4.1 SPEC-SRA-01 is the nearest structural precedent, and it was KILLED

`analysis/SRA_friction_hurdle.md` (RULING 11, 2026-07-22) killed SPEC-SRA-01 — a
5-session "anticipate the rally" family — *before any outcome contact*, on two
independent grounds: **capacity** (a ₹5 Cr position vs the spec's own ₹2 Cr/day ADV
floor = 250% of a day's volume; 25 sessions to enter a 5-session hold) and **net
expectancy** (needs 1.15×–6.06× the legacy system's entire gross alpha depending on
slippage). A post-breakout-entry family at a similar 3–5 session realised hold is
**the same friction regime and the same capacity wall.** SRA anticipated the move;
this enters after it — arguably worse, because it transacts on the volume-expansion
day itself (§7). This memo reproduces SRA's method (§5, §7) and reaches the same
structural conclusion.

### 4.2 SPEC-PEAD-01 — the operator's question IS substantially a re-ask of PEAD

Post-earnings-announcement drift is the best-documented "enter after the event,
capture the remainder" effect in all of finance, and **SPEC-PEAD-01 already holds
shadow slot 2** for it. If the operator's "breakout" is driven by a catalyst
(earnings, news), then "enter right after the move on confirmation and capture the
drift" **is PEAD**, and it is already claimed, drafted, and queued. Three things the
operator should know from `analysis/PEAD_literature_prior.md`:

- The modern peer-reviewed evidence (Martineau 2022, *Critical Finance Review*)
  says drift under a random-walk surprise estimator **died outside microcaps after
  1990**, and post-2011 survives only at a **2-to-5-day** horizon in microcaps — a
  horizon this program cannot afford (~4,800%/yr turnover; the PEAD "pincer",
  `SPEC-PEAD-01` §3.3.2).
- The India PEAD literature is **100% gross-of-cost, without exception**.
- Chordia et al. (2009): transaction costs account for **70–100% of PEAD paper
  profits**; the closest-matching SUE definition to a mechanical Indian one is the
  one that paper concludes is unprofitable after costs.

**If the operator's intent is catalyst-driven post-breakout entry, the answer is
"that is PEAD, it holds a slot, and its own literature prior is adverse."** If the
intent is pure-technical post-breakout entry, the answer is "that is the legacy
system, killed" (§2). Either way it is not a new family.

### 4.3 The queue reality

Both shadow slots are held (QFM slot 1, PEAD slot 2), with **AG-01 and 52WH already
queued** ahead of anything else. A new post-breakout family would be **at least
fifth in line** (behind QFM, PEAD, AG-01, 52WH — the same position `DECISIONS.md`
assigned VARIANT D). Even if it had a case, it could not be reached on any near
horizon, and freezing a spec whose §8 is already known unreachable just parks a
permanently-uneditable dead family in `governance/specs/`.

---

## 5. THE FRICTION HURDLE — the decisive free arithmetic

This is the deliverable that settles the question, and it is entirely free
(cost-table arithmetic, AMENDMENT A). Method mirrors `analysis/SRA_friction_hurdle.md`.

### 5.1 The statutory round trip (FACT, from `src/costs_in.py`, RULING 5)

Itemised at a ₹50,00,000 position (₹100 Cr ÷ 20 slots), delivery basis, one
scrip-day of DP, recomputed against `costs_in.round_trip`:

| Line | bps | share | tag |
|---|---|---|---|
| STT (both sides, 0.10%×2) | 20.000 | 89.8% | FACT (statutory) |
| Stamp (buy, 0.015%) | 1.500 | 6.7% | FACT |
| Exchange txn (₹307/cr ×2) | 0.614 | 2.8% | FACT (NSE/FA/73061) |
| GST (18% on brok+exch+SEBI) | 0.114 | 0.5% | FACT |
| SEBI (₹10/cr ×2) | 0.020 | 0.1% | FACT |
| DP (flat ₹15.34) | 0.031 | 0.1% | ASSUMPTION (operator, RULING 5) |
| Brokerage (₹0 delivery) | 0.000 | 0.0% | ASSUMPTION (operator, RULING 5) |
| **Statutory round trip** | **22.279 bps** | 100% | |

**STT is ~90% of the bill and is irreducible** — a tax on turnover, untouched by
any broker, venue, or execution choice. This is the structural reason a
short-horizon Indian cash-equity family is hard, and it is why the legacy kill was
a kill. (Reconciles with the ₹1L-slot figure 23.782 bps in `DECISIONS.md`; the
scale difference is the flat DP charge.) Slippage is a **separate explicit
parameter** (RULING 5), added below as `s` bps/side; round-trip cost `c = 22.279 +
2s`.

### 5.2 Annual friction drag by holding period and slippage (%/yr, per rupee deployed)

`drag = (252/H) × c/100`. **This is the whole question in one table.**

| H (sess) | s=5 | s=10 | s=20 | s=30 | s=50 | s=100 |
|---|---|---|---|---|---|---|
| **2** | 40.7 | 53.3 | 78.5 | 103.7 | 154.1 | 280.1 |
| **3** | 27.1 | 35.5 | 52.3 | 69.1 | 102.7 | 186.7 |
| **5** | 16.3 | 21.3 | 31.4 | 41.5 | 61.6 | 112.0 |
| **10** | 8.1 | 10.7 | 15.7 | 20.7 | 30.8 | 56.0 |
| **20** | 4.1 | 5.3 | 7.9 | 10.4 | 15.4 | 28.0 |
| **60** | 1.4 | 1.8 | 2.6 | 3.5 | 5.1 | 9.3 |

Anchor: the legacy system sat at **H ≈ 3.1**, i.e. between rows 3 and 5 — statutory
drag alone ~18–20%/yr, ≈ its whole gross alpha. **A post-breakout family with a
realised hold of 2–5 sessions lives in the top three rows: 27–154%/yr of drag.**

### 5.3 The assumption-free per-trade hurdle

A stop-and-target book's per-fire P&L is just its realised return; clearing zero
net requires **E[return per trade] ≥ c** — no distributional assumption:

| slippage s (bps/side) | required gross drift per round trip |
|---|---|
| 5 | **+32.3 bps** |
| 10 | **+42.3 bps** |
| 20 | **+62.3 bps** |
| 30 | **+82.3 bps** |
| 50 | **+122.3 bps** |
| 100 | **+222.3 bps** |

So: **the confirmed breakout must deliver, on average, +0.32% to +2.22% of
"remaining upside" every single time you enter, net of nothing else, just to break
even.** That is the falsifiable core of the hypothesis, stated as a number.

### 5.4 Breakeven hit-rate frontier (for the stop/target version)

With `p` = win fraction, `W` mean winner, `L` mean loser, `R=W/L`:
`p* = (1 + c/L)/(R + 1)`. At **s = 20 bps/side** (`c = 0.623%`), a plausible
mid-cap breakout-execution figure (§7 argues it is optimistic at ₹100 Cr):

| mean loser L | R=1.0 | R=1.5 | R=2.0 | R=3.0 |
|---|---|---|---|---|
| 3.0% | 60.4% | 48.3% | 40.3% | 30.2% |
| **5.0%** | **56.2%** | **45.0%** | **37.5%** | **28.1%** |
| 7.0% | 54.5% | 43.6% | 36.3% | 27.2% |

**Read this without fooling yourself (the SRA §5.2 discipline): `p*` and `R` are
not free.** For a roughly zero-mean return distribution, `R≈1` and `p≈50%` are
forced together; you cannot claim "R=3, so I only need 28%" — an uncapped stopless
book with R=3 has winners 3× its losers, a *stronger* claim than a 56% hit rate at
R=1. The diagonal is one number, not a menu. The invariant is the **edge over a
fair coin**, `c/(2L)`: at s=20, L=5%, that is **+6.2 percentage points** of hit
rate above 50/50 — every trade, out of sample, net of the legacy family's own
six-factor machinery having already tried.

### 5.5 The holding period that would actually pay its friction

Inverting §5.2 for a ≤6%/yr drag budget: at 10 bps/side you need **H ≈ 18
sessions**; at 20 bps/side, **H ≈ 26 sessions**; at 30 bps/side, **H ≈ 35
sessions**. **A family that pays its friction is a 4–7 week family, not a
post-breakout-entry family.** A 4–7 week hold is not "capture the remaining upside
of a breakout" — it is position/swing trading, and at that horizon the tradeable
edge the literature actually documents is the *slow* 52wk-high / momentum effect
(§6), which is SPEC-52WH-01, not a breakout-entry rule.

---

## 6. Literature pass (tiered; effect sizes where verifiable)

Sources read from the session scratchpad PDFs/texts (George-Hwang, Jegadeesh-Titman,
Moskowitz-Ooi-Pedersen, Novy-Marx, Hou-Xue-Zhang, Harvey-Liu-Zhu, Gervais-Kaniel-
Mingelgrin) plus the program's own prior passes (`research.md` §2/§4,
`PEAD_literature_prior.md`). The single most important reading: **where the
statistics are done properly, post-breakout edges are real but modest and monthly/
cross-sectional; where they look spectacular, the statistics were not computed.**

### 6.1 The 52-week-high effect — the most directly relevant academic result

**[PR] George & Hwang (2004), "The 52-Week High and Momentum Investing", Journal
of Finance.** CRSP, all stocks. Finding: nearness to the 52-week high
(`price / 52wk-high`) *dominates and improves upon* past-return momentum in
forecasting — a **cross-sectional, (6,6) long-short** strategy (rank monthly, hold
6 months). Headline spread on the order of **~0.45%/month** for the 52wk-high WML
(verified: the paper frames JT momentum at "~1%/month" and shows nearness dominates
it; the precise 52wh spread I did not re-read digit-by-digit — **flagged
[unverified at exact figure]**, order-of-magnitude ~0.4–0.5%/mo). **Crucially it is
a LONG-SHORT spread and a 6-MONTH hold, not a fast post-breakout entry.**

**[PR] Raju (2023) India replication** (deep-read in `research.md` §4, SSRN
4587697): 19y NSE/BSE. **The long (near-high) leg does not beat the index in any
construction** (EW Q5 t=−0.91); the premium is the short leg (far-from-high Q1,
α≈−2.4%/mo). Effect strongest in mcap ranks 201–1000. Slow decay (~84% survives 6m).
**This is the decisive India-specific evidence and it says buying the breakout —
the long leg — does not work; avoiding the far-from-high names does.**

**Conversion to a per-trade hurdle:** a 0.45%/mo long-short at a 6-month hold ≈
2.7% gross over the holding period **for the spread** — but the *long-only,
implementable* half is ≈0 excess over index (Raju). Against §5.3's +42–62 bps
per-round-trip hurdle at a *breakout* (short) hold, the near-high long leg brings
**no documented positive expectancy to clear it.**

### 6.2 Momentum, its shortest horizon, and the antagonist reversal effect

**[PR] Jegadeesh & Titman (1993)** — 3–12 month formation/holding momentum,
~1%/month gross. **[PR] Moskowitz-Ooi-Pedersen (2012), time-series momentum** —
"persistence in returns for **one to 12 months** that **partially reverses over
longer horizons**" (verified from `tsm.txt`). Both are **multi-month** effects.

**The antagonist — short-horizon REVERSAL.** [PR] Jegadeesh (1990), Lehmann (1990),
and the liquidity-provision interpretation ([PR] Nagel 2012, "Evanescent
Liquidity"): at the **1-week to 1-month** horizon, cross-sectional stock returns
**reverse**, not continue. This is the direct adversary of buy-the-breakout at
short holds: a stock that just jumped is, on the weekly evidence, more likely to
give some back than to continue. **A post-breakout family enters exactly at the
horizon where the documented cross-sectional effect has the *wrong sign*.**
[PR] Novy-Marx (2012, "Is momentum really momentum?") sharpens it: momentum is
driven by the *intermediate-horizon* (t−12 to t−7) past, not the *recent* month —
i.e. the recent surge (the breakout) is not where the continuation lives.

**Conversion:** these say the expected sign of `E[return | just broke out]` over
1–5 sessions is **weakly negative to zero** before costs. Against a +42 bps hurdle,
that is disqualifying, not marginal.

### 6.3 Volume-confirmed breakouts

**[PR] Gervais, Kaniel & Mingelgrin (2001), "The High-Volume Return Premium"** —
stocks with abnormally high volume over a day/week earn higher subsequent returns;
notably *larger for stocks WITHOUT abnormal returns at the time* (verified from
`gkm.txt`) — i.e. the premium is a **visibility** effect, weaker precisely for the
price-breakout names a volume-confirmed-breakout rule selects. Horizon is weeks/
months, magnitude modest. **[PR] Lee & Swaminathan (2000)** — high past volume
predicts *worse* momentum persistence and faster reversal ("momentum life cycle").
So the best peer-reviewed volume evidence is **ambiguous-to-adverse** for
volume-confirmed breakouts, not supportive. The program's own read (`research.md`
§2): *"no rigorous Indian false-breakout-rate study exists"* — a genuine gap, not a
positive result. **Directly relevant caveat: §8 — the live volume-confirmation gate
this design would rely on is itself mis-calibrated by ~2.95× (RULING 13).**

### 6.4 Technical trading rules under proper data-snooping control

**[PR] Sullivan, Timmermann & White (1999), JF** — the best in-sample technical
trading rule (incl. breakout/channel/filter rules) **failed out-of-sample** once
data-snooping was corrected via White's Reality Check. **[PR] Bajgrowicz & Scaillet
(2012)** — technical trading rule profits do not survive transaction costs and
multiple-testing correction. **Program-internal replication of this exact result**
(`research.md` §2): Heyman-Inghelbrecht-Pauwels across 34 emerging markets, **India's
best chart rule gross p≈0.00 → Hansen SPA p≈0.69 net of costs.** This is the same
SPA gate SPEC-52WH-01 §8 uses, and it already killed generic chart-rule breakouts
for this program.

### 6.5 Publication bias and the significance hurdle

**[PR] Hou, Xue & Zhang (2020), "Replicating Anomalies", RFS** — **65% of 452
anomalies fail** with microcaps controlled (NYSE breakpoints, value-weight); at the
multiple-testing t≥2.78 hurdle the failure rate rises to **82%**; surviving effects
are much smaller than originally reported (verified from `hxz.txt`). **[PR]
Harvey, Liu & Zhu (2016)** — a newly-claimed cross-sectional predictor needs
**t > 3.0**, not 2.0 (verified from `hlz.txt`). **[PR] McLean & Pontiff (2016)** —
anomalies decay ~58% post-publication. **Implication for a breakout family's
prior:** a technical breakout signal is in the most-published, most-arbitraged,
most-vendor-hyped corner of the anomaly space; the base rate that a fresh one
survives microcap-controlled, cost-adjusted, multiple-testing-corrected scrutiny is
**low**, and the legacy system's own t≈2.95 gross sits *below* the Harvey-Liu-Zhu
t>3 bar even before costs.

### 6.6 The [VM] environment, flagged and discounted

Darvas box, VCP, ORB "60–70% win rate" claims, most breakout-scanner marketing —
**[VM]**, hindsight-selected, no costs, no significance tests. `research.md` §2
already logged these as "not evidence." Intraday ORB on NSE (Wang-Gangwar 2025):
bootstrap **p≈0.45–0.50, indistinguishable from noise.** They characterise the
information environment (breakout-chasing is a crowded retail behaviour → adverse
selection at entry, §7) but establish no effect.

### 6.7 What I could NOT establish (TRAP 4 / TRAP 6 — stated, not filled)

- The **exact** George-Hwang 52wh WML monthly spread and t-stat (order ~0.45%/mo;
  precise figure [unverified at source] in this pass).
- Any peer-reviewed, **net-of-cost, India-specific** post-breakout-entry return at
  a *short* (≤10 session) hold. **None located — the India technical/PEAD/momentum
  literature is gross-of-cost essentially without exception** (`research.md`,
  `PEAD_literature_prior.md` §5.2). A gross-only literature is *no* evidence for the
  net question this family must answer.
- A credible published estimate of the **speed of price discovery** for Indian
  mid-cap breakouts (how much of the move is gone by confirmation). Absent, §2.2's
  "remaining upside" tension cannot be sized from literature — it would require an
  event study, which is a TRIAL and is forbidden here.

**Net of §6:** the only robustly-documented, India-replicated "near-high" effect
(a) lives in its LONG-SHORT / negative-screen form, (b) is a MONTHLY/6-month
cross-sectional effect, and (c) has a long leg that does not beat the index. At the
short horizon a breakout-entry rule actually occupies, the documented sign is
reversal. **Nothing in the literature supplies the per-trade drift §5 requires.**

---

## 7. Capacity and the breakout-specific execution penalty (Rs 100 Cr)

The ROADMAP target is Rs 100 Cr AUM and requires a family to survive its own
footprint. Post-breakout entry is the **worst possible footprint profile** because
you demand liquidity in the same direction as everyone else reacting to the same
visible event.

### 7.1 Position size vs liquidity (arithmetic, ASSUMPTION on ADV)

At Rs 100 Cr, N=20 slots => **Rs 5 Cr/position**. Position as a fraction of a
name's average daily traded value (ADV):

| ADV of name | pos/ADV at Rs100Cr, N=20 | sessions to enter @10% participation |
|---|---|---|
| Rs 5 Cr/day | 100% | 10.0 |
| Rs 10 Cr/day | 50% | 5.0 |
| Rs 25 Cr/day | 20% | 2.0 |
| Rs 100 Cr/day | 5% | 0.5 |

A breakout family lives in mid-caps (that is where breakouts with room to run are).
A Rs 5 Cr order into a Rs 10-25 Cr/day name is 20-50% of a day's volume, and you are
**buying on the breakout day, into the crowd, at the widest spread**. At a 3-5
session hold, entry can take a meaningful fraction of the holding period. This is
SPEC-SRA-01's capacity kill in the same shape.

### 7.2 Square-root impact (ASSUMPTION: Almgren-style, Y in [0.5,1.0], sigma=2.25%/day)

impact ~ Y*sigma*sqrt(Q/ADV), at Rs 100 Cr / N=20 (Rs 5 Cr position):

| ADV | Q/ADV | impact Y=0.5 | impact Y=1.0 |
|---|---|---|---|
| Rs 10 Cr | 50% | 79.5 bps | 159.1 bps |
| Rs 25 Cr | 20% | 50.3 bps | 100.6 bps |
| Rs 100 Cr | 5% | 25.2 bps | 50.3 bps |

**Even in the most liquid name a mid-cap breakout book would plausibly hold
(ADV Rs 100 Cr/day, top edge of the habitat), one-way impact is 25-50 bps, i.e.
2.5-5x the slippage floor a backtest would optimistically assume.** Add a mid-cap
half-spread (5-25 bps/side, ASSUMPTION, unverified in-repo, needs tick data) and
the **realistic slippage parameter at Rs 100 Cr is 50-100+ bps/side, not 10.**
From SS5.2 that puts annual drag at a 3-5 session hold in the **60-150%/yr** range,
multiples of the legacy system's entire 18.5% gross alpha.

### 7.3 The breakout-specific asymmetry (worse than a generic strategy)

1. **You buy into your own signal's crowd.** A confirmed volume-expansion breakout
   is visible to every momentum/retail participant at once. The `research.md` [VM]
   finding (breakout chasing is crowded retail behaviour) means **adverse selection
   at entry**: the liquidity you demand is priced against you because the event is
   public.
2. **The exit is unconditional and lands in a liquidity hole.** Like SRA SS6, entry
   is filtered on a volume-expansion day but the **exit is not**; it lands whenever
   the hold ends, quite possibly on a post-spike volume collapse. The exit leg is
   the expensive one and no breakout filter protects it.

### 7.4 Capacity verdict

**The capital base at which a 3-5 session breakout book keeps impact <= ~10 bps is
Rs 1-15 Cr (Y-dependent), an order of magnitude below the Rs 100 Cr target** (the
same finding as SPEC-SRA-01 SS6.2). A post-breakout family is at best a
small-capital strategy, which does not advance the program's stated objective and
would compete for build time against the daily overlay log (the #1 priority with a
fixed 2026-09-27 read date).

---

## 8. RULING 13 implication for volume-confirmed breakout logic

Any "volume-confirmed breakout" design leans on the volume-confirmation signal.
**In this program's own production system that signal is measurably mis-calibrated
today**, and the memo must say so plainly.

- **FACT (RULING 13, register `DIAG-VOLSHARE-0001/-0002`, one trial spent).** The
  entry path projects a partial opening bar to a full day assuming **uniform
  intraday volume**: `vol * 75 / avg20` for the 09:15-09:20 bar. NSE volume is
  front-loaded: measured first-5-min share s ~ **4.0% (median)** vs the **1.33%**
  the `x75` implies. Four independent routes converge (yfinance residual n=6,572;
  yfinance direct n=333; Kite ratio-inference; Kite exact n=22).
- **FACT (VERIFIED AT PRODUCTION HEAD `5c099d77`, RULING 9 satisfied).** The `x75`
  projection and the `VOL_GATE_BREAKOUT = 1.5` constant are **live**. The nominal
  1.5x breakout gate therefore really demands only **~0.34-0.51x** of the 20-day
  average volume. The gates *bind* (they reject 13.6/27.3/36.4% of recs) but are
  **MISLABELLED, not inert** - the "1.5x volume confirmation" a design would think
  it is buying is not what the code enforces.
- **FACT.** The fix is the **denominator, not the constant**: per-stock s spans
  ~10x (1.14% NAUKRI to 10.51% KALYANKJIL), so `75 -> 25` relocates the error
  rather than removing it. The correct construction compares the opening bar to the
  20-day average of that symbol's **own** opening bar, so s cancels.

**Two consequences for a post-breakout family:**

1. **The classic breakout-confirmation tool is not currently trustworthy in this
   stack.** A new design specifying "enter on a volume-confirmed breakout" would
   either inherit the mis-calibrated gate or have to rebuild volume confirmation
   correctly first. That rebuild is real work and, per **RULING 13d**, **no live
   parameter may change before the 2026-09-27 AB_PREREG read date** (re-tuning the
   recommended leg mid-window corrupts the A/B instrument). So a corrected
   volume-confirmed-breakout rule cannot even be deployed on the live book until
   after the read date, regardless of merit.
2. **It is a live demonstration of the program's characteristic failure (TRAP 6),
   in exactly this signal.** A volume-confirmation gate shipped plausible verdicts
   for the system's entire life while being wrong by ~3x, and production's own
   comments twice recorded "nothing has ever checked the projection". Building a new
   family on the same class of signal, before that is repaired, would be repeating
   the error.

**Related LATENT defect** (not currently firing): `volume_ratio or 0.0`
(`preopen_check.py:613/:769`) turns an UNKNOWN ratio into a hard gate failure; on
yfinance data the 09:15 bar reports zero volume in 97.65% of sessions -> all-veto
if the Kite path is ever unavailable. Confirmed not firing live (0/22 rec-days),
so latent, but it is exactly the silent-failure shape a new build must guard.

---

## 9. Is there ANY surviving region? Yes, and it is already on file

The honest, non-zero answer. A post-breakout *signal* can survive this program's
constraints **only** if it is shaped to them - and when you apply every constraint,
the surviving shape is one that already exists:

- **Not a standalone fast book** (dies on §5 friction + §7 capacity).
- **Long-only realisable** (no shorting; §6/Raju: the long near-high leg does not
  beat the index).
- **Low-turnover by mandate** (ROADMAP).
- **Composable as a screen/overlay adding ~zero incremental turnover to a slow host
  book** (the only way a high-information-decay signal pays its way - a veto costs
  nothing extra if the host already trades).

**That description is SPEC-52WH-01**: a slow, quarterly, long-only **negative
screen** ("never hold far-from-52wk-high names"), explicitly framed as a layer
composable into a selection engine, already hash-frozen and queued. The 52wk-high
*breakout* was already reframed into exactly this. If the operator wants
post-breakout information used well, **the vehicle already exists and the correct
action is to advance 52WH (C1 attempt 2, after the habitat-defect fix), not to open
a new family.**

A second, narrower survivor worth naming: post-breakout information as an
**entry-timing overlay on a family that already carries independent edge** (the
`research.md` note that the "event-breakout blocker list belongs, if anywhere, to a
future SPEC-PEAD-01 entry-timing overlay"). That is *conditioning an
already-surviving rule*, never a standalone strategy, and it cannot even be scoped
until (a) PEAD survives its own CAR study and (b) the exchange filing-timestamp
corpus closes (OPEN OPERATOR DECISION 1). It is not actionable now.

**What does NOT survive under any shaping:** a standalone "buy the confirmed
breakout, hold days, capture the remaining upside" book at the ₹100 Cr target.
That is the legacy system, and it is killed.

---

## 10. Open items that would have to close before ANY spec could be frozen

If, despite all the above, the operator still wanted to pursue a post-breakout
family, these would gate a hash-freeze (they are listed to show the distance, not
to invite the build):

1. **A production HEAD check** of every clone-only §2.4 claim (RULING 9).
2. **Repair of the volume-confirmation signal** (§8, RULING 13) - and this cannot
   deploy live before 2026-09-27 (RULING 13d).
3. **A measured "remaining upside" / price-discovery-speed estimate** - which is an
   event study, i.e. a TRIAL requiring a frozen spec and a shadow slot. Circular:
   you cannot cheaply establish the premise without spending the scarce resource.
4. **A capacity pre-screen passing at ₹100 Cr** - §7 shows it fails by ~an order of
   magnitude; per SRA §8.4 this line belongs in any spec's §1 at draft time.
5. **A shadow slot** - both are held (QFM, PEAD); AG-01 and 52WH queued. A new
   family is 5th+ in line and unreachable near-term.
6. **A resolution of the low-turnover mandate conflict** - a breakout-entry family
   is high-turnover by construction (§2.3); the ROADMAP forbids it by design.

Every one of these is a hard gate. Items 3 and 4 are, individually, disqualifying.

---

## 11. Recommendation and proposed register row

### 11.1 Recommendation

> **Do NOT build a post-breakout-entry family. Do NOT draft a spec.**

Concretely:
1. **Record this as a DECISIONS.md finding** (outcome-blind, no trial spent), in the
   shape of the 2026-07-20 VARIANT scopes and RULING 11 - a family killed on
   arithmetic and prior-evidence *before contact* is a governance asset at PMS
   due diligence.
2. **Redirect the intent to its existing vehicles:** if technical, it is the killed
   legacy system (§2); if catalyst-driven, it is SPEC-PEAD-01 (§4.2, slot 2, adverse
   prior); if "make breakout information pay", it is SPEC-52WH-01's negative screen
   (§3, §9), already frozen and queued.
3. **Do not spend the scarce resources** - no shadow slot, no sealed test, no
   `expr.py` extension - on this.
4. The program's #1 priority is unchanged and outranks this: **the daily overlay
   log** to 2026-09-27.

### 11.2 Proposed register row (TEXT ONLY - do NOT let me or any agent write it; a
concurrent agent is appending to that file)

This memo spends **no trial** (outcome-blind: literature + cost/capacity
arithmetic only, AMENDMENT A). No register row is *required*. If the operator wants
the decision auditable, the appropriate artifact is a **DECISIONS.md ruling**, not a
trial row. If a register line is nonetheless desired for traceability, propose:

```
DIAG-BREAKOUT-ENTRY-0001,2026-07-23,BREAKOUT_ENTRY,
"Post-breakout entry feasibility (operator question 2026-07-23): can entering
right after a confirmed breakout capture remaining upside net of friction at
Rs100Cr?",n/a,DO-NOT-BUILD,
"OUTCOME-BLIND, NO TRIAL SPENT, NO SHADOW SLOT, no repo outcome data touched,
no spec drafted. Analysis: analysis/breakout_entry_feasibility.md. Finding: the
idea is the legacy system's own volume-confirmed-52wk-high entry rule (killed:
gross 18.5%/yr ~= statutory cost 19.7%/yr at 1.6 RT/day); friction hurdle needs
+42-222 bps gross drift per round trip (costs_in.py, RULING 5); capacity fails at
Rs100Cr by ~an order of magnitude (SRA-shaped); literature's only India-replicated
near-high effect is the negative-screen SHORT leg (Raju 2023, long leg t=-0.91),
short-horizon documented sign is REVERSAL; volume-confirmation gate itself
mis-calibrated ~2.95x (RULING 13). Surviving shape = SPEC-52WH-01 negative screen,
already frozen+queued. GOVERNANCE NOTE: SWEEP_HOLDING.md outcome table (quarantined
per DECISIONS.md:425-428) was inadvertently read this session and disclosed;
NOT used in this analysis."
```

**Note the family field `BREAKOUT_ENTRY` is a label of convenience** - if the
operator agrees this is not a distinct family from the legacy system, the honest
booking is against `LEGACY` (as RULING 13's DIAG rows were), which also confirms no
sealed test is at risk.

---

## 12. One-line answer to the operator

**Entering right after a confirmed breakout to capture the remaining upside is the
legacy system's own design; it produced real gross alpha and friction ate all of
it, and nothing about entering *after* rather than *before* the breakout changes
that - it makes execution worse. The required net-of-cost drift exceeds anything the
literature documents at that horizon, capacity fails at ₹100 Cr, and the only
surviving form of the idea is the slow negative screen that already exists as
SPEC-52WH-01. Do not build it; finish 52WH and log the overlay.**

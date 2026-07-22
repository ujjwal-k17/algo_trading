# SPEC-SRA-01 — Friction hurdle (analytic, pre-freeze, OUTCOME-BLIND)

**Date:** 2026-07-21
**Author:** research session, at operator request
**Status:** DIAGNOSTIC, NOT A TRIAL. No price panel was loaded, no return series was
read, no backtest was run, no label was computed. Every number below is derived
from published statutory constants (`src/costs_in.py`, RULING 5), the text of
`governance/specs/SPEC-SRA-01.md`, and explicitly-labelled ASSUMPTIONS about
market microstructure. Nothing here is charged against the register's trial count
under `CONTAMINATION_POLICY.md` (outcome-blind diagnostics are free).

**Spec status at time of writing:** SPEC-SRA-01 is a **DRAFT** — no `sha256`, no
register row, no outcome contact authorized. This analysis is exactly the kind of
work the draft banner permits: it interrogates the design, not the data.

---

## 0. The question, and the one-line answer

SPEC-SRA-01 §0 states that "the cost test comes first and cannot be deferred", and
§1 pre-states the null that "the expected outcome of this family is death at §8".

This document runs that cost test with no data contact.

**One-line answer: the family clears its own §8.1 kill line only in a slippage
regime it cannot occupy, and fails §8's capacity clause outright at the program's
₹100 Cr target — by roughly an order of magnitude, on the spec's own mandatory
liquidity floor. Recommendation: KILL NOW at zero cost. Do not extend `src/expr.py`,
do not build `src/signal_sra.py`, do not hash-freeze.**

---

## 1. The cost stack, itemised (RULING 5)

Source of every constant: `src/costs_in.py`, closed by RULING 5 (`governance/DECISIONS.md`,
2026-07-19). Exchange-charge evidence:
`governance/evidence/NSE_FA_73061_transaction_charges_effective_2026-03-01.pdf`.

The §5 rule holds overnight (entry at open t+1, exit at close t+5), so it is a
**DELIVERY** product. Intraday rates do not apply.

| Component | Constant | Units | Applies | Tag |
|---|---|---|---|---|
| STT, delivery | `STT_DELIVERY = 0.001` | fraction of traded value | buy **and** sell | **FACT** (statutory) |
| NSE exchange transaction | `EXCHANGE_TXN = 0.0000307` | fraction, per side | both | **FACT** (NSE/FA/73061) |
| SEBI turnover fee | `SEBI_FEE = 0.000001` | fraction, per side (₹10/cr) | both | **FACT** (statutory) |
| Stamp duty, delivery | `STAMP_DELIVERY_BUY = 0.00015` | fraction | **buy only** | **FACT** (statutory) |
| GST | `GST = 0.18` | on (brokerage + exchange + SEBI) | both | **FACT** (statutory) |
| Brokerage, delivery | `BROKERAGE_DELIVERY = 0.0` | fraction | both | **ASSUMPTION** (operator, RULING 5 — zero-brokerage delivery plan; contract-note reconciliation WAIVED) |
| DP charge | `DP_CHARGE_SELL = 15.34` | **flat ₹ per scrip per day**, GST-incl. | **sell only** | **ASSUMPTION** (operator, RULING 5) |
| Slippage | `SLIPPAGE_FLOOR_PER_SIDE = 0.0005` | fraction, per side | — | **DELIBERATELY NOT APPLIED HERE** — separate explicit parameter by RULING 5. SPEC-SRA-01 §7 raises the family's own floor to **0.10%/side**. |

Two lines rest on an operator ASSUMPTION (brokerage and DP). Both are *small*: at a
₹5 Cr position they contribute 0.0 bps and 0.006 bps respectively. **The conclusion
of this document is insensitive to both.** If the real contract note bills 0.03%
delivery brokerage instead of zero, the round trip rises by 7.1 bps and the verdict
gets worse, never better.

### 1.1 Worked round trip — the representative trade

Representative trade: a delivery buy at the open of *t+1*, a delivery sell at the
close of *t+5*, one scrip-day of DP. Traded value assumed equal on both legs (see
ASSUMPTION A5, §7).

At a **₹1,00,000** slot (matching the figure already recorded in `DECISIONS.md`
2026-07-20, Variant A, so this recomputation is a cross-check):

```
BUY  leg: brokerage    0.00
          STT        100.00   (0.100%)
          exchange     3.07   (0.00307%)
          SEBI         0.10
          stamp       15.00   (0.015%)
          GST          0.5706
          DP           0.00
          ------------------
          total      118.7406

SELL leg: brokerage    0.00
          STT        100.00
          exchange     3.07
          SEBI         0.10
          stamp        0.00   (buy-side only)
          GST          0.5706
          DP          15.34   (flat)
          ------------------
          total      119.0806

ROUND TRIP  ₹237.8212 on ₹1,00,000  =  0.237821%  =  23.782 bps
```

Reconciles exactly with `DECISIONS.md` line 400 (0.23782%). **Verification passed.**

Round-trip decomposition in bps (₹1L slot):

| Line | bps | share |
|---|---|---|
| STT (both sides) | 20.000 | 84.1% |
| Stamp (buy) | 1.500 | 6.3% |
| DP (flat ₹15.34) | 1.534 | 6.5% |
| Exchange txn | 0.614 | 2.6% |
| GST | 0.114 | 0.5% |
| SEBI | 0.020 | 0.1% |
| Brokerage | 0.000 | 0.0% |
| **Statutory total** | **23.782** | 100% |

**STT is 84% of the statutory bill and is irreducible.** There is no broker, venue,
or execution choice that touches it. This is the structural reason a short-horizon
Indian cash-equity family is hard: the tax is charged on *turnover*, so it scales
linearly with 1/H.

### 1.2 Scale dependence

Only DP is a flat rupee charge, so the round trip falls slightly with position size
and then asymptotes:

| Position size | statutory round trip |
|---|---|
| ₹1,00,000 | 23.782 bps |
| ₹25,00,000 | 22.309 bps |
| **₹50,00,000 (₹100 Cr ÷ 20)** | **22.279 bps** |
| ₹2,50,00,000 | 22.254 bps |

**All subsequent tables use 22.279 bps** as the statutory base, i.e. the ₹5 Cr
position implied by ₹100 Cr AUM at the §5 cap of N=20. Using the ₹1L figure instead
moves every number by +1.5 bps per round trip and does not change any conclusion.

---

## 2. What SPEC-SRA-01 actually claims (§§1, 5, 7, 8)

Read verbatim from `governance/specs/SPEC-SRA-01.md`:

| Item | Spec text | Section |
|---|---|---|
| Hypothesis | a feature combination at close *t* raises P(≥10% move over *t+1…t+5*) materially above base rate, **by enough to survive RULING 5 friction at the implied turnover** | §1 |
| Label | `fwd5 = close(t+5)/close(t) − 1`; `rally = 1 if fwd5 ≥ 0.10` | §2 |
| Habitat | PIT mcap ranks **201–1000**, announce-gated; **mandatory** liquidity floor: rolling 60-session median traded value **≥ ₹2 Cr/day** | §4 |
| Entry | **open of t+1** | §5 |
| Exit | **fixed at close of t+5** — no stop, no target, no trailing | §5 |
| Sizing | equal weight, cap **N = 20** positions, flat, no conviction weighting ever | §5 |
| Implied turnover | "~50 round-trips/yr per slot ⇒ order **~5,000%/yr one-way** at full deployment" | §5 |
| Headline metric | **net expectancy per fire, in bps**, after RULING 5 + explicit slippage **≥ 0.10%/side** | §7 |
| Kill 8.1 | net expectancy per fire **≤ 0** ⇒ dead | §8 |
| Kill 8.2 | SPA p > 0.10 across the **full grid**, net ⇒ dead | §8 |
| Kill 8.3 | one-way turnover **> 6,000%/yr** ⇒ dead | §8 |
| Kill 8.4 | support **< 200** firing events ⇒ dead | §8 |
| Capacity | "capacity failure at ₹100 Cr in the deployable band **kills independently of alpha**… C3 capacity is **not deferrable** for this family" | §8 |

Note the spec is unusually well-constructed here: §8.1 is stated **per fire**, which
makes it independent of deployment fraction (how many of the 20 slots are actually
filled on an average day). That is the right choice and it removes a whole class of
ambiguity — see ASSUMPTION A4.

**Turnover, recomputed:** the position occupies sessions *t+1 … t+5* = 5 sessions.
At 252 sessions/yr, one slot recycles **252/5 = 50.4 times/yr**, i.e. **5,040%/yr
one-way** at full deployment. The spec's "~5,000%" is correct. §8.3's budget of
6,000% therefore sits only **19% above the design itself** — as the spec says, it
binds on over-firing variants, not on the base design. **§8.3 does not kill the
primary configuration.** The kill, if it comes, comes from §8.1 or capacity.

---

## 3. Round-trip cost with slippage, and annual drag

Slippage is kept as a separate explicit parameter (RULING 5). Round-trip cost
`c = 22.279 bps + 2 × s`, where `s` = slippage per side in bps.

Annual drag per rupee deployed = `c × 50.4`.

| Slippage (bps/side) | Round trip (bps) | Annual drag (%/yr) | × legacy gross alpha (18.5%) |
|---|---|---|---|
| 5 | 32.28 | 16.27 | 0.88 |
| **10** (spec §7 floor) | **42.28** | **21.31** | **1.15** |
| 15 | 52.28 | 26.35 | 1.42 |
| 20 | 62.28 | 31.39 | 1.70 |
| 30 | 82.28 | 41.47 | 2.24 |
| 50 | 122.28 | 61.63 | 3.33 |
| 75 | 172.28 | 86.83 | 4.69 |
| 100 | 222.28 | 112.03 | 6.06 |

**Read the last column.** At the spec's own mandated slippage floor of 10 bps/side,
this family must generate **more gross alpha than the entire legacy system did**
(18.5%/yr, from a six-factor score with fundamentals, catalyst, quality and an LLM
vision layer, developed over ~51 registered trials) merely to reach zero. At any
realistic mid-cap slippage it must generate a multiple of it.

**Drag is proportional to 1/H and independent of slot count** (established as FACT
in `DECISIONS.md`, 2026-07-20, Variant A). The only structural lever is the holding
period, and §2 fixes it at exactly 5 sessions and forbids treating it as a free
parameter. For reference, the holding period that would bring drag under a 6%/yr
budget:

| Slippage | H required for ≤6%/yr drag | for ≤10%/yr |
|---|---|---|
| 10 bps/side | 17.8 sessions | 10.7 sessions |
| 20 bps/side | 26.2 sessions | 15.7 sessions |
| 30 bps/side | 34.6 sessions | 20.7 sessions |

**A family that pays its friction is a 4–7 week family, not a 5-day family.** That is
a different spec, not a sensitivity of this one.

---

## 4. Sanity anchor against the legacy kill

`CLAUDE.md`: legacy daily mid-cap momentum, gross alpha **~18.5%/yr, t ≈ 2.95,
fully consumed by friction at 1.6 round-trips/day**.

Deriving the legacy turnover on the same basis (5 slots, 1.6 round-trips/day across
the book ⇒ 0.32 round-trips/day/slot ⇒ implied **H ≈ 3.125 sessions**, consistent
with the H≈3.1 already recorded in `DECISIONS.md`):

- legacy round trips/yr/slot = 252 / 3.125 = **80.6**
- legacy one-way turnover = **8,064%/yr**
- legacy statutory-only drag = 80.6 × 23.782 bps = **19.18%/yr** — already above the
  18.5% gross alpha, **before a single basis point of slippage**. That is the kill,
  reproduced from constants.
- at 5 bps/side: 27.24%/yr. At 10 bps/side: 35.31%/yr.

**Where SRA sits:**

| | one-way turnover | H | statutory drag | drag @10bps/side |
|---|---|---|---|---|
| Legacy (killed) | 8,064%/yr | 3.1 sess | 19.18%/yr | 35.31%/yr |
| **SPEC-SRA-01** | **5,040%/yr** | **5.0 sess** | **11.22%/yr** | **21.31%/yr** |
| ratio | **0.62×** | 1.6× | 0.58× | 0.60× |

**SRA is in the same friction regime as the system this program already killed.** It
is 38% cheaper — a real improvement, and not remotely enough. The legacy system
failed by a factor of ~1.04 on statutory alone and ~1.9 including slippage. SRA
starts 0.6× down that hole, so it needs gross alpha of **1.15× legacy's** just to
reach zero at the optimistic slippage floor, and it proposes to get there with
**8 OHLCV features and depth-3 AND-combinations** — strictly less machinery than the
system that produced 18.5%.

This is the single most important sentence in this document: **SRA must out-earn, on
less information, a system that already lost this exact fight.**

---

## 5. Breakeven frontier — hit rate vs payoff ratio

### 5.1 The assumption-free version (state this first)

The §5 rule has no stop and no target: it holds from the open of *t+1* to the close
of *t+5* unconditionally. So the P&L per fire is simply `fwd5`, and §8.1 reduces to:

> **E[ fwd5 | setup ] ≥ c**

with **no distributional assumption at all**. That gives the hurdle directly:

| Slippage (bps/side) | Required E[fwd5 \| setup] | Annualised equivalent |
|---|---|---|
| 5 | **+32.3 bps** per fire | 16.3%/yr |
| **10** (spec floor) | **+42.3 bps** per fire | **21.3%/yr** |
| 20 | **+62.3 bps** per fire | 31.4%/yr |
| 30 | **+82.3 bps** per fire | 41.5%/yr |
| 50 | **+122.3 bps** per fire | 61.6%/yr |
| 100 | **+222.3 bps** per fire | 112.0%/yr |

That is the whole cost test in one row: **the setup must predict a mean 5-session
return of at least +0.42%** (spec floor) **to +2.22%** (₹100 Cr capacity-implied,
§6) **above zero, every time it fires, before it is worth transacting.**

If the benchmark-relative version is wanted (§7's secondary metric, net IR vs
NIFTY500 TRI), add the index's 5-session drift — at an ASSUMED 12%/yr that is
+23.8 bps, so the hurdle becomes **+66 bps to +246 bps per fire**.

### 5.2 The hit-rate / payoff frontier

Write `p` = fraction of fires that are winners, `W` = mean gross winner (%),
`L` = mean gross loser magnitude (%), `R = W/L` = payoff ratio. Breakeven:

```
p·W − (1−p)·L − c = 0
⇒  p* = (L + c) / (W + L)  =  (1 + c/L) / (R + 1)
```

**Breakeven hit rate `p*`, at slippage = 10 bps/side (spec §7 floor, `c` = 0.4228%):**

| mean loser `L` | R = 1.0 | R = 1.25 | R = 1.5 | R = 2.0 | R = 3.0 |
|---|---|---|---|---|---|
| 3.0% | 57.05% | 50.71% | 45.64% | 38.03% | 28.52% |
| **5.0%** | **54.23%** | **48.20%** | **43.38%** | **36.15%** | **27.11%** |
| 7.0% | 53.02% | 47.13% | 42.42% | 35.35% | 26.51% |
| 10.0% | 52.11% | 46.32% | 41.69% | 34.74% | 26.06% |

**At slippage = 20 bps/side (`c` = 0.6228%):**

| mean loser `L` | R = 1.0 | R = 1.25 | R = 1.5 | R = 2.0 | R = 3.0 |
|---|---|---|---|---|---|
| 3.0% | 60.38% | 53.67% | 48.30% | 40.25% | 30.19% |
| **5.0%** | **56.23%** | **49.98%** | **44.98%** | **37.49%** | **28.11%** |
| 7.0% | 54.45% | 48.40% | 43.56% | 36.30% | 27.22% |
| 10.0% | 53.11% | 47.21% | 42.49% | 35.41% | 26.56% |

**At slippage = 30 bps/side (`c` = 0.8228%):**

| mean loser `L` | R = 1.0 | R = 1.25 | R = 1.5 | R = 2.0 | R = 3.0 |
|---|---|---|---|---|---|
| 3.0% | 63.71% | 56.63% | 50.97% | 42.48% | 31.86% |
| **5.0%** | **58.23%** | **51.76%** | **46.58%** | **38.82%** | **29.11%** |
| 7.0% | 55.88% | 49.67% | 44.70% | 37.25% | 27.94% |
| 10.0% | 54.11% | 48.10% | 43.29% | 36.08% | 27.06% |

**How to read this table without fooling yourself.** `p*` and `R` are NOT free
parameters. For any zero-mean return distribution, `R ≈ 1` and `p ≈ 50%` are forced
together. You cannot claim "R = 3, so I only need 27%" — a rule with `R = 3` on an
uncapped, stopless 5-session hold is a rule whose winners are 3× its losers, which
is a *far stronger* claim than a 54% hit rate at `R = 1`. **The diagonal of these
tables is one number, not a menu.**

The invariant that matters is the **edge over a fair coin**, which for `R = 1`
is exactly `c / (2L)`:

| Slippage | L = 3% | L = 5% | L = 7% |
|---|---|---|---|
| 10 bps/side | +7.05 pp | **+4.23 pp** | +3.02 pp |
| 20 bps/side | +10.38 pp | **+6.23 pp** | +4.45 pp |
| 30 bps/side | +13.71 pp | **+8.23 pp** | +5.88 pp |
| 50 bps/side | +20.38 pp | **+12.23 pp** | +8.73 pp |
| 100 bps/side | +37.05 pp | **+22.23 pp** | +15.88 pp |

### 5.3 Translated into the spec's own event language (§3)

The spec's diagnostic is `lift = P(rally | setup) − P(rally)`. Decomposing per-fire
expectancy into the ≥10% tail and the rest, under ASSUMPTIONS A1–A3 (§7):

Take 5-session returns as approximately N(drift, σ₅). Then `base = P(fwd5 ≥ 10%)`,
`E[fwd5 | event]` is the truncated mean, and `E[fwd5 | non-event]` is pinned by
requiring the unconditional mean to equal the index drift. Requiring
`q·E[event] + (1−q)·E[non-event] = c` gives the **required conditional event rate `q`**:

**σ₅ = 5.5% (⇒ base = 3.45%, E[ret|event] = +12.17%) — closest to the spec's own "~3%" guess:**

| Slippage | required `q` | lift | as a multiple of base |
|---|---|---|---|
| 10 bps/side | 4.95% | +1.49 pp | **1.43×** |
| 20 bps/side | 6.56% | +3.11 pp | **1.90×** |
| 30 bps/side | 8.18% | +4.73 pp | **2.37×** |
| 50 bps/side | 11.42% | +7.97 pp | **3.31×** |
| 100 bps/side | 19.51% | +16.06 pp | **5.65×** |

**σ₅ = 6.5% (⇒ base = 6.20%):**

| Slippage | required `q` | lift | multiple of base |
|---|---|---|---|
| 10 bps/side | 7.57% | +1.38 pp | 1.22× |
| 20 bps/side | 9.07% | +2.87 pp | 1.46× |
| 30 bps/side | 10.56% | +4.36 pp | 1.70× |
| 50 bps/side | 13.54% | +7.34 pp | 2.19× |
| 100 bps/side | 21.00% | +14.80 pp | 3.39× |

**σ₅ = 8.0% (⇒ base = 10.56%):**

| Slippage | required `q` | lift | multiple of base |
|---|---|---|---|
| 10 bps/side | 11.78% | +1.22 pp | 1.12× |
| 20 bps/side | 13.10% | +2.53 pp | 1.24× |
| 30 bps/side | 14.41% | +3.85 pp | 1.36× |
| 50 bps/side | 17.04% | +6.48 pp | 1.61× |
| 100 bps/side | 23.62% | +13.06 pp | 2.24× |

**The absolute lift required is robust to σ₅ (1.2–1.5 pp at the spec floor; 13–16 pp
at ₹100 Cr capacity-implied slippage); the relative multiple is not.** Both are
reported because the spec's §3 diagnostic is stated in relative terms and the
relative version is the one that flatters the family least honestly.

Honest reading at the spec's own floor: a **+1.4 pp lift on a ~3.5% base rate — a
~1.4× relative improvement — is not, on its face, an absurd ask** for a genuine
technical setup. That is the strongest thing that can be said for this family, and
it is said here deliberately, because the case against it does not need help.

But that is at 10 bps/side. §6 shows the family cannot be executed at 10 bps/side.

---

## 6. Capacity — the decisive test, and it is not close

§8 of the spec: *"Capacity failure at ₹100 Cr in the deployable band kills
independently of alpha… C3 capacity is not deferrable to 'later' for this family."*

The spec supplies every number needed to run this test **now**, with no data contact:

- AUM target: **₹100 Cr** (CLAUDE.md, program objective)
- Position cap: **N = 20**, equal weight (§5)
- ⇒ position size = **₹5.00 Cr**
- Mandatory liquidity floor: **₹2 Cr/day** rolling 60-session median traded value (§4)

**A ₹5 Cr position in a name whose median daily traded value is ₹2 Cr is 250% of a
full day's entire market volume.** At a conventional 10%-of-ADV participation cap,
entry alone takes **25 sessions**. The holding period is **5 sessions**. The trade
cannot be entered before it is due to be exited.

This is not a slippage estimate. It is an arithmetic impossibility, and it holds at
the *floor* of the spec's own admissible universe.

### 6.1 Impact across the habitat

Square-root impact (ASSUMPTION A6): `impact ≈ Y · σ_daily · √(Q/ADV)`, Almgren-style,
`Y ∈ [0.5, 1.0]`, `σ_daily` = 2.25% (ASSUMPTION A2).

**₹100 Cr AUM, N = 20 ⇒ ₹5.00 Cr position:**

| Name's ADV | Q / ADV | impact @ Y=0.5 | impact @ Y=1.0 |
|---|---|---|---|
| ₹2 Cr (spec floor) | **250.0%** | 177.9 bps | 355.8 bps |
| ₹10 Cr | 50.0% | 79.5 bps | 159.1 bps |
| ₹25 Cr (typical rank ~400) | 20.0% | 50.3 bps | 100.6 bps |
| ₹100 Cr (rank ~150–250) | 5.0% | 25.2 bps | 50.3 bps |

At the ₹2 Cr floor the model is being extrapolated far outside its calibrated
range (Q/ADV > 1 is not a trade, it is a corner), so read those cells as "no number
exists", not as "178 bps".

Even in the *most liquid* name the habitat could plausibly contain — ADV ₹100 Cr/day,
which is realistically rank ~150–250 and therefore **at or outside the top edge of
the 201–1000 band** — impact alone is **25–50 bps/side**, i.e. 2.5–5× the spec's own
mandated floor. Add a mid-cap half-spread (ASSUMPTION A7: 5–25 bps/side) and the
realistic slippage parameter for this family at ₹100 Cr is **50–100+ bps/side**,
not 10.

From §3 that means an annual friction drag of **62% to 112%/yr**, against a legacy
gross alpha benchmark of 18.5%.

### 6.2 The capital base at which the spec's own 10 bps/side floor is reachable

Inverting the impact model for `impact = 10 bps` (before spread, i.e. an unreachably
generous target):

| ADV of traded names | AUM supporting 10 bps impact @ Y=0.5 | @ Y=1.0 |
|---|---|---|
| ₹10 Cr/day | ₹1.58 Cr | ₹0.40 Cr |
| ₹25 Cr/day | ₹3.95 Cr | ₹0.99 Cr |
| ₹50 Cr/day | ₹7.90 Cr | ₹1.98 Cr |
| ₹100 Cr/day | ₹15.80 Cr | ₹3.95 Cr |

**SPEC-SRA-01 is a ₹1–15 Cr strategy at best, and the program's target is ₹100 Cr.**
It fails §8's capacity clause by roughly **an order of magnitude**, and the failure
is structural: it is imposed jointly by the 5-day horizon (which forbids patient
execution), the N=20 cap (which concentrates the book), and the 201–1000 habitat
(which is where the liquidity is not).

Loosening any one of these breaks the spec: raising N past ~40 dilutes toward an
index while doubling the number of names below the liquidity floor; moving to the
Top-200 band abandons the mid-cap volatility the ≥10%/5-session event depends on;
extending H makes it a different family (§3's H table).

**Additional structural note:** the spec's own §7 says this family "transacts on
volume-expansion days, i.e. exactly when spreads widen and impact is worst". Correct
— and note that a volume-expansion day inflates the *denominator* of Q/ADV on the
entry leg only. **The exit at close t+5 is unconditional**, so it lands on a day with
no volume-expansion filter whatsoever, and quite possibly on a post-spike volume
collapse. The exit leg is the expensive one and the spec's slippage floor does not
contemplate it. This makes 10 bps/side optimistic even at small capital.

---

## 7. ASSUMPTIONS — stated separately, as required

Everything below is a **labelled assumption**, not a derived quantity. None of it was
measured from data in this repo; measuring most of it would require tick or
order-book data the repo does not hold.

| # | Assumption | Value used | Sensitivity shown? | Direction if wrong |
|---|---|---|---|---|
| **A1** | 5-session return distribution is ~normal with zero excess mean | σ₅ ∈ {5.5%, 6.5%, 8.0%} | **Yes** — three full tables, §5.3 | Fat tails raise `base` and lower `E[ret\|event]`; net effect on required *absolute* lift is small (the §5.1 assumption-free hurdle is unaffected) |
| **A2** | Daily volatility of a rank-201–1000 Indian name | 2.25%/day (≈36%/yr) | Implicit via σ₅ range | Higher σ ⇒ higher impact ⇒ worse |
| **A3** | Index drift for the benchmark-relative variant | 12%/yr ⇒ +23.8 bps/5 sessions | Stated, not swept | Only affects §5.1's IR variant, not §8.1 |
| **A4** | **Deployment fraction (how many of 20 slots are filled on an average day) is NOT PINNED BY THE SPEC.** | **not needed** | n/a | **No impact on the verdict.** §8.1 is stated *per fire*, so deployment cancels: it scales gross return and drag identically. It matters only for portfolio-level %/yr figures in §3, which are stated "per rupee deployed". **This is a genuine gap in the spec (a §5 rule that fires 3 times a week behaves very differently from one that fires 30) but it does not rescue the arithmetic.** |
| **A5** | Buy-leg and sell-leg traded values are equal | equal | Not swept | A winning trade sells more than it buys ⇒ slightly higher STT on the sell. At +5% the round trip rises ~0.5 bps. Negligible. |
| **A6** | Market-impact functional form | square-root, `Y ∈ [0.5, 1.0]` | **Yes** — both `Y` shown throughout §6 | Linear impact would be far worse at Q/ADV > 10%; this is the *charitable* model |
| **A7** | Half-spread for rank-201–1000 NSE names | 5–25 bps/side | Range stated, not swept | **Unverified in this repo.** Verifying needs tick data. Note it makes the spec's 10 bps/side *total* floor arithmetically unreachable in this habitat on the spread alone. |
| **A8** | ADV of names by mcap rank | ₹2 / 10 / 25 / 100 Cr scenarios | **Yes** — full grid, §6.1 | The ₹2 Cr case is not a scenario, it is the spec's own binding floor |
| **A9** | **Capital base is NOT PINNED BY THE SPEC.** | swept ₹5 / ₹25 / ₹100 Cr | **Yes** — §6.1, §6.2 | The program target is ₹100 Cr (CLAUDE.md); §8 makes ₹100 Cr the capacity test explicitly |
| **A10** | Brokerage = ₹0 delivery; DP = ₹15.34/scrip/day | RULING 5 operator ASSUMPTION | Not swept | Combined they are 1.5 bps of a 22.3 bps round trip. If wrong, **the verdict gets worse**, never better |
| **A11** | 252 trading sessions/yr | 252 | Not swept | ±2% on all annualised figures |

**Two parameters SPEC-SRA-01 leaves genuinely unpinned** — deployment fraction (A4)
and capital base (A9). Both are flagged above rather than silently chosen. A4 is
harmless because the spec's headline metric is per-fire; A9 is not harmless, and its
resolution against the ₹100 Cr program target is what kills the family.

---

## 8. Verdict

### 8.1 Is the required hit rate plausible?

**Split answer, and the split is the finding.**

- **At the spec's mandated slippage floor of 10 bps/side: PLAUSIBLE-BUT-UNPROVEN.**
  The family needs `E[fwd5 | setup] ≥ +42 bps`, i.e. a ~54% hit rate at `R = 1` with
  5% average moves, i.e. a ~1.4× lift on a ~3.5% base event rate. That is a large
  ask for 8 OHLCV features — nothing in the published cross-sectional literature on
  short-horizon technical setups delivers a durable 40% relative lift in tail-event
  probability that survives out-of-sample — but it is not arithmetically absurd.
  It would deserve a trial *if it could be executed at 10 bps/side.*

- **At the slippage the family can actually be executed at, at the program's ₹100 Cr
  target: IMPLAUSIBLE, decisively.** §6 shows the realistic parameter is
  **50–100+ bps/side**, giving a required `E[fwd5 | setup]` of **+122 to +222 bps per
  fire** and an annual friction drag of **62–112%/yr**. That requires a **2.2× to
  5.7× multiple of the base rate** and a **3.3× to 6.1× multiple of the entire legacy
  system's gross alpha**. No Indian mid-cap technical rule does this. The claim is
  not merely unproven; it is outside the range of anything documented.

**Verdict: IMPLAUSIBLE.**

### 8.2 The two independent kills

**KILL 1 — §8 capacity clause, and it does not require any alpha estimate.**
At ₹100 Cr with N=20, a position is ₹5 Cr. The spec's own **mandatory** liquidity
floor admits names at ₹2 Cr/day median traded value. **A ₹5 Cr order is 250% of a
full day's volume in a floor-compliant name, and entry at any sane participation rate
takes 25 sessions against a 5-session holding period.** The spec says capacity failure
at ₹100 Cr "kills independently of alpha" and "is not deferrable". By its own clause,
the family is dead — and this was computable on the day the spec was drafted.

**KILL 2 — §8.1 net expectancy, via §6's slippage.**
Even setting capacity aside and asking only what the rule must predict: at the
capacity-implied 50–100 bps/side, the hurdle is +122 to +222 bps of mean 5-session
return per fire, i.e. 62–112%/yr gross, i.e. 3.3–6.1× the legacy system's gross
alpha — produced with strictly less machinery than the legacy system had. §8.1 is not
reachable.

**Not a kill, worth recording:** §8.3 (turnover > 6,000%/yr) does **not** fire — the
primary config is 5,040%/yr. §8.4 (support < 200) is not assessable without data. The
family dies on 8.1 and on capacity, not on the turnover budget.

### 8.3 Recommendation

> **KILL SPEC-SRA-01 NOW, AT ZERO COST. Do not advance to hash-freeze.**

Concretely:

1. **Do not extend `src/expr.py`.** §6 of the spec makes `rolling_mean`,
   `rolling_std`, `rolling_sum` and boolean comparison a **pre-freeze blocker**, and
   §6 further requires the full 52WH regression suite to pass unchanged and every new
   primitive to carry a documented, tested NaN policy (TRAP 1). That is real
   engineering on a **frozen-spec-shared module**, spent on a family that cannot pay
   its friction. **This is the largest avoidable cost on the table and killing now
   avoids all of it.**
2. **Do not build `src/signal_sra.py` or `scripts/run_trial_sra.py`.** Both are
   marked NOT BUILT in §9.
3. **Do not freeze.** RULING 6 says freezing consumes no shadow slot, so freezing is
   cheap in *slots* — but a frozen spec **cannot be edited**, and freezing a spec
   whose §8 is already known to be unreachable puts a permanently-uneditable dead
   family in `governance/specs/`. There is no upside.
4. **Record this as a DECISIONS.md ruling** with an explicit "outcome-blind, no trial
   spent" tag, in the same shape as the 2026-07-20 Legacy Variant A/B scopes. A
   family killed on arithmetic before contact is a governance asset at PMS
   due diligence — it demonstrates the cost gate operating **before** the expensive
   part, which is precisely what the legacy kill did not get to do.
5. **Do not run S0.** §10's S0 is described as free (outcome-blind coverage audit),
   and it is — but it is a panel rebuild plus a feature-coverage audit for a family
   that will not proceed. Free of *trials* is not free of *days*, and the program's
   #1 priority is the daily overlay log.

### 8.4 What survives the kill, and should be carried forward

The analysis is not wasted. Three things transfer:

1. **The hurdle table in §3 is family-agnostic.** Any future Tier 2 candidate can be
   pre-screened in five minutes: `annual drag = (252/H) × (22.3 bps + 2s)`. Applied
   *before* a spec is written, this is the cheapest gate in the program. Consider
   promoting it to a `src/` helper (`friction_hurdle(H, slippage_bps)`), so the check
   FAILS LOUDLY rather than living in a document (TRAP 7).
2. **The capacity pre-screen is equally cheap and equally decisive:**
   `position = AUM/N`, `position / ADV_floor ≤ ~10%` or the family is not deployable
   at that AUM. SPEC-SRA-01 fails this at 250%. **Every future spec should carry this
   line in its §1, computed at draft time.** Note this same screen should be run
   against SPEC-52WH-01, SPEC-QFM-01 and SPEC-PEAD-01 — 52WH is quarterly-rebalanced
   and will pass comfortably on the H axis, but its 201–1000 habitat is the same one,
   and the capacity arithmetic has not been recorded for it either.
3. **The bottleneck lesson is now quantified, not just asserted.** CLAUDE.md says
   "gross alpha was never the constraint; friction was". The precise statement is:
   **at the RULING 5 stack, every session of holding period is worth ~22.3 bps/yr of
   drag per rupee deployed, and STT is 84% of it and cannot be negotiated.** Any
   family with H < ~15 sessions is asking to out-earn the legacy system. That belongs
   in the spec template, not in an analysis file.

### 8.5 The one thing that would change this verdict

If the operator's intent for this family is **not** the ₹100 Cr fund but the
**existing low-capital production book** (₹1–5 Cr, where §6.2 shows 10 bps/side is
approachable), then KILL 1 does not apply and the family reduces to KILL 2 at the
optimistic slippage — where it is a stretch but not impossible.

That would be a different family with a different purpose, and it would need to be
said explicitly and written into the spec, because:

- SPEC-SRA-01 §8 currently makes ₹100 Cr capacity a **binding, non-deferrable kill
  clause**. A small-capital variant needs a new spec (v2), not an edit.
- A ₹1–5 Cr strategy does not advance the program's stated objective, and it would be
  competing for build time against the daily overlay log, which CLAUDE.md identifies
  as the most time-sensitive measurement in the program with a fixed 2026-09-27 read
  date that does not move.
- SPEC-SRA-01 is already **fourth in the queue** behind QFM, PEAD (both shadow slots
  held), AG-01 and 52WH — so even a rescued version is not reachable on any near
  horizon (§10).

**Absent that explicit operator redefinition, the recommendation stands: dead on
arrival, kill now.**

---

## 9. Reproducibility

Every figure above derives from:
- `src/costs_in.py` (constants, unmodified)
- `governance/DECISIONS.md` RULING 5 (cost stack), RULING 7 (inference doctrine)
- `governance/specs/SPEC-SRA-01.md` §§1–10 (design parameters)
- `CLAUDE.md` (legacy anchor: 18.5%/yr gross, t≈2.95, 1.6 round-trips/day)
- the ASSUMPTIONS table in §7

The worked round trip was recomputed against `costs_in.round_trip()` and reconciles
exactly with the ₹237.8212 / 0.23782% figure independently recorded in `DECISIONS.md`
(2026-07-20, Variant A). No data file was opened. No `data_gate` call was made.

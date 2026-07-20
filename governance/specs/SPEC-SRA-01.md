# SPEC-SRA-01 — Short-Horizon Rally Anticipation (DRAFT)

> **STATUS: DRAFT — NOT BINDING, NOT FROZEN.**
> No `sha256` is recorded and no register row exists for this family. Under the
> convention in `CLAUDE.md`, this file may be edited freely until those two things
> land in the same commit. **No outcome contact of any kind is authorized while
> this banner is present** — not a scatter plot, not a "quick look" at hit rates.
> Drafted 2026-07-20 in response to an operator question about predicting
> short-horizon rallies from news + technicals.

**Scope of data contact when frozen:** dev data **< 2024-07-17 only**. The
operator's original framing ("last 3 months", i.e. 2026-04-20 → 2026-07-20) was
declined on 2026-07-20: that window is ~2 years inside the sealed holdout and
touching it would burn this family's single final test under `SEAL.md` §2 before
the family had a spec. Redirected to the dev panel by operator instruction the
same day.

---

## 0. Standing warning — read before advocating for this family

This spec describes a **~5 trading-session holding period**. The program's
central finding is that the legacy daily mid-cap momentum system produced real
gross alpha (~18.5%/yr, t≈2.95) that was **entirely consumed by friction** at 1.6
round-trips/day. A 5-day family is in the same friction regime and starts with a
strong prior against it.

The spec is therefore written so that **the cost test comes first and cannot be
deferred** (§8), and so the family dies quietly rather than expensively. Do not
report a gross result from this family in any forum, at any stage, for any
reason. If the net test cannot be run, the answer is "unknown", not "promising".

## 1. Hypothesis (what is claimed, and what is explicitly not)

**H1 (the family):** There exists a closed, mechanically-computable, point-in-time
feature combination whose presence at the close of session *t* raises the
probability of a ≥10% forward move over sessions *t+1 … t+5* **materially above
the unconditional base rate**, by a margin large enough to survive the RULING 5
friction stack at the turnover the rule implies.

**Explicitly NOT the hypothesis:**

- Not "stocks that rallied had X in common." That is the operator's original
  framing and it is **unfalsifiable by construction** — conditioning the sample on
  the outcome guarantees a pattern is found and cannot produce a base rate. See §3.
- Not that any such rule is tradeable. §8's kill line is net-of-cost; a rule with
  real predictive lift and unpayable turnover is **dead**, not "promising".
- Not a news/sentiment claim. News is out of scope at Stage 1 (§6).

**Pre-stated null (the honest default):** the base rate of a ≥10% 5-session move
in the 201–1000 habitat is already non-trivial (mid-cap vol is high); most
technical "setups" will move it a few percentage points at best, which will not
pay 5-day turnover. **The expected outcome of this family is death at §8.** That
is stated here, before contact, so that a marginal result is read as the null
confirming rather than as a discovery.

## 2. Event definition (the label — fixed here, never re-cut)

For symbol *s* and session *t* in the panel:

```
fwd5(s,t)  = close(s, t+5) / close(s, t) - 1
rally(s,t) = 1 if fwd5(s,t) >= 0.10 else 0
```

- **Adjusted prices** (`data/workspace/price_panel_52wh.parquet` basis) for both
  legs — a split inside the window would otherwise manufacture a fake ±X% event.
- Horizon is **exactly 5 sessions**, close-to-close. The operator's "4–5 sessions"
  is collapsed to 5 deliberately: leaving both open is a free parameter, and
  choosing between them after seeing results is the contamination in TRAP 3.
  A 4-session horizon is a **pre-registered sensitivity** (§7), not a choice.
- Threshold **10%**, per the operator's question. Pre-registered sensitivities:
  8%, 15%. The primary is 10% and the headline is always the 10% result.
- Rows where `close(s, t+5)` is undefined (panel end, insufficient history,
  delisting) are **dropped from both numerator and denominator** and the dropped
  count is reported. Silent truncation here would read as coverage.
- **No path condition.** `rally` is a close-to-close outcome; a name that is +18%
  on day 3 and +2% on day 5 is a non-event. This is intentional — the tradeable
  version of the claim requires an exit rule, and §5 fixes it at the same horizon.

## 3. Design: the base-rate requirement (this is the core of the spec)

**Sampling is over the FULL panel, not over rallies.** Every (symbol, session)
observation in the habitat with defined features and a defined label enters the
sample. The quantities of interest are:

```
base    = P(rally)                        # unconditional, per period and pooled
lift    = P(rally | setup) - P(rally)     # the claim
support = count(setup)                    # how often the rule fires at all
```

A rally-conditioned sample can only ever report `P(setup | rally)` and is
structurally incapable of reporting `base`, `lift`, or the false-positive count.
**Any analysis in this family that filters to rallies first is a protocol breach**,
not a shortcut — including for "just looking at examples".

The false-positive arm is the deliverable as much as the hit arm: every trial
write-up must report `count(setup & ~rally)` alongside `count(setup & rally)`.

**Class imbalance is expected.** If `base` is ~3%, a rule with 60% "accuracy" is
worse than useless. Accuracy, F1, and AUC are **banned as headline metrics** in
this family; the headline is net expectancy per fire (§7), and `lift` is the
diagnostic.

## 4. Universe

- **Primary habitat: PIT mcap ranks 201–1000** (`pit_universe.universe_as_of`,
  band `"201-1000"`), announce-gated — same store, same gating, same earliest
  announce-safe date (**2018-01-25**) as SPEC-52WH-01.
- Sensitivity bands: `"NIFTY500"`; Top-200 (`"1-200"`).
- **Liquidity floor is mandatory, not a sensitivity.** A ≥10%/5-session move is
  trivially common in illiquid microcaps and untradeable there. Pre-committed
  floor: rolling 60-session median traded value ≥ ₹2 Cr/day, computed
  point-in-time. Names below the floor are excluded from the sample entirely
  (both arms) and the excluded count is reported.
- **Survivorship hole, disclosed:** 102/1,412 (7.2%) of fetch symbols remain
  yfinance-unservable after the 2026-07-19 rename recovery, skewed toward
  delistings. Direction of bias for THIS family is **adverse and must be argued
  as such**: delisted names disproportionately contain violent terminal moves in
  both directions, so their absence distorts the tail the family is trying to
  predict. Unlike 52WH — where the hole plausibly understates the benefit — here
  the sign is not obviously favourable. Do not borrow 52WH's argument.

## 5. The tradeable rule (fixed before contact — no discretionary exits)

A firing setup at close *t* implies:

- Entry at the **open of t+1** (not the close of *t* — the signal uses *t*'s close
  and cannot be transacted at it).
- **Fixed exit at the close of t+5.** No stop, no target, no trailing logic.
  Discretionary or optimized exits are a second fitted surface and are out of
  scope for this family at every stage.
- Equal-weight across concurrently-firing names, cap **N=20** positions; if more
  than N fire, rank by the primary continuous feature and take the top N
  (deterministic tie-break by symbol). The overflow count is reported.
- Position sizing is flat. No conviction weighting, ever, in this family.

**Implied turnover, computed before any result is read:** a full 5-session
round-trip on the whole book is ~50 round-trips/yr per slot ⇒ order
**~5,000%/yr one-way** at full deployment. §8's budget is set against this number
with eyes open.

## 6. Feature set — CLOSED list of 8 (Stage 1, technicals only)

Closed on the SPEC-52WH-01 pattern. **No additions without a spec amendment (a new
version + new hash) made BEFORE the relevant trial.** Every feature is an
expression string evaluated by `src/expr.py` and nothing else. All are computable
from OHLCV at or before close *t*.

| # | Feature | Expression (closed grammar) |
|---|---|---|
| 1 | Range compression / coil | `rolling_std(close/ref(close,1)-1, 20) / rolling_std(close/ref(close,1)-1, 100)` |
| 2 | Volume expansion | `volume / rolling_mean(volume, 50)` |
| 3 | Proximity to N-session high | `close / rolling_max(high, 60)` |
| 4 | Distance above trend | `close / rolling_mean(close, 50) - 1` |
| 5 | Prior-move exhaustion | `close / ref(close, 20) - 1` |
| 6 | Cross-sectional relative strength | `cs_rank(close / ref(close, 60))` |
| 7 | 52-week-high nearness | `close / rolling_max(high, 252)` |
| 8 | Down-day absorption | `rolling_sum((close>ref(close,1)) * volume, 10) / rolling_sum(volume, 10)` |

**Grammar dependency (pre-freeze blocker).** The current `src/expr.py` implements
only `ref`, `rolling_max`, `rolling_min`, `cs_rank` and arithmetic. Features 1, 2,
4 and 8 require `rolling_mean`, `rolling_std`, `rolling_sum`, and boolean
comparison. These must be added and unit-tested **before this spec is frozen**.
Constraints on that work:

- `expr.py` is shared with the FROZEN SPEC-52WH-01. Adding primitives does not
  alter that spec's recorded hash, but the **full 52WH regression suite must pass
  unchanged** before the addition is committed, and the addition must be
  purely additive (no change to existing primitives' semantics).
- Every new primitive inherits the `min_periods` discipline. **TRAP 1 is the
  governing lesson**: `_rolling_max` uses `min_periods=n`, so one NaN blocks the
  whole trailing window and silently starved three rebalances in C1-52WH-0001.
  Each new primitive needs an explicit, documented, tested NaN policy.

**Feature 7 overlaps SPEC-52WH-01 §2 exactly** (same expression). This is
deliberate — it lets SRA measure whether 52wk nearness carries short-horizon
information — but it means an SRA result on feature 7 is **not independent
evidence** for the 52WH family and may never be cited as such. Cross-family
citation of a shared feature is double-counting.

## 7. Combination rule and scoring

**The multiple-comparisons problem is this family's defining risk.** Eight
features with thresholds generate a very large candidate rule space, and reporting
the best one is guaranteed to produce a beautiful, false result.

Pre-committed handling:

- **The full candidate grid is enumerated and fixed IN THE REGISTER ROW before
  the run** — every feature, every threshold, every combination depth considered.
  The grid is an input, not a search log written afterwards.
- Combination depth is capped at **3 features** (AND-combination of
  threshold conditions). Deeper combinations are not explored, at any stage.
- Thresholds are drawn from a fixed cross-sectional percentile ladder
  {10, 20, 30, 70, 80, 90} — not tuned continuously.
- **Hansen SPA is run across the ENTIRE grid**, not on the selected best rule.
  This is precisely the tool for the job: SPA's null is "no rule in the searched
  universe beats the benchmark", so it charges the full search rather than
  pretending one rule was picked a priori. A best-rule-only p-value from this
  family is meaningless and must never be reported.
- SPA uses the Politis–Romano stationary bootstrap already in `src/metrics.py`.
  **Overlapping 5-day windows induce serial dependence** — this is why the
  stationary bootstrap is mandatory here and an i.i.d. bootstrap is prohibited.
- Deflated Sharpe reports, does not gate (RULING 7). Charged against the
  register's cumulative trial count. `trial_sr_std = 0.5` with the RULING 7
  caveat, **fixed here before contact** (TRAP 3).

**Headline metric: net expectancy per fire, in basis points, after the RULING 5
cost stack** at the §5 turnover, plus explicit slippage ≥ 0.10%/side (higher than
52WH's 0.05% floor — this family transacts on volume-expansion days, i.e. exactly
when spreads widen and impact is worst). Secondary: net IR of the §5 rule book vs
NIFTY500 TRI, `lift` over base, support count, false-positive count.

Walk-forward over dev data, spanning the 2018–2020 crash and the 2022 drawdown.
**Sensitivities** (each its own register row, never merged into the headline):
4-session horizon; 8% and 15% thresholds; the three universe bands.

## 8. Kill line (pre-committed, no renegotiation)

The family is **dead** if any of the following holds:

1. **Net expectancy per fire ≤ 0** after costs and slippage at the §5 rule. (Gross
   expectancy is not a defence and is not reportable.)
2. **SPA p > 0.10** across the full §7 grid, net of costs.
3. **Turnover budget: > 6,000%/yr one-way** at the primary configuration.
   Deliberately set just above §5's structural ~5,000% so the constraint binds on
   over-firing variants rather than on the design itself. A variant that busts it
   is dead regardless of gross.
4. **Support < 200 firing events** across the walk-forward at the primary config —
   too few to distinguish from luck, and small-n must be declared, not smoothed.

Capacity failure at ₹100 Cr in the deployable band kills independently of alpha:
this rule buys names on volume-expansion days at 5-day horizon, which is the worst
possible footprint profile in the program. **C3 capacity is not deferrable to
"later" for this family** — if §8.1–8.4 clear, capacity is the very next test.

## 9. Machinery bindings

| Component | Module | Status |
|---|---|---|
| Expression evaluator | `src/expr.py` | **EXTENSION REQUIRED pre-freeze** (§6) |
| PIT universe | `src/pit_universe.py` | exists, reused unchanged |
| Price panel | `scripts/build_price_panel.py` | exists; rebuild with quorum filter |
| Costs | `src/costs_in.py` | exists, reused unchanged |
| Inference | `src/metrics.py` | exists; SPA over a grid needs a grid-input path |
| Labels / features | `src/signal_sra.py` | **NOT BUILT** — features + label, outcome-blind wall on the feature side |
| Trial runner | `scripts/run_trial_sra.py` | **NOT BUILT** — the only place labels join features; must refuse without hash match + register row via `src/spec_guard.py` |

`spec_guard.preflight` is a hard dependency, same as 52WH: live sha256 == recorded,
and the trial row must pre-exist.

## 10. Trial plan after freeze

- **S0 (outcome-blind, free):** panel rebuild + **coverage-by-date audit** of every
  §6 feature, and the base-rate denominator count. Per TRAP 1, coverage is
  verified before any result is trusted; per TRAP 2, diagnostics are read before
  any verdict line. S0 touches no labels and is not a trial.
- **S1 (first trial):** the §7 grid, primary config, full SPA. One register row.
- **S2:** sensitivities (§7), one row each.
- **S3:** capacity/footprint at ₹100 Cr (§8).
- **Phase D sealed test:** only if S1–S3 clear §8 **and a shadow slot is open**.
  Cap is 2, currently held by **QFM + PEAD**, with **AG-01 and 52WH already
  queued ahead** — so this family is fourth in line and its sealed test is not
  reachable on any near horizon. Freezing this spec consumes no slot (RULING 6).

## 11. Deferred: news and exchange filings (Stage 2 — BLOCKED)

The operator's question included news and NSE filings. **Out of scope at Stage 1
and cannot be scoped in** until the **exchange filing-timestamp corpus** closes —
one of the four open unknowns, shared with SPEC-PEAD-01 and SPEC-52WH-01 §6.5.

Reason, stated plainly: without a point-in-time record of when a filing became
public, a news backtest silently uses information that was not knowable at the
close it is attributed to. That single defect is the most common source of
spurious alpha in event-driven research, and it is invisible in the output — the
backtest looks excellent precisely because it is cheating.

When the corpus closes, news enters as a **conditioner on an already-surviving
technical rule** (the SPEC-52WH-01 §6 pattern), never as a free-form text search,
and the conditioning list is closed at that point. If the technical stage dies at
§8, the news stage does not run — a conditioner on a dead rule is not a strategy.

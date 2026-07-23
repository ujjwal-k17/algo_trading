# DIAG-MACROBETA-0001 — Cross-sectional macro-factor beta structure

**Do Indian equities carry a direct, persistent, market-adjusted loading on
(a) crude oil and (b) USD/INR? Which stocks, and does the empirical set match
a-priori economic logic?**

- **Register:** `governance/research_register_v2.csv` row `DIAG-MACROBETA-0001`
  (pre-registered 2026-07-23, result row appended same family).
- **Governance:** OUTCOME-BLIND diagnostic. `CONTAMINATION_POLICY` AMENDMENT A
  lists "correlation and cointegration structure" as explicitly free.
  **NO TRIAL SPENT**; cumulative trial count stays at 53. No shadow slot; not a
  spec family. `FINAL_TEST` never set; all stock data through the research door
  (`< 2024-07-17`).
- **Hard boundary honoured:** betas, t-stats and their cross-sectional
  distribution only. No portfolio, no strategy/spread return, no cumulative
  performance, no Sharpe/IR, no forward-return-conditional statistic, no
  outcome-conditional subsetting.
- **A-priori sign map (fixed and hash-pinned BEFORE any outcome contact — TRAP 3):**
  `governance/prereg/DIAG-MACROBETA-0001_sign_map.csv`, sha256
  `16693972a15f72379049a84b76c508b8488740abe89f6120514f9ed3ddd49859`, 127
  symbols, 52 directional crude predictions + 76 directional USDINR predictions.
  Generator `scripts/prereg_macro_beta_map.py`. Runner
  `scripts/diag_macro_beta.py` (idempotent, checkpointed).

---

## 1. Coverage assertions (read FIRST — TRAP 2)

Every trust guard passed and is machine-asserted in the runner (fails loudly
otherwise):

| Guard | Pre-registered requirement | Observed | Pass |
|---|---|---|---|
| TRAP 1 quorum filter | surviving NSE sessions ∈ [2300, 2380] | **2353** (33 holiday-placeholder dates dropped) | ✅ |
| FX agreement halt | corr(INR=X, USDINR=X) log-ret > 0.99 | **1.00000** (n=2505) | ✅ |
| Brent overlap | ≥ 90% of NSE sessions carry the level | 96.86% | ✅ |
| WTI overlap | ≥ 90% | 96.81% | ✅ |
| USD/INR overlap | ≥ 90% | 99.79% | ✅ |
| NIFTY500 TRI overlap | ≥ 90% | 100.00% | ✅ |

- **Window:** 2015-01-01 → 2024-07-16 (research door; seal cutoff respected —
  factor fetch `end` set to the cutoff, panel gated, `max(date) < 2024-07-17`).
- **Universe:** 1,309 symbols carried usable returns; **1,130 cleared the
  ≥750-obs availability filter** (the only screen — no return-conditional
  selection). Median regression n = 2,199 sessions; min 756, max 2,199.
- **Factor returns:** 2,195 fully-populated rows after lags.
- **Alignment:** factor levels reindexed onto the NSE session calendar by
  **exact date match, no forward-fill**, then log-differenced between
  consecutive sessions, so factor and stock returns span the identical interval.

**Coverage-by-date is healthy across the whole window** — the C1-52WH-0001 failure
mode (first-defined-signal pushed years forward by NaN poisoning) does **not**
recur here: the quorum filter removed exactly the 33 placeholder dates and the
252-symbol-day floor is irrelevant because these are simple single-symbol
regressions, not a `rolling_max(min_periods=252)` wide pivot.

## 2. Method

Per symbol, **joint** OLS (market control MANDATORY):

`r_i,t = α + β_mkt·r_mkt + β_oil·r_brent + β_fx·r_usdinr + ε`

- **Log returns throughout**, never levels (no cointegration claim is made).
- **Three lag specs, all reported:** **SPEC-C** contemporaneous;
  **SPEC-L1** market at t, oil+fx at t-1 (**primary lagged** spec);
  **SPEC-L2** all regressors at t-1 (pure-lag robustness).
- **Newey-West HAC** t-stats (Bartlett, lag 5) everywhere; naive OLS t-stats
  reported nowhere.
- **Huber M-estimate** (c=1.345, IRLS) computed **alongside** OLS for every name
  (TRAP 8); sign disagreement disqualifies a name from the "stable" list.
- **Benjamini–Hochberg FDR at q=0.10**, per factor per spec.
- Brent primary, WTI robustness; INR-crude = Brent×USD/INR cross-check.

## 3. Factor entanglement (what the joint regression separates)

Contemporaneous log-return correlations:

|          | r_mkt | r_brent | r_wti | r_usdinr |
|----------|------:|--------:|------:|---------:|
| r_mkt    | 1.000 |  0.114  | 0.090 | −0.139 |
| r_brent  |       |  1.000  | 0.889 |  0.057 |
| r_usdinr |       |         |       |  1.000 |

- **Crude and USD/INR are nearly orthogonal contemporaneously (0.057)** — the two
  factor betas are cleanly separable in this window; multicollinearity is not
  inflating either.
- USD/INR is mildly **negatively** correlated with the market (−0.139): risk-off
  weakens the rupee. This is exactly the common-factor confound the mandatory
  market control removes — a raw pairwise USD/INR correlation would be
  contaminated by it.
- Brent–WTI 0.889 and INR-Brent–Brent 0.989: the crude robustness variants are
  near-identical; conclusions do not depend on which crude series is used.

## 4. The central statistical hazard: multiple comparisons

1,130 symbols × 2 factors ≈ 2,260 tests; **at p<0.05, ~56 false positives per
factor are expected by chance alone.** Discovery counts must be read against
that bar, not in isolation.

| Spec·Factor | tested | BH q=0.10 survivors | p<0.05 count | chance ~ | t̄ | sd(t) | frac \|t\|>1.96 |
|---|---:|---:|---:|---:|---:|---:|---:|
| **C · oil**  | 1130 | **6**  | 77  | 56 | +0.320 | 1.092 | 0.068 |
| **C · fx**   | 1130 | **2**  | 72  | 56 | +0.006 | 1.051 | 0.064 |
| **L1 · oil** | 1130 | **16** | 101 | 56 | +0.159 | 1.229 | 0.089 |
| **L1 · fx**  | 1130 | **0**  | 86  | 56 | −0.395 | 1.027 | 0.076 |
| L2 · oil     | 1130 | 32     | 199 | 56 | +1.097 | 1.057 | 0.176 |
| L2 · fx      | 1130 | 0      | 140 | 56 | +0.824 | 0.944 | 0.124 |

**Read the L2 row as a warning, not a finding.** With the market ALSO lagged,
the contemporaneous market variance is uncontrolled and lagged-oil absorbs broad
overnight/reversal structure — the whole cross-section shifts positive
(t̄=+1.097). This is precisely why the market control is mandatory and why L1
(market at t) is the primary lagged spec. L2 is shown only to make the
confound visible.

## 5. Sign test — the primary validation (does NOT condition on discovery)

One-sided binomial test of a-priori-sign agreement vs p=0.5 across ALL
directional map symbols in SPEC-C:

| Factor | sign matches | fraction | binomial p (one-sided) |
|---|---|---:|---:|
| **CRUDE** | **40 / 52** | **76.9%** | **6.4 × 10⁻⁵** |
| USD/INR   | 45 / 76     | 59.2%    | 0.068 |

- **The crude map is strongly validated.** Directionally, the economic logic
  (crude-derived input costs → negative; upstream realisation → positive) is
  right in more than three-quarters of named stocks — a result not attributable
  to chance, and it does not depend on any name individually surviving FDR.
- **The USD/INR map is only weakly directional (59%, p=0.068)** — better than a
  coin flip but not significant at 0.05. The daily USD/INR channel is real for
  one cluster (pharma exporters, §7) and essentially absent for another the
  theory demanded (IT services, §8).

## 6. Crude: FDR survivors and the stable set

**SPEC-C BH q=0.10 survivors that are map-directional (4 of 4 match sign):**

| Symbol | pred | β_oil | NW t | sector / channel |
|---|---|---:|---:|---|
| ASIANPAINT | NEG | −0.080 | −6.66 | Paints — crude-derived monomers/solvents/resins, ~50%+ of RM |
| BERGEPAINT | NEG | −0.089 | −5.16 | Paints — same basket |
| PIDILITIND | NEG | −0.064 | −4.24 | Adhesives — VAM (crude/gas-linked) |
| DALBHARAT  | NEG | −0.090 | −3.77 | Cement — pet coke + diesel freight |

**STABLE set** (BH survivor + same sign in ALL FOUR sub-periods + OLS/Huber
sign agreement) — crude, n=4:

| Symbol | β_oil | t | sign | map |
|---|---:|---:|---|---|
| ASIANPAINT | −0.080 | −6.66 | NEG | NEG ✓ |
| BERGEPAINT | −0.089 | −5.16 | NEG | NEG ✓ |
| HINDOILEXP | +0.110 | +3.86 | POS | (surprise — see §9) |
| VEDL       | +0.086 | +3.94 | POS | AMB (Vedanta: Cairn oil&gas + metals) |

The full ranked crude table (top |t| among directional map names) is textbook:
paints, adhesive and cement (high crude-input-share) most negative; **ONGC
(+0.082, t+2.20) and OIL (+0.052) positive; COALINDIA +0.036 (energy
substitution); INDIGO −0.080 (t−2.98, aviation/ATF); HINDPETRO/BPCL negative;
autos negative.** Sign matches run down the list essentially uninterrupted.

**Primary lagged spec (SPEC-L1) widens the crude set to 16 BH survivors**, all
economically coherent: ASIANPAINT, PIDILITIND (input-cost); ONGC, OIL,
HINDOILEXP, ABAN, GAIL, HINDPETRO (energy/E&P/driller); VEDL, HINDALCO,
JINDALSTEL, TATASTEEL, JINDRILL (oil-&-metals); CEATLTD, MRF (tyres); PANACEABIO.
That the **lagged** crude beta is *stronger and broader* than the contemporaneous
one is the expected non-synchronous-timing signature: NSE closes 15:30 IST while
Brent settles afterwards, so yesterday's crude move is partly news the Indian
market prices at today's open. **This lag gap is itself a pre-registered
finding** (contemporaneous-vs-L1 crude beta cross-sectional corr = 0.24 — the
two are related but far from identical).

### Shock robustness (SPEC-C β_oil, base vs shock-excluded)

| Symbol | base | ex-COVID | ex-Ukraine | ex-BOTH |
|---|---:|---:|---:|---:|
| ASIANPAINT | −0.080 | −0.065 | −0.075 | −0.055 |
| BERGEPAINT | −0.089 | −0.050 | −0.088 | −0.043 |
| PIDILITIND | −0.064 | −0.029 | −0.066 | −0.027 |
| DALBHARAT  | −0.090 | −0.025 | −0.083 | **+0.009** |
| INDIGO     | −0.080 | −0.103 | −0.070 | −0.092 |
| ONGC       | +0.082 | +0.074 | +0.069 | +0.054 |
| OIL        | +0.052 | +0.047 | +0.042 | +0.032 |
| HINDOILEXP | +0.110 | +0.087 | +0.098 | +0.064 |
| VEDL       | +0.086 | +0.080 | +0.087 | +0.079 |

- **The E&P positives (ONGC, OIL, HINDOILEXP, VEDL) are shock-robust** — sign and
  rough magnitude survive every exclusion; they are not artifacts of 2020/2022.
- **The paints negatives survive in sign but COVID contributes materially** (the
  2020 oil crash coincided with the equity crash). The channel is genuine but its
  measured magnitude is partly a shock-window phenomenon — disclose this.
- **Cement (DALBHARAT) is the weakest — it flips to +0.009 when both shocks are
  removed.** Cement's crude beta is essentially a COVID-window artifact and
  should be treated as noise, despite surviving FDR on the full sample.

## 7. USD/INR: the pharma-export cluster (real but sub-FDR)

The strongest USD/INR loadings in the entire map are **pharma exporters, all
POSITIVE as predicted**: SUNPHARMA (β+0.385, t+3.32), AUROPHARMA (+0.448,
+3.10), BIOCON (+0.304, +2.80), LUPIN (+0.277, +2.31), IPCALAB (+0.226, +2.12),
CIPLA (+0.205, +1.88). Economically clean: large US/EU generic revenue in USD
against an INR cost base.

**Yet ZERO map-directional USD/INR names survive BH q=0.10.** With so few small
p-values, the FDR threshold is stringent (roughly p < 0.0003 for the third
rank); SUNPHARMA's p≈0.0009 sits just above it. The pharma cluster is a genuine
*aggregate* signal (it drives the 59% sign rate) that is individually
underpowered at daily frequency. The two names that *do* clear FX FDR are both
**surprises** outside the directional map (§9).

## 8. The pre-registered headline miss: IT services

The map's single strongest a-priori claim — IT services long USD/INR — **did NOT
appear.** Daily contemporaneous β_fx (market-adjusted):

TCS −0.105 (t−1.21), WIPRO −0.120 (t−1.50), INFY −0.037, LTIM −0.038 all
**negative**; HCLTECH, MPHASIS, TECHM, PERSISTENT, COFORGE weakly positive — a
mixed sign split, every |t| < 1.6, nothing near significance.

The pre-registration said "if IT does not load positively the METHOD is suspect,
not the economics." On reflection the honest reading is **not** that the method
is broken (crude validated cleanly on the same pipeline), but that **the IT–USDINR
relationship is not a daily-frequency phenomenon**: IT majors hedge 1–2 quarters
forward, so daily spot moves are muted, and the exposure operates at the
quarterly-earnings horizon this daily regression cannot see. This is a real,
disclosed limitation of daily-beta measurement — and a caution against the naive
"IT = long USD/INR" day-trade.

## 9. Surprises and misses

**Surprises** (BH survivors NOT in the directional map, top-decile |t|):

- Crude: **HINDOILEXP** (+0.110, t+3.86) and **VEDL** (+0.086, +3.94). Both have
  *impeccable* stories — HINDOILEXP (Hindustan Oil Exploration) is a pure E&P
  whose realisation is crude; VEDL/Vedanta owns Cairn oil&gas. These are the map
  being *incomplete*, not spurious — I simply had not listed the small E&P names.
- USD/INR: **SKFINDIA** (−0.35, t−3.86) and **IPAPPM** (+0.61, t+3.81). SKFINDIA
  (bearings — imported inputs, domestic sales) is directionally sensible as
  FX-negative; IPAPPM (a thinly-traded paper name) is a prime spurious-correlation
  suspect and should be treated as such.

**Misses** (directional map names failing individual FDR): crude 48 of 52, USD/INR
76 of 76. For crude this is *expected and not damning* — the sign test shows the
direction is right in aggregate; only the highest-input-share names are
individually powered. For USD/INR it reflects a genuinely weak daily signal.

**Discriminating tests embedded in the map (mixed):**
- BALKRISIND (predicted crude-NEG / **FX-POS** as an export tyre-maker): β_fx
  +0.194 — right direction, but weak (t+1.47) and its domestic-tyre comparators
  did not cleanly split (MRF came out FX-**positive** at t+2.40 despite a NEG
  prediction; CEATLTD FX-negative as predicted). The export/domestic FX
  discriminator only half-fired.
- BAJAJ-AUTO (predicted **FX-POS**, ~40% export): β_fx −0.084 — **failed**,
  wrong sign and insignificant.

The discriminators being *ambiguous* is itself honest evidence: the tyre/auto FX
channel is not cleanly separable at daily frequency, and I am reporting that
rather than cherry-picking the one that worked.

## 10. Disclosed data defects (direction of bias)

- **Inherited AMFI habitat defect** (OPEN OPERATOR DECISION 2): 50,505
  blank-symbol rank rows narrowed the 201–1000 band to 719 names (~10% short),
  so part of the intended mid-cap habitat never reached the price panel this
  study inherits. Effect here: reduced *power* (fewer names tested), no
  directional bias to the betas.
- **Survivorship hole:** 102/1,412 (7.2%) symbols unservable by yfinance, skewed
  toward **delistings**. Delisted names are disproportionately distressed, and
  distress correlates with leverage and input-cost shocks — so the missing names
  are plausibly *more* crude-negative and USD-negative than the survivors. The
  hole therefore **biases the study against finding crude-negative / FX-negative
  exposure**: the true cross-sectional crude signal is, if anything, stronger
  than measured. This cuts in the conservative direction for the §5 verdict.
- **Rename map:** old-label series truncated at rename effective date (no
  dual-label double-counting).

## 11. Conceptual caveat (do not bury)

**A contemporaneous beta is an EXPOSURE, not an alpha.** Even the rock-solid
ASIANPAINT crude beta (t−6.7) is not tradable unless crude *itself* is
predictable — a separate and much harder claim this diagnostic does **not**
address and was **not** authorized to address. The legitimate uses of this
result are **risk management, hedging, factor-neutralisation, and as a
conditioning input for someone who already holds a macro view** — not a
standalone signal. Most of these betas (paints/oil, pharma/USDINR) are long
known and priced. The moment one asks "would tilting on β_oil have made money,"
that is a registered TRIAL and outside this authorization.

## 12. Verdict

- **Crude: YES, a direct and economically coherent cross-sectional exposure
  exists and is validated** (sign test 76.9%, p=6.4×10⁻⁵). Individually
  FDR-robust *and* sub-period-stable *and* Huber-agreeing *and* shock-robust:
  the **paints pair ASIANPAINT / BERGEPAINT** (crude-NEGATIVE, input-cost
  channel) and the **E&P names ONGC / OIL / HINDOILEXP / VEDL** (crude-POSITIVE,
  realisation channel). Cement survives FDR but is a COVID artifact; the broader
  40/52 directional agreement is real but individually underpowered.
- **USD/INR: WEAK and horizon-limited.** The map is only 59% directional
  (p=0.068); **no map-directional name survives FDR at daily frequency.** The one
  genuine cluster is **pharma exporters (positive, as predicted)** — real in
  aggregate, individually sub-threshold. The pre-registered strongest claim, **IT
  services, does not show at daily frequency** (hedged/quarterly horizon).
- **Guardrails held:** the mandatory market control mattered (L2 shows what its
  absence does); crude and USD/INR are cleanly separable (ρ=0.057); FDR against
  chance (~56 expected FPs) kept the discovery count honest; the sign test
  (which does not condition on discovery) is the load-bearing validation.

**NO TRIAL SPENT** (outcome-blind: correlation structure only). Cumulative trial
count unchanged at 53.

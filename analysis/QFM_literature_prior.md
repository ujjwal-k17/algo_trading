# QFM Literature Prior — outcome-blind evidence pass for SPEC-QFM-01

**Purpose.** Close `governance/specs/SPEC-QFM-01.md` OPEN ITEM 10 ("NO CITED
PRIOR"). This is a **literature pass only**. No repository data was touched: no
price panel, no PIT store, no returns, no backtest, no signal frame, no register.
Under `governance/CONTAMINATION_POLICY.md` AMENDMENT A, reading external research
is free and spends no trial. `SPEC-QFM-01.md` was not edited; it remains a DRAFT.

**Date:** 2026-07-22. **Status:** advisory input to an operator decision.

---

## VERDICT (stated first, argued below)

**(B) WEAK / MIXED — advance only with named caveats.**

The verdict is (B) rather than (C) on the strength of exactly two peer-reviewed
findings: Akbas, Jiang & Koch (2017) establishes that a profitability *trend*
predicts returns and is **not** subsumed by the *level*, and Sehgal & Pandey
(2021) reports the same "increases, not levels" result in India. Those two make
the family's core hypothesis a real hypothesis rather than an assertion.

Everything else in this review is adverse, and the adverse evidence is stronger
than the supportive evidence. **The (C) case is genuinely close** and is set out
in §9. If the operator declines any one of the four pre-conditions in §8, the
correct action is (C): release shadow slot 1.

**The three strongest pieces of evidence FOR and AGAINST are in §8.3.**

---

## 0. How to read this document

Source tiers, marked on every citation:

- **[PR]** peer-reviewed journal article.
- **[WP]** working paper / preprint / unpublished dissertation — not refereed.
- **[VM]** vendor, broker, screener or practitioner marketing — **systematically
  biased toward positive results**; used only to characterise the information
  environment, never as evidence for an effect.

**"unverified"** means I could not open a source stating it. Nothing is guessed.
Where a delegated researcher supplied a number I could not re-open myself, it is
marked **[unverified at source]**. The three numbers this review actually leans on
— Novy-Marx & Velikov Table 3, Green-Hand-Zhang's abstract, and Akbas-Jiang-Koch's
abstract — I fetched and read myself; the first was read off the NBER PDF digit by
digit.

**The distinction this document polices throughout.** SPEC-QFM-01 §1 claims
**CHANGES** (first and second differences), explicitly not **LEVELS** (quality,
profitability, value). Most literature that looks supportive is level literature.
§1.1 separates them line by line. This separation is not pedantry: it is what
turns a 14%-spread headline into a t-statistic of 0.45.

---

## 1. Core effect — what the global literature actually establishes

### 1.1 The LEVEL / DELTA split, applied

| Construct | Level or Delta | Bearing on §4.3 |
|---|---|---|
| Gross profitability, ROE, RMW, value, B/M | **LEVEL** | Not this family (spec §1 agrees). |
| Piotroski F-score | **MIXED** — **5 of 9** are YoY changes in accounting ratios (ΔROA, ΔDTA, ΔATL, ΔGM, ΔATO); a 6th (equity issuance) is a change in share count | Closest widely-tested analogue; see §1.5. |
| SUE / earnings surprise | **DELTA**, standardised | Feature 2 is an *unstandardised* cousin (§1.4). |
| Earnings acceleration | **DELTA**, 2nd difference | Feature 3. |
| Profit *trend* (Akbas et al.) | **DELTA** | The family's best prior (§1.2). |
| QMJ "Growth" leg | **DELTA**, but 5-year, per-share, profitability-only | Not the spec's delta (§1.6). |

Verbatim F-score definition, from Novy-Marx & Velikov's appendix
(<https://www.nber.org/system/files/working_papers/w20721/w20721.pdf>, p. 48):

> "Piotroski's F-score = 1(IB>0) + 1(ΔROA>0) + 1(CFO>0) + 1(CFO>IB) +
> 1(ΔDTA<0 | DLTT=0 | DLTT−12=0) + 1(ΔATL>0) + 1(EqIss≤0) + 1(ΔGM>0) + 1(ΔATO>0)"

**ΔGM and ΔATO are literally spec features 4 and 5; ΔDTA is feature 6.** Whatever
happens to the F-score under honest testing happens to half this spec's composite.
That fact drives §5.

### 1.2 The family's strongest prior

Akbas, Jiang & Koch, "The Trend in Firm Profitability and the Cross-Section of
Stock Returns", *The Accounting Review* 92(5), 2017 **[PR]** —
<https://doi.org/10.2308/accr-51708>. Abstract verbatim:

> "This study shows that the recent trajectory of a firm's profits predicts future
> profitability and stock returns. **The predictive information contained in the
> trend of profitability is not subsumed by the level of profitability, earnings
> momentum, or other well-known determinants of stock returns.** The profit trend
> also predicts the earnings surprise one quarter later, and analyst forecast
> errors over the following 12 months, suggesting that sophisticated investors
> **underreact** to the information in the profit trend. On the other hand, we find
> **no evidence of investor overreaction**, and our results cannot be explained by
> well-known risk factors."

This is the paper the spec should cite. It is peer-reviewed, in a top accounting
journal, it is explicitly a **delta** construct, it explicitly clears the two
spanning hurdles the spec fears most (level profitability and earnings momentum),
and its mechanism is **underreaction** — which, unlike overreaction, is compatible
with a hold-and-rebalance book rather than implying reversal.

**Sample period, universe, weighting and gross-vs-net: unverified** (closed
access; no OA copy). SSRN working-paper version: <https://doi.org/10.2139/ssrn.2538867>.
Before this becomes load-bearing in a frozen spec, the full text must be obtained
and its weighting scheme checked — for the reason §5 makes unavoidable.

### 1.3 The primary "fundamental momentum" anchor is NOT about accounting deltas

Novy-Marx, *Fundamentally, Momentum is Fundamental Momentum*, NBER w20984, Feb
2015 **[WP — never peer-reviewed]** — <https://www.nber.org/papers/w20984>.
Abstract verbatim:

> "Momentum in firm fundamentals, i.e., earnings momentum, explains the performance
> of strategies based on price momentum. Earnings surprise measures subsume past
> performance in cross sectional regressions of returns on firm characteristics…
> While past performance does not have independent power predicting the cross
> section of expected returns, it does predict stock comovements."

**Its signals, verbatim from the author's own PDF**
(<https://mysimon.rochester.edu/novy-marx/research/FMFM.pdf>, §2.1)
**[unverified at source — fetched by a delegated researcher]**: SUE = "the most
recent year-over-year change in earnings per share, scaled by the standard
deviation of the earnings innovations over the last eight announcements"; CAR3 =
market-excess return over the three days around the most recent announcement.
Sample Jan 1975 – Dec 2012; CRSP/Compustat; NYSE breakpoints; results
value-weighted and, in the author's own words, ignoring transaction costs.

**There is no margin, turnover, leverage or asset-side variable anywhere in the
construct.** If SPEC-QFM-01 cites Novy-Marx as its prior, that is a category
error: the paper validates *standardised earnings surprise* and *announcement
returns*, not a six-feature accounting-delta rank composite. The direction of its
spanning result is favourable (see §6), but the object it validates is not the
spec's object.

### 1.4 The standardisation gap in feature 2 — a design defect, not a kill

Every validated earnings-change construct in this literature is **standardised**:
Novy-Marx divides by the std of the last eight earnings innovations (§1.3); the
India PEAD study divides by price (§2.3); Sehgal & Jain use SUE and SUR (§2.2).

Spec feature 2 is `pat / ref(pat, 4) - 1` — an **unstandardised** growth ratio.
The §4.3 denominator guard discards non-positive year-ago PAT but does nothing
about *small* positive year-ago PAT, which is common in the 201–1000 band. A firm
going ₹1 Cr → ₹3 Cr of PAT outranks one going ₹300 Cr → ₹450 Cr on a small
fraction of the information. Cross-sectional ranking bounds the tail; it does not
fix the ordering.

**This is a new open item (§10, item A).** It is cheap to fix before freeze
(divide by the trailing std of the same series — still inside `expr.py`'s closed
grammar if a `rolling_std` primitive is added, which would itself be a grammar
change requiring a decision) and impossible to fix after.

### 1.5 The F-score's own record is worse than its reputation

Piotroski, *Journal of Accounting Research* 38(Suppl), 2000 **[PR]** —
<https://doi.org/10.2307/2672906>. **Full text not obtained** (closed). From the
Chen–Zimmermann open-source replication metadata
(<https://raw.githubusercontent.com/OpenSourceAP/CrossSection/master/SignalDoc.csv>,
row `PS`) **[unverified at source]**: sample 1976–1996, decile long-short, original
t = 5.594, and — critically — the screen **"Include highest quintile of
book-to-market only."**

**Piotroski is a value-conditional, annual, binary-coded signal.** SPEC-QFM-01 is
an unconditional, quarterly, continuous-rank composite. The F-score is the closest
antecedent but it is not the same object, and the spec should not inherit its
reputation. What happens to it under honest testing is §5.

Piotroski & So, *RFS* 25(9), 2012 **[PR]** — <https://doi.org/10.1093/rfs/hhs061>
— uses the F-score **LEVEL** to identify expectation errors. It is a level paper
and is not evidence for this family.

**ΔF-score / "F-score momentum" as a distinct signal: no peer-reviewed paper found
in any country.** OpenAlex title-and-abstract search returned zero. Recorded as
**absent from the literature**, not as disproven.

### 1.6 QMJ is a level construct with one differently-shaped delta leg

Asness, Frazzini & Pedersen, "Quality Minus Junk", *Review of Accounting Studies*,
2019 **[PR, but all three authors are AQR principals — conflict noted]** —
<https://doi.org/10.1007/s11142-018-9470-2>.

Profitability and Safety are **levels**. Growth is
`z(z_ΔGPOA + z_ΔROE + z_ΔROA + z_ΔCFOA + z_ΔGMAR)` where Δ is the **five-year**
change in residual income *per share*, excluding accruals
**[unverified at source]**. Sample Jun 1957 – Dec 2016, 24 countries,
**value-weighted, NYSE breakpoints**.

**QMJ's delta is not the spec's delta:** 5-year vs 1-year, annual vs quarterly,
per-share vs absolute, profitability-only vs six heterogeneous features. It is not
evidence for the spec, and the spec is right (§1) to disclaim a quality
interpretation. One transferable fact, from their own persistence table
**[unverified at source]**: growth and safety are the *least* persistent
components — a delta signal decays faster than a level one (see §4).

### 1.7 Earnings acceleration — the clean prior for feature 3

He & Narayanamoorthy, *Journal of Accounting and Economics* 69(1), 2020 **[PR]** —
<https://doi.org/10.1016/j.jacceco.2019.101238>. Abstract verbatim:

> "We document that earnings acceleration, defined as the **quarter-over-quarter
> change in earnings growth**, has significant explanatory power for future excess
> returns. These excess returns are **robust to a wide range of previously
> documented anomalies and a battery of risk controls**. The future return
> predictability appears to be consistent with investors assuming a **seasonal
> random walk** model for quarterly earnings…"

**Definitional mismatch to police.** Their acceleration is a *quarter-over-quarter*
change in growth. Spec feature 3 is
`(pat/ref(pat,4)-1) - (ref(pat,1)/ref(pat,5)-1)` — a quarter-over-quarter change
in *year-on-year* growth. These are close but not identical; whether they coincide
depends on the growth definition in the paper, which I could not open. **Which
anomalies the robustness covers — and whether SUE and price momentum are among
them — is UNVERIFIED.** Sample, universe, weighting and cost treatment: all
unverified.

Note also the mechanism: the effect exists *because* the market anchors on a
seasonal random walk. That is precisely the expectation model implicit in
`ref(pat, 4)`. The paper says the mispricing is in the **second** derivative of
that benchmark — feature 3 — not the first (features 1, 2).

### 1.8 The remaining features have thin, old, regression-only antecedents

From the Chen–Zimmermann `SignalDoc.csv` **[unverified at source]**:

| Spec feature | Closest tested signal | Sample | Weighting | Evidence type |
|---|---|---|---|---|
| 1 Revenue growth | RevenueSurprise (Jegadeesh & Livnat, *JAE* 2006) | 1987–2003 | EW | event study |
| 2 Earnings growth | EarningSurprise (Foster, Olsen & Shevlin, *AR* 1984) | 1974–1981 | EW | event study |
| 4 Δoperating margin | Piotroski signal ΔGM; Soliman ΔPM | 1976–96 / 1984–2002 | mixed | binary component / regression |
| 5 Δasset turnover | Soliman, *AR* 2008, <https://doi.org/10.2308/accr.2008.83.3.823> | 1984–2002 | EW, price>$5 | **regression only, t = 2.5 with controls, no portfolio sorts** |
| 6 Δleverage | Piotroski ΔDTA; Richardson et al. *JAE* 2005 | 1962–2001 | mixed | univariate regression |

Abarbanell & Bushee (1998), *The Accounting Review* 73(1) **[PR]** —
<https://doi.org/10.2308/tar-274315> — is the historical antecedent for a
multi-signal accounting composite (inventory, receivables, margins, expenses,
capex, tax rates, labour productivity). Reported ~13.2% size-adjusted returns over
12 months, with a meaningful portion accruing **around subsequent earnings
announcements** and abnormal returns **diminishing after the first year**
**[unverified at source — SSRN abstract only]**. Lev & Thiagarajan (1993), *JAR*
31(2) — <https://doi.org/10.2307/2491270> — **contents unverified; do not cite
until opened.**

**Summary of §1:** four of the spec's six features rest on pre-2003,
equal-weighted, regression-coefficient evidence, not on portfolio sorts that
anyone has traded. Two (features 3 and, via Akbas, the profit-trend idea) have
modern peer-reviewed portfolio-level support. **No paper anywhere tests an
equal-weighted six-rank accounting-delta composite.** The composite is a new
object.

---

## 2. India-specific evidence — the decisive section

**Headline: there is exactly ONE peer-reviewed India study whose stated result is
about fundamental CHANGES rather than levels, and I could not open its full text.
Everything else is level-based, gross-only, in the wrong universe, methodologically
defective, or below publishable quality.**

### 2.1 The single best India prior — "increases, not levels"

Sehgal & Pandey, "Firm quality and stock returns: Evidence from India",
*Investment Analysts Journal*, 2021 **[PR]** —
<https://doi.org/10.1080/10293523.2021.1991130>. Abstract verbatim:

> "Using data for 1 848 companies, we find that **quality increases, not quality,
> drive stock returns in India**. Profitability and safety seem to be relevant
> attributes for measuring quality. Our cross-sectional tests show that **the role
> of quality in predicting returns is partially subsumed by momentum in short
> holding periods**. Rational sources are not able to explain quality premiums.
> **We find that quality premiums result from investor overreaction.** At the same
> time, momentum profits are an outcome of investor underreaction…"

This is the closest thing published India research has to SPEC-QFM-01's H1, in the
right country, peer-reviewed, and it endorses the family's central design choice
(deltas over levels).

**Four material caveats:**

1. **Full text not obtained** (Taylor & Francis 403; OpenAlex `oa_status: closed`,
   no repository copy). **Sample period, universe composition, weighting, holding
   period and gross-vs-net are ALL unverified.** 1,848 companies suggests a broad
   all-listed sample rather than a 201–1000 band, but that is inference.
2. **"Partially subsumed by momentum in short holding periods"** — the spec's OPEN
   ITEM 9 killer, stated by the supportive paper itself, in India (§6).
3. **"Quality premiums result from investor overreaction."** Overreaction implies
   subsequent **reversal** and a bounded horizon. This directly contradicts Akbas
   et al. (§1.2), who find underreaction and *no* evidence of overreaction for the
   profit trend in the US. The two best priors for this family disagree about its
   mechanism, and the mechanism determines the right holding period.
4. It is a **quality-increase** composite (profitability + safety). Spec features 1
   (revenue growth) and 5 (asset-turnover change) have **no India prior at all**.

### 2.2 India earnings momentum — real, large-cap, gross-only, ends 2010

Sehgal & Jain, "Profitability of Price, Earnings and Revenue Momentum Strategies:
The Indian Evidence", *AAMJAF* 11(1), 47–84, 2015 **[PR, low-tier]** —
<https://ejournal.usm.my/aamjaf/article/view/aamjaf_vol11-no1-2015_3>
(PDF: <https://ejournal.usm.my/aamjaf/article/download/aamjaf_vol11-no1-2015_3/pdf>).
**Full text read.**

- **Universe: 493 firms of the BSE 500. Sample: Jan 2002 – Jun 2010.** Signals SUE
  and SUR; 6-6 and 12-12 formation/holding.
- "Momentum profits are found to be persistent in the intermediate horizon (**up to
  six months**)"; patterns "become weaker as one elongates the portfolio formation
  and the holding windows, i.e., from 6-6 to 12-12."
- **"On a long-short basis, earnings momentum provides the most profitable trading
  strategy in India"**; "both price and revenue momentum is subsumed by earnings
  momentum."
- **"The informational content of revenue surprises is incrementally very small
  after accounting for earnings and price momentum."**
- Best configuration: triple-sorted long/short **2.28%/month**; "The CAPM and the
  Fama-French model fail to explain these returns."
- **"The post-holding analysis reveals strong overreaction patterns for both
  winners as well as losers."**
- **GROSS ONLY, and the authors say so**, verbatim: *"The economic feasibility of
  these trading strategies may be explicitly tested by incorporating transaction
  costs and tax effects."*
- On who earns the money, verbatim: *"a triple-sorted long-short trading strategy
  would be best on a risk-adjusted basis because **both winners and losers
  contribute to profitability** (winners with positive alphas and losers with
  negative alphas)."*

**Three sharp consequences for SPEC-QFM-01:**

- The best India earnings-momentum result is **long/short**, with profit split
  across both legs. SPEC-QFM-01 §5 specifies a **long-only top-40 book**. The
  long-only implementation harvests part of the documented spread and the paper
  does not say what part.
- **Feature 1 (revenue growth) is specifically contra-indicated in India** by the
  only India study that tested it. The spec gives it a full 1/6 equal weight.
- The horizon is ~6 months with decay, and the attribution is **overreaction**,
  i.e. reversal follows.

### 2.3 India PEAD — exists, but the study has a survivorship defect

Harshita, Singh & Yadav, "Post-Earnings-Announcement Drift Anomaly in India",
*Theoretical Economics Letters* 8(14), 2018 **[PR, very low-tier — 4 citations]**
— <https://doi.org/10.4236/tel.2018.814197>
(PDF: <https://file.scirp.org/pdf/TEL_2018102515432009.pdf>). **Full text read.**

Nifty 500, 2002Q4–2017Q3, SUE = YoY earnings change scaled by price, decile sorts,
Fama-MacBeth. Reports significant 64-day drift "robust to inclusion of other
variables (beta, market capitalization, P/B ratio, illiquidity and idiosyncratic
volatility)".

**Defect, verbatim from the paper: *"The date of sample selection is 31 March
2014."*** A single-date constituent snapshot applied to a 2002–2017 panel is a
survivorship / look-ahead universe — precisely the class of defect
`src/pit_universe.py` exists to prevent. **Directionally suggestive only.**

**Gross only.** Its own literature review records prior findings that "a
significant proportion of drift" was attributable to transaction costs and that
the anomaly was "primarily limited to highly illiquid stocks."

Lead not opened: "Earnings surprise and sophisticated investor preferences in
India", *Journal of Contemporary Accounting & Economics* 5(1), 2009 **[PR]** —
<https://doi.org/10.1016/j.jcae.2008.11.001>. **Abstract not retrievable from any
open source; contents unverified.**

### 2.4 India F-score — one serious study, an unpublished dissertation, on nano-caps

Rastogi, "Fundamental Analysis: Evidence from India", ISB Executive Fellow
Programme dissertation, March 2025 **[WP — unpublished, not peer-reviewed, 0
citations]** —
<https://eprints.exchange.isb.edu/id/eprint/2415/1/Fundamental%20Analysis%20Evidence%20from%20India.pdf>.
**Full text read.**

- **Sample:** Prowess (CMIE), **2013–2022**, 13,258 firm-years, 2,474 firms; March
  fiscal year-ends only; portfolios formed **3 months after fiscal year end**;
  **annual** market-adjusted buy-and-hold.
- **Result:** high F (7–9) mean market-adjusted BHR **17.6%** vs low F (0–2)
  **3.4%**; spread **14.2%**, t = 5.48 (median spread 12.0%, t = 7.47).
  Fama-MacBeth **+3.7% per F-point**, t 4.45–7.47, Newey-West.
- **Habitat-relevant:** "the return predictability … strengthens for smaller firms
  facing greater information asymmetry"; significant positive SMALL × F-SCORE
  interaction; SIZE coefficient −0.032 to −0.042 (***).

**Six reasons the headline is much weaker than it looks:**

1. **The sample is nano-cap, not the spec's habitat.** Table 3 Panel A verbatim:
   `MKT_CAP (INR Billion) … Mean 45.791, p50 1.560, p25 0.347`. **Median firm
   ₹156 Cr; 25th percentile ₹35 Cr.** AMFI rank 1000 sits far above that. Most of
   this sample fails SPEC-QFM-01 §3.3's ₹2 Cr/day liquidity floor and is
   undeployable at ₹100 Cr AUM. **The "stronger in small firms" result is evidence
   that the effect lives BELOW the 201–1000 band, not inside it.**
2. **Equal-weighted, market-adjusted, over 2013–2022** — a decade of extreme Indian
   small/micro-cap outperformance. An EW nano-cap book measured against a broad
   index collects the size premium before any F-score alpha. The regressions
   control for SIZE; **the 14.2% portfolio spread is not risk-adjusted at all.**
3. **Gross only.** "Transaction cost" appears once, in a macroeconomic aside. No
   cost, turnover or implementability analysis exists.
4. **Delisting handling**, verbatim: *"In case of delisting of a firm, the return is
   considered as 0."* Not a delisting return. An undisclosed distortion in both
   legs (it happens to bias *against* the reported spread, but it is not standard).
5. **Annual, not quarterly**, with a 12-month hold. Says nothing about a quarterly
   rebalance.
6. **F-score is a mixed level/delta composite**, value-unconditional here (unlike
   Piotroski's own top-BM-quintile screen), so it is not even a faithful F-score
   replication.

The rest of the Indian F-score "literature" is not usable: Veeraraghavan,
*Business and Economics Research Journal* 13(6) **[PR, very low-tier]** —
<https://berjournal.org/wp-content/uploads/2024/09/BERJ13065x.pdf> — contains **no
return test at all** (a descriptive ratio comparison of 54 firms, concluding
F-score alone is insufficient). The remaining first-page results for "Piotroski
F-score India" are screeners and blogs — finpab.com, investsights.in, yieldiq.in,
Economic Times stock screener **[VM]** — plus at least one paper in a publisher of
doubtful standing (internationalpubls.com). **The Indian F-score information
environment is dominated by marketing, not research.** That is itself a finding:
a positive result here competes against a large retail population running the same
screen off the same free data.

### 2.5 The India-wide picture is one of DECAY

Sharma, Subramaniam & Sehgal, "Are Prominent Equity Market Anomalies in India
Fading Away?", *Global Business Review*, 2019 **[PR]** —
<https://doi.org/10.1177/0972150918811248>. Abstract verbatim:

> "Using data for NSE 500 companies… for a recent period from **July 2005 to June
> 2016**… **The value and momentum anomalies are explained by risk models which is
> contrary to prior evidence. Size and volume anomalies continue to provide
> significant returns but seem to have faded substantially over time**… The findings
> about weakening prominent Indian equity market anomalies shall pose a challenge
> for portfolio managers who may have to look for other sources of extra-normal
> profits. Indian market also seems to be informationally more efficient…"

**Same lead author as §2.1 and §2.2.** His own later, longer sample finds Indian
momentum no longer abnormal after risk adjustment.

**This is the single most important temporal caveat in this document.** The
supportive India earnings-momentum result (§2.2) ends **June 2010**. The decay
result runs to **June 2016**. SPEC-QFM-01's dev window runs to **2024-07-17**.
**The supportive evidence comes from the older third of the spec's own development
window, and the decay evidence covers the middle third.**

Best-constructed Indian cross-sectional study located: Lalwani & Meshram, "The
cross-section of Indian stock returns: evidence using machine learning", *Applied
Economics*, 2021 **[PR]** — <https://doi.org/10.1080/00036846.2021.1982132>.
Abstract verbatim:

> "We test whether 35 stock characteristics can explain the cross-section of stock
> returns in India… a comprehensive, **survivorship bias free** sample of all firms
> listed on the major Indian stock exchanges from **1994 to 2019**. Results from
> Fama-Macbeth regressions show as many as **14 predictors breaching the
> significance threshold of t-stats greater than three**."

**Which 14 predictors survive, and whether any accounting delta is among them,
could not be determined — closed access, no repository copy (OpenAlex
`oa_status: closed`). UNVERIFIED, and this is the highest-value single unknown in
this review.** It would answer "does a fundamental delta clear t > 3 in India" at
a quality level nothing else here reaches. **Recommended action in §10, item D.**

### 2.6 India quality: the long leg does not work; the money is in the short leg

Kaur, Seth & Singh, "Value and quality investing strategy in Indian stock market",
*Managerial Finance*, 2024 **[PR]** — <https://doi.org/10.1108/mf-02-2023-0112>.
Abstract verbatim:

> "…the cross-section of Bombay Stock Exchange (BSE) listed stocks from **2003 to
> 2020**. **The results indicate that the quality-only strategy failed to produce
> substantial risk-adjusted returns in the Indian stock market. The returns to
> long/short hedging strategy quality-minus-junk (QMJ) are significantly positive
> with the majority of the returns attributable to the short leg of the stock
> portfolio.** The findings further discovered that the explanatory effect of
> quality on prices is limited."

Compare Lalwani, "Quality investing in the Indian stock market", *Managerial
Finance*, 2018 **[PR]** — <https://doi.org/10.1108/mf-07-2017-0248> — on BSE-500,
where **two of four** quality indicators (Grantham Quality, Gross Profitability)
beat the market after controlling for size, value and momentum. A partial,
level-based positive.

**The pattern that matters, and it should be uncomfortable.** The most recent
India quality result says the money is in the **short leg**. §2.2 says India
earnings momentum needs **both legs**. This is structurally identical to the
programme's own SPEC-52WH-01 finding (Raju 2023: the long leg does not beat the
index; the edge is a negative screen). **Three independent findings, two of them
Indian, all say the exploitable information in fundamentals is concentrated in
avoiding bad names rather than holding good ones — and SPEC-QFM-01 §5 specifies a
long-only top-40 book.** See §10, item B.

### 2.7 Verified ABSENCES in the India literature

Systematic OpenAlex `title_and_abstract.search` queries (<https://api.openalex.org/>)
returned **zero** India studies on:

- "fundamental momentum" in India (the phrase returns fluid-mechanics textbooks and
  Novy-Marx; no Indian equity paper exists);
- change-in-F-score / ΔF-score as a signal, **in any country**;
- YoY operating-margin change, asset-turnover change or leverage change as
  standalone cross-sectional predictors in India;
- any India study of a **multi-feature accounting-delta composite**, quarterly or
  otherwise;
- any India study reporting **net-of-cost** returns to an accounting-based
  cross-sectional strategy.

Queries used: "fundamental momentum", "fundamental momentum India", "earnings
momentum India", "post-earnings announcement drift India", "Piotroski India",
"revenue momentum", "quality factor Indian stock market", "cross-section Indian
stock returns characteristics", "momentum India transaction costs", "F-score
change stock returns", "earnings growth portfolio India stock returns", "anomalies
net of transaction costs India", "financial statement analysis returns India small
cap", "profitability factor India asset pricing", "size value momentum India Fama
French".

**This absence is the actual answer to OPEN ITEM 10.** SPEC-QFM-01's specific
construct — a six-feature equal-weighted accounting-delta rank composite,
quarterly, Indian mid/small caps, net of costs — **has no India-specific prior of
any kind.** The nearest neighbours are one peer-reviewed sentence whose full text
I could not open (§2.1), one 2002–2010 large-cap SUE study (§2.2), and one
unpublished nano-cap annual F-score dissertation (§2.4).

---

## 3. Does it survive in mid/small caps? (habitat, ranks 201–1000)

### 3.1 The global evidence says most of the published effect is a weighting artefact

Hou, Xue & Zhang, "Replicating Anomalies", *RFS* 33(5), 2020 **[PR]** —
<https://doi.org/10.1093/rfs/hhy131>, WP <https://www.nber.org/papers/w23394>.
Published abstract verbatim:

> "Most anomalies fail to hold up to currently acceptable standards for empirical
> finance. **With microcaps mitigated via NYSE breakpoints and value-weighted
> returns, 65% of the 452 anomalies in our extensive data library, including 96% of
> the trading frictions category, cannot clear the single test hurdle of the
> absolute t-value of 1.96.** Imposing the higher multiple test hurdle of 2.78 at
> the 5% significance level raises the failure rate to 82%. **Even for replicated
> anomalies, their economic magnitudes are much smaller than originally reported.**"

Category replication rates **[unverified at source]**: investment 73.7%,
profitability 44.3%, value-growth 42%, intangibles 25.2%, trading frictions 3.8%.
Replication is ~58% under equal-weighting with all-stock breakpoints versus ~35%
under NYSE/VW — i.e. **roughly 40% of the published accounting-anomaly evidence
base is a weighting artefact.**

Fama & French (2016), *RFS* 29(1), verbatim **[unverified at source]**: "the
microcap quintile on average contains 57% of NYSE-AMEX-NASDAQ stocks but only 2.9%
of aggregate market cap. The next Size quintile on average includes **14.7% of
stocks but only 3.7% of aggregate market cap**." **That second quintile is the US
analogue of ranks 201–1000.** It is 3.7% of market cap. Anything documented there
is documented in a thin slice of the market.

### 3.2 Fama & French (2008) splits the spec's feature set along the wrong line

"Dissecting Anomalies", *JF* 63(4), 2008 **[PR]** —
<https://doi.org/10.1111/j.1540-6261.2008.01371.x>. Full text not obtained
(Wiley/JSTOR blocked); characterisation from the abstract and the CFA Institute
Digest summary **[unverified at source]**: net stock issues, accruals and momentum
are pervasive across all size groups; **asset growth and profitability are "less
robust"** — asset growth present in micro and small but **absent for big**;
profitability significant only in small.

**The spec's features 4, 5 and 6 (margin, turnover, leverage changes) are
profitability- and investment-shaped — the half FF flags as not robust outside
small caps.**

### 3.3 Novy-Marx & Velikov's own size section names the two signals that die

From the NBER w20721 PDF, p. 43 (**read directly**):

> "The transactions costs seem to be immaterial for the low-turnover anomalies,
> even for the micro caps. **The only exception to this rule are the micro caps
> Size, Accruals, and Piotroski's F-score strategies, whose net excess returns seem
> to drop to insignificant levels.**"

Accruals and F-score. Both are accounting-delta constructs. Both are named as the
exceptions that die in microcaps.

### 3.4 The India-side habitat evidence brackets the band without landing in it

- The only India study testing a size interaction (§2.4 **[WP]**) finds the effect
  stronger in "small" firms whose **median market cap is ₹156 Cr** — **below** the
  201–1000 band.
- The supportive India earnings-momentum result (§2.2 **[PR]**) is on **BSE 500** —
  overlapping the band's top edge at best, mostly **above** it.
- The India PEAD study reports drift robust to an Amihud control, while its own
  literature review records that elsewhere the anomaly was "primarily limited to
  highly illiquid stocks."

### 3.5 And avoiding illiquid names is not free

Chen & Velikov, "Zeroing In on the Expected Returns of Anomalies", *JFQA*
**[PR]** — <https://doi.org/10.1017/s0022109022000874>; FEDS WP
<https://www.federalreserve.gov/econres/feds/files/2020039pap.pdf>. Verbatim from
the WP **[unverified at source]**:

> "academic strategies naively trade stocks that are too illiquid. But simply
> avoiding illiquid stocks may not be wise, as **predictability is much stronger in
> the more illiquid stocks**. Indeed, Novy-Marx and Velikov (2019) find that simply
> avoiding illiquid stocks [is] also naive, as **the reduction in gross returns is
> as large or larger than the improvement in trading costs.**"

**Net read on §3.** Ranks 201–1000 is the right *choice* — it is above the
microcap zone that generated the artefactual half of the literature. But the
literature is explicit that moving up-cap costs gross return roughly as fast as it
saves cost. **Nothing directly evidences the spec's actual habitat**, and the spec
should expect a materially smaller effect than any published EW number. This is
exactly the §0 tension the spec already flags ("strongest effect vs worst data");
**the literature does not resolve it, and it is not resolvable by choosing more
carefully.**

---

## 4. Decay and turnover — is quarterly right?

### 4.1 The information horizon is about three quarters, then it reverses

Bernard & Thomas (1990), *JAE* 13(4) **[PR]** —
<https://doi.org/10.1016/0165-4101(90)90008-r>; full text
<https://deepblue.lib.umich.edu/bitstreams/76760a1a-7cf1-4f33-abdd-e9cfdda79b80/download>.
96,087 announcements, 1974–1986 **[unverified at source]**: seasonal
autocorrelations of quarterly earnings changes **+0.34, +0.19, +0.06 at lags 1–3
and −0.24 at lag 4**; the surprise portfolio earns +1.32% around the *next*
announcement, less at t+2/t+3, and **significantly negative at t+4**.

**This is the single most useful number for the spec's rebalance question.** The
information in a quarterly earnings change lives roughly three quarters and then
*reverses*. A quarterly rebalance is therefore **not too slow** — but it also means
a position should not be expected to keep working past ~3 quarters, and the spec's
pre-registered **semi-annual ("H") sensitivity is contra-indicated**, as is any
argument for holding through.

India corroborates: Sehgal & Jain (§2.2) find 6-6 stronger than 12-12 and
overreaction/reversal after the holding window.

### 4.2 Post-publication decay: the baseline haircut is ~58%

McLean & Pontiff, *JF* 71(1), 2016 **[PR]** — <https://doi.org/10.1111/jofi.12365>.
97 predictors: **−26% out-of-sample, −58% post-publication**, and decay is **worst
for portfolios concentrated in stocks with high idiosyncratic risk and low
liquidity** **[unverified at source]**. Category-level decay for accounting vs
price-based predictors: **UNVERIFIED**.

Every signal in SPEC-QFM-01 §4.3 is published, and most of the underlying papers
are pre-2003.

### 4.3 The predictability the spec relies on may already be gone

Green, Hand & Zhang, "The Characteristics that Provide Independent Information
about Average U.S. Monthly Stock Returns", *RFS* 30(12), 2017 **[PR]** —
<https://doi.org/10.1093/rfs/hhx019>. Abstract verbatim (fetched and read
directly):

> "…simultaneously including **94 characteristics** in Fama-MacBeth regressions
> that **avoid overweighting microcaps** and adjust for data-snooping bias. We find
> that while **12 characteristics are reliably independent determinants in
> non-microcap stocks from 1980 to 2014** as a whole, **return predictability
> sharply fell in 2003 such that just two characteristics have been independent
> determinants since then. Outside of microcaps, the hedge returns to exploiting
> characteristics-based predictability also have been insignificantly different
> from zero since 2003.**"

**This is the most damaging single citation in this review.** SPEC-QFM-01 proposes
a characteristics-based hedge outside microcaps. GHZ says that, in the US, that has
produced returns statistically indistinguishable from zero for the last two decades
of their sample. **Which 12, and which 2, is unverified** (closed access) — and it
matters enormously whether any accounting delta is among them.

Corroborating: PEAD attenuation. Martineau (2022), *Critical Finance Review*
11(3–4) **[PR]** — <https://cfr.ivo-welch.org/published-old/papers/martineau2021rest.pdf>,
1984–2019, verbatim **[unverified at source]**: *"In modern financial markets,
stock prices fully reflect earnings surprises on the announcement date, leading to
the disappearance of post-earnings announcement drifts. **For large stocks, PEAD
have been non-existent since 2006**, but [it] has only disappeared recently for
microcap stocks."* Chordia, Subrahmanyam & Tong (2014), *JAE* 58(1) —
<https://doi.org/10.1016/j.jacceco.2014.06.001> **[unverified at source, WP
vintage]**: post-decimalisation **SUE premium 0.14% → 0.01%/month**.

And Linnainmaa & Roberts, *RFS* 2018 **[PR]** —
<https://doi.org/10.1093/rfs/hhy030> — using pre-1963 out-of-sample data, conclude
that **"most accounting-based return anomalies … likely result from data
snooping"** **[unverified at source]**. That paper targets this family by name.

**The counterweight, stated fairly:** Chen & Zimmermann, *Critical Finance Review*,
2022 **[PR]** — <https://doi.org/10.1561/104.00000112> — reproduce 319
characteristics and find "**98% of our long-short portfolios find t-stats above
1.96**", and in *RAPS* 10(2) — <https://doi.org/10.1093/rapstu/raz011> — estimate
publication-bias-adjusted returns only **12.3% smaller** **[unverified at source]**.
The replication crisis in this literature is contested, not settled. But note the
asymmetry: Chen & Zimmermann show the published numbers are *reproducible*; HXZ and
GHZ show they do not *survive* honest weighting or the post-2003 regime. Those are
compatible claims, and both are bad news for trading the signal.

### 4.4 Turnover arithmetic the spec should confront

The 200%/yr one-way budget (§5) requires **≤50% name replacement per quarter** in a
top-40 book. Full quarterly replacement is 400%/yr one-way. The budget is binding,
not decorative.

**And there is a specific mechanism finding the spec should adopt.** Novy-Marx &
Velikov's cost-mitigation tables **[unverified at source — table digits not
personally re-read]**: for PEAD(SUE), slowing the calendar (staggered ⅓/month
rebalance) cut turnover to 24.91% and produced net 0.17 [t 1.11]; a **buy/hold
hysteresis band** (10%/20% sS rule) cut turnover to the same 24.38% and produced
net **0.35 [t 2.26]**. Same turnover reduction, opposite outcome. Across all 23
anomalies the sS rule cut turnover 41% and costs 42%.

**Recommendation (§10, item C): the spec should control turnover with a
pre-registered buy/hold band (enter top X, hold to top Y) rather than by slowing
the calendar.** Slowing the calendar destroys earnings-type signals; hysteresis
preserves them. This must be decided *before* freeze — choosing it afterwards is a
fitted parameter.

---

## 5. Net-of-cost evidence — and the failure mode the spec has not named

### 5.1 The India literature is 100% gross

**Not one India study located in this pass reports net-of-cost returns to a
fundamental or earnings-based cross-sectional strategy.**

- Sehgal & Jain 2015 (§2.2) — the best India earnings-momentum result — **explicitly
  defers costs to future work**. Eleven years later I found no paper that did it.
- Rastogi 2025 (§2.4) — no cost analysis of any kind.
- Harshita et al. 2018 (§2.3) — no cost analysis.
- OpenAlex search for India + anomalies + transaction costs returned nothing
  relevant.

The programme's own history says what a gross-only literature means: the legacy
system had real gross alpha (~18.5%/yr, t≈2.95) entirely consumed by friction.
**The India evidence base is silent on the only question that decided the last
family.**

Chen & Velikov state the general position, p. 1 **[unverified at source]**: *"With
only a couple exceptions, the literature ignores trading costs, which can
significantly reduce expected payoffs."*

### 5.2 The one honest net-of-cost table — and it is bad for this family

Novy-Marx & Velikov, "A Taxonomy of Anomalies and Their Trading Costs", *RFS*
29(1), 2016 **[PR]** — <https://doi.org/10.1093/rfs/hhv063>; NBER w20721
<https://www.nber.org/papers/w20721>. Sample 07/1963–12/2012, CRSP/Compustat,
**value-weighted deciles, NYSE breakpoints**, net of Hasbrouck (2009) effective
spreads.

**Table 3, Panel A (low turnover) and Panel B — digits read directly off the NBER
PDF, monthly %, t-statistics in brackets:**

| Anomaly | Gross | FF4 α gross | 1-sided mo. TO | T-cost | **Net** | FF4 α net |
|---|---|---|---|---|---|---|
| Gross Profitability *(LEVEL)* | 0.40 [2.94] | 0.52 [3.83] | 1.96 | 0.03 | **0.37 [2.74]** | 0.51 [3.77] |
| Value *(LEVEL)* | 0.47 [2.68] | −0.17 [−1.76] | 2.91 | 0.05 | **0.42 [2.39]** | −0.02 [−0.17] |
| Investment *(LEVEL)* | 0.56 [4.44] | 0.35 [2.90] | 6.40 | 0.10 | **0.46 [3.60]** | 0.31 [2.62] |
| **Accruals** *(DELTA)* | 0.27 [2.14] | 0.27 [2.15] | 5.74 | 0.09 | **0.18 [1.43]** | 0.19 [1.55] |
| **Asset Growth** *(DELTA)* | 0.37 [2.52] | 0.07 [0.58] | 6.37 | 0.11 | **0.26 [1.75]** | 0.03 [0.21] |
| **Piotroski's F-score** *(DELTA-heavy)* | 0.20 [1.04] | 0.31 [1.75] | 7.24 | 0.11 | **0.09 [0.45]** | 0.24 [1.37] |
| Return-on-book-equity *(LEVEL)* | 0.71 [2.96] | 0.84 [4.41] | 22.27 | 0.38 | **0.33 [1.38]** | 0.59 [3.18] |
| **PEAD (SUE)** *(DELTA)* | 0.72 [4.52] | 0.58 [4.31] | 35.07 | 0.46 | **0.26 [1.60]** | 0.29 [2.21] |
| PEAD (CAR3) *(event)* | 0.91 [6.54] | 0.87 [6.39] | 34.69 | 0.57 | **0.34 [2.41]** | 0.38 [2.85] |

*(Gross Profitability, Value, Investment, Accruals, Asset Growth and F-score rows
personally verified against the NBER PDF, p. 18. The Panel B rows and cost
mechanics are as reported by a delegated researcher from the same PDF.)*

**Read this before advocating for the family.** Under the honest VW/NYSE protocol:

- **What survives net is LEVELS** — gross profitability (net t 2.74), value (2.39),
  investment (3.60).
- **What fails net is DELTAS** — accruals (net t 1.43), asset growth (1.75),
  **Piotroski's F-score (net t 0.45)**, PEAD(SUE) (1.60).
- **Piotroski's F-score is not even significant GROSS** (t 1.04). Its FF4 alpha
  gross is t 1.75.

**Five of the F-score's nine signals are YoY changes in accounting ratios, and
three of those — ΔGM, ΔATO, ΔDTA — are literally spec features 4, 5 and 6** (§1.1).
The nearest tested analogue of half this spec's composite produces a net
t-statistic of 0.45.

### 5.3 The failure mode the spec has not named

SPEC-QFM-01 §0 says: *"the bottleneck that killed the legacy system (1.6
round-trips/day) is not the primary risk here… The primary risk is that fundamental
data arrives restated."*

**Both are real, and the literature names a third that the spec does not, and which
is more likely than either.**

Look at the F-score row again: turnover 7.24%/month, cost 0.11%/month. **The cost
is trivial. The family's structural defence — "we are low-turnover by design" —
works perfectly, and the strategy still fails, because the gross effect is not
there under honest weighting.** Net 0.09% is small because gross 0.20% was small,
not because 0.11% of cost ate it.

This is a **different failure mode from the legacy system's** and the spec is not
armoured against it:

- Against friction, the spec has a turnover budget, a slippage floor, a stress case
  and a net-IR kill line. Good.
- Against restatement look-ahead, it has the §2 PIT store, the restatement census
  and the §2.5 audit. Good.
- Against **"the gross signal is an equal-weighting artefact"**, it has **nothing**.
  §5 specifies an **equal-weighted** top-40 book, and §7's blocked EW-vs-MW
  sensitivity means the spec cannot currently even measure its exposure to the
  problem.

Novy-Marx & Velikov, verbatim (NBER w20721, p. 2–3) **[cost mechanics unverified at
source; EW quote verified directly from the PDF at line 121]**:

> "**equal-weighted portfolio results, popular in the academic literature because
> they frequently provide stronger results than value-weighted results, are
> misleading and should be viewed skeptically. Because equal-weighted strategies are
> more expensive to trade, equal-weighting often results in a deterioration of net
> performance.**" … "Round trip transaction costs for typical value-weighted
> strategies average in excess of 50 bps… **Transaction costs for equal-weighted
> strategies are generally two to three times as high.**"

**This makes SPEC-QFM-01's blocked MW path (§9 of CLAUDE.md, `backtest_52wh`
raising `NotImplementedError`) a substantive gap, not a cosmetic one.** The
CLAUDE.md CURRENT STATE records that the absolute-mcap data was recovered on
2026-07-20 and that "unblocking data is free; spending the sensitivity is a trial
AND needs a spec decision." **For this family the EW-vs-MW comparison is not a
sensitivity — it is the primary test of whether the effect exists at all.** See
§10, item E.

### 5.4 The practitioner counter-evidence, flagged

Frazzini, Israel & Moskowitz, "Trading Costs of Asset Pricing Anomalies" (2012) and
"Trading Costs" (2018) — **[VM] both are AQR working papers, never peer-reviewed,
by employees of a firm selling these strategies. Systematically biased toward
"costs are low, capacity is large."** <https://www.aqr.com/Insights/Research/Working-Paper/Trading-Costs>.
They report ~$1.7tn of live trades across 21 developed markets and costs "an order
of magnitude smaller than previous studies suggest."

**Three reasons this does not rescue the spec**, all from fetched sources
**[unverified at source]**: (a) Novy-Marx & Velikov note the FIM data is "limited to
larger stocks" over a short time series; (b) Chen & Velikov report that the size,
value and momentum net returns FIM found at 30–70 bps "drop to between −30 and +25
bps post-2005"; (c) **FIM tests size, value, momentum and short-term reversals — no
accounting-delta strategy and no emerging-market data.** It is not evidence about
this family.

### 5.5 Expected-return arithmetic, for calibration only

Chen & Velikov (§3.5) **[PR]**, published abstract **[unverified at source]**: 204
anomalies net of effective spreads, post-publication effects and the post-2005
regime — *"average anomaly's expected return is a measly 4 bps per month. The
strongest anomalies net, at best, 10 bps after controlling for data mining."* Their
FEDS decomposition: **66 bps/mo gross in-sample → 38 net in-sample → 13 adding
post-publication → 8 also restricting to post-2005**, and their costs are effective
spreads only — *"a lower bound"*, with no price impact and no short-sale fees.

This is a US calibration and India may differ. **That "India lags the US arbitrage
wave" argument is plausible and entirely unverified.** It belongs in the spec as an
assumption to be tested, never as a discount already taken.

### 5.6 There is no Indian implementation-shortfall literature to calibrate against

A targeted search for peer-reviewed Indian trading-cost / implementation-shortfall
estimates for mid- and small-caps found **nothing usable** **[unverified at source
— stream conducted by a delegated researcher]**:

- Domowitz, Glen & Madhavan, *International Finance* 4(2), 2001 **[PR]** —
  <https://doi.org/10.1111/1468-2362.00072> — 42 countries, **Sep 1996 – Dec 1998**,
  finds emerging markets have "significantly higher trading costs even after
  correcting for factors such as market capitalization and volatility". India's
  specific number unverified, and the sample **predates dematerialisation, the 2001
  badla ban, T+2 and T+1 — far too stale to parameterise anything.**
- A *Journal of Quantitative Economics* (2021) paper —
  <https://doi.org/10.1007/s40953-021-00253-z> — is reported to state that Indian
  market impact cost fell "from 3.00% in 1993 to 0.50% in 1997". **UNVERIFIED
  (Springer auth wall). Do not cite.**
- "Estimation of Impact Cost – A Study of NSE Emerge Platform" reports average
  impact cost of **16.45%** — **[PR, very low-tier, and the SME platform is the
  wrong universe]**. Order-of-magnitude illustration of the illiquid tail only.
- **Every readily accessible source on Indian round-trip costs is broker
  marketing** — Zerodha, 5paisa, ClearTax, Motilal Oswal, Chittorgarh **[VM]**.
  These omit impact cost and slippage entirely. Acceptable for reading off a
  statutory rate; **unacceptable for estimating implementation shortfall.**

**The best available anchor is NSE's own impact-cost definition and index
thresholds**, from the NSE Indices master methodology
(<https://www.niftyindices.com/Methodology/Method_NIFTY_Equity_Indices.pdf>),
verbatim **[unverified at source]**:

> "Impact cost represents the cost of executing a transaction in a given stock, for
> a specific predefined order size, at any given point of time… the percentage
> mark-up observed while buying / selling the desired quantity of a stock with
> reference to its ideal price (best buy + best sell) / 2."

with NSE's own caveats: computed separately for buy and sell, **varies with
transaction size**, dynamic, and "where a stock is not sufficiently liquid, **a
penal impact cost is applied**" — i.e. published impact cost for illiquid names is
a substituted floor, not a measurement.

Eligibility thresholds: **Nifty 50 requires ≤ 0.50% impact cost for 90% of
observations over six months, for a portfolio order size of ₹10 crore. Nifty 500
requires ≤ 1% over six months — with NO order size stated in that block.**

**A trap worth stating explicitly:** the ₹10 crore order size is attached to the
Nifty 50 test. **Do not assume it carries across to the Nifty 500 / Smallcap /
Microcap 1% criterion — that assumption is unverified and would materially
understate mid/small-cap impact.** What the threshold does give you is a free lower
bound: every name in the 201–1000 habitat that is in the Nifty 500 clears ≤1%
impact cost by construction. At ₹100 Cr AUM the binding constraint will be the
book's own footprint, not index eligibility.

**Conclusion.** There is no published Indian implementation-shortfall estimate the
spec can cite for its habitat. The friction stack must rest on (a) verified
statutory/exchange components, (b) NSE impact-cost thresholds as an
order-of-magnitude anchor with the penal-substitution caveat stated, and (c)
**slippage as an explicit, disclosed free parameter stress-tested over a range
rather than a point estimate** — which is what RULING 5 and SPEC-QFM-01 §6 already
do. **The absence of a credible Indian TCA literature is itself the finding, and it
argues for widening the stress range, not narrowing it.**

**Two constants flagged for `src/costs_in.py` review** (raised by the delegated
stream, recorded here because RULING 5 says statutory lines are FACT and must be
primary-source verified): **STT at 0.1%/side delivery** and the **SEBI turnover fee
at 0.0001%** could not be verified from a government primary in this pass —
`incometaxindia.gov.in` returns HTTP 403 to automated fetch, so only secondary
broker sources were reachable. The NSE transaction charge (**₹2.97 per lakh per
side, effective 1 Oct 2024**, NSE circular NSE/FA/64232,
<https://archives.nseindia.com/content/circulars/FA64232.pdf>) and stamp duty
(**0.015%, buyer-only, on delivery**) were verified from exchange / near-statutory
primaries. **This is a note for whoever owns RULING 5, not a finding of this
review** — the constants may well already be primary-verified in
`governance/evidence/`; if they are, disregard.

---

## 6. Overlap risk — the spec's own most-likely killer

### 6.1 The India evidence raises the alarm and does not settle it

- **Sehgal & Pandey 2021 (§2.1), verbatim:** *"the role of quality in predicting
  returns is **partially subsumed by momentum in short holding periods**."* The
  paper that best supports the delta-over-level design **states the overlap problem
  itself, in India, for the same construct.**
- **Sehgal & Jain 2015 (§2.2):** the spanning runs the *other* way — earnings
  momentum **subsumes** price and revenue momentum at 6-6 horizons in India.
- **These two are in tension and I cannot reconcile them** from an abstract and one
  full text. Different constructs (quality-increase composite vs SUE), different
  windows (unverified vs 2002–2010), opposite spanning conclusions.
- **Kaur et al. 2024 (§2.6):** *"the explanatory effect of quality on prices is
  limited."*

### 6.2 The best quantitative spanning result runs in the family's favour

Novy-Marx (§1.3), Table 2 Panel B — a long/short factor built on **standardised
YoY earnings change (SUE)**, 2×3 size × surprise sorts, NYSE 30/70 breakpoints,
**value-weighted** legs **[unverified at source — table digits fetched by a
delegated researcher from <https://www.nber.org/system/files/working_papers/w20984/w20984.pdf>]**:

| Regressand = SUE factor | Controls | α (%/mo) | t |
|---|---|---|---|
| — | none | 0.59 | [7.14] |
| | MKT, SMB, HML | 0.70 | [8.68] |
| | **+ UMD, CAR3** | **0.38** | **[5.31]** |
| | full, 1/94–12/12 | 0.34 | [3.36] |

And the mirror image, Panel A: UMD's own alpha goes from **+0.64 [3.03]** raw to
**−0.48 [−2.55]** once SUE and CAR3 are controls; adjusted R² rises 5.8% → 40.6%.
Rank correlations: SUE ↔ r₂,₁₂ = **29.1%**, SUE ↔ CAR3 = 19.9%.

**This is the strongest quantitative evidence in the whole review that a
fundamental-delta signal is not spanned by price momentum** — 0.38%/month with
t = 5.31 *after* momentum controls, and stable across subsamples. It is also
important that SUE ↔ momentum rank correlation is only 29%: related, not
duplicative. But four qualifications travel with it:

1. **The paper is an unrefereed working paper, eleven years on.** It is still
   listed under "Working Papers" on the author's own page
   (<https://mysimon.rochester.edu/novy-marx>) alongside his refereed JFE work.
2. **Half of its "fundamental momentum" is not fundamental.** CAR3 is a three-day
   *price* reaction around the announcement. The clean accounting leg is SUE alone.
3. **SUE is standardised** — the exact thing spec feature 2 is not (§1.4).
4. **Its "fully explains" claim is contradicted in the refereed literature.** Zhang,
   "What Can Explain Momentum? Evidence from Decomposition", *Management Science*,
   2021 **[PR]** — <https://doi.org/10.1287/mnsc.2021.4135> — verbatim
   **[unverified at source]**: *"firm fundamentals are the most promising among
   well-known explanations of momentum… Collectively, all explanations capture 31%
   of momentum, whereas **69% of momentum remains unexplained**."* And a rival
   full-explanation claim exists that needs no fundamentals at all: Ehsani &
   Linnainmaa, "Factor Momentum and the Momentum Factor" — <https://doi.org/10.3386/w25551>,
   later *JF* — *"Factor momentum explains all forms of individual stock momentum."*
   Two mutually incompatible "we explain all of momentum" papers is itself
   information about how much weight either deserves.

**The sting.** If Novy-Marx is right that the accounting delta is the primitive and
price momentum the derivative, then a long-only fundamental-delta book **loads on
momentum by construction, whether or not it was designed to**. India's own momentum
anomaly is reported as **explained by risk models over 2005–2016** (§2.5). An
attribution that lands on "this is investable momentum" is a §8.1 kill regardless
of which factor is causally prior.

### 6.3 The delta may be the weakest leg of its own story

Hou, Mo, Xue & Zhang, "An Augmented q-Factor Model with Expected Growth",
*Review of Finance* 25(1), 2021 **[PR]** —
<https://academic.oup.com/rof/article-abstract/25/1/1/5727769>, PDF
<https://global-q.org/uploads/1/2/2/6/122679606/q5rf2021.pdf>. The q5 expected-growth
factor forecasts future investment-to-assets changes from three predictors:
log Tobin's q (**level**), cash-based operating profitability Cop (**level**), and
**dRoe = the change in ROE over the past four quarters (a delta)**. Sample Jan 1967
– Dec 2018; R_Eg premium 0.84%/mo (t = 10.27) **[unverified at source]**.

The decomposition is the useful part. Adding each predictor's own factor to the
q-model:

- **+ Cop (level)** → alpha falls 0.67 → **0.37% (t = 6.35)** — the dominant leg.
- **+ dRoe (the delta)** → alpha falls only to **0.63% (t = 8.56)** — "dRoe plays a
  more limited role."

**Read this against the spec.** A change-in-ROE factor is real, constructible and
distinct from level profitability (correlations with R_Eg: R_Roe 0.506, R_dRoe
0.423). But it is the *weakest* of the three legs, and a profitability **level**
does most of the work. Combined with Novy-Marx & Velikov's Table 3 (§5.2, levels
survive net, deltas do not), the pattern across two independent literatures is the
same: **where a delta composite has an edge, the level content smuggled into its
ratios is a live candidate for where that edge actually comes from.** The spec's
§7 overlap test must therefore control for level profitability specifically, not
only for momentum and size.

One further warning that lands directly on spec feature 4: Ball, Gerakos,
Linnainmaa & Nikolaev, *JFE* 121(1), 2016 **[PR]** —
<https://doi.org/10.1016/j.jfineco.2016.03.002> — find that **cash-based operating
profitability subsumes accruals** in the cross-section (cash-based t = 7.4;
accrual-contaminated loses most of its power, t = 1.56) **[unverified at source]**.
The spec's operating-margin-change leg (`ebit/revenue`) is accrual-contaminated by
construction, and the spec has already excluded a `cfo`-based feature pending OPEN
ITEM 6. That exclusion is defensible, but it means the family carries the
accrual-contamination problem with no cash-based control anywhere in §4.3.

**Unfavourable, and decisive:** Green, Hand & Zhang (§4.3) *is* the spanning test,
run at scale, jointly over 94 characteristics, in the US, avoiding microcaps. Its
answer is 12 survivors over 1980–2014 and **two since 2003**.

### 6.4 The Indian infrastructure to run this test does not exist in usable form

Two findings here materially change SPEC-QFM-01 OPEN ITEM 9.

**(a) The standard Indian academic factor library has NO quality or profitability
factor.** Agarwalla, Jacob & Varma, "Four Factor Model in Indian Equities Market",
IIMA W.P. 2013-09-05 **[WP]** —
<https://faculty.iima.ac.in/~iffm/Indian-Fama-French-Momentum/>,
paper PDF
<https://faculty.iima.ac.in/~iffm/Indian-Fama-French-Momentum/four-factors-India-90s-onwards-IIM-WP-Version.pdf>.
**Factors provided: exactly four — market premium, SMB, HML, WML.** Coverage
**Oct 1993 – Dec 2025**, daily/monthly/yearly, with **survivorship-bias-adjusted
variants** (the recommended series) plus 6 size-value and 4 size-momentum
portfolios and breakpoint files. Construction excludes micro-caps below 10% of
median market cap and penny stocks (median price < ₹1.00) **[unverified at
source]**.

This is a directly useful asset for the spec — it supplies a survivorship-adjusted
Indian **momentum** control that the repo does not currently hold, over a longer
window than any NSE factor index. **But it stops at WML. There is no Indian
profitability or quality factor in it.**

**(b) Nifty200 Quality 30 is the wrong shape to serve as the spec's quality
control.** From the NSE Indices primary methodology
(<https://www.niftyindices.com/Methodology/Method_NIFTY200_Quality30.pdf>;
consolidated master
<https://www.niftyindices.com/Methodology/Method_NIFTY_Equity_Indices.pdf>),
verbatim **[unverified at source]**:

> "Z score is calculated on the basis of return on equity (ROE), debt-to-equity
> (D/E) ratio and **EPS growth variability** in the previous 5 years… **Latest
> fiscal year data is considered for the calculation of return on equity (ROE) and
> debt-to-equity (D/E) ratio.**"

Weighted Z (non-financials) = `0.33·Z(ROE) + 0.33·(−Z(D/E)) + 0.33·(−Z(EPS growth
variability))`; semi-annual rebalance; F&O-eligible Nifty 200 names only; firms
with negative EPS in any of the previous 6 FYs excluded outright.

**So: ROE LEVEL, D/E LEVEL, and YoY EPS-growth deltas entering only through their
STANDARD DEVIATION, with a negative sign.** The index contains **no directional
change-in-fundamentals signal at all**, and it *penalises* growth variability —
which is, in sign terms, arguably the opposite of what spec feature 3 (earnings
acceleration) rewards.

**Two consequences, and they pull against each other.** Fetching Quality 30 is
*less* useful than the spec assumed — a near-orthogonal benchmark is a weak
spanning control, and passing against it would prove little. But the underlying
concern is *more* serious, not less: the spec needs a control for **level
profitability** (§6.3), and neither the IIMA library nor any NSE index supplies
one. **Building an Indian profitability factor from the IIMA universe is therefore
a prerequisite for the §7 overlap test, not an optional robustness check — and
because it is a modelling choice, it must be specified in the frozen spec, before
contact.**

**(c) Launch-date backfill is worse and broader than CLAUDE.md records.** NSE
factsheets **[unverified at source]**:

| Index | Launch | Base date | Backfill gap |
|---|---|---|---|
| Nifty200 Quality 30 | **17 Apr 2018** | 1 Apr 2005 | **~13 yrs** |
| Nifty200 Momentum 30 | **25 Aug 2020** | 1 Apr 2005 | **~15 yrs** |
| Nifty500 Value 50 | **24 Oct 2018** | 1 Apr 2005 | **~13 yrs** |
| Nifty Alpha 50 | unverified | 31 Dec 2003 | ≥ launch − 2003 |

CLAUDE.md currently flags the backfill caveat for Nifty200 Momentum 30 only. **It
applies to Quality 30, Value 50 and Alpha 50 as well**, over 13–15 year gaps that
cover most of the spec's dev window. Every §7 comparator except Nifty 100 and the
broad-market TRI series is a vendor back-test for the majority of the period it
would be used over.

**One comparator is clean.** Nifty200 Momentum 30's score is a Z-composite of
12-month and 6-month price returns divided by annualised daily-return volatility —
**no fundamental input whatsoever** **[unverified at source]**. As a *price
momentum* control it is uncontaminated by fundamentals, which is exactly what §6.2
requires. Its pre-2020 history is still backfilled.

### 6.5 Net read on overlap

The spec is right that this is the most likely killer, and the picture is now
sharper than "unsettled":

- Against price momentum specifically, the evidence is **favourable** (Novy-Marx
  Panel B; Sehgal & Jain's India finding that earnings momentum subsumes price
  momentum) but rests on an unrefereed paper and a 2002–2010 India sample.
- Against **level profitability**, the evidence is **unfavourable** (q5's dRoe is
  the weak leg; NM&V's levels-survive-deltas-don't table), and this is the control
  the repo cannot currently construct.
- The joint test at scale (Green-Hand-Zhang) says almost nothing survives
  post-2003 outside microcaps.

**OPEN ITEM 9 should be reclassified from "fetch a quality TRI, or record a
reasoned decision to proceed without it" to a hard freeze blocker with a changed
requirement: construct an Indian level-profitability control (IIMA universe), and
treat Nifty200 Quality 30 as an additional, weak, differently-shaped comparator
rather than as the answer.**

---

## 7. Source-quality audit of the India evidence base

| Source | Tier | Sample | Universe | Weighting | Gross/Net | Delta or Level |
|---|---|---|---|---|---|---|
| Sehgal & Pandey 2021, *Inv. Analysts J.* | **[PR]** | **unverified** | 1,848 firms | **unverified** | **unverified** | **DELTA** (quality increases) |
| Sehgal & Jain 2015, *AAMJAF* | **[PR]** low-tier | 2002-01–2010-06 | BSE 500 (493) | unverified | **GROSS** (stated) | DELTA (SUE/SUR) |
| Harshita et al. 2018, *Theor. Econ. Letters* | **[PR]** very low-tier | 2002Q4–2017Q3 | Nifty 500, **2014-03-31 snapshot (survivorship)** | decile | **GROSS** | DELTA (SUE) |
| Rastogi 2025, ISB dissertation | **[WP]** | 2013–2022 | all-listed Prowess, **median ₹156 Cr** | equal | **GROSS** | MIXED (F-score) |
| Sharma, Subramaniam & Sehgal 2019, *Global Bus. Rev.* | **[PR]** | 2005-07–2016-06 | NSE 500 | quintile/decile | **GROSS** | n/a — **decay finding** |
| Lalwani & Meshram 2021, *Applied Economics* | **[PR]** | 1994–2019, survivorship-free | all-listed | n/a | **unverified** | **14 of 35 survivors UNVERIFIED** |
| Kaur, Seth & Singh 2024, *Managerial Finance* | **[PR]** | 2003–2020 | BSE-listed | unverified | **unverified** | LEVEL (QMJ) |
| Lalwani 2018, *Managerial Finance* | **[PR]** | unverified | BSE 500 | unverified | **unverified** | LEVEL (quality) |
| Sehgal, Subramaniam & Porteu de la Morandière 2012, *IJEF* | **[PR]** very low-tier (CCSE) | 1996–2010 | BSE-500 | equal | **GROSS** | reports **accruals/profitability signs OPPOSITE to US** |
| Veeraraghavan, *BERJ* 13(6) | **[PR]** very low-tier | n/a | 54 firms | n/a | **no return test** | n/a |
| finpab / investsights / yieldiq / ET screeners | **[VM]** | — | — | — | — | marketing |

**Zero India studies in this table report a net-of-cost result. Zero test the
spec's construct. One tests deltas rather than levels, and its full text could not
be opened.**

---

## 8. Verdict, and the conditions attached to it

### 8.1 The verdict: (B) WEAK / MIXED

Not (A): there is no strong prior. The spec's exact construct has never been tested
anywhere, the India evidence base is gross-only and mostly outside the habitat, and
the nearest US analogue of half the feature set returns a net t-statistic of 0.45.

Not (C) — **but only just.** Two peer-reviewed findings keep the family alive:
Akbas, Jiang & Koch (US, delta not subsumed by level, underreaction, top accounting
journal) and Sehgal & Pandey (India, "increases, not quality"). Both are real
evidence for the family's central design choice. The pre-stated null in
SPEC-QFM-01 §1 — that the base case is death — is now **grounded rather than
asserted**, which is what OPEN ITEM 10 asked for.

### 8.2 Four conditions. If any is declined, the verdict becomes (C).

1. **Resolve the EW-vs-MW question before the first trial, not as a sensitivity.**
   §5.3: the literature's dominant failure mode for this exact family is that the
   gross effect is an equal-weighting artefact, and the spec's only defence against
   it is currently blocked. The absolute-mcap data now exists in the PIT store
   (CLAUDE.md, closed 2026-07-20). Unblocking `weighting="MW"` is required, plus a
   spec decision on semi-annual mcap under a quarterly rebalance.
2. **Promote OPEN ITEM 9 to a hard freeze blocker, with a changed requirement.**
   §6.4. Fetching Nifty200 Quality 30 is *not* sufficient: its construction is ROE
   and D/E **levels** plus a *penalty* on EPS-growth variability, so it is close to
   orthogonal to the spec's composite and passing against it would prove little.
   The control the spec actually needs is **level profitability** (§6.3), and
   neither the NSE index family nor the IIMA four-factor library supplies one.
   Building an Indian profitability factor from the IIMA universe is a
   prerequisite, and — being a modelling choice — must be specified before freeze.
3. **Decide the long-only question explicitly** (§10 item B). Three findings — two
   Indian — say the exploitable information is in the short/avoid leg. The spec's
   own sibling family (52WH) was reframed for exactly this reason. Either justify
   long-only in writing before freeze, or reframe QFM as a negative screen.
4. **Fix feature 2's standardisation and feature 1's inclusion before freeze**
   (§1.4, §2.2). Feature 1 is contra-indicated by the only India study that tested
   it; feature 2 is unstandardised where every validated analogue is standardised.
   Both are free to change now and impossible to change after.

**If the operator will not spend the time on all four, release the slot.** A family
advanced with its most likely killer disabled, on an unstandardised signal, in a
book construction the evidence says is the wrong half, is not a cheap experiment —
it is a slot spent to learn nothing.

### 8.3 The three strongest pieces of evidence, each way

**FOR:**

1. **Akbas, Jiang & Koch, *The Accounting Review* 2017** — the profit *trend*
   predicts returns and is **not subsumed by the level of profitability, earnings
   momentum, or other well-known determinants**; mechanism is underreaction, with
   *no* evidence of overreaction. <https://doi.org/10.2308/accr-51708>
2. **Sehgal & Pandey, *Investment Analysts Journal* 2021** — in India, "**quality
   increases, not quality, drive stock returns**". The delta-over-level design
   choice, endorsed in the right country by a peer-reviewed source.
   <https://doi.org/10.1080/10293523.2021.1991130>
3. **Novy-Marx (2015) Table 2 Panel B** — a standardised YoY-earnings-delta factor
   earns **0.38%/month, t = 5.31, after controlling for price momentum and the
   3-day announcement-return factor**, stable across 1975–1993 and 1994–2012, on
   value-weighted legs with NYSE breakpoints. The single strongest quantitative
   answer to the spanning question — **caveated by being an unrefereed working
   paper whose "fully explains momentum" claim is contradicted by Zhang (*Manag.
   Sci.* 2021, 69% of momentum unexplained)**. <https://www.nber.org/papers/w20984>

*(Runner-up: He & Narayanamoorthy, JAE 2020 — earnings acceleration, the exact
shape of feature 3, "robust to a wide range of previously documented anomalies and
a battery of risk controls", <https://doi.org/10.1016/j.jacceco.2019.101238> — held
back from the top three only because the controls are unnamed and the full text
could not be opened.)*

**AGAINST:**

1. **Novy-Marx & Velikov, *RFS* 2016, Table 3** — under value-weighting with NYSE
   breakpoints, **Piotroski's F-score nets 0.09%/month, t = 0.45** (and is
   insignificant even gross, t = 1.04); accruals net t 1.43; asset growth net t
   1.75; PEAD(SUE) net t 1.60. **Five of nine F-score signals are YoY changes in
   accounting ratios and three are literally spec features 4, 5 and 6.** What
   survives net is *levels*.
   <https://doi.org/10.1093/rfs/hhv063>
2. **Green, Hand & Zhang, *RFS* 2017** — of 94 characteristics jointly tested
   outside microcaps, 12 are reliably independent over 1980–2014 and **just two
   since 2003**; **"outside of microcaps, the hedge returns to exploiting
   characteristics-based predictability also have been insignificantly different
   from zero since 2003."** <https://doi.org/10.1093/rfs/hhx019>
3. **The India evidence base is 100% gross and none of it tests the spec's
   construct** (§2.7, §5.1) — the best India earnings-momentum paper explicitly
   defers costs to future work, ends in **June 2010**, is on **BSE 500**, is
   **long/short with both legs contributing**, and finds **revenue surprise adds
   "very small" incremental information** (a full 1/6 of the spec's composite).
   Its own lead author later reports Indian anomalies **fading** through 2016.

---

## 9. The case for (C), stated fairly

An operator could reasonably return (C) — release shadow slot 1 — on this record,
and the argument is not weak:

- The spec's exact construct has **no prior anywhere**, not just no India prior.
- The nearest tested analogue of half its features nets **t = 0.45**.
- The best India support ends in **2010**, and the same author reports decay through
  **2016** over a window covering the middle of the spec's dev data.
- The best-constructed India study's answer to "which characteristics work" is
  **unverified and inaccessible** — and it is the one datum that would settle this.
- The habitat evidence **brackets** ranks 201–1000 without ever landing in it, and
  the literature says moving up-cap costs gross return as fast as it saves cost.
- Two of the four conditions in §8.2 (MW unblocking, quality TRI) are work the
  programme has already deferred once.
- The family sits behind three unresolved blockers of its own that this review does
  not touch: **the fundamentals corpus does not exist** (OPEN ITEM 2), the habitat
  fallback trigger is **unevaluable** (OPEN ITEM 1), and announce-date provenance is
  **blocked on the ToU ruling** (OPEN ITEM 3). A slot held by a family that cannot
  be frozen is a slot not held by a family that can.

**The counter, and why I did not return (C):** the two supportive peer-reviewed
findings are real, they are specifically about *deltas not levels*, and one of them
is Indian. OPEN ITEM 10 asked whether the pre-stated null could be grounded rather
than asserted. It can be, and the grounding cuts both ways rather than uniformly
against. That is the definition of (B).

---

## 10. New open items this review creates for SPEC-QFM-01

Recorded here, not written into the spec (the spec is a DRAFT and was not edited).

**A. Feature 2 is unstandardised where every validated analogue is standardised.**
§1.4. Decide before freeze; a `rolling_std` primitive would be an `expr.py` grammar
change and needs its own decision.

**B. Long-only vs negative screen.** §2.6. Three findings — Kaur et al. 2024 (India,
money in the short leg), Sehgal & Jain 2015 (India, both legs contribute), Raju 2023
(the 52WH family's own basis) — point the same way. The spec's §5 top-40 long-only
book may be harvesting the weaker half. This is a **book-construction decision that
must precede freeze**, not a sensitivity.

**C. Turnover control mechanism.** §4.4. Novy-Marx & Velikov find that for
earnings-type signals a buy/hold hysteresis band preserves net alpha at a turnover
reduction where calendar-slowing destroys it. The spec should pre-register an sS-style
band rather than rely on the quarterly calendar and the "H" sensitivity. **[table
digits unverified at source — re-read before this becomes binding.]**

**D. Obtain Lalwani & Meshram (2021) full text.** §2.5. Which 14 of 35
characteristics clear t > 3 in a survivorship-free 1994–2019 Indian sample is the
single highest-value unknown in this review. It would move the verdict in either
direction. Closed access; a library copy or author request is the route.

**E. EW-vs-MW is not a sensitivity for this family; it is the primary existence
test.** §5.3, §8.2(1).

**H. An Indian level-profitability control must be built and specified before
freeze.** §6.3, §6.4. Neither the IIMA four-factor library (market, SMB, HML, WML
only) nor any NSE factor index supplies one, and the q5 decomposition plus
Novy-Marx & Velikov's Table 3 both point at level profitability as the leading
alternative explanation for any edge this family shows.

**I. The IIMA / Agarwalla-Jacob-Varma library should be ingested.**
<https://faculty.iima.ac.in/~iffm/Indian-Fama-French-Momentum/> — market, SMB, HML,
WML, **Oct 1993 – Dec 2025**, with **survivorship-bias-adjusted variants** and
published breakpoint files. It gives the spec a survivorship-adjusted Indian
momentum control over a longer window than any NSE factor index, and it is free.
It is *not* a substitute for item H.

**J. CLAUDE.md's backfill caveat is under-scoped.** §6.4(c). The caveat is
currently recorded for Nifty200 Momentum 30 only; **Nifty200 Quality 30 (launched
2018-04-17), Nifty500 Value 50 (2018-10-24) and Nifty Alpha 50 all carry 13–15
years of vendor back-test** before their base dates of 2005-04-01 / 2003-12-31.
That covers most of the spec's dev window for every §7 comparator except Nifty 100
and the broad-market TRI series.

**K. Feature 4 is accrual-contaminated with no cash-based control.** §6.3. Ball,
Gerakos, Linnainmaa & Nikolaev find cash-based operating profitability subsumes
accruals. The spec's `ebit/revenue` margin leg carries accrual contamination by
construction, and OPEN ITEM 6 has (correctly) excluded the `cfo`-based feature that
would offset it. Disclose, or resolve OPEN ITEM 6 first.

**F. Semi-annual ("H") rebalance sensitivity is contra-indicated** by Bernard &
Thomas's lag structure (+0.34/+0.19/+0.06/−0.24) and by Sehgal & Jain's 6-6 vs
12-12 result. Worth pre-registering as a **predicted failure** before contact — a
cheap, honest, falsifiable statement.

**G. Sources to re-fetch before anything here becomes load-bearing in a frozen
spec:** Akbas, Jiang & Koch full text (weighting scheme, cost treatment); Sehgal &
Pandey 2021 full text (sample, universe, weighting); He & Narayanamoorthy full text
(does it control for SUE and price momentum?); Green, Hand & Zhang (which 12, which
2); Fama & French (2008) full text; Piotroski (2000) full text; Lev & Thiagarajan
(1993) — **not opened at all, do not cite**; Bernard & Thomas (1989) — JSTOR-blocked.

---

## 11. Method and limitations of this pass

- **Data contact: none.** No repository data of any kind was read. No file in
  `governance/` was modified. `SPEC-QFM-01.md` was not edited. Nothing was
  committed.
- **The session's WebSearch budget was exhausted at the start of this task.** All
  retrieval was by direct fetch against canonical endpoints: the OpenAlex API
  (<https://api.openalex.org/>), the Semantic Scholar Graph API, Crossref, NBER,
  and publisher landing pages. Search coverage is therefore **weaker than a normal
  pass** — OpenAlex title-and-abstract search is good at finding a paper you can
  name and mediocre at surfacing one you cannot. **The verified absences in §2.7
  should be read as "not found by systematic API search", not as proof of
  non-existence.**
- **Paywalls defeated verification repeatedly.** SSRN, ScienceDirect, Springer,
  Taylor & Francis, Wiley and JSTOR all returned 403 or auth redirects. Every claim
  resting on an abstract alone is marked as such.
- **Three parallel research streams contributed**; where a number came from a
  delegated fetch I could not personally re-open, it is marked **[unverified at
  source]**. The three decisive numbers (NM&V Table 3 accounting rows, GHZ's
  abstract, Akbas et al.'s abstract) were fetched and read directly by the author of
  this file.
- **A TRAP 6 sighting worth recording operationally.** `niftyindices.com` serves a
  **soft-404**: `Method_Nifty200_Momentum30.pdf` and `Method_NIFTY500_Value50.pdf`
  both return **HTTP 200, identical 77,663 bytes, identical md5
  `25353978724b184ca02c272dbf43a31b`, and zero extractable text**
  **[unverified at source — observed by a delegated researcher]**. This is exactly
  the pattern CLAUDE.md TRAP 6 already records for the BSE PDF archive: a 200 and a
  plausible byte count prove nothing. Any future NSE methodology fetch needs a
  content assertion (extractable text, expected keyword), not a status check. The
  workaround is the consolidated master methodology document, which is genuine
  (3.5 MB).
- **One inter-stream conflict was resolved and is worth recording**, because the
  wrong resolution would have been reassuring: one stream read Novy-Marx & Velikov's
  "<50% monthly turnover generally survives costs" as favourable to the spec's
  quarterly rebalance. The verified Table 3 digits show the opposite conclusion for
  *this* feature set — F-score, accruals and asset growth are all **low**-turnover
  and all fail net anyway, because their gross effect is weak, not because costs are
  high. The general rule is favourable; the specific rows are not, and the specific
  rows govern. **This is the single most important reading in this document
  (§5.3).**

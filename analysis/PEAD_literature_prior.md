# SPEC-PEAD-01 — India prior: literature pass (OUTCOME-BLIND, pre-freeze)

**Date:** 2026-07-22
**Author:** research session, at operator request
**Closes:** `governance/specs/SPEC-PEAD-01.md` **OPEN ITEM 9** ("NO INDIA-SPECIFIC
PRIOR HAS BEEN REVIEWED... **This is the cheapest possible kill for a family
holding a shadow slot**, and it should happen before any of items 1, 2 or 3 are
paid for.")

**Status: DIAGNOSTIC, NOT A TRIAL.** No repo data was touched. No price panel was
loaded, no PIT store was queried, no return series was read, no CAR was computed,
no event study was run, no `data_gate` call was made. Every number below is either
(a) quoted from a published paper with a URL, or (b) derived from
`src/costs_in.py`'s statutory constants and the turnover the spec itself states in
§6. Under `governance/CONTAMINATION_POLICY.md` AMENDMENT A this is a literature
pass plus a cost table — both explicitly free. **Nothing here is charged against
the register's trial count, and SPEC-PEAD-01's single Tier 2 trial remains
UNSPENT.**

**Spec status at time of writing:** DRAFT — no `sha256`, no register row, no
outcome contact authorized. This document interrogates the design and its evidence
base, not the data.

---

## 0. The question, and the one-line answer

SPEC-PEAD-01 §1 pre-states its own null: *"The base case is that gross drift
exists, is small, is concentrated in the least liquid names, and does not survive
§6. **The expected outcome of this family is death at §8.**"*

This document asks whether the published evidence gives any reason to doubt that
null — specifically, whether there is **current, India-specific, net-of-cost**
evidence for a tradeable ~60-session drift in the mid/small-cap habitat.

**One-line answer: there is not. The India PEAD literature consists of three
substantive studies, the most recent and most-cited of which is published by a
documented predatory publisher, uses a universe selected as of a single 2014 date
(not point-in-time), trims its own outcome variable, and ends its sample in
2017Q3 — six months BEFORE the spec's walk-forward would begin. Not one India
study reports a net-of-cost result. Not one covers mcap ranks 201–1000. The only
India study whose sample overlaps the spec's dev window at all finds NO
exploitable drift. Meanwhile the strongest modern international evidence says the
drift, measured with the time-series surprise the spec pins as PRIMARY, does not
persist beyond ~5 days in small caps. Verdict (C): NO CREDIBLE MODERN INDIA
PRIOR — recommend releasing shadow slot 2.**

**The friction arithmetic alone does NOT kill this family** (§6 below) — unlike
SPEC-SRA-01. That matters: this recommendation rests on **evidence quality and
horizon**, not on cost. Stated plainly so the operator can weigh the right thing.

---

## 0.1 Method and its limits (read before relying on this)

WebSearch quota for this session was exhausted before the first query returned.
The pass was run instead against **open scholarly indexes** — OpenAlex, Crossref,
Semantic Scholar — plus direct retrieval of the papers themselves. This is a
*better* route for exhaustiveness (structured title/abstract filters over a full
corpus, not a relevance-ranked top-10) but it has one named blind spot:

> **LIMITATION (named, not hidden):** Indian domestic journals with weak DOI
> coverage — *Indian Journal of Finance*, *Vikalpa*, *IIMB Management Review*,
> *Journal of Emerging Market Finance* — and unindexed NSE/SEBI/IIM working papers
> may be under-represented in these indexes. If the operator wishes to overturn
> the verdict below, **the one targeted follow-up worth paying for is a manual
> sweep of those five sources plus SSRN for the 2018–2024 window.** Nothing found
> here suggests such a sweep would change the answer, but this pass cannot rule it
> out and does not claim to.

Exhaustiveness evidence, so the thinness is auditable rather than asserted:

| Index query | Hits |
|---|---|
| OpenAlex, title/abstract: `"post-earnings announcement drift" AND India` | **5** (3 substantive) |
| OpenAlex, title/abstract: `("earnings momentum" OR "post-earnings") AND India` | **9** (5 substantive) |
| OpenAlex, same, restricted to `from_publication_date:2019-01-01` | **3** (1 substantive) |
| Crossref, `post-earnings announcement drift India`, 20 rows | **0 India papers** — returned Brazil, Hong Kong, Germany, Poland, Russia, Korea, Japan, UK, China, Thailand |

The Crossref result is worth pausing on. A relevance query built around the word
"India" returned PEAD studies for **ten other markets and none for India.** That
is not a search failure; it is the finding.

---

## 1. The core effect and its trajectory — does PEAD still exist?

The task framing is correct: the decisive question is not whether PEAD existed
(Ball & Brown 1968 onward, thousands of citations) but whether it exists **now**.
Volume of citation is not evidence of currency.

### 1.1 The decisive paper: Martineau (2022), *Critical Finance Review*

**Peer-reviewed**, Critical Finance Review (Ivo Welch, editor), 64 citations;
working-paper version on OSF.
<https://doi.org/10.1561/104.00000122> · preprint: <https://osf.io/z7k3p/download>

Title, verbatim: **"Rest in Peace Post-Earnings Announcement Drift."**

From the abstract:

> "In modern financial markets, stock prices fully reflect earnings surprises on
> the announcement date, leading to the disappearance of post-earnings
> announcement drifts (PEAD). For large stocks, PEAD have been non-existent since
> 2006 but has only disappeared recently for microcap stocks."

Four findings that bear directly on this spec, quoted from the paper:

1. **Analyst-surprise drift, by size and date:** *"since 2006, I show, analyst
   earnings surprises fail to positively predict post-announcement returns over 60
   days for all-but-microcap stocks, and since 2016 for microcap stocks."*
   The 60-day window is Martineau's own — the same window SPEC-PEAD-01 §3.3 claims.

2. **Random-walk (time-series) surprise — this is the spec's §5.1 PRIMARY:**
   *"For all-but-microcap stocks, random-walk earnings surprises only predict
   positively returns following announcements prior to 1990. For microcap stocks,
   random-walk surprises continue to positively predict post-announcement returns;
   **however, the persistence in drifts does not last more than five days.**"*

3. **Horizon collapse, by period:** *"from 1996 to 2005, stock return responses to
   earnings surprises following announcements have generally been positive and
   statistically significant and concentrated in the first ten days across all size
   quintiles. From 2006, the PEAD horizon has shortened... **Since 2011, the only
   suggestive evidence of PEAD is for microcap stocks over the 2 to 5-day
   horizon**... For the remaining daily intervals, the coefficients are not
   statistically significant."*

4. **Where any residual lives:** *"any remaining evidence of PEAD is generally
   driven by microcap stocks with poor information environment (e.g., no analysts
   coverage)."*

Martineau's own methodological recommendation is, uncomfortably, an indictment of
this spec's design: *"researchers should use analyst earnings surprise instead of
random-walk surprises"* — precisely the choice SPEC-PEAD-01 cannot make, because
no analyst-consensus history exists in this program (§5.1, first sentence).

**Caveat, stated fairly:** Martineau is **US (CRSP/Compustat/IBES) only**. It is
not India evidence and must not be cited as such. Its force here is as a prior on
*direction and mechanism* — and as the reason the burden of proof sits on the
India literature, which §2 shows cannot carry it.

### 1.2 Post-publication decay — the general law

- **McLean & Pontiff (2016), *Journal of Finance*** (1,563 citations),
  <https://doi.org/10.1111/jofi.12365>: across 97 published predictors,
  *"Portfolio returns are 26% lower out-of-sample and 58% lower post-publication."*
  Critically for this habitat: *"returns are higher for portfolios concentrated in
  stocks with high idiosyncratic risk and low liquidity"* — i.e. the surviving
  return is where it cannot be traded.
  PEAD is not a marginal case here: it is among the most-published anomalies in
  finance, so the 58% post-publication haircut is a *floor* estimate for it, not a
  ceiling.

- **Chen & Velikov (2022), *JFQA*** (116 citations),
  <https://doi.org/10.1017/s0022109022000874>: net of effective bid–ask spreads,
  post-publication effects, and the post-2000 trading-technology regime,
  *"the average anomaly's expected return is a measly 4 bps per month. The
  strongest anomalies net, at best, 10 bps after controlling for data mining...
  **Expected returns are negligible despite cost mitigations that produce
  impressive net returns in-sample and the omission of additional trading costs,
  like price impact.**"*

- **Harvey, Liu & Zhu (2016), *RFS*** (2,079 citations),
  <https://doi.org/10.1093/rfs/hhv059>: given the extent of data mining in this
  literature, *"A new factor needs to clear a much higher hurdle, with a t-statistic
  greater than 3.0."* Relevant to §7's inference stack — and a reminder that the
  India papers below report t-statistics in the 5–8 range on **gross, untrimmed-
  universe, non-PIT** samples, which is not the same test.

### 1.3 Was there ever a mechanism that would spare India?

**Hung, Li & Wang (2014), *RFS*** (141 citations),
<https://doi.org/10.1093/rfs/hhu092>, "Post-Earnings-Announcement Drift in Global
Markets: Evidence from an Information Shock", finds *"PEAD declines after the
information shock, and this decrease is more pronounced for firms with fewer
concurrent earnings announcements, greater institutional holdings, and lower
limits to arbitrage."*

This cuts **both ways** and should be read honestly. It says PEAD shrinks with
reporting quality, institutional ownership and arbitrage capital — three things
India's ranks 201–1000 have less of than the US. That is the strongest *structural*
argument for an India exception, and it is the argument an advocate for this family
would make. It is also *exactly* the same argument that predicts the effect
concentrates where §5 (capacity/liquidity) bites hardest. It buys a hypothesis, not
a prior.

---

## 2. India-specific evidence — the decisive section

**Six studies were located. Three are substantive. Zero are net of costs. Zero
cover mcap ranks 201–1000. Zero cover the spec's dev window.**

### 2.1 Harshita, Singh & Yadav (2018) — the flagship, and it does not hold

*Theoretical Economics Letters* 8, 3178–3195.
<https://doi.org/10.4236/tel.2018.814197> · PDF:
<https://content.scirp.org/pdf/tel_2018102515432009.pdf>

This is the only India paper that runs a full SUE-sorted decile PEAD design, and
it is the paper any advocate for this family would lead with. Its numbers, read
directly from the PDF:

- **Sample:** 2002 Q4 – 2017 Q3. **Universe:** Nifty 500 (NSE). Data from Ace
  Equity (the same Accord Fintech product named in §2.4 / OPEN ITEM 1).
- **Surprise:** `SUE = (EPS_e − EPS_{e−4}) / P` — a price-scaled seasonal random
  walk, **no drift term, no dispersion scaling.** Note this is *not* the spec's
  §5.1 definition, which adds a drift term and divides by `sd_8`. The two are not
  interchangeable and the India result does not transfer to the spec's estimator.
- **Window:** buy-and-hold market-adjusted return, **day +2 to +64** — the closest
  the literature comes to the spec's `CAR[+1, +60]`.
- **Table 1, time-series average PEAD by SUE decile (P1 = lowest surprise, P10 =
  highest), verbatim:**

  | Period | P1 | P10 | P1−P10 |
  |---|---|---|---|
  | 2002Q4–2017Q3 | (0.014) | **0.034** | 0.048\*\*\* |
  | 2002Q4–2008Q3 | (0.027) | **0.030** | 0.057\*\*\* |
  | 2008Q4–2017Q3 | (0.005) | **0.037** | 0.042\*\*\* |

  (brackets = negative; \*\*\* = 1% significance)

- **Fama–MacBeth slope on coded SUE:** 0.06 (t = 7.80) full period; 0.07 (t = 5.30)
  early; 0.05 (t = 6.06) late. Paper's gloss: *"the stocks with the highest coded
  SUEs generate 6 per cent higher PEAD than the stocks with the lowest coded SUEs
  over 64 days post the announcement."*

**The long leg alone — the only leg a long-only PMS can trade — is +3.4% per
63-session holding period, gross, market-adjusted, full sample; +3.7% in
2008–2017.** At ~4 holding periods per year that is order **13–15%/yr gross excess
return**. Taken at face value this would comfortably clear the spec's §8.1 kill
line. It should not be taken at face value, for five reasons, each verifiable in
the paper itself:

1. **The universe is NOT point-in-time.** Verbatim, §3: *"The scope of the study is
   Nifty 500 companies and the study stretches over a period of 2002 (quarter 4) to
   2017 (quarter 3). **The date of sample selection is 31 March 2014.**"*
   A single 2014 membership snapshot applied to a 2002–2017 sample is survivorship
   bias for the first twelve years and index look-ahead for the last three. This
   program has an entire module (`src/pit_universe.py`) and an announce-date gate
   built to prevent exactly this. **This is the same defect class the program
   itself treats as disqualifying.**

2. **The outcome variable is trimmed.** Verbatim: *"Out of the valid records, 1 per
   cent of the cases are trimmed from both the extremes to exclude outliers"* —
   applied to SUE **and separately to PEAD itself.** Winsorising a *signal* is
   defensible and the spec does it (§5.1). Winsorising the *realised return* is not
   a portfolio calculation: a real book bears its tails. The reported 3.4% is not a
   return anyone could have received.

3. **Zero transaction costs, anywhere in the paper.** The words appear only in the
   literature review, describing other people's work.

4. **The venue is a documented predatory publisher.** *Theoretical Economics
   Letters* is published by Scientific Research Publishing (SCIRP). SCIRP is on
   Beall's list; Cabells' Predatory Reports (2021) describes it as a *"well-known
   predatory publisher"*; a 2022 study notes SCIRP is *"widely known to host 'fake
   journals'"*; the publisher has documented incidents including accepting a
   computer-generated parody paper and listing academics on editorial boards
   without permission (<https://en.wikipedia.org/wiki/Scientific_Research_Publishing>).
   OpenAlex reports the journal is **not in DOAJ**, with a 2-year mean citedness of
   **0.90**. The paper has **4 citations in eight years.**
   *The authors are real academics at IIT Delhi and FORE School of Management, and
   the design is a recognisable replication of Truong (2011) and Chudek et al.
   (2011). The objection is not to them. It is that the paper carries no evidence
   of competent peer review, and the two defects above are precisely what review
   exists to catch.*

5. **The sample ends 2017Q3.** SPEC-PEAD-01 §4 and OPEN ITEM 4 put the binding
   walk-forward floor at the PIT store's announce-safe date, **2018-01-25**.
   **This paper's sample ends 116 days before the spec's walk-forward would begin.
   It provides zero observations of the period the family would actually trade.**

**One genuinely useful result in it, which cuts against the family:** in
sub-period 2 (2008–2017) the interaction `SUE × Size` becomes significant and
negative (coefficient −0.06, t = −2.21), where it was insignificant earlier. The
paper's own reading: *"period 2008-2017 reveals that the anomaly is enhanced for
stocks with lower market capitalization."* The drift migrated down-cap over the
sample — see §4.

**A second result, which cuts the other way and should be recorded:** the
interaction `SUE × Illiquidity` (Amihud) is **insignificant in all three periods**
(t = 1.27, 1.25, 0.37). Within Nifty 500, the India drift was *not* detectably
concentrated in the least liquid names. That is mildly favourable and is the single
strongest India-specific counter to Chordia et al. (§5.1). It is also weak
evidence — insignificance is not absence, Nifty 500 pre-excludes the genuinely
illiquid tail, and the habitat this spec proposes (ranks 201–1000) reaches well
*below* Nifty 500's lower bound.

### 2.2 Sehgal & Bijoy (2015) — legitimate venue, ends 2011

*Vision: The Journal of Business Perspective* (SAGE), 8 citations.
<https://doi.org/10.1177/0972262914564042>

469 companies, **December 2002 – December 2011**, 37 quarterly periods. From the
abstract:

> "Significant post-event abnormal returns are observed for 35 out of 37 quarters
> implying strong rejection of semi strong efficiency with regards to earning
> announcements... **A large part of abnormal returns is observed over an elongated
> event window rather than very close to event date.**"

**This is the best India-specific evidence FOR a long horizon** and it is recorded
as such. It is also the *only* such evidence, it is an event study rather than a
tradeable portfolio, it reports no costs, and its sample ends in 2011.

It carries a second finding the spec must not ignore:

> "Significant pre-event abnormal returns are observed for 32 out of 37 quarters
> which may be an outcome of superior analysis coupled with information asymmetry."

Pre-announcement drift in 32/37 quarters is a **leakage signature**. For a family
whose §0.1 warns that *"a PEAD backtest silently attributes information to a close
at which it was not knowable"*, published evidence of systematic Indian
pre-announcement abnormal returns raises the prior that the §2.5 timestamp audit
finds trouble — and it raises the prior that some of the measured "drift" is
continuation of a pre-event run-up rather than post-event underreaction.
(Martineau addresses this directly for the US and finds the drift decline is *not*
explained by weakening pre-announcement drift; no equivalent India test exists.)

### 2.3 Sen (2009) — peer-reviewed, pre-dates everything relevant

*Journal of Contemporary Accounting & Economics* (Elsevier), 13 citations.
<https://doi.org/10.1016/j.jcae.2008.11.001> — "Earnings surprise and sophisticated
investor preferences in India."

Legitimate venue. **Abstract not retrievable** through OpenAlex, Semantic Scholar
or Unpaywall (publisher-elided; the paper is paywalled). Cited by Harshita et al.
as reporting India PEAD. **Its sample period, universe, horizon and magnitude are
UNVERIFIED in this pass and are not relied on below.** Given publication in 2009 it
cannot cover the spec's window regardless.

### 2.4 Gupta & Dhusia (2021) — the ONLY India study overlapping post-2015, and it is negative

*Trends Economics and Management*, 0 citations, not in DOAJ.
<https://doi.org/10.13164/trends.2021.37.27>

100 NSE-listed firms, **2014–2018**, 1,130 observations. From the abstract:

> "We find that a negative association of abnormal stock returns with surprise in
> accounting earnings announcements. The stocks, which are overvalued or
> undervalued, are properly priced after the earnings announcements. **Our results
> refute the earlier studies evidencing the strong support in favour of market
> inefficiency in the Indian context**, particularly with respect to publicly
> available earnings information... **The Indian stock market tends to be efficient
> with respect to earnings announcements and therefore does not produce excessive
> returns... Superior returns cannot be derived by traders and investors on a
> consistent basis.**"

**Weight this carefully and do not overweight it.** n = 100 firms, obscure venue,
zero citations, and a reported *negative* surprise–return association that is
strange enough to suggest a sign or specification problem rather than a finding.
It is not good evidence that India PEAD is dead.

But note what it is: **the only located India study whose sample reaches past
2015, and it does not support the family.** The correct inference is not "India
PEAD is dead" — it is **"there is no credible India evidence either way after
2015."** That is the state of knowledge, and it is the state that matters, because
the spec's entire walk-forward lives there.

### 2.5 Two adjacent India studies

- **Sehgal & Jain (2015)**, *Asian Academy of Management Journal of Accounting and
  Finance*, "Profitability of Price, Earnings and Revenue Momentum Strategies: The
  Indian Evidence."
  <https://EconPapers.repec.org/RePEc:usm:journl:aamjaf01101_47-84>
  BSE 500 (493 companies), **January 2002 – June 2010**. Finds *"momentum profits
  are persistent in the intermediate horizon (up to six months)"* and that on a
  long-short basis *"earnings momentum strategy is most profitable"* and *"is able
  to subsume price and revenue momentum."* Triple-sorted portfolios reach 2.28% per
  month. **No transaction-cost treatment appears in the abstract; gross-only.**
  Ends 2010. This is the strongest India *magnitude* claim located, and it is a
  long-short, gross, pre-2011 result.

- **Kundu & Banerjee (2021)**, *Cogent Economics & Finance* (open-access, low
  selectivity — flagged), <https://doi.org/10.1080/23322039.2021.1898112>.
  **67 large-cap Indian stocks, 2010–2018.** Finds pre-announcement return premiums
  for all stocks, that *"the market can anticipate whether the firm will announce
  better earnings than the prior period"*, and that **"Post-announcement, stock
  prices adjust to reflect the disclosed earnings information, and only
  non-performers experience a drop in stock prices."**
  Read literally: in large caps 2010–2018, the *positive*-surprise adjustment
  completes at announcement and only the *negative* leg moves afterwards. That is
  Martineau's pattern appearing in Indian data, and it is adverse to a long-only
  positive-surprise book. Large-cap only, so it does not directly speak to ranks
  201–1000 — but SPEC-PEAD-01 §4 lists Top-200 as a sensitivity band, and this is
  the prior for that band.

### 2.6 India institutional features the task asked about

- **Announcement timing is ENDOGENOUS to the surprise.** Prasad & Prabhu (2020),
  *Asian Journal of Accounting Research*,
  <https://doi.org/10.1108/ajar-04-2019-0023>: 30 BSE SENSEX firms, 12 quarters.
  *"the presence of significant earnings surprises is likely to induce firms to
  make earnings announcements after the trading hours"*, and *"The market
  demonstrated a negative response to the earnings announcements made after the
  trading hours."*
  **This is directly load-bearing on SPEC-PEAD-01 §3.1's `C = 15:00` cutoff and
  OPEN ITEM 5.** The timing rule is not orthogonal to the signal: the largest
  surprises self-select into the post-close bucket, so the `C` choice and the
  `C = 15:30` sensitivity will differentially reshape the *tails* of the SUE
  distribution, not just shift a few marginal events. §3.1 currently treats `C` as
  a conservative convention; this evidence says it is closer to a sample-selection
  parameter. It should be recorded against OPEN ITEM 5 whatever the operator
  decides about the family. (Small sample, 30 SENSEX names — treat as a hypothesis
  the §2.5(2) time-of-day histogram must test, not as a fact.)

- **Quarterly reporting mandate, circuit limits, settlement cycle, retail share:**
  **UNVERIFIED in this pass.** No peer-reviewed source was located that
  quantifies these for the dev window in a form usable as a prior. The SEBI LODR
  primary text could not be retrieved (SEBI's site returned only navigation
  chrome to the fetcher; the 45-day Reg 33 figure remains the ASSUMPTION the spec
  already flags at §2.5(5) and SPEC-QFM-01 OPEN ITEM 5). The OpenAlex sweep of
  India retail-participation and circuit-limit literature returned survey-based
  behavioural-finance work with no microstructure content usable here.
  **Do not close OPEN ITEM 5 on the strength of this document.** No guess is
  offered; a disclosed gap is an asset (TRAP 4).

---

## 3. The 60-session horizon — FLAGGED HARD

The task asked for this to be flagged hard if the effect concentrates early. **It
does, and this is the single most damaging finding for the spec as written.**

The spec's claim is `CAR[+1, +60]` (§3.3), entry at the open of `D0+1`, exit at
the close of `D0+60`, with 40- and 90-session sensitivities. The evidence:

| Source | Market | Finding on horizon |
|---|---|---|
| Martineau (2022), CFR — **peer-reviewed** | US | 1996–2005: drift *"concentrated in the first ten days across all size quintiles."* Since 2011: *"the only suggestive evidence of PEAD is for microcap stocks over the **2 to 5-day horizon**"*; all other intervals insignificant. |
| Martineau (2022), random-walk surprise (= spec §5.1 primary) | US | Microcap drift *"does not last more than five days."* Non-microcap: nothing after 1990. |
| Harshita et al. (2018) | India | Measures day +2 to +64 and reports +3.4% on the long leg — **but never decomposes the window.** Cannot distinguish "3.4% earned in days 2–10" from "3.4% earned evenly over 63 days." |
| Sehgal & Bijoy (2015) | India | *"A large part of abnormal returns is observed over an elongated event window rather than very close to event date."* Sample ends 2011. |

**Why this is worse than it first looks.** If the drift is real but concentrated in
days +2 to +10, then a `[+1, +60]` book:

- captures the drift (good), but
- holds the position for a further ~50 sessions of **uncompensated** idiosyncratic
  variance, which is precisely what destroys an information ratio even when the
  expectancy is positive, and
- is measured by a headline (`CAR[+1,+60]`) that **averages the live signal
  together with 50 sessions of noise**, so the spec's own §8.1 test is
  underpowered against its own best case.

The spec already reports `CAR[+1,+5]` and `CAR[+1,+20]` as diagnostics (§3.3), so
the decomposition would be visible — **but only after the single trial is spent.**
There is no pre-registered path by which "the drift was in days 2–10" converts into
a tradeable design, because promoting a shorter hold after seeing the decomposition
is exactly the contamination §0 and TRAP 3 exist to prevent. It would require a
v2 spec and a second trial this family does not have.

**And the shorter horizon is the one this program has already killed.** A 5-day
hold at ~30 concurrent positions is order 4,800%/yr one-way turnover — an order of
magnitude above the §6 budget of 500%/yr, an instant §8.3 kill, and structurally
the same trade that killed the legacy system on friction. SPEC-SRA-01 was assessed
against a 5-day horizon in `analysis/SRA_friction_hurdle.md` and the recommendation
there was KILL NOW.

**So the family is caught between two horizons: the one the modern literature
supports is unaffordable, and the one the spec pins is the one the modern
literature says is empty.**

---

## 4. Mid/small-cap habitat (ranks 201–1000)

Both sides, as asked.

**FOR — the effect is stronger down-cap, and India's ranks 201–1000 are the
low-coverage zone:**

- Harshita et al. (2018), sub-period 2008–2017: `SUE × Size` coefficient −0.06
  (t = −2.21); the paper's reading is *"the anomaly is enhanced for stocks with
  lower market capitalization."* This is India evidence, in the more recent
  sub-period, pointing at this habitat.
- Martineau (2022) locates any residual US PEAD in *"microcap stocks with poor
  information environment (e.g., no analysts coverage)"* — a description that fits
  Indian ranks 201–1000 closely.
- Hung, Li & Wang (2014, RFS): PEAD declines less where institutional holdings are
  lower and limits to arbitrage higher — again, this habitat.

**AGAINST — this is also the zone where anomalies are manufactured, and where
they cannot be traded at size:**

- **Hou, Xue & Zhang (2020)**, cited in Martineau: microcap stocks *"account for
  many of the published anomalies"* despite representing *"only 3.2% of the
  aggregate market capitalization but 60.7% of the number of stocks."* An
  equal-weighted result in this band is the known failure mode of the anomaly
  literature, and SPEC-PEAD-01 §5.4 specifies **equal-weighted** Q5.
- McLean & Pontiff (2016): post-publication survival is highest *"in stocks with
  high idiosyncratic risk and low liquidity"* — i.e. what survives is what cannot
  be arbitraged, which is the same thing as what cannot be traded.
- Chordia et al. (2009) — see §5.1 — makes the trade-off quantitative: the drift
  rises monotonically with illiquidity and so do the costs of harvesting it.
- **Absolute size matters and is under-appreciated here.** Martineau's "microcap"
  cut is the NYSE 20th percentile. Indian ranks 201–1000 sit at absolute market
  caps that map broadly onto — or below — that threshold in USD terms. **This
  habitat is not "mid-cap"; in the frame of the literature that produced the
  residual-PEAD finding, it is the microcap bucket.** That is the bucket where
  Martineau finds a 2-to-5-day effect and nothing longer.
- **No India study covers ranks 201–1000.** Every India study located uses
  Nifty 500 (Harshita), BSE 500 (Sehgal & Jain), 469 large/mid names (Sehgal &
  Bijoy), 100 NSE firms (Gupta & Dhusia), 67 large caps (Kundu & Banerjee) or 30
  SENSEX names (Prasad & Prabhu). **The habitat this spec proposes has never been
  studied for PEAD in India.** Ranks 201–1000 extend materially below Nifty 500's
  floor.

**Net:** the theory says the effect should be here; the measurement literature says
results found here are the least reliable and least tradeable in the entire
anomaly canon; and no one has actually looked here in India.

---

## 5. Net-of-cost evidence — the crux

### 5.1 The international evidence is adverse and directly on point

**Chordia, Goyal, Sadka, Sadka & Shivakumar (2009), *Financial Analysts Journal***,
179 citations, <https://doi.org/10.2469/faj.v65.n4.3> — "Liquidity and the
Post-Earnings-Announcement Drift". Verbatim from the abstract:

> "This study documents that the post-earnings-announcement drift occurs mainly in
> highly illiquid stocks. A trading strategy that goes long high-earnings-surprise
> stocks and short low-earnings-surprise stocks provides a monthly value-weighted
> return of **0.04 percent in the most liquid stocks and 2.43 percent in the most
> illiquid stocks.** The illiquid stocks have high trading costs and high market
> impact costs. By using a multitude of estimates, the study finds that
> **transaction costs account for 70–100 percent of the paper profits** from a
> long–short strategy designed to exploit the earnings momentum anomaly."

and:

> "Previous studies have not taken trading costs into account in the calculation of
> abnormal returns... **this strategy is likely to be unprofitable after adjusting
> for transaction costs.**"

Note their SUE definition is *"the difference between the last available quarterly
earnings and the earnings during that same quarter in the previous year, scaled by
the standard deviation of this difference over the previous eight quarters"* —
**this is SPEC-PEAD-01 §5.1's estimator, minus the drift term.** The closest match
in the literature to the spec's primary signal is the paper that concludes it is
unprofitable after costs.

**This is the same finding, in the same shape, as this program's own central
result.** CLAUDE.md: *"gross alpha was never the constraint; friction was."*
Chordia et al. is that sentence, written about PEAD, in 2009.

Supporting:

- **Ng, Rusticus & Verdi (2008), *JAR***, 250 citations,
  <https://doi.org/10.1111/j.1475-679x.2008.00290.x>: *"the profits of implementing
  the PEAD trading strategy are significantly reduced by transaction costs"* and
  *"firms with higher transaction costs are the ones that provide the higher
  abnormal returns for the PEAD strategy... transaction costs can provide an
  explanation not only for the persistence but also for the existence of PEAD."*
  The mechanism is not incidental — on this account **the drift IS the unharvested
  cost.**
- **Novy-Marx & Velikov (2014/2016)**, <https://doi.org/10.3386/w20721>: *"Most of
  the anomalies... with one-sided monthly turnover lower than 50% continue to
  generate statistically significant net spreads... Few of the strategies with
  higher turnover do."* (The published RFS version could not be retrieved; the
  NBER abstract is quoted. The paper's PEAD-specific turnover classification is
  **unverified** in this pass.)
- **Chen & Velikov (2022), *JFQA*** — §1.2 above; 4 bps/month for the average
  anomaly net, before price impact.

### 5.2 The India evidence is gross-only. Plainly.

**Not one India study located reports a net-of-cost PEAD return.** Harshita et al.
mention transaction costs only when describing other authors' work. Sehgal & Jain
report 2.28%/month gross with no cost treatment. Sehgal & Bijoy report event-study
abnormal returns. Gupta & Dhusia report ERCs.

**Flagged as instructed: the Indian PEAD literature is gross-only, without
exception.** Given this program's history, a gross-only literature is not weak
evidence for a family — it is *no* evidence for the question the family must
answer.

### 5.3 The friction arithmetic — and the honest surprise in it

Computed from `src/costs_in.py` (RULING 5) at the spec's own §6 turnover. Delivery
basis, ₹10L notional per leg, outcome-blind:

| Component | bps |
|---|---|
| Buy leg (STT 10 + stamp 1.5 + exch 0.31 + SEBI 0.01 + GST) | 11.87 |
| Sell leg (STT 10 + exch 0.31 + SEBI 0.01 + GST + DP ₹15.34) | 10.53 |
| **Round-trip statutory** | **22.4** |
| + slippage at the §6 floor, 0.10%/side | 42.4 |
| + slippage at the §6 stress case, 0.20%/side | 62.4 |

At ~4 book replacements/year (the 60-session hold, §6's own structural figure):

- **at the 0.10%/side floor: 1.70%/yr**
- **at the 0.20%/side stress case: 2.50%/yr**

Against the literature's India long-leg gross figure (Harshita et al., P10 = 3.4%
per 63 sessions ⇒ order 13–15%/yr gross excess), **friction consumes only ~11–18%
of the gross. The family clears §8.1 on cost arithmetic with room to spare.**

**This must be said plainly, because it is the opposite of SPEC-SRA-01's result and
it would be dishonest to bury it: a 60-session hold is a genuinely low-turnover
design, and this program's characteristic killer does not kill it.** The §6 budget
of 500%/yr is well-chosen and the structural ~400% sits comfortably inside it.

Three things that arithmetic does **not** cover, and they are where the risk is:

1. **Price impact, which Chordia et al. say is the binding term** — and their
   result is that impact plus spread eats 70–100% of PEAD profits *in the US*, in
   the illiquid decile. `costs_in.py` models statutory and brokerage lines; the
   slippage parameter is a flat per-side assumption, not a footprint model. At
   ₹100 Cr in ranks 201–1000, **buying on post-earnings volume days** (§6's own
   stated worst execution environment), the realised figure is not 0.10%/side and
   nobody in this program has measured what it is. §8's capacity clause is the
   real test and the spec says so.
2. **The 3.4% input is the compromised number** from §2.1 — non-PIT universe,
   trimmed outcome, predatory venue, sample ending before the walk-forward starts.
   The arithmetic above is only as good as its input, and its input does not
   survive scrutiny.
3. **It assumes the drift is there at all.** Cost is the second question. §1 and §3
   are about the first.

---

## 6. Surprise definition (spec §5.1 vs §5.2)

The task's question is the sharpest one in this review, and the literature answers
it cleanly and against the spec.

**Livnat & Mendenhall (2006), *Journal of Accounting Research***, 741 citations,
<https://doi.org/10.1111/j.1475-679x.2006.00196.x>. Verbatim:

> "We show that **the drift is significantly larger when defining the earnings
> surprise using analysts' forecasts and actual earnings from I/B/E/S than when
> using a time series model based on Compustat earnings data.** Neither Compustat's
> policy of restating earnings nor the inclusion of 'special items' in reported
> earnings contribute significantly to the disparity in drift magnitudes."

Martineau (2022) sharpens it into a recommendation and a decay ordering:

> "researchers should use analyst earnings surprise instead of random-walk
> surprises because analyst surprises better explain price reaction to earnings
> news and minimize the effect of microcap stocks. When the analysis is conducted
> using random-walk surprises, it increases the number of earnings announcements
> significantly, but this increase primarily comprises of microcap stocks with no
> analyst following. Consequently, OLS regressions tend to put more weights on
> outliers with volatile returns."

**Consequences for this spec, stated exactly:**

- **§5.1 (SUE via seasonal random walk) is the surprise definition the literature
  identifies as WEAKER, NOISIER, and — per Martineau — the one that stopped working
  first.** It is not a neutral choice; it is the choice forced by data availability.
  §5.1's opening sentence concedes exactly this: *"No analyst-consensus history
  exists in this program."*
- **The task's specific question — analyst vs time-series in sparse-coverage
  markets — has no direct answer in the literature.** Livnat & Mendenhall and
  Martineau both work in a market with dense I/B/E/S coverage; they compare the two
  estimators where both are available. **Nobody has tested whether time-series SUE
  works better in a market where analyst coverage does not exist**, which is the
  Indian mid/small-cap case. This is a genuine gap, and it is the one place where a
  case for this family could honestly be built. It is a hypothesis with no evidence
  behind it, not a prior.
- **Martineau's warning about OLS weighting applies directly to §5.4.** Random-walk
  surprises in a low-coverage habitat put weight on volatile microcap outliers.
  §5.1's 1%/99% cross-sectional winsorisation is the right instinct and is
  pre-committed — good. But winsorising the *signal* does not fix a habitat where
  the *outcome* distribution is dominated by a few violent names, and §3.4's
  freeze-at-0% convention for missing prices suppresses exactly those moves (the
  spec already flags this, correctly, as adverse for this family).
- **§5.2 (price-based CAR-surprise) is not a rescue.** It requires no fundamentals
  corpus, which is its attraction — but it is not the analyst-forecast surprise the
  literature prefers. It is a *third* estimator whose India evidence base is
  empty. Promoting it would trade a signal with weak evidence for one with none.

---

## 7. Scorecard against the three criteria the task specified

Judging on **currency**, **India-specificity** and **net-of-cost**, not volume:

| Criterion | Finding | Verdict |
|---|---|---|
| **CURRENT** | Zero studies, India or otherwise, support a 60-session drift under a time-series surprise after ~2011. The only India study reaching past 2015 (2014–2018, n=100) finds no exploitable drift. **No India study covers 2018–2024 — the spec's entire walk-forward window.** | **FAIL** |
| **INDIA-SPECIFIC** | Three substantive studies. Best-known is in a predatory-publisher journal with a non-PIT universe and a trimmed outcome variable, ending 2017Q3. Next ends 2011. Next is 2009 and unverifiable. **Zero cover ranks 201–1000.** | **FAIL** |
| **NET-OF-COST** | **Zero India studies of any kind report net returns.** The on-point international paper (Chordia et al. 2009, FAJ) concludes costs consume 70–100% of PEAD profits and the strategy *"is likely to be unprofitable."* | **FAIL** |

For contrast, SPEC-52WH-01 was advanced on Raju (2023) — a single, current,
directly-on-point paper that was deep-read and recorded in `research.md`, and whose
central finding (the long leg does not beat the index) *reframed the family*. **The
PEAD literature offers no India equivalent.** The comparison is the right one to
make, because it shows this program has a working standard for what a prior looks
like, and this family does not meet it.

---

## 8. VERDICT

# (C) NO CREDIBLE MODERN INDIA PRIOR — recommend releasing shadow slot 2.

Not (B). (B) would require naming caveats that a competent execution could carry.
The defects here are not caveats — they are the absence of the evidence, in all
three dimensions that matter, and no amount of execution quality manufactures a
prior that does not exist.

**The reasoning, compressed:**

1. The spec claims `CAR[+1,+60]`. The best modern evidence says that horizon is
   empty under the spec's own primary surprise definition, and that whatever
   remains lives in days +2 to +5 — a horizon this program has already killed on
   friction, and one the spec cannot pivot to without a v2 and a second trial it
   does not have (§3).
2. The India evidence cannot arbitrate. Its flagship is unpublishable by this
   program's own PIT standards and appears in a journal from a documented predatory
   publisher; its sample ends before the walk-forward begins; the only study
   overlapping the dev window finds nothing; and **no India study has ever looked
   at ranks 201–1000** (§2).
3. Not one India study — not one — reports a net-of-cost result, and the
   international paper closest to the spec's own estimator concludes the strategy is
   unprofitable after costs (§5).

**What this verdict does NOT rest on, and the operator should know it:** it does
not rest on friction. The 60-session hold is genuinely low-turnover; at the §6
slippage floor the statutory stack costs ~1.70%/yr against an order-13%/yr gross
literature figure. **If the drift were real and current at this horizon in this
habitat, this family would be affordable.** The case fails on whether the drift is
real and current, not on whether it could be paid for. That distinction should be
recorded in `DECISIONS.md`, because it is the difference between "wrong design" and
"no evidence", and only the second is what happened here.

### 8.1 What releasing the slot buys

Per SPEC-PEAD-01 §11 and CLAUDE.md's queue, releasing slot 2 avoids committing to:

- ~2–4 days of BSE `DissemDT` ingest (OPEN ITEM 1, **ToU-BLOCKED**),
- ~1–2 days of hand-mapping BSE's 96 subcategories into §2.3.1 — which does not
  exist and without which the spec **cannot be frozen** (OPEN ITEM 2),
- a PIT fundamentals corpus with **no named admissible source** (OPEN ITEM 3,
  shared with SPEC-QFM-01),
- and a walk-forward whose start date is **overdetermined and undecided** across
  three competing floors, with §8.4's 500-event support requirement unverified
  against a ~6.5-year window in a habitat currently defect-narrowed to 719 names
  (OPEN ITEMS 4, 7).

Per CLAUDE.md, AG-01 and 52WH are both queued behind the 2-shadow cap. Releasing
slot 2 promotes one of them. **The RULING 7 trial economics apply: trials are
cheap, slots are scarce.** This is a slot decision, and the slot is better spent.

### 8.2 The one honest override path

If the operator wishes to keep the slot, there is exactly one defensible argument
and it should be stated as the hypothesis it is, not dressed as a prior:

> *Nobody has tested whether a time-series earnings surprise predicts drift in a
> market segment where analyst coverage does not exist. The literature's preference
> for analyst surprises was established where both estimators were available. Indian
> ranks 201–1000 are a genuine out-of-sample setting for that question, and Hung,
> Li & Wang (2014) supplies a mechanism — low institutional holdings, high limits to
> arbitrage — under which drift would decay more slowly there.*

That is a real argument. It is also a **bet on an untested mechanism in the exact
habitat the literature identifies as anomaly-manufacturing**, with a
gross-only evidence base, at a horizon the modern evidence says is empty, and it
would cost the four blocked items in §8.1 before a single number appeared.

**If it is taken, two things should change before freeze, and both are free:**

1. **Do the §0.1 limitation sweep first** — five Indian journals plus SSRN,
   2018–2024. If it finds nothing (expected), that null is itself worth recording
   against OPEN ITEM 9 and strengthens the kill.
2. **Reconsider the §3.3 horizon before it is frozen, not after.** A `[+1,+60]`
   headline is the one the literature least supports. Since §3.3's sensitivities
   (40 and 90 sessions) both sit on the *long* side, the grid contains no variant
   at the horizon the modern evidence actually favours — and adding one *after*
   the trial is contamination. This is fixable now, at zero cost, and it is the
   single highest-value edit available to this draft. Note the trade-off honestly:
   a short-horizon variant busts the §6 turnover budget and dies at §8.3, which is
   itself informative and should be reasoned through in the spec rather than
   discovered.

### 8.3 Findings worth keeping regardless of the verdict

Three results from this pass survive the family and belong in the record:

1. **Announcement timing is endogenous to surprise magnitude in India** (Prasad &
   Prabhu 2020) — bears on OPEN ITEM 5 and on any future India event-study family.
   `C = 15:00` is closer to a sample-selection parameter than a convention.
2. **Systematic Indian pre-announcement abnormal returns in 32/37 quarters**
   (Sehgal & Bijoy 2015) — a leakage prior that any India event study in this
   program should carry into its timestamp audit.
3. **Ace Equity (Accord Fintech) is the data source Harshita et al. used** for
   Nifty 500 quarterly EPS 2002–2017. That is independent, third confirmation of
   the vendor already surfaced twice for BSE announcements and MCX
   (`analysis/accord_fintech_enquiry.md`), and it is direct evidence the vendor
   serves the PIT-fundamentals need in SPEC-QFM-01 OPEN ITEM 2. **One enquiry now
   touches four blocked items across three families.**

---

## 9. Source table

| # | Work | Type | URL |
|---|---|---|---|
| 1 | Martineau (2022), "Rest in Peace Post-Earnings Announcement Drift", *Critical Finance Review* | **Peer-reviewed** | <https://doi.org/10.1561/104.00000122> · preprint <https://osf.io/z7k3p/download> |
| 2 | Chordia, Goyal, Sadka, Sadka & Shivakumar (2009), "Liquidity and the PEAD", *Financial Analysts Journal* | **Peer-reviewed** | <https://doi.org/10.2469/faj.v65.n4.3> |
| 3 | Ng, Rusticus & Verdi (2008), "Implications of Transaction Costs for the PEAD", *JAR* | **Peer-reviewed** | <https://doi.org/10.1111/j.1475-679x.2008.00290.x> |
| 4 | Livnat & Mendenhall (2006), "Comparing the PEAD for Surprises Calculated from Analyst and Time Series Forecasts", *JAR* | **Peer-reviewed** | <https://doi.org/10.1111/j.1475-679x.2006.00196.x> |
| 5 | McLean & Pontiff (2016), "Does Academic Research Destroy Stock Return Predictability?", *Journal of Finance* | **Peer-reviewed** | <https://doi.org/10.1111/jofi.12365> |
| 6 | Chen & Velikov (2022), "Zeroing In on the Expected Returns of Anomalies", *JFQA* | **Peer-reviewed** | <https://doi.org/10.1017/s0022109022000874> |
| 7 | Harvey, Liu & Zhu (2016), "…and the Cross-Section of Expected Returns", *RFS* | **Peer-reviewed** | <https://doi.org/10.1093/rfs/hhv059> |
| 8 | Hung, Li & Wang (2014), "PEAD in Global Markets", *RFS* | **Peer-reviewed** | <https://doi.org/10.1093/rfs/hhu092> |
| 9 | Novy-Marx & Velikov (2014), "A Taxonomy of Anomalies and their Trading Costs", NBER w20721 | Working paper | <https://doi.org/10.3386/w20721> |
| 10 | Fink (2020), "A review of the PEAD", *JBEF* | **Peer-reviewed** (survey) | <https://doi.org/10.1016/j.jbef.2020.100446> |
| 11 | **Harshita, Singh & Yadav (2018)**, "PEAD Anomaly in India", *Theoretical Economics Letters* | ⚠️ **PREDATORY PUBLISHER (SCIRP)** — not DOAJ, 4 citations | <https://doi.org/10.4236/tel.2018.814197> |
| 12 | Sehgal & Bijoy (2015), "Stock Price Reactions to Earnings Announcements: Evidence from India", *Vision* (SAGE) | Peer-reviewed, low impact | <https://doi.org/10.1177/0972262914564042> |
| 13 | Sen (2009), "Earnings surprise and sophisticated investor preferences in India", *JCAE* | Peer-reviewed — **content UNVERIFIED (paywalled)** | <https://doi.org/10.1016/j.jcae.2008.11.001> |
| 14 | Gupta & Dhusia (2021), "PEAD and Value-Glamour Anomalies in NSE Listed Firms", *Trends Economics and Management* | ⚠️ Obscure, not DOAJ, 0 citations | <https://doi.org/10.13164/trends.2021.37.27> |
| 15 | Sehgal & Jain (2015), "Profitability of Price, Earnings and Revenue Momentum Strategies: The Indian Evidence", *AAMJAF* | Peer-reviewed, low impact | <https://EconPapers.repec.org/RePEc:usm:journl:aamjaf01101_47-84> |
| 16 | Kundu & Banerjee (2021), "Predictability of earnings and its impact on stock returns: Evidence from India", *Cogent Economics & Finance* | ⚠️ Low-selectivity open access | <https://doi.org/10.1080/23322039.2021.1898112> |
| 17 | Prasad & Prabhu (2020), "Does earnings surprise determine the timing of the earnings announcement?", *AJAR* | Peer-reviewed, low impact | <https://doi.org/10.1108/ajar-04-2019-0023> |
| 18 | SCIRP publisher assessment (Beall's list, Cabells Predatory Reports 2021) | Reference | <https://en.wikipedia.org/wiki/Scientific_Research_Publishing> |

**No vendor or practitioner marketing material was used in this review.** Every
source above is an academic publication or a publisher-assessment reference.
Items 11, 14 and 16 are academic in form but flagged for venue quality; item 13 is
peer-reviewed but its content could not be retrieved and is not relied upon.

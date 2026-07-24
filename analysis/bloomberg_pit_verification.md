# Bloomberg PIT Fundamentals — Web-Verification Pass (Four Open Questions)

**Status: outcome-blind scoping. No trial spent, no register write, no spec edit.
No vendor was contacted, no form filled, no sales flow triggered. No repo data
touched. No exchange site (NSE/BSE/MCX) was scraped.** Free scoping under
`CONTAMINATION_POLICY.md` AMENDMENT A.

**Written:** 2026-07-23.
**Feeds:** `analysis/QFM_fundamentals_scope.md`; `governance/specs/SPEC-QFM-01.md`
OPEN ITEMS 2 (fundamentals corpus) and 3 (announce-date provenance);
`analysis/accord_fintech_enquiry.md`.

**Source tiers** (per `analysis/QFM_literature_prior.md`, plus one):
- **[PR]** peer-reviewed · **[WP]** working paper / preprint
- **[VM]** vendor marketing — coverage CLAIMS, never verified coverage
- **[GOV]** procurement / tender / FOI / government contract record — real,
  dated transaction evidence; the highest-value tier for pricing

**TRAP 6 discipline:** for every claim below the status is one of
**VERIFIED ABSENT** / **CLAIMED PRESENT, UNVERIFIED** / **COULD NOT DETERMINE**.
Nothing is invented (TRAP 4); a disclosed gap stays disclosed.

---

## STATUS OF THE FOUR QUESTIONS

| # | Question | Status |
|---|---|---|
| 1 | India small-cap (AMFI ranks 201–1000) depth of Bloomberg PIT/COFI back to ~2015–16, with announce timestamps | **OPEN** — nothing about COFI coverage is publicly retrievable; the dataset catalog is behind a login (verified 401). Sales enquiry required. |
| 2 | Real Data License / COFI pricing calibration points from public procurement | **NARROWED** — 6 dated US federal DL awards + 1 EU award naming the DL request-tier structure. No COFI/bulk-PIT price public anywhere found. |
| 3 | Consolidated-vs-standalone and Ind-AS handling in Bloomberg's India fundamentals model | **OPEN** — no Bloomberg methodology document publicly retrievable this pass (bloomberg.com 403s non-browser clients; no mirror reachable without search). |
| 4 | Bloomberg vs Prowess/CMIE (and Capitaline / ACE Equity) for Indian PIT fundamentals | **NARROWED (major)** — Prowess dx has an IMMUTABLE VINTAGE architecture (CMIE's own words), per-period "Date signed" fields and a Board-Meetings announcement table in its official 13,648-field indicator list — but is ACADEMIC-ONLY by CMIE's own brochure. ACE Equity: still no PIT claim. |

*(Table updated as evidence lands; each question's section below ends with a
one-line status: CLOSED / NARROWED / OPEN.)*

**Method constraint disclosed up front:** this session's web-SEARCH budget was
already exhausted (200/200 calls consumed by the prior pass) before this pass
issued its first query. Everything below was therefore gathered by DIRECT
retrieval from named primary sources — public procurement APIs (USAspending,
EU TED), official notice XML, and vendor documentation pages — not by search
engines. Consequence: discovery-type questions ("does any academic paper use
Bloomberg PIT data for India?") could not be swept and are marked COULD NOT
DETERMINE rather than answered thinly. No search-engine workaround was used.

---

## Q2 — REAL DATA LICENSE PRICING: [GOV] CALIBRATION POINTS

All figures below are from official procurement records — actual awarded
contracts, not list prices. **None of them is a COFI price and none is
extrapolated to one.** They calibrate what real institutions pay for Bloomberg
Data License access at stated scopes.

### 2.1 US federal awards (USAspending.gov API, retrieved 2026-07-23) [GOV]

| Award ID | Buyer | Amount (USD) | Period | What it covered (contract description, verbatim scope) |
|---|---|---|---|---|
| TCC14HQP0100 | Dept. of the Treasury | $24,061.58 | 2014-04 → 2016-03 (24 mo) | "Bloomberg Data License Request Builder license renewal" |
| TCC16HQP0072 | Dept. of the Treasury | $28,000.00 | 2016-04 → 2018-03 (24 mo) | "Bloomberg Data License Request Builder" |
| DEEI0003153 | Dept. of Energy | $24,000.00 | 2017-03 → 2019-03 (24 mo) | "Bloomberg Data License" |
| 2031JW18P00058 | Dept. of the Treasury | $20,000.00 | 2018-04 → 2020-03 (24 mo) | "Bloomberg Data License Request Builder" |
| 20341518P00002 | Treasury / OFR | $24,000.00 | 2018-05 → 2020-04 (24 mo) | "Bloomberg Data License for OFR" |
| 89303019PEI000036 | Dept. of Energy / EIA | $15,100.00 | 2019-07 → 2021-04 (~21 mo) | "Bloomberg Data Licenses renewal for the U.S. Energy Information Administration" |

Reading: small-scope, request-based DL subscriptions (Request Builder = the
per-request DL front end) ran **~$10–14k/yr** at US agencies in 2014–2021.
These are NOT bulk-history or PIT-fundamentals licenses; they anchor the
BOTTOM of the DL price range.

### 2.2 EU TED notices (api.ted.europa.eu, retrieved 2026-07-23) [GOV]

| Notice | Buyer | Value | Period | Scope (from notice XML, verbatim where quoted) |
|---|---|---|---|---|
| 746641-2024 / 761919-2024 | SID banka (Slovenian state development bank) | **USD 236,640** (currencyID=USD in the notice XML) | Dec 2024 award | "Subscription and license agreement for the 'Bloomberg Terminal®' and 'Bloomberg Data License'" — bundle, not decomposed |
| 163728-2023 / 582658-2023 | UKNF (Polish Financial Supervision Authority) | **PLN 2,218,500.22** | Mar/Sep 2023, 24 months | Bloomberg Terminals + Data Licence (bundle) |
| 360373-2026 | UKNF | **PLN 2,609,525.60** total (base PLN 2,392,946.15 + option PLN 216,579.45) | 24 months from 2025-09-11 | Base: **7 Bloomberg Professional Service licences (Terminals)** + "dostępu do danych Bloomberg Data License … na poziomie **1001–2500 zapytań/miesiąc**" (DL at the 1,001–2,500 requests/month tier). Option: 1 additional Terminal |
| 270607-2019 | Single Resolution Board (EU) | not stated in the list result | 2016–2020 amendment | "Financial Market data Sources and Trading Platform" — mentions Bloomberg DL among market-data sources |

The UKNF 2026 notice is the single most informative public record found: it
names the DL **request-tier** (1,001–2,500 requests/month) alongside a known
terminal count, i.e. Bloomberg prices DL by request volume bands. The bundle
is not decomposed publicly, so no DL-only figure can be extracted without
inventing a terminal price — **not done here** (TRAP 4).

### 2.3 Sources attempted and not obtained

- **India GeM portal**: award search is a JS application with no public API
  found; not retrievable this pass without search-engine discovery of
  individual award PDFs. COULD NOT DETERMINE.
- **UK Contracts Finder**: the OCDS API's keyword parameter is not honoured
  (returns the unfiltered notice stream — verified 2026-07-23, TRAP 6-style
  silent failure: HTTP 200, 100 plausible rows, zero of them relevant); no
  Bloomberg notice retrievable without a working keyword search.
- **WhatDoTheyKnow (UK FOI)**: HTTP 403 to non-browser clients.
- **RBI / ECB / BoE procurement**: not reachable without search discovery of
  the specific notice/annual-account pages.

**Q2 STATUS: NARROWED** — six dated US federal DL awards (~$10–14k/yr,
request-based scope) and one EU award naming the DL request-tier structure
(UKNF, PLN 2.61M / 24 mo for 7 terminals + DL at 1,001–2,500 req/mo) are on
record. No public price for COFI or any bulk PIT-fundamentals DL product was
found; that number still requires the sales enquiry.

---
## Q1 — BLOOMBERG PIT/COFI DEPTH FOR INDIA SMALL-CAPS

**What was attempted (all direct retrieval, 2026-07-23/24):**

1. **data.bloomberg.com** (the "Enterprise Access Point", where the COFI
   catalog entry lives). The site is an Angular SPA; its catalog API
   (`/api/catalogs/bbg/products/`, `/api/web/catalogs/bbg/products/`) returns
   **HTTP 401 `{"isLoggedIn":false}`** to unauthenticated clients — VERIFIED.
   The browsable dataset catalog, field lists and coverage notes are entirely
   behind an EAP account. Creating one is a registration/sales flow, which
   this pass was prohibited from triggering.
2. **Wayback Machine CDX sweep of data.bloomberg.com** (468 unique archived
   URLs): **zero** URLs matching `cofi`, `financial`, or `fundament`. The
   archived corpus is the SPA shell + API route patterns only. VERIFIED
   ABSENT from the public archive — which is evidence about the ARCHIVE, not
   about COFI (TRAP 6: absence of a coverage file ≠ absence of coverage).
3. **bloomberg.com/professional** marketing pages: HTTP 403 to WebFetch and
   curl (bot protection). The 2024-06-01 Wayback capture of
   `/professional/products/data/` ("Enterprise Data") retrieved and read —
   it links only category pages (reference, pricing, regulatory, ESG, funds,
   event-driven feeds); its only "India" occurrence is a country dropdown.
   No fundamentals coverage statement, no COFI mention on the archived page.
4. **2024 press-release archive sweep** (Wayback CDX, 1,177 archived
   `bloomberg.com/company/press*` URLs for 2024): no COFI/Company-Financials
   launch release surfaced under the keywords tried (launch/dataset/
   history/company/financial/fundament/point). The prior pass's 2024-04-09
   launch date was NOT re-verified this pass (nor contradicted).
5. **Academic usage of Bloomberg PIT data for India** (SSRN/Scholar sweep):
   NOT POSSIBLE without the search budget. COULD NOT DETERMINE.

**What this means for the "5,000 major-index companies same-day, others
within 24h of filing" claim:** it could not be re-verified, attributed to a
specific dataset/region, or tested against AMFI ranks 201–1000. It remains
[VM] CLAIMED PRESENT, UNVERIFIED — and note the shape of the claim itself:
AMFI 201–1000 names are precisely the "others" bucket, so even taking the
claim at face value, the timestamp quality for THIS habitat is the weaker
tier of the claim.

**Q1 STATUS: OPEN.** The public internet does not establish (or refute)
Bloomberg PIT coverage of Indian names at AMFI ranks 201–1000 back to
~2015–16. Every road terminates at the EAP login or the sales desk. This
KEEPS the sales-enquiry requirement honest: the enquiry must ask for a
machine-readable coverage file for India by mcap rank band × year × field
× announce-timestamp availability, not a verbal assurance.

---

## Q3 — CONSOLIDATED/STANDALONE AND IND-AS IN BLOOMBERG'S MODEL

**Attempted:** Bloomberg fundamentals methodology (BFAM) documents,
`bloomberg.com/professional` documentation, and archived copies. All
bloomberg.com paths 403 non-browser clients; no methodology PDF or library
guide was reachable by direct URL; the literature could not be swept
(search budget). Nothing found either way on how Bloomberg sequences
standalone vs consolidated for Indian quarterly filings or handles the
2016-17 Ind-AS transition. COULD NOT DETERMINE.

**Contrast established on the CMIE side (relevant as the comparison
baseline for §4.5):** CMIE's official Prowess dx table list SEPARATES the
bases structurally rather than merging them — distinct tables for
"Standalone" vs "Consolidated" annual and interim quarterly statements, and
SEPARATE "Annual Financial Statements - Ind AS" tables (standalone min date
31 Mar 2014; consolidated min date 31 Mar 2011) alongside the pre-Ind-AS
tables. Source: cmie.com contents-overview page, retrieved 2026-07-23 [VM].
That is exactly the shape SPEC-QFM-01 §4.5 wants recorded per
(symbol, fiscal_period). Whether Bloomberg's model preserves or collapses
this distinction for India is the question the enquiry must ask.

**Q3 STATUS: OPEN.** Public internet cannot answer for Bloomberg; the
question now has a concrete formulation ("do you preserve the
standalone/consolidated/Ind-AS basis per period as CMIE does, or normalise
across it?") for the sales enquiry.

---

## Q4 — BLOOMBERG vs PROWESS/CMIE (AND ACE EQUITY) FOR INDIAN PIT FUNDAMENTALS

### 4.1 THE FINDING OF THIS PASS: Prowess dx is built on immutable vintages

From CMIE's own vintage-release announcement (prowessdx.cmie.com,
announcement dated 01 Apr 2026, retrieved 2026-07-23) [VM]:

> "CMIE is pleased to announce the release of March, 2026 Vintage of
> Prowess Dx. This is the thirty-eighth Vintage of ProwessDx since it was
> launched. In a calendar year, there will be two vintages, released on
> 31st March and 30th September. A new Vintage includes data for the period
> since the release of the previous Vintages. **Contents of a Vintage are
> not changed once they are created. Data is neither added, deleted nor
> modified. The data remains unchanged for all times to come.** The
> December 2025 Vintage contained data for 56,746 companies. A total of 283
> new companies have been added in the March 2026 Vintage, thereby raising
> the total tally of companies in ProwessDx to 57,029."

The official brochure (cmie.com, PDF, retrieved 2026-07-23) [VM] states:
"Database vintages ensure replication of downloads."

What this IS: an as-of-snapshot architecture. 38 frozen database states
exist; recent release cadence observed from the announcements list is
~3/year through 2025 (Mar/Sep/Dec releases visible: Dec 2024, Mar 2025,
Sep 2025, Dec 2025, Mar 2026) moving to a stated 2/year. Comparing a value
for the same (company, fiscal_period, field) ACROSS vintages identifies
restatements at vintage grain — structurally the "restatements as new
rows, originals preserved" property of §2.3, at semi-annual resolution.

What this IS NOT: per-announcement point-in-time. Within one vintage,
whether a value is as-first-reported or latest-restated-as-of-the-vintage
is NOT stated publicly — COULD NOT DETERMINE. And whether CMIE will sell
HISTORICAL vintages (the ~2015–2024 dev window needs the back catalog, not
the current snapshot) is not stated publicly. Both are enquiry questions.

### 4.2 Announce-date evidence — the official indicator list

CMIE publishes the full Prowess dx indicator list as a spreadsheet
(cmie.com `wlstind` endpoint, 13,648 field rows, retrieved 2026-07-23)
[VM]. Scanned exhaustively for announcement/date fields:

- **Interim Quarterly Financial Statements** (standalone table: min date
  31 Jan 1995, 344 indicators; consolidated: 30 Jun 1999, 270): carry
  `ntrm_date` (period date), **`ntrm_date_signed` ("Date signed")**,
  `ntrm_source`, `interim_info_type`. NO explicit
  "result announcement date" field.
- **Board Meetings table** (min date 15 Jul 1996): `bm_date`,
  `bm_purpose`, `bm_abbv_purpose`, **`bm_announcement_date`**,
  `bm_announcement_exch`. Indian quarterly results are approved at board
  meetings, so (meeting date, purpose="results") is a candidate date-only
  announcement clock.
- Also: `div_announcement_date` (Dividend Declarations),
  `date_of_announcement` (Changes in Capital).

**Honest labelling:** these fields are CLAIMED PRESENT (they are in the
official field list — stronger than marketing copy, still vendor-supplied)
but their SEMANTICS are UNVERIFIED: "Date signed" may be the board
signature date (≈ the LODR announcement day) or something weaker;
`bm_announcement_date` may be the date the meeting was announced IN
ADVANCE, not the date results were disseminated. §2.5(2)'s lag-distribution
test is exactly the right instrument to validate whichever field is
offered — on sample data, before any licence.

### 4.3 Coverage, sourcing, licensing

- Coverage [VM]: 57,029 companies (Mar 2026 vintage); "time-series since
  1989"; quarterly statements of listed companies since 1995 (standalone);
  "database does not suffer from survival bias as we do not drop
  companies"; sourced from MCA filings + stock exchanges, methodically
  standardised.
- **Licensing — the catch (brochure, verbatim):** "The Prowess dx service
  is available only to educational institutions and not-for-profit
  research organisations." alpha-research is a commercial program
  (PMS → AIF). **Prowess dx as such is very likely NOT licensable to this
  program.** The commercial deliveries of the same underlying database are
  Prowess / Prowess IQ / PACE — whose public pages make NO vintage
  guarantee ("updated continuously", which is the OPPOSITE property).
  Whether CMIE sells vintage-structured data commercially is an enquiry
  question, and the single most important one on the CMIE side.
- Pricing: no public price for any Prowess product (subscription pages
  302-redirect to a login). COULD NOT DETERMINE.

### 4.4 ACE Equity (Accord Fintech) — re-verified

The ACE Equity Nxt page (accordfintech.com, retrieved 2026-07-23) [VM]
makes NO as-reported, announce-dated, or point-in-time claim; history
depth in years is not published; restatements are not discussed. Its
strongest data-provenance statement is "Balance sheet, Profit and loss,
Cash Flow data fields are directly linked to Annual report of the
company" — which, as `analysis/accord_fintech_enquiry.md` §C already
flags, suggests latest-annual-report values, i.e. possibly NOT PIT.
Unchanged; the question stays in the enquiry pack.

### 4.5 Published Bloomberg-vs-Prowess comparisons

Could not be swept without the search budget. COULD NOT DETERMINE.

**Q4 STATUS: NARROWED (major).** Prowess dx is now the first DOCUMENTED
India-native source whose architecture (immutable vintages + per-period
signed/announcement date fields) structurally matches SPEC-QFM-01 §2.3's
admissibility requirements — with three named holes: within-vintage
as-reported semantics, back-vintage availability, and the academic-only
licence wall. ACE Equity remains PIT-unverified. The Bloomberg-vs-Prowess
accuracy question remains open.

---

## VERDICT — DOES THE SALES-ENQUIRY CONCLUSION CHANGE?

**No — it is confirmed, and it gains a third leg.**

1. **Bloomberg enquiry still required** (Q1, Q3 both OPEN): the public
   internet reveals literally nothing about COFI's India small-cap depth,
   announce-timestamp coverage, or basis handling. Ask for: a coverage
   file for India cut by mcap band × year × field × timestamp
   availability; the standalone/consolidated/Ind-AS basis flag per period;
   and a DL/COFI price for a stored-research-corpus licence.
2. **Accord Fintech enquiry still required** (Q4.4 unchanged): the PIT
   question for ACE Equity is answerable only by the vendor.
3. **NEW: a CMIE enquiry belongs alongside them.** Prowess dx's vintage
   architecture is the only publicly documented restatement-vintage
   structure among the India-native vendors — but the academic-only wall
   means the operative questions are commercial: (a) is vintage-structured
   delivery available under a commercial licence; (b) are HISTORICAL
   vintages (~2015 onward) purchasable; (c) are within-vintage quarterly
   values as-first-reported or restated; (d) what exactly do
   `ntrm_date_signed` and `bm_announcement_date` record, validated on a
   sample against BSE dissemination times before any money moves.

Pricing calibration (Q2) is banked: request-based DL runs ~$10–14k/yr
[GOV, US federal, 2014–2021]; an EU supervisor's 7-terminal + DL
(1,001–2,500 req/mo) bundle runs PLN 2.61M / 24 mo [GOV, 2026]. Nothing
public prices COFI; treat any quoted number against these anchors.

*Retrieval log: all URLs fetched 2026-07-23/24; raw responses in the
session scratchpad (not repo data). No exchange site touched; no vendor
contacted; no form submitted.*

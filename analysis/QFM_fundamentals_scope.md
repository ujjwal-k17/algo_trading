# SPEC-QFM-01 — PIT Fundamentals Dependency: Gap Confirmation and Source Scope

**Status:** Scoping note. Outcome-blind. No data was acquired, downloaded, or scraped in
producing this document — sources were assessed from public documentation, pricing pages
and terms pages only. Nothing here has touched repo outcome data. Under
`CONTAMINATION_POLICY.md` this is a free, outcome-blind diagnostic; it is not a trial.

**Written:** 2026-07-21
**Scope constraint honoured:** the combined exchange ToU question (OPEN OPERATOR DECISION 1)
is unresolved, so this note SCOPES routes and does not build or run any ingest.

> **UPDATE, same day, mid-note.** When this note began, `governance/specs/` held only
> `SPEC-52WH-01.md` (+ `.sha256`) and the DRAFT `SPEC-SRA-01.md`. **A concurrent session
> drafted `SPEC-QFM-01.md` (23:14) and `SPEC-PEAD-01.md` (23:17) while this note was being
> written.** §0 and §6 below were drafted against the earlier state and their "no spec file"
> claim is now **stale** — corrected in place where it appears. Both new specs are **DRAFT,
> unhashed, with no register row** (`research_register_v2.csv` still contains a single
> incidental QFM mention), so the governance position is unchanged: not binding, no outcome
> contact authorized.
>
> **The two documents were produced independently and converge.** SPEC-QFM-01 §2.1–§2.4
> reaches the same conclusions this note reaches from the data side: `announce_date` is the
> gated clock, restatements are new rows never edits, and a source supplying only
> latest-restated values is **inadmissible** rather than degraded. That independent
> convergence is worth more than either document alone. **Where they differ is the schema,
> and the difference matters — reconciled in §4.4.**

---

## 0. Why this note exists

`SPEC-QFM-01` — "fundamental deltas" — holds one of the program's **two** scarce shadow
slots. It is named in `CLAUDE.md`, in `SPEC-52WH-01.md` §10, in `SPEC-SRA-01.md` §, in
`plan_52wh.md` B3 and in `DECISIONS.md` (the PIT fallback pre-commitment). It is the
**first** name in the Tier 2 queue.

It has:

- ~~**no spec file**~~ — **CORRECTED, see the update box above: `SPEC-QFM-01.md` was drafted
  concurrently on 2026-07-21. It is DRAFT, carries no `sha256`, and is not binding.** The
  claim held at the time this note opened and is recorded rather than quietly deleted,
  because the *reason* it held — the family sat in a queue for three days as a name with no
  document — is the point being made,
- **no register row** (`research_register_v2.csv` names QFM only inside the
  `FREEZE-52WH-0001` note, never as a family of its own) — **still true**,
- and — the subject of this note — **no data**. **Still true, and now the binding
  constraint**: SPEC-QFM-01 cannot be hash-frozen while its own OPEN ITEMS 2 and 3 (source
  admissibility and the announce-date clock) are open, and those are exactly what this note
  scopes.

The data dependency appears **nowhere** in `SETUP_OF_RECORD.md`'s "Genuinely open items".
The filing-timestamp corpus and the MCX bhavcopy gap are both listed there (item 2). The
fundamentals corpus is not. It is an unlisted, unscoped dependency sitting under the
slot-holder at the front of the queue.

This is TRAP 6 exactly: the failure is SILENCE. Nothing errors. No script raises. There is
no half-built `data/reference/fundamentals/` directory to notice. The gap is invisible
because the family that needs it has never been written down, so nothing has ever asked
for the data and failed.

---

## 1. Gap confirmed

### 1.1 What `data/` actually contains (verified 2026-07-21)

```
data/derived          204K   paper_leg{,_recs}.parquet, nav.parquet, trials/52wh/
data/legacy_snapshot  148K   trades_log_ee7ad13.csv, recs/
data/market            92K   ohlc/ (4 dated parquet), actions/    [UNADJUSTED, Tier 1]
data/reference        104M   pit/ , tri/ , rename/
data/sealed           1.9M   raw/YYYY-MM-DD/ nightly production snapshots
data/workspace        199M   ohlc_adj/ (1,312 symbol parquet), price_panel_52wh.parquet,
                             fills.parquet, recs.parquet
```

File-type census across all of `data/`: 1,325 parquet (1,312 of them the per-symbol
adjusted OHLC caches), 172 csv, 165 pdf (niftyindices press releases), 97 md, 48 json,
18 xlsx (the AMFI corpus), 1 txt, 1 log.

`data/reference/` contains exactly three subtrees:

| Subtree | Contents |
|---|---|
| `pit/` | AMFI corpus (18 xlsx) + niftyindices press releases + `pit_universe.parquet` + `staging/` + `COVERAGE.md` |
| `tri/` | six daily total-return index series (A3) |
| `rename/` | NSE symbol-change master → `rename_map.csv` |

**There is no `fundamentals/`, no statements corpus, no earnings-date corpus, and no
line-item data of any kind anywhere in the repo.** A repo-wide grep for `fundamental`,
`xbrl`, `screener.in`, `prowess`, `capitaline`, `quarterly_financials`, `balance sheet`,
`income statement` (excluding `.venv`) returns **five** hits, none of them data: one line
in `research.md` (the qlib PIT schema note), one in `CLAUDE.md` (the QFM family name), and
three in `DECISIONS.md` that refer to the LEGACY engine's internal `fundamental` scoring
weight — a production feature weight, not a research corpus.

### 1.2 What the PIT store holds today — verified, not quoted

Read directly from `data/reference/pit/pit_universe.parquet`:

```
rows      274,966
columns   symbol, field, effective_date, announce_date, value, source, isin
fields    mcap_rank        89,891
          avg_mcap_cr      78,530
          bse_avg_mcap_cr  73,427
          nse_avg_mcap_cr  33,118
sources   18 files, all of the form amfi_YYYYH{1,2}_avg_mcap.xlsx
eff_date  2017-12-31 → 2026-06-30
ann_date  2018-01-25 → 2026-07-25      (= effective_date + 25d, ASSUMED, every row)
```

This matches `CLAUDE.md`'s "274,966 rows / 4 fields" exactly. **All four fields are AMFI
market-capitalisation derivatives.** Three of the four are the same quantity at different
exchange scopes. The store's entire information content is: *what rank was this company,
and what was its six-month average market cap, at each half-year end.*

`src/pit_universe.py` says so in its own docstring — it declares exactly two field
families, `mcap_rank` and `index_member:<NAME>`, and closes with:

> Features only — no price or return data lives here.

(In passing: `index_member:*` is declared in the module docstring and implemented in
`universe_as_of`, but **no `index_member` row exists in the store** — the 164 press-release
PDFs were never normalised into member rows, per `COVERAGE.md` §7. So the `"NIFTY500"` band
form is live code with an empty backing set. Not this note's problem, but worth recording,
since it is the same shape of silence.)

### 1.3 Verdict

**CONFIRMED.** No fundamentals data exists anywhere in the repository, in any form, at any
depth. The dependency has never been started, never been scoped, and is not on the open-items
list. The `~1,300`-symbol figure in the brief is close: the union of the `201-1000` habitat
across dev-window quarter-ends is **1,249 distinct symbols** today, and would widen roughly
10% (to ~1,370) once the §6.7 blank-symbol defect is fixed — call the requirement
**~1,400 symbols** to be safe, since fixing that defect is already queued ahead of C1 attempt 2.

---

## 2. The requirement, stated precisely

### 2.1 What a "quarterly fundamental deltas" family minimally needs

The family name implies **change** in reported fundamentals — QoQ and YoY deltas, surprise
versus a trailing path, acceleration. Deltas are far more demanding of data quality than
levels, because a delta subtracts two numbers that must have been produced on the **same
basis**. Any basis change between the two — accounting standard, consolidation scope,
restatement, exceptional-item treatment — appears as signal and is noise.

**Statements needed, in priority order:**

1. **Quarterly Profit & Loss (LODR Reg 33 results format)** — the core, and effectively the
   only quarterly statement that exists in India (see §2.4). Minimal line items:
   - Revenue from operations
   - Other income
   - Total income
   - Total expenses, plus the sub-lines that let EBITDA be reconstructed rather than trusted:
     cost of materials consumed, purchases of stock-in-trade, changes in inventories,
     employee benefits expense, finance costs, depreciation & amortisation, other expenses
   - **Exceptional items** — non-negotiable. A delta family without an exceptional-items line
     will repeatedly discover that a one-off land sale is a fundamental acceleration.
   - Profit before tax
   - Tax expense (current + deferred)
   - Profit after tax from continuing operations
   - Profit/loss from discontinued operations (so continuing-ops deltas are clean)
   - EPS, basic and diluted
   - Optional but high-value: segment revenue / segment results (Ind AS 108 segment
     reporting accompanies quarterly results)

2. **Half-yearly Balance Sheet** — assets, liabilities, equity, borrowings, and enough
   working-capital detail (inventories, trade receivables, trade payables) to compute
   accruals and working-capital deltas. **Half-yearly, not quarterly** — see §2.4.

3. **Half-yearly Cash Flow Statement** — cash from operations, at minimum, so that an
   earnings-quality overlay (accruals = PAT − CFO) is available. Same frequency caveat.

4. **Shares outstanding / equity share capital** per period — required to make any per-share
   delta well-defined across issuance, and required for anything cap-normalised.

**Nice-to-have, explicitly OUT of the minimal set:** analyst estimates / consensus (that is
an I/B/E/S-class product and a separate licence), auditor opinions, related-party detail,
shareholding pattern.

### 2.2 Frequency and volume

- Quarterly P&L: 4 observations/year.
- Dev window: to match the existing adjusted price panel (2015-01-01 → 2024-07-16), that is
  ~34 fiscal quarters (FY2015-16 Q1 through FY2024-25 Q1).
- Universe: ~1,400 symbols (§1.3).

**Volume estimate:** 1,400 × 34 ≈ 47,600 statement-quarters. At ~20 P&L line items per
statement in the long `(symbol, field, ...)` row shape, that is **~950,000 rows**, rising to
roughly **1.2M** with half-yearly balance-sheet and cash-flow items. Against the current
store's 274,966 rows this is a **~4× larger artifact** — material for storage layout
(§4.3), immaterial for parquet.

### 2.3 The two dates — and why the announce date is non-negotiable

Every row must carry **two** dates, exactly as the existing schema already provides:

| Column | Fundamentals meaning |
|---|---|
| `effective_date` | **fiscal period end** — 2019-03-31, 2019-06-30, … The date the reported quantity refers to. |
| `announce_date` | **the date the result was actually published to the exchange** — the date the number became public knowledge. |

The announce date is not a convenience field. It is the **only** thing that makes the row
point-in-time, and it is load-bearing in two independent ways in code that already exists:

**(a) It is the seal gate.** `src/pit_universe.py::_visible` does:

```python
gated = data_gate.load(validate(frame), "announce_date")
```

`data_gate.load` strips every row whose gated date column is `>= 2024-07-17` unless
`FINAL_TEST=1`. So a fundamentals row is **structurally invisible to research** if and only
if its `announce_date` falls on or after the seal cutoff. The module docstring states this
as the design intent:

> rows announced on/after the seal cutoff are structurally invisible to research
> regardless of the query date

If the announce date is wrong, the seal is wrong. A source that gives a fiscal period end
and no publication date forces us to *manufacture* the field that the seal is enforced on.
That is not a data-quality compromise; it is the seal being enforced against a fiction.

**(b) It is the walk-forward's look-ahead gate.** `_visible` additionally requires
`announce_date <= query_date`. This is what stops a rebalance on 2019-04-15 from consuming
a March-quarter result that was not published until 2019-05-28. For a *quarterly* rebalance
this matters enormously: the LODR filing window is up to 45 days after quarter end, which is
half a rebalance period. Getting it wrong does not degrade the signal — it **manufactures**
one, because the "signal" becomes knowledge of a number nobody had.

**Why a constant assumed lag does NOT work here, even though the AMFI store uses one.**

The AMFI rows carry `announce_basis = ASSUMED_period_end_plus_25d` on every row. That
assumption is defensible for AMFI and *only* for AMFI, for three specific reasons documented
in `COVERAGE.md` §2: AMFI publishes on a **fixed institutional schedule** mandated by a SEBI
circular; observed publication was **≤4 and ≤5 days** after period end in the two cases that
could be checked; and +25d is therefore **conservative for every row** — later than any
observed actual publication, so no backtest can consume a rank before it was public. One
publisher, one schedule, one direction of error.

None of that survives the move to per-company earnings dates:

1. **The dispersion is the whole point.** Indian quarterly results arrive anywhere from ~2
   weeks to the 45-day statutory wall, and mid/small caps cluster hard at the wall. A single
   constant is not conservative for some rows and absurdly conservative for others.
2. **The error is correlated with the thing being measured.** Reporting lag is not random
   noise — late filing is itself associated with bad news, and a delta family is precisely a
   family that trades on the content of results. Substituting a constant lag systematically
   misdates the informative tail. This is not a small bias; it is a bias aligned with the
   hypothesis.
3. **There is no conservative direction.** Setting the constant early creates look-ahead for
   late reporters. Setting it late (+45d for everyone) destroys the signal for early
   reporters and silently pushes a whole quarter of results across a rebalance boundary. You
   cannot pick a constant that is safe in both directions.

**Consequently: a fundamentals source without a reliable per-company announce date is
unusable here regardless of how good its numbers are.** This is a hard filter applied before
any other criterion in §3, and it eliminates several otherwise-attractive sources.

One permissible middle route exists and should be named: obtain fundamentals from source A
and announce dates from source B (an exchange results/board-meeting calendar), joined on
(ISIN, fiscal period). This is a real option — but it makes the corpus's PIT integrity
depend on a **join**, and a failed join is silent (TRAP 6). If taken, the join must be
covered by a coverage assertion, not a row count: *what fraction of statement-quarters
acquired a matched announce date, by year and by market-cap decile?* An unmatched row must
be **dropped, not defaulted**.

### 2.4 A structural constraint that must go in the spec: India has no quarterly balance sheet

This is a design constraint on the family, not a vendor problem — no amount of money buys
around it.

SEBI LODR Regulation 33 requires listed companies to file **quarterly financial results**
(P&L) within **45 days** of quarter end, and annual results within **60 days** of year end
(VERIFIED against SEBI LODR FAQ material). Reg 33(3)(b) requires an entity with subsidiaries
to submit **consolidated** results **in addition to** standalone (VERIFIED — this is what
makes the basis flag in §2.4 mandatory rather than cosmetic).

Regulation 33 does **not** require a quarterly balance sheet. A statement of assets and
liabilities, and a cash flow statement, are required on a **half-yearly** basis — and that
requirement was itself *introduced partway through the dev window*, on the Kotak-Committee
LODR amendments effective around FY2019-20. **UNVERIFIED: the exact circular/amendment and
its first applicable period could not be pinned from primary SEBI text in this pass (the
FAQ page returned is silent on it, and the circular most often cited alongside it —
CIR/CFD/CMD1/44/2019, 29 Mar 2019 — is actually the limited-review/audit-report FORMAT
circular). This must be pinned from the primary regulation text before it enters a spec.**
The direction of the constraint is not in doubt even if the date is; the practical
consequence, whatever the exact date:

- **Anything requiring a balance sheet is half-yearly at best, and only from ~2019-20.**
  That means: no quarterly accruals, no quarterly ROE/ROCE delta, no quarterly
  working-capital delta, no quarterly net-debt delta — for roughly the first half of the
  dev window, none of these at all.
- **The genuinely quarterly signal surface is the P&L and nothing else** — revenue growth,
  margin change, EBITDA acceleration, PAT surprise versus trailing path, tax-rate change.

Two further quarterly-specific traps that belong in the spec, pre-registered:

- **Q4 is not a filed quarter for many companies.** Q1–Q3 results are limited-reviewed; the
  fourth quarter is commonly published as the audited full year, with "Q4" **back-derived**
  as `FY − 9M` either by the company or by the data vendor. A back-derived Q4 has **no
  independent announce date** — its true publication date is the annual-results date. A
  vendor that silently derives Q4 and stamps it with a fabricated date injects exactly the
  error §2.3 warns about, and it injects it into the same quarter every year, i.e.
  seasonally. The spec must state whether derived Q4s are admitted, and if so, that they
  inherit the annual-results announce date.
- **Standalone vs consolidated must be a first-class attribute, never a fallback.** Many
  companies file both; some file only standalone in early years. Silently falling back from
  consolidated to standalone when consolidated is missing creates a level shift that a delta
  family reads as a fundamental change. The field key must carry the basis (§4.2) and the
  spec must fix one basis with a pre-registered rule for the other.

### 2.5 Restatements — the store must retain the ORIGINALLY REPORTED figure

The requirement is that the store answers *"what did the market know on date t"*, not
*"what do we now believe the number was"*. These differ, and in India they differ more than
in most markets, for four reasons that all fall inside the dev window:

1. **Ind AS transition — and it lands squarely inside the dev window.** VERIFIED against the
   MCA roadmap as commonly summarised: **Phase 1** applied from **1 April 2016** to listed and
   unlisted companies with net worth ≥ ₹500 cr, with a restated comparative at 31 Mar 2016 and
   an opening balance sheet at 1 Apr 2015. **Phase 2** applied from **1 April 2017** to **all
   remaining listed companies** (and unlisted ≥ ₹250 cr), with a restated comparative at
   31 Mar 2017 and an opening balance sheet at 1 Apr 2016. Since the QFM habitat is ranks
   201–1000, **the great majority of the habitat transitioned in Phase 2, on 1 April 2017** —
   i.e. every YoY delta straddling FY2017-18 compares an Ind AS quarter against an IGAAP
   quarter, unless the comparative is the restated one, in which case it compares against a
   number that was **not** the number published a year earlier. There is no version of this
   that is clean; it can only be handled explicitly. On transition,
   prior-period comparatives were **restated**. A vendor that stores only current-basis
   figures shows an Ind AS comparative for a quarter that was actually reported under IGAAP.
   A YoY delta spanning the transition is then computed against a number **that was never
   published**. This affects a large slice of the 2015–2018 portion of the dev window —
   i.e. precisely the extra history a QFM family would want.
2. **Schemes of arrangement.** Mergers, demergers and slump sales in India are frequently
   given retrospective effect from an appointed date, and comparatives are restated
   accordingly. A restated comparative makes the merger look like organic growth.
3. **Ordinary restatement and reclassification.** Ind AS 8 restatements, and the very common
   quiet reclassification between "other expenses" and a named line, both change deltas
   without changing economics.
4. **Q4 derivation drift.** If Q4 is derived as `FY − 9M` and any of the first three quarters
   is later restated, the derived Q4 moves too — retroactively, with no announcement.

**Requirement:** the store must be able to hold **multiple vintages of the same
(symbol, field, fiscal period)** and resolve to the vintage current at the query date. It must
not overwrite. Where a source supplies only the latest restated figure, that limitation must
be recorded per row (an `as_reported` / `vintage_basis` flag) and disclosed in any write-up —
per TRAP 4, a disclosed gap is an asset and an invented number is a liability.

Encouragingly, **the existing row shape already expresses this correctly** — see §4.1, where
it is verified empirically rather than assumed.

---

## 3. Source survey

**Method note:** every source below was assessed from public documentation, pricing pages,
terms pages, library source on GitHub, and regulatory/third-party writeups. **No data API was
called, no account created, no dataset fetched, and no NSE/BSE/MCX endpoint was touched.**
Where a claim could not be settled from a primary page it is marked **UNVERIFIED** with the
artifact that would settle it.

### 3.0 The announce-date filter, applied first

Per §2.3 this is a hard filter, so it is worth stating the result before the detail. Applying
it to every source surveyed:

| Verdict | Sources |
|---|---|
| **Announce date structurally present** (the filing IS the date) | Exchange filing corpus (BSE `DissemDT`); Deutsche Börse "BSE India Corporate Data"; Accord ACE Datafeed (announcements leg) |
| **Announce date documented as a field, population for Indian small caps UNVERIFIED** | EODHD (`filing_date`, `reportDate`); Trendlyne (`Result Declared date` — but current-state only); FMP (`filingDate`/`acceptedDate` — US/EDGAR-derived, India population doubtful) |
| **Announce date verified ABSENT** | yfinance statements (`asOfDate` = period end); Upstox Company Fundamentals (`period` = fiscal label); Screener.in quarterly tables; Tijori; Tickertape; Finology; MCA21 (annual-only anyway) |
| **UNCLEAR, must be asked** | CMIE Prowess; Capitaline; ACE Equity; C-MOTS; Refinitiv/LSEG; Bloomberg; S&P Capital IQ; FactSet |

**The single most important structural finding of this survey is that announce dates and
fundamental values are not sold as one product at any price point we would want, and should
not be sourced as one.** The exchange filing record carries a PIT-correct dissemination
timestamp; the statement values are a separate artifact. The correct join is
**filing record (timestamp) → statement (numbers)**, keyed on ISIN + filing, and — critically
— **not** on the XBRL file's own timestamp, which by design lags the PDF dissemination by up
to 24 hours (BSE requires the PDF within 30 minutes of board-meeting close under LODR Reg
30(6)(i), and the XBRL within 24 hours). Using the XBRL timestamp would date-stamp every
observation late by 0–24h, systematically.

### 3.1 The hard history floor nobody can sell around

**BSE circular DCS/COMP/28/2016-17 (30 March 2017) made XBRL submission of financial results
mandatory with effect from 2017-04-01.** Before that, BSE's XBRL mandate covered only
corporate governance, shareholding pattern and voting results — **not financial results**.

Consequence for the requested window: **machine-readable results begin at Q4 FY2017
(announced April–May 2017).** The first ~5–9 fiscal quarters of a 2015-2016 start are
**PDF-only** — and per this program's earlier scoping, BSE announcement PDFs are themselves
retrievable only from **~2019-01**, with a soft-404 making earlier ones *look* retrievable
(TRAP 6, external variant).

This is a **structural hole from ~2015 to 2017-04 that no vendor can fill**, because the
filings did not exist in that form. It should be pre-registered as a spec limitation, not
discovered later. It also has a direct design consequence: **a QFM dev window realistically
starts ~2017-04 (first XBRL results) or 2018-04 (first clean YoY delta on XBRL-vs-XBRL)** —
which happens to align with the PIT habitat's own announce-safe floor of **2018-01-25**
(COVERAGE.md §3). *The habitat and the fundamentals corpus have the same practical start
date.* That is a convenient coincidence and it should be stated in the spec rather than
rediscovered.

NSE's equivalent "results in XBRL from date X" could **not** be established (**UNVERIFIED**),
and NSE is out of scope for this corpus regardless, on its explicit anti-automation ToU plus
this program's prior finding that BSE is strictly better for the dev window (second-precision
`DT_TM` vs NSE's HH:MM-until-2020-08).

*Forward-looking note, outside the dev window but relevant to any ingest built:* SEBI circular
SEBI/HO/CFD/CFD-PoD-2/CIR/P/2024/185 (31 Dec 2024) replaced standalone results filing with
"Integrated Filing – Financial" in XBRL, effective 2025-04-01. Any ingest will need a schema
break there to stay usable forward.

### 3.2 Free and prosumer routes — all fail, most on the announce date

#### yfinance / `Ticker.quarterly_financials` — **CLOSE THIS ROUTE, do not keep it as a fallback**

Three independent disqualifiers, any one of which is fatal:

1. **History cap ~5 quarters.** Not a rate limit — it is the endpoint. `yfinance`'s own
   source carries the comment verbatim: *"Yahoo returns maximum 4 years or 5 quarters,
   regardless of start_dt"* (`yfinance/scrapers/fundamentals.py`). Requirement is ~34
   quarters. That is a ~7× shortfall with no parameter to widen it; a paid Yahoo Finance
   subscription does not unlock it either (yfinance issue #1966).
2. **No announce date, verified from the code path.** Statement frames are keyed on
   `asOfDate`, which is the **fiscal period end**. There is no filing-date field anywhere in
   the statement payload. `get_sec_filings()` is SEC/EDGAR-backed, i.e. US-only and
   irrelevant to `.NS`. The earnings *calendar* (`get_earnings_dates`) is a **different
   object** with no join key to the statements beyond fuzzy date matching — and Yahoo
   reportedly stopped updating that endpoint in mid-2025.
3. **No vintage dimension.** There is exactly one value per (line item, period). The field is
   named `reportedValue`, which is seductive, but a restatement **overwrites in place** and
   the prior figure is gone. The honest characterisation is not "as-reported" but *"the most
   recent vendor opinion of that period, silently backfilled"* — precisely the object §2.5
   exists to prevent.

Plus: `.NS` mid/small-cap fundamentals coverage is documented-broken in the tracker
(issues #825, discussion #2089) and **unmeasured here by design**; and Yahoo's ToS prohibit
automated extraction, a materially weaker position than this repo's existing sanctioned
yfinance **OHLC** use because the output would feed a fund track record.

**Recommendation: formally close it.** The temptation is to treat 5 quarters as "a start".
It is not — a panel with no announce date and no vintage dimension is not a degraded PIT
corpus, it is a **different and structurally contaminated object**, and mixing it into
sealed-protocol work would put the governance trail at risk for data that cannot be used.

#### Screener.in

| | |
|---|---|
| Coverage | Full NSE+BSE incl. small caps — reaches the habitat |
| History | "10–15 years" claimed; exact quarter count in export **UNVERIFIED** |
| **Announce date** | **NO.** Quarterly tables are keyed on fiscal-period labels ("Jun 2023"). A separate per-company *Announcements* list carries real dated filings, but is not joined to the statements and its archive depth is **UNVERIFIED** |
| Restatements | **UNCLEAR, almost certainly as-restated.** No documentation |
| API | **None — stated explicitly.** Premium CSV export only, ≤50 columns |
| ToU | Licence is *"personal, non-commercial transitory viewing only"*; bars commercial use, mirroring, transfer |
| Cost | Premium **₹4,999/yr** |

**Material finding:** Screener credits its data to **C-MOTS Internet Technologies Pvt Ltd** —
it is a presentation layer over a licensed vendor feed, so its ToU cannot grant redistribution
rights it does not hold. **Verdict: unusable**, and the non-commercial clause alone
disqualifies it for a registration-bound track record. *(C-MOTS itself is a new vendor lead —
see §3.4.)*

#### Tijori Finance

Coverage unpublished (**UNVERIFIED** whether it reaches ranks 201–1000 at depth); 10 years of
statements; **no API, no documented export, no evidence of any date field**; terms page not
located (**UNVERIFIED**); ₹330/mo or ₹3,500/yr. **Verdict: unusable — not worth further
diligence.**

#### Trendlyne — the closest retail candidate, and still blocked

| | |
|---|---|
| Coverage | Full NSE/BSE incl. small caps; 1,758–3,512 screener parameters by tier |
| **Announce date** | **YES, uniquely — `Result Declared date` is a first-class queryable screener parameter**, alongside a `next result date` and an events calendar covering board meetings and results. **CAVEAT: it is a *current-state* filter.** Whether declared dates for 2015–2024 are retrievable as a historical series is **UNVERIFIED** — every documented use case is "today / past 1 week" |
| Restatements | **UNCLEAR.** "Rapid Results" captures results within 30 min of announcement — a snapshot mechanism — but nothing states snapshots are retained unmodified |
| API | Enterprise/custom only; no public docs, no published price (**UNVERIFIED**) |
| **ToU** | **The blocker, and explicit:** *"You may not resell, redistribute, broadcast or transfer the information or use the information in a **searchable, machine-readable database**"* absent written authorisation. Building a research corpus is exactly that. Note the same **robots.txt-vs-ToU contradiction already documented for NSE** — the ToU governs |
| Cost | ₹310/mo (GuruQ) → ₹10,000/yr (PRO PLUS) |

**Verdict: worth exactly one email, not a scrape.** Two questions settle it: (a) are
`Result Declared date` values retrievable historically to 2015, per company per quarter;
(b) as-first-reported or overwritten. If (a) is no, drop it.

#### Broker and developer APIs

| Provider | Fundamentals | Announce date | Verdict |
|---|---|---|---|
| **Upstox** | **Yes** — Company Fundamentals by ISIN (income statement, BS, CF, ratios, corporate actions), **free** | **NO — verified from the response schema.** Fields are `period` (fiscal label, e.g. "Mar 2026"), `value`, `change`. No filing/publication date anywhere | **Unusable.** Also community-reported at **~1 year** of quarterly history — consistent with being free |
| **Zerodha Kite Connect** | **No fundamentals at all** (orders, portfolio, quotes, historical prices, WebSocket) | n/a | Unusable — and barred by BINDING RULE 3 regardless |
| **Dhan (DhanHQ)** | No fundamentals endpoint found | n/a | Unusable |
| **Sensibull** | Options analytics, not a fundamentals vendor | n/a | Out of scope |

#### Global data APIs, India reality

| Provider | India depth | Announce date | Cost |
|---|---|---|---|
| **EODHD** | NSE+BSE on the Fundamentals feed. **The catch is in their own tiering:** ~11,000 major US tickers get 25–30+ yrs, while *"minor companies have the last 6 years and 20 quarters"*. **Ranks 201–1000 Indian names land in the minor bucket → ~20 quarters, likely insufficient for a 2015–2024 window** | **PARTIAL / the most promising documented case.** `Earnings::History` carries `reportDate`; quarterly `Financials` reports carry **`filing_date`**. This is the only prosumer vendor found with a documented per-row filing date. **CRITICAL UNVERIFIED: whether it is populated for Indian small caps or null outside the US** | Fundamentals feed **$59.99/mo, $599.90/yr**. **All listed tiers say "Personal use only"** — commercial licensing is a separate conversation |
| **Financial Modeling Prep** | `.NS` supported; small/mid-cap depth **UNVERIFIED** | **UNCLEAR.** `filingDate`/`acceptedDate` on US statements are SEC-derived; population for NSE is **UNVERIFIED and should be assumed absent until proven** | ~$20–100/mo |
| **Finnhub** | Claims NSE support | **Probably NO for India** — the endpoint carrying filing dates (`financials-reported`) is SEC-derived; the global endpoint is standardised. **UNVERIFIED** | **UNVERIFIED** |
| **Alpha Vantage** | India fundamentals thin, **UNVERIFIED** | No evidence | Free + paid |
| **Intrinio** | India NSE appears only as a **prices** coverage item — no India fundamentals product found | — | Enterprise |
| **Sharadar (Nasdaq Data Link SF1)** | **US only, ~16,000 US companies.** No India product exists | — | — |
| **SimFin** | **~5,000 US stocks**; non-US "coming in future quarters" (a years-old promise). **No India — rule out** | — | — |
| **OpenBB** | Aggregator only; inherits whatever provider is attached. Adds no Indian fundamentals of its own | inherits | open source |

**The Sharadar point deserves to be stated plainly, because it reframes the whole problem:**
the product category we want — **as-first-reported fundamentals with a report date, at a
prosumer price** — exists for the US (Sharadar SF1, with its ARQ/ART dimension codes) and
**does not exist for India at any retail price point.** That is a structural fact about the
Indian data market, not a search failure. Every route from here is either an exchange corpus
we build ourselves or a licensed institutional vendor.

#### Other free bulk routes — both dead ends

- **MCA21 / AOC-4 XBRL** (XBRL mandated by MCA notification, 5 Oct 2011) deserves an explicit
  kill, because it is the most "official-looking" free source. **The Companies Act filing
  regime is ANNUAL. There is no quarterly AOC-4.** Whatever its data quality, it cannot
  produce a quarterly panel. It also has no bulk export.
- **Kaggle / GitHub corpora** (e.g. "Detailed Financials of 4,492 NSE & BSE Companies";
  `jugaad-data`, `nsepython`, `Bharat-SM-Data`): the Kaggle sets are scrapes of retail
  aggregators with unverifiable provenance and almost certainly no announce date. The GitHub
  projects are **scrapers, not corpora**, and they are a governance trap in a way that is easy
  to miss: **adopting one does not change the ToU position, it moves the automated collection
  into a dependency where it is less visible in our own governance trail.** If NSE automated
  collection is prohibited, importing a library whose entire function is NSE automated
  collection is the same act with worse provenance.

### 3.3 Institutional and licensed routes

**SCOPE WARNING — THIS SUBSECTION IS INCOMPLETE, AND SAYING SO IS THE POINT.** The research
pass covering institutional vendors **terminated early on a session limit** before reaching
Refinitiv/LSEG, Bloomberg, S&P Capital IQ, FactSet, Morningstar and Orbis, and the web-search
budget was exhausted before the gap could be closed by hand. What follows for
Prowess / Capitaline / ACE is real; **what follows for the six named above is NOT RESEARCHED
and must not be read as a finding.** Per TRAP 6, an incomplete survey presented as complete is
exactly the failure this program keeps paying for, so the hole is stated rather than papered
over. Closing it is ~half a day.

#### Researched

| Source | Coverage | History | Announce date | Restatements | Cost |
|---|---|---|---|---|---|
| **CMIE Prowess** | >27,000 companies incl. NSE/BSE listed **and unlisted**; >3,500 fields. Comfortably covers the habitat | **from 1989-90** — the deepest Indian series available anywhere | **UNCLEAR — the decisive question.** It carries quarterly statements and result dates, but whether a true per-row *dissemination* date is exposed (versus a period label or a board-meeting convention) is **UNVERIFIED** | **NO vintage store** — standard vendor practice is that restatements overwrite. This is also the long-standing criticism of Prowess in the academic literature (**UNVERIFIED in this pass, flagged from the earlier agent's summary, not from a primary source**) | Commercial/institutional; typically ₹ lakhs/yr; **very commonly available via a university licence** (e.g. IIM libraries) |
| **Capitaline** (Capital Market Publishers) | Indian listed universe; reported at ~650 finance fields in one place and 74,800+ companies / ~2,500 fields in another — **the two figures are from different product tiers and were not reconciled (UNVERIFIED)**. 10-yr P&L/BS standard | Long | **UNCLEAR** | **NO** stated vintage handling | Commercial, **pricing not public** |
| **Accord Fintech — ACE Equity / ACE Equity Nxt** | **>40,000 Indian companies, ~1,750 fields, compiled from annual reports, all Indian exchanges** | Long (not quantified — **UNVERIFIED**) | **UNCLEAR — but structurally the most likely to be solvable**, because Accord *separately* licenses the BSE/NSE **corporate-announcements** feed. A joined product is plausible in a way it is not for Prowess or Capitaline | Not stated (**UNVERIFIED**) | Commercial, **pricing not public** |
| **Deutsche Börse — "BSE India Corporate Data"** | BSE-listed (4,500+). Deutsche Börse is the **exclusive licensor of BSE Information Products to international customers** | **UNVERIFIED — must be asked, and it is the question that decides this route** | **YES in principle — the product bundles Corporate Announcements *and* Financial Results (quarterly/half-yearly/yearly, in regulatory formats) in one XML/XBRL feed.** This is the §3.0 join sold pre-joined | **Implicitly vintaged** — filings are immutable, so a restatement arrives as a new filing rather than an overwrite | **Price on application (UNVERIFIED)** |
| **C-MOTS Internet Technologies** | Screener.in's upstream vendor; scope unquantified | **UNVERIFIED** | **UNVERIFIED** | **UNVERIFIED** | **UNVERIFIED** |

#### NOT RESEARCHED — do not treat as assessed

**Refinitiv / LSEG** (Datastream, Worldscope, Eikon/Workspace, RDP API, and specifically
whether **Worldscope point-in-time** or I/B/E/S carry Indian small-cap report dates);
**Bloomberg** (Terminal/BQL/Data License/B-PIPE, the `ANNOUNCEMENT_DT` field, "as-reported"
versus "standardized" fundamentals, and the redistribution restrictions that bite for a fund's
research use); **S&P Capital IQ**; **FactSet**; **Morningstar/PitchBook**; **Bureau van Dijk
Orbis**. Nothing in this note should be cited about any of them.

Two observations that can be made without research and that shape how much this hole matters:

- All six are **enterprise-priced** — realistically five to six figures USD per year, i.e. an
  order of magnitude above every other route here, and almost certainly out of proportion to
  a pre-revenue research program. They are the *right* answer for a funded desk and probably
  the wrong answer today.
- All six are **global standardized-data** vendors, and standardized data is precisely where
  as-first-reported figures get normalised away. The India-small-cap coverage question is also
  genuinely open for all of them — global vendors thin out fast below the Nifty 500.

**Consequently, resolving this hole is unlikely to change the recommendation in §5**, which is
why the note is being delivered rather than held. It should still be closed for completeness
before any procurement decision, because "we did not look" is a weaker position at due
diligence than "we looked and they were too expensive."

### 3.4 New vendor leads surfaced by this pass

Two names emerged that were not in the brief and that materially change the option set:

1. **Deutsche Börse Market Data + Services** is the **exclusive licensor of BSE Information
   Products to all international customers**. Its **"BSE India Corporate Data"** product
   bundles, in **XML and XBRL**, by secure download: *Corporate Announcements · Financial
   Results (quarterly, half-yearly, yearly in regulatory formats) · Shareholder Pattern ·
   Corporate Actions · Corporate Governance · Board Meetings · Results Calendar · Voting
   Results · Consolidated Pledge*. **This is the §3.0 join — announcements and financial
   results — sold pre-joined, under licence.** It is the single best structural fit found in
   this entire survey. **History depth and pricing are not published and require an enquiry
   (UNVERIFIED).**
2. **C-MOTS Internet Technologies Pvt Ltd** — identified as Screener.in's actual upstream data
   vendor. Same category as Accord: a licensed Indian feed vendor. Worth one enquiry alongside
   Accord. Pricing **UNVERIFIED**.

And a third observation that is now hard to dismiss: **Accord Fintech has surfaced
independently in *three* separate research passes of this program** — BSE announcements, MCX,
and now fundamentals (ACE Equity / ACE Equity Nxt: >40,000 Indian companies, ~1,750 fields,
compiled from annual reports, all Indian exchanges; and an ACE Datafeed that explicitly
includes corporate announcements). At three independent surfacings this stops being a
coincidence. **One enquiry to Accord could plausibly dissolve the ToU blocker, the
fundamentals corpus and the MCX data plan simultaneously — with a licence attached, which is
itself the due-diligence asset.**

---

## 4. Can the existing PIT store absorb fundamentals?

### 4.1 The row shape maps cleanly — verified, not assumed

`src/pit_universe.py` declares:

```python
SCHEMA = ("symbol", "field", "effective_date", "announce_date", "value", "source")
OPTIONAL_COLS = ("isin",)
```

`research.md` Part 1 records qlib's PIT schema as
`(instrument, field, fiscal_period, announce_date, value)` resolved as-of a date. Checked
against qlib's actual source, that note is accurate: `scripts/data_collector/pit/collector.py`
normalises its raw ingest to exactly five columns — `date, period, value, field, symbol` —
where `date` is the announcement date and `period` the report period. The
correspondence to this repo is one-to-one:

| qlib | this repo | fundamentals meaning |
|---|---|---|
| `instrument` | `symbol` | NSE/BSE ticker (join key should be `isin`, per COVERAGE.md §6.2) |
| `field` | `field` | line item, e.g. `fin:CONS:revenue_cr` |
| `fiscal_period` | `effective_date` | quarter end |
| `announce_date` | `announce_date` | publication date |
| `value` | `value` | float64 |
| — | `source` | provenance (repo addition, strictly better) |

The repo's schema is a **superset** of qlib's: it carries `source` per row, and its
`effective_date` is a real date rather than a packed period integer, so quarter ends,
half-year ends and annual ends all live in one column without an encoding convention.

**The critical question is whether the as-of resolution handles vintages correctly.** It
does. Verified directly against `snapshot_as_of` with a synthetic three-row frame — one
fiscal quarter reported at 100.0 on 2019-05-14 and restated to 92.0 on 2020-05-20, plus the
next quarter reported at 110.0 on 2019-08-10:

| Query date | Returned | Correct? |
|---|---|---|
| 2019-05-13 | `{}` (nothing) | yes — not yet announced |
| 2019-05-20 | `100.0` | yes — the **originally reported** figure |
| 2019-09-01 | `110.0` | yes — latest visible period |
| 2020-06-01 | `110.0` | yes — the 2020 restatement of Q1 does not overwrite Q2 |

The mechanism is `_visible`'s `sort_values(["effective_date", "announce_date"])` followed by
`groupby("symbol").tail(1)`: latest fiscal period among visible rows, and within it the
latest vintage announced on or before the query date. **That is exactly correct vintage
semantics, and it was already built** — it just happens to be untested against fundamentals
because there are none.

### 4.2 What is genuinely missing (three items, all small)

1. **A history accessor.** `snapshot_as_of` returns **one** value per symbol — the latest
   visible period. A *delta* family needs, as of date `t`, the value at period `p` **and** at
   `p-1` / `p-4`, each at the vintage current on `t`. That is not expressible with the current
   API: asking for the earlier period would require a second call at an earlier query date,
   which returns the vintage as of *then*, not as of `t`. Wrong answer, silently.
   **Needed:** `series_as_of(frame, date, field) -> DataFrame[effective_date × symbol]`,
   returning for each (symbol, period) the latest vintage with `announce_date <= date`.
   **PROTOTYPED AND VERIFIED — it is six lines over the same `_visible` gate:**

   ```python
   def series_as_of(frame, date, field):
       vis = pit_universe._visible(frame, date)          # gated, no look-ahead
       vis = vis.loc[vis["field"] == field]
       if vis.empty:
           return pd.DataFrame()
       last = vis.groupby(["symbol", "effective_date"], sort=True).tail(1)
       return last.pivot(index="effective_date", columns="symbol", values="value")
   ```

   Run against the same synthetic restatement frame, it returns the Q1 value as **100.0**
   when queried at 2019-09-01 and as **92.0** when queried at 2020-06-01, with the surrounding
   quarters unchanged — i.e. correct vintage-at-query-date semantics across a full history,
   which is exactly what a YoY delta needs and what `snapshot_as_of` cannot give.
   This is the single most important piece of code this family needs, and it is nearly free.
2. **Basis and units carried in the field key.** The schema has no units column and no
   consolidation flag. The store already has the right precedent: `avg_mcap_cr` encodes its
   unit in the field name, and `index_member:NIFTY500` encodes a parameter in the field name.
   Follow it: `fin:CONS:revenue_cr`, `fin:STAND:revenue_cr`, `fin:CONS:pat_cr`. This keeps
   `SCHEMA` unchanged — no edit to a module that a frozen spec's code path depends on.
   Rupee figures must be normalised to a **single** unit (crore, matching `avg_mcap_cr`) with
   a parse-time assertion, because Indian filings mix lakh, crore and million freely.
3. **A `vintage_basis` / `as_reported` provenance column.** `OPTIONAL_COLS` is the designed
   extension point and currently holds only `isin`; adding one string column there is a
   one-line change and is carried through `validate` automatically.

**A fourth item is an expression-layer mismatch, worth flagging early.** `src/expr.py`'s
`ref(x, n)` shifts by `n` **rows** of a wide date×symbol frame. A YoY fundamental delta is
`x / ref(x, 4)` **only if the frame is indexed by fiscal period**. A daily price frame and a
quarterly fundamentals frame therefore cannot appear in one expression. The closed grammar
already supports the delta form; QFM's spec must simply state that its expressions evaluate
on a **period-indexed** frame, and any price interaction happens at the join, not inside the
expression. Cheap to get right now, expensive to discover later.

### 4.3 Recommendation: same schema, same module, **separate parquet file**

**Do not add fundamentals rows to `pit_universe.parquet`.** Do reuse the schema and the
module. `load_store(path)` is already parameterised, so a second store needs **zero**
changes to `pit_universe.py` beyond the additions in §4.2.

Proposed: `data/reference/fundamentals/pit_fundamentals.parquet`, plus its own
`COVERAGE.md`, `manifest.csv`, `staging/` and `raw/` — mirroring the `pit/` layout exactly,
because that layout has already proved itself.

Four reasons to keep the files apart:

1. **Blast radius under a frozen spec.** `pit_universe.parquet` defines SPEC-52WH-01's
   habitat. A fundamentals ingest bug that added, duplicated or mis-keyed rows would silently
   change the 52WH habitat — the exact failure mode of the §6.7 blank-symbol defect, which
   already narrowed the habitat ~10% and nobody noticed for months. A frozen spec's universe
   should not share a mutable artifact with an unfrozen family's ingest pipeline.
2. **Cost per query.** Every as-of call runs `validate` + `data_gate.load` over the **whole**
   frame before filtering. A quarterly walk-forward makes one such call per rebalance. Making
   the frame ~4-5× larger taxes every 52WH rebalance for data it never reads.
3. **Different rebuild cadence and different provenance.** AMFI is semi-annual, one publisher,
   18 files. Fundamentals are quarterly, per-company, and will be rebuilt far more often
   during development. Mixing them means every fundamentals rebuild rewrites the habitat file.
4. **Different symbol-space status.** The AMFI half carries the known §6.7 blank-symbol
   defect and its deliberate bug-for-bug reproduction in `parse_amfi.py`. A fundamentals
   corpus should be built ISIN-first and clean. Merging them would either import the defect or
   create two disagreeing symbol spaces in one file.

**Hard sequencing note:** the fundamentals corpus must join to the habitat on **ISIN**
(COVERAGE.md §6.2: NSE-symbol coverage in the top 1000 is 88.7–96.9%, never 100%). Since the
habitat's own symbol column is defective (§6.7) and a fix is already queued as OPEN OPERATOR
DECISION 2, **the habitat fix should land before the fundamentals symbol master is built**,
or the fundamentals fetch list inherits a ~10%-narrow universe exactly as the price panel did.

---

### 4.4 Reconciliation with the concurrently-drafted SPEC-QFM-01 §2.1

The spec proposes a **seven**-column schema against this note's six:

```
spec §2.1   (symbol, field, fiscal_period, period_end, announce_date, value, source [, isin])
this note   (symbol, field, effective_date,            announce_date, value, source [, isin])
```

**The spec is right and this note's §4.1 mapping should yield to it**, for a reason that only
shows up in the fundamentals case: it splits what the constituent store conflates.
`period_end` is a *date* (used for staleness, §2.6); `fiscal_period` is an *ordered label*
(`FY2019Q3`) that indexes the fiscal panel. They are not the same axis once non-March fiscal
year-ends exist (spec OPEN ITEM 4), and `ref(x, 4)` for a YoY delta must count **fiscal
periods**, not calendar dates — which is precisely the expression-layer mismatch flagged in
§4.2 item 4. The spec's extra axis is the clean fix for it.

Three consequences worth recording:

1. **This makes §4.3's "separate parquet file" recommendation a requirement, not a
   preference.** The column sets now differ outright, so fundamentals *cannot* share
   `pit_universe.parquet` even if one wanted to. The recommendation stands and is
   strengthened.
2. **The spec's §2.2 claim that there is "no `effective_date` condition for fundamentals" is
   correct in principle and harmless in practice if `_visible` is reused.** `_visible` ANDs
   `effective_date <= date` alongside the announce gate. For real filings
   `period_end <= announce_date` always, so with `effective_date := period_end` the extra
   condition can never bind and reuse is safe. Worth asserting in a test rather than
   reasoning about each time — this is exactly the class of "harmless until it isn't" that
   TRAP 1 was paid for.
3. **The `series_as_of` prototype in §4.2 carries over unchanged**, keying on
   `fiscal_period` instead of `effective_date`. Its verified vintage semantics — original
   figure before the restatement is announced, restated figure after — are precisely what the
   spec's §2.3 "restatements are NEW ROWS" rule requires at query time. **The spec states the
   storage rule; this note supplies the verified reader that honours it.** Neither is
   complete without the other.

---

## 5. Effort estimates and the decisive trade-off

Three routes survive §3. One of them is not a corpus route at all — it is a cheap probe that
makes the other two decidable, and it should run first.

### Route A — Licensed vendor feed (Accord ACE Datafeed, or Deutsche Börse "BSE India Corporate Data")

Buy the announcements-plus-results feed already joined, under licence.

| Step | Days |
|---|---|
| Enquiry to Accord + Deutsche Börse + C-MOTS (scope, history depth, announce-date field, as-reported policy, price) | **0.5** |
| Evaluate sample delivery against the five questions in §5.4 | 1 |
| Ingest + normalise delivered feed → `staging/` (schema drift, units, basis flags) | 3–5 |
| Store build + `COVERAGE.md` with volume/coverage assertions (TRAP 6) | 2 |
| `series_as_of` + units/basis conventions + tests | 1 |
| **Total engineering, AFTER a licence exists** | **~7.5–9.5 days** |

Plus **unknown procurement lead time** (realistically weeks) and **unknown cost**
(₹ five-to-six figures/yr is the plausible band for an Indian feed vendor; **UNVERIFIED**).

### Route B — Build the corpus from the BSE filing record

BSE announcements (`DissemDT`) for the timestamps + XBRL financial results for the numbers,
joined on ISIN + filing.

| Step | Days |
|---|---|
| BSE announcements ingest (already scoped in a prior pass: ~2–4 days) | 2–4 |
| XBRL results parse + normalise (multi-generation taxonomy, standalone/consolidated, units) | 4–6 |
| Line-item mapping to the closed field list, hand-validated, pre-registered in the spec | 2–3 |
| Store build + `COVERAGE.md` + assertions | 2 |
| `series_as_of` + tests | 1 |
| **Total engineering** | **~11–16 days** |

But the true cost is not the days. Route B carries three riders:

1. **It is entirely blocked on OPEN OPERATOR DECISION 1** (the exchange ToU ruling). If the
   ruling goes against automated collection, the whole route dies **after** the estimate is
   made, not before.
2. **The 2015 → 2017-04 hole is unfixable** (§3.1) — results XBRL did not exist. And pre-2019
   announcement PDFs are not reliably retrievable either. The corpus realistically starts
   ~2017-04, with a first clean YoY delta around 2018-04.
3. **Every silence trap in this program's history lives on this path**: soft-404s returning
   HTTP 200, `[]` without an `Origin` header, taxonomy drift across filing generations, and a
   join whose failure mode is a quietly missing row. It needs coverage assertions by year and
   by market-cap decile, not row counts.

### Route C — the EODHD feasibility probe (**not a corpus — a decision-cheapener**)

EODHD is the only prosumer vendor with a **documented per-row `filing_date`** on quarterly
financials. Two facts decide whether it is viable and both are answerable for **$60 and half
a day**: (a) is `filing_date` actually *populated* for rank-201-to-1000 `.NS` names, or null
outside the US; (b) is the history more than the "20 quarters for minor companies" its own
tiering implies.

| Step | Days | Cost |
|---|---|---|
| One month's Fundamentals subscription; pull ~20 habitat symbols; check `filing_date` population + quarter depth + a known restatement case | **0.5–1** | **$59.99** |

**This requires operator authorisation** — it is data acquisition, and this task is scoped to
scoping only. It is listed because it is by far the cheapest way to collapse a large
uncertainty, and because if it comes back positive it changes the ranking. Note that even a
positive result does **not** make EODHD the answer on its own: its tiers are marked
**"Personal use only"**, so a fund track record would need separate commercial licensing.

### The decisive trade-off

**It is not effort versus effort. It is money versus the ToU ruling.**

- **Route A does not need the ToU ruling** — the licence *is* the ruling, and a signed licence
  from a SEBI-ecosystem authorised vendor is a **due-diligence asset** on the path to PMS/AIF
  registration, where BSE and MCX are regulated counterparties. It costs money and weeks.
- **Route B is free of licence cost and entirely hostage to the ruling.** It costs ~2–3 weeks
  of engineering, produces a corpus with a permanent, disclosable 2015→2017 hole, and carries
  the risk that the ruling kills it after the work is scoped.

The asymmetry is that **Route A's enquiry is half a day and is already queued** under OPEN
OPERATOR DECISION 1. There is no version of this where sending that enquiry is the wrong first
move — it is cheap, it is reversible, it informs Route B's go/no-go, and Accord has now
surfaced **three times independently** across announcements, MCX and fundamentals.

### 5.1 Recommendation

1. **Send the vendor enquiry (0.5 day) before building anything.** Accord Fintech, Deutsche
   Börse MD+S, and C-MOTS. Fold it into the existing OPEN OPERATOR DECISION 1 enquiry rather
   than raising a new thread — it is the same email to the same counterparty.
2. **Close the §3.3 institutional hole (0.5 day)** so the procurement decision is made against
   a complete option set.
3. **Do not build any ingest** until the ToU ruling lands and the enquiry returns. Route B's
   estimate is only meaningful conditional on the ruling.
4. **Formally close the yfinance route** (§3.2) so it is not quietly retried as "a start".
5. **SPEC-QFM-01 was drafted concurrently on 2026-07-21 — so the remaining free work is
   closing its OPEN ITEMS, not drafting.** Two of them (2: source admissibility;
   3: the announce-date clock) are answered only by the vendor enquiry in step 1, which makes
   that enquiry the gating action for the freeze as well as for the data. Two more can be
   closed at zero cost today and should be: **OPEN ITEM 6** (is the balance-sheet input
   half-yearly rather than quarterly — §2.4 above says yes, direction certain, exact circular
   still to pin) and **OPEN ITEM 8** (the habitat blank-symbol defect — already queued as OPEN
   OPERATOR DECISION 2). Also worth reconciling before freeze: the spec's seven-column schema
   versus this note's six (§4.4 — the spec is right, and the consequence is that fundamentals
   must live in a separate parquet).

### 5.2 A sequencing constraint worth stating separately

The fundamentals corpus must join to the habitat on **ISIN** (COVERAGE.md §6.2: NSE-symbol
coverage in the top 1000 is 88.7–96.9%, never 100%). The habitat's symbol column currently
carries the §6.7 blank-symbol defect, whose fix is already queued as OPEN OPERATOR DECISION 2
ahead of C1 attempt 2. **The habitat fix should land before the fundamentals symbol master is
built**, or the fundamentals fetch list inherits a ~10%-narrow universe exactly as the price
panel did — the same defect, propagated into a second corpus.

### 5.3 A governance guard to build in from the start

qlib makes its PIT fields **syntactically distinct** (`$$roewa_q`) and **unusable without the
`P()` operator**, raising if referenced directly. That is a structural wall of the same species
as `screen_52wh`'s outcome-blind guard, and it is why a qlib user cannot leak PIT data by
accident. **Recommend the same here:** fundamentals fields carry a reserved `fin:` prefix
(§4.2) and any code path that reads them other than through the gated as-of accessor raises.
Cheap now, impossible to retrofit after a family has been built on it.

**And a specific warning about copying qlib's collector:** when the announcement date is
missing, qlib's PIT collector silently **imputes `pubDate = statDate + 45 days`** for quarterly
data, with no per-row flag. Forty-five days is also exactly the LODR Reg 33 deadline, so it is
the natural Indian default too — and it is wrong in a *directional* way, because healthy
companies report early and stressed ones report at the wall (§2.3). If any announce date is
ever imputed, it **must** carry an `announce_basis` flag per row, exactly as the AMFI rows
already do.

### 5.4 The five questions to put to any vendor

1. Do you supply a **per-row result-announcement/dissemination date** for quarterly results,
   historically back to 2015 — or only a fiscal period label? *(Vendor marketing says
   "announcement date" for things that are period-end plus a convention. Ask for a sample row.)*
2. Are figures **as first reported**, or overwritten on restatement? Do you retain **vintages**?
3. What is the **coverage rate for NSE/BSE companies ranked 201–1000 by market cap**, by year?
   *(Not "we cover India" — a percentage, by year.)*
4. How is **Q4** handled — filed, or derived as `FY − 9M`? If derived, what date is stamped on it?
5. Are **standalone and consolidated** carried as separate series, or is one silently
   substituted for the other when missing?

---

## 6. Proposed `SETUP_OF_RECORD.md` open-item entry

**FOR OPERATOR APPROVAL — NOT APPLIED.** `SETUP_OF_RECORD.md` has not been edited. The text
below is drafted to match the numbered house style of the existing "Genuinely open items"
list. Item numbering assumes it appends as **item 6** after the current five.

Two housekeeping observations to fold in at the same time, at the operator's discretion:
existing **item 3** (absolute market cap missing from the PIT store) was **CLOSED 2026-07-20**
per `CLAUDE.md` and could be marked as such; and the file's header still says "42 tests"
against a current suite of 233.

---

```markdown
6. **PIT fundamentals corpus does not exist — SPEC-QFM-01 cannot be frozen
   without it** (new 2026-07-21). `data/reference/` holds only `pit/` (AMFI
   constituents + mcap ranks), `rename/` and `tri/`. The PIT store is 274,966
   rows across 4 fields, and **all four are AMFI market-cap derivatives**
   (`mcap_rank`, `avg_mcap_cr`, `bse_avg_mcap_cr`, `nse_avg_mcap_cr`). There is
   no fundamentals data anywhere in the repo, at any depth. SPEC-QFM-01
   ("fundamental deltas") holds **shadow slot 1** — first in the Tier 2 queue —
   and was drafted 2026-07-21 (DRAFT, no `sha256`, no register row); its OPEN
   ITEMS 2 and 3 are precisely this dependency, so **the spec cannot be
   hash-frozen until this item closes.** Until 2026-07-21 the family held its
   slot for three days as a name with no document and no data, and the data
   dependency was on no list at all — unlike the filing-timestamp and MCX gaps,
   it was never even scoped. Classic TRAP 6: nothing errors, because nothing
   had ever asked for the data.
   **The binding constraint is the ANNOUNCE DATE, not the numbers.**
   `src/pit_universe.py` gates every as-of query through
   `data_gate.load(frame, "announce_date")`, so a row's announce date is what
   makes it visible to research and what enforces the seal. A source without a
   true per-company publication date cannot be made point-in-time and is
   unusable regardless of quality — and the AMFI `+25d` trick does NOT carry
   over, because per-company reporting lag runs 15–45 days, clusters at the
   LODR wall for small caps, and is **correlated with the news** a delta family
   trades on. Applying that filter: yfinance FAILS outright (~5 quarters max,
   `asOfDate` is the period end, no vintage dimension — recommend formally
   CLOSING it); Screener/Tijori/Tickertape/Upstox carry no date; Trendlyne has
   one but forbids machine-readable databases in its ToU; the as-first-reported
   prosumer product that exists for the US (Sharadar) **has no Indian
   equivalent at any retail price**. Two hard facts constrain every route:
   BSE made results XBRL mandatory only from **2017-04-01**, so ~2015→2017 is a
   structural hole no vendor can fill; and India has **no quarterly balance
   sheet** (LODR Reg 33 is P&L quarterly, BS/CF half-yearly), so quarterly
   signal is P&L-only. Restatements matter more here than usual: the **Ind AS
   transition (Phase 2, 1 Apr 2017, covering most of the 201–1000 habitat)**
   restated comparatives inside the dev window, so any YoY delta straddling
   FY2017-18 compares against a number that was never published.
   **Viable routes, in order:** (A) licensed vendor — Accord Fintech ACE
   Datafeed or **Deutsche Börse "BSE India Corporate Data"**, which bundles
   corporate announcements AND financial results in one XBRL feed, i.e. the
   required join sold pre-joined; ~7.5–9.5 days engineering after a licence
   exists, cost UNVERIFIED. (B) build from the BSE filing record; ~11–16 days,
   **entirely blocked on the exchange ToU ruling** (open item 2). (C) a $60,
   half-day EODHD probe to test whether its documented `filing_date` is
   populated for Indian small caps — **requires operator authorisation, as it
   is data acquisition.**
   **The decisive trade-off is money vs. the ToU ruling, not effort vs.
   effort** — a licence makes the ruling moot and is itself a due-diligence
   asset at PMS/AIF registration. **Accord has now surfaced independently in
   three research passes** (BSE announcements, MCX, fundamentals); one enquiry
   could dissolve three open items at once, and it belongs in the OPEN OPERATOR
   DECISION 1 email rather than a new thread.
   **Immediate no-cost action: SPEC-QFM-01 was drafted 2026-07-21 — it now
   needs its OPEN ITEMS closed, not more drafting.** Note the schema divergence
   to settle: the spec's §2.1 uses seven columns splitting `fiscal_period` from
   `period_end`; that is the correct call and it means the fundamentals store
   **cannot** share `pit_universe.parquet` and must be a separate artifact.
   **Sequencing: the habitat blank-symbol
   fix (open decision 2) must land BEFORE the fundamentals symbol master is
   built, or that corpus inherits the same ~10%-narrow universe the price panel
   did.** Full scope: `analysis/QFM_fundamentals_scope.md`.
   **Residual gap in that note, stated rather than hidden:** the institutional
   survey is INCOMPLETE — Refinitiv/LSEG, Bloomberg, S&P Capital IQ, FactSet,
   Morningstar and Orbis were NOT researched (the pass hit a session limit).
   ~0.5 day to close; unlikely to change the recommendation, but "we did not
   look" is a weaker position at due diligence than "we looked and they were
   too expensive."
```

---

## 7. Summary of what is verified versus assumed

| Claim | Status |
|---|---|
| No fundamentals data anywhere in the repo | **VERIFIED** — full `data/` sweep + repo-wide grep |
| PIT store = 274,966 rows, 4 fields, all AMFI mcap derivatives | **VERIFIED** — read from the parquet |
| Habitat = 1,249 distinct symbols over the dev window | **VERIFIED** — computed via `universe_as_of` |
| `announce_date` is the seal-gated column | **VERIFIED** — `pit_universe._visible` → `data_gate.load` |
| Existing row shape holds vintages correctly | **VERIFIED** — synthetic restatement frame, four query dates |
| `series_as_of` is missing and is ~6 lines | **VERIFIED** — prototyped and run |
| LODR Reg 33: 45 days quarterly / 60 annual; consolidated required in addition to standalone | **VERIFIED** (SEBI LODR FAQ material) |
| Ind AS Phase 1 from 1 Apr 2016 (≥₹500cr), Phase 2 from 1 Apr 2017 (all listed) | **VERIFIED** (MCA roadmap, secondary sources) |
| BSE results XBRL mandatory from 2017-04-01 | **VERIFIED** (BSE circular DCS/COMP/28/2016-17, via secondary sources) |
| yfinance ~5-quarter cap; `asOfDate` = period end; no vintage | **VERIFIED** (yfinance source + issue tracker) |
| qlib PIT schema, `_next` revision chain, `P()` operator wall, +45d imputation | **VERIFIED** (qlib source) |
| Half-yearly BS/CF requirement and its first applicable period | **UNVERIFIED** — direction certain, exact circular not pinned |
| Announce-date availability at Prowess / Capitaline / ACE / C-MOTS | **UNCLEAR** — the decisive question, must be asked |
| Deutsche Börse BSE Corporate Data history depth and price | **UNVERIFIED** — enquiry required |
| EODHD `filing_date` population for Indian small caps | **UNVERIFIED** — Route C probe settles it |
| Refinitiv, Bloomberg, Capital IQ, FactSet, Morningstar, Orbis | **NOT RESEARCHED** |
| NSE results-XBRL commencement date | **UNVERIFIED** — NSE out of scope regardless |
| `SPEC-QFM-01.md` / `SPEC-PEAD-01.md` created 2026-07-21, both DRAFT and unhashed | **VERIFIED** — filesystem + `git status` |
| No QFM register row exists | **VERIFIED** — `research_register_v2.csv` |

---

## 8. What was NOT done (by constraint)

- **No data was acquired, downloaded, scraped, or bulk-fetched.** No exchange endpoint was
  touched. No account was created and no data API was called.
- **No outcome data was touched.** No prices, no returns, no backtests. This note is
  outcome-blind and is not a trial.
- **No file was edited outside `analysis/`.** `SETUP_OF_RECORD.md`, `SEAL.md`, the frozen
  spec, `overlay_log.csv` and `research_register_v2.csv` are untouched. Nothing was committed.
- **§3.3's institutional survey is incomplete** and the web-search budget was exhausted before
  it could be closed by hand (§3.3 scope warning).

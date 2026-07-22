# Accord Fintech (ACE Datafeed) — Vendor Enquiry Pack

**Status: DRAFT ONLY. NOTHING HAS BEEN SENT.**
Prepared 2026-07-21. No email was sent, no web form was submitted, no messaging or
mail tool was invoked. The operator sends this, or does not.

Purpose: one vendor enquiry that may dissolve two open data blockers at once
(exchange filing timestamps; MCX futures history) and possibly a third
(point-in-time quarterly fundamentals). See `governance/DECISIONS.md` —
OPEN OPERATOR DECISION 1 (exchange terms of use).

---

## PART 1 — WHAT WAS VERIFIED ABOUT THE VENDOR

### Verified from the vendor's own public pages (primary source = vendor, self-asserted)

| Item | Finding | Source |
|---|---|---|
| Legal entity | Accord Fintech Private Limited | vendor site, D&B listing |
| Registered address | 1201 B, A Wing, Rupa Renaissance, Juinagar, MIDC Road, Navi Mumbai 400705, India | accordfintech.com/contact-us |
| Main phone | +91-22-67834000 / +91-22-48904000 | accordfintech.com/contact-us |
| General email | info@accordfintech.com | accordfintech.com/contact-us |
| Enquiry form | https://www.accordfintech.com/enquiry — fields: Name*, Email*, Mobile*, "Products Interested in" (dropdown), Comments, CAPTCHA. No stated character limit. | accordfintech.com/enquiry |
| Regional numbers | Bangalore +91-9379404042 · Delhi +91-9312101077 · Kolkata +91-9378077772 · Ahmedabad +91-9375404042 · Chennai +91-9362040819 · Hyderabad +91-9346216482 · Pune +91-7666999805 | accordfintech.com/contact-us |
| Business hours | 09:30–18:30 IST, Mon–Sat, excl. public holidays | accordfintech.com/contact-us |
| Authorised-vendor claim | "Authorized data feed vendor of BSE/NSE/MCX/NCDEX exchange for their products." | accordfintech.com/market-data-feed |
| Product line | ACE Equity Nxt, ACE MF Nxt, ACE Datafeed, ACE Wealth Manager, ACE Web, ACE Report, ACE TP, ACE Transconnect | accordfintech.com |
| ACE Datafeed content | "Stock Market data, Equity, Derivatives, IPOs Commodities, Currency, Mutual Funds, Corporate Announcements, News, Other Markets, Company Information – Historical, intraday and End of the Day prices." Explicitly lists "Corporate Action – BSE EOD" and "Commodity Prices [MCX, NCDEX]". | accordfintech.com/data-feed-solutions, /market-data-feed |
| Delivery | "We provide financial information feed through FTP and API." CSV / JSON indicated. | accordfintech.com/data-feed-solutions |
| ACE Equity Nxt scope | ">40,000 Indian companies, including 7,000 listed and 33,000 private"; "1750 unique financial data fields compiled from the Annual Report"; standalone & consolidated; Ind AS format for annual and quarterly; Windows app, cloud-hosted, Excel plug-in | accordfintech.com/ace-equity-nxt |
| Related brand | ACE Analyser (aceanalyser.com), founded 2008, same group | vendor site, Tracxn |

### NOT verified — treat every line below as an open question for the vendor

1. **The authorised-redistributor claim is self-asserted and was NOT independently
   confirmed.** NSE's and MCX's published vendor lists could not be retrieved
   (NSE PDF endpoints timed out; the MCX list URL returned HTTP 403 to a normal
   browser fetch). Accord Fintech was therefore neither confirmed nor refuted on
   any exchange-published list. **Do not record the claim as fact until the
   vendor supplies the licence basis in writing.**
2. **Every exchange list that does exist is titled "Authorised REALTIME Data
   Vendors."** Real-time authorisation says nothing about the right to
   redistribute a HISTORICAL archive. This is exactly the trap already paid for
   with the BSE feed (~₹9L/yr, real-time only, no historical-announcements SKU).
   The two are separate licences and must be asked about separately.
3. **No evidence found either way that BSE announcement records carry
   `DissemDT` or `DT_TM`.** The vendor advertises "Corporate Announcements" and
   "Corporate Action – BSE EOD" but publishes no field list. Timestamp
   granularity is entirely unknown.
4. **No evidence of any SEBI Reg 30 categorisation** in the vendor's product.
   Neither exchange tags it natively, so a vendor that does would be a
   material find — and one that claims to must be asked HOW.
5. **MCX coverage depth, and whether it is anything more than real-time
   prices, is unknown.** "Commodity Prices [MCX, NCDEX]" and "Bullion Price –
   EOD" are the only public statements. No contract-level futures history,
   no field list, no start date. The known structural problem — MCX publishes
   no settlement-price column, only `Close` — must be put to them directly.
6. **ACE Equity Nxt history depth in years is not published**, nor is the
   as-originally-reported vs restated question addressed anywhere public.
   Data is described as "directly linked to Annual report", which suggests
   restatement follows the latest annual report — i.e. possibly NOT
   point-in-time. This is the single most important question in section C.
7. **No pricing, no trial terms, no sample data, no API documentation** is
   public anywhere. All must be asked.
8. **No dedicated sales email exists publicly** — only `info@`. Expect the
   first reply to be a routing reply; the enquiry is written to survive that.

---

## PART 2 — DRAFT EMAIL (do not send until reviewed)

**To:** info@accordfintech.com
**Subject:** Data licensing enquiry — historical BSE announcements, MCX futures history, point-in-time fundamentals

---

Dear Accord Fintech team,

I am writing to enquire about licensing historical Indian market data for
quantitative research use.

I run a systematic research programme covering Indian listed equities and
commodity futures. The work is currently pre-commercial and self-funded; the
intended path is registration as a SEBI Portfolio Manager in due course, at
which point licensed and auditable data provenance becomes a compliance
requirement rather than a preference. I am approaching that requirement now
rather than retrofitting it, which is why I would prefer a licensed vendor
relationship over public sources.

Three datasets are in scope, listed below with the specific questions I need
answered to evaluate fit. I have kept them precise deliberately — a short,
concrete reply will be more useful to both of us than a general brochure.

One point applies across all three and matters most to me. For each exchange
whose data you would supply, I would like written confirmation that Accord
Fintech is an authorised redistributor, and confirmation of the licence basis
under which the historical archive (as distinct from any real-time feed) is
redistributed to a client for internal research use. I understand these are
often separate licences. A clear written statement on this is, for my purposes,
as valuable as the data itself, and I would rather establish it at the outset
than discover a gap later.

If a call is easier than a written reply, I am happy to arrange one — though I
would still appreciate the licence position in writing.

Kind regards,

[FULL NAME]
[DESIGNATION — or omit this line entirely if there is no firm]
[FIRM / ENTITY NAME — or "independent researcher" if no entity is registered yet]
[EMAIL] · [PHONE]
[CITY], India

---

### DATASET REQUIREMENTS

**A. BSE corporate announcements — historical archive**

- Earliest date from which the announcement archive is available.
- Exact field list per announcement record. Specifically: do your records
  carry BSE's **`DissemDT`** (the dissemination / "became public at" timestamp)
  and **`DT_TM`** (submission timestamp)? If only one, which — and at what
  precision (date only / minute / second)?
- Is the announcement PDF or full text supplied, or only metadata? From what
  date is the attachment available?
- Do you supply any **SEBI Regulation 30 categorisation** of announcements
  beyond the exchange's own subcategory codes? If so, is it exchange-supplied
  or Accord-derived, and is the mapping documented? If Accord-derived, is the
  methodology available for review?
- Are announcements keyed to **ISIN** as well as ticker, and is a symbol-change
  / rename history supplied?
- Is the historical archive a **separate SKU from the real-time feed**, and can
  the historical archive be licensed **on its own**?
- Delivery: one-time bulk backfill (FTP / S3 / other), then incremental? File
  format and schema documentation?

**B. MCX commodity futures — historical**

- Earliest date available, and at what granularity (daily bhavcopy / intraday
  / tick).
- Is the data **contract-level** (one row per contract per day, all listed
  expiries) rather than a single continuous or spot series? Term-structure
  reconstruction requires the former.
- Exact field list per contract-day. Specifically: do you supply a
  **settlement price** distinct from `Close`? MCX's own published bhavcopy
  does not, and this distinction is material to me — please be precise rather
  than mapping one onto the other.
- Are **open interest** and **volume** supplied per contract, and is there any
  flag distinguishing a genuinely traded close from an administratively
  marked one on an illiquid contract?
- How are **contract-specification changes** (lot size, quotation basis)
  handled historically — is there a contract master with effective dates?
- Same licence question as above: authorised redistributor for MCX, and does
  the licence cover **historical** data for internal research?

**C. Point-in-time quarterly fundamentals (ACE Equity / ACE Datafeed)**

- Universe and history: how many listed names, and from what date are
  **quarterly** results available? My working universe is roughly 1,300 listed
  names from around 2015.
- **The critical question:** are figures supplied **as originally reported**,
  or are they overwritten when a company restates? If both are retained, how
  is a prior vintage retrieved?
- Is a reliable **announcement / result-declaration date** supplied per
  quarterly record — the date the figure first became public, as distinct from
  the period-end date? Timestamp precision?
- Is the fundamentals data available through **ACE Datafeed (FTP / API)** as a
  bulk historical file, or only via the ACE Equity Nxt desktop application?
- Are standalone and consolidated series both supplied, with a flag?

**D. Commercial — all datasets**

- **Sample or trial:** can you provide a sample extract (e.g. one month of
  announcements, one month of MCX contract-day rows, 20 companies of
  quarterly fundamentals) so I can verify schema and field semantics before
  committing?
- **Indicative pricing** per dataset, distinguishing the one-time historical
  backfill from any ongoing subscription. An indicative range is sufficient at
  this stage.
- **Licence scope:** internal research and back-testing by a single entity, no
  onward redistribution, no display to third parties. Is derived output
  (research results, and later a fund's trading decisions) unrestricted under
  your standard terms?
- Minimum contract term, and whether a historical-only, no-subscription
  purchase is possible.

---

## PART 3 — SHORT VERSION FOR THE WEB CONTACT FORM

Use at https://www.accordfintech.com/enquiry — select **ACE DATAFEED** in the
"Products Interested in" dropdown, paste the block below into Comments.

> Enquiring about licensed HISTORICAL data for quantitative research (pre-commercial,
> SEBI PMS registration intended in due course). Three datasets: (1) BSE corporate
> announcements archive — need the field list, and specifically whether DissemDT and
> DT_TM timestamps are included; (2) MCX futures history at contract level — need to
> know if any settlement price is supplied distinct from Close; (3) point-in-time
> quarterly fundamentals, as-originally-reported with announcement dates, ~1,300
> listed names from 2015.
> For each: earliest history date, exact fields, FTP/API delivery, whether historical
> is a separate SKU from real-time, sample availability, indicative pricing.
> Please also confirm in writing that Accord Fintech is an authorised redistributor
> for each exchange, and the licence basis covering HISTORICAL data for internal use.
> Happy to take a call. — [NAME], [EMAIL], [PHONE]

---

## PART 4 — OPERATOR NOTE

### Fill in before sending

- `[FULL NAME]`, `[EMAIL]`, `[PHONE]`, `[CITY]`.
- `[FIRM / ENTITY NAME]` — **if no entity is registered, delete the line and the
  `[DESIGNATION]` line entirely.** Do not invent a firm, a title, or a
  credential. "Independent researcher" is credible; a fabricated firm name is a
  liability at exactly the due-diligence stage this exercise exists to serve.
- Decide whether to send from a personal or a domain email. A domain address
  materially raises the chance of an institutional-desk reply rather than a
  retail-product pitch.
- Optional: name a target timeline ("evaluating in the next 4–6 weeks"). Sales
  desks prioritise dated enquiries. Only include it if it is true.
- Decide whether dataset C is in scope at all. Dropping it shortens the email
  and sharpens the two blocking asks; keeping it is the cheaper path if the
  fundamentals dependency is likely to be needed anyway.

### What has been deliberately kept OUT

No strategy logic, no signal definitions, no performance figures, no research
calendar, no mention of the seal, cutoff, register or any internal governance
artefact. The only programme facts disclosed are the shape of the data needed —
universe size, date range, and field-level requirements — which cannot be
omitted without making the enquiry unanswerable. Keep it that way in any reply.

### What a GOOD reply looks like

- Names the specific licence or agreement under which the historical archive is
  redistributed, and says whether it is separate from the real-time licence.
- Answers the `DissemDT` / `DT_TM` question **directly and by field name**,
  including "no, we only carry date" if that is the truth.
- States a start date for each archive rather than "extensive history".
- Confirms MCX data is contract-level and states plainly whether a settlement
  price exists separately from `Close` — including "no, MCX does not publish
  one" (which is the correct answer, and a vendor who says so is trustworthy).
- Offers a sample extract or schema document without requiring a commitment.
- Distinguishes as-reported from restated fundamentals unprompted.

### Red flags

- **"We are an authorised vendor" repeated without naming the licence.** The
  claim is already on their website; the enquiry asks for the basis. A restated
  claim is a non-answer.
- **Real-time pricing quoted in response to a historical-archive question.**
  This is the exact failure mode already seen with the BSE feed at ~₹9L/yr.
  If the quote is per-month-per-user for a live feed, the historical question
  was not read.
- **A settlement-price column asserted for MCX without explanation.** MCX does
  not publish one. A vendor claiming one is either deriving it (and must say
  how) or has mapped `Close` onto the label — which would be silently wrong in
  a way that corrupts any carry or term-structure work. Do not accept
  "yes, settlement is included" without a written definition.
- **Reg 30 categorisation claimed without a documented methodology.** Neither
  exchange tags it, so any categorisation is vendor-derived. Undocumented
  derivation is worse than none.
- **"All history available" / "since inception"** with no date. Ask again.
- Refusal to supply a sample, or a demo of the desktop app offered in place of
  a schema. The desktop product is not the deliverable; the feed is.
- A licence that forbids derived commercial use, or requires per-user display
  licensing for what is a machine-consumed research feed. Read this clause
  before pricing.

### The answer that closes the exchange ToU ruling

**A written statement from Accord Fintech that it is an authorised
redistributor of BSE corporate announcements (and separately of MCX data),
naming the licence, AND confirming that the licence permits supplying the
HISTORICAL archive to a client for internal research use.**

That single confirmation would let OPEN OPERATOR DECISION 1 be closed in
`governance/DECISIONS.md` as: *licensed vendor route adopted; no automated
collection from exchange websites is undertaken.* It dissolves the NSE ToU
prohibition entirely — not by reinterpreting it, but by not relying on it —
and removes the need to rule on BSE's unverified clauses at all.

Note what does NOT close the ruling: a real-time-only licence. If the reply
confirms authorisation for the live feed but is silent or negative on the
historical archive, the ToU question stands open exactly as it does today, and
the ruling must still be made on its own terms.

Two further outcomes worth recording either way, since both are governance
assets:

- If the vendor confirms MCX contract-level history with no settlement price,
  that independently corroborates the constraint already identified and can be
  cited in any future spec that touches commodity carry.
- If the vendor declines or cannot supply the historical announcement archive,
  that is itself evidence that the licensed route was pursued in good faith and
  found unavailable — which is a materially stronger position at due diligence
  than never having asked.

Log the outcome — reply, non-reply, or refusal — in `governance/DECISIONS.md`.
A vendor who does not reply within two weeks is also a finding.

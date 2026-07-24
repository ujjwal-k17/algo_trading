# Habitat defect fix — report of record

**Date of fix: 2026-07-22. Operator-approved and committed 2026-07-23 (`d4092ca`).**
Closes OPEN OPERATOR DECISION 2. Companion documents: the independent verification memo
`analysis/habitat_defect_verification.md` (pre-fix measurement, bias direction), and
`data/reference/pit/COVERAGE.md` §6.7 (defect entry) / §6.8 (fetch-list consequence).
Scope: data groundwork only — **C1-52WH-0002 remains unauthorized**; nothing here touches
outcome data or the research register.

---

## 1. The defect

The original A1 parser (never persisted to the repo) derived `symbol` from AMFI's NSE
column with a BSE fallback that fired **only on the literal `-` sentinel, never on an
empty cell**. Only the 2025H2 and 2026H1 editions use `-`; all 16 editions 2017H2–2025H1
leave the missing NSE cell EMPTY. The fallback therefore fired **zero times** across the
entire pre-2025H2 corpus (`symbol_exchange == 'BSE'` count: 0), and **50,505 rank rows
carried a blank symbol despite AMFI supplying a BSE ticker**.

The blank rows were then structurally invisible: `pit_universe.snapshot_as_of` groups by
`symbol`, and pandas `groupby` drops NA keys by default. No error, no log line — the
program's characteristic failure (TRAP 6). Consequences on record:

- `universe_as_of(store, date, "201-1000")` returned **719 names instead of ~800**
  (band named counts ran 690–766 of 800 across editions).
- Every 52WH result to date, including the withdrawn C1-52WH-0001, ran on a habitat
  ~10% narrower than SPEC-52WH-01 §habitat specifies.
- The missing names never reached the price-panel fetch list (`build_price_panel.py`
  draws from the store), so the survivorship analysis undercounted its own hole.
- COVERAGE.md §6.2's original "100% top-1000 NSE-symbol coverage" claim was wrong for
  the same root cause (empty cell vs `-` sentinel); true figure 88.7%–96.9%, corrected.

## 2. The fix

All in `scripts/parse_amfi.py`, committed as `d4092ca`:

1. **`derive_symbol`**: NaN, empty, whitespace-only and `-` are now all treated as a
   missing NSE cell; any of them triggers the BSE fallback. A row is blank/`NONE` only
   when neither exchange supplies a ticker.
2. **One symbol derivation for both staging halves.** `parse_amfi.py` now generates
   `amfi_mcap_rank.csv` (field `mcap_rank` = AMFI `Sr. No.`) as well as
   `amfi_avg_mcap.csv`, from a single `derive_symbol` pass per edition — the two halves
   cannot drift because they no longer have separate parsers.
3. **Provenance assertion** (`verify_against_ranks`, runs BEFORE the old rank file is
   overwritten): the new symbol space must equal the previous one **plus the fix and
   nothing else** — it may FILL a blank symbol (fallback firing at last) or BLANK one
   (collision rule below), but a non-blank ticker rewritten to a different non-blank
   ticker is a hard MISMATCH. ISIN and Sr.-No. ordering must be untouched.
4. **Diagnostic column** `symbol_recovery` (`NSE` / `BSE_FALLBACK` / `DROPPED_COLLISION`
   / `NO_TICKER`) carried in staging, not a store field.

## 3. The collision rule (pre-committed)

A recovered BSE ticker already in use in the same edition — by a name whose NSE cell is
populated, or by another recovered row — is **DROPPED and reported unrecoverable**. Never
overwritten, never merged, never heuristically disambiguated: attributing one company's
rows to another company's ticker is silent data corruption; a disclosed gap is only a gap
(TRAP 4 logic).

Measured on the rebuild: **74 rows dropped store-wide, 5 of them in band 201–1000**
(SESHAPAPER 2019H2 + 2020H1, PAISALO 2022H1, JASH 2025H1 + 2025H2). Full list with
reasons in `data/reference/pit/symbol_recovery_report.csv` (3,397 rows total: 74
`DROPPED_COLLISION` + 3,323 `NO_TICKER`, of which 53 no-ticker rows sit in band).

## 4. Measured effect (store rebuilt 2026-07-22)

| Quantity | Before | After |
|---|---|---|
| Band 201–1000 named, per edition | 690–766 of 800 | **794–799 of 800** |
| As-of habitat 2018-01-25 | 716 | **796** |
| As-of habitat 2019-03-01 | 719 | **824** |
| As-of habitat 2024-07-16 | 856 | **927** |
| Store rows | ~275k | **297,515** |
| Blank-symbol rank rows | 50,505 | 3,397 (74 collision + 3,323 no-ticker) |

Store field counts after rebuild: `mcap_rank` 89,891 · `avg_mcap_cr` 89,729 ·
`bse_avg_mcap_cr` 84,777 · `nse_avg_mcap_cr` 33,118. Staging: rank half 89,895 rows,
mcap half 207,781 rows; 53,380 staged rows now carry `symbol_exchange == 'BSE'`.

## 5. Honest scope correction (COVERAGE.md §6.8)

The recovery is real but **smaller than the original ~10% / ~80-name framing**. AMFI
ranks by ALL-EXCHANGE market cap, and ~73% of the recovered names are BSE-primary
companies never listed on NSE. Survivor-conditioned against AMFI 2026H1's working NSE
column, the genuinely **NSE-tradeable** recovery is **8–26 names per edition
(1.1%–3.7%)** — not ~80. The fix was still correct to land before C1 attempt 2 (the
verification memo's §9 shows the missing names skew toward delistings, i.e. toward the
far-from-high population the 52WH screen targets, so the pre-fix increment was
understated), but the *size* of the payoff is the corrected figure, and any C1 write-up
must use it.

## 6. Fetch-list decision (COVERAGE.md §8) — RESOLVED 2026-07-23, operator-approved

**Adopted rule: FETCH AND ALLOW TO FAIL.** BSE-tagged symbols are NOT excluded at fetch
time. The `build_price_panel.py` fetch list grows **1,412 → 1,600 symbols (+188)**; of
the 188 added, only 36 are corroborated NSE-listed in AMFI 2026H1 and 132 still exist at
all, so unservability was *estimated* at ~250/1,600 (~16%), up from 102/1,412 (7.2%).

Rationale (stated to the operator, uncontested): **a measured unservable count beats a
filtered guess** (TRAP 4 — never proxy or pre-judge what can be observed). An
unfetchable name cannot enter either arm of the backtest, so the research question is
unaffected either way; what changes is the survivorship-caveat paragraph of the C1
write-up, which should quote the measured count from `price_panel_missing.txt`, not an
exclusion rule's assumption. The store keeps the symbol regardless of exchange;
`symbol_exchange` remains a staging-only column.

## 7. Guards added alongside the fix

- `scripts/build_pit_universe.py::deduplicate` — named-symbol duplicate collapse is now
  a HARD STOP (it means the staging halves drifted); blank-symbol collapse is disclosed
  per field with distinct-ISIN counts instead of a bare count (pre-fix, the bare count
  silently absorbed 22,710 rows).
- `src/pit_universe.py::_require_field` — an as-of query against a field with ZERO rows
  in the store now raises instead of returning an empty universe (a build defect must
  not read as a legitimate empty state; TRAP 6).
- Tests (in the 257-passing suite): fallback fires on empty AND dash; whitespace-only
  cells count as missing; collisions drop rather than overwrite; both staging halves
  share one symbol space; per-edition band 201–1000 named count ≥ 794/800 (coverage
  assertion, not a row count — TRAP 1/6); no recovered ticker names two companies in one
  edition; never-ingested field raises while present-but-empty returns `[]`.

## 8. What this does and does not unblock

- **Unblocked**: the price-panel rebuild under the adopted fetch rule (data groundwork,
  ROADMAP item 7(b) — done).
- **Still OPEN**: C1 ATTEMPT 2 authorization (ROADMAP item 7(c)). A new
  `C1-52WH-0002` register row requires explicit operator authorization; none exists.
  No outcome contact has occurred in any of the work described here.

# Independent verification — OPEN OPERATOR DECISION 2 (inherited habitat defect)

Date: 2026-07-21. Scope: outcome-blind. No price panel, return series, backtest output or
trial was loaded or run. Evidence is PIT constituent data only
(`data/reference/pit/`, the AMFI raw xlsx corpus, and the current NIFTY500 constituent CSV).

Read-only throughout: no staging file, parquet store, parser or governance file was modified.

---

## 0. Verdict table

| Claim | Status | Measured |
|---|---|---|
| (a) BSE fallback fires only on `-`, never on empty; effectively never fired pre-2025H2 | **CONFIRMED (exactly)** | `symbol_exchange=='BSE'` count is **0 in all 16 editions 2017H2–2025H1**, 2950 in 2025H2, 2954 in 2026H1 |
| (b) 50,505 rank rows carry a blank symbol | **CONFIRMED** | **50,505** in `staging/amfi_mcap_rank.csv` for 2017H2–2025H1 (50,873 all periods). In the parquet store: **50,501** / 50,869 — 4 rows lost to de-duplication |
| (c) blank rows invisible to `snapshot_as_of` via groupby NaN-drop | **CONFIRMED** | mechanism reproduced; see §3 |
| (d) habitat returns 719 instead of ~800 | **CONFIRMED but MISLEADING** | 719 is correct **only for 2019-03-01**. Actual as-of habitat ranges **716 → 856** across the dev window; per-edition named count ranges **690 → 766**. And ~800 is the **wrong benchmark** — see §5 |
| (e) missing names never reach the price-panel fetch list | **CONFIRMED (by construction)** | fetch list is built from `universe_as_of`; blank symbols cannot appear in it |
| (f) COVERAGE.md §6.2 claimed 100%, true figure 88.7%–96.9% | **CONFIRMED — and already corrected in the file** | my independent recount reproduces COVERAGE.md's corrected table **row for row** (2020H1 = 887, 2026H1 = 969 → range 88.7%–96.9%) |

Plus **two defects NOT on the record**, found during verification — §6 and §7. One of them
(§6) silently destroys 22,706 store rows.

---

## 1. Claim (a) — the fallback condition

`scripts/parse_amfi.py:166`

```python
dashed = nse.eq(MISSING_SENTINEL).fillna(False).astype(bool)
```

`scripts/parse_amfi.py:171`

```python
bse_ok = dashed & bse.notna() & bse.ne(MISSING_SENTINEL) & bse.ne("")
```

`bse_ok` is gated on `dashed`, and `dashed` is true only for the literal `"-"`. An empty /
NaN NSE cell is forced to `False` by the `.fillna(False)` — so the BSE ticker is never
consulted. The empty cell then flows to `parse_amfi.py:168` (`symbol = nse.fillna("")`) and
yields a blank symbol tagged `NSE` at line 169.

The parser's own docstring (`parse_amfi.py:144-161`) states this and calls it "a DEFECT
inherited from the original ingest". It is reproduced deliberately so both staging halves
share one symbol space.

**CONFIRMED, and stronger than stated.** Measured from `staging/amfi_mcap_rank.csv`, the
`symbol_exchange=='BSE'` tag (i.e. the fallback actually firing) appears:

| edition | fallback fired |
|---|---|
| 2017H2 … 2025H1 (16 editions) | **0** |
| 2025H2 | 2,950 |
| 2026H1 | 2,954 |

Not "effectively never" — **literally never**, in every pre-2025H2 edition. Confirmed
against the raw source: in `amfi_2020H1_avg_mcap.xlsx` the top-1000 rows contain **113
empty NSE cells and zero `"-"` cells**.

`scripts/build_pit_universe.py` contains no symbol logic; it only validates and
de-duplicates (§6).

---

## 2. Claim (b) — recount

Store `data/reference/pit/pit_universe.parquet`: **274,966 rows**, 4 fields.

| field | rows | blank symbol |
|---|---|---|
| mcap_rank | 89,891 | 50,869 |
| avg_mcap_cr | 78,530 | 39,508 |
| bse_avg_mcap_cr | 73,427 | 36,201 |
| nse_avg_mcap_cr | 33,118 | **0** |
| **total** | **274,966** | **126,578** |

Blank is `symbol is NA` (0 empty-string rows — the CSV blanks became NaN at
`pd.read_csv`).

- mcap_rank blank, **2017H2–2025H1**: **50,501** in the store; **50,505** in
  `staging/amfi_mcap_rank.csv`.
- The 4-row difference is de-duplication in `build_pit_universe.py` (§6). **The recorded
  figure 50,505 is the staging count and is exactly right.**
- Blank rows announced pre-cutoff (< 2024-07-17), i.e. research-visible: **41,417**.

Note the last row of the table: **`nse_avg_mcap_cr` has zero blank-symbol rows.** Every row
where AMFI omitted the NSE symbol also has no NSE market-cap figure. This looks like
evidence the names are BSE-only — it is not, see §5.

---

## 3. Claim (c) — the NaN-drop mechanism

`src/pit_universe.py:83`, inside `snapshot_as_of`:

```python
last = vis.groupby("symbol", sort=True).tail(1)
```

`DataFrame.groupby` defaults to `dropna=True`, so every NA-keyed row is discarded before
`.tail(1)`. Reproduced:

```
symbol=['A', None, 'B', None]  ->  rows in 4, rows out 2
```

`universe_as_of` → `_rank_band` → `snapshot_as_of`, so the drop is on the only path the
habitat is built by. No warning, no count, no error. **CONFIRMED.**

---

## 4. Claim (d) — measured habitat size

`universe_as_of(store, date, "201-1000")` on the live store:

| date | habitat | date | habitat |
|---|---|---|---|
| 2016-01-08 | **0** | 2021-06-30 | 745 |
| 2017-06-30 | **0** | 2021-12-31 | 770 |
| 2018-01-25 | 716 | 2022-06-30 | 795 |
| 2018-06-29 | 716 | 2022-12-30 | 811 |
| 2018-12-31 | 727 | 2023-06-30 | 820 |
| **2019-03-01** | **719** | 2023-12-29 | 837 |
| 2019-06-28 | 719 | 2024-03-28 | 856 |
| 2019-12-31 | 724 | 2024-06-28 | 856 |
| 2020-06-30 | 725 | 2024-07-16 | 856 |

**719 is a single-date reading, not a constant.** It happens to hold at the exact date
COVERAGE.md cites (2019-03-01). Presenting it as "the habitat returns 719" understates the
variability and, for the later dev window, understates the size by up to 137 names.

Per AMFI edition (the clean measure, no as-of accumulation), band 201–1000 always has
exactly 800 ranked rows; the named subset is:

| period | named | blank | | period | named | blank |
|---|---|---|---|---|---|---|
| 2017H2 | 716 | 84 | | 2022H1 | 739 | 61 |
| 2018H1 | 723 | 77 | | 2022H2 | 744 | 56 |
| 2018H2 | 704 | 96 | | 2023H1 | 750 | 50 |
| 2019H1 | 701 | 99 | | 2023H2 | 759 | 41 |
| 2019H2 | 697 | 103 | | 2024H1 | 760 | 40 |
| 2020H1 | **690** | **110** | | 2024H2 | 763 | 37 |
| 2020H2 | 698 | 102 | | 2025H1 | 766 | 34 |
| 2021H1 | 716 | 84 | | 2025H2 | 799 | 1 |
| 2021H2 | 733 | 67 | | 2026H1 | 799 | 1 |

The gap is **worst in 2019H2–2020H2 (102–110 names, 12.8%–13.8%)** — i.e. precisely across
the 2018–2020 drawdown leg the spec requires. That is the one respect in which the
defect is worse than the record implies.

---

## 5. The benchmark of "~800" is wrong — this is the finding that should change the decision

AMFI ranks companies by **average market cap across ALL exchanges**. Ranks 201–1000
therefore include companies that are **not listed on NSE at all**. A habitat that can only
be traded and priced on NSE is structurally smaller than 800 no matter how the parser
behaves. "719 vs ~800" compares a tradeable count against an untradeable ceiling.

Two independent outcome-blind tests of whether the dropped names are NSE-listed:

**Test 1 — NIFTY500 base rate at equal rank** (current NIFTY500 constituent CSV, joined on
ISIN):

| rank slice | named rows: in N500 | blank rows: in N500 |
|---|---|---|
| 1–200 | 89.8% | 65.7% |
| 201–500 | 56.4% | **11.9%** |
| 501–1000 | 8.0% | **1.9%** |

**Test 2 — survivor-conditioned, using AMFI's own 2026H1 edition** (where the NSE column
works). Restricting to band companies from pre-cutoff editions that still exist in 2026H1:

| | n | has NSE symbol in 2026H1 |
|---|---|---|
| named rows | 8,820 | **99.0%** |
| blank rows | 761 | **26.9%** |

Both tests agree: **roughly three-quarters of the dropped names are BSE-primary companies
that were never NSE-tradeable.** A fix that injects their BSE tickers into `symbol` would
push them into `build_price_panel.py`'s `<symbol>.NS` fetch list, where they fail —
inflating the unservable count (today 102/1,412) rather than widening the habitat.

Effective NSE-tradeable ceiling, and the real shortfall (blank rows known NSE-listed in
2026H1, plus delisted blanks pro-rated at the 26.9% survivor rate):

| period | named | effective ceiling | real shortfall |
|---|---|---|---|
| 2017H2 | 716 | 735 | 2.6% |
| 2018H2 | 704 | 728 | 3.3% |
| 2019H2 | 697 | 722 | 3.5% |
| **2020H1** | 690 | 718 | **3.9%** (worst) |
| 2021H2 | 733 | 753 | 2.7% |
| 2022H2 | 744 | 762 | 2.4% |
| 2023H2 | 759 | 771 | 1.6% |
| 2024H1 | 760 | 775 | 1.9% |

**The habitat is ~1.6%–3.9% narrower than achievable, not ~10%.** In absolute terms the
recoverable, genuinely NSE-listed names number roughly **9–33 per edition**, not 34–110.

Not a reason to skip the fix — a 3.9% habitat gap concentrated in the crash window is still
worth closing, and the affected names are real midcaps (MCX, SPICEJET, WESTLIFE, ISGEC,
NOVARTIS INDIA, FORCE MOTORS, GOODYEAR, KENNAMETAL, ELANTAS BECK, KIRLOSKAR PNEUMATIC,
SESHASAYEE PAPER, ION EXCHANGE, HAWKINS COOKER, MAX INDIA, APOLLO TRICOAT, UGRO CAPITAL).
But the operator is being asked to fund a rebuild on a stated **~10% / ~80-name** benefit
whose realisable size is **~2–4% / ~9–33 names**. Budget accordingly.

Mechanics of the fix, measured across the band, 2017H2–2025H1 (1,141 blank rows):
- **1,090** have a usable ticker in AMFI's BSE Symbol column (fallback would fire);
- **51** have neither NSE nor BSE ticker — unrecoverable at any price;
- **4** would collide with a symbol already present in the same edition (needs a tie-break
  rule before the rebuild, not after).

Note also: AMFI's "BSE Symbol" column mostly holds the **alphabetic NSE-style ticker**
(NESTLEIND, SPICEJET, MCX), not a BSE numeric scrip code — which is why the fallback
recovers usable symbols at all for the NSE-listed quarter.

---

## 6. NOT ON THE RECORD — de-duplication silently destroys 22,706 mcap rows

`scripts/build_pit_universe.py:55-57`:

```python
merged = merged.drop_duplicates(subset=[c for c in pit_universe.SCHEMA
                                        if c != "source"])
```

The key is `(symbol, field, effective_date, announce_date, value)`. When `symbol` is NA,
two **different companies** in the same edition that happen to share the same rounded
rupee market cap collapse into one row.

- staging total 297,676 rows → store 274,966 = **22,710 rows dropped**;
- **100% of them are blank-symbol rows** (22,706 mcap + 4 rank);
- e.g. 2017H2: `Duropack Ltd` (INE138B01018) and `Abhinav Leasing & Finance`
  (INE211D01027) both at ₹10.00 Cr — one survives, one vanishes.

`build_pit_universe.py:58` prints `dropped N duplicate rows`. It ran, it printed a
five-figure number, and nothing acted on it — the same silence pattern as TRAP 6.

**Habitat impact: negligible.** The dropped rows sit deep in the tail (rank min 923, median
4,152); exactly **1** falls inside 201–1000. But two consequences matter:
1. `avg_mcap_cr` / `bse_avg_mcap_cr` coverage in the tail is understated by ~11k rows each,
   which touches any future MW work below rank ~900;
2. **if the blank-symbol defect is fixed, these rows stop colliding and the store grows by
   ~22.7k rows.** Any post-fix row-count assertion must expect ~297.7k, not ~275k, or the
   rebuild will look wrong when it is right.

Recommend the de-dup key include `isin` (or `source`) regardless of the operator's decision
on the main defect.

---

## 7. NOT ON THE RECORD — `universe_as_of(..., "NIFTY500")` returns `[]` silently

The store contains **four fields only**: `mcap_rank`, `avg_mcap_cr`, `bse_avg_mcap_cr`,
`nse_avg_mcap_cr`. There are **zero `index_member:*` rows**, despite `src/pit_universe.py`
documenting that field and `universe_as_of` supporting an index-name band, and despite
SPEC-52WH-01 listing `"NIFTY500"` as an admissible band.

Measured: `universe_as_of(store, '2020-06-30', 'NIFTY500')` → `list`, **length 0**. No
exception, no warning. `snapshot_as_of` returns an empty Series, `pd.to_numeric` accepts it,
and an empty universe comes back looking like a legitimate answer.

The 166 NSE index-change press releases are present as **unparsed PDFs** under
`data/reference/pit/raw/nse_index_changes/` — staged but never normalised into the store.

A NIFTY500 sensitivity run today would silently backtest an empty universe. This should get
a hard failure in `universe_as_of` (empty index-membership result → raise) whatever else is
decided.

---

## 8. Claim (f) — COVERAGE.md §6.2

The file **already carries the correction** (COVERAGE.md §6 item 2, "CORRECTED 2026-07-20"),
which explicitly retracts the earlier 100.0% claim and gives a per-period table. My
independent recount from the raw xlsx reproduces that table **exactly** — 2017H2 = 914,
2020H1 = 887, 2025H1 = 965, 2026H1 = 969.

- NSE-symbol coverage in the top 1000: **88.7% (2020H1) – 96.9% (2026H1)**. CONFIRMED.
- For pre-2025H2 editions only the max is 96.5%; the 96.9% figure comes from 2026H1.
- With the BSE fallback ("either" column) coverage would be **99.5%–99.9%** — but per §5
  most of that increment is BSE-primary names, so it is symbol coverage, not tradeable
  coverage.

COVERAGE.md §6.7's own description of the defect is accurate. Its one weakness is the same
as CLAUDE.md's: it quotes "719 for 2019-03-01" and "~10%" without noting that ~800 is an
all-exchange ceiling.

---

## 9. Direction of bias

**What kind of company silently vanished.** Three measured properties, all outcome-blind:

1. **Not NSE-listed** — ~73% of them (§5, two independent tests).
2. **Smaller** — across the whole store, blank-symbol companies have median AMFI rank
   **3,298** vs **1,198** for named; only 1% sit above rank 749. Inside the band they
   concentrate in the lower half (1,006 of 1,141 blank band rows are ranks 501–1000).
3. **More likely to die** — survival to 2026H1 for pre-cutoff band rows: **71.1% blank vs
   87.1% named**. This is the load-bearing one.

**Is the selection random?** The *mechanism* is: whether AMFI's data-entry left an NSE cell
empty is orthogonal to price behaviour. But the *population it selects* is not — it is
correlated with BSE-primacy, small size, and delisting propensity.

**Effect on a 52-week-high negative screen.** A directional argument, not a measurement:

- Delisted names are predominantly names that fell. Names that fell are, by construction,
  **far from their 52-week high** — the Q1 bucket the screen exists to exclude.
- The habitat therefore under-samples the exact population the screen targets.
- Both arms lose those names, but they are asymmetric in value: the **unscreened control**
  loses constituents that would have dragged it down, while the **screened** arm would have
  excluded them anyway.
- Net: the measured **increment (screened − unscreened) is understated**. The defect
  **penalises** the 52WH family and biases toward a false kill, not a false survive.

This runs in the **same direction** as the two survivorship caveats already on record (the
102/1,412 unservable names skewed to delistings, and `backtest_52wh`'s frozen-position
handling). They compound rather than offset — the 52WH results to date are conservative on
this axis, which is the safe direction for a kill-line decision but means a *marginal* kill
verdict cannot be trusted as final.

**Honest limit.** The magnitude cannot be established without returns for the missing
names, which is a registered trial. The *sign* rests on the empirical delisting differential
(71.1% vs 87.1%, measured here) plus the structural claim that delisting correlates with
being far from the 52-week high. The first is measured; the second is an assumption. Treat
the direction as ASSUMPTION-tagged, not FACT.

---

## 10. Recommendations

1. **Restate the benefit before authorising.** The rebuild buys ~2–4% habitat width
   (~9–33 NSE-tradeable names per edition), not ~10% / ~80 names. Sequencing (b)-before-(c)
   remains correct; the *size* of (b)'s payoff does not justify the framing on record.
2. **Decide what `symbol` means before rebuilding.** If BSE-primary tickers enter the
   symbol column, `build_price_panel.py` will emit ~800 dead `.NS` fetches per rebuild and
   the unservable count will roughly triple. Either tag them and exclude at fetch time, or
   restrict the fallback to companies with corroborating NSE evidence.
3. **Fix the de-dup key (§6)** in the same change; assert the post-fix store at ~297.7k
   rows, not ~275k, or a correct rebuild will read as a regression.
4. **Make `universe_as_of` fail loudly on an empty index-membership band (§7)**, and either
   parse the 166 NSE press-release PDFs into `index_member:*` rows or remove `"NIFTY500"`
   from the admissible band list.
5. **Pre-commit the 4 symbol-collision tie-breaks** before the rebuild runs.
6. **Assert coverage, not row counts, after the rebuild** (TRAP 1/6): per-edition named
   count in band 201–1000, and per-date signal coverage on the rebuilt panel.

#!/usr/bin/env python3
"""Parse the AMFI semi-annual list into ABSOLUTE average-market-cap PIT rows.

The A1 ingest kept AMFI's ``Sr. No.`` as ``mcap_rank`` and DROPPED the rupee
market-cap columns, which blocked spec SPEC-52WH-01 §7's EW-vs-MW sensitivity
(``src/backtest_52wh.py`` raises rather than proxy a rank). This script closes
the data gap; spending the sensitivity is a separate, operator-authorised trial.

Reads ``data/reference/pit/raw/amfi/amfi_<YYYY>H<1|2>_avg_mcap.xlsx`` and emits
``data/reference/pit/staging/amfi_avg_mcap.csv`` in pit_universe long form.
Fields (all in Rs CRORE = 1e7 INR, AMFI's own unit, a 6-month daily average of
TOTAL market capitalisation — not free float):

- ``avg_mcap_cr``     — "Average of All Exchanges" (the canonical series)
- ``nse_avg_mcap_cr`` — NSE 6-month average
- ``bse_avg_mcap_cr`` — BSE 6-month average

Conventions reproduced EXACTLY from the in-use rank staging file
(``amfi_mcap_rank.csv``) so that the two join row-for-row on
(source_file, isin) — see ``verify_against_ranks``:

- ``effective_date`` = period end (Jun 30 / Dec 31) parsed from the FILENAME.
- ``announce_date``  = effective_date + 25 calendar days, ASSUMED, flagged per
  row in ``announce_basis``. AMFI does not publish a timestamp; this lag is the
  governing PIT visibility assumption for the whole store.
- rows with a null ``Sr. No.`` are trailer/notes rows and are dropped.
- ``symbol`` is the NSE ticker, with a BSE fallback whenever AMFI leaves the
  NSE cell missing (NaN, empty or the "-" sentinel), and blank only when
  neither exchange gives a ticker (see ``derive_symbol``).

Since the 2026-07-22 habitat fix this script is also the generator of the RANK
staging half (``amfi_mcap_rank.csv``, field ``mcap_rank`` = AMFI's ``Sr. No.``).
The original A1 parser was never persisted; regenerating both halves here is
what keeps them in ONE symbol space, which ``verify_against_ranks`` asserts
row-for-row against the previous rank file before it is overwritten.

Header text drifts across editions ("MSE Symbol" vs "MSEI Symbol", spacing in
the mcap headers), so every column is matched by SUBSTRING and asserted unique.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[1]
RAW = REPO / "data" / "reference" / "pit" / "raw" / "amfi"
STAGING = REPO / "data" / "reference" / "pit" / "staging"
OUT = STAGING / "amfi_avg_mcap.csv"
RANK_STAGING = STAGING / "amfi_mcap_rank.csv"
# NOT under staging/ — build_pit_universe.py globs staging/*.csv and this is a
# diagnostic, not a store half.
RECOVERY_REPORT = REPO / "data" / "reference" / "pit" / "symbol_recovery_report.csv"

RANK_FIELD = "mcap_rank"

# AMFI publishes no release timestamp. period_end + 25d is the pre-committed
# ASSUMPTION governing PIT visibility (plan_52wh.md A1); every row carries the
# flag so a later corpus with real dates can supersede it without ambiguity.
ANNOUNCE_LAG_DAYS = 25
ANNOUNCE_BASIS = "ASSUMED_period_end_plus_25d"

# The 2025H2+ editions write "-" where earlier editions left the cell empty.
MISSING_SENTINEL = "-"

FILENAME_RE = re.compile(r"amfi_(\d{4})H([12])_avg_mcap", re.IGNORECASE)

SR_NO_HEADER = "Sr. No."
ISIN_HEADER = "ISIN"
NAME_HEADER = "Company name"
CATEGORY_HEADER = "Categorization as per SEBI Circular"
NSE_SYMBOL_HEADER = "NSE Symbol"
BSE_SYMBOL_HEADER = "BSE Symbol"

# field name -> header substring. "NSE 6 month" does not occur inside the BSE
# or MSEI headers, so each needle resolves to exactly one column.
MCAP_FIELDS = {
    "avg_mcap_cr": "Average of All Exchanges",
    "nse_avg_mcap_cr": "NSE 6 month Avg Total Market Cap",
    "bse_avg_mcap_cr": "BSE 6 month Avg Total Market Cap",
}

# Parsed but NOT emitted as a store field: the MSEI figure is present for well
# under 100 companies per edition and is of no use to the habitat. It is read
# only to VERIFY the all-exchange identity (see ``exchange_identity_report``),
# which held exactly across all 18 editions.
MSEI_MCAP_AUX = "msei_avg_mcap_cr"

STAGING_COLUMNS = [
    "symbol",
    "field",
    "effective_date",
    "announce_date",
    "value",
    "source_file",
    "isin",
    "company_name",
    "amfi_category",
    "symbol_exchange",
    "announce_basis",
]


def find_column(frame: pd.DataFrame, needle: str) -> str:
    """The one column whose header CONTAINS ``needle``.

    Exact equality is not usable: the MSEI symbol header is "MSE Symbol" in
    2018H1-2019H1 and 2021H1 and "MSEI Symbol" elsewhere, and the mcap headers
    differ in punctuation between editions. Ambiguity is an error, never a
    silent first-match.
    """
    hits = [c for c in frame.columns if needle.lower() in str(c).lower()]
    if len(hits) != 1:
        raise KeyError(
            f"column matching {needle!r} resolved to {hits} "
            f"(headers: {list(frame.columns)})"
        )
    return hits[0]


def find_msei_mcap_column(frame: pd.DataFrame) -> str:
    """The MSEI market-cap column, whose header drifts "MSE"/"MSEI".

    Needs its own matcher: no substring picks out both spellings without also
    hitting "BSE 6 month" / "NSE 6 month", so match on the MSE prefix instead.
    """
    hits = [
        c
        for c in frame.columns
        if str(c).strip().upper().startswith("MSE") and "6 MONTH" in str(c).upper()
    ]
    if len(hits) != 1:
        raise KeyError(f"MSEI market-cap column resolved to {hits}")
    return hits[0]


def period_dates(path: Path) -> tuple[pd.Timestamp, pd.Timestamp]:
    """(effective_date, announce_date) from the filename's YYYYH[12] period."""
    m = FILENAME_RE.search(path.name)
    if not m:
        raise ValueError(f"{path.name}: filename carries no YYYYH[12] period")
    year, half = int(m.group(1)), int(m.group(2))
    effective = pd.Timestamp(year, 6, 30) if half == 1 else pd.Timestamp(year, 12, 31)
    return effective, effective + pd.Timedelta(days=ANNOUNCE_LAG_DAYS)


def _clean_text(series: pd.Series) -> pd.Series:
    """Trimmed strings; NaN and the "-" sentinel both become the empty string."""
    out = series.astype("string").str.strip()
    return out.fillna("").replace(MISSING_SENTINEL, "")


def derive_symbol(nse_raw: pd.Series, bse_raw: pd.Series) -> pd.DataFrame:
    """(symbol, symbol_exchange) for one AMFI edition, BSE fallback FIXED.

    The rule, as of the 2026-07-22 habitat fix:

    - the NSE cell is used whenever AMFI supplies one (``NSE``);
    - when the NSE cell is MISSING — NaN, empty/whitespace, or the literal "-"
      sentinel — the BSE ticker is used instead (``BSE``);
    - when neither exchange supplies a ticker the symbol is blank (``NONE``).

    THE FIX. The as-built A1 convention gated the fallback on ``dashed`` alone,
    i.e. the literal "-". Editions before 2025H2 leave the cell EMPTY rather
    than dashed, so the fallback literally never fired in any of the 16
    editions 2017H2-2025H1: 50,505 rank rows carried a blank symbol despite
    AMFI supplying a BSE ticker, and ``pit_universe.snapshot_as_of``'s
    ``groupby("symbol")`` silently drops NA keys, so those names were invisible
    to every habitat query. See ``analysis/habitat_defect_verification.md`` and
    data/reference/pit/COVERAGE.md §6.7.

    COLLISION RULE (pre-committed, not negotiable at run time). A recovered BSE
    ticker that is ALREADY in use in the same edition — either by a name whose
    NSE cell is populated, or by another recovered row — is DROPPED and the row
    is left blank/``NONE``, i.e. reported as unrecoverable. Never overwritten,
    never merged, never heuristically disambiguated: attributing one company's
    rows to another company's ticker is silent data corruption, whereas a
    disclosed gap is merely a gap. The dropped rows are emitted to
    ``data/reference/pit/symbol_recovery_report.csv``.

    Returns columns ``symbol``, ``symbol_exchange`` and the outcome-blind
    diagnostic ``symbol_recovery`` (one of ``NSE``, ``BSE_FALLBACK``,
    ``DROPPED_COLLISION``, ``NO_TICKER``), which is NOT a store field.
    """
    nse = nse_raw.astype("string").str.strip()
    bse = bse_raw.astype("string").str.strip()
    # THE FIX: an EMPTY / whitespace / NaN cell counts as missing, exactly like
    # the "-" sentinel. The old condition was `nse.eq(MISSING_SENTINEL)`, which
    # never fires on an empty cell.
    missing = nse.isna() | nse.eq("") | nse.eq(MISSING_SENTINEL)

    symbol = nse.fillna("").mask(missing, "")
    bse_ok = missing & bse.notna() & bse.ne(MISSING_SENTINEL) & bse.ne("")

    # Collision guard, evaluated over the whole edition.
    taken = set(symbol.loc[~missing].tolist())
    candidate = bse.where(bse_ok)
    dup_within = candidate.map(candidate.value_counts()).fillna(0) > 1
    collision = bse_ok & (candidate.isin(taken) | dup_within)
    recovered = bse_ok & ~collision

    symbol = symbol.mask(recovered, bse)
    exchange = pd.Series("NSE", index=nse.index, dtype="object")
    exchange = exchange.mask(missing, "NONE").mask(recovered, "BSE")

    recovery = pd.Series("NSE", index=nse.index, dtype="object")
    recovery = (
        recovery.mask(missing, "NO_TICKER")
        .mask(collision, "DROPPED_COLLISION")
        .mask(recovered, "BSE_FALLBACK")
    )
    return pd.DataFrame(
        {"symbol": symbol, "symbol_exchange": exchange, "symbol_recovery": recovery}
    )


def parse_file(path: Path) -> pd.DataFrame:
    """One AMFI xlsx -> wide frame, one row per listed company.

    Row 1 is the sheet title and row 2 the header, so data starts at row 3
    (``header=1``). Trailer rows carry a null ``Sr. No.``; 2018H2 also carries a
    footnote row whose ``Sr. No.`` is the text "*NA - ISIN not available". Both
    are non-numeric and both are dropped, matching the rank staging row counts.
    """
    raw = pd.read_excel(path, header=1)
    sr_col = find_column(raw, SR_NO_HEADER)
    sr_no = pd.to_numeric(raw[sr_col], errors="coerce")
    raw = raw.loc[sr_no.notna()].reset_index(drop=True)
    sr_no = sr_no.dropna().reset_index(drop=True)

    effective, announce = period_dates(path)
    symbols = derive_symbol(
        raw[find_column(raw, NSE_SYMBOL_HEADER)],
        raw[find_column(raw, BSE_SYMBOL_HEADER)],
    )
    out = pd.DataFrame(
        {
            "symbol": symbols["symbol"],
            "symbol_exchange": symbols["symbol_exchange"],
            "symbol_recovery": symbols["symbol_recovery"],
            "bse_symbol": _clean_text(raw[find_column(raw, BSE_SYMBOL_HEADER)]),
            "sr_no": sr_no.astype("int64"),
            "isin": _clean_text(raw[find_column(raw, ISIN_HEADER)]),
            "company_name": _clean_text(raw[find_column(raw, NAME_HEADER)]),
            "amfi_category": _clean_text(raw[find_column(raw, CATEGORY_HEADER)]),
            "effective_date": effective,
            "announce_date": announce,
            "source_file": path.name,
            "announce_basis": ANNOUNCE_BASIS,
        }
    )
    def numeric(column: str) -> pd.Series:
        return pd.to_numeric(
            raw[column].astype("string").str.replace(",", ""), errors="coerce"
        ).astype("float64")

    for field, needle in MCAP_FIELDS.items():
        out[field] = numeric(find_column(raw, needle))
    out[MSEI_MCAP_AUX] = numeric(find_msei_mcap_column(raw))
    return out


def to_long(wide: pd.DataFrame) -> pd.DataFrame:
    """Wide per-company frame -> pit_universe long rows, null values dropped.

    A missing mcap cell yields NO row rather than a null-valued one: the store
    is a set of assertions, and "AMFI published nothing here" is not a value.
    """
    frames = []
    for field in MCAP_FIELDS:
        part = wide.loc[wide[field].notna()].copy()
        part["field"] = field
        part["value"] = part[field].astype("float64")
        frames.append(part.loc[:, STAGING_COLUMNS])
    return pd.concat(frames, ignore_index=True)


def to_long_ranks(wide: pd.DataFrame) -> pd.DataFrame:
    """Wide per-company frame -> ``mcap_rank`` long rows (value = AMFI Sr. No.).

    AMFI's ``Sr. No.`` IS its all-exchange market-cap rank, so it needs no
    derivation; this exists so BOTH staging halves come out of ONE symbol
    derivation (``derive_symbol``) instead of two parsers that can drift.
    """
    part = wide.copy()
    part["field"] = RANK_FIELD
    part["value"] = part["sr_no"].astype("int64")
    return part.loc[:, STAGING_COLUMNS]


def recovery_report(wide_by_file: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Every row the BSE fallback could NOT resolve, with the reason.

    Two disjoint reasons, both meaning "no symbol": ``DROPPED_COLLISION`` (a
    usable BSE ticker existed but was already taken in that edition — the
    pre-committed rule drops rather than guesses) and ``NO_TICKER`` (AMFI gave
    neither exchange a ticker). Written out so the gap is disclosed rather than
    inferred from a row count.
    """
    frames = []
    for source_file, wide in wide_by_file.items():
        bad = wide.loc[wide["symbol_recovery"].isin(("DROPPED_COLLISION", "NO_TICKER"))]
        if bad.empty:
            continue
        frames.append(
            bad.loc[
                :,
                [
                    "source_file",
                    "effective_date",
                    "sr_no",
                    "isin",
                    "company_name",
                    "bse_symbol",
                    "symbol_recovery",
                ],
            ]
        )
    if not frames:
        return pd.DataFrame(
            columns=[
                "source_file", "effective_date", "sr_no", "isin",
                "company_name", "bse_symbol", "symbol_recovery",
            ]
        )
    out = pd.concat(frames, ignore_index=True)
    out["in_band_201_1000"] = out["sr_no"].between(201, 1000)
    return out.sort_values(["source_file", "sr_no"]).reset_index(drop=True)


def verify_against_ranks(wide_by_file: dict[str, pd.DataFrame]) -> None:
    """Assert the newly parsed symbol space is the PREVIOUS one plus the fix.

    Both staging halves are now generated here from one ``derive_symbol`` call
    per edition, so they share a symbol space by construction. What still needs
    asserting is that the habitat fix is CONFINED to the rows it claims: it may
    fill a blank symbol (the BSE fallback firing at last) and it may blank a
    symbol (the collision rule dropping an ambiguous recovery), but it must
    NEVER rewrite one non-blank ticker into a different non-blank ticker, and it
    must not disturb isin or the Sr. No. ordering.

    Compares against the rank staging file as it exists on disk, so it must run
    BEFORE that file is overwritten.
    """
    if not RANK_STAGING.exists():
        print(f"  (skipped: {RANK_STAGING.name} absent)")
        return
    ranks = pd.read_csv(RANK_STAGING, keep_default_na=False, dtype=str)
    problems = filled = blanked = 0
    for source_file, wide in wide_by_file.items():
        got = ranks.loc[ranks["source_file"] == source_file]
        if len(got) != len(wide):
            print(f"  MISMATCH {source_file}: rank rows {len(got)} vs mcap {len(wide)}")
            problems += 1
            continue
        # The old rank file kept raw cell whitespace ("NA          "); this
        # parser strips it, so compare stripped. That is the ONE deliberate
        # divergence (documented in COVERAGE.md).
        if (got["isin"].str.strip().to_numpy() != wide["isin"].astype(str).to_numpy()).any():
            print(f"  MISMATCH {source_file}.isin: rows differ")
            problems += 1
        if (got["value"].astype(int).to_numpy() != wide["sr_no"].to_numpy()).any():
            print(f"  MISMATCH {source_file}: Sr. No. ordering differs from ranks")
            problems += 1
        old = got["symbol"].str.strip().to_numpy()
        new = wide["symbol"].astype(str).to_numpy()
        changed = old != new
        filled += int((changed & (old == "")).sum())
        blanked += int((changed & (new == "")).sum())
        rewritten = changed & (old != "") & (new != "")
        if rewritten.any():
            print(
                f"  MISMATCH {source_file}: {int(rewritten.sum())} non-blank "
                f"symbols REWRITTEN to a different non-blank symbol"
            )
            problems += 1
    print(f"  symbols filled by the fixed fallback: {filled}")
    print(f"  symbols blanked by the collision rule: {blanked}")
    print("  rank-staging agreement: OK" if not problems else f"  {problems} MISMATCHES")


def monotonicity_report(wide_by_file: dict[str, pd.DataFrame]) -> None:
    """Where AMFI's own Sr. No. disagrees with its mcap column.

    AMFI's rank IS the mcap ordering, so any adjacent pair whose avg_mcap_cr
    rises with Sr. No. is an internal inconsistency in the source document.
    """
    print("\n=== Sr. No. vs avg_mcap_cr monotonicity ===")
    total = 0
    for source_file, wide in wide_by_file.items():
        ordered = wide.sort_values("sr_no")
        vals = ordered["avg_mcap_cr"].to_numpy()
        srs = ordered["sr_no"].to_numpy()
        bad = [i for i in range(1, len(vals)) if vals[i] > vals[i - 1]]
        if not bad:
            continue
        total += len(bad)
        for i in bad:
            dev = (vals[i] - vals[i - 1]) / vals[i - 1] * 100
            print(
                f"  {source_file}: Sr. No. {srs[i - 1]} ({vals[i - 1]:,.2f}) < "
                f"{srs[i]} ({vals[i]:,.2f})  +{dev:.2f}%"
            )
    print(f"  {total} violation(s) across {len(wide_by_file)} periods")


def exchange_identity_report(wide_by_file: dict[str, pd.DataFrame]) -> None:
    """Check avg_mcap_cr == mean of the AVAILABLE per-exchange figures.

    Establishes the semantics of the headline column: it is an unweighted mean
    across the exchanges that quote the name (BSE, NSE, MSEI), not an NSE
    figure and not a volume-weighted blend. Verified, not assumed.
    """
    print("\n=== all-exchange identity (avg == mean of available legs) ===")
    worst = 0.0
    for source_file, wide in wide_by_file.items():
        legs = wide[["bse_avg_mcap_cr", "nse_avg_mcap_cr", MSEI_MCAP_AUX]]
        expected = legs.mean(axis=1)
        # Sub-lakh shells round a leg to 0.0 while the headline keeps digits;
        # they are excluded from the relative test, not from the data.
        rel = ((wide["avg_mcap_cr"] - expected) / expected).abs().loc[expected > 0]
        breaks = int((rel > 1e-6).sum())
        worst = max(worst, float(rel.max(skipna=True)))
        if breaks:
            print(f"  {source_file}: {breaks} rows deviate (max {rel.max():.2%})")
    print(f"  max relative deviation across all editions: {worst:.2e}")


def quality_report(wide_by_file: dict[str, pd.DataFrame], top: int = 1000) -> None:
    """Habitat-relevant coverage: count and nulls of avg_mcap_cr in ranks <= top."""
    print(f"\n=== avg_mcap_cr coverage, Sr. No. <= {top} ===")
    for source_file, wide in wide_by_file.items():
        head = wide.loc[wide["sr_no"] <= top]
        print(
            f"  {source_file}: n={len(head)} "
            f"nulls={int(head['avg_mcap_cr'].isna().sum())} "
            f"blank_symbol={int((head['symbol'] == '').sum())} "
            f"min={head['avg_mcap_cr'].min():,.0f} max={head['avg_mcap_cr'].max():,.0f}"
        )


def main() -> None:
    files = sorted(p for p in RAW.glob("amfi_*_avg_mcap.xlsx"))
    if not files:
        sys.exit(f"no AMFI xlsx files in {RAW}")
    wide_by_file = {}
    mcap_frames, rank_frames = [], []
    for path in files:
        wide = parse_file(path)
        wide_by_file[path.name] = wide
        mcap_frames.append(to_long(wide))
        rank_frames.append(to_long_ranks(wide))
        print(
            f"  {path.name}: {len(wide)} companies, "
            f"avg_mcap_cr nulls {int(wide['avg_mcap_cr'].isna().sum())}, "
            f"blank symbols {int((wide['symbol'] == '').sum())}"
        )

    # Runs BEFORE the rank file is overwritten — it reads the previous one.
    print("\n=== provenance check ===")
    verify_against_ranks(wide_by_file)

    long = pd.concat(mcap_frames, ignore_index=True).sort_values(
        ["field", "effective_date", "symbol"], kind="stable"
    ).reset_index(drop=True)
    ranks = pd.concat(rank_frames, ignore_index=True).sort_values(
        ["effective_date", "value"], kind="stable"
    ).reset_index(drop=True)

    # TRAP 6: assert an EXPECTED VOLUME, never a non-empty row count. One rank
    # row per company per edition, three mcap fields per company at most.
    expected_ranks = sum(len(w) for w in wide_by_file.values())
    if len(ranks) != expected_ranks:
        sys.exit(f"rank rows {len(ranks)} != companies parsed {expected_ranks}")
    if len(long) > 3 * expected_ranks:
        sys.exit(f"mcap rows {len(long)} exceed 3 x {expected_ranks}")

    STAGING.mkdir(parents=True, exist_ok=True)
    long.to_csv(OUT, index=False)
    ranks.to_csv(RANK_STAGING, index=False)
    print(f"\nwrote {len(long)} rows -> {OUT}")
    print(f"wrote {len(ranks)} rows -> {RANK_STAGING}")
    print(long["field"].value_counts().to_string())

    report = recovery_report(wide_by_file)
    RECOVERY_REPORT.parent.mkdir(parents=True, exist_ok=True)
    report.to_csv(RECOVERY_REPORT, index=False)
    counts = report["symbol_recovery"].value_counts().to_dict()
    band = report.loc[report["in_band_201_1000"]] if len(report) else report
    print(
        f"\nwrote {len(report)} unrecoverable rows -> {RECOVERY_REPORT}\n"
        f"  all ranks: {counts}\n"
        f"  band 201-1000: "
        f"{band['symbol_recovery'].value_counts().to_dict() if len(band) else {}}"
    )

    exchange_identity_report(wide_by_file)
    quality_report(wide_by_file)
    monotonicity_report(wide_by_file)


if __name__ == "__main__":
    main()

"""Acceptance tests for scripts/parse_amfi.py — the AMFI absolute-market-cap
ingest that unblocks SPEC-52WH-01 §7's EW-vs-MW sensitivity.

Reference data only: nothing here touches prices, returns, or any outcome.

Synthetic workbooks carry the header drift seen in the real corpus ("MSE
Symbol" in 2018H1-2019H1 and 2021H1 vs "MSEI Symbol" elsewhere) so the
substring matcher is proven against it without needing the gitignored corpus.
The few real-corpus checks skip when the corpus is absent.
"""

import importlib.util
import sys
from pathlib import Path

import pandas as pd
import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

_spec = importlib.util.spec_from_file_location(
    "parse_amfi", REPO / "scripts" / "parse_amfi.py"
)
parse_amfi = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(parse_amfi)

CORPUS = pytest.mark.skipif(
    not sorted(parse_amfi.RAW.glob("amfi_*_avg_mcap.xlsx")),
    reason="AMFI raw corpus absent (data/ is gitignored)",
)


def workbook(tmp_path, name, msei_header="MSEI Symbol", rows=None):
    """A minimal AMFI-shaped xlsx: title on row 1, header on row 2, data below."""
    rows = rows if rows is not None else [
        # sr, company, isin, bse_sym, bse_mcap, nse_sym, nse_mcap, msei, msei_mcap, avg, cat
        (1, "Reliance Industries Ltd", "INE002A01018", "RELIANCE", 544406.34,
         "RELIANCE", 552996.80, None, None, 548701.57, "Large Cap"),
        (2, "Nestle India Ltd.", "INE239A01016", "NESTLEIND", 69778.96,
         None, None, None, None, 69778.96, "Large Cap"),
        (3, "Dash Sentinel Ltd", "INE111A01011", "DASHCO", 500.0,
         "-", None, "-", None, 500.0, "Small Cap"),
        (4, "No Ticker Ltd", "INE222A01012", "-", None,
         "-", None, "-", None, 12.5, "Small Cap"),
        (None, "trailer note row", None, None, None,
         None, None, None, None, None, None),
    ]
    frame = pd.DataFrame(
        rows,
        columns=[
            "Sr. No.",
            "Company name",
            "ISIN",
            "BSE Symbol",
            "BSE 6 month Avg Total Market Cap in (Rs. Crs.)",
            "NSE Symbol",
            "NSE 6 month Avg Total Market Cap (Rs. Crs.)",
            msei_header,
            f"{msei_header.replace('Symbol', '')}6 month Avg Total Market Cap"
            " in (Rs Crs.)",
            "Average of All Exchanges (Rs. Cr.)",
            "Categorization as per SEBI Circular dated Oct 6, 2017",
        ],
    )
    path = tmp_path / name
    frame.to_excel(path, index=False, startrow=1)
    return path


# --- filename -> PIT dates ------------------------------------------------


@pytest.mark.parametrize(
    "name,effective,announce",
    [
        ("amfi_2017H2_avg_mcap.xlsx", "2017-12-31", "2018-01-25"),
        ("amfi_2018H1_avg_mcap.xlsx", "2018-06-30", "2018-07-25"),
        ("amfi_2026H1_avg_mcap.xlsx", "2026-06-30", "2026-07-25"),
    ],
)
def test_announce_convention_is_period_end_plus_25d(name, effective, announce):
    eff, ann = parse_amfi.period_dates(Path(name))
    assert eff == pd.Timestamp(effective)
    assert ann == pd.Timestamp(announce)
    assert (ann - eff).days == parse_amfi.ANNOUNCE_LAG_DAYS


def test_announce_basis_flagged_on_every_row(tmp_path):
    wide = parse_amfi.parse_file(workbook(tmp_path, "amfi_2019H1_avg_mcap.xlsx"))
    long = parse_amfi.to_long(wide)
    assert (long["announce_basis"] == "ASSUMED_period_end_plus_25d").all()
    assert (long["announce_date"] == pd.Timestamp("2019-07-25")).all()
    assert (long["effective_date"] == pd.Timestamp("2019-06-30")).all()


def test_unparseable_filename_rejected():
    with pytest.raises(ValueError, match="no YYYYH"):
        parse_amfi.period_dates(Path("amfi_latest.xlsx"))


# --- header matching ------------------------------------------------------


@pytest.mark.parametrize("msei_header", ["MSE Symbol", "MSEI Symbol"])
def test_substring_matching_survives_header_drift(tmp_path, msei_header):
    """Both MSEI header spellings must parse identically — exact-equality
    matching would have silently broken on the 2018H1-2019H1 / 2021H1 files."""
    path = workbook(tmp_path, "amfi_2021H1_avg_mcap.xlsx", msei_header=msei_header)
    wide = parse_amfi.parse_file(path)
    assert list(wide["symbol"]) == ["RELIANCE", "", "DASHCO", ""]
    assert wide.loc[0, "avg_mcap_cr"] == pytest.approx(548701.57)


def test_mcap_needles_are_unambiguous(tmp_path):
    """"NSE 6 month" must not also match the BSE or MSEI mcap headers."""
    wide = pd.read_excel(workbook(tmp_path, "amfi_2020H1_avg_mcap.xlsx"), header=1)
    for needle in parse_amfi.MCAP_FIELDS.values():
        assert parse_amfi.find_column(wide, needle)


def test_ambiguous_header_raises(tmp_path):
    frame = pd.DataFrame(columns=["NSE Symbol", "nse symbol (old)"])
    with pytest.raises(KeyError, match="resolved to"):
        parse_amfi.find_column(frame, "NSE Symbol")


def test_missing_header_raises():
    with pytest.raises(KeyError, match="resolved to"):
        parse_amfi.find_column(pd.DataFrame(columns=["A"]), "Average of All Exchanges")


# --- symbol convention ----------------------------------------------------


def test_dash_sentinel_falls_back_to_bse_empty_cell_does_not(tmp_path):
    """The as-built rank-file convention, reproduced deliberately: a "-" NSE
    cell falls back to BSE, an EMPTY one does not (that gap is the inherited
    defect documented in COVERAGE.md)."""
    wide = parse_amfi.parse_file(workbook(tmp_path, "amfi_2022H1_avg_mcap.xlsx"))
    assert list(wide["symbol"]) == ["RELIANCE", "", "DASHCO", ""]
    assert list(wide["symbol_exchange"]) == ["NSE", "NSE", "BSE", "NONE"]


@CORPUS
def test_matches_in_use_rank_staging(capsys):
    """The new rows must land in the same (source_file, isin, symbol) space as
    the canonical rank rows, which must never be rewritten."""
    if not parse_amfi.RANK_STAGING.exists():
        pytest.skip("rank staging absent")
    wide_by_file = {
        p.name: parse_amfi.parse_file(p)
        for p in sorted(parse_amfi.RAW.glob("amfi_*_avg_mcap.xlsx"))
    }
    parse_amfi.verify_against_ranks(wide_by_file)
    out = capsys.readouterr().out
    assert "rank-staging agreement: OK" in out
    assert "MISMATCH" not in out


# --- null handling --------------------------------------------------------


def test_non_numeric_and_null_sr_no_rows_dropped(tmp_path):
    """Trailer rows (null Sr. No.) and 2018H2's "*NA - ISIN not available"
    footnote must not become PIT rows."""
    rows = [
        (1, "Real Co", "INE001A01011", "REALCO", 10.0, "REALCO", 10.0,
         None, None, 10.0, "Small Cap"),
        ("*NA - ISIN not available", "footnote", None, None, None,
         None, None, None, None, None, None),
        (None, None, None, None, None, None, None, None, None, None, None),
    ]
    wide = parse_amfi.parse_file(
        workbook(tmp_path, "amfi_2018H2_avg_mcap.xlsx", rows=rows)
    )
    assert len(wide) == 1
    assert wide["sr_no"].dtype == "int64"


def test_null_mcap_emits_no_row(tmp_path):
    """A missing cell yields NO row rather than a null-valued one — the store
    holds assertions, and "AMFI published nothing" is not a value."""
    long = parse_amfi.to_long(
        parse_amfi.parse_file(workbook(tmp_path, "amfi_2023H1_avg_mcap.xlsx"))
    )
    assert long["value"].notna().all()
    counts = long["field"].value_counts()
    assert counts["avg_mcap_cr"] == 4  # every row has an all-exchange average
    assert counts["nse_avg_mcap_cr"] == 1  # only Reliance has an NSE figure
    assert counts["bse_avg_mcap_cr"] == 3


def test_long_form_matches_pit_schema(tmp_path):
    from src import pit_universe

    long = parse_amfi.to_long(
        parse_amfi.parse_file(workbook(tmp_path, "amfi_2024H1_avg_mcap.xlsx"))
    )
    validated = pit_universe.validate(long.rename(columns={"source_file": "source"}))
    assert set(validated["field"]) <= set(parse_amfi.MCAP_FIELDS)
    assert validated["value"].dtype == "float64"


# --- units / scale sanity -------------------------------------------------


def test_thousands_separators_parsed(tmp_path):
    rows = [
        (1, "Comma Co", "INE001A01011", "COMMACO", "1,234.56", "COMMACO",
         "1,234.56", None, None, "1,234.56", "Large Cap"),
    ]
    wide = parse_amfi.parse_file(
        workbook(tmp_path, "amfi_2025H1_avg_mcap.xlsx", rows=rows)
    )
    assert wide.loc[0, "avg_mcap_cr"] == pytest.approx(1234.56)


@CORPUS
def test_real_corpus_units_are_rupee_crore():
    """Scale guard. In Rs CRORE the largest Indian company sits in the 1e5-1e7
    band and the top-1000 floor in the 1e2-1e4 band; in rupees or in millions
    these assertions fail loudly, which is the point."""
    path = parse_amfi.RAW / "amfi_2017H2_avg_mcap.xlsx"
    if not path.exists():
        pytest.skip("2017H2 file absent")
    wide = parse_amfi.parse_file(path)
    top = wide.sort_values("sr_no").iloc[0]
    assert top["symbol"] == "RELIANCE"
    assert 1e5 < top["avg_mcap_cr"] < 1e7
    floor = wide.loc[wide["sr_no"] == 1000, "avg_mcap_cr"].iloc[0]
    assert 1e2 < floor < 1e4


@CORPUS
def test_all_exchange_column_is_mean_of_available_legs():
    """Pins the SEMANTICS of avg_mcap_cr: an unweighted mean over the exchanges
    that quote the name (BSE, NSE, MSEI) — not an NSE figure, not volume
    weighted. Held exactly (max relative deviation 0) on all 18 editions."""
    for path in sorted(parse_amfi.RAW.glob("amfi_*_avg_mcap.xlsx")):
        wide = parse_amfi.parse_file(path)
        legs = wide[
            ["bse_avg_mcap_cr", "nse_avg_mcap_cr", parse_amfi.MSEI_MCAP_AUX]
        ]
        expected = legs.mean(axis=1)
        # Sub-lakh shells sit at the rounding floor (a per-exchange leg prints
        # 0.0 while the all-exchange column keeps digits), so exclude zeros
        # from the relative test — they are checked absolutely instead.
        rel = ((wide["avg_mcap_cr"] - expected) / expected).abs()
        assert rel.loc[expected > 0].max() < 1e-6, path.name
        assert (wide.loc[expected == 0, "avg_mcap_cr"].abs() < 1e-2).all(), path.name


@CORPUS
def test_top_1000_fully_covered_every_period():
    """Habitat guard: ranks 1-1000 must carry a non-null avg_mcap_cr in every
    one of the 18 half-years, else the MW sensitivity has holes."""
    for path in sorted(parse_amfi.RAW.glob("amfi_*_avg_mcap.xlsx")):
        head = parse_amfi.parse_file(path).query("sr_no <= 1000")
        assert len(head) == 1000, path.name
        assert head["avg_mcap_cr"].notna().all(), path.name


@CORPUS
def test_only_2021h1_breaks_sr_no_monotonicity():
    """AMFI's Sr. No. IS its mcap ordering. 2021H1 contradicts itself at four
    adjacent pairs; every other edition is strictly descending. Pinned so a
    future corpus refresh cannot change it silently."""
    offenders = {}
    for path in sorted(parse_amfi.RAW.glob("amfi_*_avg_mcap.xlsx")):
        wide = parse_amfi.parse_file(path).sort_values("sr_no")
        vals = wide["avg_mcap_cr"].to_numpy()
        srs = wide["sr_no"].to_numpy()
        bad = [int(srs[i]) for i in range(1, len(vals)) if vals[i] > vals[i - 1]]
        if bad:
            offenders[path.name] = bad
    assert offenders == {
        "amfi_2021H1_avg_mcap.xlsx": [221, 773, 1031, 1160],
    }

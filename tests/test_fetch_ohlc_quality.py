"""Quality gate on the Tier 1 OHLC ingest (DECISIONS.md 2026-07-21).

Regression guard for a defect that passed every check the ingest had: the
2026-07-21 run wrote 544 rows, 34/34 expected symbols, correct date range —
and EVERY symbol's newest close was NaN. Row counts, symbol counts and a zero
exit code all looked healthy. Close is the field settlement and NAV depend on.

Second defect guarded here: the fetch universe was read only from
`data/legacy_snapshot/recs/`, which is frozen. Recs deposited by the nightly
ingest under `data/sealed/raw/<date>/` were never read, so any symbol first
recommended after the snapshot date was never fetched — DIXON, picked
2026-07-16 and held live for three sessions, had no OHLC at all.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

import fetch_ohlc  # noqa: E402


def _frame(rows):
    return pd.DataFrame(
        rows, columns=["date", "open", "high", "low", "close", "symbol"]
    )


class TestValidateOhlc:
    def test_null_close_row_is_dropped_not_written(self):
        """The exact 2026-07-21 shape: O/H/L present, close NaN."""
        df = _frame([
            ("2026-07-17", 100.0, 101.0, 99.0, 100.5, "AAA"),
            ("2026-07-20", 100.5, 102.0, 100.0, float("nan"), "AAA"),
        ])
        clean, report = fetch_ohlc.validate_ohlc(df, ["AAA"])
        assert report["dropped_null_close"] == 1
        assert len(clean) == 1
        assert clean["close"].notna().all()
        assert report["newest_date"] == "2026-07-17"

    def test_clean_frame_passes_untouched(self):
        df = _frame([
            ("2026-07-17", 100.0, 101.0, 99.0, 100.5, "AAA"),
            ("2026-07-20", 100.5, 102.0, 100.0, 101.5, "AAA"),
        ])
        clean, report = fetch_ohlc.validate_ohlc(df, ["AAA"])
        assert report["dropped_null_close"] == 0
        assert len(clean) == len(df)

    def test_missing_symbol_is_reported(self):
        """DIXON's failure mode: expected, never fetched, silently absent."""
        df = _frame([("2026-07-17", 100.0, 101.0, 99.0, 100.5, "AAA")])
        _, report = fetch_ohlc.validate_ohlc(df, ["AAA", "DIXON"])
        assert report["symbols_missing"] == ["DIXON"]
        assert report["symbols_present"] == 1
        assert report["symbols_expected"] == 2

    def test_all_null_close_yields_empty_and_is_detectable(self):
        """Whole-file failure must be visible, not written as an empty file."""
        df = _frame([
            ("2026-07-20", 100.0, 101.0, 99.0, float("nan"), "AAA"),
            ("2026-07-20", 200.0, 201.0, 199.0, float("nan"), "BBB"),
        ])
        clean, report = fetch_ohlc.validate_ohlc(df, ["AAA", "BBB"])
        assert clean.empty
        assert report["dropped_null_close"] == 2
        assert report["newest_date"] is None
        assert sorted(report["symbols_missing"]) == ["AAA", "BBB"]


class TestRecSymbolSources:
    def test_reads_both_comment_and_skiprows_rec_shapes(self, tmp_path):
        """Rec CSVs carry a provenance line 1 and header on line 2, in two
        forms across the corpus. Both must parse."""
        hashed = tmp_path / "top5_report_data_a.csv"
        hashed.write_text("# Data as of: 2026-07-16\nsymbol,close\nDIXON,14507\n")
        bare = tmp_path / "top5_report_data_b.csv"
        bare.write_text("Data as of: 2026-07-16\nsymbol,close\nRADICO,4132.4\n")
        assert fetch_ohlc._rec_symbols_from(hashed) == {"DIXON"}
        assert fetch_ohlc._rec_symbols_from(bare) == {"RADICO"}

    def test_unparseable_file_yields_empty_not_exception(self, tmp_path):
        junk = tmp_path / "top5_report_data_junk.csv"
        junk.write_text("not,a,rec\n")
        assert fetch_ohlc._rec_symbols_from(junk) == set()

    def test_sealed_raw_is_in_the_search_path(self):
        """The coverage bug: sealed/raw/ holds recs the frozen snapshot dir
        does not. Pin that the source is read, so removing it fails loudly."""
        src = (REPO / "src" / "fetch_ohlc.py").read_text()
        assert '"sealed" / "raw"' in src, (
            "fetch universe no longer reads data/sealed/raw/ — new recs would "
            "again be silently excluded from the Tier 1 fetch"
        )


class TestLiveStoreIntegrity:
    """Guards the real store, not a fixture. Skips cleanly if absent."""

    def _newest(self):
        files = sorted((REPO / "data" / "market" / "ohlc").glob("ohlc_*.parquet"))
        return files[-1] if files else None

    def test_newest_ingest_has_no_null_closes(self):
        f = self._newest()
        if f is None:
            pytest.skip("no ingested OHLC present")
        d = pd.read_parquet(f)
        n = int(d["close"].isna().sum())
        assert n == 0, (
            f"{f.name}: {n} null-close rows across "
            f"{d[d['close'].isna()]['symbol'].nunique()} symbols — settlement and "
            f"NAV read this file (run_paper_leg.py takes the newest parquet)"
        )

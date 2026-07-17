"""Tests for data_gate.load_operational (RULING 2, Tier 1 door)."""

import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import data_gate

SNAP = "data/legacy_snapshot/trades_log_ee7ad13.csv"


def _rec_frame(dates):
    return pd.DataFrame(
        {"rec_key": [f"{d}|X|1" for d in dates], "pick_date": dates, "symbol": "X", "r": 1.0}
    )


def test_valid_operational_load_passes_and_prints_notice(capsys):
    out = data_gate.load_operational(_rec_frame(["2026-06-29", "2026-07-10"]), "pick_date", SNAP)
    assert len(out) == 2
    assert "Tier 1 forward data" in capsys.readouterr().err


def test_seal_gap_dates_rejected():
    with pytest.raises(ValueError, match="seal gap"):
        data_gate.load_operational(_rec_frame(["2025-03-01"]), "pick_date", SNAP)


def test_historical_pre_cutoff_dates_rejected():
    with pytest.raises(ValueError, match="research-tier"):
        data_gate.load_operational(_rec_frame(["2024-01-05"]), "pick_date", SNAP)


def test_generic_ohlc_panel_rejected_even_with_valid_dates():
    panel = pd.DataFrame(
        {"symbol": "X", "date": ["2026-07-01"], "open": [1.0], "high": [1.0],
         "low": [1.0], "close": [1.0]}
    )
    with pytest.raises(ValueError, match="OHLC panel"):
        data_gate.load_operational(panel, "date", SNAP)


def test_ohlc_with_rec_key_admissible_for_settlement(capsys):
    joined = pd.DataFrame(
        {"rec_key": ["2026-07-01|X|1"], "date": ["2026-07-02"], "open": [1.0],
         "high": [1.0], "low": [1.0], "close": [1.0]}
    )
    out = data_gate.load_operational(joined, "date", SNAP)
    assert len(out) == 1


def test_market_source_admissible_with_settlement_shape(capsys):
    # RULING 2 amendment: data/market/ is admissible; shape rule still applies.
    joined = pd.DataFrame(
        {"rec_key": ["2026-07-01|X|1"], "date": ["2026-07-02"], "open": [1.0],
         "high": [1.0], "low": [1.0], "close": [1.0]}
    )
    out = data_gate.load_operational(joined, "date", "data/market/ohlc/ohlc_2026-07-17.parquet")
    assert len(out) == 1


def test_inadmissible_source_rejected():
    # data/sealed/raw/ became admissible under the RULING 3 amendment
    # (settlement source); an arbitrary path outside the list must still fail.
    with pytest.raises(ValueError, match="inadmissible source"):
        data_gate.load_operational(
            _rec_frame(["2026-07-01"]), "pick_date", "notebooks/scratch/x.csv"
        )

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import data_gate


def _frame() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "date": ["2024-07-15", "2024-07-16", "2024-07-17", "2025-01-02"],
            "x": [1, 2, 3, 4],
        }
    )


def test_gate_strips_post_cutoff_rows_by_default(monkeypatch):
    monkeypatch.delenv("FINAL_TEST", raising=False)
    out = data_gate.load(_frame(), "date")
    assert len(out) == 2
    assert out["date"].max() < data_gate.SEAL_CUTOFF


def test_gate_passes_sealed_rows_with_final_test(monkeypatch, capsys):
    monkeypatch.setenv("FINAL_TEST", "1")
    out = data_gate.load(_frame(), "date")
    assert len(out) == 4
    assert "BURNS" in capsys.readouterr().err


def test_gate_does_not_mutate_input(monkeypatch):
    monkeypatch.delenv("FINAL_TEST", raising=False)
    df = _frame()
    data_gate.load(df, "date")
    assert len(df) == 4
    assert not pd.api.types.is_datetime64_any_dtype(df["date"])

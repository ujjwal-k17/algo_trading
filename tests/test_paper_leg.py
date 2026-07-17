"""Synthetic-OHLC tests for the paper-leg engine.

Each test names the SOP_OF_RECORD.md rule it verifies (§4 exits, §7 resolutions).
Rec: entry 100 on 2026-07-01, SL 95, T1 110, T2 120, 5-session hold.
"""

import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import paper_leg

REC = {
    "rec_key": "2026-06-30|TEST|1",
    "entry_date": "2026-07-01",
    "entry_price": 100.0,
    "stop_loss": 95.0,
    "t1": 110.0,
    "t2": 120.0,
}


def _ohlc(rows):
    dates = pd.bdate_range("2026-07-01", periods=len(rows))
    return pd.DataFrame(
        [{"date": d, "open": o, "high": h, "low": l, "close": c}
         for d, (o, h, l, c) in zip(dates, rows)]
    )


def test_clean_t1_hit():  # SOP §4 priority 3: high >= t1 -> exit at t1
    out = paper_leg.settle(REC, _ohlc([(100, 105, 99, 104), (105, 112, 103, 108)]))
    assert out["exit_rule"] == "T1" and out["exit_price"] == 110.0
    assert out["r_multiple"] == pytest.approx(2.0)  # (110-100)/(100-95)
    assert not out["flag_ambiguous_same_bar"]


def test_clean_sl_hit():  # SOP §4 priority 1: low <= sl -> exit at sl
    out = paper_leg.settle(REC, _ohlc([(100, 103, 98, 99), (99, 101, 94, 96)]))
    assert out["exit_rule"] == "SL" and out["exit_price"] == 95.0
    assert out["r_multiple"] == pytest.approx(-1.0)


def test_time_exit_close_of_day5():  # SOP §7.5: close of 5th session, Day 1 = entry day
    flat = [(100, 104, 98, 101)] * 5
    out = paper_leg.settle(REC, _ohlc(flat))
    assert out["exit_rule"] == "TIME" and out["sessions_held"] == 5
    assert out["exit_price"] == 101.0


def test_time_exit_rolls_over_holiday():  # SOP §7.5: bar 5 is next session after a gap
    dates = [pd.Timestamp(d) for d in
             ["2026-07-01", "2026-07-02", "2026-07-03", "2026-07-06", "2026-07-09"]]
    df = pd.DataFrame([{"date": d, "open": 100, "high": 104, "low": 98, "close": 102}
                       for d in dates])
    out = paper_leg.settle(REC, df)
    assert out["exit_rule"] == "TIME"
    assert out["exit_date"] == pd.Timestamp("2026-07-09") and out["exit_price"] == 102


def test_same_bar_t1_and_sl_is_sl_first_and_flagged():  # SOP §7.2 (RULING 4b)
    out = paper_leg.settle(REC, _ohlc([(100, 111, 94, 100)]))
    assert out["exit_rule"] == "SL_SAME_BAR_AMBIGUOUS"
    assert out["exit_price"] == 95.0 and out["flag_ambiguous_same_bar"]


def test_gap_open_below_sl_exits_at_open():  # SOP §7.3 (RULING 4c)
    out = paper_leg.settle(REC, _ohlc([(92, 96, 90, 94)]))
    assert out["exit_rule"] == "SL_GAP_OPEN" and out["exit_price"] == 92.0
    assert out["r_multiple"] == pytest.approx(-1.6)  # worse than -1R: realism


def test_gap_open_above_t1_exits_at_open():  # SOP §7.4 (RULING 4d)
    out = paper_leg.settle(REC, _ohlc([(113, 115, 111, 114)]))
    assert out["exit_rule"] == "T1_GAP_OPEN" and out["exit_price"] == 113.0


def test_t2_beats_t1_within_bar():  # SOP §4 priority 2 over 3 (FACT)
    out = paper_leg.settle(REC, _ohlc([(105, 121, 104, 118)]))
    assert out["exit_rule"] == "T2" and out["exit_price"] == 120.0


def test_halt_carry_flagged_on_entry():  # SOP §7.7 (RULING 4f)
    ohlc = pd.DataFrame([{"date": pd.Timestamp("2026-07-06"),
                          "open": 100, "high": 104, "low": 98, "close": 101}])
    entry = paper_leg.resolve_entry(
        {"pick_date": "2026-06-30", "halted_until": "2026-07-03"}, ohlc)
    assert entry["flag_halt_carry"] and entry["flag_entry_assumed"]
    assert entry["entry_price"] == 100.0  # first available price (RULING 4a/4f)


def test_unsettled_when_data_runs_out():
    out = paper_leg.settle(REC, _ohlc([(100, 104, 98, 101)] * 3))
    assert out["exit_rule"] == "UNSETTLED" and out["sessions_held"] == 3


def test_dividend_credit_and_ex_date_flag():  # amended RULING 4h (Option 1 ruling)
    divs = pd.DataFrame({"ex_date": [pd.Timestamp("2026-07-02")], "dividend": [2.5]})
    flat = [(100, 104, 98, 101)] * 5
    out = paper_leg.settle(REC, _ohlc(flat), dividends=divs)
    assert out["flag_ex_date"] is True and out["dividend_credit"] == 2.5
    assert out["r_multiple"] == pytest.approx((101 - 100 + 2.5) / 5)


def test_ex_date_flag_false_when_evaluated_and_none_in_window():
    divs = pd.DataFrame({"ex_date": [pd.Timestamp("2026-09-01")], "dividend": [2.5]})
    out = paper_leg.settle(REC, _ohlc([(100, 112, 99, 108)]), dividends=divs)
    assert out["flag_ex_date"] is False and out["dividend_credit"] == 0.0

"""Acceptance tests for src/costs_in.py (RULING 5): the worked round-trip
recomputation from plan_52wh.md A2, to the paisa."""

import pytest

from src import costs_in

LAKH = 100_000.0


def test_delivery_round_trip_one_lakh_each_side():
    # Hand-computed in plan_52wh.md A2:
    # STT 200 + exch 6.14 + SEBI 0.20 + stamp 15 + GST 1.1412 + DP 15.34
    total = costs_in.round_trip("delivery", LAKH, LAKH, dp_scrip_days=1)
    assert total == pytest.approx(237.8212, abs=0.005)


def test_delivery_buy_leg_breakdown():
    b = costs_in.delivery_leg("buy", LAKH)
    assert b["brokerage"] == 0.0
    assert b["stt"] == pytest.approx(100.0)
    assert b["exchange_txn"] == pytest.approx(3.07)
    assert b["sebi"] == pytest.approx(0.10)
    assert b["stamp"] == pytest.approx(15.0)
    assert b["gst"] == pytest.approx(0.18 * (3.07 + 0.10))
    assert b["dp"] == 0.0


def test_delivery_sell_leg_has_no_stamp_and_carries_dp():
    s = costs_in.delivery_leg("sell", LAKH, dp_scrip_days=1)
    assert s["stamp"] == 0.0
    assert s["dp"] == pytest.approx(15.34)


def test_intraday_round_trip_one_lakh_each_side():
    # brokerage 40 + STT 25 + exch 6.14 + SEBI 0.20 + stamp 3 + GST 8.3412
    total = costs_in.round_trip("intraday", LAKH, LAKH)
    assert total == pytest.approx(82.6812, abs=0.005)


def test_intraday_brokerage_cap_crossover():
    # Below the cap: 0.03% of ₹50,000 = ₹15 < ₹20.
    small = costs_in.intraday_leg("buy", 50_000.0)
    assert small["brokerage"] == pytest.approx(15.0)
    # Above the cap: 0.03% of ₹1L = ₹30 → capped at ₹20.
    big = costs_in.intraday_leg("buy", LAKH)
    assert big["brokerage"] == pytest.approx(20.0)


def test_stt_dominates_delivery_costs():
    # The structural fact the strategy design leans on: STT is ~84% of a
    # zero-brokerage delivery round trip.
    total = costs_in.round_trip("delivery", LAKH, LAKH, dp_scrip_days=1)
    assert 200.0 / total > 0.8


def test_zero_value_legs():
    assert costs_in.delivery_leg("buy", 0.0)["total"] == 0.0
    assert costs_in.intraday_leg("sell", 0.0)["total"] == 0.0


def test_invalid_inputs_raise():
    with pytest.raises(ValueError):
        costs_in.delivery_leg("short", LAKH)
    with pytest.raises(ValueError):
        costs_in.delivery_leg("buy", LAKH, dp_scrip_days=1)
    with pytest.raises(ValueError):
        costs_in.round_trip("options", LAKH, LAKH)


def test_slippage_not_baked_in():
    # Slippage must remain an explicit external parameter (RULING 5).
    b = costs_in.delivery_leg("buy", LAKH)
    assert "slippage" not in b
    assert costs_in.SLIPPAGE_FLOOR_PER_SIDE == pytest.approx(0.0005)

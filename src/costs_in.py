"""Verified NSE cash-equity cost stack (SPEC-52WH-01 Stage 3, plan_52wh.md A2).

Every constant here is either FACT (statutory, primary-source verified) or
ASSUMPTION (broker schedule, operator-waived contract-note reconciliation) per
RULING 5 in ``governance/DECISIONS.md`` (2026-07-19). Exchange-charge evidence:
``governance/evidence/NSE_FA_73061_transaction_charges_effective_2026-03-01.pdf``.

Slippage is deliberately NOT modeled here. It is a separate, explicit parameter
in the trial harness (literature floor >= 0.05-0.10% per side, higher for mcap
ranks 201-1000) — baking it into statutory constants would hide the assumption.

All rates are fractions of traded value per leg unless noted. DP charge is a
flat rupee amount per scrip per day on the delivery sell leg, GST-inclusive.
"""

from __future__ import annotations

# --- Statutory (FACT) ------------------------------------------------------
STT_DELIVERY = 0.001            # each side (buy AND sell)
STT_INTRADAY_SELL = 0.00025     # sell side only
EXCHANGE_TXN = 0.0000307        # each side; NSE ₹307/crore incl. ₹0.01 IPFT
SEBI_FEE = 0.000001             # each side; ₹10/crore, GST applies
STAMP_DELIVERY_BUY = 0.00015    # buy side only
STAMP_INTRADAY_BUY = 0.00003    # buy side only
GST = 0.18                      # on brokerage + exchange txn + SEBI fee

# --- Broker schedule (ASSUMPTION, RULING 5) --------------------------------
BROKERAGE_DELIVERY = 0.0                 # zero-brokerage delivery plan
BROKERAGE_INTRADAY_RATE = 0.0003         # per executed order...
BROKERAGE_INTRADAY_CAP = 20.0            # ...capped at ₹20, whichever lower
DP_CHARGE_SELL = 15.34                   # ₹/scrip/day, delivery sell, GST incl.

# Literature floor retained as the named slippage fallback (never applied here).
SLIPPAGE_FLOOR_PER_SIDE = 0.0005         # 0.05%; use more for ranks 201-1000


def _brokerage_intraday(value: float) -> float:
    return min(value * BROKERAGE_INTRADAY_RATE, BROKERAGE_INTRADAY_CAP)


def delivery_leg(side: str, value: float, *, dp_scrip_days: int = 0) -> dict:
    """Rupee cost breakdown for one delivery leg of ``value`` traded.

    ``side`` is ``"buy"`` or ``"sell"``. ``dp_scrip_days`` counts scrip-days
    debited on this sell (0 for buys; typically 1 per scrip sold per day).
    """
    if side not in ("buy", "sell"):
        raise ValueError(f"side must be 'buy' or 'sell', got {side!r}")
    if side == "buy" and dp_scrip_days:
        raise ValueError("DP charges apply to sell legs only")
    brokerage = BROKERAGE_DELIVERY * value
    exchange = EXCHANGE_TXN * value
    sebi = SEBI_FEE * value
    breakdown = {
        "brokerage": brokerage,
        "stt": STT_DELIVERY * value,
        "exchange_txn": exchange,
        "sebi": sebi,
        "stamp": STAMP_DELIVERY_BUY * value if side == "buy" else 0.0,
        "gst": GST * (brokerage + exchange + sebi),
        "dp": DP_CHARGE_SELL * dp_scrip_days,
    }
    breakdown["total"] = sum(breakdown.values())
    return breakdown


def intraday_leg(side: str, value: float) -> dict:
    """Rupee cost breakdown for one intraday leg of ``value`` traded."""
    if side not in ("buy", "sell"):
        raise ValueError(f"side must be 'buy' or 'sell', got {side!r}")
    brokerage = _brokerage_intraday(value)
    exchange = EXCHANGE_TXN * value
    sebi = SEBI_FEE * value
    breakdown = {
        "brokerage": brokerage,
        "stt": STT_INTRADAY_SELL * value if side == "sell" else 0.0,
        "exchange_txn": exchange,
        "sebi": sebi,
        "stamp": STAMP_INTRADAY_BUY * value if side == "buy" else 0.0,
        "gst": GST * (brokerage + exchange + sebi),
        "dp": 0.0,
    }
    breakdown["total"] = sum(breakdown.values())
    return breakdown


def round_trip(product: str, buy_value: float, sell_value: float,
               *, dp_scrip_days: int = 1) -> float:
    """Total rupee cost of a buy leg + sell leg. ``product`` is
    ``"delivery"`` or ``"intraday"``. Slippage excluded by design."""
    if product == "delivery":
        return (delivery_leg("buy", buy_value)["total"]
                + delivery_leg("sell", sell_value,
                               dp_scrip_days=dp_scrip_days)["total"])
    if product == "intraday":
        return (intraday_leg("buy", buy_value)["total"]
                + intraday_leg("sell", sell_value)["total"])
    raise ValueError(f"product must be 'delivery' or 'intraday', got {product!r}")

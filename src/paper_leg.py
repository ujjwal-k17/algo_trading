"""Paper-leg settlement engine — pure functions, no I/O.

Computes what a recommendation would have done if executed exactly per SOP.
Every rule traces to governance/SOP_OF_RECORD.md (rules + RULING 4 conventions;
FACT/ASSUMPTION tags live there and in governance/DECISIONS.md).

Conventions implemented (RULING 4):
  a. Entry price when no recorded fill: next-session open (caller resolves;
     see resolve_entry()).
  b. Same-bar SL+T1/T2 touch: SL-first, trade FLAGGED (flag_ambiguous_same_bar).
  c. Gap open below SL: exit at OPEN price, not SL.
  d. Gap open beyond T1 (and, by the residual realism principle, T2): exit at
     OPEN price.
  e. Time exit: close of the 5th holding session (entry day = Day 1); bars are
     trading sessions, so a holiday/halt on the nominal final day naturally
     rolls to the next session's close.
  f. Halted/limit-locked at entry: carry to first available session,
     flag_halt_carry.
  g. Full fill at rec size — counterfactual of the SOP, not of liquidity.
  h. OHLC must be an adjusted series; recs spanning an ex-date are flagged by
     the caller when corporate-action data is supplied (flag_ex_date defaults
     None = not evaluated).

Exit priority within a bar (FACT, exit_manager.py:111-140): SL -> T2 -> T1 ->
TIME. T1 is a FULL exit (FACT: DB semantics, exit_manager.py:127-134,161-168).
R-multiple = (exit - entry) / (entry - stop) (FACT, exit_manager.py:41-45).
"""

from __future__ import annotations

from typing import Optional

import pandas as pd

HOLD_SESSIONS = 5

_OHLC_COLS = ("date", "open", "high", "low", "close")


def resolve_entry(rec: dict, ohlc: pd.DataFrame) -> Optional[dict]:
    """Resolve entry date/price for a rec against its symbol's OHLC sessions.

    RULING 4a: with no recorded fill, entry is the next session's open after
    ``pick_date`` (entry day = Day 1). Returns a dict with entry_date,
    entry_price, flag_entry_assumed, flag_halt_carry — or None if no session
    after pick_date exists in the data (rec not yet enterable).

    If the first available session is more than one calendar step beyond the
    first row after pick_date we cannot distinguish holiday from halt with
    daily data alone; flag_halt_carry is set only when the caller marks the
    symbol halted via rec["halted_until"] (date) — RULING 4f.
    """
    pick_date = pd.Timestamp(rec["pick_date"])
    bars = ohlc.loc[pd.to_datetime(ohlc["date"]) > pick_date]
    if bars.empty:
        return None
    first = bars.iloc[0]
    halted_until = rec.get("halted_until")
    halted = halted_until is not None and pd.Timestamp(first["date"]) > pd.Timestamp(halted_until)
    return {
        "entry_date": pd.Timestamp(first["date"]),
        "entry_price": float(first["open"]),
        "flag_entry_assumed": True,
        "flag_halt_carry": bool(halted),
    }


def settle(rec: dict, ohlc: pd.DataFrame, dividends: pd.DataFrame | None = None) -> dict:
    """Settle one entered rec against subsequent daily OHLC.

    Args:
        rec: dict with entry_date, entry_price, stop_loss, t1, and optionally
            t2, rec_key, flags from resolve_entry().
        ohlc: DataFrame with columns date/open/high/low/close — the symbol's
            UNADJUSTED daily sessions (amended RULING 4h: level comparisons
            replicate exit_manager's actual check against traded prices; rec
            levels are never rescaled), ascending; must include entry_date
            onward.
        dividends: optional DataFrame with ex_date/dividend for the symbol.
            Cash dividends whose ex-date falls inside the holding window
            (entered before ex-date, still held on it) are CREDITED to the
            trade's R (amended RULING 4h); flag_ex_date is the credit marker
            (None = actions data unavailable, not evaluated).

    Returns:
        dict: rec_key, entry_date, entry_price, exit_date, exit_price,
        r_multiple, exit_rule, sessions_held, flag_ambiguous_same_bar,
        flag_halt_carry, flag_entry_assumed, flag_ex_date.
        exit_rule is one of SL / T2 / T1 / TIME / SL_GAP_OPEN / T2_GAP_OPEN /
        T1_GAP_OPEN / SL_SAME_BAR_AMBIGUOUS / UNSETTLED (insufficient data).
    """
    missing = [c for c in _OHLC_COLS if c not in ohlc.columns]
    if missing:
        raise ValueError(f"settle: OHLC missing columns {missing}")

    entry_date = pd.Timestamp(rec["entry_date"])
    entry = float(rec["entry_price"])
    sl = float(rec["stop_loss"])
    t1 = float(rec["t1"])
    t2 = float(rec["t2"]) if rec.get("t2") not in (None, "") else None
    risk = entry - sl

    base = {
        "rec_key": rec.get("rec_key"),
        "entry_date": entry_date,
        "entry_price": entry,
        "exit_date": None,
        "exit_price": None,
        "r_multiple": None,
        "exit_rule": "UNSETTLED",
        "dividend_credit": 0.0,
        "sessions_held": 0,
        "flag_ambiguous_same_bar": False,
        "flag_halt_carry": bool(rec.get("flag_halt_carry", False)),
        "flag_entry_assumed": bool(rec.get("flag_entry_assumed", False)),
        "flag_ex_date": None,  # None = actions data unavailable (amended RULING 4h)
    }

    bars = ohlc.loc[pd.to_datetime(ohlc["date"]) >= entry_date].reset_index(drop=True)
    if bars.empty:
        return base

    def _exit(row, price: float, rule: str, session: int, ambiguous: bool = False) -> dict:
        exit_date = pd.Timestamp(row["date"])
        credit = 0.0
        flag_ex = None
        if dividends is not None:
            ex = pd.to_datetime(dividends["ex_date"])
            in_window = (ex > entry_date) & (ex <= exit_date)
            credit = float(dividends.loc[in_window, "dividend"].sum())
            flag_ex = bool(in_window.any())
        return {
            **base,
            "exit_date": exit_date,
            "exit_price": float(price),
            "r_multiple": round((float(price) - entry + credit) / risk, 4) if risk else None,
            "dividend_credit": credit,
            "exit_rule": rule,
            "sessions_held": session,
            "flag_ambiguous_same_bar": ambiguous,
            "flag_ex_date": flag_ex,
        }

    for i, row in bars.iterrows():
        session = i + 1  # entry day = Day 1 (FACT: market_calendar.py:170-178)
        o, h, l, c = (float(row[k]) for k in ("open", "high", "low", "close"))

        # Gap opens are resolved first — the open prints before intrabar levels
        # (RULING 4c/4d, realism).
        if o <= sl:
            return _exit(row, o, "SL_GAP_OPEN", session)
        if t2 is not None and o >= t2:
            return _exit(row, o, "T2_GAP_OPEN", session)
        if o >= t1:
            return _exit(row, o, "T1_GAP_OPEN", session)

        hit_sl = l <= sl
        hit_t2 = t2 is not None and h >= t2
        hit_t1 = h >= t1

        if hit_sl and (hit_t1 or hit_t2):
            # RULING 4b: touch order unknowable on a daily bar — SL-first, FLAG.
            return _exit(row, sl, "SL_SAME_BAR_AMBIGUOUS", session, ambiguous=True)
        if hit_sl:
            return _exit(row, sl, "SL", session)
        if hit_t2:
            return _exit(row, t2, "T2", session)
        if hit_t1:
            return _exit(row, t1, "T1", session)
        if session >= HOLD_SESSIONS:
            # RULING 4e: close of final holding day (bars are trading sessions,
            # so holidays/halts roll forward naturally).
            return _exit(row, c, "TIME", session)

    return {**base, "sessions_held": len(bars)}

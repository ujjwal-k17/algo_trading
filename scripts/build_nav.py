#!/usr/bin/env python3
"""Derive a daily NAV series (data/derived/nav.parquet) — DERIVED, never from the DB.

Method (when inputs suffice): 5 slots x Rs.1,00,000 book (FACT,
observer.py:1060-1073 capital convention); every entered pick marks one slot
at each session's close from entry through exit; idle cash earns 0.

Inputs required for an honest daily mark:
  1. trades_log snapshot (entered picks with entry/exit) — present.
  2. Daily closes for every held symbol on every session of the holding
     window, from a sanctioned source (data_gate.load_operational).

If input 2 is not available for the full window, this script REFUSES to
approximate and prints exactly what is missing (RULING: no silent NAV).
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))
import data_gate
from run_paper_leg import SNAPSHOT, _latest_ohlc_snapshot, load_settlement_ohlc  # noqa: E402

sys.path.insert(0, str(REPO / "scripts"))

OUT = REPO / "data" / "derived" / "nav.parquet"
SLOT = 100_000.0
BOOK = 500_000.0


def main() -> None:
    raw = pd.read_csv(SNAPSHOT)
    ledger = data_gate.load_operational(raw, "pick_date", source=str(SNAPSHOT))
    ledger["rec_key"] = (
        ledger["pick_date"].dt.strftime("%Y-%m-%d") + "|" + ledger["symbol"].astype(str) + "|1"
    )
    entered = ledger.loc[ledger["exit_reason"] != "AUTO_EXPIRED_5_SESSIONS"]
    need_from = ledger["pick_date"].min()
    need_to = pd.Timestamp.today().normalize()

    ohlc_path = _latest_ohlc_snapshot()
    coverage = {}
    if ohlc_path:
        coverage = load_settlement_ohlc(ohlc_path, ledger)

    if not coverage:
        print("[nav] REFUSING to build: inputs insufficient for an honest daily mark.")
        print(f"[nav] Missing: daily closes for {entered['symbol'].nunique()} held symbols "
              f"across sessions {need_from.date()} -> {need_to.date()} from a sanctioned source.")
        print(f"[nav] Sanctioned OHLC available: "
              f"{ohlc_path or 'none'} — "
              + ("single-day snapshot dated 2026-06-24, entirely before the live window"
                 if ohlc_path else "no prices_eod_backup in any raw snapshot"))
        print("[nav] Unblock: a multi-day adjusted OHLC export from production entering "
              "data/sealed/raw/ via the nightly ingest (RULING 3 amendment already scopes it).")
        sys.exit(1)

    sessions = sorted({d for g in coverage.values() for d in g["date"]})
    rows = []
    for day in sessions:
        mtm = 0.0
        n_held = 0
        for _, p in entered.iterrows():
            if p["pick_date"] >= day:
                continue
            exit_d = pd.to_datetime(p.get("exit_date")) if pd.notna(p.get("exit_date")) else None
            if exit_d is not None and day >= exit_d:
                continue
            sym = coverage.get(p["symbol"])
            if sym is None or day not in set(sym["date"]):
                print(f"[nav] REFUSING: no close for held {p['symbol']} on {day.date()}")
                sys.exit(1)
            close = float(sym.loc[sym["date"] == day, "close"].iloc[0])
            entry = float(p["entry_price"])
            mtm += SLOT * (close / entry)
            n_held += 1
        rows.append({"date": day, "n_held": n_held,
                     "nav": BOOK + mtm - n_held * SLOT})
    out = pd.DataFrame(rows)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    out.to_parquet(OUT, index=False)
    print(f"[nav] {len(out)} daily marks -> {OUT}")


if __name__ == "__main__":
    main()

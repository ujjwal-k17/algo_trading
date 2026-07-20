#!/usr/bin/env python3
"""What still needs an overlay decision — the daily prompt.

    .venv/bin/python scripts/overlay_today.py              # today's recs
    .venv/bin/python scripts/overlay_today.py --date 2026-07-17
    .venv/bin/python scripts/overlay_today.py --all        # whole live window
    .venv/bin/python scripts/overlay_today.py --commands   # paste-able lines only

Prints, for each rec with no logged decision, ONLY what was knowable at
decision time (rec_key, symbol, dates, entry reference close, stop and targets)
and a ready-to-paste ``overlay '<rec_key>' ...`` line. No outcomes, no P&L, no
settled results — by construction (see src/overlay_queue.py).

READ-ONLY. This script never writes governance/overlay_log.csv. Those rows are
the operator's own decisions and the object of the pre-registered study; only
the operator may create them.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

import overlay_queue as oq  # noqa: E402


def _fmt(v: object) -> str:
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return "-"
    if isinstance(v, float):
        return f"{v:,.2f}"
    return str(v)


def render(rows: pd.DataFrame, decisions: dict[str, str]) -> str:
    """Render the decision-time card for each rec. Outcome-blind wall applies."""
    oq.assert_outcome_blind(rows)
    out = []
    for _, r in rows.iterrows():
        key = str(r["rec_key"])
        state = decisions.get(key)
        badge = f"[LOGGED {state}]" if state else "[UNLOGGED]"
        out.append(f"  {badge} {key}")
        out.append(
            f"      {r.get('symbol', '?')}"
            f"   rank {_fmt(r.get('rank'))}"
            f"   conviction {_fmt(r.get('conviction'))}"
        )
        out.append(
            f"      close {_fmt(r.get('close'))}"
            f"   stop {_fmt(r.get('stop_loss'))}"
            f"   t1 {_fmt(r.get('target_1'))}"
            f"   t2 {_fmt(r.get('target_2'))}"
        )
        if not state:
            out.append(f"      overlay '{key}' EXECUTE 1 <reason>")
        out.append("")
    return "\n".join(out)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Overlay decisions still outstanding.")
    ap.add_argument("--date", help="pick date YYYY-MM-DD (default: latest available)")
    ap.add_argument("--all", action="store_true", help="every unlogged rec in the live window")
    ap.add_argument("--commands", action="store_true", help="emit only paste-able command lines")
    ap.add_argument("--log", default=str(oq.OVERLAY_LOG), help="overlay log path")
    args = ap.parse_args(argv)

    recs = oq.live_window_recs()
    if recs.empty:
        print("\n  NO LIVE-WINDOW RECS FOUND in admissible sources.")
        print("  Check that the nightly ingest is landing files in data/sealed/raw/<day>/")
        print("  (tail data/sealed/ingest.log). Nothing can be logged until recs arrive.\n")
        return 1

    b = oq.backlog(recs, args.log)
    decisions = oq.logged_keys(args.log)
    latest = recs["pick_date"].max()

    if args.all:
        rows, scope = b["unlogged"], "ALL UNLOGGED IN LIVE WINDOW"
    else:
        want = pd.Timestamp(args.date) if args.date else latest
        rows = recs.loc[recs["pick_date"] == want]
        scope = f"PICK DATE {want:%Y-%m-%d}"

    if args.commands:
        for line in oq.command_lines(rows.loc[~rows["rec_key"].isin(decisions)]):
            print(line)
        return 0

    print()
    print("=" * 72)
    print(f"  OVERLAY DECISION QUEUE — {scope}")
    print("=" * 72)
    # Ingest health first: if the snapshot is dead, an empty queue below is a
    # pipeline failure, not a quiet day, and the two look identical.
    for warning in oq.ingest_health():
        print(f"  !! INGEST: {warning}")
    if args.date is None and not args.all and latest is not pd.NaT:
        stale = (pd.Timestamp.today().normalize() - latest).days
        if stale > 0:
            print(f"  WARNING: newest available rec is {stale} day(s) old "
                  f"({latest:%Y-%m-%d}). Ingest may be stale — check "
                  f"data/sealed/ingest.log.")
    print()

    if rows.empty:
        print("  Nothing outstanding for this scope.\n")
    else:
        print(render(rows, decisions))

    print("-" * 72)
    print(f"  BACKLOG: {b['n_unlogged']} of {b['n_total']} live-window recs UNLOGGED "
          f"({b['n_logged']} logged)")
    if b["oldest_unlogged"]:
        print(f"  Oldest unlogged pick date: {b['oldest_unlogged']}")
    if b["n_logged"] == 0:
        print("  Analyses 2-4 of governance/AB_PREREG.md have n = 0. Read date "
              "2026-09-27 does not move; lost days are unrecoverable.")
    stale_unlogged = (
        0 if b["unlogged"].empty
        else int((b["unlogged"]["pick_date"] < latest).sum())
    )
    if stale_unlogged:
        print()
        print(f"  NOTE: {stale_unlogged} of the unlogged recs are from PAST pick dates.")
        print("  A decision entered for them now is NOT decision-time evidence — it is")
        print("  recollection, and AB_PREREG analyses 2-4 admit the DECISION_TIME scope")
        print("  only. Log them only if you genuinely recall the call you made at the")
        print("  time, and say so in the reason. They are counted here for honesty about")
        print("  the size of the hole, not as a to-do list.")
    print("-" * 72)
    if not b["by_date"].empty:
        print("\n  per pick date (date  recs  logged  unlogged):")
        for _, r in b["by_date"].iterrows():
            flag = "" if r["n_unlogged"] == 0 else "   <-- outstanding"
            print(f"    {r['date']}   {r['n_recs']:>3}   {r['n_logged']:>3}   "
                  f"{r['n_unlogged']:>3}{flag}")
    print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""SPEC-52WH-01 trial runner — the ONLY place returns are joined to signals.

Stages 1-3 (`pit_universe`, `expr`, `signal_52wh`, `screen_52wh`, `rebalance`)
are features-only by construction: outcome contact exists nowhere in them. This
script is the single door through which that wall is crossed, and it does not
open unless the governance preconditions hold:

  1. `governance/specs/SPEC-52WH-01.md` live sha256 == recorded hash (B3 freeze), and
  2. the named trial_id is already pre-registered in research_register_v2.csv.

Both are checked BEFORE any panel is read, so a failed preflight cannot leak a
glance at outcomes. On completion the run appends a result reference to the
register (append-only, never an edit).

`--preflight-only` verifies the gate and touches no price data at all. A full
run reads the dev panel through the research door (< 2024-07-17), executes the
screened-vs-unscreened walk-forward, scores it net of the RULING 5 cost stack,
and charges the result against the register's CUMULATIVE trial count via
Deflated Sharpe and Hansen SPA.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import date
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
from src import backtest_52wh, data_gate, metrics, pit_universe, spec_guard

SPEC_ID = "SPEC-52WH-01"
REGISTER = REPO / "governance" / "research_register_v2.csv"
PANEL = REPO / "data" / "workspace" / "price_panel_52wh.parquet"
TRI = REPO / "data" / "reference" / "tri" / "raw" / "nifty500_tri.csv"
OUT_DIR = REPO / "data" / "derived" / "trials" / "52wh"

# Opening balance from research_register_v2.csv row INHERITED-0000. ESTIMATE:
# the legacy register's own count was approximate, so the deflation is if
# anything too lenient.
INHERITED_TRIALS = 51

_BANNER = """
------------------------------------------------------------------------
SPEC-52WH-01 TRIAL RUNNER — outcome contact begins past this point.
  spec_id     : {spec_id}
  spec_sha256 : {spec_sha256}
  trial_id    : {trial_id}
  data_tier   : {data_tier}
  description : {trial_description}
Dev data only (< 2024-07-17, research door). The sealed holdout is NOT
opened here: the family's single final test is a separate Phase D
pre-registration and requires FINAL_TEST=1 (which burns it).
------------------------------------------------------------------------
"""


def append_register_result(trial_id: str, verdict: str, note: str) -> None:
    """Append-only: results are new rows, never edits to the pre-registered row."""
    with REGISTER.open(newline="") as fh:
        fieldnames = next(csv.reader(fh))
    with REGISTER.open("a", newline="") as fh:
        csv.DictWriter(fh, fieldnames=fieldnames).writerow(
            {
                "trial_id": f"{trial_id}-RESULT",
                "date": date.today().isoformat(),
                "family": "SPEC_52WH",
                "description": f"Result of {trial_id} (scripts/run_trial_52wh.py)",
                "data_tier": "dev",
                "result": verdict,
                "notes": note,
            }
        )


def cumulative_trial_count() -> int:
    """Register rows that are actual trials, plus the inherited opening balance.

    Convention/freeze/result bookkeeping rows are not trials; counting them
    would inflate the deflation bar for the wrong reason.
    """
    rows = spec_guard.register_rows()
    counted = [
        r for r in rows
        if r.get("data_tier") not in ("n/a", "")
        and not r["trial_id"].startswith(("INHERITED-", "CONVENTION-"))
        and not r["trial_id"].endswith("-RESULT")
    ]
    return INHERITED_TRIALS + len(counted)


def load_benchmark() -> pd.Series:
    """NIFTY 500 TRI daily returns, research-door gated (spec §7 headline)."""
    tri = pd.read_csv(TRI)
    tri["date"] = pd.to_datetime(tri["date"])
    tri = data_gate.load(tri, "date").sort_values("date")
    tri["tri_close"] = pd.to_numeric(tri["tri_close"], errors="coerce")
    s = tri.set_index("date")["tri_close"].dropna()
    return s.pct_change().dropna().rename("nifty500_tri")


def score(result: dict, benchmark: pd.Series, n_trials: int,
          trial_sr_std: float) -> dict:
    """Spec §7 scoring: the headline is the screened-vs-unscreened INCREMENT."""
    arms = result["arms"]
    out = {"params": result["params"], "n_trials_charged": n_trials,
           "trial_sr_std": trial_sr_std, "arms": {}}

    for label, arm in arms.items():
        bench = benchmark.reindex(arm.net_returns.index).dropna()
        aligned = arm.net_returns.reindex(bench.index)
        out["arms"][label] = {
            "net": metrics.summary(aligned, benchmark=bench),
            "gross": metrics.summary(arm.gross_returns.reindex(bench.index)),
            "annual_turnover_one_way": arm.annual_turnover,
            "total_cost_frac": float(arm.costs.sum()),
            "n_rebalances": int(len(arm.turnover)),
            "frozen_symbol_days": arm.diagnostics["frozen_symbol_days"],
            "median_holdings": float(arm.n_holdings.median()),
        }

    # The claim under test: does the screen add net IR over the same book?
    scr = arms["screened"].net_returns
    uns = arms["unscreened"].net_returns
    common = scr.index.intersection(uns.index).intersection(benchmark.index)
    incr = (scr.reindex(common) - uns.reindex(common)).dropna()
    out["increment"] = {
        "ann_return_delta": (metrics.annualized_return(scr.reindex(common))
                             - metrics.annualized_return(uns.reindex(common))),
        "ir_delta": (metrics.information_ratio(scr.reindex(common), benchmark.reindex(common))
                     - metrics.information_ratio(uns.reindex(common), benchmark.reindex(common))),
        "maxdd_delta": (metrics.max_drawdown(scr.reindex(common))
                        - metrics.max_drawdown(uns.reindex(common))),
        "skew_delta": (metrics.skew(scr.reindex(common))
                       - metrics.skew(uns.reindex(common))),
        "incremental_sharpe": metrics.sharpe(incr),
    }
    out["inference"] = {
        "deflated_sharpe_screened_active": metrics.deflated_sharpe(
            (scr.reindex(common) - benchmark.reindex(common)).dropna(),
            n_trials=n_trials, trial_sr_std=trial_sr_std,
        ),
        "spa_screen_vs_unscreened": metrics.hansen_spa(
            pd.DataFrame({"screen_increment": incr}), n_boot=1000, seed=0
        ),
    }

    # Spec §8, applied mechanically — no post-hoc renegotiation.
    ir = out["arms"]["screened"]["net"]["information_ratio"]
    spa = out["inference"]["spa_screen_vs_unscreened"]
    p = spa["p_value"]
    turn = out["arms"]["screened"]["annual_turnover_one_way"]
    # Deterministic kills need no inference and are never softened: spec §5 is
    # explicit that a budget bust is dead REGARDLESS of gross, and a non-positive
    # net IR is an arithmetic fact, not an estimate.
    deterministic = []
    if ir <= 0:
        deterministic.append(f"net IR {ir:.3f} <= 0")
    if turn > 3.0:
        deterministic.append(f"one-way turnover {turn:.1%}/yr busts the 300% budget")

    if deterministic:
        verdict, reasons = "DEAD", list(deterministic)
    elif spa.get("degenerate_models"):
        # SPA could not be studentized. Reporting DEAD on that basis would blame
        # the strategy for a modelling artifact; withhold the verdict instead.
        verdict = "INCONCLUSIVE"
        reasons = [f"SPA degenerate ({spa['note']}) — inference verdict withheld"]
    elif p > 0.10:
        verdict, reasons = "DEAD", [f"SPA p {p:.3f} > 0.10"]
    else:
        verdict, reasons = "SURVIVES", []

    out["kill_line"] = {
        "verdict": verdict,
        "reasons": reasons,
        "rule": "spec §8: net IR <= 0, or SPA/RC p > 0.10 net of costs -> family dead; "
                "spec §5: turnover budget bust is an independent kill",
    }
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--trial-id",
        required=True,
        help="pre-registered trial_id in research_register_v2.csv (e.g. C1-52WH-0001)",
    )
    ap.add_argument(
        "--preflight-only",
        action="store_true",
        help="verify the freeze + register gate and exit; touches no price data",
    )
    ap.add_argument("--band", default="201-1000", help="PIT universe band (spec §4)")
    ap.add_argument("--freq", default="Q", choices=("Q", "M", "H"),
                    help="rebalance frequency (spec §5; Q is the default, M/H sensitivities)")
    ap.add_argument("--exclude-buckets", default="Q1",
                    help="comma-separated buckets to screen out (spec §3; 'Q1,Q2' sensitivity)")
    ap.add_argument("--unranked-policy", default="keep", choices=("keep", "drop"))
    ap.add_argument("--slippage-per-side", type=float, default=0.0005,
                    help="spec §7 floor is 0.05%%/side; stress higher for ranks 201-1000")
    ap.add_argument("--book-value", type=float, default=backtest_52wh.DEFAULT_BOOK_VALUE,
                    help="₹ book size; only the flat DP charge is size-sensitive")
    ap.add_argument("--trial-sr-std", type=float, default=0.5,
                    help="cross-trial ANNUALIZED Sharpe dispersion for DSR (ASSUMPTION)")
    ap.add_argument("--n-trials", type=int, default=None,
                    help="override the cumulative trial count charged to DSR")
    ap.add_argument("--tag", default="", help="suffix for the output directory")
    args = ap.parse_args()

    try:
        stamp = spec_guard.preflight(SPEC_ID, args.trial_id)
    except spec_guard.SpecGuardError as exc:
        print(f"[REFUSED] {exc}", file=sys.stderr)
        return 2

    print(_BANNER.format(**stamp))

    if args.preflight_only:
        print("[preflight] gate PASSED — no data touched (--preflight-only).")
        return 0

    if not PANEL.exists():
        print(f"[REFUSED] price panel missing: {PANEL}\n"
              "Build it with scripts/build_price_panel.py first.", file=sys.stderr)
        return 4

    n_trials = args.n_trials or cumulative_trial_count()
    print(f"[trial] charging this result against {n_trials} cumulative trials "
          f"({INHERITED_TRIALS} inherited + register rows); "
          f"trial_sr_std={args.trial_sr_std} (ASSUMPTION)")

    panel = data_gate.load(pd.read_parquet(PANEL), "date")
    store = pit_universe.load_store()
    print(f"[data] panel {len(panel):,} rows, {panel['symbol'].nunique():,} symbols, "
          f"max date {panel['date'].max().date()}")

    print("[walk-forward] rebalance schedule:")
    result = backtest_52wh.run_walk_forward(
        panel, store, stamp=stamp,
        band=args.band, freq=args.freq,
        exclude_buckets=tuple(b.strip() for b in args.exclude_buckets.split(",") if b.strip()),
        unranked_policy=args.unranked_policy,
        book_value=args.book_value,
        slippage_per_side=args.slippage_per_side,
    )

    benchmark = load_benchmark()
    scored = score(result, benchmark, n_trials, args.trial_sr_std)

    out_dir = OUT_DIR / (args.trial_id + (f"_{args.tag}" if args.tag else ""))
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "summary.json").write_text(json.dumps(scored, indent=2, default=str))
    result["schedule"].to_csv(out_dir / "schedule.csv", index=False)
    for label, arm in result["arms"].items():
        pd.DataFrame({"gross": arm.gross_returns, "net": arm.net_returns}).to_csv(
            out_dir / f"returns_{label}.csv"
        )

    scr = scored["arms"]["screened"]["net"]
    uns = scored["arms"]["unscreened"]["net"]
    print(f"\n  screened   : IR {scr['information_ratio']:+.3f}  "
          f"ann {scr['ann_return']:+.2%}  maxDD {scr['max_drawdown']:.2%}  "
          f"skew {scr['skew']:+.2f}")
    print(f"  unscreened : IR {uns['information_ratio']:+.3f}  "
          f"ann {uns['ann_return']:+.2%}  maxDD {uns['max_drawdown']:.2%}  "
          f"skew {uns['skew']:+.2f}")
    print(f"  increment  : IR {scored['increment']['ir_delta']:+.3f}  "
          f"SPA p {scored['inference']['spa_screen_vs_unscreened']['p_value']:.3f}  "
          f"DSR {scored['inference']['deflated_sharpe_screened_active']['dsr']:.3f}")
    print(f"  turnover   : {scored['arms']['screened']['annual_turnover_one_way']:.1%}/yr one-way")
    verdict = scored["kill_line"]["verdict"]
    print(f"\n  KILL LINE  : {verdict}"
          + (f" — {'; '.join(scored['kill_line']['reasons'])}" if scored["kill_line"]["reasons"] else ""))
    print(f"  outputs    : {out_dir}")

    append_register_result(
        args.trial_id, verdict,
        f"screened net IR {scr['information_ratio']:+.4f}, increment IR "
        f"{scored['increment']['ir_delta']:+.4f}, SPA p "
        f"{scored['inference']['spa_screen_vs_unscreened']['p_value']:.4f}, DSR "
        f"{scored['inference']['deflated_sharpe_screened_active']['dsr']:.4f}, "
        f"one-way turnover {scored['arms']['screened']['annual_turnover_one_way']:.2%}/yr, "
        f"charged vs {n_trials} trials (trial_sr_std={args.trial_sr_std} ASSUMPTION); "
        f"artifacts {out_dir.relative_to(REPO)}"
    )
    print("  register   : result row appended (append-only)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

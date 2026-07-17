"""Overlay-alpha join: paper-leg results vs the discretionary overlay log.

Analysis only — no significance claims are computed here by design.

Conventions:
- overlay_log.csv is append-only; corrections are new rows with the same
  rec_key; analysis takes the LAST row per rec_key (file order).
- executed_size is the fraction of the one-slot SOP size (1 = execute full,
  0 = veto, 0<x<1 = reduce) — ASSUMPTION, governance/README_overlay.md.
- Per-trade: recommended outcome = paper-leg R; executed outcome =
  paper R x executed_size; overlay delta = executed - recommended.
- RULING 4b: weekly summaries report with AND without trades flagged
  ambiguous (same-bar SL+target).
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

import data_gate

REPO = Path(__file__).resolve().parents[1]
OVERLAY_LOG = REPO / "governance" / "overlay_log.csv"


def last_per_key(overlay: pd.DataFrame) -> pd.DataFrame:
    """Collapse the append-only log to the last row per rec_key (file order)."""
    return overlay.groupby("rec_key", sort=False).tail(1).reset_index(drop=True)


def load_overlay(path: str | Path = OVERLAY_LOG) -> pd.DataFrame:
    """Load the overlay log through the Tier 1 door and collapse corrections."""
    df = pd.read_csv(path)
    if df.empty:
        return df
    df = data_gate.load_operational(df, "ts_local", source=str(path))
    return last_per_key(df)


def join_overlay(paper: pd.DataFrame, overlay: pd.DataFrame) -> pd.DataFrame:
    """Join paper-leg settlements to overlay decisions on rec_key.

    Returns one row per overlay-decided rec: paper (recommended) outcome,
    executed outcome scaled by executed_size, and the overlay delta.
    Vetoes (executed_size 0) contribute 0 executed R by construction.
    """
    overlay = last_per_key(overlay)
    joined = overlay.merge(paper, on="rec_key", how="left", validate="one_to_one")
    size = pd.to_numeric(joined["executed_size"], errors="coerce").fillna(0.0)
    joined["recommended_r"] = joined["r_multiple"]
    joined["executed_r"] = joined["r_multiple"] * size
    joined["delta_r"] = joined["executed_r"] - joined["recommended_r"]
    return joined


def reconcile_fills(joined: pd.DataFrame, ledger: pd.DataFrame) -> pd.DataFrame:
    """Reconcile paper-leg exit prices vs actual fills recorded in trades_log,
    for EXECUTED overlay trades only. This is the only settlement check
    independent of yfinance (production prices from yfinance too).

    Returns per-trade rows with pct divergence; empty if no executed trade has
    an actual exit fill recorded yet.
    """
    executed = joined.loc[joined["decision"] == "EXECUTE"]
    fills = ledger.loc[ledger["exit_price"].notna(), ["rec_key", "exit_price"]].rename(
        columns={"exit_price": "actual_exit"}
    )
    rec = executed.merge(fills, on="rec_key", how="inner")
    if rec.empty:
        return pd.DataFrame(columns=["rec_key", "paper_exit", "actual_exit", "pct_divergence"])
    rec["pct_divergence"] = (
        (rec["exit_price"] - rec["actual_exit"]) / rec["actual_exit"] * 100
    )
    return rec[["rec_key", "exit_price", "actual_exit", "pct_divergence"]].rename(
        columns={"exit_price": "paper_exit"}
    )


def weekly_summary(joined: pd.DataFrame, ledger: pd.DataFrame | None = None) -> pd.DataFrame:
    """Weekly overlay-vs-paper summary. Descriptive only — no significance
    claims; RULING 4b: rows are emitted for all trades and for the subset
    excluding flag_ambiguous_same_bar trades."""
    settled = joined.loc[joined["exit_date"].notna()].copy()
    if settled.empty:
        return pd.DataFrame()
    settled["week"] = pd.to_datetime(settled["exit_date"]).dt.strftime("%G-W%V")

    def _agg(df: pd.DataFrame, scope: str) -> pd.DataFrame:
        g = df.groupby("week")
        out = g.agg(
            n_trades=("rec_key", "count"),
            n_veto=("decision", lambda s: (s == "VETO").sum()),
            n_reduce=("decision", lambda s: (s == "REDUCE").sum()),
            recommended_r_sum=("recommended_r", "sum"),
            executed_r_sum=("executed_r", "sum"),
            delta_r_sum=("delta_r", "sum"),
        ).reset_index()
        out.insert(1, "scope", scope)
        return out

    full = _agg(settled, "all")
    clean = settled.loc[~settled["flag_ambiguous_same_bar"].fillna(False)]
    parts = [full] + ([_agg(clean, "ex_ambiguous")] if not clean.empty else [])
    out = pd.concat(parts, ignore_index=True).sort_values(["week", "scope"]).reset_index(drop=True)

    if ledger is not None:
        rec = reconcile_fills(joined, ledger)
        if rec.empty:
            print("[reconcile] no executed trades with recorded exit fills yet")
        else:
            d = rec["pct_divergence"]
            print(f"[reconcile] paper vs actual exits, {len(rec)} executed trades: "
                  f"mean {d.mean():+.2f}% | median {d.median():+.2f}% | "
                  f"min {d.min():+.2f}% | max {d.max():+.2f}%")
    return out

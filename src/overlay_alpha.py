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


def join_overlay(
    paper: pd.DataFrame,
    overlay: pd.DataFrame,
    ledger: pd.DataFrame | None = None,
    provenance: str = "DECISION_TIME",
) -> pd.DataFrame:
    """Join paper-leg settlements to overlay decisions on rec_key.

    Returns one row per overlay-decided rec: paper (recommended) outcome,
    executed outcome scaled by executed_size, and the overlay delta.
    Vetoes (executed_size 0) contribute 0 executed R by construction.

    Fills basis (pre-log window ruling): where the ledger records an actual
    exit fill, the EXECUTED leg's R is recomputed from the fill instead of the
    paper exit price (requires stop_loss in the paper frame). Ledger
    entry_price is NEVER used as a fill — it records rec-close, not a fill.
    """
    overlay = last_per_key(overlay)
    joined = overlay.merge(paper, on="rec_key", how="left", validate="one_to_one")
    size = pd.to_numeric(joined["executed_size"], errors="coerce").fillna(0.0)
    joined["recommended_r"] = joined["r_multiple"]
    executed_base = joined["r_multiple"].copy()
    joined["fill_based"] = False
    if ledger is not None and "stop_loss" in joined.columns and "pick_date" in joined.columns:
        fills = ledger.loc[ledger["exit_price"].notna(),
                           ["pick_date", "symbol", "exit_price"]].rename(
            columns={"exit_price": "actual_exit"})
        fills["pick_date"] = pd.to_datetime(fills["pick_date"])
        joined["pick_date"] = pd.to_datetime(joined["pick_date"])
        joined = joined.merge(fills, on=["pick_date", "symbol"], how="left")
        risk = joined["entry_price"] - joined["stop_loss"]
        has_fill = joined["actual_exit"].notna() & risk.gt(0) & joined["entry_price"].notna()
        executed_base = executed_base.where(
            ~has_fill,
            (joined["actual_exit"] - joined["entry_price"]
             + joined.get("dividend_credit", 0.0).fillna(0.0)) / risk,
        )
        joined["fill_based"] = has_fill
    joined["executed_r"] = executed_base * size
    joined["delta_r"] = joined["executed_r"] - joined["recommended_r"]
    joined["provenance"] = provenance
    return joined


def reconstruct_overlay(
    universe_paper: pd.DataFrame,
    ledger: pd.DataFrame,
    first_log_date: str | pd.Timestamp | None = None,
) -> tuple[pd.DataFrame, int]:
    """RECONSTRUCTED scope for the pre-log window (ruling, DECISIONS.md).

    Infers decisions by joining the settled rec universe against trades_log:
    matching ENTERED trade -> EXECUTE (size 1); no matching trade -> inferred
    VETO (size 0); matching AUTO_EXPIRED row -> SYSTEM_NO_ENTRY, excluded from
    grading (count returned). Binary only — REDUCE is not inferable.

    Returns (synthetic overlay frame, n_system_no_entry). Feed the frame to
    join_overlay(..., provenance="RECONSTRUCTED"); never merge with the
    decision-time scope.
    """
    recs = universe_paper.copy()
    recs["pick_date"] = pd.to_datetime(recs["pick_date"])
    if first_log_date is not None:
        recs = recs.loc[recs["pick_date"] < pd.Timestamp(first_log_date)]
    led = ledger.copy()
    led["pick_date"] = pd.to_datetime(led["pick_date"])
    expired = led["exit_reason"] == "AUTO_EXPIRED_5_SESSIONS"
    entered_keys = set(zip(led.loc[~expired, "pick_date"], led.loc[~expired, "symbol"]))
    expired_keys = set(zip(led.loc[expired, "pick_date"], led.loc[expired, "symbol"]))

    rows, n_system = [], 0
    for _, r in recs.iterrows():
        k = (r["pick_date"], r["symbol"])
        if k in expired_keys:
            n_system += 1
            continue
        if k in entered_keys:
            dec, size, why = "EXECUTE", 1, "reconstructed: matching entered trade"
        else:
            dec, size, why = "VETO", 0, "reconstructed: no matching trade"
        rows.append({"ts_local": None, "rec_key": r["rec_key"], "decision": dec,
                     "executed_size": size, "reason": why})
    return (
        pd.DataFrame(rows, columns=["ts_local", "rec_key", "decision", "executed_size", "reason"]),
        n_system,
    )


def reconcile_fills(joined: pd.DataFrame, ledger: pd.DataFrame) -> pd.DataFrame:
    """Reconcile paper-leg exit prices vs actual fills recorded in trades_log,
    for EXECUTED overlay trades only. This is the only settlement check
    independent of yfinance (production prices from yfinance too).

    Returns per-trade rows with pct divergence; empty if no executed trade has
    an actual exit fill recorded yet.
    """
    executed = joined.loc[joined["decision"] == "EXECUTE"].copy()
    fills = ledger.loc[ledger["exit_price"].notna(),
                       ["pick_date", "symbol", "exit_price"]].rename(
        columns={"exit_price": "actual_exit"}
    )
    if executed.empty or fills.empty or "pick_date" not in executed.columns:
        return pd.DataFrame(columns=["rec_key", "paper_exit", "actual_exit", "pct_divergence"])
    fills["pick_date"] = pd.to_datetime(fills["pick_date"])
    executed["pick_date"] = pd.to_datetime(executed["pick_date"])
    if "actual_exit" in executed.columns:  # already merged by join_overlay
        rec = executed.loc[executed["actual_exit"].notna()].copy()
    else:
        rec = executed.merge(fills, on=["pick_date", "symbol"], how="inner")
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
    if "provenance" in joined.columns and joined["provenance"].nunique() > 1:
        raise ValueError(
            "weekly_summary: mixed provenance — RECONSTRUCTED and DECISION_TIME "
            "scopes must never be merged (pre-log window ruling)"
        )
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
        out.insert(1, "provenance", df["provenance"].iloc[0] if "provenance" in df else "DECISION_TIME")
        return out

    if "system_entered" in settled.columns and settled["system_entered"].notna().any():
        # Assumed-entry audit ruling (DECISIONS.md 2026-07-18): the headline is
        # the gate-respecting (system-entered) figure; recs settled from
        # AUTO_EXPIRED rows via assumed entries report in a separate
        # ASSUMED_ENTRY scope — never merged, like RECONSTRUCTED.
        entered = settled.loc[settled["system_entered"].astype(bool)]
        assumed = settled.loc[~settled["system_entered"].astype(bool)]
        parts = []
        if not entered.empty:
            parts.append(_agg(entered, "entered"))
            clean = entered.loc[~entered["flag_ambiguous_same_bar"].fillna(False)]
            if not clean.empty:
                parts.append(_agg(clean, "entered_ex_ambiguous"))
        if not assumed.empty:
            parts.append(_agg(assumed, "assumed_entry"))
        out = (pd.concat(parts, ignore_index=True)
               .sort_values(["week", "scope"]).reset_index(drop=True))
    else:
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

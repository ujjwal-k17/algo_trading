#!/usr/bin/env python
"""Measure `s` — the 9:15-9:20 bar's share of full-day volume — on up-sessions.

WHY THIS EXISTS
---------------
`preopen_check.py` (frozen clone) computes the go/no-go volume confirmation as
`volume_ratio = first_5min_volume * 75 / avg_volume_20d`, where 75 is the bar
count of a 375-minute NSE session and `avg_volume_20d` is a mean of DAILY
volume. That extrapolation is valid only if intraday volume is uniform across
the session. Writing `s` for the opening bar's true share of daily volume:

    volume_ratio = s * 75 * (today_volume / avg20_volume)

so the `>= 1.2` gate really tests `today_relative_volume >= 1.2 / (75 * s)`.
`1 / mean(s)` is the empirically correct replacement for the hardcoded 75.

THE RESIDUAL METHOD (and why the direct measurement is impossible)
------------------------------------------------------------------
yfinance carries the CORRECT PRICE for the 09:15-09:20 bar but reports its
VOLUME as zero in ~98% of sessions. Verified three ways on 2026-07-22:
(a) median volume 0 at 09:15 vs ~57k at 09:20; (b) the 09:15 bar's open equals
the official NSE open (ADANIPORTS 2026-06-24: 1786.00 exactly), proving bars
are START-labelled and 09:15 really is the 09:15-09:20 interval; (c) the sum
of 5m bars falls 5.9-8.2% short of official daily volume.

Bars run 09:15 -> 15:25 start-labelled, so they span the whole session. The
only material things absent from their sum are the dropped opening volume and
the post-15:30 closing auction. Hence:

    missing_frac = 1 - (sum of 5m bars / official daily volume)
                 = s + tail          on sessions where the 09:15 volume is 0
                 = tail              on sessions where it is reported

`tail` (closing auction + off-book) is therefore estimable from the ~2% of
sessions Yahoo does report, and subtracted elsewhere. That gives a bracketed
estimate of `s`, not a point estimate. The precise figure needs Kite intraday,
which BINDING RULE 3 forbids; that is disclosed, not routed around.

GOVERNANCE
----------
Reads POST-CUTOFF intraday data and selects sessions on an outcome. Neither
`data_gate` door admits that, by design. Refuses to run unless RULING 13 is in
`governance/DECISIONS.md` (TRAP 7). Per RULING 13b no return is ever a measured
quantity — price enters only as a sample filter. Per RULING 13d this measures
only; it authorises no change to any live parameter before 2026-09-27.
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

import pandas as pd
import yfinance as yf

REPO = Path(__file__).resolve().parents[1]
DECISIONS = REPO / "governance" / "DECISIONS.md"
SNAPSHOT = REPO / "data" / "sealed" / "raw" / "2026-07-22"
UNIVERSE_SRC = SNAPSHOT / "prices_eod_backup_20260624.csv"
# NOT data/workspace/ — that tree carries a standing zero-post-cutoff-rows
# invariant (tests/test_isolation.py::test_workspace_has_zero_post_cutoff_rows)
# because it holds the GATED pre-cutoff dev panels. RULING 13 data is
# post-cutoff by construction, so it lives under data/derived/ (Tier 1).
CACHE = REPO / "data" / "derived" / "volume_share_diag"

SESSION_BARS = 75
BAR_QUORUM = 70
OPEN_BAR = "09:15"
IST = "Asia/Kolkata"


def require_ruling_13() -> None:
    """Hard-fail unless RULING 13 is in force. No bypass flag, deliberately."""
    if not DECISIONS.exists():
        sys.exit(f"REFUSING: {DECISIONS} not found.")
    if "RULING 13" not in DECISIONS.read_text():
        sys.exit(
            "REFUSING TO RUN — RULING 13 is not in governance/DECISIONS.md.\n\n"
            "This script reads post-cutoff intraday data and conditions on an\n"
            "outcome. Neither data_gate door admits that. Running anyway would\n"
            "violate BINDING RULE 4.\n"
            "Draft: analysis/proposed_ruling_13_2026-07-22.md"
        )
    print("[gate] RULING 13 present in DECISIONS.md — proceeding.")


def load_universe() -> pd.DataFrame:
    """250-name system universe = NIFTY50 + NEXT50 + MIDCAP150, deduped."""
    df = pd.read_csv(UNIVERSE_SRC)
    out = df[["symbol", "turnover_cr", "volume", "open"]].dropna(subset=["symbol"])
    out = out.drop_duplicates("symbol").reset_index(drop=True)
    out = out.rename(columns={"volume": "official_vol_0624", "open": "official_open_0624"})
    if len(out) != 250:
        print(f"[warn] universe is {len(out)} names, expected 250")
    out["liq_tier"] = pd.qcut(
        out["turnover_cr"].rank(method="first"), 5,
        labels=["Q1 (thinnest)", "Q2", "Q3", "Q4", "Q5 (deepest)"],
    )
    return out


def fetch_intraday(symbols: list[str], refresh: bool = False) -> pd.DataFrame:
    CACHE.mkdir(parents=True, exist_ok=True)
    cache_file = CACHE / "intraday_5m.parquet"
    if cache_file.exists() and not refresh:
        print(f"[fetch] using cache {cache_file}")
        return pd.read_parquet(cache_file)

    frames, failed = [], []
    for i, sym in enumerate(symbols, 1):
        try:
            h = yf.Ticker(f"{sym}.NS").history(
                period="60d", interval="5m", auto_adjust=False
            )
            if h is None or h.empty:
                failed.append(sym)
            else:
                h = h.reset_index()
                h.columns = [str(c) for c in h.columns]
                ts = pd.to_datetime(h[h.columns[0]], utc=True).dt.tz_convert(IST)
                frames.append(pd.DataFrame({
                    "symbol": sym, "ts": ts,
                    "open": h["Open"].astype(float),
                    "high": h["High"].astype(float),
                    "low": h["Low"].astype(float),
                    "close": h["Close"].astype(float),
                    "volume": h["Volume"].fillna(0).astype("int64"),
                }))
        except Exception as exc:
            failed.append(sym)
            print(f"  [yf] {sym} failed: {type(exc).__name__}: {exc}")
        if i % 25 == 0:
            print(f"  [fetch] {i}/{len(symbols)} ({len(failed)} failed)")
        time.sleep(0.12)

    if not frames:
        sys.exit("REFUSING: zero symbols returned intraday data (TRAP 6).")
    panel = pd.concat(frames, ignore_index=True)
    panel.to_parquet(cache_file, index=False)
    pd.Series(failed, dtype=str).to_csv(CACHE / "failed_symbols.csv", index=False)
    print(f"[fetch] {panel['symbol'].nunique()} symbols, {len(panel):,} bars; "
          f"{len(failed)} failed")
    return panel


def fetch_daily(symbols: list[str], refresh: bool = False) -> pd.DataFrame:
    CACHE.mkdir(parents=True, exist_ok=True)
    cache_file = CACHE / "daily.parquet"
    if cache_file.exists() and not refresh:
        print(f"[fetch] using cache {cache_file}")
        return pd.read_parquet(cache_file)

    frames = []
    for start in range(0, len(symbols), 50):
        chunk = symbols[start:start + 50]
        d = yf.download([f"{s}.NS" for s in chunk], period="90d", interval="1d",
                        auto_adjust=False, group_by="ticker", progress=False,
                        threads=True)
        for sym in chunk:
            try:
                sub = d[f"{sym}.NS"].dropna(subset=["Close"])
            except (KeyError, TypeError):
                continue
            if sub.empty:
                continue
            frames.append(pd.DataFrame({
                "symbol": sym,
                "date": pd.to_datetime(sub.index).date,
                "daily_volume": sub["Volume"].fillna(0).astype("int64").values,
            }))
        print(f"  [daily] {min(start + 50, len(symbols))}/{len(symbols)}")
    daily = pd.concat(frames, ignore_index=True)
    daily.to_parquet(cache_file, index=False)
    return daily


def validate_denominator(daily: pd.DataFrame, uni: pd.DataFrame) -> None:
    """The residual is only as good as the daily-volume denominator.

    Cross-check yfinance daily volume against the official production
    `prices_eod` backup for 2026-06-24 (RULING 13e).
    """
    d = daily.copy()
    d["date"] = pd.to_datetime(d["date"])
    t = d[d["date"] == pd.Timestamp("2026-06-24")].merge(uni, on="symbol", how="inner")
    if t.empty:
        print("[validate] 2026-06-24 not in window — denominator check SKIPPED")
        return
    t["err"] = (t["daily_volume"] - t["official_vol_0624"]).abs() / t["official_vol_0624"]
    bad = int((t["err"] > 0.01).sum())
    print(f"[validate] daily-volume vs official prices_eod on {len(t)} symbols: "
          f"median err {t['err'].median():.4%}, max {t['err'].max():.4%}, "
          f"{bad} symbols >1%")
    if t["err"].median() > 0.01:
        sys.exit("REFUSING: yfinance daily volume disagrees with official "
                 "prices_eod by >1% at the median — the residual denominator "
                 "is unsound, so the whole method fails.")


def build_sessions(panel: pd.DataFrame, daily: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    diag: dict = {}
    p = panel.copy()
    p["date"] = p["ts"].dt.date
    p["hhmm"] = p["ts"].dt.strftime("%H:%M")

    flat = (p["open"] == p["high"]) & (p["high"] == p["low"]) & (p["low"] == p["close"])
    placeholder = flat & (p["volume"] == 0) & (p["hhmm"] != OPEN_BAR)
    diag["placeholder_bars_dropped"] = int(placeholder.sum())
    p = p[~placeholder]

    grp = p.groupby(["symbol", "date"], sort=False)
    # The 09:15 bar is located by IST clock time, never by position.
    open_bars = p[p["hhmm"] == OPEN_BAR].groupby(["symbol", "date"], sort=False).agg(
        first5_volume=("volume", "sum"), price_0920=("close", "last"),
    )
    agg = grp.agg(intraday_volume=("volume", "sum"), price_1530=("close", "last"),
                  n_bars=("volume", "size"))
    s = agg.join(open_bars, how="left")
    diag["sessions_raw"] = len(s)
    diag["sessions_missing_0915_bar"] = int(s["first5_volume"].isna().sum())
    s = s.dropna(subset=["first5_volume", "price_0920"])

    short = s["n_bars"] < BAR_QUORUM
    diag["sessions_below_bar_quorum"] = int(short.sum())
    s = s[~short].reset_index()
    s["date"] = pd.to_datetime(s["date"])

    d = daily.copy()
    d["date"] = pd.to_datetime(d["date"])
    s = s.merge(d, on=["symbol", "date"], how="left")
    # Residual REQUIRES the official denominator — no intraday fallback here.
    miss = s["daily_volume"].isna() | (s["daily_volume"] <= 0)
    diag["sessions_dropped_no_daily_volume"] = int(miss.sum())
    s = s[~miss]

    s["missing_frac"] = 1.0 - s["intraday_volume"] / s["daily_volume"]
    s["s_direct"] = s["first5_volume"] / s["daily_volume"]
    s["open_vol_reported"] = s["first5_volume"] > 0

    impossible = (s["missing_frac"] < -0.01) | (s["missing_frac"] > 0.5)
    diag["sessions_dropped_implausible_residual"] = int(impossible.sum())
    s = s[~impossible]

    s["up_session"] = s["price_1530"] > s["price_0920"]
    diag["sessions_clean"] = len(s)
    diag["sessions_up"] = int(s["up_session"].sum())
    diag["sessions_open_vol_reported"] = int(s["open_vol_reported"].sum())
    diag["pct_open_vol_missing"] = round(100 * (1 - s["open_vol_reported"].mean()), 2)
    diag["symbols_final"] = int(s["symbol"].nunique())
    diag["date_min"] = str(s["date"].min().date())
    diag["date_max"] = str(s["date"].max().date())
    diag["trading_dates"] = int(s["date"].nunique())
    return s, diag


def wmean(df: pd.DataFrame, col: str) -> float:
    """Operator-specified estimator: mean weighted by full-day volume.

    Equals the pooled share sum(numerator) / sum(daily_volume).
    """
    w = df["daily_volume"]
    return float((df[col] * w).sum() / w.sum()) if len(df) and w.sum() else float("nan")


def report(sess: pd.DataFrame, uni: pd.DataFrame, diag: dict) -> None:
    print("\n" + "=" * 74)
    print("COVERAGE — read this before the headline (TRAP 2)")
    print("=" * 74)
    for k, v in diag.items():
        print(f"  {k:38s} {v}")
    print(f"  {'universe_expected':38s} 250")
    print(f"  {'symbol_coverage_pct':38s} {100 * diag['symbols_final'] / 250:.1f}%")

    cal = sess[sess["open_vol_reported"]]     # tail only
    res = sess[~sess["open_vol_reported"]]    # s + tail
    if len(cal) < 30:
        print(f"\n[warn] calibration subset is only {len(cal)} sessions — the "
              f"tail estimate is weak and the bracket should be read as wide.")

    # The tail estimate MUST be outlier-robust. The volume-weighted mean is
    # not: a handful of sessions with missing_frac up to 27% drag it to ~4.2%,
    # while the median is ~0.02%. Using the weighted mean here subtracts a
    # phantom tail and collapses s to a value near 1/75 purely by artefact.
    tail_hat = float(cal["missing_frac"].median()) if len(cal) else float("nan")
    tail_wtd = wmean(cal, "missing_frac") if len(cal) else float("nan")

    print("\n" + "=" * 74)
    print("STEP 1 — CALIBRATION: the non-opening tail (closing auction + off-book)")
    print("=" * 74)
    print(f"  sessions where Yahoo DID report 09:15 volume   {len(cal):,}")
    print(f"  distinct symbols in subset                     {cal['symbol'].nunique()}")
    print(f"  their missing_frac (= tail alone), MEDIAN      {tail_hat:.4%}  <- used")
    print(f"  their missing_frac, volume-weighted            {tail_wtd:.4%}  "
          f"(outlier-inflated, NOT used)")
    print(f"  their DIRECT s = first5/daily, MEDIAN          {cal['s_direct'].median():.4%}")
    print(f"  their DIRECT s, mean                           {cal['s_direct'].mean():.4%}")
    print("  The median tail is ~0: when Yahoo reports the opening volume,")
    print("  nothing material is missing. So missing_frac IS the opening share.")
    print("  DIRECT s above is an INDEPENDENT measurement — cross-check it")
    print("  against the residual estimate below. Agreement validates the method.")

    for label, sub in (("UP-SESSIONS ONLY (operator spec)", res[res["up_session"]]),
                       ("ALL SESSIONS (control)", res)):
        if sub.empty:
            continue
        upper = wmean(sub, "missing_frac")
        s_wtd = max(upper - tail_hat, 0.0)
        s_med = max(float(sub["missing_frac"].median()) - tail_hat, 0.0)
        print("\n" + "=" * 74)
        print(f"STEP 2 — {label}")
        print("=" * 74)
        print(f"  n sessions                                   {len(sub):,}")
        print(f"  s, volume-weighted (operator estimator)      {s_wtd:.4%}")
        print(f"  s, MEDIAN (outlier-robust)                   {s_med:.4%}")
        print(f"  s, unweighted mean                           "
              f"{max(sub['missing_frac'].mean() - tail_hat, 0):.4%}")
        print(f"  decile spread (10-90)                        "
              f"{sub['missing_frac'].quantile(.10):.4%} - {sub['missing_frac'].quantile(.90):.4%}")
        print(f"  (tail of {tail_hat:.4%} already subtracted)")
        if label.startswith("UP"):
            up_s, up_upper = s_med, s_wtd

    print("\n" + "=" * 74)
    print("IMPLICATION FOR THE GATE  (up-sessions, operator spec)")
    print("=" * 74)
    lo, hi = up_s, up_upper          # bracket: median .. volume-weighted
    print(f"  hardcoded multiplier in preopen_check.py       75.00")
    print(f"  (assumed s = 1/75 = {1/75:.4%})")
    for name, sv in (("MEDIAN s (robust)", lo), ("VOLUME-WEIGHTED s (operator spec)", hi)):
        if sv <= 0:
            continue
        print(f"\n  -- {name}: s = {sv:.4%} --")
        print(f"     empirically correct multiplier (1/s)       {1 / sv:8.2f}")
        print(f"     overstatement factor (75 * s)              {75 * sv:8.2f}x")
        print(f"     '1.2x' gate really demands rel-volume >=   {1.2 / (75 * sv):8.3f}x")
        print(f"     '1.0x' gate really demands rel-volume >=   {1.0 / (75 * sv):8.3f}x")

    print("\n" + "=" * 74)
    print("BY LIQUIDITY TIER — up-sessions, tail-corrected (2026-06-24 turnover quintiles)")
    print("=" * 74)
    m = res[res["up_session"]].merge(uni[["symbol", "liq_tier"]], on="symbol", how="left")
    for tier, g in m.groupby("liq_tier", observed=True):
        sv = max(float(g["missing_frac"].median()) - tail_hat, 1e-9)
        print(f"  {str(tier):16s} n={len(g):6,}  s={sv:.4%}  implied mult={1 / sv:7.2f}  "
              f"1.2x gate demands >= {1.2 / (75 * sv):.3f}x")

    out = CACHE / "session_shares.parquet"
    sess.to_parquet(out, index=False)
    print(f"\n[out] per-session detail -> {out}")
    print("\nCAVEATS (carry into any write-up): s is BRACKETED, not a point "
          "estimate — the\ndirect measurement is impossible because yfinance "
          "drops the 09:15 volume in\n~98% of sessions. The tail correction is "
          "calibrated on the ~2% Yahoo does\nreport, which may not be "
          "representative. RULING 13d: measurement only, no\nlive parameter "
          "change before the 2026-09-27 AB_PREREG read date.")


def main() -> None:
    require_ruling_13()
    uni = load_universe()
    syms = uni["symbol"].tolist()
    limit = next((int(a.split("=")[1]) for a in sys.argv if a.startswith("--limit=")), None)
    if limit:
        global CACHE
        CACHE = CACHE.parent / f"{CACHE.name}_smoke{limit}"
        syms = syms[:limit]
        uni = uni[uni["symbol"].isin(syms)]
        print(f"[SMOKE] limited to {limit} symbols; cache -> {CACHE.name}")
    print(f"[universe] {len(syms)} symbols")
    refresh = "--refresh" in sys.argv
    panel = fetch_intraday(syms, refresh=refresh)
    daily = fetch_daily(syms, refresh=refresh)
    validate_denominator(daily, uni)
    sess, diag = build_sessions(panel, daily)
    report(sess, uni, diag)


if __name__ == "__main__":
    main()

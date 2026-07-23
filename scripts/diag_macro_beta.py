#!/usr/bin/env python3
"""DIAG-MACROBETA-0001 — cross-sectional macro-factor beta structure.

OUTCOME-BLIND DIAGNOSTIC. Betas, t-stats and their cross-sectional distribution
ONLY. NO portfolio construction, NO strategy/spread return, NO cumulative
performance, NO Sharpe/IR, NO forward-return-conditional statistic, NO
outcome-conditional subsetting. CONTAMINATION_POLICY AMENDMENT A lists
"correlation and cointegration structure" as explicitly free — this spends NO
trial. FINAL_TEST is never set; all stock data passes the research door.

Pre-registration: governance/research_register_v2.csv row DIAG-MACROBETA-0001.
A-priori sign map: governance/prereg/DIAG-MACROBETA-0001_sign_map.csv
(sha256 16693972a15f72379049a84b76c508b8488740abe89f6120514f9ed3ddd49859).

Idempotent, checkpointed stages (the environment is unstable — resume from cache):
  --stage factors   fetch + cache BZ=F, CL=F, INR=X, USDINR=X  → factors_raw.parquet
  --stage panel     build the gated, quorum-filtered stock log-return matrix
                    aligned to NSE sessions + factor log-returns → returns_aligned.parquet
  --stage regress   per-symbol joint regressions (SPEC-C/L1/L2), NW HAC + Huber,
                    written incrementally → betas.parquet
  --stage score     FDR, sign test, sub-period stability, shock robustness,
                    theory scorecard → summary.json (+ analysis write-up inputs)
  --stage all       run every stage, skipping any whose output already exists
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
from src import data_gate  # noqa: E402

OUT = REPO / "data" / "derived" / "macro_beta_diag"
PANEL = REPO / "data" / "workspace" / "price_panel_52wh.parquet"
TRI = REPO / "data" / "reference" / "tri" / "raw" / "nifty500_tri.csv"
MAP = REPO / "governance" / "prereg" / "DIAG-MACROBETA-0001_sign_map.csv"
MAP_SHA = "16693972a15f72379049a84b76c508b8488740abe89f6120514f9ed3ddd49859"

FACTORS_RAW = OUT / "factors_raw.parquet"
RETURNS = OUT / "returns_aligned.parquet"
FACTOR_RET = OUT / "factor_returns.parquet"
BETAS = OUT / "betas.parquet"
SUMMARY = OUT / "summary.json"

# Pre-registered parameters (FIXED — TRAP 3, do not revise post-contact)
DEV_START = pd.Timestamp("2015-01-01")
SEAL = data_gate.SEAL_CUTOFF  # 2024-07-17
MIN_OBS = 750
EXPECT_SESSIONS = (2300, 2380)
SUBPERIODS = {
    "P1": ("2015-01-01", "2017-12-31"),
    "P2": ("2018-01-01", "2019-12-31"),
    "P3": ("2020-01-01", "2021-12-31"),
    "P4": ("2022-01-01", "2024-07-16"),
}
MIN_SUB_OBS = 120
SHOCKS = {
    "COVID": ("2020-02-01", "2020-06-30"),
    "UKRAINE": ("2022-02-01", "2022-06-30"),
}
NW_LAG = 5
HUBER_C = 1.345
FDR_Q = 0.10
YF_TICKERS = ["BZ=F", "CL=F", "INR=X", "USDINR=X"]


# ---------------------------------------------------------------- stage: factors
def stage_factors() -> None:
    if FACTORS_RAW.exists():
        print(f"[factors] cache exists → {FACTORS_RAW} (skip)")
        return
    import time

    import yfinance as yf

    OUT.mkdir(parents=True, exist_ok=True)
    frames = []
    for t in YF_TICKERS:
        raw = yf.Ticker(t).history(
            start="2014-12-01",
            end=str(SEAL.date()),  # never pull sealed rows
            auto_adjust=False,
        )
        if raw.empty:
            sys.exit(f"[factors] EMPTY fetch for {t} — refuse to proceed")
        s = raw[["Close"]].copy()
        s.index = pd.to_datetime(s.index).tz_localize(None).normalize()
        s = s[~s.index.duplicated(keep="last")]
        s.columns = [t]
        frames.append(s)
        print(f"[factors] {t}: {len(s)} rows {s.index.min().date()}→{s.index.max().date()}")
        time.sleep(0.3)
    fac = pd.concat(frames, axis=1).sort_index()
    # never let a sealed-range factor row survive
    fac = fac.loc[fac.index < SEAL]
    fac.to_parquet(FACTORS_RAW)
    print(f"[factors] wrote {fac.shape} → {FACTORS_RAW}")
    print(fac.tail(3))


# ------------------------------------------------------------------ stage: panel
def _drop_non_trading_dates(panel: pd.DataFrame, quorum: float = 0.10):
    counts = panel.groupby("date")["symbol"].size()
    threshold = counts.median() * quorum
    bad = counts.index[counts < threshold]
    return panel.loc[~panel["date"].isin(set(bad))].copy(), pd.DatetimeIndex(bad)


def stage_panel() -> None:
    if RETURNS.exists() and FACTOR_RET.exists():
        print(f"[panel] caches exist → {RETURNS}, {FACTOR_RET} (skip)")
        return
    if not FACTORS_RAW.exists():
        sys.exit("[panel] factors_raw.parquet missing — run --stage factors first")

    # --- stock panel through the research door (gate strips >= seal cutoff) ---
    raw = pd.read_parquet(PANEL, columns=["date", "symbol", "close"])
    panel = data_gate.load(raw, "date")
    assert panel["date"].max() < SEAL, "gate failed: post-cutoff stock rows present"
    panel = panel.loc[panel["date"] >= DEV_START]

    # TRAP 1 quorum filter — a handful of holiday-placeholder dates NaN-poison
    # the wide pivot. Assert the surviving NSE session count is in the expected
    # band and FAIL LOUDLY otherwise (TRAP 6: coverage, not row count).
    panel, dropped = _drop_non_trading_dates(panel)
    sessions = sorted(panel["date"].unique())
    n_sess = len(sessions)
    print(f"[panel] dropped {len(dropped)} non-session dates; {n_sess} NSE sessions remain")
    if not (EXPECT_SESSIONS[0] <= n_sess <= EXPECT_SESSIONS[1]):
        sys.exit(f"[panel] FAIL: {n_sess} sessions outside pre-registered {EXPECT_SESSIONS}")

    sess_idx = pd.DatetimeIndex(sessions)

    # --- factor levels → NSE session calendar by EXACT DATE MATCH (no ffill) ---
    fac = pd.read_parquet(FACTORS_RAW)
    # Co-moving-series guards (src/factor_guards.py, added 2026-07-23 after the
    # corrupted Brent/WTI bars caught in DIAG-MACROBETA-0001-FWDLOOK — a ~14%
    # same-day decoupling that only an eyeball caught. Now structural.)
    from src.factor_guards import (
        FactorGuardError,
        assert_comoving_divergence,
        assert_return_agreement,
    )
    try:
        # same quantity, two sources: must agree (pre-registered corr>0.99 halt)
        fx_corr = assert_return_agreement(
            fac["INR=X"], fac["USDINR=X"], "INR=X", "USDINR=X", min_corr=0.99
        )
        print(f"[panel] corr(INR=X, USDINR=X) log-returns = {fx_corr:.5f}")
        # distinct but near-cointegrated grades: same-day divergence cap.
        # Hard cap is TAIL-SCOPED (last 5 bars = the unsettled-fresh-pull
        # zone): the dev window contains REAL >5% Brent/WTI decoupling on 30
        # days, peaking 0.2672 on 2020-04-22 (WTI negative-price episode) —
        # a full-history cap would reject valid data. Full series reported.
        div = assert_comoving_divergence(
            fac["BZ=F"], fac["CL=F"], "BZ=F", "CL=F",
            max_abs_divergence=0.05, tail_bars=5,
        )
        n_hist = int((div > 0.05).sum())
        print(
            f"[panel] Brent/WTI divergence: full-series max {div.max():.4f}, "
            f"{n_hist} day(s) > 5% (known-real incl. Apr-2020); tail-5 clean"
        )
    except FactorGuardError as e:
        sys.exit(f"[panel] FAIL: {e}")

    fac_on_sess = fac.reindex(sess_idx)  # exact match; missing → NaN
    # factor overlap assertion (>=90% of NSE sessions carry each factor level)
    for col in YF_TICKERS:
        ov = fac_on_sess[col].notna().mean()
        print(f"[panel] factor {col} overlap on NSE sessions = {ov:.4f}")
        if ov < 0.90:
            sys.exit(f"[panel] FAIL: {col} overlap {ov:.4f} < 0.90")

    # --- TRI market factor ---
    tri = pd.read_csv(TRI, parse_dates=["date"])
    tri = data_gate.load(tri, "date")
    tri = tri.set_index("date")["tri_close"].reindex(sess_idx)
    tri_ov = tri.notna().mean()
    print(f"[panel] NIFTY500 TRI overlap on NSE sessions = {tri_ov:.4f}")
    if tri_ov < 0.90:
        sys.exit(f"[panel] FAIL: TRI overlap {tri_ov:.4f} < 0.90")

    # --- log returns on the session grid ---
    # factor log returns (INR-crude derived = brent + usdinr)
    fr = pd.DataFrame(index=sess_idx)
    fr["r_mkt"] = np.log(tri).diff()
    fr["r_brent"] = np.log(fac_on_sess["BZ=F"]).diff()
    fr["r_wti"] = np.log(fac_on_sess["CL=F"]).diff()
    fr["r_usdinr"] = np.log(fac_on_sess["INR=X"]).diff()
    fr["r_usdinr_x"] = np.log(fac_on_sess["USDINR=X"]).diff()
    fr["r_inrbrent"] = fr["r_brent"] + fr["r_usdinr"]
    fr.index.name = "date"
    fr.to_parquet(FACTOR_RET)
    print(f"[panel] wrote factor returns {fr.shape} → {FACTOR_RET}")

    # stock log returns (long form, gate-clean). Sort for correct diff per symbol.
    panel = panel.sort_values(["symbol", "date"])
    panel["r"] = panel.groupby("symbol", sort=False)["close"].transform(
        lambda c: np.log(c).diff()
    )
    stock = panel.dropna(subset=["r"])[["date", "symbol", "r"]]
    stock.to_parquet(RETURNS)
    print(f"[panel] wrote stock returns {stock.shape}, "
          f"{stock['symbol'].nunique()} symbols → {RETURNS}")


# ---------------------------------------------------------------- stage: regress
def _nw_se(X: np.ndarray, resid: np.ndarray, lag: int) -> np.ndarray:
    """Newey-West HAC covariance → sqrt(diag). Bartlett kernel."""
    n, k = X.shape
    XtX_inv = np.linalg.inv(X.T @ X)
    u = X * resid[:, None]
    S = u.T @ u
    for L in range(1, lag + 1):
        w = 1.0 - L / (lag + 1.0)
        G = u[L:].T @ u[:-L]
        S += w * (G + G.T)
    cov = XtX_inv @ S @ XtX_inv
    d = np.diag(cov)
    d = np.where(d < 0, np.nan, d)
    return np.sqrt(d)


def _huber_beta(X: np.ndarray, y: np.ndarray, c: float = HUBER_C, iters: int = 50):
    """Huber M-estimate via IRLS. Returns coefficient vector (sign check only)."""
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    for _ in range(iters):
        r = y - X @ beta
        s = np.median(np.abs(r - np.median(r))) * 1.4826
        if s < 1e-12:
            break
        z = r / s
        w = np.where(np.abs(z) <= c, 1.0, c / np.abs(z))
        WX = X * w[:, None]
        try:
            beta_new = np.linalg.solve(X.T @ WX, X.T @ (w * y))
        except np.linalg.LinAlgError:
            break
        if np.max(np.abs(beta_new - beta)) < 1e-8:
            beta = beta_new
            break
        beta = beta_new
    return beta


SPECS = {
    # name: (market lag, oil lag, fx lag)  — lag applied to the FACTOR (shift +L)
    "C": (0, 0, 0),
    "L1": (0, 1, 1),
    "L2": (1, 1, 1),
}


def _design(fr: pd.DataFrame, spec: str) -> pd.DataFrame:
    lm, lo, lf = SPECS[spec]
    d = pd.DataFrame(index=fr.index)
    d["r_mkt"] = fr["r_mkt"].shift(lm)
    d["r_brent"] = fr["r_brent"].shift(lo)
    d["r_usdinr"] = fr["r_usdinr"].shift(lf)
    return d


def _fit_one(y: pd.Series, D: pd.DataFrame) -> dict | None:
    df = pd.concat([y.rename("y"), D], axis=1).dropna()
    if len(df) < MIN_OBS:
        return None
    yv = df["y"].to_numpy()
    Xcols = ["r_mkt", "r_brent", "r_usdinr"]
    X = np.column_stack([np.ones(len(df)), df[Xcols].to_numpy()])
    beta, *_ = np.linalg.lstsq(X, yv, rcond=None)
    resid = yv - X @ beta
    se = _nw_se(X, resid, NW_LAG)
    hub = _huber_beta(X, yv)
    names = ["alpha", "b_mkt", "b_oil", "b_fx"]
    out = {"nobs": len(df)}
    for i, nm in enumerate(names):
        out[nm] = beta[i]
        out[f"{nm}_se"] = se[i]
        out[f"{nm}_t"] = beta[i] / se[i] if se[i] and np.isfinite(se[i]) else np.nan
    out["b_oil_huber"] = hub[2]
    out["b_fx_huber"] = hub[3]
    return out


def stage_regress() -> None:
    if BETAS.exists():
        print(f"[regress] cache exists → {BETAS} (skip)")
        return
    if not (RETURNS.exists() and FACTOR_RET.exists()):
        sys.exit("[regress] returns caches missing — run --stage panel first")

    stock = pd.read_parquet(RETURNS)
    fr = pd.read_parquet(FACTOR_RET)
    designs = {sp: _design(fr, sp) for sp in SPECS}

    wide = stock.pivot(index="date", columns="symbol", values="r")
    symbols = list(wide.columns)
    print(f"[regress] {len(symbols)} symbols to fit across specs {list(SPECS)}")

    tmp = BETAS.with_suffix(".partial.parquet")
    rows = []
    for i, sym in enumerate(symbols, 1):
        y = wide[sym].dropna()
        if len(y) < MIN_OBS:
            continue
        rec = {"symbol": sym, "nobs_raw": len(y)}
        keep = False
        for sp in SPECS:
            r = _fit_one(y, designs[sp])
            if r is None:
                continue
            keep = True
            for k, v in r.items():
                rec[f"{sp}_{k}"] = v
        if keep:
            rows.append(rec)
        if i % 200 == 0:
            pd.DataFrame(rows).to_parquet(tmp)  # checkpoint
            print(f"[regress] {i}/{len(symbols)} fitted, {len(rows)} kept (checkpoint)")

    betas = pd.DataFrame(rows)
    betas.to_parquet(BETAS)
    if tmp.exists():
        tmp.unlink()
    print(f"[regress] wrote {betas.shape} → {BETAS}")


# ------------------------------------------------------------------ stage: score
def _bh(pvals: np.ndarray, q: float) -> np.ndarray:
    """Benjamini-Hochberg. Returns boolean reject mask aligned to input order."""
    p = np.asarray(pvals, float)
    ok = np.isfinite(p)
    idx = np.where(ok)[0]
    m = len(idx)
    rej = np.zeros(len(p), bool)
    if m == 0:
        return rej
    order = idx[np.argsort(p[idx])]
    thresh = q * (np.arange(1, m + 1)) / m
    passed = p[order] <= thresh
    if passed.any():
        kmax = np.max(np.where(passed)[0])
        rej[order[: kmax + 1]] = True
    return rej


def _norm_sf(t):
    # two-sided p from |t| using a normal approx (NW t is asymptotically normal)
    from math import erfc, sqrt
    return np.array([erfc(abs(x) / sqrt(2)) if np.isfinite(x) else np.nan for x in t])


def _subperiod_signs(stock, fr):
    """Per-symbol SPEC-C beta signs within each sub-period (>=MIN_SUB_OBS)."""
    wide = stock.pivot(index="date", columns="symbol", values="r")
    D = _design(fr, "C")
    out = {}
    for name, (a, b) in SUBPERIODS.items():
        m = (wide.index >= a) & (wide.index <= b)
        dm = (D.index >= a) & (D.index <= b)
        Dw = D.loc[dm]
        sub = wide.loc[m]
        res = {}
        for sym in wide.columns:
            df = pd.concat([sub[sym].rename("y"), Dw], axis=1).dropna()
            if len(df) < MIN_SUB_OBS:
                continue
            X = np.column_stack([np.ones(len(df)), df[["r_mkt", "r_brent", "r_usdinr"]].to_numpy()])
            beta, *_ = np.linalg.lstsq(X, df["y"].to_numpy(), rcond=None)
            res[sym] = (np.sign(beta[2]), np.sign(beta[3]))  # (oil, fx)
        out[name] = res
    return out


def _shock_betas(stock, fr):
    """SPEC-C oil/fx betas dropping each shock window (and both)."""
    wide = stock.pivot(index="date", columns="symbol", values="r")
    D = _design(fr, "C")
    masks = {"EX-COVID": ["COVID"], "EX-UKRAINE": ["UKRAINE"], "EX-BOTH": ["COVID", "UKRAINE"]}
    out = {}
    for label, shocks in masks.items():
        res = {}
        for sym in wide.columns:
            df = pd.concat([wide[sym].rename("y"), D], axis=1).dropna()
            keep = pd.Series(True, index=df.index)
            for sh in shocks:
                a, b = SHOCKS[sh]
                keep &= ~((df.index >= a) & (df.index <= b))
            df = df[keep]
            if len(df) < MIN_OBS:
                continue
            X = np.column_stack([np.ones(len(df)), df[["r_mkt", "r_brent", "r_usdinr"]].to_numpy()])
            beta, *_ = np.linalg.lstsq(X, df["y"].to_numpy(), rcond=None)
            res[sym] = (beta[2], beta[3])
        out[label] = res
    return out


def stage_score() -> None:
    import hashlib
    assert hashlib.sha256(MAP.read_bytes()).hexdigest() == MAP_SHA, "sign map hash mismatch"
    betas = pd.read_parquet(BETAS).set_index("symbol")
    amap = pd.read_csv(MAP).set_index("symbol")
    stock = pd.read_parquet(RETURNS)
    fr = pd.read_parquet(FACTOR_RET)

    result = {"n_symbols_fit": int(len(betas))}

    # factor correlation matrix (entanglement)
    fc = fr[["r_mkt", "r_brent", "r_wti", "r_usdinr", "r_inrbrent"]].dropna()
    result["factor_corr"] = fc.corr().round(4).to_dict()
    result["n_factor_obs"] = int(len(fc))

    # FDR per factor per spec + full t distribution moments vs N(0,1)
    disc = {}
    tdist = {}
    for sp in SPECS:
        for fac, col in [("oil", f"{sp}_b_oil_t"), ("fx", f"{sp}_b_fx_t")]:
            if col not in betas:
                continue
            t = betas[col].to_numpy()
            p = _norm_sf(t)
            rej = _bh(p, FDR_Q)
            n = int(np.isfinite(t).sum())
            key = f"{sp}_{fac}"
            disc[key] = {
                "n_tested": n,
                "n_reject_bh_q10": int(rej.sum()),
                "n_p_lt_05": int(np.nansum(p < 0.05)),
                "expected_fp_at_05": round(0.05 * n, 1),
                "t_mean": round(float(np.nanmean(t)), 4),
                "t_std": round(float(np.nanstd(t)), 4),
                "t_absgt196_frac": round(float(np.nanmean(np.abs(t) > 1.96)), 4),
            }
            betas[f"{key}_bh_reject"] = rej
    result["discoveries"] = disc

    # theory scorecard on SPEC-C, primary
    def score(fac, sign_col, beta_col, t_col, huber_col, reject_col):
        pred = amap[sign_col]
        directional = pred[pred.isin(["POS", "NEG"])]
        rows = []
        for sym, ps in directional.items():
            if sym not in betas.index:
                rows.append({"symbol": sym, "pred": ps, "in_fit": False})
                continue
            b = betas.at[sym, beta_col]
            t = betas.at[sym, t_col]
            hub = betas.at[sym, huber_col]
            rej = bool(betas.at[sym, reject_col]) if reject_col in betas else False
            emp = "POS" if b > 0 else "NEG"
            rows.append({
                "symbol": sym, "pred": ps, "beta": float(b), "t": float(t),
                "emp_sign": emp, "match": emp == ps, "bh_reject": rej,
                "huber_sign": "POS" if hub > 0 else "NEG",
                "ols_huber_agree": (b > 0) == (hub > 0),
                "sector": amap.at[sym, "sector"],
            })
        return pd.DataFrame(rows)

    from math import comb
    scored = {}
    for fac, scol in [("oil", "crude_sign"), ("fx", "fx_sign")]:
        sc = score(fac, scol, f"C_b_{fac}", f"C_b_{fac}_t", f"C_b_{fac}_huber", f"C_{fac}_bh_reject")
        fitted = sc.dropna(subset=["match"]) if "match" in sc else sc.iloc[0:0]
        n = len(fitted)
        k = int(fitted["match"].sum())
        # one-sided binomial sign test vs p=0.5 across ALL directional fitted names
        pval = sum(comb(n, j) for j in range(k, n + 1)) / (2 ** n) if n else np.nan
        surv = fitted[fitted["bh_reject"]]
        scored[fac] = {
            "n_directional_map": int((amap[scol].isin(["POS", "NEG"])).sum()),
            "n_fitted": int(n),
            "n_sign_match": int(k),
            "sign_match_frac": round(k / n, 4) if n else None,
            "sign_test_p_one_sided": float(pval),
            "n_map_bh_survivors": int(len(surv)),
            "n_survivors_match": int(surv["match"].sum()) if len(surv) else 0,
            "hit_rate_among_survivors": round(surv["match"].mean(), 4) if len(surv) else None,
        }
        sc.to_csv(OUT / f"scorecard_{fac}.csv", index=False)
    result["theory_scorecard"] = scored

    # surprises: BH survivors NOT in the directional map, top decile |t|
    surprises = {}
    for fac in ["oil", "fx"]:
        col_t = f"C_b_{fac}_t"
        rej_col = f"C_{fac}_bh_reject"
        dirmap = set(amap.index[amap[{"oil": "crude_sign", "fx": "fx_sign"}[fac]].isin(["POS", "NEG"])])
        s = betas[betas.get(rej_col, False) == True].copy()
        s = s[~s.index.isin(dirmap)]
        thr = betas[col_t].abs().quantile(0.90)
        s = s[s[col_t].abs() >= thr].sort_values(col_t, key=lambda x: x.abs(), ascending=False)
        surprises[fac] = [
            {"symbol": sym, "t": round(float(s.at[sym, col_t]), 2),
             "beta": round(float(s.at[sym, f"C_b_{fac}"]), 3),
             "in_map_ambiguous": sym in set(amap.index)}
            for sym in s.index[:30]
        ]
    result["surprises"] = surprises

    # misses: directional map names that fail BH
    misses = {}
    for fac, scol in [("oil", "crude_sign"), ("fx", "fx_sign")]:
        rej_col = f"C_{fac}_bh_reject"
        dm = amap.index[amap[scol].isin(["POS", "NEG"])]
        present = [s for s in dm if s in betas.index]
        miss = [s for s in present if not bool(betas.at[s, rej_col]) if rej_col in betas]
        misses[fac] = {"n": len(miss), "symbols": miss}
    result["misses"] = misses

    # sub-period sign stability + OLS/Huber agreement → STABLE set
    subsigns = _subperiod_signs(stock, fr)
    stable = {"oil": [], "fx": []}
    for fac, idx in [("oil", 0), ("fx", 1)]:
        rej_col = f"C_{fac}_bh_reject"
        for sym in betas.index:
            if rej_col in betas and not bool(betas.at[sym, rej_col]):
                continue
            signs = []
            for name in SUBPERIODS:
                if sym in subsigns[name]:
                    signs.append(subsigns[name][sym][idx])
            if len(signs) < len(SUBPERIODS):
                continue
            if len(set(signs)) != 1:
                continue
            b = betas.at[sym, f"C_b_{fac}"]
            hub = betas.at[sym, f"C_b_{fac}_huber"]
            if (b > 0) != (hub > 0):
                continue
            stable[fac].append({
                "symbol": sym, "beta": round(float(b), 4),
                "t": round(float(betas.at[sym, f"C_b_{fac}_t"]), 2),
                "sign": "POS" if b > 0 else "NEG",
                "in_map": sym in set(amap.index),
                "map_pred": amap.at[sym, {"oil": "crude_sign", "fx": "fx_sign"}[fac]] if sym in amap.index else None,
            })
    result["stable"] = {k: {"n": len(v), "names": v} for k, v in stable.items()}

    # shock robustness: max |Δbeta| vs SPEC-C base for map survivors
    shock = _shock_betas(stock, fr)
    result["shock_note"] = "per-symbol EX-shock betas cached in shock_betas.json"
    (OUT / "shock_betas.json").write_text(json.dumps(
        {lab: {s: [round(v[0], 5), round(v[1], 5)] for s, v in d.items()} for lab, d in shock.items()}))

    # contemporaneous vs lagged gap (cross-sectional corr of beta vectors)
    gap = {}
    for fac in ["oil", "fx"]:
        for a, b in [("C", "L1"), ("C", "L2")]:
            ca, cb = f"{a}_b_{fac}", f"{b}_b_{fac}"
            if ca in betas and cb in betas:
                d = betas[[ca, cb]].dropna()
                gap[f"{fac}_{a}_vs_{b}_beta_corr"] = round(float(d[ca].corr(d[cb])), 4)
    result["contemp_vs_lagged_beta_corr"] = gap

    betas.reset_index().to_parquet(BETAS)  # persist bh_reject columns
    SUMMARY.write_text(json.dumps(result, indent=2, default=str))
    print(f"[score] wrote → {SUMMARY}")
    print(json.dumps({k: result[k] for k in ["discoveries", "theory_scorecard", "misses"]}, indent=2, default=str))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--trial-id", default="DIAG-MACROBETA-0001")
    ap.add_argument("--stage", choices=["factors", "panel", "regress", "score", "all"], default="all")
    args = ap.parse_args()
    assert args.trial_id == "DIAG-MACROBETA-0001"
    stages = ["factors", "panel", "regress", "score"] if args.stage == "all" else [args.stage]
    for st in stages:
        print(f"=== stage: {st} ===")
        globals()[f"stage_{st}"]()


if __name__ == "__main__":
    main()

# DIAG-MACROBETA-0001-FWDLOOK — Tier-1 forward monitoring glance

**A 3-session forward look (close 2026-07-20 → close 2026-07-23) at the 250-name
legacy universe, juxtaposed against the DIAG-MACROBETA-0001 dev-window crude
betas. Qualitative reconciliation only. Confirms NOTHING about the beta.**

- **Register:** `governance/research_register_v2.csv` row
  `DIAG-MACROBETA-0001-FWDLOOK` (appended 2026-07-23).
- **Governance:** TIER-1 LOOK-DON'T-TUNE (RULING 2), **NOT** a sealed-test trial.
  Consumes NO shadow slot, burns NO family's sealed test, `FINAL_TEST` not set.
  **Cumulative DSR/SPA trial count UNCHANGED at 53** (see §5). Forward data only
  (post-2026-06-29 live window), NOT the sealed holdout (cutoff 2024-07-17).
- **Data (BINDING RULE 3 compliant):** yfinance auto-adjusted public data; no
  Kite, no broker call, no scraping. Universe = the 250 names in the sanctioned
  sealed backup `data/sealed/raw/2026-07-23/prices_eod_backup_20260624.csv`
  (250 rows), **not** production `config.py`.
- **Hard boundary held:** no portfolio, no strategy/spread/basket return, no
  cumulative performance, no Sharpe/IR/hit-rate, no forward-return-conditional
  *statistic*; no names selected, tuned, weighted or ranked.

---

## 1. The look

- Of the 250-name universe, **66 rose** over the 3 sessions
  (close 2026-07-20 → close 2026-07-23); 184 fell/flat.
- The 66 gainers intersected with the crude-directional names from
  `DIAG-MACROBETA-0001`:
  - a-priori sign map = **52 crude-directional** names
    (`governance/prereg/DIAG-MACROBETA-0001_sign_map.csv`);
  - empirical FDR survivors = **18** (`C_oil_bh_reject` / `L1_oil_bh_reject` in
    `data/derived/macro_beta_diag/betas.parquet`);
  - union pool = **61**.
- **16 crude names** were among the 66 gainers.

## 2. Macro backdrop (the reliable read)

Brent (BZ=F), WTI (CL=F), USD/INR (INR=X) over the same window:

- **Crude rose ~+11.7%** 2026-07-16 → 2026-07-22 (Brent 84.23 → 94.07, WTI
  corroborating).
- **USD/INR essentially flat** (~+0.3%).

## 3. Data-quality catch (part of the diagnostic's value — TRAP 6 / TRAP 8)

The **2026-07-23 crude bars are corrupted and were discarded**, not used:

| Grade | 2026-07-22 → 2026-07-23 | printed move |
|---|---|---|
| Brent (BZ=F) | 94.07 → 87.10 | **−7.4%** |
| WTI (CL=F)   | 86.83 → 92.43 | **+6.4%** |

That is a **~14% same-day decoupling** of two grades whose daily log returns
co-move at ~0.89 (DIAG-MACROBETA-0001 §3) — physically impossible, almost
certainly an unsettled / partial-session yfinance artifact (the TRAP 6 shape: a
healthy-looking bar that is really a partial session). **The reliable crude read
therefore stops at 2026-07-22.**

## 4. Reconciliation — WEAK, SPLIT, PARTIAL (qualitative only)

- **Consistent with crude-up:** E&P / crude-POSITIVE names rose — ONGC +1.1%,
  OIL +1.2%, VEDL +1.1%. Crude-NEGATIVE demand/margin names fell — OMCs
  HINDPETRO −5.0% / BPCL −2.4% / IOC −1.7%; aviation INDIGO −3.9%.
- **Inconsistent:** the FDR-significant crude-NEGATIVE input-cost names rose
  slightly — PIDILITIND +0.6%, BERGEPAINT +0.6%, DALBHARAT +0.4%. The very names
  that carried the dev-window crude signal did **not** track it over these 3 days.
- **Irrelevant:** the headline movers (autos +7–9%: M&MFIN, TVSMOTOR,
  BAJAJ-AUTO) have **statistically insignificant** crude betas — their moves say
  nothing about crude.

**Interpretive discipline:** 3 sessions against a beta estimated on **2,353**
sessions confirms nothing about the beta and is fully consistent with **chance
alignment**. This look does not re-test, revalidate, refute or update
`DIAG-MACROBETA-0001`.

## 5. AMENDMENT-A adjudication (argued both ways)

**FOR "it is a look, not a sealed-test trial":** it is Tier-1 forward data
(post-2026-06-29), not the sealed holdout (cutoff 2024-07-17); no
strategy/spread/portfolio return, Sharpe, IR or hit-rate was computed; no names
were selected or tuned; no family's single sealed test and no shadow slot were
touched; RULING 2 explicitly permits look-don't-tune on Tier-1 forward data.

**AGAINST (it edges toward a conditional observation):** it did observe forward
returns of signal-classified (crude-beta) names and asked whether they lined up
— the exact shape AMENDMENT A names ("conditional return plots … 'sanity check'
performance summaries … regardless of formality").

**Determination:** recorded as a **Tier-1 look-don't-tune diagnostic** that
consumes NO shadow slot and burns NO family's sealed test. On the shape-match it
lands on the **look** side: AMENDMENT A and the DSR/SPA cumulative-trial count
exist to charge the **dev/holdout multiple-testing budget** (RULING 7 —
best-of-N selection over dev/sealed data); a forward monitoring glance with no
performance statistic and no selection does not draw on that budget.
**Cumulative DSR/SPA trial count UNCHANGED at 53.**

**Honest residual (not a false all-clear):** the one point on which an operator
could take a more conservative view is whether AMENDMENT A's "regardless of
formality" should reach a no-statistic forward glance. If so, the conservative
treatment is to charge **one** marginal trial (→ 54), which per TRIAL ECONOMICS
is cheap (moves the deflation bar ~0.3%) and changes nothing in this result.
Flagged for operator override; nothing here is gated on it.

## 6. Firewall (binding)

**This observation must NOT feed the design, selection or tuning of any research
family.** If it ever does, it becomes contamination and a registered trial. A
green 3-day alignment is not evidence for or against any strategy and grants no
re-test of `DIAG-MACROBETA-0001` or any spec family.

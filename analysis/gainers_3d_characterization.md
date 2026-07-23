# DIAG-GAINERS3D-0001 — 3-day gainer cross-section (2026-07-20 → 2026-07-23)

**Question (operator):** of the 66 stocks (of the 250-name universe) that ROSE
over the last 3 trading sessions (close 07-20 → close 07-23), what common
patterns or trigger reasons do they share?

---

## 0. GOVERNANCE FIREWALL — READ FIRST (defines the whole exercise)

- **This is a Tier-1 MONITORING / look-don't-tune diagnostic (RULING 2). It is
  MONITORING ONLY.** Its output MUST NOT feed the design, selection, or tuning
  of any research family, spec, or signal. The moment it does, it becomes
  outcome-conditional contamination and a registered TRIAL. **No signal is
  built or proposed here. No name is selected or tuned.**
- **Selecting stocks BY their forward return and hunting for common causes is
  conditioning on the outcome** — the textbook data-snooping pattern
  `CONTAMINATION_POLICY` AMENDMENT A exists to stop ("if in doubt, it is a
  trial"). The exercise is kept legitimate ONLY by the **mandatory base-rate
  control**: every candidate pattern is reported as its rate in the 66 UP names
  **vs** the 184 DOWN/flat names. A feature equally common in losers explains
  nothing and is discarded. This converts winner-fishing into a defensible
  up-vs-down cross-sectional description (the "correlation structure" bucket
  AMENDMENT A lists as free).
- **No trial spent; no shadow slot; not a spec family.** Descriptive cross-tab
  only — no strategy return, Sharpe, IR, hit-rate, or forward-return-conditional
  statistic beyond the up-vs-down descriptive split. All betas cited are the
  pre-cutoff (`< 2024-07-17`) dev-window estimates from
  `DIAG-MACROBETA-0001` — no post-cutoff outcome contact via those.
- **"Trigger reasons" carry maximum skepticism (TRAP: "every stock has a
  plausible crude story after the fact").** No per-stock catalyst is hand-
  assigned. Any news narrative is labelled **POST-HOC / UNVERIFIED / NOT
  USABLE**. Only SCHEDULED, ex-ante-knowable, checkable events would count —
  and none are asserted as causal below.

---

## 1. VERDICT (lead)

**The 3-day tape reduces to a SECTOR-ROTATION on a mildly DOWN market — NOT a
market-beta effect, NOT a crude/macro impulse, and NOT a set of findable
per-stock triggers.**

1. **The market FELL over the window.** Universe mean return **−1.29%**, median
   **−1.41%** (proxy; the sealed nifty backup is a single stale day). So "these
   66 went up" is emphatically **NOT** "the index went up and these are the
   high-beta names." It is the opposite: on a down tape the gainers are the
   **relative** out-performers.
2. **Consistent with that, the up-group has LOWER market beta, not higher.**
   Mean dev-window `C_b_mkt`: **UP 0.951 vs DOWN 0.991**; up-rate falls monotonic
   across beta terciles (low 0.300 → mid 0.304 → **high 0.214**). Spearman
   corr(3-day ret, `C_b_mkt`) = **−0.13**. **"These went up" does NOT reduce to
   a high-beta tilt** — if anything a mild low-beta/defensive tilt, exactly what
   a down tape produces.
3. **SURVIVES the base-rate control (differential over the 26.4% base up-rate):**
   a **sector rotation** — Chemicals, Metals & Mining, and Autos over-
   represented among winners; Financials, IT, Realty/Telecom/Services under-
   represented. Plus a mild **higher-delivery-%** tilt.
4. **WASHED OUT against the control:** crude-beta clustering (identical up vs
   down — confirms the sibling `DIAG-MACROBETA-0001` finding), turnover/size of
   name, Capital Goods / Power / FMCG (all ≈ base rate), and any "high-beta
   momentum" read.
5. **No per-stock trigger is recoverable or claimed.** The pattern is a
   sector/relative-strength cross-section; individual catalysts (e.g. the
   +14.8% M&MFIN move) are POST-HOC and left unassigned by design.

---

## 2. Data & method (auditable)

- **Universe (250, sanctioned):** columns of
  `data/sealed/raw/2026-07-23/prices_eod_backup_20260624.csv`. = Nifty50 (50) +
  Next50 (50) + Midcap150 (150), confirmed exactly.
- **Returns:** auto-adjusted daily closes cached at
  `scratchpad/universe_recent_closes.csv` (yfinance, public — BINDING RULE 3,
  no Kite). `ret = close(07-23)/close(07-20) − 1`. **UP = ret > 0 → 66;
  DOWN/flat = 184.** 250/250 have a defined return.
- **Sector & size:** `Industry` field and membership from the ex-ante
  (2026-07-19) niftyindices lists under
  `data/reference/pit/raw/niftyindices_current/` (nifty50 / nifty100 → next50 /
  midcap150). Sector UNKNOWN = 0/250. **FACT** (real membership, not fabricated).
- **Betas:** `data/derived/macro_beta_diag/betas.parquet` (`C_b_mkt`, `C_b_oil`,
  `C_b_fx`; SPEC-C). Coverage 209/250 (the 41 gaps are newer listings absent
  from the pre-2024 dev panel — LENSKART, NYKAA, NTPCGREEN, ETERNAL, ICICIAMC,
  MEDANTA, etc.). **ASSUMPTION:** a dev-window beta is a usable ex-ante
  descriptor of a name's cyclicality; it is not re-estimated on live data.
- **Liquidity:** `turnover_cr`, `delivery_pct` from the 2026-06-24 sealed
  snapshot — **~1 month stale** (ASSUMPTION: rank-stable as a coarse descriptor).
- Runner: `scratchpad/analyze_gainers.py`; merged frame
  `scratchpad/gainers_merged.parquet`.

---

## 3. Base-rate control — the load-bearing table

**Whole-universe base UP-rate = 66/250 = 26.4%.** A pattern only "explains"
gainers if its UP-rate materially exceeds 26.4% AND its DOWN-composition is
lower. Read up-rate against 26.4%, always.

### 3a. SECTOR (up-rate vs 26.4% base; N = names in universe)

| Sector | N | n_up | up-rate | vs base | read |
|---|--:|--:|--:|--:|---|
| **Chemicals** | 8 | 5 | **62.5%** | +36pp | SURVIVES (small N) |
| **Metals & Mining** | 12 | 7 | **58.3%** | +32pp | SURVIVES (small N) |
| Consumer Durables | 9 | 4 | 44.4% | +18pp | suggestive, small N |
| Construction Materials | 7 | 3 | 42.9% | +16pp | suggestive, small N |
| **Automobile & Auto Components** | 19 | 8 | **42.1%** | +16pp | SURVIVES (the headline) |
| Consumer Services | 12 | 4 | 33.3% | +7pp | ≈ base |
| FMCG | 16 | 5 | 31.2% | +5pp | ≈ base (WASH) |
| Capital Goods | 28 | 7 | 25.0% | −1pp | WASH |
| Power | 12 | 3 | 25.0% | −1pp | WASH |
| Healthcare | 22 | 5 | 22.7% | −4pp | ≈ base |
| Oil/Gas/Fuels | 10 | 2 | 20.0% | −6pp | under |
| **Financial Services** | 59 | 10 | **16.9%** | −10pp | UNDER-represented |
| Information Technology | 14 | 2 | 14.3% | −12pp | UNDER-represented |
| Realty / Telecom / Services / Textiles / Construction | 20 | 0 | **0.0%** | −26pp | fully absent |

- **The rotation is genuine and directional:** cyclical/commodity-linked
  (Chemicals, Metals, Autos, Consumer Durables) over the line; rate-sensitive
  and defensive-growth (Financials, IT, Realty, Telecom) under it or absent.
- **The base-rate lesson made concrete:** Financials contributes the **most
  winners in absolute count** (10 names, 15.2% of the up-group) purely because
  it is the biggest sector (59 names) — yet it has the **lowest up-rate of any
  large sector (16.9%)**. Counting winners without the control would have read
  Financials as a "theme"; the control shows it is the opposite. This is
  exactly why the control is mandatory.
- **Caveat:** Chemicals (N=8) and Metals (N=12) are small buckets; 5/8 and 7/12
  are suggestive, not statistically nailed. Reported as differentials, not
  as a discovery to trade.

### 3b. SIZE bucket

| Bucket | N | n_up | up-rate |
|---|--:|--:|--:|
| Nifty50 (large) | 50 | 17 | 34.0% |
| Next50 | 50 | 16 | 32.0% |
| Midcap150 | 150 | 33 | 22.0% |

Mild large-cap tilt (large/mid-large ~33% vs midcap 22%) — consistent with a
risk-off session where midcaps lag. Small differential; a secondary read, not a
driver.

### 3c. MARKET BETA (`C_b_mkt`, dev-window) — the decisive control

| Group | n | mean C_b_mkt | median |
|---|--:|--:|--:|
| UP | 57 | **0.951** | 0.911 |
| DOWN | 152 | **0.991** | 0.970 |

Up-rate by beta tercile: low **0.300** / mid **0.304** / high **0.214**.
Spearman(ret, C_b_mkt) = **−0.13**. **The gainers are NOT the high-beta names.**
On a −1.3% tape the higher-beta names fell more; the winners skew slightly
low-beta/defensive. This is the single most important negative result: it
removes the "up-tape × high-beta" explanation entirely.

### 3d. CRUDE / FX beta clusters (cross-ref sibling DIAG-MACROBETA-0001)

| | UP mean | DOWN mean | read |
|---|--:|--:|---|
| `C_b_oil` (crude) | +0.0017 | +0.0016 | **IDENTICAL → WASH.** Not a crude cluster. |
| `C_b_fx` (USD/INR) | −0.013 | +0.026 | small tilt: gainers marginally FX-negative (importer/domestic), but `C_b_fx` is itself a weak/noisy daily signal (sibling §7–8) → treat as weak, not a driver |

**Confirms the sibling look:** the auto leaders and the up-group broadly have
**insignificant crude betas** — this is NOT a crude/macro impulse. The Metals &
Mining names in the up-group (VEDL, HINDALCO, JINDALSTEL, HINDZINC, NATIONALUM,
JSL) are a metals-complex cluster, but their crude loadings are noise; any
"global metals bid" story is **POST-HOC / UNVERIFIED**.

### 3e. LIQUIDITY (2026-06-24 snapshot, stale)

| Metric | UP median | DOWN median | read |
|---|--:|--:|---|
| turnover_cr | 168.9 | 166.3 | WASH (identical) |
| delivery_pct | **52.6** | **45.6** | mild differential — gainers had higher cash-delivery % (less intraday churn / more positional conviction) |

Delivery-% differential is the only liquidity signal with a gap, and it is
mild and from a month-old snapshot. Noted, not leaned on.

---

## 4. The auto / auto-finance headline — honest sizing

The operator's named cluster (M&MFIN, TVSMOTOR, BAJAJ-AUTO, HEROMOTOCO,
EICHERMOT, M&M, MOTHERSON, BOSCHLTD) is **8/8 up** — but that list was
**pre-selected by the operator**, so 8/8 is not an independent finding. The
defensible statements:

- The **broad "Automobile & Auto Components" sector (19 names) is 42.1% up** —
  a real +16pp differential over base, so autos genuinely over-participated.
- **M&MFIN (+14.8%) is the single largest gainer in the universe** and an
  auto-*finance* name (classified Financial Services), so it does not even sit
  in the auto sector bucket — it inflates the "auto rally" narrative while
  formally belonging elsewhere.
- The auto SECTOR is split (8 up / 11 down): the up-rate beats base but is far
  from "the whole sector ran." **No scheduled event is asserted for any auto
  name.** Any "auto rotation catalyst" is **POST-HOC / UNVERIFIED / NOT USABLE**.

---

## 5. Does it reduce to market-beta / sector rotation? — direct answer

**Yes, almost entirely to SECTOR ROTATION, and explicitly NOT to market beta.**

- Market-beta channel: **rejected** (up-group lower beta; market fell; §3c).
- Crude/macro channel: **rejected** (crude betas identical up vs down; §3d).
- What remains is a **cross-sectional sector rotation** (cyclicals/commodities/
  autos bid, financials/IT/realty/telecom sold) on a mildly risk-off tape, with
  a mild large-cap and mild high-delivery tilt. That is a *description of which
  sectors moved*, not a *per-stock trigger*. **There is largely no stock-
  specific "trigger" to find** — the winners are mostly "names in the sectors
  that rotated up," which is the null the base-rate control was built to expose.

**Does a distinct cluster survive?** The **Chemicals + Metals & Mining** pair is
the one non-obvious survivor (up-rates 62.5% / 58.3% vs the auto headline's
42.1%), i.e. the commodity/materials complex out-participated even the autos.
Named, per the brief, purely as an observable attribute (`Industry ∈ {Chemicals,
Metals & Mining}`) with small-N caveat — **NOT proposed as a signal**.

---

## 6. What WASHED OUT (report these so the operator does not over-read)

- **Market beta / momentum tilt** — inverted, not present.
- **Crude-beta cluster** — identical up vs down.
- **Turnover / size-of-name (liquidity depth)** — identical medians.
- **Capital Goods, Power, FMCG, Healthcare, Consumer Services** — all within
  ±7pp of the 26.4% base; not differentiated.
- **Any single-stock "catalyst" story** — unassigned by design; POST-HOC.

---

## 7. Caveats

- Small-N sectors (Chemicals 8, Metals 12, Consumer Durables 9, Construction
  Materials 7): differentials are suggestive, not significant (no scipy;
  proportions reported with N so the reader sizes the noise).
- Market proxy = universe mean/median (the sealed nifty backup is one stale
  day); good enough for sign and rough magnitude, not a precise index print.
- Betas & liquidity are pre-cutoff / stale descriptors used only as coarse
  ex-ante attributes; no post-cutoff outcome contact runs through them.
- 41/250 names lack a dev-window beta (newer listings); the beta reads use the
  209 covered names and could shift slightly with fuller coverage.

---

## 8. PROPOSED REGISTER ROW (TEXT ONLY — do NOT write; sibling owns the register this round)

```
DIAG-GAINERS3D-0001,2026-07-23,MONITORING,look-don't-tune,\
  "3-day up-vs-down cross-sectional description (close 2026-07-20->2026-07-23), \
   250-name universe, 66 up / 184 down; base-rate-controlled sector/size/beta/ \
   crude-fx/liquidity cross-tab; NO signal built or selected",\
  outcome_blind=DESCRIPTIVE_UPVSDOWN_ONLY, trial_spent=NO, shadow_slot=NONE, \
  final_test=NO, cumulative_trial_count=UNCHANGED(53), \
  firewall="monitoring only; must never feed spec/signal design or tuning"
```

Rationale for NO trial: an up-vs-down cross-sectional *description* with a
mandatory base-rate control and no strategy return / Sharpe / forward-return-
conditional statistic sits in AMENDMENT A's free "correlation structure"
bucket, same as the sibling `DIAG-MACROBETA-0001`. **If any downstream use
selects or tunes on this, it retroactively becomes a TRIAL and must be
registered as such.**

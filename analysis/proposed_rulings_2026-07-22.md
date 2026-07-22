# PROPOSED RULINGS 11 and 12 — for operator review

> **STATUS: DRAFTED, NOT ADOPTED.** These are proposed additions to
> `governance/DECISIONS.md`. They are NOT in force until the operator appends
> them to that file. Drafted 2026-07-22 following the outcome-blind Tier 2
> analysis pass (`analysis/SRA_friction_hurdle.md`, `analysis/AG01_circularity.md`).
>
> Neither ruling observes an outcome. Neither spends a trial, consumes a shadow
> slot, or touches sealed data. Both are reversible by a superseding ruling.

---

## 2026-07-22 — RULING 11: SPEC-SRA-01 is killed as a fund candidate (no trial spent)

- **Context.** `SPEC-SRA-01.md` (DRAFT, never frozen, no hash, no register row)
  proposed a ~5-trading-session rally-anticipation family. Its own §0 required
  the cost test to come first and could not be deferred; its own pre-stated null
  was that a 5-day family dies on friction. The test was run analytically on
  2026-07-22 with **zero outcome contact** — no panel, no returns, no
  `data_gate` call — per `CONTAMINATION_POLICY.md` AMENDMENT A (outcome-blind
  diagnostics are free).

- **FACT — statutory friction.** Worked delivery round trip at a ₹1L slot =
  **23.782 bps**, reconciling exactly with the RULING 5 Variant A figure already
  on record. **STT is 84% of it and is irreducible.** At a ₹5 Cr position the
  flat DP charge dilutes to a **22.279 bps** base. Brokerage (₹0) and DP
  (₹15.34) remain operator ASSUMPTION lines totalling ~1.5 bps; if either is
  wrong the verdict only worsens.

- **FACT — turnover.** A 5-session hold implies 252/5 = 50.4 round trips/yr/slot
  = **5,040%/yr one-way**. SPEC-SRA-01 §8.3's own 6,000% budget therefore does
  NOT fire on the primary config. The family does not die on its own turnover
  budget; it dies on expectancy and capacity.

- **FACT — capacity, and this kill needs no alpha estimate.** At the programme's
  stated ₹100 Cr target with N=20, position size is **₹5 Cr**. SPEC-SRA-01's own
  MANDATORY liquidity floor admits names at **₹2 Cr/day ADV**. The order is
  therefore **250% of a full day's volume**, and entry at 10% participation
  takes **25 sessions against a 5-session hold**. This is arithmetically
  impossible at the floor of the spec's own admissible universe. Inverted, the
  spec describes a **₹1–15 Cr strategy** — off by roughly an order of magnitude
  from the fund mandate.

- **FACT — expectancy.** Required per-fire edge `E[fwd5|setup] ≥ c`: **+42.3 bps**
  at the spec §7 slippage floor of 10 bps/side, rising to **+122.3 bps** at 50
  and **+222.3 bps** at 100. Annualised friction drag **21.3% / 61.6% / 112.0%**
  respectively — i.e. **1.15× / 3.33× / 6.06×** the legacy system's entire
  measured gross alpha. At the capacity-implied 50–100 bps/side the family needs
  3.3–6.1× legacy gross.

- **FACT — the legacy anchor.** Recomputed, the killed legacy system ran ~1.6
  round trips/day over ~5 slots ⇒ **8,064%/yr one-way**, statutory drag
  **19.18%/yr against 18.5%/yr gross alpha** — already underwater before any
  slippage. SRA sits at **0.62× legacy turnover**: a real 38% improvement, and
  nowhere near sufficient. SRA would have to out-earn, on 8 OHLCV features, a
  six-factor system with fundamentals and catalyst data that lost this exact
  fight.

- **RULING.** SPEC-SRA-01 is **KILLED as a ₹100 Cr fund candidate**. It is not
  to be hash-frozen. `src/expr.py` is NOT to be extended for it (the §6
  pre-freeze blocker — new primitives on a module shared with the FROZEN
  SPEC-52WH-01, with regression suite and per-primitive NaN policies — was the
  largest avoidable cost on the board). `signal_sra.py` and `run_trial_sra.py`
  are not to be built. Stage S0 is not to be run. The DRAFT file is retained as
  the audit record of why.

- **Trial accounting: NO TRIAL SPENT.** No outcome was observed. The cumulative
  register count is unchanged. No shadow slot was held or released — SRA never
  held one.

- **SCOPE OF THE KILL, stated narrowly.** This kills SRA *as a fund candidate at
  the ₹100 Cr mandate*. Capital base is NOT pinned anywhere in SPEC-SRA-01, and
  the capacity kill vanishes at ₹1–5 Cr. Should the operator later want this as
  a small-capital production variant, that requires a **new versioned spec**
  (the SEAL_v2 pattern) with the capital base pinned in writing — never an edit
  to SPEC-SRA-01, and never a quiet reinterpretation of this ruling.

- **ASSUMPTION flagged.** The half-spread in this habitat is UNVERIFIED in this
  repo (needs tick data). Notably the spec's 10 bps/side *total* floor is likely
  below the half-spread alone, making that column an unreachable optimistic
  bound rather than a central case. The impact model is square-root
  (`Y·σ_d·√(Q/ADV)`, Y ∈ {0.5, 1.0}) — the CHARITABLE choice; linear impact
  would be materially worse above 10% of ADV.

- **Spillover — carried to a separate action, not adopted here.** Two
  family-agnostic gates fell out of this work: the hurdle
  `(252/H) × (22.3 bps + 2s)` and the capacity pre-screen
  `position / ADV_floor ≤ ~10%`. **The capacity pre-screen has NOT been recorded
  for SPEC-52WH-01, SPEC-QFM-01 or SPEC-PEAD-01, which share the same 201–1000
  habitat.** Per TRAP 7 these belong in `src/` as a loud-failing helper, not in
  a document.

---

## 2026-07-22 — RULING 12: SPEC-AG-01 demoted below SPEC-52WH-01; depth spike re-scoped, not cancelled

- **Context.** SPEC-AG-01 (MCX Silver carry / term structure) sat third in the
  Tier 2 queue ahead of SPEC-52WH-01. An outcome-blind desk analysis was run
  2026-07-22 on facts already recorded in the repo. **No MCX endpoint was
  touched** — the exchange ToU question is unresolved (OPEN OPERATOR DECISION 1)
  and fetching first would pre-empt the very ruling the analysis feeds.

- **FACT — the circularity is real but remains an ASSUMPTION.** The record says
  MCXCCL *"may"* mark an illiquid far month from the spread between active
  contracts. Where it does, the tautology is algebraic, not approximate: if
  `P(T2) = P(T1)·exp(ĉ·Δ)` then a carry estimator returns `ĉ` exactly. It is
  worse than the binary framing suggests — the trade-information weight is
  **endogenous to the signal**, because far-month liquidity collapses precisely
  when carry is doing something interesting, so measurement error pulls toward
  the clearing corporation's model *in exactly the states of interest*.

- **FACT — a second, additive defect not previously recorded.** `Close` legs are
  **asynchronous** across MCX's long session (last-trade marks struck hours
  apart). For a spread, that noise can exceed the signal. This is independent of
  the circularity and survives any fix to it.

- **FACT — the proposed contamination flag does not partition.** Separating
  `volume==0 AND close==PCP` (stale) from `volume==0 AND close!=PCP`
  (spread-derived) sorts rows into "provably contaminated" and "unknown", never
  "clean". Its largest blind spot is **calendar-spread execution reported as two
  legs**, where the far leg's print is arithmetic on the near price —
  contamination *inside* genuine non-zero volume, invisible to any volume
  threshold. It also misses single-print `O=H=L=C` bars with volume>0, which is
  the exact fingerprint of the C1-52WH-0001 defect.

- **FACT — statistical power, and this is decisive.** The one design that
  cleanly escapes the circularity — measuring the **traded calendar spread**
  during the roll rather than the ratio of two outright marks — yields only
  **~48–114 independent roll episodes** across the entire 2015 → 2024-07 dev
  window. The roll episode, not the session, is the unit of independent
  information, and the stationary-bootstrap SPA will correctly see through
  within-episode autocorrelation. **This will not clear a SPA gate charged
  against 52+ cumulative trials, and it kills the design even if the
  circularity resolves favourably.**

- **FACT — two blockers not previously on the list.** (1) **AG-01 has no cost
  stack**: RULING 5 and `src/costs_in.py` are NSE cash-equity only, and
  commodity friction is a prerequisite rather than a detail when the edge is
  basis points of a spread. (2) **AMENDMENT C bites hardest on the seasonality
  fallback** — the one design that escapes circularity runs on the very series
  the ≥8-trial Silver ML engine already iterated over.

- **RULING.** SPEC-AG-01 is **demoted below SPEC-52WH-01** in the Tier 2 queue.
  It has no frozen spec, no data, no cost stack, an unresolved ToU blocker and
  now a power problem; SPEC-52WH-01 has a built Stage 1–5 stack and a decision
  already before the operator. Queue position gates only the shadow-book/sealed
  stage (RULING 6) and is reversible by a superseding ruling.

- **RULING — the depth spike is RE-SCOPED, NOT CANCELLED.** Cancelling would
  kill a family on an assumption, which is the same error as advancing on one.
  The spike as originally written answers "do bytes come back?", the least
  valuable available question: reaching 2010 instead of 2015 moves N from ~48 to
  ~72, i.e. **~22% on a t-statistic**, whereas the circularity question is
  binary. Revised sequence:
  1. Capacity arithmetic from published aggregates — free, may kill outright.
  2. **Read MCXCCL's published DSP methodology and the bhavcopy file spec** —
     documentary, no endpoint touched, settles the circularity to FACT in either
     direction. If the rule proves to be e.g. "last 30-min VWAP else previous
     DSP", that is BETTER news than currently assumed.
  3. The exchange ToU ruling (MCX is the worst fetch-first candidate of the
     three exchanges).
  4. Pre-commit a kill line in writing.
  5. Re-scoped spike whose FIRST question is **"does the bhavcopy publish traded
     calendar-spread rows with their own volume and OI?"** — 1–2 dates, 2010
     fetch dropped. Net cheaper than the original.

- **FACT — vendor scope.** A licensed vendor (Accord Fintech / ACE Datafeed,
  now surfaced independently in four research passes) would solve **access and
  ToU, not circularity**. No vendor manufactures a settlement price MCX never
  computed, nor roll episodes the calendar never contained. It could however
  supply a distinct DSP field, OI, and **number of trades** — the diagnostic the
  volume flag structurally cannot see. Those asks are already in the drafted
  enquiry (`analysis/accord_fintech_enquiry.md`).

- **Trial accounting: NO TRIAL SPENT.** No outcome observed, no data acquired,
  no shadow slot moved. AG-01 held no slot (QFM and PEAD hold both).

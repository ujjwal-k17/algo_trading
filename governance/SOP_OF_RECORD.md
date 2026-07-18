# SOP OF RECORD — Entry/Exit Rules of the Legacy Engine

**Derived from the frozen clone at `~/vendor/legacy-engine`, pinned SHA
`ee7ad13228244f4f27e3d2d839baf70897ff24fe` (governance/LEGACY_PIN.md).**
Every rule cites file:line in that clone. This document — not the code — is what
the paper-leg engine and its tests trace to.

**Status: CONFIRMED 2026-07-17 — all open questions resolved by RULING 4
(governance/DECISIONS.md). §7 records each resolution with its
FACT/ASSUMPTION tag. §8 states the governing principle.**

---

## 1. Recommendation lifecycle

- Recs are generated on the evening of `pick_date` (Day 0); the stock is not
  held on Day 0. Candidate entry is the **next trading session**, which is
  Day 1 (`market_calendar.py:170-178`, `picks_log.py:44-56`).
- The rec's reference entry price `rec_entry` is the **close of pick_date**
  (`picks_log.py:62` — `ep = close or entry_price`, inserted as both
  `entry_price` and `rec_entry` at `picks_log.py:72-79`).
- Entry statuses: `PENDING → ENTERED | SKIPPED`; conditional entry types
  requiring morning confirmation are `CONDITIONAL, BREAKOUT, LIMIT, WAIT*`
  (`picks_log.py:30-38`); anything else is entered unconditionally
  (`picks_log.py:66` — `estatus = "PENDING" if _is_conditional else "ENTERED"`).

## 2. Entry confirmation gates (intraday, morning of Day 1)

From `preopen_check.py:580-733` (`check_entry_confirmation`, 9:20 check on the
09:15–09:20 first candle) and `preopen_check.py:736+`
(`check_thirtymin_confirmation`, 9:45 binary BUY/SKIP on the 09:15–09:45 candle):

| entry_type | BUY when | SKIP when |
|---|---|---|
| CONDITIONAL | candle close > `hold_level` AND volume_ratio ≥ 1.0 (`:605-612`) | close > 1% below hold_level (`:624-631`) |
| BREAKOUT | candle close > entry_price AND volume_ratio ≥ 1.5 (`:655-661`) | close > 1% below entry level (`:670-676`) |
| WAIT AND WATCH | gap ≥ 0.5% AND volume_ratio ≥ 2.0 (`:686-690`) | no meaningful gap (`:696-697`) |
| LIMIT | pre-open ≤ limit price (`:701-706`) | — (stays WAIT) |

- `hold_level` defaults to `entry_price * 0.995` (`preopen_check.py:592`).
- 9:20 WAIT verdicts go to the 9:45 check, which is **binary and final**
  (`preopen_check.py:736-745`).
- **Actual fill price proxy** on confirmation: the 9:20 first-candle close or
  the 9:45 30-min close, recorded with slippage vs `rec_entry`
  (`observer.py:419-436`). Entry day is Day 1 (`observer.py:449-452`).

## 3. Expiry of never-entered picks (not an exit)

- Unconfirmed picks are auto-expired once **≥ 5 NSE trading sessions** have
  elapsed after `pick_date` (exclusive) (`run_phase2.py:74-118`:
  `_trading_days_since` + `_expire_assumed_positions`,
  reason `AUTO_EXPIRED_5_SESSIONS`).
- These rows are excluded from performance stats (`observer.py:432-434`).
  In `trades_log.csv` the patch sets only `exit_date`/`exit_reason`, no price
  (`run_phase2.py:121-133`).

## 4. Exit rules for ENTERED positions (daily EOD, priority order)

From `exit_manager.py:50-140` (`run_exit_checks`), evaluated once per session
against that session's OHLC, **first match wins**:

| Priority | Rule | Trigger | Exit price | Source |
|---|---|---|---|---|
| 1 | STOPPED | `low ≤ stop_loss` | `stop_loss` (the level) | `exit_manager.py:111-117` |
| 2 | T2_HIT | `high ≥ t2` | `t2` | `exit_manager.py:119-125` |
| 3 | T1_HIT | `high ≥ t1` | `t1` | `exit_manager.py:127-134` |
| 4 | TIMEOUT | `sessions_open ≥ 5` (pre-increment) | that session's **close** | `exit_manager.py:136-140` |
| 5 | no exit | — | counters increment | `exit_manager.py:142-158` |

- **Same-bar SL+target: the stop is checked first and wins** — this is the
  code's deterministic convention (order of `:111` before `:119`/`:127`).
- Sessions with no OHLC row are skipped and carried forward
  (`exit_manager.py:102-105`).
- Missing-data days do not increment `sessions_open`.

## 5. Metrics

- `pnl_pct = (exit − entry) / entry × 100`; **R-multiple =
  `(exit − entry) / (entry − stop_loss)`** (risk = entry − stop;
  `exit_manager.py:41-45`).
- Sizing convention: **5 slots × ₹1,00,000 = ₹5,00,000 book; every ENTERED
  pick deploys exactly one full slot** at ledger entry price; idle cash earns 0
  (`observer.py:1060-1073`).

## 6. Cross-check against fills snapshot (step c)

Snapshot: `data/legacy_snapshot/trades_log_ee7ad13.csv` (26 rows, copied from
the frozen clone's committed `output/trades_log.csv` — not from live production).

- **Zero completed STOPPED/T1/T2/TIMEOUT exits exist in the snapshot** —
  14 rows are `AUTO_EXPIRED_5_SESSIONS` (never entered), 11 are open. The
  exit-price rules therefore **could not be validated against realized exits**;
  no contradictions found, but vacuously so.
- What could be verified: expiry timing matches spec — e.g. picks dated
  2026-06-29 (Mon) expired 2026-07-06 = exactly 5 NSE sessions after pick_date
  (matches `run_phase2.py:88-99`); expired rows carry empty `exit_price`
  (matches `run_phase2.py:121-133`). ✓
- Executed-entry mismatches prove nothing (discretionary overlay), per brief.

## 7. RESOLUTIONS (RULING 4, 2026-07-17) — supersedes the open questions below

1. **T1 semantics → FULL exit at t1. CONFIRMED-BY-OPERATOR (2026-07-18):**
   the operator states the desk takes the full exit at T1; the 50%-partial
   alert text (`exit_manager.py:220-227`) is not traded. FACT: DB semantics
   (`exit_manager.py:127-134,161-168`) — now operator-confirmed, no longer an
   assumption chosen by inference. No SOP v2 required.
2. **Same-bar SL+T1/T2 → SL-first, trade FLAGGED** (`flag_ambiguous_same_bar`).
   ASSUMPTION (conservative-standard; also matches code check order). Reporting
   shows results with and without flagged trades.
3. **Gap open beyond SL → exit at OPEN price** (not the SL level). ASSUMPTION
   (realism over the code's level-fill).
4. **Gap open beyond T1 → exit at OPEN price**; extended to T2 gaps by the same
   logic. ASSUMPTION (realism).
5. **Time exit → close of the 5th holding session, entry day = Day 1** (FACT:
   `market_calendar.py:170-178`); holiday/halt on the nominal final day rolls
   to the next session's close (ASSUMPTION).
6. **Entry → per clone code (FACT); unrecorded fill price → next-session open**
   (ASSUMPTION, RULING 4a). Entries resolved this way carry
   `flag_entry_assumed`.
7. **Halted/limit-locked → carry to first available price, FLAG**
   (`flag_halt_carry`). ASSUMPTION.
8. **Partial fills → none: full fill at rec size.** CAVEAT (RULING 4g): the
   paper leg is a counterfactual of the SOP, not of liquidity — its results
   assume the one-slot size always fills.
9. **Corporate actions → adjusted price series throughout** (RULING 4h);
   `flag_ex_date` set when corp-action data is supplied, else recorded as
   not-evaluated (None). ASSUMPTION.
10. **Post-cutoff governance → Tier 1 operational door**
    (`data_gate.load_operational`, RULING 2, `governance/SEAL_COMPANION.md`).

## 8. Governing principle (RULING 4i)

**Realism, biased in neither direction.** The paper leg is the benchmark the
discretionary overlay is graded against; every residual convention must
neither flatter nor punish the executed leg. Where the engine's code and
realistic fills disagree (gap-through levels), realism wins and the choice is
tagged ASSUMPTION.

---

### Appendix: original open questions (historical, superseded by §7)

1. **T1 semantics conflict.** The DB records T1_HIT as a **full exit at t1**
   (`exit_manager.py:127-134,161-168`), but the alert text instructs a **50%
   partial at T1, trail stop to entry, run rest to T2**
   (`exit_manager.py:220-227`). Which is SOP for the paper leg?
2. **Same-bar SL+T1/T2.** Code convention on a daily bar is SL-first (worst
   case). Adopt for paper leg, or flag such bars as indeterminate?
3. **Gap-through levels.** Code exits at the level even when price gapped past
   it (e.g. open < SL ⇒ real fill ≈ open, code says SL). Keep code-faithful
   level fills, or realistic `min(open, level)` / `max(open, level)` fills?
4. **Time-exit counting.** `exit_manager` fires TIMEOUT at `sessions_open ≥ 5`
   pre-increment (positions table), the ledger uses
   `trading_sessions_since(pick_date) ≥ 5` with Day 1 = entry day. Confirm the
   daily-bar mapping: exit at the close of the 5th holding session (entry day
   = Day 1) if nothing else triggered?
5. **Entry gates aren't computable from daily OHLC** (9:20/9:45 candles,
   pre-open, intraday volume ratios). Choose: (a) assume every rec enters at
   Day-1 open (pure "if executed" counterfactual); (b) daily-bar approximation
   (gap from open, ignore volume gates); (c) use the system's recorded
   verdicts from `candle_verdicts_<date>.json` snapshots as the entry oracle?
6. **Paper-leg entry price.** `rec_entry` (pick-date close), Day-1 open, or
   the candle-close fill proxy (only available under 5c)?
7. **Partial fills.** No partial-fill logic exists anywhere in the clone —
   confirm all-or-none fills for the paper leg.
8. **LIMIT recs.** Pre-open data unavailable in daily bars; treat LIMIT recs
   under the same choice as Q5, or exclude them?
9. **Governance tier conflict (needs a ruling, not code).** Every rec is
   post-2024-07-17, so `data_gate.load()` in default mode strips 100% of them —
   a workspace built per the ingest spec would be empty for this task. The seal
   was designed for signal research on history; the paper leg is operational
   analysis of live-era data. Options: a declared operational-data tier
   (gate mode `OPERATIONAL=1` that logs but passes), a separate gate function,
   or an explicit SEAL_v2 carve-out. Your call.

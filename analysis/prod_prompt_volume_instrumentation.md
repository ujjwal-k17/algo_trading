# Production prompt — volume-projection instrumentation (NO behaviour change)

> Drafted 2026-07-22 for the **production** project
> (`~/Desktop/AI Apps/NSE_Stock_Picks`), to be run there by the operator.
> This research workspace cannot and must not run it (BINDING RULE 1).
>
> Basis: RULING 13 + the 2026-07-22 `VERIFIED AT PRODUCTION HEAD` entry in
> `governance/DECISIONS.md`; register rows `DIAG-VOLSHARE-0001`,
> `-0001-RESULT`, `-0002-REFINE`.
>
> **Why instrumentation only.** RULING 13d forbids any live parameter change
> before the 2026-09-27 AB_PREREG read date. Independently of governance, the
> measured `s` is a bracketed estimate from a source with a 98% hole in the
> exact bar under test; production's own Kite data is strictly better evidence.
> Instrument first, recalibrate on production's own numbers after the read date.
>
> **Do not recalibrate from the numbers in this file.** They are indicative,
> and the per-stock spread (~10×) means no single constant is correct anyway —
> the recommended end-state is a per-symbol denominator, not a new constant.

---

## The prompt

```
Context: our entry-path volume gates project a partial bar to a full day by
assuming volume is spread uniformly across the session. preopen_check.py:433
and :475 do `vol * 75 / avg_vol` for the 9:15-9:20 bar; :523 and :568 do
`total_vol * 12.5 / avg_vol` for the 30-minute bar. Both assume uniform
intraday volume. NSE volume is heavily front-loaded, so both projections
overstate. observer.py:493 and store.py:780 both note that nothing has ever
compared the projection against the realized day. That is what this task fixes.

An external study on yfinance data estimates the 9:15-9:20 bar is ~4-6% of
daily volume (vs the 1.33% that x75 implies) and the first 30 minutes ~13-18%
(vs the 8% that x12.5 implies). Treat those as indicative only - that data
source is known to be defective for exactly this bar. The point of this task
is to measure it properly from OUR OWN Kite data.

BINDING CONSTRAINT - read carefully:
This change must NOT alter any recommendation, verdict, or entry decision.
It is instrumentation only. The recommended leg is currently the measured
instrument in a live A/B running to 2026-09-27; changing what the system
recommends mid-window corrupts that measurement.

Specifically, you MUST NOT:
  - change the 75 or the 12.5 projection constants
  - change VOL_GATE_CONDITIONAL (1.0), VOL_GATE_BREAKOUT (1.5),
    VOL_GATE_WAIT (2.0) in preopen_check.py:46-57
  - change the `or 0.0` coercion at preopen_check.py:613 and :769
    (it collapses None/unknown into a hard gate failure - a real bug, but
    fixing it changes decisions, so it is deferred, NOT forgotten)
  - change any verdict, reason string that feeds a decision, or gate branch

WHAT TO BUILD

1. Persist the projection inputs at decision time. Wherever a volume_ratio is
   computed (preopen_check.py:433, :475, :523, :568), record alongside it:
   symbol, session date, the anchor (09:15-09:20 or 09:15-09:45), the raw bar
   volume, avg_volume_20d, the projection multiplier used, and the resulting
   volume_ratio. Store it where the existing candle/verdict records live so it
   joins on symbol+date. Note volume_ratio is ALREADY persisted in some paths
   (see the vol_ratio_projected kwarg at preopen_check.py:1636 and :1721) -
   extend that rather than building a parallel store.

2. Add an end-of-day reconciliation job that, for each symbol-session
   instrumented that morning, fetches the REALIZED full-day volume and records:
     realized_full_day_volume
     realized_share = raw_bar_volume / realized_full_day_volume
     implied_correct_multiplier = 1 / realized_share
     projection_error = (multiplier_used * realized_share)
       -> 1.0 means the projection was exactly right; >1 means it overstated
   Run it after the close, in the existing nightly slot, via guarded_run.py
   like every other com.nse job.

3. Make it fail loudly, not silently. Assert an expected row count per session
   and log a WARNING if instrumented symbols < expected, or if realized volume
   is missing for >10% of them. A zero exit code and a non-empty table are not
   evidence that it worked.

4. Log a WARNING (do not change behavior) whenever the 9:15-9:20 bar arrives
   with volume == 0 or None while its price fields are valid. On yfinance this
   happens in ~98% of sessions; if it is also happening on the Kite path we
   need to know immediately, because `or 0.0` then turns it into a silent
   all-veto. Include the source field (kite / yfinance / unavailable) in the
   log line and in the persisted row.

5. Add a small report surface (extend an existing daily/weekly report rather
   than adding a new one) showing, over the trailing N sessions: median and
   volume-weighted realized_share for both anchors, the implied correct
   multiplier, and the count of zero-volume opening bars by source.

REQUIREMENTS
  - Follow this repo's own governance: if a register row or change-log entry is
    required for a production change, create it. Unwritten state does not exist.
  - Tests for the new reconciliation logic, including the zero-volume and
    missing-realized-volume paths.
  - Do not touch the ledger schema destructively; additive columns/tables only.
  - Do not make live broker calls beyond what the existing nightly jobs
    already do.

DELIVERABLE
A short summary of: what you instrumented, where the rows land, how to read
the report, and confirmation that no decision path changed - ideally by
showing that verdict outputs are byte-identical before and after on a replayed
session.
```

---

## After the 2026-09-27 read date

The recommended end-state is **not** `75 -> 25`. Measured `s` spans ~10×
across stocks (1.14% NAUKRI → 10.51% KALYANKJIL), so a single global constant
is wrong for individual names in both directions — it relocates the error
rather than removing it.

Replace the **denominator**: compare the 9:15–9:20 volume against the 20-day
average of *that symbol's own* 9:15–9:20 volume. Then `s` cancels
algebraically, `1.0×` / `1.5×` / `2.0×` recover their intended meanings, and
the gate self-calibrates per symbol and per liquidity tier. The same applies to
the 30-minute anchor with its own 20-day average.

By then the instrumentation above will have supplied a clean per-symbol
baseline from Kite data, which is exactly what that denominator needs.

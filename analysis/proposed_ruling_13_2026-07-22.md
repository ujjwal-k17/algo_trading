# PROPOSED RULING 13 — for operator review

> **STATUS: DRAFTED, NOT ADOPTED.** This is a proposed addition to
> `governance/DECISIONS.md`. It is NOT in force until the operator appends it
> to that file. Drafted 2026-07-22.
>
> Unlike RULINGS 11 and 12, this ruling **does authorize outcome contact** and
> **does spend a trial**. Read the trial accounting section before signing.

---

## 2026-07-22 — RULING 13: microstructure diagnostic door (opening-bar volume share)

### Context — the defect under test

`preopen_check.py:420` and `:462` in the frozen clone compute the go/no-go
volume confirmation as:

```python
v_rat = round((vol * 75) / avg_vol, 2)
```

where `vol` is the volume of the single 9:15–9:20 bar and `avg_vol` is
`get_avg_volume_20d` — a 20-session mean of **daily** volume from `prices_eod`.
`synthesis.py:51-57` then treats `< 1.0x` as unconfirmed, `< 1.2x` as
unconfirmed unless the chart read is "yes", and `>= 1.2x` as confirmed.

`75` is the bar count of a 375-minute NSE session (verified empirically:
yfinance returns exactly 75 five-minute bars per session). The `× 75`
extrapolation is therefore only valid if intraday volume is **uniformly
distributed across the session**. It is not — NSE volume is front-loaded.

Writing `s` for the opening bar's true share of daily volume:

```
volume_ratio = s × 75 × (today_volume / avg20_volume)
```

so the `>= 1.2` gate actually tests `today_relative_volume >= 1.2 / (75 × s)`.
At the implicit assumption `s = 1/75` this is the intended "today >= 1.2×
normal volume". At any larger `s` the gate loosens proportionally and may be
**near-vacuous** — passing everything except unusually quiet days.

`s` has never been measured in this program. This ruling authorizes measuring it.

### FACT — why neither existing door admits the measurement

Read from `src/data_gate.py` on 2026-07-22:

- `load()` strips every row `>= 2024-07-17` (`SEAL_CUTOFF`). Intraday data does
  not exist that far back (see next item), so the research door returns empty.
- `load_operational()` rejects the frame three separate ways: a 250-name
  intraday panel is not rec_key-joinable and trips the explicit *"generic OHLC
  panel"* rejection (`data_gate.py:128-137`); roughly half the reachable window
  (2026-05-23 → 06-28) falls in the seal gap and is rejected outright
  (`:148-153`); and `data/workspace/` is not an admissible source.

**This blocker is independent of the outcome conditioning.** Dropping the
up-day selection entirely would not change any of the three rejections. A
ruling is required to measure `s` at all, in any form.

### FACT — the data horizon is 60 days and cannot be extended

Probed 2026-07-22: yfinance returns 5-minute bars only for the last 60 calendar
days (`"The requested range must be within the last 60 days"`; Jan/Mar/Apr 2026
requests returned 0 rows). Reachable window is therefore approximately
**2026-05-23 → 2026-07-22, ~40 trading sessions**.

Deeper intraday history exists only via Kite Connect, which **BINDING RULE 3
forbids**. This ruling does not disturb that. The 60-day horizon is accepted as
a permanent constraint on this measurement, not a temporary one.

Consequence: the measurement window straddles the seal gap
(2026-05-23 → 06-28) and the live window (2026-06-29 →). It cannot be confined
to the live window without discarding more than half the sessions.

### RULING

1. **A narrow diagnostic door is opened**, for this measurement only:
   post-cutoff intraday (5-minute) OHLCV for the 250-name system universe may
   be fetched from yfinance and analysed **for volume-share statistics only**.

2. **Scope limit — no return is ever a measured quantity.** The dependent
   variable is `s = first_5min_volume / full_day_volume`, a pure volume share.
   Price enters ONLY as a sample-selection filter (sessions where the 15:30
   price exceeds the 9:20 price). No return is averaged, regressed, attributed,
   or reported as a performance figure. Any extension beyond a volume share
   requires a new ruling.

3. **The conditioning is disclosed, not hidden.** Selecting on up-sessions IS
   outcome-conditional under `CONTAMINATION_POLICY.md`. It is authorized here
   because the operator has specified it, and it is recorded as a spent trial
   (below) rather than being reclassified as a free diagnostic.

4. **Measurement only — no live change before the read date.** This ruling
   authorizes measuring `s`. It does **not** authorize altering the `× 75`
   constant, the `1.2` threshold, or any other live recommendation parameter.
   The recommended leg is the instrument under measurement in `AB_PREREG.md`
   through **2026-09-27**; re-tuning it mid-window would change the instrument
   mid-experiment and corrupt analyses 1–4. Acting on the result is a separate
   decision, to be taken on or after the read date.

5. **Mandatory coverage assertions (TRAP 1 / TRAP 6).** The run must report,
   and the write-up must disclose: symbols successfully fetched of 250;
   sessions retained per symbol; bars per session (expect 75) with sessions
   below quorum dropped and counted; placeholder/zero-volume rows dropped and
   counted; and the count of sessions failing the 9:15 bar-date check. A
   successful exit code and a non-empty row count are not evidence.

6. **Reporting.** Report the operator-specified volume-weighted mean
   (equivalently the pooled share `Σ first5 / Σ full_day`) AND the unweighted
   mean, median, and decile spread, AND a breakdown by index tier
   (NIFTY50 / NEXT50 / MIDCAP150). A single pooled number would hide the
   liquidity dependence that is the whole point.

7. **Known caveats to be carried into any write-up.** (a) Universe membership
   is taken as of the 2026-06-24 snapshot and applied to the whole window, so
   May sessions use marginally forward-looking membership — immaterial for a
   volume share, disclosed for completeness. (b) The window contains no index
   reconstitution (March done, September pending) but does contain expiry days,
   which concentrate volume. (c) 40 sessions is a short window and `s` may vary
   with the volatility regime; this is an estimate, not a constant of nature.

### Trial accounting — A TRIAL IS SPENT

- **One trial is spent** and must be appended to
  `governance/research_register_v2.csv`. Under `CONTAMINATION_POLICY.md`, an
  outcome-conditional analysis is a trial; the up-session filter is exactly
  that. It is booked honestly rather than argued away.
- **Cost is low, per the CLAUDE.md trial-economics corollary.** A marginal
  trial moves the deflation bar ~0.3%. The scarce resources are the 2 shadow
  slots and the single sealed test per family.
- **No shadow slot is consumed.** This touches no Tier 2 family — not QFM, not
  PEAD, not AG-01, not 52WH. Both shadow slots remain with QFM and PEAD.
- **No sealed test is burned.** The trial is charged against the **legacy**
  daily mid-cap momentum family, which is already KILLED as a fund candidate
  (real gross alpha ~18.5%/yr, t≈2.95, fully consumed by friction). That family
  has no remaining sealed test to protect, so the contamination has no target.
- **`FINAL_TEST=1` is NOT set and must not be.** No Tier 2 family's holdout is
  opened by this run.

### Reversibility

The diagnostic door is opened for this measurement only and closes on
completion. It does not amend `load()` or `load_operational()`; the carve-out
lives in the calling script, which hard-fails unless this ruling is present in
`governance/DECISIONS.md`. Superseding this ruling requires only a later
ruling; no data is destroyed and no seal is moved.

# SEAL COMPANION — Operational Tier Addendum (v1)

Companion to `governance/SEAL.md` (which is immutable and remains untouched).
Added 2026-07-17 under RULING 2 (`governance/DECISIONS.md`).

## Look-don't-tune (Tier 1 forward data)

The seal governs **historical market data used for research** (dev strictly
before 2024-07-17; sealed holdout 2024-07-17 onward). **Forward operational
data** — recommendations, fills, overlay decisions, and paper-leg settlements
dated on or after the live-window start (**2026-06-29**, the first ledger
date) — is **Tier 1: look, don't tune.**

- Sanctioned uses: settlement, monitoring, and pre-registered A/B comparison
  (e.g. overlay vs paper leg).
- NOT sanctioned: design iteration. Tuning a signal, threshold, or rule on
  Tier 1 data burns it as evidence, exactly as peeking burns a sealed test.
- The only door is `src/data_gate.load_operational()`, which validates source
  and shape and prints the standing Tier 1 notice on every load.
- Dates between the seal cutoff and the live-window start belong to the sealed
  holdout and are rejected by the operational door entirely.
- Generic OHLC panels are never Tier 1, regardless of date — post-cutoff OHLC
  is admissible only joined to specific rec dates for settlement.

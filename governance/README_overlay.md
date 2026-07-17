# Overlay log conventions

**CONVENTION (read first):** `overlay_log.csv` is append-only. Corrections are
NEW rows with the same `rec_key` and the reason prefixed `correction:` — never
edits. Analysis takes the LAST row per `rec_key` (file order).

## rec_key format (RULING 1, branch 2 — versioning found)

```
data_date|SYMBOL|seq        e.g.  2026-06-25|PAGEIND|4
```

- `data_date` — the rec file's data date (first date in the filename).
- `SYMBOL` — NSE symbol exactly as in the rec file.
- `seq` — 1-based ordinal of that data date's generation, ordered by the
  generated-date in the filename. Most days have exactly one generation →
  `seq=1`. Re-issued days count up (data 2026-06-25 had generations
  06-25, 06-27, 06-28, 06-29, 06-30, 07-01 → seq 1..6).
- Rows keyed from `trades_log.csv` (no generation recorded) use `seq=1`.

Why not a native ID: none exists in the system's outputs (verified across all
rec CSV headers and the picks_log schema). Why seq: the same data_date+symbol
recurs across generations with different content, so `date|symbol` alone
collides; the generation ordinal disambiguates.

## Logging

Source `scripts/overlay.sh` from `.zshrc`, then at decision time:

```sh
overlay '2026-07-17|AJANTPHARM|1' EXECUTE 1 clean setup, taking it
overlay '2026-07-17|PRESTIGE|1'  VETO    0 results overhang
overlay '2026-07-17|PRESTIGE|1'  VETO    0 correction: meant REDUCE not VETO
```

`ts_local` is stamped automatically. `executed_size` is the fraction of the
one-slot SOP size (1 = full slot, 0 = veto, 0<x<1 = reduce). Never size up: the
overlay is execute / veto / reduce only.

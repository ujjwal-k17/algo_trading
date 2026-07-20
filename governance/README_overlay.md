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

**Setup (required, and the reason 21 days produced zero rows):** `overlay.sh`
must actually be sourced. Add to `~/.zshrc`:

```sh
source ~/alpha-research/scripts/overlay.sh
```

Without this line the `overlay` command does not exist in the shell.

## The daily queue: `overlay_today`

```sh
overlay_today                 # today's recs, unlogged ones flagged
overlay_today --all           # every unlogged rec in the live window
overlay_today --commands      # paste-able command lines only
overlay_today --date 2026-07-17
```

Prints, per rec, ONLY what was knowable at decision time — rec_key, symbol,
dates, reference close, stop, targets — plus a ready-to-paste
`overlay '<rec_key>' ...` line, so the rec_key is never hand-built. Then the
backlog: how many live-window recs exist and how many are still unlogged.

**Outcome-blind by construction** (`src/overlay_queue.py`). Settled results
would contaminate the decision being logged — the overlay's discretionary skill
is the thing under measurement. Two structural defences, not conventions: only
rec-file columns are ever read (`paper_leg*.parquet` and `trades_log.csv` are
never opened), and `assert_outcome_blind` raises on any outcome-ish column
reaching the display path. Recs load through `data_gate.load_operational`.

`overlay_today` is read-only and idempotent. It NEVER writes the log.

### Back-logging past recs is not decision-time evidence

The backlog counts past unlogged recs for honesty about the hole's size, not as
a to-do list. A decision entered days later is recollection, and AB_PREREG
analyses 2-4 admit the DECISION_TIME scope only. If you log one from memory,
say so in the reason.

## Validation enforced by `overlay`

rec_key shape (`YYYY-MM-DD|SYMBOL|seq`, integer seq); verb in
EXECUTE/VETO/REDUCE; `executed_size` numeric in 0..1 (>1 rejected as sizing
up); verb/size coherence (EXECUTE=1, VETO=0, REDUCE strictly between);
non-empty reason. A malformed rec_key silently fails to join in
`overlay_alpha` — it would look like a MISSING decision rather than a broken
one — hence the door check.

Re-logging a rec_key that already has a decision is **blocked** unless the
reason starts with `correction:`. Analysis takes the LAST row, so an accidental
double entry would silently override a real decision.

## Recommended: a daily reminder (NOT installed — operator's call)

Nothing prompts the decision today. A LaunchAgent modelled on `com.alpha.ingest`
would post the queue every morning. To install:

1. Write `~/Library/LaunchAgents/com.alpha.overlay.reminder.plist` with Label
   `com.alpha.overlay.reminder`, ProgramArguments
   `/bin/sh -c '$HOME/alpha-research/.venv/bin/python
   $HOME/alpha-research/scripts/overlay_today.py'`,
   `StartCalendarInterval` around 09:00 IST (before the entry window, well
   clear of the 01:00 ingest), and StandardOutPath
   `$HOME/alpha-research/data/derived/overlay_reminder.log`.
2. `launchctl load ~/Library/LaunchAgents/com.alpha.overlay.reminder.plist`
3. Verify: `launchctl list | grep overlay` shows exit status 0.

A log file alone is easy to ignore; consider piping to `terminal-notifier` or
having it write to a file you already open daily.

**Caveat before relying on any agent:** `com.alpha.ingest` currently exits
**23** — launchd's rsync lacks Full Disk Access to `~/Desktop`, so nightly rec
ingest has been failing since 2026-07-18 (see `data/sealed/ingest.log`). A
reminder agent reading only the repo is unaffected, but the ingest fix is
prerequisite to the queue seeing current recs: add `/bin/sh` (and/or
`/usr/bin/rsync`) under System Settings → Privacy & Security → Full Disk
Access, then `launchctl kickstart -k gui/$(id -u)/com.alpha.ingest`.

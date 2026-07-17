#!/bin/sh
# Nightly snapshot of production output files (READ-ONLY source) into
# data/sealed/raw/YYYY-MM-DD/. Append-only: dated directories are never
# revisited on later days, and --ignore-existing never overwrites a file
# that already exists in today's snapshot (idempotent per day).
#
# Scope per RULING 3 (governance/DECISIONS.md): recommendations, fills/ledger
# exports, entry verdicts, daily assessment, macro scores. Excludes logs,
# configs, code, credentials/token files, charts, PDFs, backtest artifacts,
# raw OHLC panels, and any *.db/*.sqlite live database file.
set -eu

SRC="${INGEST_SRC:-/Users/ujjwalkejriwal/Desktop/AI Apps/NSE_Stock_Picks/output}"
DEST_ROOT="${INGEST_DEST_ROOT:-$HOME/alpha-research/data/sealed/raw}"
DAY="${INGEST_DAY:-$(date +%F)}"
DEST="$DEST_ROOT/$DAY"

mkdir -p "$DEST"

rsync -a --ignore-existing \
    --exclude="*.db" --exclude="*.sqlite*" \
    --include="top5_report*.csv" --include="top5_report*.md" \
    --include="top20_*.csv" \
    --include="candle_verdicts_*.json" \
    --include="trades_log.csv" \
    --include="open_positions_migrated_*.csv" \
    --include="daily_assessment.md" \
    --include="macro_context.json" \
    --include="prices_eod_backup_*.csv" \
    --include="nifty_backup_*.csv" \
    --exclude="*" \
    "$SRC/" "$DEST/"

echo "[ingest] $(ls "$DEST" | wc -l | tr -d ' ') files in $DEST"

# Independent OHLC + actions fetch (amended RULING 2) — after the rsync step.
# INGEST_SKIP_FETCH=1 skips it (tests exercise the rsync stage in isolation).
if [ -z "${INGEST_SKIP_FETCH:-}" ] && [ -n "${HOME:-}" ]; then
    "$HOME/alpha-research/.venv/bin/python" "$HOME/alpha-research/src/fetch_ohlc.py" \
        || echo "[ingest] WARNING: OHLC fetch failed (rsync snapshot unaffected)"
fi

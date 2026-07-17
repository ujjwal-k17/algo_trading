# scripts/overlay.sh — overlay decision logger. Source from .zshrc:
#   source ~/alpha-research/scripts/overlay.sh
#
# Usage:
#   overlay '<rec_key>' <EXECUTE|VETO|REDUCE> <executed_size> <reason...>
#   e.g. overlay '2026-07-17|AJANTPHARM|1' VETO 0 earnings tomorrow, skipping
#
# rec_key format (RULING 1): data_date|SYMBOL|seq  — seq is the 1-based ordinal
# of that data date's generation (see governance/README_overlay.md).
#
# NOTE: validating executed_size against the rec's size is NOT this function's
# job — rec size is deliberately not in this log (minimal 5-column schema);
# size-vs-rec checks happen downstream in overlay-alpha analysis.

overlay() {
    local log="${OVERLAY_LOG:-$HOME/alpha-research/governance/overlay_log.csv}"
    if [ "$#" -lt 4 ]; then
        echo "usage: overlay '<rec_key>' <EXECUTE|VETO|REDUCE> <executed_size> <reason...>" >&2
        return 1
    fi
    local rec_key="$1" decision="$2" size="$3"
    shift 3
    local reason="$*"

    case "$decision" in
        EXECUTE|VETO|REDUCE) ;;
        *)  echo "overlay: invalid decision '$decision' (must be EXECUTE, VETO, or REDUCE)" >&2
            return 1 ;;
    esac
    if [ ! -f "$log" ]; then
        echo "overlay: log not found at $log" >&2
        return 1
    fi

    local ts
    ts=$(date "+%Y-%m-%d %H:%M:%S")
    # CSV-quote fields that may contain commas/quotes (reason, rec_key is safe).
    local quoted_reason="\"${reason//\"/\"\"}\""
    printf '%s,%s,%s,%s,%s\n' "$ts" "$rec_key" "$decision" "$size" "$quoted_reason" >> "$log"
    tail -n 1 "$log"
}

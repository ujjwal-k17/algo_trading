# scripts/overlay.sh — overlay decision logger. Source from .zshrc:
#   source ~/alpha-research/scripts/overlay.sh
#
# Usage:
#   overlay '<rec_key>' <EXECUTE|VETO|REDUCE> <executed_size> <reason...>
#   e.g. overlay '2026-07-17|AJANTPHARM|1' VETO 0 earnings tomorrow, skipping
#
#   overlay_today [args...]   — what still needs a decision, with ready-to-paste
#                               command lines. Read-only; never writes the log.
#
# rec_key format (RULING 1): data_date|SYMBOL|seq  — seq is the 1-based ordinal
# of that data date's generation (see governance/README_overlay.md).
#
# NOTE: validating executed_size against the rec's size is NOT this function's
# job — rec size is deliberately not in this log (minimal 5-column schema);
# size-vs-rec checks happen downstream in overlay-alpha analysis. What IS
# validated here: rec_key shape, decision verb, size range and verb/size
# coherence, non-empty reason, and the append-only correction convention.

ALPHA_RESEARCH="${ALPHA_RESEARCH:-$HOME/alpha-research}"

overlay() {
    local log="${OVERLAY_LOG:-$ALPHA_RESEARCH/governance/overlay_log.csv}"
    if [ "$#" -lt 4 ]; then
        echo "usage: overlay '<rec_key>' <EXECUTE|VETO|REDUCE> <executed_size> <reason...>" >&2
        return 1
    fi
    local rec_key="$1" decision="$2" size="$3"
    shift 3
    local reason="$*"

    # rec_key shape: YYYY-MM-DD|SYMBOL|seq. A malformed key silently fails to
    # join in overlay_alpha, which looks like a MISSING decision rather than a
    # broken one — so reject it at the door.
    case "$rec_key" in
        [0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]\|*\|*) ;;
        *)  echo "overlay: malformed rec_key '$rec_key' (want data_date|SYMBOL|seq, e.g. 2026-07-17|AJANTPHARM|1)" >&2
            echo "overlay: run 'overlay_today' for exact keys — never hand-build them" >&2
            return 1 ;;
    esac
    local sym="${rec_key#*|}"; sym="${sym%%|*}"
    local seq="${rec_key##*|}"
    if [ -z "$sym" ]; then
        echo "overlay: rec_key has an empty SYMBOL field" >&2
        return 1
    fi
    case "$seq" in
        ''|*[!0-9]*) echo "overlay: rec_key seq '$seq' must be a positive integer" >&2; return 1 ;;
    esac

    case "$decision" in
        EXECUTE|VETO|REDUCE) ;;
        *)  echo "overlay: invalid decision '$decision' (must be EXECUTE, VETO, or REDUCE)" >&2
            return 1 ;;
    esac

    # executed_size: numeric, 0..1 inclusive. Above 1 would be sizing UP, which
    # the overlay protocol forbids outright (execute / veto / reduce only).
    case "$size" in
        ''|*[!0-9.]*|*.*.*) echo "overlay: executed_size '$size' is not a number" >&2; return 1 ;;
    esac
    if ! awk -v s="$size" 'BEGIN{exit !(s>=0 && s<=1)}' </dev/null; then
        echo "overlay: executed_size '$size' out of range — must be 0..1 (never size up)" >&2
        return 1
    fi
    # Verb/size coherence (governance/README_overlay.md): 1 = full slot,
    # 0 = veto, 0<x<1 = reduce. An incoherent pair corrupts analyses 3 and 4.
    case "$decision" in
        EXECUTE) awk -v s="$size" 'BEGIN{exit !(s==1)}' </dev/null || {
            echo "overlay: EXECUTE requires executed_size 1 (use REDUCE for a partial)" >&2; return 1; } ;;
        VETO)    awk -v s="$size" 'BEGIN{exit !(s==0)}' </dev/null || {
            echo "overlay: VETO requires executed_size 0" >&2; return 1; } ;;
        REDUCE)  awk -v s="$size" 'BEGIN{exit !(s>0 && s<1)}' </dev/null || {
            echo "overlay: REDUCE requires 0 < executed_size < 1 (0 is VETO, 1 is EXECUTE)" >&2; return 1; } ;;
    esac

    # Reason is the only field recording WHY. Blank reasons make analyses 3-4
    # uninterpretable after the fact.
    case "$reason" in
        *[!\ ]*) ;;
        *) echo "overlay: reason must not be empty" >&2; return 1 ;;
    esac

    if [ ! -f "$log" ]; then
        echo "overlay: log not found at $log" >&2
        echo "overlay: expected the header-only log in governance/ — do not create one ad hoc" >&2
        return 1
    fi

    # Append-only convention (governance/README_overlay.md): corrections are NEW
    # rows with the reason prefixed 'correction:'. Re-logging the same key
    # without that prefix is almost always an accidental double entry — and
    # since analysis takes the LAST row, it would silently override a real
    # decision. Block it and make the correction explicit.
    if grep -q "^[^,]*,$rec_key," "$log" 2>/dev/null; then
        case "$reason" in
            correction:*) ;;
            *)  echo "overlay: '$rec_key' already has a logged decision:" >&2
                grep "^[^,]*,$rec_key," "$log" | tail -n 1 >&2
                echo "overlay: to change it, log a NEW row with the reason prefixed 'correction:'" >&2
                echo "overlay:   overlay '$rec_key' $decision $size correction: <why>" >&2
                return 1 ;;
        esac
    fi

    local ts
    ts=$(date "+%Y-%m-%d %H:%M:%S")
    # CSV-quote fields that may contain commas/quotes (reason, rec_key is safe).
    local quoted_reason="\"${reason//\"/\"\"}\""
    printf '%s,%s,%s,%s,%s\n' "$ts" "$rec_key" "$decision" "$size" "$quoted_reason" >> "$log"
    tail -n 1 "$log"
}

# Read-only queue view. Never writes the log.
overlay_today() {
    "$ALPHA_RESEARCH/.venv/bin/python" "$ALPHA_RESEARCH/scripts/overlay_today.py" "$@"
}

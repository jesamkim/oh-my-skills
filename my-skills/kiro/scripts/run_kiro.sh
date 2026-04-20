#!/usr/bin/env bash
# run_kiro.sh - Kiro CLI wrapper for non-interactive task delegation
# Strips ANSI escape codes, handles timeouts, and returns clean output.

set -euo pipefail

KIRO_BIN="/Applications/Kiro CLI.app/Contents/MacOS/kiro-cli"
DEFAULT_MODEL="claude-opus-4.6-1m"
DEFAULT_TIMEOUT=300
TRUST_ALL=false
MODEL=""
TIMEOUT=""

usage() {
    cat <<'EOF'
Usage: run_kiro.sh [OPTIONS] "prompt"

Options:
  --timeout SEC    Max seconds to wait (default: 300)
  --trust-all      Auto-approve all tool usage (-a flag)
  --model MODEL    Override default model (default: claude-opus-4.6-1m)
  --help           Show this help

Examples:
  run_kiro.sh "Summarize /path/to/file.md"
  run_kiro.sh --trust-all "Read and analyze /path/to/project/"
  run_kiro.sh --timeout 600 --model claude-sonnet-4.5 "Quick task"
  cat file.txt | run_kiro.sh "Summarize the piped content"
EOF
    exit 0
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        --timeout)
            TIMEOUT="$2"
            shift 2
            ;;
        --trust-all)
            TRUST_ALL=true
            shift
            ;;
        --model)
            MODEL="$2"
            shift 2
            ;;
        --help)
            usage
            ;;
        -*)
            echo "Error: Unknown option $1" >&2
            exit 1
            ;;
        *)
            PROMPT="$1"
            shift
            ;;
    esac
done

# Use defaults if not set
TIMEOUT="${TIMEOUT:-$DEFAULT_TIMEOUT}"
MODEL="${MODEL:-$DEFAULT_MODEL}"

# Check if prompt was provided
if [[ -z "${PROMPT:-}" ]]; then
    # Check for piped input
    if [[ ! -t 0 ]]; then
        PIPED_INPUT=$(cat)
        echo "Error: No prompt provided. Pipe content detected but a prompt argument is still required." >&2
        echo "Usage: cat file.txt | run_kiro.sh \"Summarize this\"" >&2
        exit 1
    fi
    echo "Error: No prompt provided." >&2
    usage
fi

# If stdin has piped content, prepend it to the prompt
if [[ ! -t 0 ]]; then
    PIPED_INPUT=$(cat)
    PROMPT="$PIPED_INPUT

---
$PROMPT"
fi

# Check kiro binary exists
if [[ ! -x "$KIRO_BIN" ]]; then
    echo "Error: Kiro CLI not found at $KIRO_BIN" >&2
    echo "Install Kiro from https://kiro.dev" >&2
    exit 1
fi

# Build command
CMD=("$KIRO_BIN" chat --no-interactive --model "$MODEL")

if [[ "$TRUST_ALL" == "true" ]]; then
    CMD+=(-a)
fi

CMD+=("$PROMPT")

# Determine timeout command (macOS uses gtimeout from coreutils, Linux uses timeout)
if command -v gtimeout &>/dev/null; then
    TIMEOUT_CMD="gtimeout"
elif command -v timeout &>/dev/null; then
    TIMEOUT_CMD="timeout"
else
    TIMEOUT_CMD=""
fi

# Run kiro (with timeout if available)
if [[ -n "$TIMEOUT_CMD" ]]; then
    if OUTPUT=$("$TIMEOUT_CMD" "$TIMEOUT" "${CMD[@]}" 2>&1); then
        EXIT_CODE=0
    else
        EXIT_CODE=$?
    fi
else
    # No timeout command available — run without timeout
    if OUTPUT=$("${CMD[@]}" 2>&1); then
        EXIT_CODE=0
    else
        EXIT_CODE=$?
    fi
fi

# Strip ANSI escape codes, kiro UI chrome, and clean up output
CLEAN_OUTPUT=$(echo "$OUTPUT" | sed \
    -e 's/\x1b\[[0-9;]*[a-zA-Z]//g' \
    -e 's/\x1b\][0-9]*;[^\x07]*\x07//g' \
    -e 's/\x1b\[?[0-9]*[a-zA-Z]//g' \
    -e 's/\x1b(B//g' \
    -e 's/\x0f//g' \
    -e 's/\r//g' \
    -e '/^[[:space:]]*$/d' \
    -e '/^[[:space:]]*▸ Credits:/d' \
    -e '/Checkpoints are enabled/d' \
    -e '/^> $/d' \
    -e 's/^> //' \
    -e '/Reading file:.*using tool: read/d' \
    -e '/✓ Successfully read/d' \
    -e '/Completed in [0-9]/d')

echo "$CLEAN_OUTPUT"

if [[ $EXIT_CODE -eq 124 ]]; then
    echo "" >&2
    echo "Error: Kiro timed out after ${TIMEOUT}s" >&2
    exit 124
elif [[ $EXIT_CODE -ne 0 ]]; then
    echo "" >&2
    echo "Error: Kiro exited with code $EXIT_CODE" >&2
    exit "$EXIT_CODE"
fi

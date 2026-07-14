#!/usr/bin/env bash
# run_kiro.sh - Kiro CLI wrapper for non-interactive task delegation.
#
# Runs `kiro-cli chat --no-interactive`, strips terminal chrome (ANSI codes,
# the OSC "Response complete" marker, and the leading "> " prefix), enforces a
# timeout when one is available, and returns clean text on stdout.
#
# Verified against kiro-cli 2.12.1 (2026-07):
#   - Default model is `auto` (1.00x credits, task-routed). We pass `auto` so
#     the skill follows the CLI's own default instead of pinning a pricey model.
#   - Chat answers always print as styled terminal text on STDOUT even when
#     piped; there is no JSON output mode for chat. We de-chrome with perl
#     because macOS ships BSD sed, which does NOT understand \x1b hex escapes.
#   - The credits/time trailer and MCP/checkpoint banners go to STDERR, so we
#     keep the streams separate and only clean stdout.

set -euo pipefail

# --- Binary resolution -------------------------------------------------------
# macOS default app path first, then PATH, then KIRO_BIN override.
KIRO_BIN="${KIRO_BIN:-/Applications/Kiro CLI.app/Contents/MacOS/kiro-cli}"
if [[ ! -x "$KIRO_BIN" ]]; then
    if command -v kiro-cli &>/dev/null; then
        KIRO_BIN="$(command -v kiro-cli)"
    fi
fi

# --- Defaults ----------------------------------------------------------------
# `auto` mirrors the CLI default (1.00x credits, picks a model per task). Pin a
# specific model with --model only when you need determinism.
DEFAULT_MODEL="auto"
DEFAULT_TIMEOUT=300

MODEL=""
TIMEOUT=""
EFFORT=""
AGENT=""
TRUST_MODE="read"      # read | all | none | custom
TRUST_TOOLS=""         # explicit allowlist when TRUST_MODE=custom
PROMPT=""

usage() {
    cat <<'EOF'
Usage: run_kiro.sh [OPTIONS] "prompt"

Delegate a task to Kiro CLI in non-interactive mode and return clean output.

Options:
  --model MODEL      Model to use (default: auto = CLI default, 1.00x credits).
                     Examples: claude-opus-4.8, claude-sonnet-4.6, claude-haiku-4.5
  --effort LEVEL     Reasoning effort: low|medium|high|xhigh|max
                     (only models exposing reasoning effort honor this)
  --agent NAME       Use a custom/built-in agent (e.g. code-reviewer, kiro_planner)
  --timeout SEC      Max seconds to wait (default: 300; needs coreutils timeout/gtimeout)
  --trust read       Allow read-only tools (fs_read) [DEFAULT - safe]
  --trust all        Auto-approve ALL tools (-a). Use only when writes are intended.
  --trust none       Trust no tools (pure text/analysis, no file access)
  --trust-tools LIST Explicit comma-separated allowlist, e.g. fs_read,execute_bash
                     (MCP/custom tools must be namespaced: @server/tool)
  --help             Show this help

Examples:
  run_kiro.sh "Summarize /abs/path/to/file.md"
  run_kiro.sh --trust none "Explain the tradeoffs of optimistic locking"
  run_kiro.sh --trust all "Read and refactor /abs/path/to/project/"
  run_kiro.sh --effort high --model claude-opus-4.8 "Hard reasoning task"
  run_kiro.sh --agent code-reviewer --trust read "Review /abs/path/to/file.py"
  git diff | run_kiro.sh "Review these staged changes for bugs"

Notes:
  - Kiro starts with ZERO context. Put everything it needs (absolute paths,
    instructions, expected output format) into the prompt itself.
  - In-chat slash commands like /goal and /plan are INTERACTIVE-ONLY and do not
    work here. To get goal-style iterate-until-verified behavior, phrase it in
    the prompt (see run_kiro_review.sh for a worked example).
EOF
    exit 0
}

# --- Argument parsing ---------------------------------------------------------
# require_arg NAME: ensure the current flag has a following value (friendlier
# than the bare "unbound variable" error that `set -u` would otherwise emit).
require_arg() {
    if [[ $# -lt 2 || "$2" == -* ]]; then
        echo "Error: $1 requires an argument" >&2
        exit 1
    fi
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --model)       require_arg "$@"; MODEL="$2"; shift 2 ;;
        --effort)      require_arg "$@"; EFFORT="$2"; shift 2 ;;
        --agent)       require_arg "$@"; AGENT="$2"; shift 2 ;;
        --timeout)     require_arg "$@"; TIMEOUT="$2"; shift 2 ;;
        --trust)       require_arg "$@"; TRUST_MODE="$2"; shift 2 ;;
        --trust-tools) require_arg "$@"; TRUST_MODE="custom"; TRUST_TOOLS="$2"; shift 2 ;;
        --help)        usage ;;
        --)            shift; PROMPT="${1:-}"; shift || true; break ;;
        -*)            echo "Error: Unknown option $1" >&2; exit 1 ;;
        *)             PROMPT="$1"; shift ;;
    esac
done

TIMEOUT="${TIMEOUT:-$DEFAULT_TIMEOUT}"
MODEL="${MODEL:-$DEFAULT_MODEL}"

# --- Stdin (piped context) handling ------------------------------------------
# If content is piped in, read it ONCE and prepend it to the prompt. We must
# read stdin before validating the prompt, but only consume it when it is
# actually a pipe (not an interactive TTY).
PIPED_INPUT=""
if [[ ! -t 0 ]]; then
    PIPED_INPUT="$(cat)"
fi

if [[ -z "${PROMPT:-}" ]]; then
    if [[ -n "$PIPED_INPUT" ]]; then
        echo "Error: Pipe content detected but a prompt argument is still required." >&2
        echo "Usage: cat file.txt | run_kiro.sh \"Summarize this\"" >&2
        exit 1
    fi
    echo "Error: No prompt provided." >&2
    usage
fi

if [[ -n "$PIPED_INPUT" ]]; then
    PROMPT="$PIPED_INPUT

---
$PROMPT"
fi

# --- Binary existence check ---------------------------------------------------
if [[ ! -x "$KIRO_BIN" ]]; then
    echo "Error: Kiro CLI not found at '$KIRO_BIN'." >&2
    echo "Install Kiro from https://kiro.dev or set KIRO_BIN=/path/to/kiro-cli" >&2
    exit 1
fi

# --- Build command -----------------------------------------------------------
CMD=("$KIRO_BIN" chat --no-interactive --model "$MODEL")
[[ -n "$EFFORT" ]] && CMD+=(--effort "$EFFORT")
[[ -n "$AGENT" ]] && CMD+=(--agent "$AGENT")

case "$TRUST_MODE" in
    all)    CMD+=(--trust-all-tools) ;;
    none)   CMD+=(--trust-tools=) ;;
    custom) CMD+=(--trust-tools="$TRUST_TOOLS") ;;
    read|*) CMD+=(--trust-tools=fs_read) ;;
esac

CMD+=("$PROMPT")

# --- Timeout command detection (optional) ------------------------------------
TIMEOUT_CMD=""
if command -v gtimeout &>/dev/null; then
    TIMEOUT_CMD="gtimeout"
elif command -v timeout &>/dev/null; then
    TIMEOUT_CMD="timeout"
fi

# --- Run ----------------------------------------------------------------------
# Capture stdout (the answer) and stderr (banners + the credits/time trailer +
# any real error like auth/model/MCP failures) SEPARATELY. We keep them apart so
# stderr chrome doesn't pollute the clean answer, but we must NOT discard stderr:
# on failure it carries the only diagnostic. So stderr goes to a temp file and is
# surfaced to the caller only when the run fails.
ERR_FILE="$(mktemp "${TMPDIR:-/tmp}/run_kiro_err.XXXXXX")"
cleanup() { rm -f "$ERR_FILE"; }
trap cleanup EXIT

set +e
if [[ -n "$TIMEOUT_CMD" ]]; then
    OUTPUT="$("$TIMEOUT_CMD" "$TIMEOUT" "${CMD[@]}" 2>"$ERR_FILE")"
    EXIT_CODE=$?
else
    OUTPUT="$("${CMD[@]}" 2>"$ERR_FILE")"
    EXIT_CODE=$?
fi

# --- De-chrome the output -----------------------------------------------------
# perl handles the escape sequences portably (BSD sed on macOS does NOT
# understand \x1b/\x07 hex escapes and would leave the codes intact):
#   1. OSC sequences: ESC ] ... BEL   (e.g. the "Response complete" marker)
#   2. CSI/SGR sequences: ESC [ ... letter   (colors, cursor moves)
#   3. misc one-shots: ESC ( B, SI (0x0f)
#   4. carriage returns
# Then drop spinner/checkpoint/credits chrome lines and strip the leading "> ".
# This pipeline stays inside the `set +e` region so a perl/sed hiccup can never
# mask Kiro's real exit code below.
CLEAN_OUTPUT="$(printf '%s\n' "$OUTPUT" | perl -pe '
    s/\e\][0-9;]*;[^\a\e]*(?:\a|\e\\)//g;   # OSC ... BEL or ST
    s/\e\][0-9;]*[^\a\e]*(?:\a|\e\\)//g;     # OSC variants
    s/\e\[[0-9;?]*[ -\/]*[@-~]//g;           # CSI / SGR
    s/\e\(B//g;                              # charset select
    s/\x0f//g;                               # shift-in
    s/\r//g;
' | sed \
    -e '/^[[:space:]]*$/d' \
    -e '/^[[:space:]]*▸ Credits:/d' \
    -e '/Checkpoints are enabled/d' \
    -e '/Checkpoints are not available/d' \
    -e '/^> $/d' \
    -e 's/^> //' \
    -e '/using tool: read)/d' \
    -e '/^ ✓ Successfully read/d' \
    -e '/^ - Completed in [0-9]/d')"
set -e

printf '%s\n' "$CLEAN_OUTPUT"

# --- Exit-code handling -------------------------------------------------------
# kiro-cli: 0 ok; 1 general (auth/invalid model); 2 arg-parse; 3 MCP startup;
# 124 = timeout killed it. On failure, surface Kiro's captured stderr so the
# caller sees the actual cause (auth expired, unknown model, MCP down) instead
# of a bare exit code.
emit_stderr() {
    if [[ -s "$ERR_FILE" ]]; then
        echo "--- Kiro stderr ---" >&2
        # De-chrome stderr too so the diagnostic is readable.
        perl -pe 's/\e\][0-9;]*[^\a\e]*(?:\a|\e\\)//g; s/\e\[[0-9;?]*[ -\/]*[@-~]//g; s/\r//g;' "$ERR_FILE" >&2
    fi
}
if [[ $EXIT_CODE -eq 124 ]]; then
    echo "" >&2
    echo "Error: Kiro timed out after ${TIMEOUT}s" >&2
    emit_stderr
    exit 124
elif [[ $EXIT_CODE -ne 0 ]]; then
    echo "" >&2
    echo "Error: Kiro exited with code $EXIT_CODE" >&2
    emit_stderr
    exit "$EXIT_CODE"
fi

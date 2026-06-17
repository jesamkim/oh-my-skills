---
name: kiro
description: |
  Delegate tasks to Kiro CLI (kiro-cli) when Claude Code's context window is
  insufficient or when you need an independent AI session for isolated analysis,
  a second opinion, or a specialized CODE REVIEW. Runs Kiro non-interactively,
  strips terminal chrome, and returns clean results. Two modes: (1) general
  delegation for large-document analysis, summarization, and fresh-context work;
  (2) a code-review specialization (like the codex skill) that auto-detects git
  scope, runs an adversarial read-only review, and returns findings with
  file:line and a ship/no-ship verdict. Use whenever context is running low,
  when a subagent would exceed token limits, when you want an unbiased review of
  changes, or when the user asks to use Kiro.
  Triggers: "kiro", "kiro로", "kiro 한테", "kiro 리뷰", "kiro review",
  "context 부족", "context window", "delegate to kiro", "ask kiro", "run kiro",
  "code review with kiro", "키로", "키로로 리뷰".
license: MIT License
metadata:
  skill-author: Jesam Kim
  version: 2.0.0
allowed-tools: [Bash, Read, Write, Glob, Grep]
---

# Kiro CLI Delegation Skill

Delegate work to **Kiro CLI** (`kiro-cli`, the rebranded Amazon Q Developer CLI;
`q` is aliased to it) when Claude Code's context window is running low, when you
need an independent AI session for isolated analysis, or when you want a
specialized **code review** of pending changes.

Two modes:

1. **General delegation** (`scripts/run_kiro.sh`) - run any task in Kiro's fresh
   context and get clean text back.
2. **Code review** (`scripts/run_kiro_review.sh`) - an adversarial, read-only
   review specialization (analogous to the codex skill's review), with git-scope
   auto-detection and a ship/no-ship verdict.

## How It Works

Kiro CLI runs in **non-interactive (headless) mode** - you send a prompt, it
processes the task in a completely separate context window, and returns the
result. Because Kiro has its own context (separate from Claude Code), it can
handle work that would otherwise exceed your remaining budget, and it gives an
unbiased second opinion.

The wrapper scripts handle the messy parts: resolving the binary, enforcing a
timeout, choosing a safe tool-trust level, and **stripping terminal chrome**
(ANSI color codes, the OSC "Response complete" marker, the leading `> ` prefix)
so you get clean text. Output de-chroming uses `perl`, not `sed`, because macOS
ships BSD `sed` which does not understand `\x1b` hex escapes.

## Kiro CLI Configuration

```yaml
Binary (macOS): /Applications/Kiro CLI.app/Contents/MacOS/kiro-cli
Binary (Linux): kiro-cli on PATH (e.g. /usr/bin/kiro-cli)
Binary override: KIRO_BIN=/custom/path bash run_kiro.sh "..."
Mode: chat --no-interactive
Default model: auto   # the CLI's own default: task-routed, 1.00x credits
```

**Model choice matters (verified on kiro-cli 2.7.x).** The real CLI default is
`auto` (1.00x credits, picks a model per task). The scripts follow that default.
Pin a model with `--model` only when you need determinism or a specific tier:

| Model | Credits | When to use |
|-------|---------|-------------|
| `auto` (default) | 1.00x | Most delegations; let Kiro route |
| `claude-haiku-4.5` | 0.40x | Cheap, fast summaries / simple checks |
| `claude-sonnet-4.6` | 1.30x | Balanced analysis, 1M context |
| `claude-opus-4.8` | 2.20x | Hardest reasoning / deep reviews |

Do **not** hardcode `claude-opus-4.8` for routine work - it is 2.2x credits.

## Mode 1: General Delegation

### Basic Invocation

```bash
bash <SKILL_DIR>/scripts/run_kiro.sh "Your prompt here"
```

The default trust level is **read-only** (`fs_read`): Kiro can read files but
cannot modify anything. This is the safe default for analysis and summarization.

### Options

```bash
# Trust levels (pick the least privilege the task needs):
bash run_kiro.sh --trust none "Explain the CAP theorem tradeoffs"      # no file access
bash run_kiro.sh --trust read "Summarize /abs/path/to/doc.md"          # read-only (default)
bash run_kiro.sh --trust all  "Refactor /abs/path/to/project/"         # writes allowed (-a)
bash run_kiro.sh --trust-tools "fs_read,execute_bash" "Run the tests and explain failures"

# Reasoning depth (models that expose effort honor this):
bash run_kiro.sh --effort high  "Reason carefully about this race condition"
bash run_kiro.sh --effort xhigh --model claude-opus-4.8 "Hardest analysis"

# Model + timeout:
bash run_kiro.sh --model claude-sonnet-4.6 --timeout 600 "Analyze this large codebase"

# Use a custom or built-in agent:
bash run_kiro.sh --agent kiro_planner "Break this idea into an implementation plan"

# Pipe context in (prepended to the prompt):
git diff | bash run_kiro.sh "Review these changes for correctness"
cat /abs/path/big.md | bash run_kiro.sh "Summarize this document in 5 bullets"
```

### When to Use General Delegation

| Scenario | Why Kiro Helps |
|----------|----------------|
| Context window running low | Kiro has its own fresh context |
| Large file analysis (>1000 lines) | Dedicated context for the full file |
| Document summarization | Read and summarize in isolation |
| Second opinion on a design | Separate AI session = unbiased view |
| Parallel independent analysis | Multiple kiro calls can run concurrently |

## Mode 2: Code Review (Specialization)

`scripts/run_kiro_review.sh` delegates an **adversarial, read-only** code review
to Kiro - the same role the codex skill plays, but through Kiro's context. It
detects what to review from git state, feeds a skeptical reviewer prompt
(`assets/prompts/adversarial-review.md`), and returns findings with `file:line`,
severity, a concrete fix each, and a final `VERDICT: ship | no-ship`.

```bash
# Auto-detect scope from git (branch diff if ahead of base, else working tree):
bash <SKILL_DIR>/scripts/run_kiro_review.sh

# Explicit scopes:
bash run_kiro_review.sh --scope working-tree                 # staged+unstaged+untracked
bash run_kiro_review.sh --scope branch --base origin/develop # this branch vs base
bash run_kiro_review.sh -- src/payments/ src/auth/handler.ts # explicit paths

# Tuning:
bash run_kiro_review.sh --focus "concurrency and the retry path"
bash run_kiro_review.sh --json     # also emit a machine-readable JSON findings block
bash run_kiro_review.sh --model claude-opus-4.8 --effort max   # deepest review
```

**Key properties (mirrors the codex review contract):**

- **Review-only.** It reports findings; it does not fix, patch, stage, or commit.
  Hand the findings back to the main agent or the user to act on.
- **Read-only by construction.** The wrapper pre-computes the git diff/status and
  passes it as context, then runs Kiro with `fs_read` only. Kiro cannot run shell
  commands or modify files during the review.
- **Self-verifying (the `/goal` value, headless-safe).** The prompt tells Kiro to
  verify each finding against the real code (read the file, confirm the path,
  cite `file:line`) before reporting it - replicating the goal-driven,
  verify-before-complete behavior of the interactive `/goal` loop, which is not
  reachable in non-interactive mode (see "On `/goal`" below).
- **Both structured and verbatim.** By default you get human-readable findings;
  with `--json`, Kiro appends a JSON block (`verdict`, `summary`, `findings[]`).
  Return Kiro's output to the user **verbatim** - do not silently fix or
  paraphrase the findings.

**Optional persistent agent.** A schema-validated reviewer agent is bundled at
`assets/agents/code-reviewer.json`. Its own config constrains `execute_bash` to
read-only `git`/`grep`/inspection commands (via a `toolsSettings` denylist that
blocks `rm`/`mv`/`commit`/`push`/redirection/etc.), so it can run git and grep
during verification without being able to mutate files. To use it, copy it to
`~/.kiro/agents/` and set `KIRO_REVIEW_AGENT=code-reviewer`. When an agent is
used, the wrapper passes `--trust none` at the CLI and lets the agent's own
`allowedTools`/`toolsSettings` be the single source of truth for trust - so the
review never silently gets broader permission than the agent declares. Only use
this with the bundled `code-reviewer` (or an agent you have vetted as
read-only); pointing it at a write-capable agent would not be a read-only
review. The default path (no agent, `fs_read` only) needs no installation and
is the safest footing.

### Recommended review flow (for the main agent)

1. Estimate size first: `git status --short --untracked-files=all` and
   `git diff --shortstat` (and `--cached`). Treat untracked files as reviewable.
2. For a tiny change (~1-2 files) run in the foreground and wait. For anything
   larger or unclear, run via Claude Code's background Bash so you don't block.
3. Return the verdict and findings to the user verbatim. Do not act on them
   unless the user asks.

## On `/goal` and other interactive features (important)

kiro-cli 2.7.x added `/goal` - a goal-driven iterative agent loop that verifies
the task is done (with cited evidence) before completing. It is powerful, **but
`/goal` and other interactive slash commands (`/plan`, `/model` picker, `/agent`
picker, etc.) DO NOT work in `--no-interactive` mode** - they require a terminal
and will error or be ignored. This was verified empirically: passing
`/goal ...` as the headless input does nothing.

Because this skill's whole purpose is **non-interactive delegation**, it does not
call `/goal` directly. Instead:

- The **review mode replicates `/goal`'s value in the prompt** (iterate, verify
  each finding against real code, cite evidence before concluding).
- If a human wants the genuine interactive `/goal` loop, they run Kiro
  themselves: `kiro-cli chat` then `/goal <description> [--max N]`. Mention this
  to the user when an interactive autonomous loop is genuinely what they want;
  it is outside what this delegation skill drives.

Other 2.7.x capabilities the scripts expose where they help headless work:
`--effort`, `--agent`, granular `--trust-tools`, and the `auto` model default.
The KAS engine (`--v3` / `--agent-engine kas`) and `--mode spec|vibe` exist but
are interactive/IDE-oriented and not used by this delegation skill.

## Constructing Effective Prompts

Kiro starts with **zero context** - it has not seen your conversation. Put
everything it needs into the prompt itself.

**Good prompt pattern:**

```
Read the file /absolute/path/to/file.py and identify:
1. Bugs or logic errors
2. Security vulnerabilities (injection, authz gaps, secrets)
3. Performance issues

Report critical issues only, as a numbered list with file:line references and a
one-line fix each.
```

**Key principles:**

- Use **absolute paths** - Kiro may not share your working directory.
- Be **specific** about what you want; don't assume context.
- State the **output format** you expect.
- For multi-file tasks, list every relevant path explicitly.
- For structured output, ask Kiro to emit a fenced JSON or Markdown block
  (chat has no native JSON output mode; you ask for it in the prompt).

## Handling Results

- The wrapper returns clean text on stdout; progress/errors go to stderr.
- Exit codes: `0` ok; `1` general failure (auth, invalid model); `2` argument
  parse error; `3` MCP startup failure (only with `--require-mcp-startup`);
  `124` timeout. Always check the exit code; non-zero means the result is
  unreliable.
- For review results, return them to the user verbatim (do not fix silently).

## Limitations

- Kiro has no access to your current conversation context.
- Each invocation is stateless (no memory between calls) unless you use session
  resume (`--resume` / `--resume-id`), which is cwd-scoped.
- Interactive slash commands (`/goal`, `/plan`, pickers) are not available
  headless - see "On `/goal`" above.
- Requires Kiro CLI installed and authenticated (`kiro-cli login`, or
  `KIRO_API_KEY` for CI on a Pro plan).
- Network-dependent (Kiro calls its own backend).
- Timeout enforcement needs coreutils `timeout`/`gtimeout`; without it the
  script runs without a hard timeout.

## File Structure

```
kiro/
├── SKILL.md                          # This file
├── README.md                         # Human-facing overview
├── LICENSE
├── scripts/
│   ├── run_kiro.sh                   # General delegation wrapper
│   └── run_kiro_review.sh            # Code-review specialization
└── assets/
    ├── prompts/
    │   └── adversarial-review.md     # Reviewer prompt template
    └── agents/
        └── code-reviewer.json        # Optional persistent reviewer agent
```

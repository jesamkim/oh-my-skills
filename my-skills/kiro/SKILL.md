---
name: kiro
description: |
  Delegate tasks to Kiro CLI when Claude Code's context window is insufficient
  or when you need an independent AI session for isolated analysis. Runs Kiro
  in non-interactive mode with a specific prompt, captures the response, and
  returns clean results. Ideal for large document analysis, code QA across many
  files, summarization of lengthy content, or any task that benefits from a
  fresh context window. Use this skill whenever context is running low, when
  a subagent would exceed token limits, when you need a second opinion from
  a separate AI session, or when the user explicitly asks to use Kiro.
  Triggers: "kiro", "kiro로", "kiro 한테", "context 부족", "context window",
  "delegate to kiro", "ask kiro", "run kiro", "키로".
license: MIT License
metadata:
  skill-author: Jesam Kim
  version: 1.0.0
allowed-tools: [Bash, Read, Write, Glob, Grep]
---

# Kiro CLI Delegation Skill

Delegate specific tasks to Kiro CLI when Claude Code's context window is
running low or when an independent AI session is needed for isolated analysis.

## How It Works

Kiro CLI runs in **non-interactive mode** — you send a prompt, it processes the
task in a completely separate context, and returns the result. This is useful
because Kiro has its own context window (separate from Claude Code), so it can
handle tasks that would otherwise exceed your remaining context budget.

## Kiro CLI Configuration

```yaml
Binary: /Applications/Kiro CLI.app/Contents/MacOS/kiro-cli
Mode: chat --no-interactive
Default Model: claude-opus-4.6-1m
Default Agent: (kiro's built-in default agent)
```

## Usage

### Basic Invocation

Use the wrapper script for clean output:

```bash
bash <SKILL_DIR>/scripts/run_kiro.sh "Your prompt here"
```

### With Options

```bash
# Specify timeout (default: 300 seconds)
bash <SKILL_DIR>/scripts/run_kiro.sh --timeout 600 "Analyze this large codebase..."

# Trust all tools (auto-approve file reads, writes, etc.)
bash <SKILL_DIR>/scripts/run_kiro.sh --trust-all "Read and summarize all files in /path/to/docs/"

# Specify a different model
bash <SKILL_DIR>/scripts/run_kiro.sh --model claude-sonnet-4.5 "Quick summary of this file"

# Pipe file content as context
cat /path/to/large-file.md | bash <SKILL_DIR>/scripts/run_kiro.sh "Summarize this document"

# Combine options
bash <SKILL_DIR>/scripts/run_kiro.sh --trust-all --timeout 600 "QA review of /path/to/project/"
```

### Direct CLI Invocation (advanced)

If the wrapper script is not suitable, call kiro-cli directly:

```bash
"/Applications/Kiro CLI.app/Contents/MacOS/kiro-cli" chat \
  --no-interactive \
  --model claude-opus-4.6-1m \
  "Your prompt here"
```

Note: Direct invocation includes ANSI escape codes in output. The wrapper
script strips these automatically.

## When to Use This Skill

| Scenario | Why Kiro Helps |
|----------|----------------|
| Context window running low | Kiro has its own fresh context |
| Large file analysis (>1000 lines) | Dedicated context for the full file |
| QA / code review of many files | Independent review without polluting main context |
| Document summarization | Kiro can read and summarize in isolation |
| Second opinion on implementation | Separate AI session = unbiased analysis |
| Parallel independent analysis | Multiple kiro calls can run concurrently |

## Constructing Effective Prompts

When delegating to Kiro, include everything it needs in the prompt itself.
Kiro starts with zero context — it has not seen your conversation.

**Good prompt pattern:**

```
Read the file /absolute/path/to/file.py and identify:
1. Any potential bugs or logic errors
2. Security vulnerabilities (SQL injection, XSS, etc.)
3. Performance issues

Focus on critical issues only. Output as a numbered list with
file:line references.
```

**Key principles:**
- Use **absolute paths** — Kiro may not share your working directory
- Be **specific** about what you want — don't assume context
- State the **output format** you expect
- Include **file paths** for any code/docs Kiro needs to read
- For multi-file tasks, list all relevant paths explicitly

## Handling Results

The wrapper script returns clean text output. Parse it as needed:

- For structured output, ask Kiro to respond in JSON or Markdown
- For long results, ask Kiro to be concise or provide a summary first
- Check the exit code: 0 = success, non-zero = error (timeout, auth, etc.)

## Limitations

- Kiro has no access to your current conversation context
- Each invocation is stateless (no conversation memory between calls)
- Requires Kiro CLI to be installed and authenticated
- Network-dependent (Kiro calls its own backend API)
- Default timeout is 300 seconds; increase for complex tasks

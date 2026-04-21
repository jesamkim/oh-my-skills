# Kiro CLI Delegation Skill

Delegate tasks to [Kiro CLI](https://kiro.dev) when Claude Code's context window is running low or when an independent AI session is needed for isolated analysis.

## Overview

| Item | Value |
|------|-------|
| **Version** | 1.0.0 |
| **Author** | Jesam Kim |
| **License** | MIT |
| **Default Model** | claude-opus-4.7 |

## What It Does

Runs Kiro CLI in **non-interactive mode** (`--no-interactive`) to process a specific task in a completely separate context window. This is useful when:

- Claude Code's context window is running low
- You need large document analysis or code QA across many files
- You want an independent, unbiased second opinion
- A subagent would exceed token limits

## Prerequisites

- [Kiro CLI](https://kiro.dev) installed at `/Applications/Kiro CLI.app/`
- Kiro authenticated (run `kiro-cli login` first)

## Usage

### Via Wrapper Script (Recommended)

```bash
# Basic usage
bash my-skills/kiro/scripts/run_kiro.sh "Summarize /path/to/large-doc.md"

# Trust all tools (auto-approve file reads/writes)
bash my-skills/kiro/scripts/run_kiro.sh --trust-all "Review code in /path/to/project/"

# Custom timeout (default: 300s)
bash my-skills/kiro/scripts/run_kiro.sh --timeout 600 "Analyze this large codebase"

# Different model
bash my-skills/kiro/scripts/run_kiro.sh --model claude-sonnet-4.5 "Quick summary"
```

### Via Claude Code Skill

When installed as a Claude Code skill, simply describe your task and mention "kiro":

> "kiro한테 이 파일 QA 시켜줘"
> "context가 부족하니까 kiro로 분석해줘"
> "delegate this code review to kiro"

## How It Works

1. Claude Code constructs a prompt with all necessary context (file paths, instructions)
2. The wrapper script calls `kiro-cli chat --no-interactive --model claude-opus-4.7`
3. ANSI escape codes are stripped from the output
4. Clean text result is returned to Claude Code

## File Structure

```
kiro/
├── SKILL.md              # Skill definition for Claude Code
├── README.md             # This file
├── LICENSE               # MIT License
└── scripts/
    └── run_kiro.sh       # Wrapper script with ANSI stripping & timeout
```

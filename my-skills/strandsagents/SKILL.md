---
name: strandsagents
description: |
  Build autonomous AI agents with the AWS Strands Agents SDK — using a
  live-documentation workflow rather than frozen examples. This skill should be
  used when the user asks to build, design, debug, or deploy agents with Strands
  Agents: "strands", "strands agents", "strands sdk", "model-agnostic agent",
  "ReAct agent", "agent tool", "@tool decorator", "multi-agent", "agents as
  tools", "swarm", "graph", "agent loop", "Bedrock agent with strands",
  "스트랜즈", "스트랜즈 에이전트", "에이전트 만들어", "멀티 에이전트".
  Because the SDK evolves quickly (new features, changed syntax), this skill keeps
  only the version-agnostic mental model and instead checks the installed/latest
  version and fetches the official docs at run time, then writes code against
  what it just read.
license: MIT License
metadata:
    skill-author: jesamkim
    version: 2.0.0
allowed-tools: [Read, Write, Edit, Bash, Grep, Glob, WebFetch, WebSearch]
---

# Strands Agents — Live-Documentation Development Skill

> **READ THIS FIRST.** Every code snippet in this skill and its references is
> *illustrative of the mental model only*. The Strands Agents SDK changes
> frequently — import paths, class and parameter signatures, model IDs, and
> install commands all drift between versions. **Never write Strands code from
> memory or from a snippet in this skill.** Always run the Delegation Workflow
> below first and write code against the docs you just fetched. When this skill
> and the official docs disagree, the docs win.

## What Strands Agents Is (invariant)

Strands Agents is an open-source AWS SDK for building AI agents with a
**model-driven** approach: the model decides which tools to call and how to
sequence work, instead of you hand-coding the control flow. It is available for
Python and TypeScript, integrates natively with Amazon Bedrock (and other model
providers), and aims for minimal boilerplate.

The mental model is stable even as the API changes:

```
define tools  ->  configure a model  ->  create an agent  ->  run the agent
                                              |
                                       (the agent loop: model reasons,
                                        calls tools, reads results,
                                        repeats until it answers)
```

This much is safe to rely on. The *exact code* for each box is not — fetch it.

## Trusted Sources (the registry)

Use these in priority order. URLs are stable enough to hardcode; if one 404s,
re-fetch the index to rediscover the current path.

| Purpose | Source |
|---|---|
| Latest published version | `https://pypi.org/pypi/strands-agents/json` (field `info.version`) |
| Doc index (LLM-friendly) | `https://strandsagents.com/latest/llms.txt` (structured list of `index.md` pages) |
| Full doc corpus | `https://strandsagents.com/latest/llms-full.txt` (~2.4MB — fetch specific pages instead) |
| Source / releases | `https://github.com/strands-agents/sdk-python` (release notes, breaking changes) |
| Per-task pages | See the Task → Doc table below |

## The Delegation Workflow

Follow these steps **before writing any Strands code**.

### Step 0 — Version & freshness check (always first)
- If Strands is installed locally, run `pip show strands-agents` to read the
  installed version.
- Otherwise (or to compare against latest), fetch the PyPI JSON API and read
  `info.version`:
  ```bash
  python3 -c "import urllib.request,json; print(json.load(urllib.request.urlopen('https://pypi.org/pypi/strands-agents/json'))['info']['version'])"
  ```
- Skip this **only if you ran `pip show` / the PyPI check yourself earlier in
  this same session AND no environment change has happened since** (no venv
  switch, no upgrade). A version the user merely mentioned, or one you assumed,
  does not count — verify it.
- If you cannot determine the version, tell the user and proceed cautiously —
  never silently guess at version-specific API.

### Step 1 — Fetch the authoritative doc for the task
- Map the user's intent to a page in the Task → Doc table below and read it with
  **WebFetch**.
- If the URL 404s or the table has no entry, fetch
  `https://strandsagents.com/latest/llms.txt` and locate the right `index.md`
  link from the structured index, then fetch that.
- Fetch the *specific* page(s) you need — do not pull `llms-full.txt` wholesale,
  to keep context focused.

### Step 2 — Fallback to web search (only after Step 1)
- Enter this step **only after a Step 1 WebFetch returned insufficient or missing
  content**. Even for migration / brand-new feature / breaking-change tasks, fetch
  the official page first — then use **WebSearch** to *supplement*, never to
  *replace*, the official doc.
- Prefer `github.com/strands-agents` releases and issues over third-party articles
  (blogs, StackOverflow). Never copy code from a non-official source without
  confirming it against an official page you fetched.

### Step 3 — Synthesize & implement against fetched facts
- Write code using the import paths, class names, parameter signatures, and model
  IDs **from the doc you fetched in Step 1** — not from this skill's snippets.
- If a snippet here conflicts with the doc, the doc is correct.

### Step 4 — Verify (default-on when you implement)
- Before claiming any code works, run a smoke test: confirm the **exact import
  lines from the doc you fetched** resolve, then run the script. Build the check
  from the fetched imports — do not assume specific symbol names. The version
  probe `python3 -c "import strands; print(strands.__version__)"` is safe and
  useful as part of this.
- If you genuinely cannot execute (no environment), say so explicitly to the user
  and label the code **UNVERIFIED** — do not imply it was tested.
- On failure, re-fetch the relevant page, correct the code, and **re-run until it
  passes**.

## Task → Doc table (core)

Base URL: `https://strandsagents.com/docs/user-guide/`
Append each path below. (All verified reachable; if one changes, use `llms.txt`.)

| Task / intent | Page (append to base) |
|---|---|
| Quickstart / first agent | `quickstart/python/index.md` |
| TypeScript quickstart | `quickstart/typescript/index.md` |
| Add tools (overview) | `concepts/tools/index.md` |
| Write a custom `@tool` | `concepts/tools/custom-tools/index.md` |
| Use MCP tools | `concepts/tools/mcp-tools/index.md` |
| Multi-agent overview | `concepts/multi-agent/multi-agent-patterns/index.md` |
| Agents as Tools (hierarchical) | `concepts/multi-agent/agents-as-tools/index.md` |
| Swarm (autonomous collaboration) | `concepts/multi-agent/swarm/index.md` |
| Graph (explicit workflow) | `concepts/multi-agent/graph/index.md` |
| Agent loop (mental model) | `concepts/agents/agent-loop/index.md` |
| Structured output | `concepts/agents/structured-output/index.md` |
| Streaming responses | `concepts/streaming/index.md` |
| Conversation management | `concepts/agents/conversation-management/index.md` |
| Session management | `concepts/agents/session-management/index.md` |
| Hooks | `concepts/agents/hooks/index.md` |
| Bedrock model provider | `concepts/model-providers/amazon-bedrock/index.md` |
| Deploy to Bedrock AgentCore | `deploy/deploy_to_bedrock_agentcore/index.md` |
| Operating agents in production | `deploy/operating-agents-in-production/index.md` |

For anything not listed (e.g. sandbox, plugins/skills, interrupts, voice/realtime,
other model providers), start from `llms.txt` and follow the matching link.

## Choosing a Multi-Agent Pattern (concept, not code)

These *concepts* are stable; fetch the linked doc for current code.

| Pattern | Use when | Doc |
|---|---|---|
| **Agents as Tools** | Clear manager → specialist hierarchy; sequential delegation | `agents-as-tools` |
| **Swarm** | Workflow not predetermined; agents hand off flexibly by capability | `swarm` |
| **Graph** | Fixed workflow with explicit steps and branching you want visible | `graph` |

Decision shortcut: simple delegation → Agents as Tools; flexible collaboration →
Swarm; fixed, inspectable workflow → Graph.

## Best-Practice Principles (direction, not API)

Apply these as goals; fetch the docs for the current API that achieves them.

- **Cost control** — cap response length, prefer cheaper models for simple steps,
  keep tool outputs concise, and limit retained context. (See conversation /
  context management docs for the current classes and parameters.)
- **Context management** — return summaries, not raw dumps, from tools; trim or
  window history for long conversations.
- **Tool design** — specific names, clear docstrings, full type hints, structured
  returns, graceful error handling; one responsibility per tool.
- **Security** — least privilege (give an agent only the tools it needs), validate
  tool inputs, and filter sensitive data out of tool outputs.

## Troubleshooting (approach, not fixed answers)

When something breaks, re-fetch the relevant doc first — the fix may be a changed
API. General directions:

- **Tool not called** → improve docstring/name/type hints; simplify the signature.
- **Infinite tool loops** → limit conversation history; make tool outputs complete
  and actionable; tighten the system prompt.
- **Context window exceeded** → reduce tool verbosity; window/summarize history.
- **Bedrock errors** → check model ID availability in the region, AWS credentials,
  IAM permissions, and quotas (fetch the Bedrock model-provider doc for current
  model IDs and config).
- **Import / syntax errors** → you are likely using an outdated API; re-fetch the
  page and match it exactly. Confirm with `pip show strands-agents`.

## References

- `references/core_concepts.md` — version-agnostic mental model and pattern
  concepts (no code).
- `references/doc_navigation_guide.md` — how to use `llms.txt` and pick the right
  page; what to fetch for less-common tasks.
- `assets/templates/agent_scaffold.md` — a fill-in-after-fetching checklist for
  scaffolding an agent project.

---

**Version**: 2.0.0
**Author**: jesamkim
**License**: MIT License

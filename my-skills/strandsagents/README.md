# Strands Agents Skill

![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

Build autonomous AI agents with the AWS Strands Agents SDK — using a
**live-documentation workflow** instead of frozen code examples.

## Why v2.0.0 is different

The Strands Agents SDK evolves quickly: new subsystems (hooks, structured output,
streaming, sessions, sandbox, plugins, interrupts), reorganized import paths,
changed signatures, and rotating model IDs. A skill that hardcodes SDK knowledge
goes stale and starts giving confidently wrong answers.

This skill keeps only the **version-agnostic mental model** and a **delegation
workflow**: it checks the installed/latest version, fetches the relevant official
docs at run time, and writes code against what it just read. The skill's own
snippets are illustrative of the mental model only — the official docs are always
the source of truth for code.

## How it works

1. **Version check** — `pip show strands-agents` or the PyPI JSON API.
2. **Fetch docs** — map the task to an official `index.md` page (via the built-in
   Task → Doc table, or `strandsagents.com/latest/llms.txt`) and read it.
3. **Web search fallback** — for migrations, new features, or breaking changes.
4. **Implement against fetched facts** — never from memory or old snippets.
5. **Verify** — confirm imports/syntax (or run) before claiming success.

## Trusted sources

- Latest version: `https://pypi.org/pypi/strands-agents/json`
- Doc index (LLM-friendly): `https://strandsagents.com/latest/llms.txt`
- Source / releases: `https://github.com/strands-agents/sdk-python`

## Installation

```bash
/plugin install strandsagents@my-skills
```

## Usage

Ask Claude to build with Strands and it will fetch current docs first, e.g.:
- "Create a Strands agent with a custom tool for Bedrock"
- "Set up a multi-agent swarm with Strands"
- "How do I stream responses / get structured output with Strands?"
- "Deploy my Strands agent to Bedrock AgentCore"

The skill always verifies the SDK version and the latest syntax before writing code.

## Structure

- **SKILL.md** — invariant core, delegation workflow, and the Task → Doc URL table.
- **references/core_concepts.md** — version-agnostic mental model and patterns (no code).
- **references/doc_navigation_guide.md** — how to navigate `llms.txt` and pick the right page.
- **assets/templates/agent_scaffold.md** — a fill-in-after-fetching scaffolding checklist.

## License

MIT License - See LICENSE.txt for details

## Author

jesamkim (jesamkim@gmail.com)

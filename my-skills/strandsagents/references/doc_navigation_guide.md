# Documentation Navigation Guide

How to find the right, current Strands Agents documentation quickly. Use this
when the task isn't in the SKILL.md Task → Doc table, or when a hardcoded URL has
moved.

## Start from llms.txt

`https://strandsagents.com/latest/llms.txt` is a structured, LLM-friendly index
(~696 lines) of the entire user guide and API reference. Each entry links to a
plain-markdown `.../index.md` page that WebFetch reads cleanly. Prefer it over a
generic web search — it is the official, current map of the docs.

Its top-level groups (stable enough to navigate by):
- **Get Started** — overview, Python quickstart, TypeScript quickstart.
- **Build** — adding tools, custom tools, MCP tools, multi-agent systems,
  structured output, streaming, voice & realtime.
- **Concepts** — agent loop, state, session management, snapshots, prompts, hooks,
  conversation management, context management, memory, retry strategies, sandbox,
  interrupts, tools (executors / community tools / vended tools), plugins (skills,
  steering, context-offloader/injector, goal-loop), interventions.
- **Model providers** — Amazon Bedrock, Amazon Nova, Anthropic, and others.
- **Deploy** — Bedrock AgentCore, AWS Lambda, Fargate, App Runner, EKS, EC2,
  Docker, Kubernetes, Terraform, operating agents in production.
- **API reference** — generated per-module reference.

## Fetching strategy

- **Fetch specific `index.md` pages**, not `llms-full.txt`. The full corpus is
  ~2.4MB; pulling it wastes context. Pull only the 1–3 pages the task needs.
- **Chain fetches** when a task spans topics — e.g. "a Bedrock multi-agent app
  with MCP tools" → fetch the Bedrock provider page + the multi-agent pattern page
  + the MCP tools page, then synthesize.
- **Re-derive moved URLs**: if a page 404s, fetch `llms.txt` and search its text
  for the topic keyword to get the current link. Do not guess at a path.

## Mapping common intents to doc areas

| If the user wants to... | Look under |
|---|---|
| Make a first agent run | Get Started → Python quickstart |
| Define what the agent can do | Build → Adding Tools / Custom Tools |
| Connect external tools/servers | Build → Using MCP Tools; Concepts → Tools (vended/community) |
| Coordinate several agents | Build → Multi-Agent Systems; Concepts → multi-agent (agents-as-tools / swarm / graph / workflow / agent-to-agent) |
| Get typed/JSON results | Build → Structured Output |
| Stream tokens / events | Build → Streaming; Concepts → streaming (async-iterators, callback-handlers) |
| Build voice / realtime | Build → Voice & Realtime; Concepts → bidirectional-streaming |
| Persist or resume state | Concepts → session-management, state, snapshots |
| Hook into the agent loop | Concepts → hooks, interventions, interrupts |
| Control cost / context length | Concepts → conversation-management, context-management |
| Add memory / knowledge base | Concepts → memory (overview, bedrock-knowledge-base) |
| Pick / configure a model | Model providers → (Bedrock / Nova / Anthropic / ...) |
| Ship to production | Deploy → (AgentCore / Lambda / Fargate / ...), operating-agents-in-production |
| Look up an exact class/param | API reference (from llms.txt) |

## Version awareness

- Confirm the version first (see SKILL.md Step 0). When you report code to the
  user, it is good practice to note which version you verified against.
- For "what changed" / migration questions, the docs may lag — check the GitHub
  releases at `https://github.com/strands-agents/sdk-python` via WebSearch.
- The docs site is versioned under `/latest/`; if a user pins an older SDK, look
  for a matching versioned docs path or rely on that version's release notes.

## When to fall back to web search

Use WebSearch (not just the docs) when:
- The official docs return nothing useful for the topic.
- The question is about a breaking change, deprecation, or a release that may be
  newer than the docs site reflects.
- You need community examples or issue threads for an edge case.

Target `github.com/strands-agents` and `strandsagents.com` in the query to stay
close to authoritative sources.

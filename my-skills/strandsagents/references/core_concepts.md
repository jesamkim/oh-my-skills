# Core Concepts (version-agnostic)

This file holds the parts of Strands Agents that do **not** change between SDK
versions: the mental model and the reasoning behind each pattern. It contains
**no code** on purpose — for current syntax, follow the Delegation Workflow in
`SKILL.md` and fetch the official docs.

## The model-driven philosophy

Traditional agent frameworks ask you to encode the control flow: "call tool A,
then if X call tool B." Strands inverts this. You give the model a set of tools
and a goal; the **model** decides which tools to call, in what order, and when it
has enough information to answer. This is the model-driven approach.

Implications that stay true regardless of API:
- The quality of your tool **descriptions** drives behavior more than any wiring.
  The model picks tools from their names, docstrings, and signatures.
- You shape outcomes through prompts, tool design, and guardrails — not through
  hardcoded branching.
- Less boilerplate, but less explicit control; you trade determinism for
  flexibility.

## The agent loop (mental model)

Every run, whatever the current API looks like, follows this conceptual cycle:

1. The agent receives user input plus its system prompt.
2. The model reasons and decides whether to call one or more tools.
3. Selected tools execute and return results.
4. The model reads those results and may call more tools.
5. The loop repeats until the model produces a final answer.

When you debug, locate the failure in this loop: is the model not *choosing* the
tool (description problem), is the tool *failing* (implementation problem), or is
it *looping* (the results aren't conclusive, or history isn't bounded)?

## Tools: the unit of capability

A tool is a function the model can call. The stable principles:
- **One responsibility per tool.** Composable, narrow tools beat one do-everything tool.
- **Describe for the model, not the human.** The description is a prompt; it tells
  the model *when* to use the tool.
- **Type the inputs and outputs.** Structure lets the model pass correct arguments
  and parse results.
- **Fail soft.** Return error information the model can reason about rather than
  throwing and crashing the loop.

(The exact decorator, signature conventions, and validation helpers are
version-specific — fetch `concepts/tools/custom-tools`.)

## Multi-agent patterns: when to use which

The *shapes* are stable; the *code* is not.

### Agents as Tools (hierarchical)
A coordinator agent treats specialist agents as callable tools. Use when there is
a clear manager → specialist hierarchy and delegation is mostly sequential. Easy
to reason about; the coordinator stays in control.

### Swarm (autonomous collaboration)
Peer agents hand work off to each other based on capability, with no fixed script.
Use when the path isn't known in advance and different expertise is needed at
different moments. More flexible, harder to predict.

### Graph (explicit workflow)
You define nodes (agents/steps) and edges (transitions) explicitly. Use when the
workflow is fixed, you need branching you can see, and execution should be
inspectable. Most control, least emergent behavior.

**Decision shortcut:** simple delegation → Agents as Tools; flexible
collaboration → Swarm; fixed, inspectable workflow → Graph.

## Why this skill fetches instead of remembers

Strands moves fast. Between versions, import paths get reorganized, classes are
renamed or relocated, parameters change defaults, new subsystems appear (hooks,
structured output, streaming, sessions, sandbox, plugins, interrupts), and model
IDs rotate. A frozen example that worked last quarter can fail or, worse, run with
silently wrong behavior today. The mental model above is your anchor; the SDK's
own docs are always the source of truth for code.

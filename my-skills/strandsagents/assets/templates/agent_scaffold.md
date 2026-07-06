# Agent Scaffold Checklist

A procedure for scaffolding a new Strands Agents project. It is deliberately
**code-free** — fill each step in with syntax fetched from the current docs (see
the Delegation Workflow in `SKILL.md`). Do not paste old snippets.

## 0. Confirm the version
- [ ] Determine the Strands version (`pip show strands-agents`, or the PyPI JSON
      API). Note it; you will verify code against this version.

## 1. Read the right docs for this build
- [ ] Quickstart page (always, for current install + import + minimal agent).
- [ ] One page per capability you need: custom tools, MCP tools, multi-agent
      pattern, structured output, streaming, sessions, etc.
- [ ] Bedrock (or chosen) model-provider page for the current model IDs and config.

## 2. Decide the shape (concept — see core_concepts.md)
- [ ] Single agent, or multi-agent? If multi: Agents-as-Tools / Swarm / Graph?
- [ ] List the tools the agent needs (one responsibility each).
- [ ] Choose the model (capability vs cost) and a sensible response-length cap.

## 3. Implement against the fetched docs
- [ ] Install per the quickstart's current command.
- [ ] Define tools using the current decorator/signature conventions.
- [ ] Configure the model with a model ID confirmed from the provider doc.
- [ ] Create the agent (system prompt, tools, any conversation/context manager).
- [ ] Wire multi-agent coordination if applicable, per the pattern's doc.

## 4. Apply best-practice principles (see SKILL.md)
- [ ] Tool descriptions are clear and specific; inputs/outputs typed.
- [ ] Tools fail soft (return error info, don't crash the loop).
- [ ] Least privilege: the agent has only the tools it needs.
- [ ] Tool inputs validated; sensitive data filtered from outputs.
- [ ] Cost/context: concise tool outputs; history bounded for long chats.

## 5. Verify before claiming done
- [ ] Imports resolve — run a smoke test using the **exact import lines from the
      quickstart you fetched in step 1** (do not assume `from strands import
      Agent, tool`). `python3 -c "import strands; print(strands.__version__)"` is a
      safe baseline probe.
- [ ] A minimal run works end-to-end.
- [ ] If anything fails with an import/attribute/signature error, re-fetch the doc
      — the API likely changed — correct, and re-run until it passes.
- [ ] If you cannot execute (no environment), label the code UNVERIFIED to the user.

## 6. (Optional) Deployment
- [ ] If deploying, fetch the relevant Deploy page (AgentCore / Lambda / Fargate /
      etc.) and follow its current steps and IAM requirements.

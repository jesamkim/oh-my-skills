# MCP-Based External System Integration Pattern

Pattern for showing how an AWS AI agent platform (Bedrock AgentCore, Bedrock Agents)
connects to external/on-premises systems via the Model Context Protocol (MCP).

Captured from real customer architecture work (Samsung Welstory SCM AI, Q1 2026).
This is a recurring pattern whenever a customer asks to show "MCP integration with
legacy systems" — the same visual conventions should apply every time.

## When to Use This Pattern

- Customer has on-premises or external SaaS systems that the AI agent needs to call
- AgentCore / Bedrock Agents exposes an MCP Gateway tool layer
- You need to visually distinguish MCP calls from normal AWS service calls
- External systems don't fit inside AWS Cloud container (they're outside the AWS boundary)

If the external systems are AWS-hosted but in a different account/region, this is
NOT the right pattern — use cross-account/cross-region arrows instead.

## Visual Conventions

| Element | Style | Why |
|---------|-------|-----|
| MCP arrow color | `#8C4FFF` (Networking purple) | MCP is a protocol/networking concern |
| MCP arrow style | `dashed` | Async/protocol boundary, not direct data flow |
| MCP arrow direction | `bidirectional` | MCP is request/response (client calls tool, tool returns result) |
| MCP arrow label | `"MCP Protocol"` | Single shared label, not per-arrow |
| External system icon | `on-premises` | Pre-existing AWS Architecture deck icon for non-AWS systems |
| External system sublabel | `"On-Premises"` or vendor name | Makes it obvious this is outside AWS |
| External grouping | `generic` container, dashed gray border, label `"<Customer> On-Premises Systems"` | Visually separates from AWS-hosted services |

The single shared `"MCP Protocol"` label (instead of per-arrow labels) is intentional:
MCP is the protocol binding the whole branch, so labeling it once on the shared path
makes the diagram less noisy. Per-arrow labels only help if the tools are semantically
different (`"menu plan"` vs `"purchase order"`) — usually they're not.

## Layout Recipe

The canonical layout is:

```
[AWS Cloud]
  ...
  [AgentCore Runtime / Bedrock Agents container]
       |
       | (internal arrow to)
       |
       v
  [MCP Gateway node]
       |
       :  (dashed purple, bidirectional)
       :
       v
  ┌── [Customer On-Premises Systems] ──┐ (dashed gray generic container)
  │   [External System 1]              │
  │   [External System 2]              │
  └────────────────────────────────────┘
```

Key placement rules:
- MCP Gateway should sit at the boundary between the AgentCore container and the
  external grouping — it's literally the protocol bridge
- The external grouping goes in free space (usually top-right or bottom-right of
  the slide) so the MCP arrow can take an L-shaped path that doesn't cross other flows
- All MCP arrows from MCP Gateway share one vertical segment up/down to a split point,
  then branch horizontally — this reads as "one protocol, many tools" rather than
  "many unrelated connections"

## JSON Recipe (aws-diagram engine)

```json
{
  "title": "SCM AI with MCP Integration",
  "subtitle": "Bedrock AgentCore + MCP bridge to on-premises systems",
  "theme": "light",
  "size": "complex",
  "nodes": [
    {"id": "user", "service": "users", "label": "Users", "x": 0, "y": 2},
    {"id": "apigw", "service": "api-gateway", "label": "API Gateway", "x": 1, "y": 2},
    {"id": "agentcore", "service": "bedrock-agentcore", "label": "AgentCore Runtime", "sublabel": "Strands + Memory", "x": 2, "y": 2, "container": "platform"},
    {"id": "mcp", "service": "lambda", "label": "MCP Gateway", "sublabel": "MCP Server", "x": 3, "y": 2, "container": "platform"},
    {"id": "sys1", "service": "on-premises", "label": "Meal Forecast", "sublabel": "On-Premises", "x": 4, "y": 1, "container": "welstory"},
    {"id": "sys2", "service": "on-premises", "label": "Menu Planning", "sublabel": "On-Premises", "x": 4, "y": 3, "container": "welstory"}
  ],
  "connections": [
    {"source": "user", "target": "apigw", "label": "HTTPS", "style": "solid"},
    {"source": "apigw", "target": "agentcore", "label": "Invoke", "style": "solid"},
    {"source": "agentcore", "target": "mcp", "style": "solid"},
    {"source": "mcp", "target": "sys1", "label": "MCP Protocol", "style": "bidirectional", "color": "#8C4FFF", "source_port": "right"},
    {"source": "mcp", "target": "sys2", "style": "bidirectional", "color": "#8C4FFF", "source_port": "right"}
  ],
  "containers": [
    {"id": "platform", "type": "generic", "label": "Amazon Bedrock AgentCore Platform", "children": ["agentcore", "mcp"]},
    {"id": "welstory", "type": "generic", "label": "Welstory On-Premises Systems", "children": ["sys1", "sys2"]}
  ]
}
```

Notes:
- Only ONE MCP connection carries the `"MCP Protocol"` label — the others share it
  visually since they all originate from the same MCP Gateway
- `source_port: "right"` on the MCP connections forces both to exit the MCP Gateway's
  right edge, which creates the visual "one protocol, many tools" fan-out
- `container: "welstory"` groups the external systems in a generic container that
  renders with dashed gray border — the `aws-diagram` engine handles this automatically

See `examples/scm-ai-mcp-integration.json` for a complete, renderable example.

## Alternative: Hybrid Overlay on an Existing PPTX

Sometimes the customer (or their prototyping engineer) has already drawn the AWS
architecture in PowerPoint and you just need to ADD the MCP external connections
without redrawing everything.

In this case, use the `myslide` skill's `pptx-overlay` workflow (see
`references/pptx-overlay.md` in that skill). The key things to remember:

- Keep the arrow color and style identical to the JSON recipe above (#8C4FFF, dashed, bidirectional)
- Use the same `"MCP Protocol"` single-label convention
- Position the external grouping in empty slide space (check the actual coordinates
  of existing shapes first — don't eyeball from the rendered image, the coordinate
  grid you see is not the one PowerPoint uses)
- Pin the shared vertical segment BELOW the slide title area (y >= 2.4 inches
  on a 13.33 × 7.5 slide) so the arrow never crosses the title/subtitle

## Common Mistakes (and Why They Happen)

1. **Per-arrow "MCP Protocol" labels on every connection** — clutters the diagram
   and misrepresents MCP as N separate protocols. One shared label reads better.

2. **Solid arrows for MCP calls** — readers interpret solid as "direct request/response
   in the hot path" and dashed as "protocol/async/sidecar". MCP is protocol-layer,
   so dashed matches reader expectations.

3. **External systems placed inside VPC/Subnet containers** — on-premises or SaaS
   systems are OUTSIDE the AWS boundary by definition. Nesting them in a VPC
   container is architecturally wrong and will confuse the reader.

4. **Missing bidirectional arrowheads** — MCP is request/response. If you show
   only one direction, the reader assumes fire-and-forget, which is wrong for
   tool-calling semantics.

5. **Diagonal arrows to external systems** — always route MCP arrows orthogonally
   (L-shape: vertical → horizontal → vertical). Diagonal lines signal "informal
   sketch", orthogonal lines signal "architecture".

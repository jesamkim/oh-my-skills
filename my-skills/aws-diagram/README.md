# aws-diagram

Generate professional AWS architecture diagrams with official service icons,
guaranteed orthogonal arrow routing, and VPC/AZ/Subnet container nesting.
Outputs self-contained SVG, PNG, and PPTX.

## Features

- **Python engine** with deterministic orthogonal (right-angle) arrow routing
- **JSON-driven** - Claude creates JSON definitions, engine handles layout/rendering
- **150+ AWS icons** (incl. 9 group icons) inline-embedded for self-contained SVGs
- **Bedrock AgentCore support** - dedicated `bedrock-agentcore` icon (Q1 2026) plus AgentCore component-specific outline icons (May 2026)
- **Official AWS color palette** following AWS Architecture Icon Deck guidelines
- **Two diagram types** - Infrastructure (VPC/AZ/Subnet nesting) and High-Level (hub-spoke logical grouping)
- **Container hierarchy** (AWS Cloud > Region > VPC > AZ > Subnet) plus `generic` logical-grouping containers
- **Dual output** - SVG + optional PNG + optional PPTX
- **Sub-agent / Team-Up** support for complex diagrams (10+ services)
- **Light + dark theme** support

## Quick Start

```bash
# Generate SVG + PNG from JSON definition
python3 scripts/generate_diagram.py -i diagram.json -o architecture.svg --png

# Also generate PPTX
python3 scripts/generate_diagram.py -i diagram.json -o architecture.svg --png --pptx architecture.pptx
```

## JSON Schema

```json
{
  "title": "My Architecture",
  "theme": "light",
  "size": "standard",
  "nodes": [
    {"id": "alb", "service": "elb", "label": "ALB", "x": 0, "y": 0, "container": "pub"}
  ],
  "connections": [
    {"source": "alb", "target": "ec2", "label": "HTTP", "style": "solid", "step_number": 1},
    {"source": "dc", "target": "alb", "label": "Direct Connect", "style": "dashed", "color": "#8C4FFF", "source_port": "right", "target_port": "left"}
  ],
  "containers": [
    {"id": "vpc", "type": "vpc", "label": "VPC", "children": ["pub", "priv"]},
    {"id": "platform", "type": "generic", "label": "Bedrock AgentCore", "children": ["runtime", "memory"]}
  ]
}
```

- **Connections** support a `color` field (hex, arrowhead auto-matches) and forced `source_port` / `target_port` (`left`/`right`/`top`/`bottom`) to control which edge an arrow exits/enters.
- **Containers** include a `generic` type (dashed gray border) for logical grouping in High-Level diagrams without implying VPC/Subnet boundaries.

## Directory Structure

```
aws-diagram/
├── SKILL.md              # Skill specification and workflow
├── README.md             # This file
├── icons/                # 150+ AWS service SVG icons (incl. AgentCore component icons)
├── scripts/
│   ├── generate_diagram.py      # CLI entry point, orchestrates pipeline
│   ├── diagram_schema.py        # JSON schema and data classes
│   ├── layout_engine.py         # Grid-to-pixel layout calculator
│   ├── orthogonal_router.py     # Right-angle arrow routing
│   ├── svg_renderer.py          # SVG assembly with inline icons
│   ├── pptx_export.py           # Native PPTX shape export
│   ├── pptx_connector.py        # OOXML connector injection for PPTX arrows
│   ├── icon_rasterizer.py       # SVG-to-PNG rasterization for PPTX icons
│   └── download-icons.sh        # Icon updater from npm
├── examples/
│   ├── 3-tier-web.json              # CloudFront + ALB + EC2 + RDS (Infrastructure)
│   ├── serverless-api.json          # API GW + Lambda + DynamoDB + Cognito
│   ├── data-pipeline.json           # S3 + Glue + Kinesis + Redshift (High-Level)
│   ├── static-website.json          # CloudFront + S3 + Route 53 (High-Level)
│   └── scm-ai-mcp-integration.json  # AgentCore + MCP Gateway + on-prem (High-Level)
└── references/
    ├── mcp-external-integration.md  # AgentCore/MCP external integration pattern
    └── troubleshooting.md           # Common pitfalls and SVG fixes
```

## Diagram Types

| Type | Use For | Layout |
|------|---------|--------|
| **Infrastructure** | Deployment topology, network/security boundaries | AWS Cloud > Region > VPC > AZ > Subnet nesting, numbered request-flow steps |
| **High-Level** | Platform overviews, service interactions, executive briefs | Hub-spoke around a central service, `generic` dashed groupings, no VPC/Subnet, descriptive arrow labels |

## Bedrock AgentCore

- **Dedicated icon** (Q1 2026): use `"service": "bedrock-agentcore"` for AgentCore Runtime nodes instead of reusing the generic `bedrock` icon. Sub-services (Memory, Gateway, Identity, etc.) reuse the same icon, differentiated by `sublabel`, grouped inside a single `generic` container.
- **Component-specific outline icons** (May 2026): for L200 / slide decks that must distinguish individual components, `icons/` ships `agentcore-{component}-{color}-{theme}.svg`:
  - **Components** (9): `logo`, `ai-agent`, `runtime`, `gateway`, `identity`, `code-interpreter`, `observability`, `browser-tool`, `memory`
  - **Colors**: `teal` (`#01A88D`), `blue` (`#538DF7`), `purple` (`#7B27FF`), `cyan` (`#7CF9FF`, dark theme only)
  - **Themes**: `light` (black outline + accent), `dark` (white outline + accent)
  - Example: `agentcore-runtime-teal-light.svg`, `agentcore-memory-purple-dark.svg`

## Design Rules

The engine guarantees orthogonal routing; the rest is enforced by rules in `SKILL.md`:

- **Hard Rules** (non-negotiable): WAF/Cognito are sidecars not in the traffic path; outside-VPC services keep a ≥1 grid-column gap from VPC borders; max 3 outgoing arrows per node, each on a different port.
- **Arrowhead Endpoint Rules**: every arrowhead must land on the target's source-facing (near) edge — never pierce through to the far side, never run through the icon's label/sublabel text. Verify in the PNG, fix in the SVG, then re-rasterize.

## Usage Examples

```
"3-tier 웹 앱 아키텍처 그려줘"
"서버리스 API 아키텍처 다이어그램 만들어줘"
"VPC 내부 ECS 마이크로서비스 구성도"
"S3 -> Glue -> Redshift 데이터 파이프라인 시각화"
"AgentCore 기반 AI 에이전트 플랫폼 하이레벨 다이어그램"
```

## Version

- **v3.1.0** - Native PPTX hand-coordinate path: `pptx_native_lib.py` (NativeSlideBuilder — container/line/arrow_label/node helpers, AWS colors baked in, CJK-safe fixed-width labels with word_wrap off, strict z-order) + `references/pptx-native-workflow.md` (workflow, layout-rule table, subagent QA loop). Born from a field session where `--pptx` automated export produced 20 visual defects on a 12-node Korean-label diagram and a hand-coordinate rebuild rendered clean in one pass. SKILL.md now routes editable-PPTX deliverables to the native path and marks `--pptx` as not recommended for customer deliverables
- **v3.0.0** - 150+ icon catalog; Bedrock AgentCore (dedicated icon + component-specific outline icons); High-Level hub-spoke diagram type with `generic` logical-grouping containers; forced `source_port`/`target_port` and custom arrow colors; Hard Rules and Arrowhead Endpoint Rules; native PPTX connectors (`pptx_connector.py`) and icon rasterization (`icon_rasterizer.py`)
- **v2.0.0** - Python SVG engine, JSON-driven workflow, PPTX export, Icon Deck alignment
- **v1.1.0** - Orthogonal arrow routing rules, anti-overlap, step number circles
- **v1.0.0** - Initial release with 85 icons and 7 architecture patterns

## Author

jesamkim

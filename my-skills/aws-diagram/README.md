# aws-diagram

Generate professional AWS architecture diagrams with official service icons,
guaranteed orthogonal arrow routing, and VPC/AZ/Subnet container nesting.
Outputs self-contained SVG, PNG, and PPTX.

## Features

- **Python engine** with deterministic orthogonal (right-angle) arrow routing
- **JSON-driven** - Claude creates JSON definitions, engine handles layout/rendering
- **85 AWS icons** (76 service + 9 group) inline-embedded for self-contained SVGs
- **Official AWS color palette** following AWS Architecture Icon Deck guidelines
- **Container hierarchy** (AWS Cloud > Region > VPC > AZ > Subnet)
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
    {"source": "alb", "target": "ec2", "label": "HTTP", "style": "solid", "step_number": 1}
  ],
  "containers": [
    {"id": "vpc", "type": "vpc", "label": "VPC", "children": ["pub", "priv"]}
  ]
}
```

## Directory Structure

```
aws-diagram/
├── SKILL.md              # Skill specification and workflow
├── README.md             # This file
├── icons/                # 85 AWS service SVG icons (64x64 viewBox)
├── scripts/
│   ├── generate_diagram.py      # CLI entry point
│   ├── diagram_schema.py        # JSON schema definitions
│   ├── layout_engine.py         # Grid-to-pixel layout calculator
│   ├── orthogonal_router.py     # Right-angle arrow routing
│   ├── svg_renderer.py          # SVG assembly with inline icons
│   ├── pptx_export.py           # PPTX generation from PNG
│   └── download-icons.sh        # Icon updater from npm
└── examples/
    └── 3-tier-web.json          # Example diagram definition
```

## Usage Examples

```
"3-tier 웹 앱 아키텍처 그려줘"
"서버리스 API 아키텍처 다이어그램 만들어줘"
"VPC 내부 ECS 마이크로서비스 구성도"
"S3 -> Glue -> Redshift 데이터 파이프라인 시각화"
```

## Version

- **v2.0.0** - Python SVG engine, JSON-driven workflow, PPTX export, Icon Deck alignment
- **v1.1.0** - Orthogonal arrow routing rules, anti-overlap, step number circles
- **v1.0.0** - Initial release with 85 icons and 7 architecture patterns

## Author

jesamkim

---
name: aws-diagram
description: |
  Generate professional AWS architecture diagrams with official service icons,
  orthogonal (right-angle) arrow routing, and VPC/AZ/Subnet container nesting.
  Produces self-contained SVGs and optional PPTX with inline-embedded icons.
  Follows AWS Architecture Icon Deck guidelines for colors, arrows, and labels.
  Supports sub-agent parallelization for complex diagrams.
  Use this skill whenever the user wants to create, draw, or visualize any AWS
  architecture, infrastructure layout, or cloud service diagram. Also trigger when
  the user mentions "draw architecture", "make a diagram", "visualize infrastructure",
  "show me the architecture", "AWS 구성도", "인프라 그림", "아키텍처 다이어그램",
  "AWS 다이어그램", "aws diagram", "architecture diagram", "aws-diagram",
  or provides a list of AWS services and asks to see how they connect.
license: MIT License
metadata:
  skill-author: jesamkim
  version: 3.0.0
allowed-tools: [Read, Write, Edit, Bash, Glob, Agent, AskUserQuestion]
---

# AWS Architecture Diagram Generator

Generate professional AWS architecture diagrams with official service icons,
guaranteed orthogonal arrow routing, and standard AWS design system.

## Quick Start

```bash
# 1. Create JSON definition (see Schema below)
# 2. Generate SVG + PNG
python3 scripts/generate_diagram.py -i diagram.json -o output.svg --png

# 3. Verify: read the PNG and visually inspect
# 4. Optional: add PPTX
python3 scripts/generate_diagram.py -i diagram.json -o output.svg --png --pptx output.pptx
```

---

## Workflow

### Primary: JSON-Driven Generation (Recommended)

The Python engine handles layout, routing, and rendering deterministically.
Claude produces a JSON definition; the engine guarantees correct output.

```
1. Analyze user requirements -> identify services, connections, containers
2. Choose diagram type: Infrastructure (VPC-centric) or High-Level (logical grouping)
3. Create a JSON diagram definition (see Schema below)
4. Run: python3 scripts/generate_diagram.py -i diagram.json -o output.svg --png
5. QA: visually inspect the PNG output (MANDATORY)
6. Optional: --pptx output.pptx for PowerPoint export
```

### Fallback: Manual SVG

For very simple diagrams (2-3 services, no containers), hand-craft SVG
following the rules in Sections 3-7 below. Use `icons/` directory for service icons.

---

## JSON Diagram Schema

Claude generates this JSON; the Python engine handles the rest.

```json
{
  "title": "3-Tier Web Application",
  "subtitle": "ALB + EC2 + RDS on AWS",
  "theme": "light",
  "size": "standard",
  "nodes": [
    {"id": "alb", "service": "elb", "label": "Application\nLoad Balancer", "x": 1, "y": 1, "container": "pub-sub"},
    {"id": "ec2", "service": "ec2", "label": "Amazon EC2", "sublabel": "Web Server", "x": 2, "y": 1, "container": "priv-sub"}
  ],
  "connections": [
    {"source": "alb", "target": "ec2", "label": "HTTP", "style": "solid", "step_number": 1},
    {"source": "dc", "target": "alb", "label": "Direct Connect", "style": "dashed", "color": "#8C4FFF", "source_port": "right"}
  ],
  "containers": [
    {"id": "cloud", "type": "aws-cloud", "label": "AWS Cloud", "children": ["vpc"]},
    {"id": "vpc", "type": "vpc", "label": "VPC", "parent": "cloud", "children": ["pub-sub", "priv-sub"]},
    {"id": "pub-sub", "type": "public-subnet", "label": "Public subnet", "parent": "vpc", "children": ["alb"]},
    {"id": "priv-sub", "type": "private-subnet", "label": "Private subnet", "parent": "vpc", "children": ["ec2"]}
  ]
}
```

**Node fields:** `id`, `service` (icon filename without .svg), `label`, `x`/`y` (grid), `sublabel`?, `container`?
**Connection fields:** `source`, `target`, `label`?, `style` (solid/dashed/bidirectional), `step_number`?, `color`? (hex), `source_port`? (left/right/top/bottom), `target_port`? (left/right/top/bottom)
**Container fields:** `id`, `type`, `label`, `parent`?, `children[]`
**Container types:** aws-cloud, region, vpc, az, public-subnet, private-subnet, security-group, auto-scaling-group, generic
**Size presets:** simple (800x500), standard (1024x768), complex (1200x900), wide (1400x600)
**Themes:** light (white bg, default), dark (AWS Squid Ink #232F3E bg)

---

## Engine Architecture

The Python engine consists of 7 modules with clear separation of concerns:

| Module | Responsibility |
|--------|---------------|
| `generate_diagram.py` | CLI entry point, orchestrates pipeline |
| `diagram_schema.py` | JSON schema, data classes (DiagramNode, DiagramConnection, DiagramContainer, DiagramDefinition), serialization |
| `layout_engine.py` | Grid-to-pixel coordinate computation, container bounding box calculation |
| `orthogonal_router.py` | Arrow routing (L-shape, Z-shape), obstacle avoidance, label/callout placement |
| `svg_renderer.py` | SVG assembly with inline icon symbols, container styling, arrow rendering |
| `pptx_export.py` | Native PPTX shapes (editable containers, icons, labels, connectors) |
| `pptx_connector.py` | OOXML connector injection for native PowerPoint arrows |
| `icon_rasterizer.py` | SVG-to-PNG rasterization for PPTX icon embedding |

### Layout Constants (for precise positioning)

| Constant | Value | Description |
|----------|-------|-------------|
| `ICON_SIZE` | 48px | Service icon dimensions |
| `CELL_WIDTH` | 180px | Grid cell width (x-axis spacing) |
| `CELL_HEIGHT` | 160px | Grid cell height (y-axis spacing) |
| `CANVAS_MARGIN` | 60px | Outer margin around all content |
| `HEADER_HEIGHT` | 26px | Container header bar height |
| `ICON_LABEL_GAP` | 14px | Gap between icon and label text |
| `CALLOUT_RADIUS` | 12px | Step number circle radius |
| `PARALLEL_OFFSET` | 15px | Offset between parallel arrows |

---

## CLI Usage

```bash
# SVG only
python3 scripts/generate_diagram.py -i diagram.json -o architecture.svg

# SVG + PNG (for QA and embedding)
python3 scripts/generate_diagram.py -i diagram.json -o architecture.svg --png

# SVG + PNG + PPTX
python3 scripts/generate_diagram.py -i diagram.json -o architecture.svg --png --pptx architecture.pptx

# Validate JSON before generating
python3 scripts/generate_diagram.py -i diagram.json -o architecture.svg --validate

# Custom icons directory
python3 scripts/generate_diagram.py -i diagram.json -o architecture.svg --icons-dir ./icons

# Custom PNG resolution
python3 scripts/generate_diagram.py -i diagram.json -o architecture.svg --png --png-width 3072
```

---

## Diagram Types & When to Use

### Type 1: Infrastructure Diagram (VPC-centric)

Use for: deployment architecture, network topology, security boundaries.
Containers: AWS Cloud > Region > VPC > AZ > Subnet > Services.
Examples: 3-tier web, microservices on EKS, multi-AZ RDS.

### Type 2: High-Level Architecture (Logical Grouping)

Use for: platform overviews, service interactions, solution architecture briefs.
Characteristics:
- **NO VPC/Subnet containers** -- use `generic` container type with dashed borders for logical groupings
- **Hub-spoke layout** -- central service (e.g., AgentCore Runtime, EventBridge) with radiating connections
- **AWS Cloud container optional** -- omit for cleaner presentation when all services are obviously AWS
- **Multi-directional arrows** -- not just left-to-right; use top/bottom/left/right ports freely
- **Descriptive arrow labels** -- "Agent invocations (Streamable HTTP)", "IdP integration", "Metrics & logs"
- **Observability services at bottom** -- CloudWatch, X-Ray placed below the main flow

**High-Level Layout Pattern (Hub-Spoke):**
```
x=0: External (User client at y=2)
x=1: Entry (Amplify/CloudFront at y=2), Auth (Cognito at y=1)
x=2: API Layer -- horizontal chain: API GW (y=0) → Lambda (y=0) → DynamoDB (y=0)
x=2: Hub center (AgentCore Runtime at y=2) inside generic dashed container
x=3: Spoke services (CodeInterpreter y=1, Identity y=2, Memory y=3)
x=4: External integrations (IdP at y=2, Custom Tool at y=3)
x=2~3 bottom: Observability (CloudWatch y=5, X-Ray y=5)
```

**Generic container for logical grouping:**
```json
{"id": "platform", "type": "generic", "label": "Amazon Bedrock AgentCore", "children": ["runtime", "code-interp", "identity", "memory", "gateway", "observability"]}
```

---

## AWS Category Color System

| Category | Hex | Services |
|----------|-----|----------|
| Compute | `#ED7100` | EC2, Lambda, ECS, EKS, Fargate, Batch, App Runner, Lightsail, Auto Scaling, ECR |
| Storage | `#7AA116` | S3, EBS, EFS, FSx, Storage Gateway, S3 Glacier |
| Database | `#C925D1` | RDS, DynamoDB, Aurora, ElastiCache, Redshift, Neptune, DocumentDB, MemoryDB |
| Networking | `#8C4FFF` | VPC, CloudFront, Route 53, API Gateway, ELB, Direct Connect, Transit Gateway, VPC Lattice, PrivateLink |
| Security | `#DD344C` | IAM, WAF, Shield, KMS, Secrets Manager, ACM, Cognito, GuardDuty, Security Hub |
| App Integration | `#E7157B` | SQS, SNS, EventBridge, Step Functions, AppSync, MQ |
| AI/ML | `#01A88D` | Bedrock, SageMaker, Rekognition, Textract, Comprehend, Lex, Amazon Q |
| Management | `#E7157B` | CloudWatch, CloudFormation, CloudTrail, Systems Manager, Config, Organizations, X-Ray |
| Analytics | `#8C4FFF` | Athena, Glue, Kinesis, QuickSight, Lake Formation, EMR, OpenSearch, Data Firehose |

## Container Hierarchy & Styling

Nesting order (outermost to innermost):
```
AWS Cloud > Region > VPC > Availability Zone > Subnet > Service Icons
```

| Container | Border | Fill | Header |
|-----------|--------|------|--------|
| AWS Cloud | solid #232F3E 2px, rx=8 | none | dark bg, white text |
| Region | dashed #00A4A6 1.5px | none | teal bg, white text |
| VPC | solid #8C4FFF 1.5px | none | purple bg, white text |
| AZ | dashed #147EBA 1px | none | text label only |
| Public Subnet | solid #7AA116 1px | #E8F5E9/50% | green bg, white text |
| Private Subnet | solid #147EBA 1px | #E3F2FD/50% | blue bg, white text |
| Security Group | dashed #DD344C 1px | none | red text label |
| Auto Scaling | dashed #ED7100 1px | none | orange text label |
| Generic | solid #AEB6BF 1px, rx=4 | none | gray text label |

**Generic container tip:** For high-level diagrams, use `"type": "generic"` with descriptive labels to group related services without implying infrastructure boundaries.

## Arrow Rules (AWS Architecture Icon Deck)

**ALL arrows use straight lines and right angles.** This is enforced by the Python engine.

- **Style:** Open Arrow, stroke-width 2, color `#545B64` (light) / `#D5DBDB` (dark)
- **Routing:** Horizontal + vertical segments ONLY (M/L path commands, no curves)
- **Diagonal:** ONLY when right angles are impossible (rare edge case)
- **Endpoints:** Connect to CENTER of icon edge (not corners)
- **Parallel arrows:** Offset by >= 15px
- **Labels:** Italic, above the arrow line, >= 15px from callout circles
- **Numbered callouts:** Black circles (#232F3E) with white bold numbers
- **Custom colors:** Use `color` field (hex) for category-matched arrows (e.g., `#8C4FFF` for networking). Arrowhead markers auto-match the arrow color.
- **Forced ports:** Use `source_port`/`target_port` to control which edge arrows exit/enter. Useful when multiple arrows share a node.
- **Title bar avoidance:** Arrows auto-reroute below container title bars (VPC, AWS Cloud, Subnet headers).
- **Multi-arrow separation:** When multiple arrows exit the same icon, assign different ports (top=monitoring, right=main flow, bottom=data, left=bus pattern).

### Arrow Style by Diagram Type

| Diagram Type | Default Arrow Style |
|-------------|-------------------|
| Infrastructure | Solid gray `#545B64`, numbered steps for request flow |
| High-Level | Mix of solid (traffic) + dashed (internal/async), descriptive labels instead of step numbers |

### Arrow Semantics

| Arrow Style | Use For | Example |
|------------|---------|---------|
| Solid | Direct traffic flow, synchronous calls | Users → CloudFront, API GW → Lambda |
| Dashed | Async, internal, sidecar associations | Auth check, monitoring, event notifications |
| Bidirectional | Two-way data exchange | DynamoDB Streams, WebSocket, sync replication |

## Icon Labels (AWS Architecture Icon Deck)

- Font: 12pt Arial (Amazon Ember when available)
- Max 2 lines, "Amazon" or "AWS" prefix on first line
- Centered below icon with 12px gap
- Lines must NOT break mid-word

## Sub-Agent Strategy (Complex Diagrams)

For diagrams with 8+ services, use sub-agents to speed up the workflow:

```
# Sub-agent 1: Generate the JSON diagram definition
"Analyze the user request and create a JSON diagram definition
following the aws-diagram schema. Services: [list]. Save to /tmp/diagram.json"

# Sub-agent 2: Run the Python engine (after JSON is ready)
"Run: python3 scripts/generate_diagram.py -i /tmp/diagram.json -o output.svg --png --pptx output.pptx"

# Sub-agent 3: QA inspection (after SVG/PNG are ready)
"Visually inspect the PNG. Check: arrows are orthogonal, no overlaps,
containers nested correctly, labels readable. Report issues."
```

## Architecture Pattern Examples

See `examples/` directory for complete JSON definitions:

| Pattern | File | Services | Type |
|---------|------|----------|------|
| 3-Tier Web (Multi-AZ) | `examples/3-tier-web.json` | CloudFront, ALB, EC2, RDS | Infrastructure |
| Serverless API | `examples/serverless-api.json` | API GW, Lambda, DynamoDB, Cognito | Infrastructure |
| Data Pipeline | `examples/data-pipeline.json` | S3, Glue, Kinesis, Redshift, QuickSight | High-Level |
| Static Website | `examples/static-website.json` | CloudFront, S3, Route 53 | High-Level |

### Additional Patterns

| Pattern | Strategy | Key Services |
|---------|----------|-------------|
| AI Agent Platform | Hub-spoke, generic container | Bedrock, AgentCore, Lambda, API GW |
| Event-Driven | Central bus (EventBridge), producers left/consumers right | EventBridge, SQS, Lambda, ECS |
| RAG Pipeline | Left-to-right chain | S3, Bedrock KB, OpenSearch, API GW |
| CI/CD Pipeline | Horizontal chain | CodeCommit, CodeBuild, CodeDeploy, ECR |

---

## Icon Catalog (150+ icons)

Service icons are in `icons/` directory. Use the filename (without .svg) as the `service` field in JSON nodes.

**Compute:** ec2, lambda, ecs, eks, fargate, elastic-beanstalk, batch, app-runner, lightsail, auto-scaling, ecr, ec2-auto-scaling, ec2-image-builder, ecs-anywhere, eks-anywhere, compute-optimizer
**Storage:** s3, ebs, efs, fsx, storage-gateway, s3-glacier, backup, datasync
**Database:** rds, dynamodb, aurora, elasticache, redshift, neptune, documentdb, memorydb, dms
**Networking:** vpc, cloudfront, route53, api-gateway, elb, direct-connect, global-accelerator, transit-gateway, vpc-lattice, privatelink, client-vpn, cloud-wan, cloud-map, app-mesh, efa
**Security:** iam, waf, shield, kms, secrets-manager, acm, cognito, guardduty, security-hub, detective, audit-manager, cloudhsm, directory-service, artifact
**App Integration:** sqs, sns, eventbridge, step-functions, appsync, mq, appflow, b2b-data-interchange
**AI/ML:** bedrock, sagemaker, rekognition, textract, comprehend, comprehend-medical, lex, q, augmented-ai, deepracer, elastic-inference
**Management:** cloudwatch, cloudformation, cloudtrail, systems-manager, config, organizations, x-ray, control-tower, devops-guru, appconfig, chatbot, cloud-control-api, cloudshell
**Analytics:** athena, glue, kinesis, quicksight, lake-formation, emr, opensearch, data-firehose, data-exchange, datazone, clean-rooms, cloudsearch
**Developer:** codepipeline, codebuild, codecommit, codedeploy, codeartifact, codecatalyst, codeguru, cloud9, cli, cdk, application-composer
**Migration:** application-migration, application-discovery, disaster-recovery
**Frontend/Mobile:** amplify, device-farm, appstream
**Other:** connect, chime, chime-sdk, braket, deadline-cloud, cost-explorer, budgets, billing-conductor, cost-usage-report

**Group icons:** group-aws-cloud, group-region, group-vpc, group-public-subnet, group-private-subnet, group-auto-scaling, group-aws-account, group-ec2-instance, group-datacenter

## External Elements

For non-AWS elements, use these service IDs in nodes:
- `users` - User/client icon (person silhouette)
- `internet` - Globe icon
- `on-premises` - Corporate data center box

For elements without pre-built icons, use a nearby AWS icon with a descriptive `sublabel`:
- SDK/Framework: use `cli` icon with sublabel "Agentic SDK"
- Custom tool: use `lambda` icon with sublabel "Custom Tool"
- Third-party API: use `internet` icon with sublabel "External API"

## Dark Theme

Set `"theme": "dark"` for AWS Squid Ink (#232F3E) background. Use for blog hero images, conference slides, social media. Arrows auto-switch to `#D5DBDB`, callouts invert to white, container borders use lighter variants (VPC: `#A97BFF`, Region: `#00D4D7`), subnet fills use dark variants (`#1B3A1B`, `#1A2A3A`).

---

## Hard Rules (MUST follow)

These are non-negotiable rules. Violating them produces architecturally incorrect or visually broken diagrams.

### AWS Service Relationship Rules
- **WAF is always attached TO CloudFront (or ALB)** -- WAF is an inline filter, NOT a separate hop in the traffic flow. Show WAF co-located with CF (same x, adjacent y) with a short dashed association line. NEVER draw Users->CF->WAF->APIGW as if WAF is a proxy.
- **CloudFront -> WAF direction is WRONG.** If showing the association, draw it as WAF->CF (WAF feeds into CF) or just place them side-by-side with a bidirectional dashed line.
- **Cognito is an auth sidecar, not in the traffic path.** Always connect APIGW->Cognito as a dashed "Auth" line exiting from APIGW's LEFT or TOP port. Never place Cognito in the main left-to-right traffic flow.
- **Services outside VPC must NOT touch VPC/Subnet borders.** SQS, S3, Bedrock, Step Functions are regional services -- they must have >= 30px visual gap from any VPC or Subnet border line.
- **AgentCore sub-services are internal** -- CodeInterpreter, Identity, Memory, Gateway, Observability are part of AgentCore Runtime. Group them inside a single generic container with dashed border.

### Arrow-Icon Collision Rules
- **Arrows must NEVER cross over service icons.** The orthogonal router performs obstacle avoidance (up to 3 iterations), but if an arrow still visually overlaps an icon in the rendered PNG, fix it by:
  1. Forcing `source_port`/`target_port` to route the arrow around the obstacle icon
  2. Moving the obstacle node to a different grid position to clear the path
  3. Adding an intermediate waypoint by splitting the connection into two segments via a relay node
- **Arrow segments must maintain >= 10px clearance** from any icon bounding box (icon + label area). The engine's `OBSTACLE_CLEARANCE = 10` enforces this, but verify in PNG output.
- **In hub-spoke layouts, radial arrows must not cross sibling spokes.** Place spoke services at staggered y-positions and use explicit ports to avoid crossings.

### Arrow Port Rules
- **One node, max 3 outgoing arrows.** If a node needs more, consolidate via intermediate services (e.g., EKS->SQS->StepFn->Bedrock instead of EKS->Bedrock directly).
- **No two arrows may exit the same port to different targets.** Each outgoing arrow must use a DIFFERENT port (top/right/bottom/left). If two targets are to the right, place them at different y-coordinates so one uses `right` port and the other uses `top` or `bottom` port with an L-shaped route.
- **Arrow routing midpoints must NOT coincide with container border edges.** Maintain >= 20px gap between any arrow segment and any container rect border.
- **Obvious connections need no labels.** ALB->EKS, APIGW->ALB are self-explanatory. Only label non-obvious flows: Auth, Async, SQL, Files, AI Inference.
- **Prefer horizontal straight arrows.** Place target nodes at the SAME y-coordinate as the source whenever possible. A horizontal arrow is always cleaner than an L-shaped route.

### Container Sizing Rules
- **VPC should comfortably wrap its subnets** -- not too tight (cramped), not too loose (wasteful). Aim for ~30px padding around the outermost subnet edges.
- **Subnet boxes should fit their icons with comfortable padding** (~25px each side). Not stretched to grid column width, but not so tight that labels clip.
- **VPC border must end BEFORE outside-VPC services.** If services at x=5 are outside VPC, the VPC right edge must be at least 30px left of x=5 icon positions.

### VPC Inside/Outside Separation Rules (Grid Gap)
Outside-VPC services (S3, SQS, EventBridge, Step Functions, Bedrock, CodeBuild, etc.) often overlap with VPC/Subnet container borders when placed at adjacent grid positions. This is the most common layout defect.

- **MUST skip at least 1 grid column** between the rightmost VPC node and the first outside-VPC node. Example: if VPC nodes end at x=5, outside-VPC nodes must start at x=7 (skip x=6).
- **Outside-VPC nodes must NOT share the same y as Subnet-edge nodes.** If the App Subnet contains nodes at y=3, do not place outside-VPC services at y=3 in the adjacent column -- use y=2 or y=4 instead to avoid the Subnet border visually touching or overlapping the external icon.
- **Above-VPC services (same x as VPC nodes) also overlap.** If a VPC node is at (x=5, y=3), placing an outside-VPC service at (x=5, y=1) will cause it to sit directly above the VPC border. Move it to x=7 instead.
- **Verify with PNG inspection** -- after generation, visually confirm that no outside-VPC icon touches any VPC/Subnet rectangle border.

### Post-Generation Verification (MANDATORY)
After every diagram generation, **read the PNG file** and visually verify:
1. All icons are fully inside their assigned containers
2. No arrow lines overlap with container borders
3. No labels are clipped at viewBox edges
4. External icons (users, internet, on-premises) actually render (not blank)

---

## Design Guidelines (SHOULD follow)

These are soft recommendations that improve quality. They can be relaxed based on context.

### Diagram Type Selection
- **10+ services with VPC/Subnet boundaries:** Infrastructure diagram
- **Platform overview, service interactions, executive presentation:** High-Level diagram
- **When in doubt:** Ask the user. Default to High-Level for presentations, Infrastructure for engineering docs.

### Container Minimalism
- **Infrastructure diagrams:** Always include the AWS Cloud container as the outermost boundary. Keep VPC compact with thin border.
- **High-Level diagrams:** Omit AWS Cloud container. Use `generic` containers only for logical platform groupings (e.g., "Bedrock AgentCore", "Data Processing Layer").
- If AWS Cloud container IS used, it should encompass all AWS services with generous right margin (+80px beyond rightmost icon label).

### Node Selection
- **Only show core infrastructure as icons** (EKS, RDS, S3, ALB, API Gateway, etc.). Supporting/operational services (CloudWatch, ECR, CodePipeline, Secrets Manager) can be omitted and noted in documentation.
- **WAF and Cognito: always show as separate icons.** They are core security components. WAF goes below CloudFront (same x, y+2). Cognito goes below CF (same x, y+1). Do NOT merge them into CloudFront's sublabel.
- **AI/ML services** (Bedrock, SageMaker): show as icons if they have explicit connections in the architecture. Only use text labels if they are tangential to the main flow.
- **Aim for 10-15 nodes max.** Beyond that, split into multiple diagrams.

### Spacing and Readability
- **White space = readability.** Generous spacing between service groups is more important than fitting everything compactly.
- **Outside-VPC services must align horizontally with their source.** Place SQS at the same y as EKS-App if EKS-App->SQS is a connection. This guarantees horizontal straight arrows instead of L-shaped routes.
- **Pipeline chains (StepFn->Bedrock) should be horizontal.** Place them at the same y, adjacent x, at the bottom of the diagram.

### Arrow Style
- **Default: consistent gray (`#545B64`) for all arrows.** This is cleaner than per-category colors. Only use colored arrows when the diagram explicitly needs to distinguish data flow types AND the user requests it.
- **Dashed lines for non-traffic associations**: Auth (Cognito), WAF integration, monitoring (CloudWatch), secrets retrieval.
- **Solid lines for traffic flow**: User requests, API calls, data queries.

### Title Layout
- **Single-line title** with subtitle inline (smaller font, gray) is more compact than two separate lines.

### Recommended Grid Layout: Infrastructure

```
x=0: External (Users at y=2)
x=1: Edge + Auth + Security
      CF (y=1), Cognito (y=2), WAF (y=3)  -- CF->Cognito->WAF top-to-bottom
x=2: API Gateway + Routing
      APIGW (y=2)
x=3~5: VPC Resources [Private Subnets]
      Lambda/EKS-CP (y=1), RDS (y=2), NLB/ALB/ECS (y=3)
x=6: (EMPTY -- gap column for VPC boundary separation)
x=7: Integration (outside VPC)
      EventBridge (y=1), S3 (y=2)  -- different y from Subnet-edge nodes
x=8~9: Pipeline
      StepFn (y=1), CodeBuild (y=1)  -- horizontal chain
```

### Recommended Grid Layout: High-Level (Hub-Spoke)

```
x=0: External clients (Users y=2, Mobile y=3)
x=1: Entry + Auth
      Amplify/CF (y=2), Cognito (y=1)
x=2: API + Central Hub
      Top chain: API GW (y=0) -> Lambda (y=0) -> DynamoDB (y=0)
      Hub: Central service (y=2) inside generic dashed container
x=3: Spoke services (radiate from hub)
      Service-A (y=1), Service-B (y=2), Service-C (y=3)
x=4: External integrations
      IdP (y=1), Custom Tool (y=3)
Bottom row (y=5): Observability
      CloudWatch (x=2), X-Ray (x=3)
```

**Key principles (both types):**
- y-range: 0-3 for core flow, extend to y=4-5 for pipeline/async/observability.
- **Skip 1 grid column** between VPC and outside-VPC services to prevent border overlap.
- **Outside-VPC services at DIFFERENT y from Subnet-edge nodes.**
- CF, Cognito, WAF in same column (x=1), stacked vertically in that order.
- Cognito at same y as APIGW for clean horizontal "Auth" dashed arrow.
- Prefer **wide** (landscape) layout over tall (portrait) for presentation slides.
- **viewBox margin**: always add +150px right margin beyond the rightmost node to prevent label clipping.

---

## QA Checklist

After generating:
- [ ] All arrows are orthogonal (no diagonal lines)
- [ ] No element overlap (icons, labels, containers)
- [ ] Container nesting is correct
- [ ] Icon labels are readable (12pt, max 2 lines)
- [ ] Arrow labels don't overlap with callout circles
- [ ] Colors match AWS category palette
- [ ] viewBox fits all elements with margin
- [ ] **Arrow-icon collision** -- no arrow line crosses over any service icon (>= 10px clearance)
- [ ] **SVG layer order** -- icons render ABOVE arrows (icons are topmost layer)
- [ ] **Arrow edge alignment** -- all path M/L values match icon edge_center coordinates
- [ ] **Title bar clearance** -- no arrows cross container header bars
- [ ] **Multi-arrow separation** -- arrows from same icon use different edge ports (no overlap)
- [ ] **Callout spacing** -- number circles have >= 15px gap from text labels
- [ ] **Marker color match** -- arrow color and arrowhead marker color are identical
- [ ] **Container-arrow separation** -- arrow routing midpoints do NOT coincide with container border edges (>= 15px gap)
- [ ] **Right-edge label visibility** -- labels on rightmost column nodes are fully visible within viewBox
- [ ] **External icon rendering** -- users, internet, on-premises icons render correctly (not blank)
- [ ] **VPC boundary gap** -- outside-VPC services have at least 1 empty grid column gap from VPC nodes (no border overlap)
- [ ] **Subnet-edge y separation** -- outside-VPC services do NOT share the same y as Subnet-edge nodes in adjacent columns

---

## Troubleshooting

For common pitfalls (VPC overlap, label clipping, arrow crossings) and
post-generation SVG fixes, see `references/troubleshooting.md`.

---

## Output & Dependencies

Default output: `docs/architecture.{svg,png,pptx}`. Dependencies: Python 3 (Pillow, python-pptx, lxml), rsvg-convert, icons/ directory (150+ SVG, CC-BY-4.0).

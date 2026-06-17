# Native PPTX Workflow (hand-coordinate path)

When the deliverable is an **editable PowerPoint slide** (customer will move
shapes, tweak labels), use `scripts/pptx_native_lib.py` and write a small
build script with explicit inch coordinates. Do NOT use
`generate_diagram.py --pptx` for this — see "Why not the automated
exporter" below.

## Why not the automated exporter

Field evidence (a customer SAP architecture, 12 nodes / 5
containers / 12 connections, Korean labels): `--pptx` output had 20 visual
defects on independent inspection — container borders piercing icons,
container labels orphaned outside their boxes, a vertical dashed arrow
slicing through an icon and its label, CJK labels wrapped to 3 lines, a
purple bidirectional arrow rendered as two gray fragments. Root causes are
structural, not bugs to patch around:

- The px→EMU translation inherits the SVG layout's ignorance of **rendered
  text extents** — and CJK text runs ~1.7× wider than the Latin metrics
  assumed.
- Orthogonal auto-routing decides corridor positions without knowing where
  PPTX label boxes land.

A hand-coordinate rebuild of the same diagram (62 shapes) rendered clean on
the first full pass and took one QA iteration. For editable-PPTX work the
hand path is both faster and better.

## Workflow

```
1. Rasterize the icons you need (once per project)
2. Write build script using NativeSlideBuilder  ← layout rules below
3. Render via LibreOffice → JPEG
4. QA the JPEG with a SUBAGENT (fresh eyes — you will see what you
   expect, not what's there)
5. Fix coordinates, re-render, repeat until a pass finds nothing
```

### 1. Rasterize icons

```python
from pptx_native_lib import rasterize_icons
rasterize_icons(["lambda", "s3", "athena"], svg_dir="<skill>/icons")
```

### 2. Build script skeleton

```python
from pptx_native_lib import NativeSlideBuilder, DARK, PURPLE

b = NativeSlideBuilder()
b.title("Customer x AWS — Architecture (Draft)", "subtitle · date · 논의용")

# containers FIRST (z-order bottom). Outermost = dark_header.
b.container(4.20, 1.20, 11.50, 6.65, "고객 AWS 계정",
            border_color=DARK, width_pt=1.75, dark_header=True)
b.container(4.45, 1.55, 7.55, 4.35, "데이터 레이크")

# lines SECOND. L/Z routes = 2-3 calls, arrowhead on last segment only.
b.line(7.11, 3.40, 8.31, 3.40, tail=True)            # S3 → AgentCore
b.line(8.65, 3.06, 8.65, 2.10, dashed=True)           # ┐ L-route
b.line(8.65, 2.10, 10.11, 2.10, dashed=True, tail=True)  # ┘ to Bedrock

# labels THIRD (white fill masks the line behind them)
b.arrow_label(7.72, 3.18, "RAG · 분석", w=1.0)

# nodes LAST (z-order top)
b.node(6.80, 3.40, "s3", "Amazon S3", "데이터 레이크")
b.node(8.65, 3.40, "bedrock-agentcore", "AgentCore Runtime", "AI Agent · MCP")

b.save("out.pptx")
```

Keep the build script in the project (`arch/build_native_slide.py` style) —
it is the editable source of truth; rerunning it regenerates the deck.

## Layout rules (each one maps to an observed defect)

| Rule | Defect it prevents |
|------|--------------------|
| Node pitch: horizontal ≥ 1.55in, vertical ≥ 1.25in center-to-center | 1.4in label boxes colliding / label overlapping icon below |
| Container edges ≥ 0.25in clear of foreign icons (icon spans center ± 0.31in) | account border slicing through SAP BDC/BPA icons |
| Container label = part of `container()` call, never a separate floating textbox | "데이터 레이크" label orphaned outside its box |
| Vertical arrow from a node starts below the label block (cy + 0.9in) when text sits under the icon | dashed line spearing "AgentCore Runtime / AI Agent · MCP" |
| Arrow into a node from below stops ≥ 0.5in below center | arrowhead through label text |
| Route long return paths through empty canvas margin (e.g. x=0.33 west corridor) | return path overlapping container borders / labels |
| Human actors (users icon) OUTSIDE the cloud/account container | user icon floating inside account box |
| Bidirectional = one `line(head=True, tail=True)`, with explicit `color=` | two gray fragments instead of one purple arrow |

## 3-4. Render & subagent QA

```bash
soffice --headless --convert-to pdf out.pptx   # use scripts/office/soffice.py wrapper if sandboxed
pdftoppm -jpeg -r 130 out.pdf qa
```

Then spawn a subagent: "Visually inspect qa-1.jpg. Assume there are
defects — find them. Check: container/icon overlap, orphaned or misplaced
labels, arrows piercing icons or text, CJK labels wrapped to multiple
lines, arrow color/style mismatches, elements outside their logical
boundary." Inspecting your own layout fails reliably — you see the
intent, not the render. That session's 20 defects were all found
by a subagent after self-review passed the slide.

Fix → re-render → re-inspect until a full pass reports nothing. One
iteration is typical when starting from the layout rules above.

## Combining with the SVG path

A common deliverable is a 2-slide deck: slide 1 = high-res PNG embed (from
the SVG path — best-looking, presentation-safe), slide 2 = native shapes
(editable). Build slide 1 by `add_picture()` of the generated PNG with
aspect-preserving fit, then `NativeSlideBuilder(prs=prs)` adds slide 2 to
the same Presentation object.

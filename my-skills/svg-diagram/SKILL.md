---
name: svg-diagram
description: |
  Generate pixel-perfect SVG diagrams, banners, and architecture visualizations.
  No external tools needed — pure SVG markup with anti-overlap rules.
  Supports: architecture diagrams, flowcharts, hero banners, pipeline visuals,
  comparison charts, and README/Notion-ready graphics.
license: MIT License
metadata:
    skill-author: jesamkim
    version: 1.0.0
allowed-tools: [Read, Write, Edit, Bash]
---

# SVG Diagram Generator

Generate clean, professional SVG diagrams and banners with precise text positioning and zero element overlap.

## Core Principles

### 1. Canvas First
Always start with a fixed `viewBox`. Common sizes:
- **Banner**: `viewBox="0 0 800 300"` (wide, shallow)
- **Architecture**: `viewBox="0 0 800 520"` (wide, tall)
- **Flowchart**: `viewBox="0 0 600 800"` (narrow, very tall)
- **Comparison**: `viewBox="0 0 800 400"` (wide, medium)

### 2. Anti-Overlap Rules (CRITICAL)
These rules prevent the #1 problem in AI-generated SVGs:

```
RULE 1: Text Anchoring
  - Always use text-anchor="middle" with x at center of container
  - For left-aligned text, use text-anchor="start" with explicit x offset

RULE 2: Vertical Spacing
  - Minimum 40px between box elements
  - Minimum 15px between text lines (font-size 12-13)
  - Minimum 12px between text lines (font-size 9-10)
  - Text y-position = box_y + (box_height / 2) + (font_size / 3)

RULE 3: Horizontal Spacing
  - Minimum 10px gap between adjacent boxes
  - Arrow/connector labels centered between source and target
  - Never place text outside viewBox bounds

RULE 4: Container Padding
  - Text inside boxes: minimum 8px padding from all edges
  - Box width = text_width + 20px minimum
  - If text might overflow, use font-size 9 or truncate
```

### 3. Style Presets

Two presets available. **DEFAULT: vercel-stripe (light)** from 2026-04-30.

#### Preset A: vercel-stripe (LIGHT, DEFAULT)

Inspired by Vercel blog + Stripe docs. Use this for blog posts, docs,
architecture diagrams, product content.

**Reference SVG**: `vercel-stripe-reference.svg` (same directory).
READ THIS FIRST before generating — it demonstrates the exact conventions.

```xml
<!-- Canvas: pure white, NO gradient -->
fill="#FFFFFF"

<!-- Card gradient -->
<linearGradient id="cardBg" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0%" stop-color="#FFFFFF"/>
  <stop offset="100%" stop-color="#FAFAFA"/>
</linearGradient>

<!-- Hero black gradient (ONLY for main agent/orchestrator, max 1) -->
<linearGradient id="accentBlack" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0%" stop-color="#111111"/>
  <stop offset="100%" stop-color="#333333"/>
</linearGradient>

<!-- Data layer pastel -->
<linearGradient id="dataBg" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0%" stop-color="#F6F9FF"/>
  <stop offset="100%" stop-color="#EEF3FF"/>
</linearGradient>

Stripe purple:   #635BFF (primary accent)
Cyan:            #00D9FF (hero-inside label)
Teal:            #00B4A6 (secondary tool accent)
Green:           #10B981 (success, output)
Blue (cool):     #3B4FCC (data layer label)

Card border:     #E5E5EA (1px)
Data border:     #D6DFF5 (1px)
Divider:         #EAEAEA

Primary text:    #0A0A0A
Secondary text:  #6B6B75
Tertiary text:   #B0B0B8

Flow arrow:      #8C8C95, stroke-width 1.5, solid
Data-ref arrow:  #B8C5E8, stroke-width 1.2, dashed (4 4)
Return arrow:    #D6DFF5, stroke-width 1.5
Success arrow:   #10B981, stroke-width 1.5

<!-- Arrow marker -->
<marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5"
        markerWidth="6" markerHeight="6" orient="auto-start-reverse">
  <path d="M0,1 L9,5 L0,9 Z" fill="#8C8C95"/>
</marker>

<!-- Soft shadow (apply to ALL cards) -->
<filter id="softShadow" x="-20%" y="-20%" width="140%" height="140%">
  <feGaussianBlur in="SourceAlpha" stdDeviation="2"/>
  <feOffset dx="0" dy="2"/>
  <feComponentTransfer><feFuncA type="linear" slope="0.08"/></feComponentTransfer>
  <feMerge><feMergeNode/><feMergeNode in="SourceGraphic"/></feMerge>
</filter>

rx="12"  outer containers, hero cards
rx="10"  default cards
rx="8"   inner chips inside data layer

font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', 'Inter', sans-serif"
```

**Card types:**

| Type            | Fill              | Border            | Use                                  |
|-----------------|-------------------|-------------------|--------------------------------------|
| Default         | url(#cardBg)      | #E5E5EA 1px       | Input/output, generic nodes          |
| Hero (black)    | url(#accentBlack) | #000 1px          | **Main orchestrator — 1 per diagram** |
| Tool card       | url(#cardBg) + 4px left accent bar | #E5E5EA 1px | External tools, APIs      |
| Data card       | url(#dataBg)      | #D6DFF5 1px       | Data layer, storage                  |
| Inner chip      | #FFFFFF           | #D6DFF5 1px       | Sub-items inside data layer          |

**Typography:**
- Title: 22px, weight 700, letter-spacing -0.5, #0A0A0A
- Subtitle: 13px, weight 400, #6B6B75
- Category label: 11px, weight 600, letter-spacing 0.3em, UPPERCASE, accent color
- Node title: 14-15px, weight 600, #0A0A0A (or #FFFFFF on hero)
- Description: 12px, weight 400, #6B6B75 (or #A0A0AA on hero)
- Arrow annotation: 10px, weight 500, #6B6B75

**Arrow rules:**
- Start/end MUST snap to card edge (not center, not inside)
- Use cubic Bezier (C) for smooth curves between diagonal nodes — NOT quadratic
- Numbered flow labels: 1, 2, 3, 4 (or circled variants) near arrow start
- Don't route arrows over card bodies — go around
- Return flows: lighter gray #D6DFF5, optional dashed

#### Preset B: dark (LEGACY, explicit request only)

Only for conference slides, social thumbnails, or when user explicitly asks for dark.

```xml
<linearGradient id="bg">
  <stop offset="0%" style="stop-color:#0a0a2e"/>
  <stop offset="100%" style="stop-color:#1a1a3e"/>
</linearGradient>

Green:   #00d4aa, #00ff88
Blue:    #00a8ff, #00ccff
Orange:  #ff9900, #ffaa00
Red:     #ff4444
Purple:  #aa88ff, #ff44ff
Yellow:  #ffdd44
Gray:    #888, #555, #333
```

### 4. Typography

**vercel-stripe preset (default)**: sans-serif only
```xml
font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', 'Inter', sans-serif"
<!-- Titles: 18-24px, weight 700, #0A0A0A -->
<!-- Body: 12-14px, weight 400-600, #6B6B75 or #0A0A0A -->
<!-- Category labels: 11px, weight 600, uppercase, letter-spacing 0.3em -->
```

**dark preset (legacy)**: monospace
```xml
font-family="monospace" font-size="18-42" fill="white" font-weight="bold"
```

Never use serif fonts in technical diagrams. For Korean text use
`NanumSquareRound, -apple-system, sans-serif` to avoid cairosvg tofu.

## Templates

### Hero Banner Template
```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 300">
  <rect width="800" height="300" fill="url(#bg)" rx="12"/>

  <!-- Background decoration: grid, chart lines, particles -->
  <!-- Main title: y=110-120, font-size 36-42 -->
  <!-- Subtitle: y=150-160, font-size 14-16 -->
  <!-- Tech stack pills: y=180-210, evenly spaced -->
  <!-- Stats bar: y=245-255, font-size 12 -->
  <!-- Bottom accent line: y=272 -->
</svg>
```

### Architecture Diagram Template (vercel-stripe default)

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 520"
     font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', 'Inter', sans-serif">
  <defs>
    <!-- See vercel-stripe-reference.svg for full defs (gradients, marker, filter) -->
  </defs>
  <rect width="960" height="520" fill="#FFFFFF"/>

  <!-- Title block: x=40, y=50 (22px, weight 700) + subtitle y=74 (13px, #6B6B75) -->
  <!-- Divider line: y=92 at x=40-920, #EAEAEA -->
  <!-- Flow cards: x=40+, y=130-280 area -->
  <!-- Data layer card: x=540, y=340, 380x100 pastel blue -->
  <!-- Arrows: #8C8C95 1.5px, with url(#arrow) marker -->
  <!-- Watermark: x=920, y=500, text-anchor=end, 10px #B0B0B8 -->
</svg>
```

**Dark legacy template** (explicit request only):
```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 520">
  <rect width="800" height="520" fill="url(#bg)" rx="12"/>
  <!-- Title y=35, step boxes x=100 w=180 h=40 rx=8, arrows #333 -->
</svg>
```

### Pipeline Flow Template
```xml
<!-- Horizontal pipeline with boxes and arrows -->
<g transform="translate(START_X, Y)">
  <!-- Box 1 -->
  <rect x="0" y="0" width="W" height="36" rx="6" fill="BG" stroke="COLOR"/>
  <text x="W/2" y="13" text-anchor="middle" font-size="8" fill="COLOR">Label</text>
  <text x="W/2" y="25" text-anchor="middle" font-size="8" fill="COLOR">Detail</text>

  <!-- Arrow -->
  <text x="W+7" y="18" font-size="12" fill="#555">→</text>

  <!-- Box 2 at x = W + 20 -->
</g>
```

### Pill/Badge Template
```xml
<!-- Tech stack pill -->
<rect x="X" y="Y" width="120" height="24" rx="12"
  fill="#00d4aa" fill-opacity="0.15"
  stroke="#00d4aa" stroke-width="1" stroke-opacity="0.4"/>
<text x="X+60" y="Y+16" text-anchor="middle"
  font-family="monospace" font-size="11" fill="#00d4aa">Label</text>
```

## Checklist Before Output

Before writing the final SVG, verify:

- [ ] All text elements have explicit `text-anchor` and `x`, `y` coordinates
- [ ] No two elements share the same y-range at the same x-range
- [ ] All text fits within its container (check string length × ~6px per char at font-size 10)
- [ ] `viewBox` dimensions accommodate all elements with 20px+ margin
- [ ] Colors meet WCAG AA on white background (vercel-stripe default). Secondary text #6B6B75 passes at 12px+
- [ ] Font sizes: titles ≥18, labels ≥10, box text ≥8
- [ ] Arrow connectors are between steps, not overlapping content
- [ ] `rx` (border radius) is consistent: 12 for main bg, 8 for step boxes, 6 for pipeline boxes, 4 for pills

## Example Usage

"README에 넣을 프로젝트 히어로 배너 만들어줘"
→ Hero Banner Template + project name, tech stack, stats

"시스템 아키텍처 다이어그램 그려줘"
→ Architecture Diagram Template + components, data flow

"CI/CD 파이프라인 시각화해줘"
→ Pipeline Flow Template + stages, tools

"비교 차트 만들어줘 (A vs B)"
→ Side-by-side boxes with comparison metrics

## Output

Always save SVG files to the `docs/` directory:
```bash
docs/banner.svg
docs/architecture.svg
docs/pipeline.svg
```

Embed in README.md:
```markdown
<p align="center">
  <img src="docs/filename.svg" alt="Description" width="100%"/>
</p>
```

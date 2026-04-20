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

### 3. Dark Mode Compatible
Default palette (works on both light and dark backgrounds):

```xml
<!-- Background -->
<linearGradient id="bg">
  <stop offset="0%" style="stop-color:#0a0a2e"/>
  <stop offset="100%" style="stop-color:#1a1a3e"/>
</linearGradient>

<!-- Accent colors (high contrast on dark) -->
Green:   #00d4aa (primary), #00ff88 (bright)
Blue:    #00a8ff (primary), #00ccff (bright)
Orange:  #ff9900 (AWS), #ffaa00 (warning)
Red:     #ff4444 (error/bearish)
Purple:  #aa88ff (secondary), #ff44ff (AI/brain)
Yellow:  #ffdd44 (adaptive)
Gray:    #888 (labels), #555 (secondary), #333 (lines)
```

### 4. Typography
```xml
<!-- Titles -->
font-family="monospace, Courier" font-size="18-42" fill="white" font-weight="bold"

<!-- Labels -->
font-family="monospace" font-size="10-13" fill="#888"

<!-- Inside boxes -->
font-family="monospace" font-size="8-10" fill="<accent-color>"

<!-- Never use serif fonts in technical diagrams -->
```

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

### Architecture Diagram Template
```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 520">
  <rect width="800" height="520" fill="url(#bg)" rx="12"/>

  <!-- Title: y=35 -->
  <!-- Time labels: x=50, left column -->
  <!-- Step boxes: x=100, width=180, height=40, rx=8 -->
  <!-- Detail text: x=320+, right side -->
  <!-- Pipeline section: dashed border container -->
  <!-- Pipeline boxes: height=36, rx=6, evenly spaced -->
  <!-- Arrows: stroke="#333", between steps -->
  <!-- Monitoring sidebar: right side, separate box -->
  <!-- Footer: y=500 -->
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
- [ ] Colors are readable on dark backgrounds (#0a0a2e)
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

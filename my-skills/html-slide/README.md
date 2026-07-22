# HTML Slide — Keynote-Grade HTML Presentation Generator

Build presentation decks as a **single self-contained HTML file** — no build
step, no framework, no CDN-critical dependency. Open it in any browser and
present with the arrow keys. The output is designed to look like it came from a
keynote design studio, not a Bootstrap template.

Every rule in this skill traces back to killing the two chronic defects of
naive AI-generated HTML slides:

1. **Text too small** — web-page habits (16-24px body) leak into slides. Fixed
   by a **1920×1080 design-px stage** auto-scaled to any viewport, so a 40px
   body means 40px-at-1080p on a laptop, a projector, or a video-call tile.
2. **Boxy template sameness** — centered title + three grey cards + bullets,
   repeated N times. Fixed by committed art direction: one distinctive theme,
   layout variety enforced by the Mix Rule + Surface-variety rule, and
   typography as the hero.

## Features

- **Single self-contained file**: the deck is one `.html` — the engine JS
  (~120 lines) and all styles inline; the only external request is the Korean
  font CDN, with a full system fallback so it survives offline
- **Fixed 1920×1080 stage**: `transform: scale()` fits the stage to any
  viewport (letterboxed). No media queries, no responsive reflow — the designer
  controls exactly where every element sits, like PPTX/Keynote
- **Typography contract**: design-px scale (body 36-48px / min 30, headings
  64-80px, hero stats 280px+, section numerals 240-360px) that fixes the
  small-text defect; 1pt ≈ 2px @1080p
- **5 preset themes, varied per topic**: Midnight Keynote, Aurora Tech, Paper
  Editorial, Swiss Minimal, Terminal Mono — presets are starting points, never
  used verbatim (accent + display font varied per deck)
- **18-layout catalog with two anti-repetition rules**:
  - **Mix Rule** — never the same layout 3× in a row
  - **Surface-variety rule** — rounded `.cell` cards at most twice in a row;
    the third information group goes card-free or a chart, so a deck never
    collapses into "a few grey rounded boxes"
  - Includes **card-free layouts** (Ledger List, Indexed Definitions, Split
    Contrast) that build structure from hairline rules and whitespace, and
    **chart layouts** (Bar Chart, Donut/Pie + KPI)
- **Effects library — impact with restraint**: staggered rise, blur-reveal,
  product settle, gradient shimmer, mask wipe, count-up, Ken Burns, typewriter,
  Apple-style **pinned storytelling** (`:has()`-driven), exploded view, and
  **chart draw-on** (bars grow / lines draw / arcs sweep). Pick 2-3 signature
  effects per deck and reuse them
- **Accessible & no-JS-safe**: `prefers-reduced-motion` kills animation globally
  while every effect settles to its real end-state, so a deck with motion
  disabled (or JS off) still shows finished content, charts included
- **Built-in navigation**: keyboard (←/→/Space/Home/End), touch swipe,
  click-to-advance, `data-step` fragment builds, URL hash routing (`#5`),
  progress bar, `f` fullscreen
- **Three AWS branding modes**: `customer-session` (AWS-style cover + branded
  footer on every slide + Amazon Ember / Nanum Gothic fonts, all embedded),
  `logo-only` (smile logo on the title slide), and `none`
- **Source citations** for share-out decks: per-slide attribution with real
  clickable `<a href>` links, placed above the footer band and clear of the
  page counter

## Quick Start

```bash
# Trigger with:
/html-slide
# or natural language:
#   "html 슬라이드 만들어줘", "html presentation", "브라우저 슬라이드"
#   "임팩트 있는 슬라이드", "애니메이션 슬라이드", "keynote in browser"
```

The skill gathers topic, audience, slide count, language, AWS branding mode,
and the presenter's name and title/role (asked interactively — never assumed;
the presentation date defaults to today), then (for 6+ slides) proposes a
one-screen design spec for approval before building the single `.html` file.

## Themes

| Theme | Mood | Default for |
|-------|------|-------------|
| **Midnight Keynote** | near-black, huge white type, one gradient accent | product launch, keynote, "임팩트" |
| **Aurora Tech** | deep navy, aurora gradient mesh, glassy cards | AI/cloud tech talks, demos |
| **Paper Editorial** | warm paper, serif display, ink text | strategy, storytelling, exec audience |
| **Swiss Minimal** | white, visible grid, one hard accent | data-heavy, portfolio, design review |
| **Terminal Mono** | CRT dark, monospace, scanline texture | engineering deep-dive, CLI/devtools |

Variation is mandatory: change at least the accent color + display font pairing
per topic. Two decks from this skill should never look like siblings unless the
user asks for a series. Each deck stays within ≤ 5 colors.

## Layout Catalog

18 layouts, chosen per slide under the Mix Rule and Surface-variety rule:

- **Structural**: Title, Section Divider, Big Statement, Hero Stat, Two-Column
  Asymmetric (35/65), Quote, Timeline/Steps, Code Walkthrough, Image Full Bleed,
  Closing
- **Card**: Bento Grid, Card Row, Comparison
- **Card-free** (hairline rules + whitespace, no card fills): Ledger List,
  Indexed Definitions, Split Contrast
- **Chart** (hand-authored inline SVG, paired with chart draw-on): Bar Chart,
  Donut/Pie + KPI

## Directory Structure

```
html-slide/
├── SKILL.md                  # main skill instructions
├── README.md                 # this file
├── LICENSE.txt               # MIT
├── references/
│   ├── engine.md             # self-contained HTML skeleton (do not modify)
│   ├── themes.md             # 5 preset token blocks + variation notes
│   ├── layouts.md            # 18-layout catalog + Mix / Surface-variety rules
│   └── effects.md            # effects library (A1-A9, steps, ambient)
├── assets/
│   ├── aws-logo-white.png    # for dark themes
│   ├── aws-logo-dark.png     # for light themes
│   └── fonts/                # Amazon Ember (Lt/Rg/Bd) for customer-session mode
└── evals/
    └── evals.json
```

## How It Works

1. **Engine skeleton** (`references/engine.md`) provides the fixed-stage
   scaling, navigation, step builds, hash routing, and progress UI. It is
   copied verbatim — only theme tokens, slide `<section>` markup, and effect
   classes are written on top.
2. **Theme tokens** are a single `:root` CSS variable block, customized per
   topic.
3. **Slides** are `<section class="slide" id="sN">` blocks; edits locate a block
   by id or heading and change only that block.
4. **QA** runs against the checklist in `SKILL.md` (text overflow, body ≥ 30px,
   contrast, Mix Rule, Surface-variety, keyboard nav, Korean line breaks
   and 존댓말 tone, single-file size < 2MB, branding correctness).

## Dependencies

None to install. The deck itself needs only a browser. Authoring/QA uses a
headless Chromium (via `agent-browser` or Playwright) to screenshot slides at
1920×1080 and 1280×720.

## Version

**1.4.0** — added the chart draw-on effect (A9: bars/lines/donut), card-free
layouts (Ledger List, Indexed Definitions, Split Contrast) and chart layouts
(Bar Chart, Donut/Pie + KPI), and the Surface-variety rule that breaks up
card-heavy decks.

## License

MIT License — see [LICENSE.txt](LICENSE.txt). Copyright (c) 2026 Jesam Kim.

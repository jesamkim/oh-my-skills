---
name: html-slide
description: |
  Create stunning, self-contained HTML slide decks (single .html file, zero
  dependencies) with keynote-grade typography, preset design themes, and
  impactful visual effects including Apple.com-style product-reveal
  techniques. Fixes the two chronic defects of naive AI-generated HTML
  slides: tiny text and boxy template sameness. Every deck renders on a
  fixed 1920x1080 stage auto-scaled to any viewport, with keyboard/touch
  navigation, step-by-step builds, progress bar, and URL hash routing
  built in. Five preset themes (Midnight Keynote,
  Aurora Tech, Paper Editorial, Swiss Minimal, Terminal Mono) that get
  customized per topic — never used verbatim. Use this skill whenever the
  user wants a presentation as HTML/web slides, a browser-viewable deck,
  an animated keynote, scrollytelling-style product intro slides, or says
  they want slides but the deliverable is HTML (not PPTX — that's myslide).
  Trigger: "html slide", "html 슬라이드", "web slides", "웹 슬라이드",
  "html presentation", "html로 발표자료", "브라우저 슬라이드",
  "html-slide", "html 덱", "reveal 스타일", "keynote in browser",
  "애니메이션 슬라이드", "임팩트 있는 슬라이드"
license: MIT License
metadata:
  skill-author: Jesam Kim
  version: 1.4.0
allowed-tools: [Read, Write, Edit, Bash, Grep, Glob, Agent, AskUserQuestion]
---

# HTML Slide — Keynote-Grade HTML Presentation Generator

Build presentation decks as a **single self-contained HTML file**: no build
step, no framework, no CDN-critical dependency. Open in any browser and
present with arrow keys. The output should look
like it was designed by a keynote design studio, not assembled from a
Bootstrap template.

## Why this skill exists (the two defects to kill)

Naive HTML slides fail in two predictable ways. Every rule in this skill
traces back to one of them:

1. **Text is too small.** Web-page habits (16-24px body) leak into slides.
   A slide is read from meters away, projected or shrunk into a video call
   tile. Slide typography starts where web typography ends.
2. **Boxy template sameness.** Centered title + three equal cards + bullet
   list, repeated N times, in Inter on a purple-gradient background. The
   fix is committed art direction: one distinctive theme, layout variety,
   and typography as the hero.

## Positioning vs sibling skills

| Deliverable | Skill |
|-------------|-------|
| **HTML deck** (browser, animation, single file) | **this skill** |
| PPTX (PowerPoint, AWS-themed) | `myslide` |
| Standalone SVG diagram/banner | `svg-diagram` |
| AWS architecture diagram | `aws-diagram` |

If the user says "슬라이드 만들어줘" without a format, ask once — HTML
(animated, browser) vs PPTX (editable, corporate). If they mention motion,
web, or "임팩트", default to HTML.

## Quick Start

1. Gather topic, audience, slide count, language (Korean/English/mixed) —
   and ask the AWS-branding + presenter questions (see § AWS Branding) in
   the same breath
2. Pick a theme from [references/themes.md](references/themes.md) and
   **customize it to the topic** (accent color, display font, texture) —
   presets are starting points, never final answers
3. For 6+ slides, write a 1-screen design spec first (table: # / layout /
   grammar / key message / effect) and get user approval — structural
   rework is the expensive kind
4. Build the deck on the engine skeleton in
   [references/engine.md](references/engine.md) — read it before writing
   any HTML; it contains the scaling, navigation, steps, and print
   machinery that must not be reinvented
5. Choose layouts per slide from [references/layouts.md](references/layouts.md)
   respecting the Mix Rule (below)
6. Add 2-3 signature effects from [references/effects.md](references/effects.md)
   — including the Apple-style reveal templates when the deck introduces a
   product/feature
7. Run the QA checklist (below), then deliver the single .html file

## Typography Contract (CRITICAL — this is the "small text" fix)

All sizes are px on the fixed 1920×1080 stage. The engine scales the whole
stage, so these are effectively viewport-proportional. Rule of thumb for
translating presentation-industry pt guidance: **1pt ≈ 2px @1080p**
(PowerPoint's 13.33in canvas mapped to 1920px) — so the classic "24pt
body minimum, Kawasaki's 30pt gold standard" lands at 48-60px here.

| Role | Size | Weight / notes |
|------|------|----------------|
| Deck title (title slide) | 112–176px | 700-800, line-height 1.02-1.08, letter-spacing -0.02em to -0.04em |
| Hero statement / big claim | 88–128px | one sentence max |
| Hero stat ("80%", "3x") | 280–420px | gradient or accent color |
| Section numeral ("01") | 240–360px | the numeral IS the visual |
| Slide heading (h2) | 64–80px | ≤ 2 lines |
| Subheading / lead | 40–48px | |
| Body & bullets | **36–48px, absolute minimum 30px** | line-height 1.5-1.6 (Korean: 1.6-1.7) |
| Code | 28–32px monospace | ≤ 14 lines per slide |
| Eyebrow label | 22–28px | uppercase, letter-spacing 0.12-0.2em |
| Caption / footer / page number | 20–24px | this is the ONLY place ≤ 24px is allowed |

Use ≤ 3 text sizes per slide, stepped on a modular scale (×1.25 Major
Third or ×1.333 Perfect Fourth) rather than ad-hoc values — e.g.
36 → 48 → 64 → 80. Prefer the upper half of the body range for keynote/
exec decks; the lower half is for dense engineer content.

Text budget: **one idea per slide**. Heading ≤ 2 lines. Body ≤ 5 bullets
or ≤ 60 words. If content doesn't fit at minimum sizes, split the slide —
never shrink the font. Body text column ≤ 62% of stage width (readability,
not timidity).

**Why the fixed stage matters**: the browser's default 16px body is the
root cause of tiny slide text — the viewport grows but web-document type
does not. On the fixed 1920×1080 stage every px is a design px, so the
contract above holds identically on a 14" laptop, a projector, and a
video-call tile. Never use `rem`/`vh`/`vw` or browser-default sizes
inside slides.

## Space Budget (the "empty box" fix)

The sibling defect of small text: boxes drawn content-fit around small
type, leaving the stage mostly dead space (or, inverted, a giant box with
a lost caption inside). Rules:

- **Content covers 60-80% of the stage area** on standard content slides.
  Below 60%: scale typography up or enrich the layout — don't leave
  accidental voids. (Deliberate Big-Statement slides are the exception:
  their emptiness is designed, not leftover.)
- **Boxes are sized by the layout grid, not by their content.** A card in
  a 3-card row is 1/3 of the content band, full height — text fills the
  card, not the reverse. Sibling cards share identical dimensions (grid
  `1fr`), never shrink-wrapped individually.
- **Whitespace goes to margins and gutters** (page margin 96-120px,
  gutters 32-48px), not trapped inside or between boxes randomly.
- Fill ratio check: eyeball each slide at thumbnail size — if it reads as
  "small text island in a dark ocean", the space budget failed.

**Korean text**: `word-break: keep-all; line-break: strict;` on every text
container (plus `overflow-wrap: break-word` as a long-token safety valve).
Default Korean-capable stack: Pretendard (CDN with system fallback).
Korean is full-width square glyphs — give body text MORE leading than
Latin (1.6-1.7 vs 1.5) but tighten Korean display headlines to 1.15-1.25;
Korean display also reads ~5% larger than Latin at equal px.

**Text budget headline rule**: write slide titles as *action titles* —
full-sentence conclusions ("추론 비용이 구조적으로 꺾였습니다"), not topic
labels ("비용 현황"). The title should pass the glance test: reading
titles alone tells the deck's whole story.

**Korean tone — default to 존댓말 (honorific/polite) everywhere.** This is
the presenter speaking to an audience of customers and colleagues, so slide
copy carries the same courtesy as the spoken talk. Titles, headings, body,
captions, and closing lines all use polite endings (-습니다/-합니다/-됩니다,
noun phrases, or the polite 요-form) — the emphatic plain form (반말:
꺾였다 / 결정한다 / 움직이고 있다 / 제품이다) reads as terse and is the one
place naive slide copy most often slips, especially in punchy action-title
headings where the plain form *feels* stronger. It isn't: an honorific
action title ("추론 비용이 구조적으로 꺾였습니다", "런타임이 결정합니다",
"현장은 이미 움직이고 있습니다") lands with the same conviction and matches
the room. Short noun-phrase labels ("비용 현황", "도입 로드맵", "세 가지
통합 패턴") stay as-is — they read as neutral captions, not clipped
sentences, so they don't need a verb ending. Switch to plain form only when
the user explicitly asks for it (a punchy 반말 brand voice, a quote that was
actually said in 반말). English copy is unaffected.

**Korean naturalness — run a translationese sweep on every Korean deck.**
Tone (존댓말) being correct doesn't make the copy *natural*: the most common
field correction on Korean decks is not grammar but 번역투 — phrasing that
is a literal carry-over from the English tech idiom the deck was drafted
in. Users consistently rewrite these, so catch them before delivery. The
recurring offenders, all field-corrected at least once:

| Pattern | Example (bad → good) | Why it fails |
|---------|----------------------|--------------|
| **Untranslated jargon transliterated** | 노브(knob) 총정리 → 튜닝 포인트 총정리 / 조정 항목 | English-community shorthand ("knobs to tune") means nothing to a Korean audience; find the concept, not the word |
| **Direct calque of an English idiom** | 세 가지 축이 전부입니다 ("three axes is all") → 세 가지만 기억하시면 됩니다 | Grammatical but nobody says it; rewrite as what a presenter would actually *say* |
| **Stiff Sino-Korean compound where a plainer phrase exists** | 데이터 상주(residency) 요건 → 데이터 저장 요건 / 국내 데이터 저장이 필요한 | Direct dictionary translation of a compliance term reads bureaucratic; prefer the phrase Korean engineers use in conversation |
| **Same concept, two Korean renderings in one deck** | slide A "재순위화", slide B "리랭킹" → pick one (리랭킹) and keep it | Audiences read term changes as concept changes; do a find-pass for every loanword-vs-번역어 pair (리랭킹/재순위, 청킹/분할, 임베딩/벡터화…) |

The test for each suspicious phrase: *"발표자가 무대에서 이 문장을 소리 내어
말한다면 자연스러운가?"* If you'd never hear it spoken at a Korean tech
conference, rewrite it — meaning first, word second. When a term is
genuinely ambiguous (loanword vs 번역어 both plausible), prefer the form
the AWS Korean documentation/blog uses, and keep it consistent deck-wide.

This sweep is cheap: after the deck is drafted, re-read only the Korean
strings (titles → labels → body, in that order — titles are the most
visible and the most prone to calques because action-title pressure
invites literal translation). Fix in place before the visual QA pass.

## Theme Selection (preset + mandatory variation)

Full tokens in [references/themes.md](references/themes.md).

| Theme | Mood | Default for |
|-------|------|-------------|
| **Midnight Keynote** | near-black, huge white type, one gradient accent | product launch, keynote, "임팩트" requests |
| **Aurora Tech** | deep navy, aurora gradient mesh, glassy cards | AI/cloud tech talks, demos |
| **Paper Editorial** | warm paper, serif display, ink text | strategy, storytelling, exec audience |
| **Swiss Minimal** | white, grid-visible, one hard accent | data-heavy, portfolio, design review |
| **Terminal Mono** | CRT dark, monospace, scanline texture | engineering deep-dive, CLI/devtools |

**Variation is mandatory**: change at least accent color + display font
pairing to fit the topic before building. Two decks from this skill should
never look identical. Keep each deck to **≤ 5 colors total** (bg, surface,
text, muted, accent — gradient stops count as one accent family).

Never: Inter/Roboto/Arial as display font, purple-gradient-on-white,
default blue links, five competing accent colors.

## Layout Grammar & Mix Rule

Layout catalog with copy-paste HTML in
[references/layouts.md](references/layouts.md): Title, Section Divider,
Big Statement, Hero Stat, Two-Column Asymmetric (35/65), Bento Grid,
Card Row, Quote, Timeline/Steps, Comparison, Code Walkthrough, Image Full
Bleed, Closing, plus card-free layouts (Ledger List, Indexed Definitions,
Split Contrast) and chart layouts (Bar Chart, Donut/Pie + KPI).

**Mix Rule** (inherited from myslide, field-proven): never repeat the same
layout 3+ times in a row. Centered-symmetric layouts count as one implicit
grammar — break runs with an asymmetric split, a bento, or a margin-heavy
statement slide. In an 8+ deck use at least 4 distinct layouts.

**Surface-variety rule**: rounded `.cell` cards dominate the Bento, Card
Row, Comparison, and Code layouts — reach for them every slide and the deck
reads as repetitive grey boxes even when the Mix Rule passes. Use card
layouts at most twice in a row; make the third information group card-free
(Ledger List, Indexed Definitions, Split Contrast, Two-Column) or a chart.

Decoration discipline: typography and structural blocks are the visual
hero. Add decoration only where it carries information (a CTA band, a
section numeral). No random orbs, no thin gradient strips on every slide,
no icon confetti.

## Visual Effects (the "임팩트" layer)

Full library with code in [references/effects.md](references/effects.md).
Two categories:

**Slide-enter builds** — fire when a slide becomes active:
staggered rise, blur-reveal (Apple product-shot style), gradient headline
shimmer, count-up stats, mask wipe, Ken Burns on full-bleed images,
product settle (scale 1.06→1 + shadow bloom).

**In-slide steps** — `data-step` elements revealed one keypress at a time,
enabling Apple-style pinned storytelling: one persistent object on stage
whose state (transform/label/highlight) changes per step, like apple.com's
scroll-pinned product sections translated to keypress phases.

Restraint contract:
- Pick **2-3 signature effects per deck** and reuse them consistently —
  every-slide-different-effect reads as chaos, not craft
- One easing everywhere: `cubic-bezier(0.16, 1, 0.3, 1)`, entrances
  600-900ms, steps 300-500ms
- Every effect must respect `prefers-reduced-motion` (engine handles the
  global kill-switch; don't bypass it)
- Effects never gate content: with JS disabled or motion reduced, the deck
  must still show all content (animate FROM an offset TO the natural state,
  never the reverse)

## AWS Branding (ask before building)

Most decks from this skill represent AWS field work, but the right amount
of branding depends on who's in the room. Three modes — which one applies
is the user's call, not yours:

| Mode | What it means | Typical use |
|------|---------------|-------------|
| **customer-session** | Official AWS deck treatment: AWS-style cover + branded footer on every other slide | SA customer sessions, Summits, workshops |
| **logo-only** | Smile logo on the title slide top-left, nothing else | decks that want identification without ceremony |
| **none** | no AWS marks | non-AWS topics, internal scratch decks |

**Ask once, up front.** During requirements gathering fold both branding
questions into the one AskUserQuestion call from Quick Start step 1:

1. "AWS 브랜딩을 어떻게 할까요?" — options: **AWS 고객 세션 덱**
   (recommend when the audience is customers), **로고만**, **없음**.
2. Presenter name & role (drives the cover's presenter block and the
   closing slide) plus the presentation date. Never assume a presenter:
   ask for the name and the title/role as free-form input — there is no
   preset default person — and default the date to today (`YYYY-MM-DD`).

Skip a question when the request already answers it ("로고 넣어줘" →
logo-only, "고객 세션용이야" → customer-session, "로고 없이" → none;
presenter named in the prompt → use it; date in the prompt → use it, else
today). In unattended runs (subagent,
eval, headless) default to **none** and omit the presenter block unless
the prompt names a presenter — a missing logo or credit is a smaller
error than an unwanted or wrong one — unless the prompt itself picks a
mode.

### Assets & embedding (single-file rule still holds)

| File | For |
|------|-----|
| `assets/aws-logo-white.png` | dark themes — Midnight Keynote, Aurora Tech, Terminal Mono |
| `assets/aws-logo-dark.png` | light themes — Paper Editorial, Swiss Minimal |

Official artwork — never substitute look-alikes, redraw the smile,
recolor, stretch, or add glow/shadow. Aspect ratio ≈ 5:3 (800×478); size
by width only, and keep the logo on a background it reads on (white logo
needs a dark region beneath — watch full-bleed images).

Inline the ONE variant the theme needs as a base64 data URI
(`base64 -i <skill-dir>/assets/aws-logo-white.png | tr -d '\n'`), defined
**exactly once** as a CSS custom property. This matters in
customer-session mode: the footer repeats on every slide, and repeating a
~70-100KB URI per slide is the fastest way to blow the 2MB budget.

```css
:root { --aws-logo: url("data:image/png;base64,…"); }  /* define ONCE */
```

### logo-only placement

- Title slide: top-left, aligned to the 96-120px page margin, width
  150-190px. This is the canonical spot; it also frees the bottom for
  presenter credit.
- Content slides: nothing, or quiet footer level — bottom-left, width
  100-130px, opacity .85. Never inside the content band.
- Closing slide: may sit above/beside the contact line, same size as title.

### customer-session anatomy (lineage: official AWS PPTX decks)

**Cover slide** mirrors the AWS deck cover — five fixed elements, stacked
top-to-bottom on the left: title → subtitle → date → presenter:

1. Logo top-left, page-margin aligned, width 150-190px (static block, not
   part of the bottom-anchored group)
2. Deck title flush-left at deck-title scale (112-176px), upper-middle;
   optional subtitle 36-44px muted directly beneath it
3. **Presentation date** directly under the title/subtitle block, 28-32px
   muted, ISO format `YYYY-MM-DD` (e.g. `2026-07-21`). Always include it —
   a dated cover reads as current; an undated one looks like a template.
   Ask the user for the date (default: today) during requirements
   gathering, alongside the presenter question.
4. Presenter block below the date: name 38-44px bold, role 30-34px muted on
   the next line
5. Copyright line bottom-left (`.aws-copyright`) — no footer logo on the
   cover; the big top-left logo already identifies the deck

Compose the title→subtitle→date→presenter as one left-aligned group in the
upper-to-middle band (not bottom-anchored) so the date and presenter sit
directly under the title rather than drifting to the slide's bottom edge.

**Every other slide** (content, section dividers, closing) carries the
footer as the section's last child:

```css
.aws-logo-cover { width: 170px; aspect-ratio: 800/478;
  background: var(--aws-logo) no-repeat left center / contain; }
.aws-footer { position: absolute; left: 120px; bottom: 36px; z-index: 40;
  display: flex; align-items: center; gap: 28px; }
.aws-footer::before { content: ""; flex: none; width: 64px;
  aspect-ratio: 800/478;
  background: var(--aws-logo) no-repeat center / contain; }
.aws-footer span, .aws-copyright { font-size: 20px; color: var(--muted); }
.aws-copyright { position: absolute; left: 120px; bottom: 36px; }
```

```html
<div class="aws-footer"><span>© 2026, Amazon Web Services, Inc. or its
affiliates. All rights reserved.</span></div>
```

### Source citations (per-slide, for share-out decks)

When a deck may be **shared after the session** (not just presented), each
slide must stand on its own — the audience reads it without the speaker.
Cite the source of any external claim, stat, screenshot, or quote in small
type on that slide, and make the deck self-explanatory (spell out acronyms
on first use, name the console path for how-to steps, note when a
screenshot continues on the next slide).

Citation placement — two hard rules, both field-corrected:

1. **Sit the citation ABOVE the footer band, nudged toward the body — never
   on the footer's baseline.** A cite sharing the `bottom` of `.aws-footer`
   / `#counter` reads as chrome and visually collides with the page number.
   Anchor it higher (`bottom: 88px` when a 36px footer is present) so it
   reads as a note on *this slide's content*.
2. **Right-align it, clearing the bottom-right `#counter`.** Keep `right`
   ≥ 120px and cap `max-width` so a long source list wraps to 2 lines
   rather than sliding under the page number.

```css
.cite { position: absolute; right: 120px; bottom: 88px; z-index: 40;
  font-size: 19px; color: var(--muted); opacity: .72;
  max-width: 1050px; text-align: right; line-height: 1.35; }
```

**Every URL in a citation (and in body/resource cards) MUST be a real
`<a href>` hyperlink**, not plain text — a shared HTML deck is clicked, not
retyped. Open external links in a new tab and keep them legible against the
dark surface:

```css
.cite a, .caption a { color: var(--muted); text-decoration: underline;
  text-underline-offset: 3px; text-decoration-thickness: 1px; }
.card a { color: inherit; text-decoration: underline; text-underline-offset: 4px; }
```
```html
<p class="cite">출처: <a href="https://aws.amazon.com/blogs/mt/…" target="_blank"
  rel="noopener">Cloud Operations Blog GA 발표 (2026-03-31)</a></p>
```

Keep each cite to the claim's true origin — attribute a customer quote to
the customer ("Deriv 사례 · 화면: 제품 PR 리뷰 리포트"), not to the deck it
was lifted from. Add a "자료 출처 —" summary block on the closing/resources
slide listing every source once. Never invent a URL: link only pages you
verified exist, and leave sourceless claims uncited rather than fabricating
attribution.

**Fonts** — customer-session decks use the AWS pairing: **Amazon Ember**
for Latin, **Nanum Gothic** for Korean.

Ember ships bundled with this skill (`assets/fonts/AmazonEmber_{Lt,Rg,Bd}.woff2`,
weights 300/400/700, ~36KB each) and must be **embedded as base64 data
URIs** — do NOT `src: url(https://a0.awsstatic.com/…)`: awsstatic serves
no `Access-Control-Allow-Origin` header and browsers enforce CORS on
cross-origin `@font-face`, so remote loading silently falls back. Only
those three weights exist publicly (Md/He return 403) — don't hunt for
others. Nanum Gothic stays a Google Fonts `<link>` (proper CORS, subset
serving; a full-Hangul embed would be megabytes).

```html
<link href="https://fonts.googleapis.com/css2?family=Nanum+Gothic:wght@400;700&display=swap" rel="stylesheet">
```
```css
/* base64: base64 -i <skill-dir>/assets/fonts/AmazonEmber_Rg.woff2 | tr -d '\n' */
@font-face { font-family: "Amazon Ember"; font-weight: 300; font-display: swap;
  src: url("data:font/woff2;base64,…") format("woff2"); }
@font-face { font-family: "Amazon Ember"; font-weight: 400; font-display: swap;
  src: url("data:font/woff2;base64,…") format("woff2"); }
@font-face { font-family: "Amazon Ember"; font-weight: 700; font-display: swap;
  src: url("data:font/woff2;base64,…") format("woff2"); }

:root {
  --font-display: "Amazon Ember", "Nanum Gothic", Pretendard, -apple-system, sans-serif;
  --font-body:    "Amazon Ember", "Nanum Gothic", Pretendard, -apple-system, sans-serif;
}
```

The three embeds add ~145KB — budget-safe, and Latin type now renders
offline too.

Ember carries Latin glyphs; Korean falls through to Nanum Gothic — one
stack covers mixed-script slides. Consequence of the 300/400/700 ceiling:
**cap `font-weight` at 700 in this mode** (the typography contract's
"700-800" becomes 700). Weight 800 would fake-bold Ember while Nanum
Gothic renders a true 800, making mixed headings visibly inconsistent.
AWS deck titles are Bold, not Black — 700 is the authentic look anyway.

Rules that keep it official-looking instead of cluttered:

- **Copyright text** (customer-facing default):
  `© <year>, Amazon Web Services, Inc. or its affiliates. All rights
  reserved.` Never append "Amazon Confidential and Trademark" on a
  customer deck — that marker means *internal*; add it only when the user
  explicitly says the deck is internal-only.
- **Page number**: the engine's `#counter` (bottom-right) already is the
  slide number — don't add a second one.
- **No layout changes needed**: the footer lives in the bottom 36-75px
  band, below the 96px content padding, so slide content is untouched.
- Official decks print this line at ~13px equivalent; that's below this
  skill's legibility floor. 20px — quiet but readable — is the floor here.
- Full-bleed image slides: check footer legibility (white smile on a
  bright region); add a subtle bottom scrim or omit the footer on that
  one slide.

## Engine Contract (do not reinvent)

The skeleton in [references/engine.md](references/engine.md) provides:

- Fixed 1920×1080 stage, `transform: scale()` fit-to-viewport (letterboxed)
- Keyboard (←/→/Space/Home/End), touch swipe, click-to-advance zones
- `data-step` fragment builds within a slide
- URL hash routing (`#5` = slide 5, shareable/resumable)
- Progress bar + `current/total` counter, `f` fullscreen
- Print stylesheet (fallback only): a `@media print` block exists so a deck
  degrades gracefully when printed, but browser print is unreliable —
  backgrounds, gradients, and effect end-states often drop or mangle, so it
  does NOT reproduce the deck faithfully. Don't advertise Ctrl+P as a delivery
  path; for a shareable static copy, screenshot each slide with headless
  Chromium at 1920×1080 instead
- `prefers-reduced-motion` global handling

Copy the skeleton, then write only: theme tokens (CSS variables), slide
`<section>` markup, and effect classes. The engine JS (~120 lines) is
final — modifying navigation/scaling logic is a bug source, not a feature.

## Workflow

### A. New deck

1. Requirements: topic, audience, count, language, tone ("임팩트" vs calm),
   AWS branding mode + presenter name/role (§ AWS Branding — one
   AskUserQuestion covers all of these)
2. **Spec gate** — 6+ slides: write spec table, wait for approval
   ("go"/"승인"/"OK"). 1-5 slides: proceed directly.
3. Build single .html (engine skeleton → theme tokens → slides → effects)
4. QA (below), fix, deliver file path + open instructions

### B. Editing an existing deck

Slides are `<section class="slide" id="s3">` blocks — locate by id or
heading text, edit that block only. Theme-wide changes go through the CSS
variables at the top, never per-slide inline styles.

### C. Large decks (10+ slides)

Parallelize with subagents by content section, one file part each; the
main agent owns theme tokens + engine and assembles. Give each subagent
the theme token block verbatim — divergent tokens are the #1 assembly
defect. Grouping by content area (not odd/even) makes failure recovery
cheap.

## QA Checklist (run before delivering)

Layout/served checks — open the file (agent-browser or playwright,
1920×1080 and 1280×720 viewports):

1. No text overflow/clipping on any slide (check longest-content slide)
1b. Display-scale wrap check — the failure mode QA exists for: a section
    numeral ("02") breaking onto a second line, a hero stat clipping, or
    a 100px+ headline orphaning one word/어절 onto its own line. Fix by
    `white-space: nowrap` (numerals/stats), manual `<br>` at phrase
    boundaries, or stepping the size down one notch — never by letting
    the browser wrap display type on its own
2. Body text ≥ 30px on stage; captions the only exception
2b. Space budget: content covers 60-80% of stage on content slides; no
    shrink-wrapped boxes floating in dead space (thumbnail eyeball test)
3. Contrast: body text ≥ 7:1 against background, large headings ≥ 4.5:1.
   Projector safety: avoid pure primaries for text (pure green ≈ 1.4:1 on
   white — unreadable); prefer off-white/near-black over pure #FFF/#000
4. Mix Rule holds (no 3-in-a-row layout repeats); Surface-variety holds
   (no 3+ card-`.cell` layouts in a row — break with a card-free or chart layout)
5. Keyboard nav works end-to-end; hash routing lands on the right slide
6. Steps (`data-step`) reveal in reading order
7. No content is gated behind an effect: with animation disabled
   (`prefers-reduced-motion`) every slide still shows its full content, none
   trapped in an un-run animation's start-state
8. Korean: no mid-word line breaks (keep-all applied); tone is 존댓말
   throughout — no plain-form (반말) sentence endings in titles, headings,
   body, or captions unless the user explicitly asked for plain form
8b. Korean naturalness sweep done (§ Korean naturalness): no transliterated
    jargon (노브…), no English-idiom calques (…이 전부입니다), no stiff
    compound where a plain phrase exists (상주→저장), one rendering per
    concept deck-wide (리랭킹 OR 재순위, not both) — titles first, they're
    the most calque-prone
8c. Closing slide is a single-page "감사합니다." with no extra contact/CTA
    line unless the user requested one
9. Single file: no external requests except declared font CDNs; deck
   still legible if fonts fail (fallback stack)
10. File size < 2MB (embedded images are the usual offender — compress or
    gradient-substitute)
11. If the AWS logo is in: correct variant for the theme (white-on-dark /
    dark-on-light), aspect ratio intact, margin-aligned, legible in the
    1280×720 screenshot
12. customer-session mode: cover has all four elements (logo top-left,
    title, presenter block, copyright); every non-cover slide carries the
    `.aws-footer`; the base64 URI appears exactly once in the file; no
    "Confidential" wording on a customer deck; fonts are Amazon Ember +
    Nanum Gothic with no `font-weight` above 700
13. Citations (share-out decks): every external claim/stat/screenshot/quote
    is sourced in small type; each cite sits ABOVE the footer band (not on
    its baseline) and clears the bottom-right page counter; EVERY URL in a
    cite or resource card is a real clickable `<a href target="_blank">`,
    not plain text; no fabricated URLs (link only verified pages)

## Output conventions

- One file: `<deck-name>.html` in the user's working directory
- Deck title in `<title>` and as `og:title`
- Footer: presenter name / event / date on content slides (from user),
  page number `current / total`
- No watermarks

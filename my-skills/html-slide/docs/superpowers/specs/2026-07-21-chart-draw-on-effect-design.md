# A9. Chart draw-on — Design

_2026-07-21 · html-slide skill · references/effects.md_

## Problem

The effects library covers slide entrances (A1–A5, A7), a title-only
typewriter (A8), and a single JS `count-up` (A6) — but nothing that makes a
**chart construct itself**. Yet the engine tells authors to hand-write charts
as inline SVG (`engine.md:230`), and the Swiss Minimal theme is explicitly the
data/table/chart theme. The highest-impact moment of a data deck (the reveal
of the numbers) had no motion vocabulary. This adds it as **A9**.

## Approach

One effect entry, `A9. Chart draw-on`, with three sub-patterns (bars, lines,
donut/gauge). Chosen over slide-transition or inline-text-highlight ideas
because the gap is clearest, it needs **no engine changes**, and it's pure CSS.

Web research (2026-07-21, Tavily) confirmed the standard, battle-tested
techniques and the accessibility constraint:

- **Bars**: `transform: scaleY()` with `transform-origin: bottom` —
  compositor-friendly, obeys the "opacity/transform/filter only" rule.
- **Lines**: `stroke-dashoffset` line-drawing (Jake Archibald's SVG technique,
  corroborated by CSS-Tricks and Stack Overflow). Using `pathLength="1"` lets
  hand-authored SVG skip `getTotalLength()` pixel math entirely.
- **Donut/gauge**: same dash technique on a `<circle>` with `pathLength="100"`
  so the percentage doubles as the dash value.
- **Accessibility**: research stressed *reduce, don't nuke* motion — the
  finished state must survive `prefers-reduced-motion`. Satisfied for free
  because the engine kill-switch strips animation globally and every A9
  keyframe animates FROM an offset TO the real value.

## Design

**Placement**: `references/effects.md`, section A, after A8, before the `---`.
Same format as A1–A8 (one paragraph + css/html blocks). No new file, no engine
edit.

**Hooks**: key off `.slide.entered` (on-enter build) or `[data-step].revealed`
(keypress build). Both are existing engine toggles.

**Invariants**:
- `to`-state == real data value → correct in print / reduced-motion.
- Only `transform`, `stroke-dashoffset`, `opacity` animated.
- Entrance 700–900ms, `var(--ease)`. No timer-looped or pulsing charts
  (anti-pattern). Bar stagger reuses A1's 90ms rhythm via `--i`.
- Pairs with A6 count-up on one slide: number ticks while bar grows.

**Sub-pattern summary**:

| Sub-pattern | Mechanism | Author input |
|-------------|-----------|--------------|
| Bars | `scaleY(0)→1`, origin bottom, `--i` stagger | real `height:%` per bar |
| Lines | `pathLength="1"`, dashoffset `1→0` | real `d` path |
| Donut/gauge | `pathLength="100"`, dashoffset `100→(100−v)` | real `--rest`=100−value |

**Side edits**: § Effect pairing table gains "chart draw-on" on the Swiss
Minimal and Aurora Tech rows (the data themes).

## Out of scope (YAGNI)

- Slide-to-slide transitions (needs engine JS; conflicts with presenter-owns-
  pacing philosophy).
- Inline text highlight sweep (separate, unrelated effect).
- Any JS charting library — engine mandates hand-authored inline SVG.

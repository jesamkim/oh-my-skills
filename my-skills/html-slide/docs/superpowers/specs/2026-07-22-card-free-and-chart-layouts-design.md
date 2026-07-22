# Card-free + chart layouts — Design

_2026-07-22 · html-slide skill · references/layouts.md + SKILL.md_

## Problem

A user reported decks from this skill "feel repetitive across a few design
patterns." Diagnosis of the catalog found the real cause: the rounded
`.cell` card (`--surface` fill, 24px radius) is the shared skeleton of
layouts 6 (Bento), 7 (Card Row), 10 (Comparison), and 11 (Code) — roughly
half the catalog. Layout *names* differ but the *screen* converges on "a few
grey rounded boxes." The existing Mix Rule only forbids repeating the same
*layout* 3x in a row; it never constrains repeated *surface treatment*. And
the catalog had no chart layout at all, despite the engine mandating
hand-authored inline SVG charts and the new A9 chart draw-on effect.

## Approach

Add five layouts and one rule, matching the existing catalog format
(when-to-use + copy-paste HTML/CSS at 1920×1080 design px). No engine change,
no new theme, no JS chart lib.

- **Card-free trio (14-16)** builds structure from hairline rules,
  whitespace, and alignment instead of card fills — the Paper Editorial /
  Swiss Minimal philosophy, which the catalog espoused but never supplied a
  layout for. Each is a direct alternative to a card-heavy layout.
- **Chart pair (17-18)** pairs with A9: every bar height / arc value is the
  real number (print + reduced-motion safe), A9 only reveals it on
  `data-step`. Line chart is a one-line variant of 17; pie is a `stroke-width`
  variant of 18 (YAGNI — no separate entries).
- **Surface-variety rule** is the load-bearing change. Adding examples
  without a rule would still leave the author reaching for cards, so the rule
  ("card layouts at most twice in a row; make the third card-free or a
  chart") ships alongside the layouts, in three places.

## Design

| # | Layout | Replaces | Structure |
|---|--------|----------|-----------|
| 14 | Ledger List | Card Row (7) | full-width rows, hairline `border-top`, label/payload split |
| 15 | Indexed Definitions | Bento (6) peers | oversized numerals + hanging indent, whitespace grouping |
| 16 | Split Contrast | Comparison (10) | one vertical hairline, verdict by weight/alignment |
| 17 | Bar Chart | — (new) | inline SVG/div bars, A9 `barGrow`, height% = value/max |
| 18 | Donut/Pie + KPI | — (new) | `pathLength="100"` arc + center %, A9 `arcFill`, legend |

**Rule text** (Surface-variety): rounded `.cell` cards dominate 6/7/10/11;
use card layouts at most twice in a row, make the third information group
card-free (14/15/16/5) or a chart (17/18). Card ↔ card-free is itself a
rhythm.

**Edit sites (3)**:
1. `layouts.md` — new "Card-free layouts" + "Chart layouts" sections before
   the Composition sequence guide; Surface-variety rule under Mix Rule;
   Composition table row 5 gains chart options.
2. `SKILL.md` § Layout Grammar — layout list extended, Surface-variety
   paragraph added after Mix Rule.
3. `SKILL.md` QA checklist item 4 — Surface-variety check added.

## Invariants preserved

- Chart truth = real values; A9 keyframes reveal, never fabricate.
- Axis/labels `--muted`, bars/arcs accent family, ≤ 5 colors total.
- Card-free layouts use `1fr` grids but fill via border/whitespace, not
  `.cell`.
- All layouts work in every theme; 14-16 peak in Paper/Swiss.

## Out of scope (YAGNI)

- Separate line-chart and pie layouts (folded into 17/18 as variants).
- New themes, engine edits, JS charting, multi-series charts.

## Note

`docs/` is gitignored in this repo, so this spec stays local; the layouts.md
and SKILL.md changes are what gets committed.

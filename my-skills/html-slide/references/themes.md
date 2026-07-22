# Themes — Preset Tokens + Mandatory Variation

Five presets. Each is a complete `:root` token block that drops into the
engine skeleton, plus art-direction notes. **Presets are starting points:
before building, vary at least the accent family and the display font to
fit the topic.** The goal is that two decks produced by this skill never
look like siblings unless the user asks for a series.

Color discipline (all themes): ≤ 5 colors per deck — bg, surface, text,
muted, accent (a 2-3 stop gradient counts as ONE accent family). Contrast:
body text ≥ 7:1 on bg, muted/captions ≥ 4.5:1.

Font sourcing: Pretendard covers Korean+Latin body everywhere. For display
personality add ONE font via Google Fonts/jsdelivr `<link>` with a full
system fallback stack. Never Inter/Roboto/Arial as display.

---

## 1. Midnight Keynote

Apple-keynote lineage: near-black stage, enormous white type, a single
warm gradient reserved for THE moment. Default for product launches and
"임팩트" requests.

```css
:root {
  --bg: #0B0B0F;
  --surface: #16161D;
  --text: #F5F5F7;
  --muted: #86868B;
  --accent: #FF7A18;
  --accent-2: #E93A7D;
  --grad: linear-gradient(120deg, #FF7A18, #E93A7D);
  --font-display: "Pretendard Variable", Pretendard, -apple-system, sans-serif;
  --font-body: "Pretendard Variable", Pretendard, -apple-system, sans-serif;
  --font-mono: "SF Mono", "JetBrains Mono", Consolas, monospace;
  --ease: cubic-bezier(0.16, 1, 0.3, 1);
}
```

Art direction: typography IS the design — headings 700-800 weight,
letter-spacing -0.03em. The gradient appears on at most 1-2 elements per
deck (hero stat, one headline via `background-clip: text`). Everything
else is white/gray on black. Cards: `--surface` fill, 24px radius, NO
borders. Signature effects: blur-reveal, product settle, count-up.

Variation levers: gradient hue per topic (finance → gold/amber, bio →
green/teal, AI → electric blue/violet), or swap display font to
"Instrument Sans" / "Schibsted Grotesk" for a less Apple voice.

---

## 2. Aurora Tech

Deep navy with a slow-moving aurora gradient mesh in the background,
glassmorphism cards. For AI/cloud tech talks and demo days.

```css
:root {
  --bg: #060B1A;
  --surface: rgba(255, 255, 255, 0.06);
  --surface-border: rgba(255, 255, 255, 0.14);
  --text: #EAF0FF;
  --muted: #8A94B0;
  --accent: #4DA3FF;
  --accent-2: #9B5CFF;
  --accent-3: #2BD9C7;
  --grad: linear-gradient(115deg, #4DA3FF, #9B5CFF 55%, #2BD9C7);
  --font-display: "Space Grotesk", "Pretendard Variable", sans-serif; /* swap per deck! */
  --font-body: "Pretendard Variable", Pretendard, sans-serif;
  --font-mono: "JetBrains Mono", Consolas, monospace;
  --ease: cubic-bezier(0.16, 1, 0.3, 1);
}
```

Aurora background (one fixed layer on the stage, not per slide):

```css
#stage::before {
  content: ""; position: absolute; inset: -20%;
  background:
    radial-gradient(40% 55% at 20% 25%, rgba(77,163,255,.28), transparent 70%),
    radial-gradient(35% 45% at 80% 20%, rgba(155,92,255,.22), transparent 70%),
    radial-gradient(45% 50% at 60% 85%, rgba(43,217,199,.16), transparent 70%);
  filter: blur(40px);
  animation: aurora 24s var(--ease) infinite alternate;
  z-index: 0;
}
.slide { z-index: 1; }
@keyframes aurora {
  to { transform: translate(-4%, 3%) rotate(4deg) scale(1.08); }
}
```

Glass card: `background: var(--surface); border: 1px solid
var(--surface-border); border-radius: 24px; backdrop-filter: blur(24px);`

Art direction: the mesh is atmosphere, not content — keep it ≤ 30%
opacity. Glass cards need the 1px light border to read as glass. Note the
display font marked "swap per deck" — literally change it each time.

---

## 3. Paper Editorial

Warm paper white, high-contrast serif display, magazine rules and
generous margins. For strategy narratives, exec audiences, storytelling.

```css
:root {
  --bg: #FAF6EF;
  --surface: #FFFFFF;
  --text: #1A1714;
  --muted: #6E675D;
  --accent: #C24A22;          /* burnt sienna — vary per topic */
  --grad: none;               /* editorial theme uses NO gradients */
  --font-display: "Playfair Display", "Noto Serif KR", serif;
  --font-body: "Pretendard Variable", Pretendard, sans-serif;
  --font-mono: "JetBrains Mono", Consolas, monospace;
  --ease: cubic-bezier(0.16, 1, 0.3, 1);
}
```

Art direction: serif display + sans body is the signature pairing.
Hairline rules (`1px solid #DDD5C7`) separate regions — no card boxes at
all; whitespace and rules do the structuring. Eyebrow labels in
small-caps tracking 0.18em. Accent used for drop caps, numerals, one
underline — like a magazine's spot color. Effects: mask wipe on
headlines, slow Ken Burns on full-bleed photos. No glow, no gradient text.

Korean pairing: Playfair→"Noto Serif KR" fallback works; a full-Korean
editorial deck can promote Noto Serif KR to display outright.

---

## 4. Swiss Minimal

White, visible grid, one hard accent, Helvetica-lineage grotesk. For
data-heavy reviews, portfolios, design crits. The discipline theme:
nothing moves much, everything aligns.

```css
:root {
  --bg: #FFFFFF;
  --surface: #F4F4F2;
  --text: #111111;
  --muted: #767676;
  --accent: #E0301E;          /* Swiss red — or cobalt #1D4ED8, vary */
  --grad: none;
  --font-display: "Archivo", "Pretendard Variable", sans-serif;
  --font-body: "Pretendard Variable", Pretendard, sans-serif;
  --font-mono: "JetBrains Mono", Consolas, monospace;
  --ease: cubic-bezier(0.16, 1, 0.3, 1);
}
```

Art direction: 12-column mental grid; headings flush-left, often
oversized and cropped by the slide edge (intentional bleed). Accent
appears as solid blocks (a filled square bullet, a bar behind a number)
— never as text color for body. Tables and charts shine here: hairline
borders, tabular numerals. Effects: staggered rise only, 400ms, minimal.
The restraint IS the impact.

---

## 5. Terminal Mono

CRT-dark, all-monospace, phosphor accent, scanline texture. For
engineering deep-dives, CLI/devtools, incident reviews.

```css
:root {
  --bg: #0A0F0A;
  --surface: #101710;
  --text: #D8E8D8;
  --muted: #5E6E5E;
  --accent: #3DF56E;           /* phosphor green — amber #FFB000 variant */
  --grad: none;
  --font-display: "JetBrains Mono", "D2Coding", monospace;
  --font-body: "JetBrains Mono", "D2Coding", monospace;
  --font-mono: "JetBrains Mono", "D2Coding", monospace;
  --ease: steps(24);           /* stepped easing fits the theme */
}
```

Scanline texture (subtle, on stage):

```css
#stage::after {
  content: ""; position: absolute; inset: 0; pointer-events: none;
  background: repeating-linear-gradient(0deg,
    transparent 0 2px, rgba(0,0,0,.18) 2px 4px);
  z-index: 40;
}
```

Art direction: everything monospace including headings (weight 700 for
display, tracking -0.01em). Prompt markers (`$`, `>`) as bullets. Accent
for commands/output-of-interest only. Effects: typewriter reveal on the
title slide (once per deck), cursor blink, instant `steps()` transitions.
Body text in this theme reads smaller — bump minimum to 32px.

---

## Choosing & varying

| Signal from user/topic | Theme |
|------------------------|-------|
| launch, keynote, "임팩트", hero product | Midnight Keynote |
| AI/ML, cloud, platform, demo day | Aurora Tech |
| strategy, story, exec/board, history | Paper Editorial |
| data review, metrics, portfolio, design | Swiss Minimal |
| CLI, infra, debugging, postmortem | Terminal Mono |

Then vary (mandatory, pick ≥ 2):
1. **Accent family** — re-derive from the topic/brand (their logo color,
   their domain's connotation)
2. **Display font** — one distinctive choice with Korean fallback
3. **Texture** — grain overlay, grid lines, blueprint dots, none
4. **Radius language** — sharp 0px (Swiss/Terminal) vs 16-28px (Keynote/Aurora)

Record the final tokens in a comment at the top of the deck's `<style>`
so later edits stay consistent.

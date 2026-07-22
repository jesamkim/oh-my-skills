# Effects Library — Impact With Restraint

Effects are what make an HTML deck feel like a keynote instead of a
document. But the craft is in restraint: **pick 2-3 signature effects per
deck and reuse them consistently.** A different effect on every slide
reads as chaos; the same two effects, precisely timed, read as art
direction.

Global rules (engine.md enforces the kill-switch):
- One easing everywhere: `var(--ease)` = `cubic-bezier(0.16, 1, 0.3, 1)`
  (Apple-style "ease-out-expo" feel: fast start, long settle)
- Entrances 600-900ms; step reveals 300-500ms; ambient loops ≥ 20s
- Everything must survive `prefers-reduced-motion` (engine kills all
  animation globally) and print (content never hidden by an un-run
  animation's `to`-state — always animate FROM offset TO natural state)
- Animate only `opacity`, `transform`, `filter` (compositor-friendly);
  never `left/top/width/height`

Engine hook: on activation the engine re-toggles `.entered` on the slide,
restarting CSS animations. Key everything off `.slide.entered`.

---

## A. Slide-enter builds

### A1. Staggered rise (the workhorse)

Children rise 40px + fade, 90ms apart. Suits every theme; if a deck has
only one effect, it's this.

```css
.slide.entered .rise > * {
  animation: rise .7s var(--ease) both;
}
@keyframes rise {
  from { opacity: 0; transform: translateY(40px); }
  to   { opacity: 1; transform: none; }
}
.rise > :nth-child(1) { animation-delay: .05s; }
.rise > :nth-child(2) { animation-delay: .14s; }
.rise > :nth-child(3) { animation-delay: .23s; }
.rise > :nth-child(4) { animation-delay: .32s; }
.rise > :nth-child(5) { animation-delay: .41s; }
```

### A2. Blur-reveal (Apple product-shot entrance)

The apple.com hero technique: element arrives from blur + slight scale,
like a lens pulling focus. Reserve for hero objects — title slide
headline, product image, hero stat.

```css
.slide.entered .blur-reveal {
  animation: blurIn 1.1s var(--ease) both;
}
@keyframes blurIn {
  from { opacity: 0; filter: blur(28px); transform: scale(1.06); }
  60%  { opacity: 1; }
  to   { opacity: 1; filter: blur(0); transform: scale(1); }
}
```

### A3. Product settle (Apple "hero lands" moment)

Object scales down from 1.08 while its shadow blooms beneath — the
"product lands on the table" feel from Apple product pages. For device
mockups, screenshots, big cards.

```css
.slide.entered .settle {
  animation: settle 1s var(--ease) both;
}
.slide.entered .settle::after {   /* shadow bloom */
  content: ""; position: absolute; left: 8%; right: 8%; bottom: -36px;
  height: 48px; border-radius: 50%;
  background: radial-gradient(closest-side, rgba(0,0,0,.5), transparent);
  animation: shadowBloom 1s var(--ease) both;
  z-index: -1;
}
@keyframes settle {
  from { opacity: 0; transform: translateY(-24px) scale(1.08); }
  to   { opacity: 1; transform: none; }
}
@keyframes shadowBloom {
  from { opacity: 0; transform: scaleX(.6); }
  to   { opacity: 1; transform: none; }
}
```

### A4. Gradient headline shimmer (Apple "Hello" lineage)

Gradient text whose gradient sweeps once on entry, then holds. Max ONE
per deck — this is a title-slide or thesis-slide move.

```css
.shimmer {
  background: linear-gradient(100deg,
    var(--text) 0%, var(--accent) 30%, var(--accent-2) 50%, var(--text) 70%);
  background-size: 300% 100%;
  -webkit-background-clip: text; background-clip: text; color: transparent;
}
.slide.entered .shimmer { animation: shimmer 2.4s var(--ease) .3s 1 both; }
@keyframes shimmer {
  from { background-position: 100% 0; }
  to   { background-position: 0% 0; }
}
```

### A5. Mask wipe (editorial reveal)

Text revealed by a clip-path sweep — the Paper Editorial signature. Also
good for section dividers in any theme.

```css
.slide.entered .wipe {
  animation: wipe .9s var(--ease) both;
}
@keyframes wipe {
  from { clip-path: inset(0 100% 0 0); }
  to   { clip-path: inset(0 0 0 0); }
}
```

### A6. Count-up stat

The one JS effect. Add this snippet ONCE after the engine block (it hooks
the engine's `entered` toggle via MutationObserver — no engine edits).

```html
<script>
(() => {
  const fmt = new Intl.NumberFormat('en-US');
  new MutationObserver(muts => muts.forEach(m => {
    if (!m.target.classList?.contains('entered')) return;
    m.target.querySelectorAll('[data-count]').forEach(el => {
      const target = parseFloat(el.dataset.count), t0 = performance.now();
      const dur = 1400;
      (function tick(t) {
        const p = Math.min((t - t0) / dur, 1);
        const eased = 1 - Math.pow(1 - p, 4);
        el.textContent = fmt.format(Math.round(target * eased));
        if (p < 1) requestAnimationFrame(tick);
      })(t0);
    });
  })).observe(document.getElementById('stage'),
              { subtree: true, attributes: true, attributeFilter: ['class'] });
})();
</script>
```

Usage: `<div class="stat" data-count="503">503</div>` — static text stays
correct for print/no-JS.

### A7. Ken Burns (full-bleed images)

```css
.kenburns { animation: kb 22s var(--ease) both; }
@keyframes kb {
  from { transform: scale(1); }
  to   { transform: scale(1.08) translate(-1.5%, -1%); }
}
```

### A8. Typewriter (Terminal Mono only, once per deck)

```css
.type {
  overflow: hidden; white-space: nowrap; width: 0;
  border-right: 3px solid var(--accent);
}
.slide.entered .type {
  animation: typing 1.6s steps(28) .3s both, caret .8s step-end infinite;
}
@keyframes typing { to { width: 100%; } }
@keyframes caret { 50% { border-color: transparent; } }
```

### A9. Chart draw-on (data reveals itself)

The data-slide centerpiece: bars grow, lines draw, arcs sweep — the chart
constructs itself instead of just appearing. Three sub-patterns share one
rule: **the `to`-state is always the real value**, so print and
`prefers-reduced-motion` (engine kill-switch) show the finished chart, never
a blank one. Animate only `transform` / `stroke-dashoffset` / `opacity`.
Key off `.slide.entered` for an on-enter build, or off `[data-step].revealed`
to draw on keypress. Pairs with A6 count-up on the same slide — the number
ticks up while its bar grows.

**Bars** — `scaleY` from a pinned base; `--i` staggers them on A1's 90ms
rhythm. Works for `<rect>` in an SVG or plain `<div>` bars.

```css
.slide.entered .bar { animation: barGrow .8s var(--ease) both;
  transform-origin: bottom; animation-delay: calc(var(--i) * .09s); }
@keyframes barGrow { from { transform: scaleY(0); } to { transform: none; } }
```
```html
<div class="bar" style="--i:0; height:62%"></div>
<div class="bar" style="--i:1; height:88%"></div>
```

**Lines** — give the `<path>` `pathLength="1"`, then the dash math needs no
pixel measuring: the line is one dash the length of the whole path, offset
out of view, then pulled to 0.

```css
.slide.entered .draw-line {
  stroke-dasharray: 1; stroke-dashoffset: 1;
  animation: drawLine .9s var(--ease) both; }
@keyframes drawLine { to { stroke-dashoffset: 0; } }
```
```html
<path class="draw-line" pathLength="1" fill="none"
  stroke="var(--accent)" stroke-width="3" d="M0 90 L120 60 L240 72 L360 20"/>
```

**Donut / gauge** — set `pathLength="100"` so the percentage IS the dash
value; sweep the offset from 100 down to `100 − value`.

```css
.slide.entered .arc {
  stroke-dasharray: 100; stroke-dashoffset: 100;
  animation: arcFill 1s var(--ease) both; }
@keyframes arcFill { to { stroke-dashoffset: var(--rest); } }  /* 100 − value */
```
```html
<circle class="arc" pathLength="100" style="--rest:32"  /* 68% filled */
  cx="60" cy="60" r="52" fill="none" stroke="var(--accent)"
  stroke-width="12" transform="rotate(-90 60 60)"/>
```

Static markup (real height / real `d` / real `--rest`) is the truth; the
animation only reveals it. Never animate a timer-looped or pulsing chart —
one build on reveal, then it holds.

---

## B. In-slide step effects (`data-step` + engine)

The engine reveals `[data-step]` elements per keypress. These classes
control HOW they appear (pair with `visibility` handling — the engine
toggles `.revealed`).

```css
[data-step] { opacity: 0; transform: translateY(24px);
  transition: opacity .45s var(--ease), transform .45s var(--ease); }
[data-step].revealed { opacity: 1; transform: none; }

/* variant: scale-pop for cards/badges */
[data-step].pop { transform: scale(.92); }
[data-step].pop.revealed { transform: scale(1); }

/* variant: highlight-shift — previously revealed items dim as new ones arrive */
.focus-run [data-step].revealed { opacity: .38; }
.focus-run [data-step].revealed:last-of-type,
.focus-run [data-step].revealed.current { opacity: 1; }
```

### B-special: Pinned storytelling (Apple scroll-section, keypress edition)

Apple.com pins a product image while scrolling text changes its state.
Keypress translation: **one persistent object on stage; each `data-step`
both reveals a caption AND drives the object's state** via CSS sibling
logic. No JS needed.

```html
<section class="slide" id="pinned-demo">
  <h2 class="h2">요청 한 건의 여정</h2>
  <div style="display:grid; grid-template-columns:8fr 5fr; gap:64px; flex:1;">
    <!-- the pinned object: an SVG pipeline whose stages light up -->
    <svg viewBox="0 0 900 500" style="width:100%;" id="pipe">
      <g class="stage-a"><!-- gateway node --></g>
      <g class="stage-b"><!-- agent node --></g>
      <g class="stage-c"><!-- tools node --></g>
    </svg>
    <!-- steps that drive it -->
    <div style="display:flex; flex-direction:column; gap:32px; justify-content:center;">
      <div class="cell" data-step id="st1"><p class="body">1. 게이트웨이가 인증·라우팅</p></div>
      <div class="cell" data-step id="st2"><p class="body">2. 에이전트가 계획 수립</p></div>
      <div class="cell" data-step id="st3"><p class="body">3. 툴 호출, 결과 종합</p></div>
    </div>
  </div>
</section>
<style>
/* object state driven by which steps are revealed */
#pipe .stage-a, #pipe .stage-b, #pipe .stage-c {
  opacity: .18; transition: opacity .5s var(--ease), filter .5s var(--ease);
}
#pinned-demo:has(#st1.revealed) .stage-a,
#pinned-demo:has(#st2.revealed) .stage-b,
#pinned-demo:has(#st3.revealed) .stage-c {
  opacity: 1; filter: drop-shadow(0 0 24px color-mix(in srgb, var(--accent) 60%, transparent));
}
</style>
```

The `:has()` selector wires "step N revealed → object part N activates".
Works for: pipeline stages lighting up, a device mockup swapping screens
(stack images, opacity per step), an architecture diagram highlighting a
path, a chart adding series. This is the single highest-impact pattern
in the library — use it on the deck's centerpiece slide.

### B-special 2: Exploded view (Apple parts-separation)

Product/architecture layers slide apart on one step, labels appear.

```html
<div class="exploded" data-step id="explode">
  <img src="…layer1…" class="layer" style="--i:0">
  <img src="…layer2…" class="layer" style="--i:1">
  <img src="…layer3…" class="layer" style="--i:2">
</div>
<style>
.exploded { position: relative; }
.exploded .layer {
  position: absolute; inset: 0;
  transition: transform .8s var(--ease);
  transition-delay: calc(var(--i) * 90ms);
}
.exploded.revealed .layer {
  transform: translateY(calc((var(--i) - 1) * -110px));
}
</style>
```

---

## C. Ambient / atmosphere (背景, one per deck max)

- **Aurora mesh** — themes.md § Aurora Tech (24s drift loop)
- **Grain overlay** — `background: url(data:image/svg+xml;base64,<feTurbulence noise>)`,
  opacity .04-.06, `pointer-events:none`. Kills flat-gradient banding.
- **Grid lines** (Swiss) — `repeating-linear-gradient` 1px lines at 160px
  intervals, opacity .05
- **Scanlines** (Terminal) — themes.md § Terminal Mono

Ambient layers live on `#stage::before/::after`, never per slide, always
`pointer-events: none`, and must not exceed ~6% visual weight.

---

## Effect pairing per theme

| Theme | Signature set (pick from) |
|-------|---------------------------|
| Midnight Keynote | blur-reveal + product settle + count-up; shimmer on title |
| Aurora Tech | aurora mesh + staggered rise + pinned storytelling; chart draw-on for data |
| Paper Editorial | mask wipe + Ken Burns; NO glow/shimmer |
| Swiss Minimal | staggered rise (400ms) + chart draw-on — restraint is the effect |
| Terminal Mono | typewriter (title) + stepped transitions + cursor blink |

## Anti-patterns

- 3D flip/cube/spin slide transitions (2010 reveal.js energy)
- Continuous floating/pulsing on content elements (motion sickness,
  distracts from the speaker)
- Per-letter animation of body text (only ever display-size, ≤ 1 word run)
- Effects that reorder reading flow (reveal order must equal reading order)
- Autoplaying steps on a timer — the presenter owns pacing, always

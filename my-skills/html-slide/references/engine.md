# Engine — Self-Contained HTML Deck Skeleton

This is the machinery layer of every deck: fixed-stage scaling, navigation,
step builds, hash routing, progress UI, and print-to-PDF. **Copy the
skeleton below and do not modify the engine JS/CSS** — write only theme
tokens, slide markup, and effect classes on top of it. The engine is ~120
lines and every line exists because a naive version breaks somewhere
(mobile Safari scaling, print fragmenting, hash desync, reduced-motion).

## Why fixed 1920×1080 + transform scale (not responsive CSS)

Slides are a fixed-canvas medium: the designer controls exactly where
every element sits, like PPTX/Keynote. Responsive reflow is the enemy —
it's what makes AI HTML slides "web-page-like". The stage is authored at
1920×1080 (design px) and the engine scales the whole stage uniformly to
fit any viewport, letterboxing the rest. Consequences you rely on:

- All px values in slide CSS are design px — they mean the same thing on
  every screen. A 40px body IS 40px-at-1080p everywhere.
- `transform: scale()` keeps text crisp (it's not a bitmap zoom).
- No media queries needed inside slides. Ever.

## The Skeleton

```html
<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>DECK TITLE</title>
<!-- Korean-capable font. Keep the fallback stack — deck must survive offline. -->
<link rel="preconnect" href="https://cdn.jsdelivr.net">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable-dynamic-subset.min.css">
<style>
/* ===== THEME TOKENS (the ONLY block you re-write per deck) ===== */
:root {
  --bg: #0B0B0F;
  --surface: #16161D;
  --text: #F5F5F7;
  --muted: #86868B;
  --accent: #FF7A18;
  --accent-2: #E93A7D;          /* optional 2nd gradient stop */
  --grad: linear-gradient(120deg, var(--accent), var(--accent-2));
  --font-display: "Pretendard Variable", Pretendard, -apple-system, sans-serif;
  --font-body: "Pretendard Variable", Pretendard, -apple-system, sans-serif;
  --font-mono: "SF Mono", "JetBrains Mono", Consolas, monospace;
  --ease: cubic-bezier(0.16, 1, 0.3, 1);
}

/* ===== ENGINE (do not modify) ===== */
* { margin: 0; padding: 0; box-sizing: border-box; }
html, body { height: 100%; overflow: hidden; background: #000; }
body { font-family: var(--font-body); }

#viewport {
  position: fixed; inset: 0;
  display: flex; align-items: center; justify-content: center;
}
#stage {
  width: 1920px; height: 1080px;
  position: relative; overflow: hidden;
  background: var(--bg); color: var(--text);
  transform-origin: center center;
  flex: none;
}
.slide {
  position: absolute; inset: 0;
  padding: 96px 120px;
  display: none;
  word-break: keep-all; line-break: strict;
}
.slide.active { display: flex; flex-direction: column; }

/* step builds: hidden until revealed */
.slide [data-step] { visibility: hidden; }
.slide [data-step].revealed { visibility: visible; }

/* chrome */
#progress {
  position: absolute; left: 0; top: 0; height: 6px; width: 0%;
  background: var(--grad); z-index: 50; transition: width .3s var(--ease);
}
#counter {
  position: absolute; right: 48px; bottom: 36px; z-index: 50;
  font-size: 22px; color: var(--muted); font-variant-numeric: tabular-nums;
}

/* reduced motion: kill everything globally */
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation: none !important; transition: none !important;
  }
}

/* ===== PRINT → PDF (Ctrl+P, landscape). Do not modify. ===== */
@media print {
  @page { size: 1920px 1080px; margin: 0; }
  html, body { overflow: visible; background: none; }
  #viewport { position: static; display: block; }
  #stage {
    transform: none !important; width: 1920px; height: auto;
  }
  .slide {
    display: flex !important; position: relative;
    width: 1920px; height: 1080px;
    page-break-after: always; break-after: page;
  }
  .slide [data-step] { visibility: visible !important; }
  #progress, #counter { display: none; }
}
</style>
</head>
<body>
<div id="viewport">
  <div id="stage">
    <div id="progress"></div>
    <div id="counter"></div>

    <!-- ===== SLIDES: one <section class="slide"> each ===== -->
    <section class="slide" id="s1">
      <!-- slide content -->
    </section>
    <section class="slide" id="s2">
      <p data-step>First revealed on keypress…</p>
      <p data-step>…then this.</p>
    </section>
    <!-- ===== /SLIDES ===== -->

  </div>
</div>
<script>
/* ===== ENGINE JS (do not modify) ===== */
(() => {
  const slides = [...document.querySelectorAll('.slide')];
  const total = slides.length;
  let cur = Math.min(Math.max(parseInt(location.hash.slice(1)) || 1, 1), total) - 1;

  function steps(i) { return [...slides[i].querySelectorAll('[data-step]')]; }

  function show(i, revealAll = false) {
    cur = Math.min(Math.max(i, 0), total - 1);
    slides.forEach((s, k) => s.classList.toggle('active', k === cur));
    steps(cur).forEach(el => el.classList.toggle('revealed', revealAll));
    document.getElementById('progress').style.width = ((cur + 1) / total * 100) + '%';
    document.getElementById('counter').textContent = (cur + 1) + ' / ' + total;
    history.replaceState(null, '', '#' + (cur + 1));
    // re-fire enter animations
    const s = slides[cur];
    s.classList.remove('entered'); void s.offsetWidth; s.classList.add('entered');
    broadcastState();
  }

  function next() {
    const pending = steps(cur).filter(el => !el.classList.contains('revealed'));
    if (pending.length) { pending[0].classList.add('revealed'); return; }
    if (cur < total - 1) show(cur + 1);
  }
  function prev() {
    const shown = steps(cur).filter(el => el.classList.contains('revealed'));
    if (shown.length) { shown[shown.length - 1].classList.remove('revealed'); return; }
    if (cur > 0) show(cur - 1, true);
  }

  addEventListener('keydown', e => {
    if (['ArrowRight',' ','PageDown'].includes(e.key)) { e.preventDefault(); next(); }
    else if (['ArrowLeft','PageUp'].includes(e.key)) { e.preventDefault(); prev(); }
    else if (e.key === 'Home') show(0);
    else if (e.key === 'End') show(total - 1, true);
    else if (e.key === 'f') document.documentElement.requestFullscreen?.();
  });

  // touch swipe
  let tx = null;
  addEventListener('touchstart', e => tx = e.touches[0].clientX, {passive: true});
  addEventListener('touchend', e => {
    if (tx === null) return;
    const dx = e.changedTouches[0].clientX - tx;
    if (dx < -60) next(); else if (dx > 60) prev();
    tx = null;
  }, {passive: true});

  // fit stage to viewport
  function fit() {
    const s = Math.min(innerWidth / 1920, innerHeight / 1080);
    document.getElementById('stage').style.transform = 'scale(' + s + ')';
  }
  addEventListener('resize', fit);

  addEventListener('hashchange', () => {
    const n = parseInt(location.hash.slice(1));
    if (n >= 1 && n <= total && n - 1 !== cur) show(n - 1);
  });

  // ===== slidecast-nav bridge (parent viewer overlay) =====
  // Parent frame drives next/prev and reads current/total for its nav
  // overlay. Works without allow-same-origin: postMessage crosses the
  // sandbox boundary. No-op when there is no distinct parent frame.
  function broadcastState() {
    if (window.parent === window) return;
    try {
      window.parent.postMessage(
        { type: 'slidecast-state', cur: cur + 1, total: total },
        '*'
      );
    } catch (e) { /* parent unreachable; ignore */ }
  }
  addEventListener('message', (e) => {
    const d = e.data;
    if (!d || d.type !== 'slidecast-nav') return;
    if (d.action === 'next') next();
    else if (d.action === 'prev') prev();
    else if (d.action === 'ping') broadcastState();
  });

  fit(); show(cur);
})();
</script>
</body>
</html>
```

## Contract details

### Navigation model
`next()` reveals pending `data-step` elements first, then advances the
slide — identical to PowerPoint's click model. `prev()` un-reveals in
reverse, and when leaving a slide backwards, the previous slide arrives
fully revealed (`show(i, true)`) so backward review never hides content.

### Enter animations hook
On every activation the engine toggles the `entered` class (with a reflow
between remove/add so CSS animations restart). Effect CSS keys off
`.slide.entered .your-element` — see effects.md. Never animate off
`.active` directly: it doesn't re-fire when revisiting a slide.

### slidecast-nav bridge
The engine listens for `{type:"slidecast-nav", action:"next"|"prev"|"ping"}`
messages and, on every `show()`, broadcasts `{type:"slidecast-state",
cur, total}` to its parent frame. This lets a host viewer (e.g. Slidecast)
draw a bottom navigation overlay that drives next/prev and displays the
current/total page — without granting the iframe `allow-same-origin`, since
`postMessage` crosses the sandbox boundary. It is a no-op at top level
(`window.parent === window`), so a standalone deck is unaffected.

### Print / PDF
Ctrl+P with the built-in stylesheet gives one slide per 1920×1080 page,
all steps force-revealed, chrome hidden. Tell the user: destination
"Save as PDF", margins "None", background graphics ON. For batch/CI
export, headless Chrome works:
`chrome --headless --print-to-pdf=deck.pdf --no-pdf-header-footer deck.html`
(playwright's `page.pdf()` equally fine). Never rasterize slides to
images for PDF.

### Self-containment rules
- Only allowed external request: the font CDN `<link>` (with full system
  fallback stack so the deck survives offline).
- Images: prefer inline SVG (crisp at any scale, themeable via CSS vars).
  Photos: embed as base64 `data:` URI only if < ~300KB each; otherwise
  ask the user whether a sibling assets folder is acceptable.
- No JS libraries. The engine is all the JS a deck needs. Charts: inline
  SVG, hand-authored or generated — not Chart.js.

### Speaker notes (optional)
`<aside class="notes">` inside a slide, `display:none` on stage and in
print. Only add when the user asks for notes.

## Known traps

| Trap | Symptom | Rule |
|------|---------|------|
| vh/vw units inside slides | breaks under stage scaling | design px only |
| `position: fixed` inside a slide | escapes the transformed stage (fixed is relative to viewport, not stage) | use `absolute` (stage is the containing block) |
| animating `display` | steps snap instead of easing | `visibility` + opacity/transform |
| hover-dependent content | invisible when projected/printed | hover is garnish only |
| `100%` heights on nested flex | Safari collapse | give slides explicit flex layout |
| font-size in rem | inherits browser setting, breaks the contract | px only inside the stage |

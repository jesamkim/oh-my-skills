# Layout Catalog

Each layout: when to use, structure, and copy-paste HTML/CSS sized for the
1920×1080 stage. All sizes are design px (see engine.md). Shared
assumptions: slide padding 96px 120px; gutters 32-48px; boxes sized by the
grid (`1fr`), never shrink-wrapped to content.

**Mix Rule**: never the same layout 3+ times in a row. Centered-symmetric
variants count as one implicit grammar. An 8+ deck uses ≥ 4 distinct
layouts. Vary rhythm: dense (bento, comparison) → breather (statement,
quote) → dense.

**Surface-variety rule**: layout names can differ while the screen stays
the same — rounded `.cell` cards dominate layouts 6, 7, 10, 11, and a deck
that reaches for them every time reads as monotonous grey boxes regardless
of the Mix Rule. So: **use card (`.cell`) layouts at most twice in a row;
make the third information group card-free** — Ledger List (14), Indexed
Definitions (15), Split Contrast (16), Two-Column (5), or a chart (17-18).
Card layout ↔ card-free layout is itself a rhythm; alternate it.

**Card fill rule** (field QA lesson): grid sizes the card's WIDTH, but
don't let a short-content card stretch to full remaining height with the
text top-anchored — a card whose bottom 60% is empty reads as unfinished.
Pick one per row: (a) cap the row height to the content band
(`align-content:start` + fixed row height), (b) vertically center the
card's content (`justify-content:center`), or (c) bottom-anchor it
(`justify-content:flex-end`, the bento signature). Same choice for every
sibling card.

**Korean display-text line breaks**: `keep-all` prevents mid-word breaks
but not orphan lines — a headline wrapping as "…하루면 / 됩니다." strands
a single word. For headings ≥ 64px, control breaks manually with `<br>`
at phrase boundaries (2-3 balanced lines), or `max-width` tuned so each
line carries ≥ 2 어절.

Shared helper classes used below:

```css
.eyebrow {
  font-size: 26px; text-transform: uppercase; letter-spacing: .16em;
  color: var(--accent); font-weight: 700; margin-bottom: 28px;
}
.h2 {
  font-family: var(--font-display); font-size: 72px; font-weight: 800;
  line-height: 1.1; letter-spacing: -0.02em; margin-bottom: 48px;
}
.body { font-size: 38px; line-height: 1.55; color: var(--text); }
.muted { color: var(--muted); }
```

---

## 1. Title

Flush-left, bottom-anchored (asymmetric > centered). The title typography
is the hero — no decorative panels.

```html
<section class="slide" id="s1">
  <div style="margin-top:auto; max-width:1400px;">
    <p class="eyebrow">AWS Summit Seoul · 2026</p>
    <h1 style="font-family:var(--font-display); font-size:136px; font-weight:800;
               line-height:1.04; letter-spacing:-0.03em;">
      에이전트가 일하는<br>클라우드
    </h1>
    <p style="font-size:42px; color:var(--muted); margin-top:40px;">
      Bedrock AgentCore로 보는 자율 에이전트 아키텍처
    </p>
  </div>
  <p style="position:absolute; right:120px; bottom:96px; font-size:24px;"
     class="muted">발표자 이름 · 직함/역할</p>
</section>
```

## 2. Section Divider

Giant numeral as the visual anchor. Solid background, nothing else.

```html
<section class="slide">
  <div style="margin:auto 0;">
    <div style="font-family:var(--font-display); font-size:300px; font-weight:800;
                line-height:1; white-space:nowrap; background:var(--grad);
                -webkit-background-clip:text; background-clip:text; color:transparent;">01</div>
    <h2 class="h2" style="margin:24px 0 0;">왜 지금 에이전트인가</h2>
    <p style="font-size:38px;" class="muted">시장 신호 세 가지</p>
  </div>
</section>
```

## 3. Big Statement (breather)

One sentence, 20-30% content coverage — the deliberate exception to the
space budget. Use 1-2 per deck between dense slides.

```html
<section class="slide">
  <p style="margin:auto; max-width:1500px; font-family:var(--font-display);
            font-size:104px; font-weight:800; line-height:1.15;
            letter-spacing:-0.02em; text-align:left;">
    모델이 아니라 <span style="color:var(--accent)">루프</span>가
    제품입니다.
  </p>
</section>
```

## 4. Hero Stat

One number owns the slide. Pairs with the count-up effect.

```html
<section class="slide">
  <div style="margin:auto 0;">
    <div class="stat" data-count="503" style="font-family:var(--font-display);
         font-size:360px; font-weight:800; line-height:1;
         background:var(--grad); -webkit-background-clip:text;
         background-clip:text; color:transparent;
         font-variant-numeric:tabular-nums;">503</div>
    <p style="font-size:44px; margin-top:24px;">건의 프로덕션 배포, 첫 90일 동안</p>
    <p style="font-size:26px; margin-top:12px;" class="muted">출처: 내부 배포 로그, 2026 Q2</p>
  </div>
</section>
```

## 5. Two-Column Asymmetric (35/65)

The default two-region layout. 50/50 is banned — asymmetry gives the eye
a starting point. Narrow side: short label/claim. Wide side: the payload.

```html
<section class="slide">
  <h2 class="h2">아키텍처 선택지</h2>
  <div style="display:grid; grid-template-columns:5fr 9fr; gap:64px; flex:1;">
    <div>
      <p style="font-family:var(--font-display); font-size:52px; font-weight:800;
                line-height:1.2;">런타임이<br>결정합니다</p>
      <p style="font-size:32px; margin-top:24px;" class="muted">확장 단위 = 에이전트 세션</p>
    </div>
    <div class="body">
      <ul style="list-style:none; display:flex; flex-direction:column; gap:36px;">
        <li data-step><strong style="color:var(--accent)">세션 격리</strong> — microVM 단위 실행, 상태 유출 없음</li>
        <li data-step><strong style="color:var(--accent)">버스트 확장</strong> — 콜드스타트 &lt; 1s, 요청당 과금</li>
        <li data-step><strong style="color:var(--accent)">긴 수명</strong> — 8시간 세션, 비동기 작업 유지</li>
      </ul>
    </div>
  </div>
</section>
```

## 6. Bento Grid

5-7 items with importance hierarchy — dominant cell ≥ 1.5× the others,
uniform 32px gap, shared radius. Cells are grid-sized, never content-sized.

```html
<section class="slide">
  <h2 class="h2">2026 상반기 하이라이트</h2>
  <div style="display:grid; flex:1; gap:32px;
              grid-template-columns:repeat(4,1fr); grid-template-rows:repeat(2,1fr);">
    <div class="cell" style="grid-column:span 2; grid-row:span 2;"><!-- LARGE -->
      <p class="eyebrow">모델</p>
      <p style="font-size:44px; font-weight:700; line-height:1.3;">Claude Fable 5 GA<br>Bedrock 글로벌 CRIS</p>
    </div>
    <div class="cell"><p class="eyebrow">에이전트</p><p style="font-size:34px;">AgentCore 정식 출시</p></div>
    <div class="cell"><p class="eyebrow">보안</p><p style="font-size:34px;">Guardrails v3</p></div>
    <div class="cell" style="grid-column:span 2;"><!-- WIDE -->
      <p class="eyebrow">경제성</p><p style="font-size:34px;">추론 비용 전년 대비 -80%</p>
    </div>
  </div>
</section>
<style>
.cell { background:var(--surface); border-radius:24px; padding:48px;
        display:flex; flex-direction:column; justify-content:flex-end; }
</style>
```

## 7. Card Row (3-up)

Equal siblings — same size by grid, text fills the card. Use bento instead
when importance differs.

```html
<section class="slide">
  <h2 class="h2">세 가지 통합 패턴</h2>
  <div style="display:grid; grid-template-columns:repeat(3,1fr); gap:40px; flex:1;">
    <!-- repeat 3x, identical structure -->
    <div class="cell" data-step>
      <div style="font-size:64px; font-weight:800; color:var(--accent);">A</div>
      <p style="font-size:40px; font-weight:700; margin:20px 0;">Tools-as-API</p>
      <p style="font-size:32px; line-height:1.5;" class="muted">
        기존 REST를 MCP 게이트웨이로 노출. 코드 변경 없음.
      </p>
    </div>
  </div>
</section>
```

## 8. Quote

```html
<section class="slide">
  <div style="margin:auto 0; max-width:1480px;">
    <div style="font-size:200px; line-height:.6; color:var(--accent);
                font-family:var(--font-display);">“</div>
    <p style="font-family:var(--font-display); font-size:76px; font-weight:600;
              line-height:1.3; margin:32px 0 48px;">
      6개월 걸릴 마이그레이션을 3주 만에 끝냈습니다.
    </p>
    <p style="font-size:34px;"><strong>박OO</strong>
       <span class="muted"> · 플랫폼 리드, OO커머스</span></p>
  </div>
</section>
```

## 9. Timeline / Steps

Horizontal, numbered, connector line behind. Steps reveal one by one.

```html
<section class="slide">
  <h2 class="h2">도입 로드맵</h2>
  <div style="display:grid; grid-template-columns:repeat(4,1fr); gap:40px;
              flex:1; align-content:center; position:relative;">
    <div style="position:absolute; top:44px; left:5%; right:5%; height:2px;
                background:var(--surface);"></div>
    <!-- repeat 4x -->
    <div data-step style="position:relative;">
      <div style="width:88px; height:88px; border-radius:50%;
                  background:var(--accent); color:var(--bg);
                  display:grid; place-items:center;
                  font-size:40px; font-weight:800;">1</div>
      <p style="font-size:36px; font-weight:700; margin:28px 0 12px;">PoC</p>
      <p style="font-size:30px; line-height:1.5;" class="muted">단일 유스케이스, 2주</p>
    </div>
  </div>
</section>
```

## 10. Comparison (2-way)

Verdict-first: visually favor the recommended side (accent border) rather
than false symmetry.

```html
<section class="slide">
  <h2 class="h2">직접 구축 vs 매니지드</h2>
  <div style="display:grid; grid-template-columns:1fr 1fr; gap:48px; flex:1;">
    <div class="cell" style="opacity:.75;">
      <p style="font-size:42px; font-weight:700;">직접 구축</p>
      <ul class="body" style="margin-top:32px; line-height:1.8; font-size:34px;">
        <li>인프라 제어 최대</li><li>운영 인력 2-3 FTE</li><li>TTM 4-6개월</li>
      </ul>
    </div>
    <div class="cell" style="border:3px solid var(--accent);">
      <p style="font-size:42px; font-weight:700;">매니지드
        <span style="font-size:26px; color:var(--accent); vertical-align:middle;
        margin-left:16px;">RECOMMENDED</span></p>
      <ul class="body" style="margin-top:32px; line-height:1.8; font-size:34px;">
        <li>운영 0 FTE</li><li>세션 격리 내장</li><li>TTM 2-3주</li>
      </ul>
    </div>
  </div>
</section>
```

## 11. Code Walkthrough

Code left (60%), annotations right. Code ≤ 14 lines, 28-32px mono. More
code → more slides, not smaller font. Highlight the lines that matter with
`.hl`.

```html
<section class="slide">
  <h2 class="h2">에이전트 정의는 12줄</h2>
  <div style="display:grid; grid-template-columns:8fr 5fr; gap:56px; flex:1;">
    <pre style="background:var(--surface); border-radius:20px; padding:48px;
                font-family:var(--font-mono); font-size:30px; line-height:1.6;
                overflow:hidden;"><code>from strands import Agent

agent = Agent(
    model="claude-fable-5",
<span class="hl">    tools=[search, deploy],</span>
    system="You are an SRE."
)
agent("서울 리전 p99 급증 원인?")</code></pre>
    <div style="display:flex; flex-direction:column; gap:32px; justify-content:center;">
      <div class="cell" data-step style="padding:36px;">
        <p class="eyebrow" style="margin-bottom:12px;">WHY</p>
        <p style="font-size:30px; line-height:1.5;">툴 목록이 곧 권한 경계</p>
      </div>
      <div class="cell" data-step style="padding:36px;">
        <p class="eyebrow" style="margin-bottom:12px;">GOTCHA</p>
        <p style="font-size:30px; line-height:1.5;">system 프롬프트에 범위 제한 명시</p>
      </div>
    </div>
  </div>
</section>
<style>.hl { background:color-mix(in srgb, var(--accent) 22%, transparent);
             display:inline-block; width:100%; }</style>
```

## 12. Image Full Bleed

Image or gradient fills the entire stage (inset 0, padding 0), dark
overlay for legibility, one message. Max 1-2 per deck.

```html
<section class="slide" style="padding:0;">
  <img src="data:image/..." alt=""
       style="position:absolute; inset:0; width:100%; height:100%;
              object-fit:cover;" class="kenburns">
  <div style="position:absolute; inset:0;
              background:linear-gradient(180deg, transparent 30%, rgba(0,0,0,.72));"></div>
  <p style="position:absolute; left:120px; bottom:120px; max-width:1300px;
            font-family:var(--font-display); font-size:88px; font-weight:800;
            line-height:1.1; color:#fff;">현장은 이미 움직이고 있습니다</p>
</section>
```

## 13. Closing

Default to a single-page **"감사합니다."** and nothing else — one centered
line of display type, mirroring the title slide's composition (수미상관).
The bare thank-you reads as confident and lets the deck land on a clean
beat; a wall of contact details on the last slide dilutes that. Add a
contact/CTA line only when the user explicitly asks for one (email, QR,
"데모 요청"). Keep the honorific tone here too — "감사합니다", never a plain
"고맙다".

```html
<section class="slide">
  <div style="margin:auto 0; text-align:center;">
    <h2 style="font-family:var(--font-display); font-size:140px; font-weight:800;
               letter-spacing:-0.03em;">감사합니다</h2>
  </div>
</section>
```

If the user does want contact info, add one muted line beneath:

```html
    <p style="font-size:38px; margin-top:40px;" class="muted">
      발표자-이메일@ · 데모 요청은 QR 또는 메일로
    </p>
```

---

# Card-free layouts (surface variety)

Layouts 6, 7, 10, 11 all lean on the `.cell` card (rounded `--surface`
box). Lean on them too often and a deck collapses into "a few grey rounded
boxes" no matter how the layout names differ — the #1 source of the
sameness feeling. Layouts 14-16 build structure from **hairline rules,
whitespace, and alignment instead of card fills**. They shine in Paper
Editorial and Swiss Minimal (where rules/whitespace ARE the system) but
work in every theme. See the Surface-variety rule under Mix Rule.

## 14. Ledger List (ruled rows)

The card-free replacement for Card Row (7). Each item is a full-width row
divided only by a top hairline — a magazine contents page. Left: a short
label or index; right: the payload. No boxes.

```html
<section class="slide">
  <h2 class="h2">세 가지 통합 패턴</h2>
  <div style="display:grid; flex:1; align-content:center;">
    <!-- repeat 3-5x -->
    <div data-step style="display:grid; grid-template-columns:4fr 8fr; gap:64px;
         align-items:baseline; padding:40px 0; border-top:1px solid var(--muted);">
      <p style="font-family:var(--font-display); font-size:44px; font-weight:800;">
        Tools-as-API</p>
      <p style="font-size:36px; line-height:1.5;" class="muted">
        기존 REST를 MCP 게이트웨이로 노출. 코드 변경 없이 에이전트가 호출.</p>
    </div>
  </div>
</section>
```

Tip: give the last row `border-bottom` too so the list reads as a closed
block. Accent one label per slide (the one you'll dwell on), not all.

## 15. Indexed Definitions (hanging numerals)

Card-free replacement for Bento (6) when items are peers, not a hierarchy.
Oversized index numerals (01–04) anchor each entry; a hanging indent groups
the text. Grouping comes from whitespace, not a box.

```html
<section class="slide">
  <h2 class="h2">도입을 막는 네 가지 오해</h2>
  <div style="display:grid; grid-template-columns:1fr 1fr; gap:72px 96px; flex:1;
              align-content:center;">
    <!-- repeat 4x -->
    <div data-step style="display:grid; grid-template-columns:auto 1fr; gap:32px;
                          align-items:start;">
      <span style="font-family:var(--font-display); font-size:88px; font-weight:800;
                   line-height:.9; color:var(--accent);">01</span>
      <div>
        <p style="font-size:40px; font-weight:700; margin-bottom:12px;">비용이 는다</p>
        <p style="font-size:30px; line-height:1.5;" class="muted">
          세션당 과금은 유휴 인스턴스보다 대체로 싸다.</p>
      </div>
    </div>
  </div>
</section>
```

## 16. Split Contrast (ruled comparison)

Card-free Comparison (10). One vertical hairline splits the stage; the
verdict is carried by weight and alignment, not a bordered box. Favored
side gets the accent label and heavier type.

```html
<section class="slide">
  <h2 class="h2">직접 구축 vs 매니지드</h2>
  <div style="display:grid; grid-template-columns:1fr 1px 1fr; gap:0; flex:1;
              align-items:center;">
    <div style="padding-right:72px; opacity:.7;">
      <p style="font-size:40px; font-weight:700; margin-bottom:32px;">직접 구축</p>
      <ul class="body" style="line-height:1.9; font-size:34px; list-style:none;">
        <li>인프라 제어 최대</li><li>운영 2-3 FTE</li><li>TTM 4-6개월</li></ul>
    </div>
    <div style="background:var(--muted); align-self:stretch;"></div>
    <div style="padding-left:72px;">
      <p style="font-size:40px; font-weight:800; margin-bottom:32px;">매니지드
        <span style="font-size:24px; color:var(--accent); margin-left:14px;">추천</span></p>
      <ul class="body" style="line-height:1.9; font-size:34px; list-style:none; font-weight:600;">
        <li>운영 0 FTE</li><li>세션 격리 내장</li><li>TTM 2-3주</li></ul>
    </div>
  </div>
</section>
```

---

# Chart layouts (pairs with A9 chart draw-on)

Hand-authored inline SVG (engine policy — no chart libs). Every bar height
/ arc value is the REAL number, so print and reduced-motion show the true
chart; A9's `barGrow` / `arcFill` only reveal it on `data-step`. Axis and
labels use `--muted`; bars/arcs use the accent family (stay ≤ 5 colors).

## 17. Bar Chart

3-7 categories, one series. Bars grow from the baseline. For a horizontal
comparison of magnitudes; more than 7 bars → aggregate or split slides.

```html
<section class="slide">
  <h2 class="h2">리전별 p99 지연 (ms)</h2>
  <div style="flex:1; display:grid; grid-template-columns:1fr; align-content:end;">
    <div style="display:grid; grid-template-columns:repeat(5,1fr); gap:48px;
                align-items:end; height:560px; border-bottom:2px solid var(--muted);">
      <!-- repeat per datum; height % = value / max -->
      <div style="display:flex; flex-direction:column; align-items:center; gap:20px; height:100%; justify-content:flex-end;">
        <span class="stat" data-count="182" style="font-size:36px; font-weight:800;
              font-variant-numeric:tabular-nums;">182</span>
        <div class="bar" style="--i:0; width:100%; height:46%; background:var(--accent);
             border-radius:8px 8px 0 0;"></div>
      </div>
      <!-- …more bars, each with its own --i and height% … -->
    </div>
    <div style="display:grid; grid-template-columns:repeat(5,1fr); gap:48px; margin-top:20px;">
      <span style="text-align:center; font-size:28px;" class="muted">서울</span>
      <!-- …matching labels… -->
    </div>
  </div>
</section>
```

Bars pair with A6 count-up (the value ticks while the bar grows) and A9
`barGrow`. Line-chart variant: swap the bar row for one A9 `.draw-line`
`<path pathLength="1">` over an SVG grid — same slide frame.

## 18. Donut / Pie + KPI

One dominant ratio. Donut with the headline percent in the hole (the data
version of Hero Stat 4); a legend sits beside it. For a pie, widen
`stroke-width` toward the radius.

```html
<section class="slide">
  <h2 class="h2">추론 비용 절감 구성</h2>
  <div style="display:grid; grid-template-columns:5fr 6fr; gap:96px; flex:1; align-items:center;">
    <div style="position:relative; justify-self:center;">
      <svg viewBox="0 0 240 240" width="440" height="440">
        <circle cx="120" cy="120" r="104" fill="none" stroke="var(--surface)" stroke-width="28"/>
        <!-- --rest = 100 − 68 ; A9 arcFill sweeps to it -->
        <circle class="arc" pathLength="100" style="--rest:32" cx="120" cy="120" r="104"
                fill="none" stroke="var(--accent)" stroke-width="28" stroke-linecap="round"
                transform="rotate(-90 120 120)"/>
      </svg>
      <div style="position:absolute; inset:0; display:flex; align-items:baseline;
                  justify-content:center;">
        <span class="stat" data-count="68" style="font-family:var(--font-display);
              font-size:120px; font-weight:800;">68</span><span style="font-size:48px;
              font-weight:700; margin-left:6px;">%</span>
      </div>
    </div>
    <ul style="list-style:none; display:flex; flex-direction:column; gap:36px;">
      <li data-step style="display:flex; align-items:center; gap:24px; font-size:36px;">
        <span style="width:28px; height:28px; border-radius:6px; background:var(--accent);"></span>
        캐싱·배치 <span class="muted" style="margin-left:auto;">68%</span></li>
      <li data-step style="display:flex; align-items:center; gap:24px; font-size:36px;">
        <span style="width:28px; height:28px; border-radius:6px; background:var(--surface);"></span>
        모델 최적화 <span class="muted" style="margin-left:auto;">32%</span></li>
    </ul>
  </div>
</section>
```

---

## Composition sequence guide

A proven 10-slide rhythm:

| # | Layout | Role |
|---|--------|------|
| 1 | Title | hook |
| 2 | Big Statement | thesis |
| 3 | Section Divider | ch.1 |
| 4 | Two-Column Asymmetric | argument |
| 5 | Hero Stat / Bar Chart / Donut+KPI | evidence |
| 6 | Bento Grid | landscape |
| 7 | Section Divider | ch.2 |
| 8 | Code Walkthrough / Timeline | how |
| 9 | Comparison | decision |
| 10 | Closing | CTA |

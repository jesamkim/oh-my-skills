---
name: paper-trans
description: |
  Format-preserving academic paper PDF translation to Korean.
  Overlay method: original text blocks are redacted in place (figures,
  equations, line art preserved) and Korean is inserted into the same bbox,
  so page count and layout stay identical to the source paper.
  Input: local PDF path or URL (arxiv.org/abs links auto-convert to /pdf).
  Claude translates directly (no external MT API); papers over 10 pages use
  parallel subagent translation. Output: KO_<name>.pdf plus verification.
  Trigger: "paper translate", "translate paper", "paper-trans", "논문 번역",
  "arxiv 번역", "페이퍼 번역", "translate this paper to Korean"
license: MIT License
metadata:
    skill-author: Jesam Kim
    version: 1.1.0
allowed-tools: [Read, Write, Edit, Bash, Grep, Glob, Task]
---

# Paper Format-Preserving PDF Translation

## Overview

Translate academic paper PDFs (arXiv, ACL, IEEE, ACM, ...) into Korean while
keeping the **original layout, page count, figures, tables, and equations
intact**. The method is an in-place overlay: each translatable text block is
erased from the original page (text only — images and vector line art are
preserved) and the Korean translation is inserted into the same bounding box,
auto-shrinking when the translation runs longer than the original.

**Pipeline**: fetch -> extract/classify -> Claude translates JSON -> overlay -> verify.

**What gets translated**: body paragraphs, abstract, figure/table captions.
**What stays original**: equations, code blocks, the References list,
authors/affiliations/emails, paper and section titles, headers/footers/page
numbers, arXiv margin stamp, text inside figures, tables of symbols.

## Critical Rules

### NEVER DO
- **NEVER** translate blocks marked `"translate": false` unless you have a
  clear reason to override (then flip the flag AND fill `translated_text`)
- **NEVER** translate `figure-text` / `rotated` blocks (labels inside
  diagrams) — overwriting them is what garbles figures; leave them original
- **NEVER** modify `id`, `page`, `bbox`, `font_size`, or `bold` fields
- **NEVER** translate: model/dataset/product names, technical acronyms,
  author names, citation markers `[12]`, inline math symbols, URLs
- **NEVER** produce invalid JSON — escape inner double quotes with `\"`

### ALWAYS DO
- **ALWAYS** fill only the `translated_text` field
- **ALWAYS** use academic written Korean (문어체: "~한다", "~이다")
- **ALWAYS** keep `"그림 N:"` / `"표 N:"` prefixes for captions
- **ALWAYS** run the verify step with `--blocks` (figure-integrity diff) and
  the Vision QA before delivering, and Read every `figdiff_*` crop pair

## Prerequisites

- PyMuPDF: `pip install pymupdf` (1.26+ for `insert_htmlbox`)
- A Korean font (NanumGothic preferred): `sudo apt install fonts-nanum`
  (the apply script auto-detects via known paths and `fc-match`)

## Step 0 — Resolve input

Accept a local PDF path or a URL. arXiv `abs` pages are rewritten to `/pdf/`.

```bash
python ${SKILL_DIR}/scripts/fetch_pdf.py "<url-or-path>" --out-dir <workdir>
```

The last stdout line is the local PDF path. Exit 1 = download/validation
failure; report the error to the user.

## Step 1 — Extract and classify blocks

```bash
# Small papers (<= 10 translatable pages): single JSON
python ${SKILL_DIR}/scripts/extract_blocks.py "<paper.pdf>"

# Larger papers: one JSON per 3-page group, translatable blocks only
python ${SKILL_DIR}/scripts/extract_blocks.py "<paper.pdf>" --split-pages 3 --translatable-only
```

Outputs `{stem}_blocks.json` (or `{stem}_blocks_g{K}.json` per group) plus a
classification histogram on stderr. Review the histogram: `TRANSLATE` should
dominate on body pages; `references`, `front-matter`, `figure-text`, `math`
buckets should be non-zero for a typical paper.

**Exit 2** means the PDF has no usable text layer (scanned document) — stop
and tell the user OCR is out of scope for this skill.

Each block:

```json
{"id": "p3_b7", "page": 3, "bbox": [53.8, 84.8, 295.6, 227.0],
 "text": "English text ...", "font_size": 8.96, "bold": false,
 "translate": true, "reason": "body", "translated_text": null}
```

The classifier is heuristic. You may override individual mistakes during
translation: a mislabeled skip block can be translated by setting
`"translate": true` + `translated_text`; a mislabeled body block (e.g. a
table of numbers) is skipped by leaving `translated_text` null.

## Step 2 — Translate the JSON (Claude)

### Workflow A — Sequential (single JSON, small papers)

Read the blocks JSON, translate every `"translate": true` block, write the
JSON back with `translated_text` filled.

### Workflow B — Parallel (group JSONs, > 10 pages)

Dispatch one subagent per group file (all in parallel). Subagent prompt
template:

```
You are a professional English-to-Korean translator for academic AI/ML papers.
Edit the JSON file: {group_file}
For EVERY block with "translate": true, fill "translated_text" with a Korean
translation. Do not modify any other field.

Rules:
- Academic written register (문어체: "~한다", "~이다"), natural Korean structure.
- KEEP IN ENGLISH: model/product/dataset names, technical acronyms
  (ML, RL, LLM, API, ...), author names, citation markers like [12],
  inline math symbols, URLs.
- Captions: "Figure N:" -> "그림 N:", "Table N:" -> "표 N:".
- If a block is clearly not translatable prose (numeric table, code,
  figure fragment), leave translated_text null.
- CRITICAL: output must remain valid JSON — escape inner double quotes (\").
Write the complete updated JSON back to the same path, then verify with:
python3 -c "import json; json.load(open('{group_file}'))"
```

After all subagents return, audit coverage before applying:

```bash
python3 -c "
import json, glob
for f in sorted(glob.glob('<stem>_blocks_g*.json')):
    d = json.load(open(f))
    miss = [b['id'] for b in d['blocks'] if b['translate'] and not b['translated_text']]
    print(f, 'missing:', miss)
"
```

Re-dispatch a fix-up subagent for any file with missing blocks.

## Step 3 — Apply overlay

```bash
python ${SKILL_DIR}/scripts/apply_overlay.py "<paper.pdf>" "<stem>_blocks*.json"
```

Creates `KO_{name}.pdf` (override with `--out`, prefix with `--prefix JA_`
etc.) and `{stem}_apply_report.json` with expected/untranslated/applied/
failed/shrunk stats. Per page it redacts only the translated blocks' text
(images and line art preserved via `PDF_REDACT_IMAGE_NONE` /
`PDF_REDACT_LINE_ART_NONE`), then inserts Korean with `insert_htmlbox`
(auto-shrink down to scale 0.4, NanumGothic with DejaVu fallback for math
glyphs).

Safety behavior:
- Every JSON is validated against the target PDF (source name, page count,
  page ranges, duplicate ids) — mismatches abort before any redaction.
- `translate: true` blocks without `translated_text` are kept original and
  listed in the report (`untranslated`) — the intended path for blocks a
  translator judged non-prose.
- A block that cannot fit even at scale 0.4 counts as failed, and the
  output is saved as `KO_{name}.partial.pdf` instead of the normal name so
  a broken PDF is never presented as the final result. Shorten those
  translations in the JSON and re-run.

## Step 4 — Verify + Vision QA

```bash
python ${SKILL_DIR}/scripts/verify_output.py "<paper.pdf>" "KO_<name>.pdf" \
    "<stem>_apply_report.json" --blocks "<stem>_blocks*.json" \
    --render 0,1,5 --render-dir <workdir>/qa
```

Checks page count, failed insertions, hangul coverage, excessive shrink
(< 0.6 scale). **Always pass `--blocks`** — every paper has figures, so the
**figure-integrity diff** is part of the standard QA, not an add-on. It
renders every page of source and output, masks the regions where change is
expected (translated prose blocks, rasterized pages, existing patches), and
pixel-compares the rest. Any residual diff means the overlay touched
something it should not have — typically labels inside a figure that were
redacted or overwritten (this is exactly how garbled "Figure 1" text was
caught on arXiv 2508.02292). The check is deterministic (each page is
rendered once from its own document handle), so a clean result is
trustworthy. Each finding is reported with its bbox, side-by-side
`figdiff_*` crops, and a ready-to-run patch command.

Then **Read the rendered PNGs** (including every `figdiff_*` crop pair) and
visually confirm:
- Korean text fits its box, no overlap with neighbors or figures
- No leftover English fragments inside translated regions
- Figures/tables/equations undamaged, no garbled or tofu characters inside
  figures (if damaged -> crop-patch fallback below)

Fix prose issues by editing the affected block's JSON (e.g. shorten the
translation, or null out a figure block's `translated_text`) and re-running
Step 3. Render 2-3 representative pages: page 0, the densest body page, and
one caption/figure-heavy page.

### Crop-patch fallback (damaged figure regions)

**Confirm before patching.** A figdiff finding is a *candidate*, not a
verdict — the pixel diff can flag a legitimate change or a boundary artifact.
Always Read the `figdiff_*_src.png` / `figdiff_*_out.png` pair first and
judge whether the figure is actually damaged. Patch only regions you have
visually confirmed as damaged; report ambiguous ones to the user rather than
patching blind.

When a figdiff crop shows real damage — a figure label wiped by redaction,
Korean text sitting inside a diagram, lost strokes — paste the original
pixels back over just that region. `verify_output.py` prints the exact
command for each finding:

```bash
python ${SKILL_DIR}/scripts/patch_regions.py "<paper.pdf>" "KO_<name>.pdf" \
    --region 4:160.4,86.3,386.0,98.8 --region 4:411.0,109.3,471.0,128.3
```

Each region is rendered from the SOURCE page at 300 dpi and inserted over
the same rect in the output, so the figure area becomes a pixel-perfect
image of the original (non-selectable, but visually intact). Prefer fixing
the root cause first — a figure block that got translated should have its
`translated_text` nulled and Step 3 re-run; patch only what redaction
itself damaged. **Run patching last**: re-running apply_overlay.py
regenerates the PDF and discards patches. After patching, re-run Step 4 —
patched regions are auto-masked, so a clean result confirms the fix.

If a diff is legitimate (e.g. a page you deliberately altered), exclude it
with `--fig-skip-pages 4` instead of patching.

### Rasterize fallback (whole-page)

If damage is spread across a whole page (vector figure losing many strokes,
table rules disappearing everywhere), patching region-by-region is not
worth it — re-run Step 3 with that page in rasterize mode instead. The page
is rendered to a 200-dpi image as background, translated regions are
covered with white patches, and Korean is overlaid on top. Text on such
pages becomes non-selectable but visuals are pixel-perfect:

```bash
python ${SKILL_DIR}/scripts/apply_overlay.py "<paper.pdf>" "<stem>_blocks*.json" --rasterize-pages 4,7
```

## Translation Quality Guidelines

- Terminology consistent across the whole paper (e.g. "reinforcement
  learning" -> "강화학습" everywhere)
- Keep sentence-level fidelity; do not summarize or expand
- Prefer established Korean academic terms; keep the English in parentheses
  on first use only when the Korean term is uncommon:
  "지식 증류(knowledge distillation)"
- Numbers, percentages, units: keep as-is

## Edge Cases

- **Scanned PDF**: extract exits 2 — abort with a clear user message
- **Two-column layouts**: handled naturally (block-level processing)
- **Overflow**: htmlbox auto-shrinks to 0.4 scale; verify warns below 0.6,
  and below 0.4 the block fails (output becomes `.partial.pdf`) — shorten
  those translations and re-apply
- **Hyperlinks**: annotation layer untouched by redaction — preserved
- **Appendix after References**: classifier resumes translation at bold
  appendix headings ("A.1 ...") — spot-check this boundary in the JSON

## Output Naming

- Default: `KO_{original_name}.pdf` (same directory as source)
- Other languages: `--prefix JA_` etc., and adapt the translation prompt

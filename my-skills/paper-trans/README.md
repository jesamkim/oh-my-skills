# paper-trans

Format-preserving academic paper PDF translation to Korean.

Translates a paper (local PDF or URL, e.g. `https://arxiv.org/pdf/2508.02292`)
into Korean while keeping the original layout, page count, figures, tables,
and equations intact, and produces `KO_<name>.pdf`.

## How it works

1. **fetch_pdf.py** — resolves the input: downloads URLs (arXiv `abs` links
   are rewritten to `/pdf/`), validates local paths.
2. **extract_blocks.py** — extracts text blocks with PyMuPDF and classifies
   each one: body/abstract/captions are marked for translation; equations
   (math fonts), code (monospace), the References list, authors/affiliations,
   headers/footers, figure-internal text, and titles keep the original.
   Detects scanned PDFs (no text layer) and aborts — OCR is out of scope.
3. **Claude translation** — Claude fills `translated_text` in the block JSON
   directly (no external MT API). Papers over ~10 pages are translated by
   parallel subagents, one per page group.
4. **apply_overlay.py** — redacts only the original text of translated
   blocks (images and vector line art preserved) and inserts Korean into the
   same bounding box via `insert_htmlbox` with auto-shrink (NanumGothic).
   A `--rasterize-pages` fallback renders problem pages as background images
   (capture-and-crop) when redaction would damage complex vector figures.
5. **verify_output.py** — checks page count, failed insertions, hangul
   coverage, and excessive shrink; renders pages to PNG for Claude Vision QA.

## Requirements

- Python 3.10+, PyMuPDF 1.26+ (`pip install pymupdf`)
- Korean font: `sudo apt install fonts-nanum` (auto-detected; `fc-match`
  fallback)

## Usage (via Claude Code)

Say: "이 논문 한글로 번역해줘: https://arxiv.org/pdf/2508.02292"

Or run the scripts directly:

```bash
python scripts/fetch_pdf.py "https://arxiv.org/abs/2508.02292" --out-dir work
python scripts/extract_blocks.py work/2508.02292.pdf --split-pages 3 --translatable-only
# ... fill translated_text in the JSON files (Claude) ...
python scripts/apply_overlay.py work/2508.02292.pdf "work/2508.02292_blocks*.json"
python scripts/verify_output.py work/2508.02292.pdf work/KO_2508.02292.pdf \
    work/2508.02292_apply_report.json --render 0,1 --render-dir work/qa
```

## Scope

- Translated: body paragraphs, abstract, figure/table captions
- Kept original: equations, code, References, authors/affiliations,
  paper/section titles, headers/footers, text inside figures

## License

MIT

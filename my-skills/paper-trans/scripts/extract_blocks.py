#!/usr/bin/env python3
"""Extract text blocks from a paper PDF and classify them for translation.

Classification (translate: true/false + reason):
- body / abstract / caption  -> translate
- math, code, references (and everything after), front-matter (page-1 title,
  authors, affiliations), margin (headers/footers/page numbers/arXiv stamp),
  figure-text, rotated, tiny -> keep original
Claude may override individual decisions during the translation step.
"""
import argparse
import json
import pathlib
import re
import statistics
import sys

import fitz

MATH_FONT = re.compile(r"(CMMI|CMSY|CMEX|MSAM|MSBM|Math|rsfs|EUSM|StMary|Symbol|ESINT)", re.I)
MONO_FONT = re.compile(r"(Mono|Courier|Consolas|Typewriter|CMTT|Menlo|Inconsolata)", re.I)
REF_HEADING = re.compile(r"^\s*(references?|bibliography)\s*$", re.I)
CAPTION = re.compile(r"^\s*(figure|fig\.|table|tab\.|listing|algorithm)\s*\d+", re.I)
ABSTRACT = re.compile(r"^\s*abstract\b", re.I)
SECTION_HEADING = re.compile(
    r"^\s*(\d+(\.\d+)*\s+\S|appendix\b|acknowledg|introduction\s*$|conclusion[s]?\s*$"
    r"|related work\s*$|keywords?\s*$)",
    re.I,
)
# Appendix headings that end the References list ("A.1 Market Dataset",
# "B FinWorld as a ...", "Appendix A ...")
APPENDIX_HEADING = re.compile(r"^\s*(appendix\b|[A-Z](\.\d+)*\s+[A-Z][\w-]+)")
TABLE_SYMBOLS = "✓✗✔✘"  # check marks / crosses in comparison tables

MARGIN_PT = 70          # header/footer band height (ACM/IEEE running headers)
MIN_CHARS = 2
MATH_RATIO = 0.35
MONO_RATIO = 0.60
FIG_OVERLAP = 0.5


def clean_text(lines):
    """Join block lines, de-hyphenating end-of-line breaks."""
    out = []
    for i, line in enumerate(lines):
        t = line.rstrip()
        if not t:
            continue
        if t.endswith("-") and i < len(lines) - 1:
            out.append(t[:-1])
        else:
            out.append(t + " ")
    return "".join(out).strip()


def figure_rects(page):
    """Rects occupied by raster images and clustered vector drawings."""
    rects = []
    for img in page.get_images(full=True):
        try:
            rects.extend(page.get_image_rects(img[0]))
        except Exception:
            pass
    try:
        rects.extend(page.cluster_drawings())
    except Exception:
        pass
    # Ignore page-wide background rects
    parea = abs(page.rect)
    return [r for r in rects if 100 < abs(r) < parea * 0.9]


def analyze_block(block):
    """Return (text, stats dict) for a dict-mode text block."""
    lines_text, sizes = [], []
    chars = math_c = mono_c = bold_c = 0
    rotated = False
    for line in block["lines"]:
        if tuple(round(v, 2) for v in line["dir"]) != (1.0, 0.0):
            rotated = True
        lines_text.append("".join(s["text"] for s in line["spans"]))
        for s in line["spans"]:
            n = len(s["text"])
            if not s["text"].strip():
                continue
            chars += n
            sizes.extend([s["size"]] * n)
            if MATH_FONT.search(s["font"]):
                math_c += n
            if (s["flags"] & 8) or MONO_FONT.search(s["font"]):
                mono_c += n
            if s["flags"] & 16:
                bold_c += n
    text = clean_text(lines_text)
    return text, {
        "chars": max(chars, 1),
        "math": math_c,
        "mono": mono_c,
        "bold": bold_c,
        "size": round(statistics.median(sizes), 2) if sizes else 10.0,
        "rotated": rotated,
        "first_line": next((t.strip() for t in lines_text if t.strip()), ""),
    }


def classify(text, st, bbox, page_rect, fig_rects, ctx):
    """Return (translate, reason). ctx tracks refs_started / abstract_seen."""
    if ctx["refs_started"]:
        # An appendix often follows the reference list; a bold short heading
        # like "A.1 Market Dataset" ends references mode.
        if (APPENDIX_HEADING.match(text) and len(text) < 100
                and st["bold"] / st["chars"] > 0.5):
            ctx["refs_started"] = False
            return False, "heading"
        return False, "references"
    # clean_text() joins physical lines, so test the raw first line too:
    # a "References" heading may share its block with the first entries.
    if REF_HEADING.match(text) or REF_HEADING.match(st["first_line"]):
        ctx["refs_started"] = True
        return False, "references-heading"
    if len(text) < MIN_CHARS:
        return False, "tiny"
    if st["rotated"]:
        return False, "rotated"

    x0, y0, x1, y1 = bbox
    in_margin = y1 < page_rect.y0 + MARGIN_PT or y0 > page_rect.y1 - MARGIN_PT
    if in_margin and len(text) < 150:
        return False, "margin"
    if x1 < page_rect.x0 + 40:  # arXiv stamp strip
        return False, "margin"

    if st["math"] / st["chars"] > MATH_RATIO:
        return False, "math"
    if st["mono"] / st["chars"] > MONO_RATIO:
        return False, "code"
    if sum(text.count(c) for c in TABLE_SYMBOLS) >= 3:
        return False, "table"

    is_caption = bool(CAPTION.match(text))
    if overlap_ratio(bbox, fig_rects) > FIG_OVERLAP and not is_caption:
        return False, "figure-text"

    if ABSTRACT.match(text):
        ctx["abstract_seen"] = True
        # An "Abstract" heading alone stays; a merged abstract block translates
        if len(text) < 30:
            return False, "heading"
        return True, "abstract"
    if ctx["page"] == 0 and not ctx["abstract_seen"]:
        return False, "front-matter"
    if SECTION_HEADING.match(text) and len(text) < 80:
        return False, "heading"
    if is_caption:
        return True, "caption"
    return True, "body"


def overlap_ratio(b, rects):
    r1 = fitz.Rect(b)
    if r1.is_empty:
        return 0.0
    best = 0.0
    for r in rects:
        inter = fitz.Rect(r1) & r
        if not inter.is_empty:
            best = max(best, abs(inter) / abs(r1))
    return best


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("pdf", help="input PDF path")
    ap.add_argument("--split-pages", type=int, default=0, metavar="N",
                    help="write one JSON per N-page group (for parallel translation)")
    ap.add_argument("--translatable-only", action="store_true",
                    help="keep only translate:true blocks in the output JSON "
                         "(smaller files for subagent translation)")
    args = ap.parse_args()

    pdf_path = pathlib.Path(args.pdf).expanduser().resolve()
    doc = fitz.open(pdf_path)

    total_text = 0
    blocks = []
    ctx = {"refs_started": False, "abstract_seen": False, "page": 0}
    for pno, page in enumerate(doc):
        ctx["page"] = pno
        fig_rects = figure_rects(page)
        for bno, block in enumerate(page.get_text("dict")["blocks"]):
            if block["type"] != 0:
                continue
            text, st = analyze_block(block)
            total_text += len(text)
            translate, reason = classify(text, st, block["bbox"], page.rect, fig_rects, ctx)
            blocks.append({
                "id": f"p{pno}_b{bno}",
                "page": pno,
                "bbox": [round(v, 2) for v in block["bbox"]],
                "text": text,
                "font_size": st["size"],
                "bold": st["bold"] / st["chars"] > 0.5,
                "translate": translate,
                "reason": reason,
                "translated_text": None,
            })

    if total_text < 50 * doc.page_count:
        print("ERROR: this PDF has little or no text layer (scanned document?). "
              "paper-trans requires a text-based PDF; OCR is out of scope.",
              file=sys.stderr)
        return 2

    base = {"source_pdf": str(pdf_path), "page_count": doc.page_count}
    stem = pdf_path.with_suffix("")
    out_blocks = ([b for b in blocks if b["translate"]]
                  if args.translatable_only else blocks)
    written = []
    if args.split_pages > 0:
        n = args.split_pages
        groups = {}
        for b in out_blocks:
            groups.setdefault(b["page"] // n, []).append(b)
        for k in sorted(groups):
            out = pathlib.Path(f"{stem}_blocks_g{k}.json")
            out.write_text(json.dumps({**base, "blocks": groups[k]},
                                      ensure_ascii=False, indent=1))
            written.append(str(out))
    else:
        out = pathlib.Path(f"{stem}_blocks.json")
        out.write_text(json.dumps({**base, "blocks": out_blocks},
                                  ensure_ascii=False, indent=1))
        written.append(str(out))

    hist = {}
    for b in blocks:
        key = "TRANSLATE" if b["translate"] else b["reason"]
        hist[key] = hist.get(key, 0) + 1
    print(f"pages={doc.page_count} blocks={len(blocks)}", file=sys.stderr)
    for k in sorted(hist, key=hist.get, reverse=True):
        print(f"  {k}: {hist[k]}", file=sys.stderr)
    for w in written:
        print(w)
    return 0


if __name__ == "__main__":
    sys.exit(main())

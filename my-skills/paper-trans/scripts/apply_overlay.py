#!/usr/bin/env python3
"""Apply translated block JSON onto the original PDF as an overlay.

For every block with translated_text: redact only the original text
(images and vector line art preserved), then insert the Korean text into
the same bbox with insert_htmlbox (auto-shrink to fit).

Fallback for pages where redaction damages the visuals (--rasterize-pages):
render the original page to an image, place it as a full-page background,
cover each translated block with a white patch, then overlay the Korean
text on top (capture-and-crop workaround).
"""
import argparse
import glob
import html
import json
import pathlib
import subprocess
import sys

import fitz

SHRINK_WARN = 0.6   # report blocks shrunk below this scale
SCALE_FLOOR = 0.4   # readability floor: below this the insertion fails

FONT_CANDIDATES = [
    "/usr/share/fonts/truetype/nanum/NanumGothic.ttf",
    "/usr/share/fonts/truetype/nanum/NanumGothic-Regular.ttf",
]
BOLD_CANDIDATES = [
    "/usr/share/fonts/truetype/nanum/NanumGothicBold.ttf",
    "/usr/share/fonts/truetype/nanum/NanumGothic-Bold.ttf",
]


def find_font(candidates, pattern):
    for c in candidates:
        if pathlib.Path(c).is_file():
            return pathlib.Path(c)
    try:
        out = subprocess.run(["fc-match", "--format", "%{file}", pattern],
                             capture_output=True, text=True, timeout=10)
        p = pathlib.Path(out.stdout.strip())
        if p.is_file():
            return p
    except Exception:
        pass
    return None


def load_blocks(json_paths, pdf_path, page_count):
    """Load and merge block JSONs, validating them against the target PDF."""
    blocks, seen = [], set()
    for jp in json_paths:
        data = json.loads(pathlib.Path(jp).read_text())
        src_name = pathlib.Path(data["source_pdf"]).name
        if src_name != pdf_path.name:
            raise ValueError(f"{jp}: source_pdf is {src_name}, "
                             f"but target PDF is {pdf_path.name}")
        if data["page_count"] != page_count:
            raise ValueError(f"{jp}: page_count {data['page_count']} != "
                             f"PDF page count {page_count}")
        for b in data["blocks"]:
            if b["id"] in seen:
                raise ValueError(f"{jp}: duplicate block id {b['id']}")
            seen.add(b["id"])
            if not 0 <= b["page"] < page_count:
                raise ValueError(f"{jp}: block {b['id']} page out of range")
            blocks.append(b)
    return blocks


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("pdf", help="source PDF path")
    ap.add_argument("json_files", nargs="+",
                    help="block JSON file(s) or glob(s) with translated_text filled")
    ap.add_argument("--out", default=None, help="output PDF path (default: KO_<name>.pdf)")
    ap.add_argument("--prefix", default="KO_", help="output filename prefix")
    ap.add_argument("--rasterize-pages", default="",
                    help="comma-separated 0-based pages to process in "
                         "capture-and-crop fallback mode (page rendered as "
                         "background image instead of text redaction)")
    args = ap.parse_args()

    raster_pages = {int(x) for x in args.rasterize_pages.split(",") if x.strip()}

    pdf_path = pathlib.Path(args.pdf).expanduser().resolve()
    doc = fitz.open(pdf_path)

    json_paths = []
    for pat in args.json_files:
        json_paths.extend(sorted(glob.glob(pat)) or [pat])
    try:
        blocks = load_blocks(json_paths, pdf_path, doc.page_count)
    except (ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"ERROR: invalid block JSON: {exc}", file=sys.stderr)
        return 1

    out_path = (pathlib.Path(args.out).resolve() if args.out
                else pdf_path.parent / f"{args.prefix}{pdf_path.name}")

    regular = find_font(FONT_CANDIDATES, "NanumGothic")
    if not regular:
        print("ERROR: no Korean font found (NanumGothic). Install fonts-nanum.",
              file=sys.stderr)
        return 1
    bold = find_font(BOLD_CANDIDATES, "NanumGothic:bold")
    arch = fitz.Archive(str(regular.parent))
    css_faces = f'@font-face {{font-family: kfont; src: url("{regular.name}");}}\n'
    if bold and bold.parent == regular.parent:
        css_faces += (f'@font-face {{font-family: kfont; src: url("{bold.name}"); '
                      "font-weight: bold;}\n")
    # Fallback face for glyphs missing from the Korean font (math symbols
    # like circumflexed variables that survive in translated prose).
    font_stack = "kfont"
    fallback = pathlib.Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
    if fallback.is_file():
        arch.add(str(fallback.parent))
        css_faces += ('@font-face {font-family: ffont; '
                      f'src: url("{fallback.name}");}}\n')
        font_stack = "kfont, ffont"

    expected = [b for b in blocks if b.get("translate")]
    todo = [b for b in expected if b.get("translated_text")]
    untranslated = [b["id"] for b in expected if not b.get("translated_text")]
    if untranslated:
        print(f"WARNING: {len(untranslated)} translate:true blocks have no "
              f"translated_text (kept original): {', '.join(untranslated[:10])}"
              f"{' ...' if len(untranslated) > 10 else ''}", file=sys.stderr)
    by_page = {}
    for b in todo:
        by_page.setdefault(b["page"], []).append(b)

    applied, failed, shrunk = 0, [], []
    for pno, page_blocks in sorted(by_page.items()):
        page = doc[pno]
        if pno in raster_pages:
            # Capture-and-crop fallback: render the page, wipe ALL its content
            # (so no original text layer survives underneath), then lay the
            # rendered image back as the background.
            pix = page.get_pixmap(dpi=200)
            page.add_redact_annot(page.rect)
            page.apply_redactions(images=fitz.PDF_REDACT_IMAGE_REMOVE)
            page.insert_image(page.rect, pixmap=pix)
            for b in page_blocks:
                # Pad the white patch: rendered glyphs bleed slightly
                # outside their reported bbox.
                page.draw_rect(fitz.Rect(b["bbox"]) + (-1.5, -1.5, 1.5, 1.5),
                               color=None, fill=(1, 1, 1))
        else:
            for b in page_blocks:
                page.add_redact_annot(fitz.Rect(b["bbox"]), fill=False)
            page.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE,
                                  graphics=fitz.PDF_REDACT_LINE_ART_NONE)
        for b in page_blocks:
            rect = fitz.Rect(b["bbox"])
            text = html.escape(b["translated_text"]).replace("\n", " ")
            if b.get("bold"):
                text = f"<b>{text}</b>"
            css = (css_faces +
                   f"* {{font-family: {font_stack}; "
                   f"font-size: {b['font_size']}pt; "
                   "line-height: 1.22; margin: 0; padding: 0;}")
            try:
                spare, scale = page.insert_htmlbox(rect, text, css=css,
                                                   archive=arch,
                                                   scale_low=SCALE_FLOOR)
            except Exception as exc:
                failed.append({"id": b["id"], "error": str(exc)})
                continue
            if spare < 0:
                failed.append({"id": b["id"],
                               "error": f"does not fit at scale {SCALE_FLOOR} "
                                        "(shorten the translation)"})
            else:
                applied += 1
                if scale < SHRINK_WARN:
                    shrunk.append({"id": b["id"], "scale": round(scale, 2)})

    if failed:
        # Redactions already removed the original text of failed blocks;
        # do not present a silently broken PDF as the normal output.
        out_path = out_path.with_suffix(".partial.pdf")
        print(f"WARNING: {len(failed)} insertions failed; saving as "
              f"{out_path.name} instead of the normal output", file=sys.stderr)
    doc.subset_fonts()
    doc.ez_save(out_path)

    report = {"out_pdf": str(out_path), "page_count": doc.page_count,
              "expected_translate_blocks": len(expected),
              "untranslated": untranslated,
              "translated_blocks": len(todo), "applied": applied,
              "failed": failed, "shrunk": shrunk}
    report_path = pdf_path.parent / f"{pdf_path.stem}_apply_report.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=1))
    print(f"applied={applied}/{len(todo)} failed={len(failed)} "
          f"shrunk<{SHRINK_WARN}={len(shrunk)}", file=sys.stderr)
    print(out_path)
    print(report_path, file=sys.stderr)
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())

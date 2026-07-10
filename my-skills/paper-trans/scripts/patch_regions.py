#!/usr/bin/env python3
"""Patch regions of a paper-trans output PDF with crops from the source PDF.

Use when Vision QA (or the figure-integrity check in verify_output.py)
shows that redaction damaged content inside a figure: garbled/tofu glyphs,
wiped labels, lost strokes. Each --region is rendered from the SOURCE page
at --dpi and pasted over the same rect in the output PDF, so the figure
becomes a pixel-perfect image of the original. Text under the patch is no
longer selectable; the rest of the page keeps its text layer.

Run this LAST: re-running apply_overlay.py regenerates the output PDF and
discards patches.
"""
import argparse
import os
import pathlib
import sys
import tempfile

import fitz

PAD = 2.0  # points of padding: rendered glyphs bleed slightly outside bboxes


def parse_region(spec):
    try:
        page_s, coords = spec.split(":")
        x0, y0, x1, y1 = (float(v) for v in coords.split(","))
        return int(page_s), fitz.Rect(x0, y0, x1, y1)
    except ValueError:
        raise SystemExit(f"ERROR: bad --region {spec!r} (want page:x0,y0,x1,y1)")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("source_pdf", help="original (untranslated) PDF")
    ap.add_argument("output_pdf", help="translated KO_*.pdf to patch")
    ap.add_argument("--region", action="append", required=True,
                    help="page:x0,y0,x1,y1 (0-based page, PDF points); repeatable")
    ap.add_argument("--dpi", type=int, default=300)
    ap.add_argument("--out", default=None,
                    help="result path (default: overwrite output_pdf in place)")
    args = ap.parse_args()

    src = fitz.open(args.source_pdf)
    out_path = pathlib.Path(args.output_pdf).expanduser().resolve()
    out = fitz.open(out_path)
    if src.page_count != out.page_count:
        print(f"ERROR: page counts differ ({src.page_count} vs {out.page_count})",
              file=sys.stderr)
        return 1

    for spec in args.region:
        pno, rect = parse_region(spec)
        if not 0 <= pno < src.page_count:
            print(f"ERROR: page {pno} out of range", file=sys.stderr)
            return 1
        rect = (rect + (-PAD, -PAD, PAD, PAD)) & src[pno].rect
        if rect.is_empty:
            print(f"ERROR: region {spec} is empty after clipping", file=sys.stderr)
            return 1
        pix = src[pno].get_pixmap(dpi=args.dpi, clip=rect)
        out[pno].insert_image(rect, pixmap=pix)
        print(f"patched page {pno} rect ({rect.x0:.1f},{rect.y0:.1f},"
              f"{rect.x1:.1f},{rect.y1:.1f}) with {pix.width}x{pix.height}px "
              f"@ {args.dpi}dpi crop of the original", file=sys.stderr)

    dest = pathlib.Path(args.out).expanduser().resolve() if args.out else out_path
    if dest == out_path:
        # fitz cannot save over its own open input; go through a temp file
        fd, tmp = tempfile.mkstemp(suffix=".pdf", dir=dest.parent)
        os.close(fd)
        out.ez_save(tmp)
        out.close()
        os.replace(tmp, dest)
    else:
        out.ez_save(dest)
    print(dest)
    return 0


if __name__ == "__main__":
    sys.exit(main())

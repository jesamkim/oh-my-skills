#!/usr/bin/env python3
"""Verify a paper-trans output PDF against the source and apply report.

Checks: page count equality, zero failed insertions, Korean text coverage
on translated pages, excessive shrink warnings. Optionally renders pages
to PNG for visual QA.
"""
import argparse
import json
import pathlib
import sys

import fitz

HANGUL = range(0xAC00, 0xD7A4)


def hangul_ratio(text):
    if not text:
        return 0.0
    letters = [c for c in text if not c.isspace()]
    if not letters:
        return 0.0
    ko = sum(1 for c in letters if ord(c) in HANGUL)
    return ko / len(letters)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("source_pdf")
    ap.add_argument("output_pdf")
    ap.add_argument("report_json")
    ap.add_argument("--render", default="", help="comma-separated 0-based page numbers to PNG")
    ap.add_argument("--render-dir", default=".", help="PNG output dir")
    args = ap.parse_args()

    src = fitz.open(args.source_pdf)
    out = fitz.open(args.output_pdf)
    report = json.loads(pathlib.Path(args.report_json).read_text())

    problems, warnings = [], []
    if src.page_count != out.page_count:
        problems.append(f"page count differs: {src.page_count} vs {out.page_count}")
    if report["failed"]:
        problems.append(f"{len(report['failed'])} failed insertions: "
                        + ", ".join(f["id"] for f in report["failed"][:10]))
    if report["applied"] < report["translated_blocks"]:
        warnings.append(f"applied {report['applied']}/{report['translated_blocks']} blocks")
    if report.get("untranslated"):
        ids = ", ".join(report["untranslated"][:10])
        warnings.append(f"{len(report['untranslated'])} translate-marked blocks "
                        f"kept original (no translated_text): {ids}")
    if report["shrunk"]:
        ids = ", ".join(f"{s['id']}({s['scale']})" for s in report["shrunk"][:10])
        warnings.append(f"{len(report['shrunk'])} blocks shrunk below 0.6: {ids}")

    ratio = hangul_ratio("".join(p.get_text() for p in out))
    if ratio < 0.05:
        problems.append(f"almost no Korean text in output (hangul ratio {ratio:.3f})")
    else:
        print(f"hangul ratio in output text: {ratio:.2f}", file=sys.stderr)

    if args.render:
        rdir = pathlib.Path(args.render_dir)
        rdir.mkdir(parents=True, exist_ok=True)
        for pno in [int(x) for x in args.render.split(",") if x.strip()]:
            pix = out[pno].get_pixmap(dpi=110)
            png = rdir / f"verify_p{pno}.png"
            pix.save(png)
            print(f"rendered: {png}", file=sys.stderr)

    if problems:
        print("FAIL")
        for p in problems:
            print(f"  - {p}")
        return 1
    print("PASS" if not warnings else "PASS (with warnings)")
    for w in warnings:
        print(f"  - {w}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

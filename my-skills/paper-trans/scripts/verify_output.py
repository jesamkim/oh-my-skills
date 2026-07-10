#!/usr/bin/env python3
"""Verify a paper-trans output PDF against the source and apply report.

Checks: page count equality, zero failed insertions, Korean text coverage
on translated pages, excessive shrink warnings. Optionally renders pages
to PNG for visual QA.

Figure-integrity check (--blocks): renders every page of the source and
the output, masks the regions where change is EXPECTED (translated prose
blocks, plus images present only in the output — i.e. rasterized pages and
patch_regions.py patches), then pixel-diffs the rest. Any remaining diff
means visuals were damaged (figure labels redacted, strokes lost, tofu).
Each damaged region is reported with its PDF-point bbox, side-by-side
crops are saved for visual confirmation, and a ready-to-run
patch_regions.py command is printed.
"""
import argparse
import glob
import json
import pathlib
import sys

import fitz

HANGUL = range(0xAC00, 0xD7A4)

# Blocks with these classifier reasons live inside figures; a diff there is
# damage even if a translator (wrongly) filled translated_text for them.
FIGURE_REASONS = {"figure-text", "rotated", "tiny"}

MASK_PAD = 2.0       # points around expected-change regions
DIFF_TOL = 30        # per-pixel channel-sum threshold
MIN_CLUSTER_PX = 40  # ignore diff clusters smaller than this many pixels
ROW_GAP = 4          # rows apart at most to belong to the same cluster


def hangul_ratio(text):
    if not text:
        return 0.0
    letters = [c for c in text if not c.isspace()]
    if not letters:
        return 0.0
    ko = sum(1 for c in letters if ord(c) in HANGUL)
    return ko / len(letters)


def load_blocks(patterns):
    blocks = []
    for pat in patterns:
        for jp in sorted(glob.glob(pat)) or [pat]:
            blocks.extend(json.loads(pathlib.Path(jp).read_text())["blocks"])
    return blocks


def image_rects(page):
    rects = []
    for img in page.get_images(full=True):
        rects.extend(page.get_image_rects(img[0]))
    return rects


def foreign_image_rects(src_page, out_page):
    """Rects of images in the output that the source page does not have.

    These are deliberate overlays (rasterize fallback, patch_regions.py
    patches) — expected to differ from the vector original, so masked.
    """
    src = image_rects(src_page)
    foreign = []
    for r in image_rects(out_page):
        if not any(max(abs(r.x0 - s.x0), abs(r.y0 - s.y0),
                       abs(r.x1 - s.x1), abs(r.y1 - s.y1)) < 2 for s in src):
            foreign.append(r)
    return foreign


def white_out(pix, rects_px):
    """Paint each pixel-space rect white, in place. Masking in pixel space
    (rather than draw_rect on the live page) keeps each page rendered exactly
    once — PyMuPDF's per-page display-list cache renders differently when the
    same page is rasterized twice at different dpi, so a second render would
    desync src vs out and manufacture phantom diffs."""
    w, h, n = pix.w, pix.h, pix.n
    for r in rects_px:
        x0, y0 = max(0, int(r.x0)), max(0, int(r.y0))
        x1, y1 = min(w, int(r.x1) + 1), min(h, int(r.y1) + 1)
        white = b"\xff" * ((x1 - x0) * n) if n <= 3 else None
        for y in range(y0, y1):
            base = (y * w + x0) * n
            if white is not None:
                pix.samples_mv[base:base + (x1 - x0) * n] = white
            else:
                for x in range(x0, x1):
                    o = base + (x - x0) * n
                    pix.samples_mv[o:o + 3] = b"\xff\xff\xff"


def diff_clusters(pix_a, pix_b):
    """Pixel-diff two same-size RGB pixmaps -> list of (Rect_px, count)."""
    w, h, n = pix_a.w, pix_a.h, pix_a.n
    sa, sb = pix_a.samples, pix_b.samples
    stride = w * n
    rows = {}  # y -> (minx, maxx, count)
    for y in range(h):
        ra = sa[y * stride:(y + 1) * stride]
        rb = sb[y * stride:(y + 1) * stride]
        if ra == rb:
            continue
        minx, maxx, cnt = None, 0, 0
        for x in range(w):
            o = x * n
            if (abs(ra[o] - rb[o]) + abs(ra[o + 1] - rb[o + 1])
                    + abs(ra[o + 2] - rb[o + 2])) > DIFF_TOL:
                cnt += 1
                if minx is None:
                    minx = x
                maxx = x
        if cnt:
            rows[y] = (minx, maxx, cnt)

    clusters, current = [], None  # current: [y0, y1, minx, maxx, count]
    for y in sorted(rows):
        minx, maxx, cnt = rows[y]
        if current and y - current[1] <= ROW_GAP:
            current[1] = y
            current[2] = min(current[2], minx)
            current[3] = max(current[3], maxx)
            current[4] += cnt
        else:
            if current:
                clusters.append(current)
            current = [y, y, minx, maxx, cnt]
    if current:
        clusters.append(current)
    return [(fitz.Rect(c[2], c[0], c[3] + 1, c[1] + 1), c[4])
            for c in clusters if c[4] >= MIN_CLUSTER_PX]


def figure_check(source_pdf, output_pdf, blocks, dpi, render_dir, skip_pages):
    """Compare src/out page renders outside expected-change regions.

    Opens its own fresh document handles and renders each page exactly once
    at `dpi`, masking expected-change regions in pixel space. Returns a list
    of findings: {page, rect (PDF points), diff_px, crops}.
    """
    src = fitz.open(source_pdf)
    out = fitz.open(output_pdf)

    expected_by_page = {}
    for b in blocks:
        if b.get("translated_text") and b.get("reason") not in FIGURE_REASONS:
            expected_by_page.setdefault(b["page"], []).append(fitz.Rect(b["bbox"]))

    findings = []
    scale = 72.0 / dpi
    for pno in range(src.page_count):
        if pno in skip_pages:
            continue
        sp, op = src[pno], out[pno]
        masks = [r + (-MASK_PAD, -MASK_PAD, MASK_PAD, MASK_PAD)
                 for r in expected_by_page.get(pno, [])]
        foreign = foreign_image_rects(sp, op)
        full_page = [r for r in foreign
                     if abs(r) >= abs(op.rect) * 0.9]
        if full_page:
            print(f"  fig-check: page {pno} is a full-page image overlay "
                  "(rasterized/patched) - skipped", file=sys.stderr)
            continue
        masks += [r + (-MASK_PAD, -MASK_PAD, MASK_PAD, MASK_PAD)
                  for r in foreign]
        pa = sp.get_pixmap(dpi=dpi)
        pb = op.get_pixmap(dpi=dpi)
        if (pa.w, pa.h) != (pb.w, pb.h):
            findings.append({"page": pno, "rect": list(op.rect),
                             "diff_px": -1, "crops": []})
            continue
        masks_px = [fitz.Rect(r.x0 / scale, r.y0 / scale,
                              r.x1 / scale, r.y1 / scale) for r in masks]
        white_out(pa, masks_px)
        white_out(pb, masks_px)
        for rect_px, cnt in diff_clusters(pa, pb):
            rect_pt = fitz.Rect(rect_px.x0 * scale, rect_px.y0 * scale,
                                rect_px.x1 * scale, rect_px.y1 * scale)
            rect_pt = (rect_pt + (-3, -3, 3, 3)) & sp.rect
            crops = []
            if render_dir:
                rdir = pathlib.Path(render_dir)
                rdir.mkdir(parents=True, exist_ok=True)
                for tag, doc in (("src", src), ("out", out)):
                    png = rdir / (f"figdiff_p{pno}_"
                                  f"{int(rect_pt.x0)}_{int(rect_pt.y0)}_{tag}.png")
                    doc[pno].get_pixmap(dpi=200, clip=rect_pt).save(png)
                    crops.append(str(png))
            findings.append({"page": pno,
                             "rect": [round(v, 1) for v in rect_pt],
                             "diff_px": cnt, "crops": crops})
    return findings


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("source_pdf")
    ap.add_argument("output_pdf")
    ap.add_argument("report_json")
    ap.add_argument("--render", default="", help="comma-separated 0-based page numbers to PNG")
    ap.add_argument("--render-dir", default=".", help="PNG output dir")
    ap.add_argument("--blocks", nargs="*", default=None,
                    help="block JSON file(s)/glob(s) used for the overlay; "
                         "enables the figure-integrity pixel diff")
    ap.add_argument("--fig-dpi", type=int, default=100,
                    help="render dpi for the figure diff (default 100)")
    ap.add_argument("--fig-skip-pages", default="",
                    help="comma-separated 0-based pages to exclude from the "
                         "figure diff (confirmed-legitimate diffs)")
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

    if args.blocks is not None and src.page_count == out.page_count:
        skip = {int(x) for x in args.fig_skip_pages.split(",") if x.strip()}
        blocks = load_blocks(args.blocks)
        # figure_check opens its own document handles so its renders are not
        # perturbed by the --render pass above (see white_out docstring).
        findings = figure_check(args.source_pdf, args.output_pdf, blocks,
                                args.fig_dpi, args.render_dir, skip)
        if findings:
            script_dir = pathlib.Path(__file__).parent
            for f in findings:
                r = f["rect"]
                problems.append(
                    f"figure diff on page {f['page']}: rect "
                    f"({r[0]},{r[1]},{r[2]},{r[3]}) {f['diff_px']}px changed")
                print(f"  inspect crops: {' | '.join(f['crops'])}",
                      file=sys.stderr)
                print(f"  if damaged, patch with:\n"
                      f"    python {script_dir}/patch_regions.py "
                      f"\"{args.source_pdf}\" \"{args.output_pdf}\" "
                      f"--region {f['page']}:{r[0]},{r[1]},{r[2]},{r[3]}",
                      file=sys.stderr)
        else:
            print("figure-integrity diff: clean", file=sys.stderr)

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

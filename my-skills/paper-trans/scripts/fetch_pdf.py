#!/usr/bin/env python3
"""Resolve a paper input (URL or local path) to a local PDF file.

- Local path: validate it exists and is a PDF.
- URL: download it. arxiv.org/abs/... URLs are rewritten to /pdf/.
Prints the absolute path of the local PDF as the last stdout line.
"""
import argparse
import pathlib
import re
import sys
import urllib.request

ARXIV_ABS = re.compile(r"^(https?://(?:www\.)?arxiv\.org)/abs/(.+)$", re.I)
USER_AGENT = "Mozilla/5.0 (paper-trans skill; PDF fetch)"


def resolve_url(url: str) -> str:
    m = ARXIV_ABS.match(url.strip())
    if m:
        return f"{m.group(1)}/pdf/{m.group(2)}"
    return url.strip()


def filename_from_url(url: str) -> str:
    name = url.rstrip("/").split("/")[-1].split("?")[0] or "paper"
    if not name.lower().endswith(".pdf"):
        name += ".pdf"
    return name


def is_pdf(path: pathlib.Path) -> bool:
    try:
        with open(path, "rb") as f:
            return f.read(5) == b"%PDF-"
    except OSError:
        return False


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("source", help="PDF URL or local file path")
    ap.add_argument("--out-dir", default=".", help="download directory (default: cwd)")
    args = ap.parse_args()

    src = args.source.strip()
    if not re.match(r"^https?://", src, re.I):
        path = pathlib.Path(src).expanduser().resolve()
        if not path.is_file():
            print(f"ERROR: file not found: {path}", file=sys.stderr)
            return 1
        if not is_pdf(path):
            print(f"ERROR: not a PDF file: {path}", file=sys.stderr)
            return 1
        print(path)
        return 0

    url = resolve_url(src)
    out_dir = pathlib.Path(args.out_dir).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    dest = out_dir / filename_from_url(url)

    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=60) as resp, open(dest, "wb") as f:
            f.write(resp.read())
    except Exception as exc:
        print(f"ERROR: download failed: {exc}", file=sys.stderr)
        return 1

    if not is_pdf(dest):
        dest.unlink(missing_ok=True)
        print("ERROR: downloaded content is not a PDF (check the URL)", file=sys.stderr)
        return 1

    print(f"Downloaded: {url}", file=sys.stderr)
    print(dest)
    return 0


if __name__ == "__main__":
    sys.exit(main())

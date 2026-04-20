"""Convert SVG icon files to PNG bytes for embedding in PPTX as Picture shapes."""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Optional

# Cache: (svg_path_str, size) -> PNG bytes
_cache: dict[tuple[str, int], bytes] = {}


def rasterize_icon(svg_path: Path, size: int = 96) -> bytes:
    """Return PNG bytes for the given SVG icon at the requested pixel size.

    Tries cairosvg first, then rsvg-convert, then falls back to a
    Pillow-generated placeholder rectangle.
    """
    key = (str(svg_path), size)
    if key in _cache:
        return _cache[key]

    png_bytes = (
        _try_cairosvg(svg_path, size)
        or _try_rsvg(svg_path, size)
        or _make_placeholder(svg_path.stem, size)
    )

    _cache[key] = png_bytes
    return png_bytes


def find_icon_path(service: str, icons_dir: Path) -> Optional[Path]:
    """Resolve a service name to its SVG path inside *icons_dir*.

    Matching strategy (first hit wins):
      1. Exact filename match  (e.g. "lambda" -> lambda.svg)
      2. Case-insensitive match
      3. Substring match on stem (e.g. "ec2" matches "ec2.svg")
    """
    # Normalise the lookup key
    needle = service.lower().strip()

    # 1. Exact match
    exact = icons_dir / f"{needle}.svg"
    if exact.is_file():
        return exact

    # 2. Case-insensitive / substring scan
    for svg in sorted(icons_dir.glob("*.svg")):
        stem = svg.stem.lower()
        if stem == needle:
            return svg

    for svg in sorted(icons_dir.glob("*.svg")):
        stem = svg.stem.lower()
        if needle in stem or stem in needle:
            return svg

    return None


# --- private helpers ------------------------------------------------------- #

def _try_cairosvg(svg_path: Path, size: int) -> Optional[bytes]:
    try:
        import cairosvg

        return cairosvg.svg2png(
            url=str(svg_path),
            output_width=size,
            output_height=size,
        )
    except Exception:
        return None


def _try_rsvg(svg_path: Path, size: int) -> Optional[bytes]:
    try:
        result = subprocess.run(
            [
                "rsvg-convert",
                "--width", str(size),
                "--height", str(size),
                "--format", "png",
                str(svg_path),
            ],
            capture_output=True,
            check=True,
        )
        return result.stdout
    except Exception:
        return None


def _make_placeholder(label: str, size: int) -> bytes:
    """Create a simple coloured rectangle with the service name."""
    from PIL import Image, ImageDraw, ImageFont
    import io

    img = Image.new("RGBA", (size, size), (35, 47, 62, 255))
    draw = ImageDraw.Draw(img)

    # Try to pick a readable font size
    font_size = max(10, size // 6)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
    except Exception:
        font = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), label, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text(
        ((size - tw) / 2, (size - th) / 2),
        label,
        fill=(255, 153, 0, 255),
        font=font,
    )

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


# --- self-test ------------------------------------------------------------- #

if __name__ == "__main__":
    icons_dir = Path(__file__).resolve().parent.parent / "icons"

    for svc in ("lambda", "s3", "ec2", "nonexistent-service"):
        icon = find_icon_path(svc, icons_dir)
        if icon is None:
            print(f"[{svc}] icon not found -> generating placeholder")
            png = _make_placeholder(svc, 96)
        else:
            print(f"[{svc}] found: {icon.name}")
            png = rasterize_icon(icon, size=96)

        assert isinstance(png, bytes) and len(png) > 0
        print(f"  PNG size: {len(png)} bytes")

        # Verify it is valid PNG (starts with PNG signature)
        assert png[:4] == b"\x89PNG", f"Invalid PNG for {svc}"

    # Verify cache works
    icon = find_icon_path("lambda", icons_dir)
    _ = rasterize_icon(icon, size=96)
    assert (str(icon), 96) in _cache
    print("\nCache verification passed.")
    print("All tests passed.")

#!/usr/bin/env python3
"""
AWS Architecture Diagram Generator - CLI Entry Point.

Reads a JSON diagram definition and produces:
- SVG (self-contained, with inline icons)
- PNG (via rsvg-convert)
- PPTX (via pptx_export module)

Usage:
    python3 generate_diagram.py --input diagram.json --output architecture.svg
    python3 generate_diagram.py --input diagram.json --output architecture.svg --png
    python3 generate_diagram.py --input diagram.json --output architecture.svg --pptx arch.pptx
"""

import argparse
import subprocess
import sys
from pathlib import Path

# Add scripts directory to path for imports
SCRIPTS_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPTS_DIR))

from diagram_schema import from_file, DiagramDefinition
from layout_engine import compute_layout
from orthogonal_router import route_connections
from svg_renderer import SvgRenderer


def find_icons_dir() -> Path:
    """Locate the icons/ directory relative to this script."""
    candidates = [
        SCRIPTS_DIR.parent / "icons",
        SCRIPTS_DIR / "icons",
        Path.cwd() / "icons",
    ]
    for candidate in candidates:
        if candidate.is_dir():
            return candidate
    print("Warning: icons/ directory not found, SVG symbols will be empty")
    return SCRIPTS_DIR.parent / "icons"


def generate_svg(diagram: DiagramDefinition, icons_dir: Path) -> tuple[str, "LayoutResult", list]:
    """Generate SVG string from a diagram definition.

    Returns (svg_string, layout, routes) so layout/routes can be reused for PPTX.
    """
    layout = compute_layout(diagram)
    routes = route_connections(layout, diagram.connections)
    renderer = SvgRenderer(layout, routes, diagram, str(icons_dir))
    return renderer.render(), layout, routes


def svg_to_png(svg_path: str, png_path: str, width: int = 2048) -> bool:
    """Convert SVG to PNG using rsvg-convert."""
    try:
        subprocess.run(
            ["rsvg-convert", "-w", str(width), svg_path, "-o", png_path],
            check=True, capture_output=True, text=True,
        )
        print(f"PNG saved: {png_path}")
        return True
    except FileNotFoundError:
        print("Error: rsvg-convert not found. Install librsvg2-bin.")
        return False
    except subprocess.CalledProcessError as e:
        print(f"Error converting SVG to PNG: {e.stderr}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Generate AWS architecture diagram from JSON definition"
    )
    parser.add_argument(
        "--input", "-i", required=True,
        help="Path to JSON diagram definition file"
    )
    parser.add_argument(
        "--output", "-o", required=True,
        help="Output SVG file path"
    )
    parser.add_argument(
        "--png", action="store_true",
        help="Also generate PNG (requires rsvg-convert)"
    )
    parser.add_argument(
        "--png-width", type=int, default=2048,
        help="PNG output width in pixels (default: 2048)"
    )
    parser.add_argument(
        "--pptx", type=str, default=None,
        help="Also generate PPTX file at this path"
    )
    parser.add_argument(
        "--icons-dir", type=str, default=None,
        help="Path to icons/ directory (auto-detected if not specified)"
    )
    parser.add_argument(
        "--validate", action="store_true",
        help="Validate JSON before generating"
    )

    args = parser.parse_args()

    # Load diagram
    print(f"Loading: {args.input}")
    diagram = from_file(args.input)

    # Resolve icons directory
    icons_dir = Path(args.icons_dir) if args.icons_dir else find_icons_dir()

    # Validation
    if args.validate:
        errors = _validate(diagram, icons_dir)
        if errors:
            print("Validation errors:")
            for err in errors:
                print(f"  - {err}")
            sys.exit(1)
        print("Validation passed")

    # Generate SVG (also returns layout/routes for PPTX reuse)
    svg_content, layout, routes = generate_svg(diagram, icons_dir)

    # Write SVG
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(svg_content, encoding="utf-8")
    print(f"SVG saved: {output_path} ({len(svg_content)} bytes)")

    # Optional PNG
    if args.png:
        png_path = str(output_path.with_suffix(".png"))
        svg_to_png(str(output_path), png_path, args.png_width)

    # Optional PPTX (native shapes - no PNG intermediary needed)
    if args.pptx:
        try:
            from pptx_export import export_pptx_native
            export_pptx_native(
                diagram, layout, routes, str(icons_dir), args.pptx
            )
            print(f"PPTX saved: {args.pptx}")
        except Exception as e:
            print(f"Warning: PPTX generation failed: {e}")


def _validate(diagram: DiagramDefinition, icons_dir: "Path | None" = None) -> list[str]:
    """Basic validation of diagram definition."""
    errors = []
    node_ids = {n.id for n in diagram.nodes}
    container_ids = {c.id for c in diagram.containers}

    # Check icon file existence
    if icons_dir and icons_dir.is_dir():
        available_icons = {p.stem for p in icons_dir.glob("*.svg")}
        for node in diagram.nodes:
            if node.service not in available_icons:
                errors.append(f"Icon '{node.service}.svg' not found in {icons_dir}")

    # Check connection references
    for conn in diagram.connections:
        if conn.source not in node_ids:
            errors.append(f"Connection source '{conn.source}' not found in nodes")
        if conn.target not in node_ids:
            errors.append(f"Connection target '{conn.target}' not found in nodes")

    # Check container references
    for c in diagram.containers:
        if c.parent and c.parent not in container_ids:
            errors.append(f"Container '{c.id}' parent '{c.parent}' not found")
        for child in c.children:
            if child not in node_ids and child not in container_ids:
                errors.append(f"Container '{c.id}' child '{child}' not found")

    # Check for duplicate IDs
    all_ids = [n.id for n in diagram.nodes] + [c.id for c in diagram.containers]
    seen = set()
    for id_ in all_ids:
        if id_ in seen:
            errors.append(f"Duplicate ID: '{id_}'")
        seen.add(id_)

    return errors


if __name__ == "__main__":
    main()

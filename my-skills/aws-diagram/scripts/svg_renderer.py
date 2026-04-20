"""
SVG renderer for AWS architecture diagrams.

Assembles a complete, self-contained SVG from:
- Layout positions (from layout_engine)
- Routed arrows (from orthogonal_router)
- Icon SVG files (from icons/ directory)
- Container/group styling (from AWS Architecture Icon Deck)
"""

from __future__ import annotations

import os
import re
from pathlib import Path
from xml.sax.saxutils import escape

from layout_engine import LayoutResult, ContainerLayout, BoundingBox, ICON_SIZE
from orthogonal_router import RoutedPath, CALLOUT_RADIUS


# ============================================================
# AWS Architecture Icon Deck - Official Colors
# ============================================================

THEME_COLORS = {
    "light": {
        "background": "#FFFFFF",
        "text": "#232F3E",
        "arrow": "#545B64",
        "label": "#666666",
        "title": "#232F3E",
    },
    "dark": {
        "background": "#232F3E",
        "text": "#FFFFFF",
        "arrow": "#D5DBDB",
        "label": "#AEB6BF",
        "title": "#FFFFFF",
    },
}

# Container styling per theme (AWS Architecture Icon Deck guidelines)
CONTAINER_STYLES = {
    "light": {
        "aws-cloud": {
            "fill": "none", "stroke": "#232F3E", "stroke-width": "2",
            "stroke-dasharray": None, "rx": "8",
            "header_bg": "#232F3E", "header_text": "#FFFFFF",
        },
        "region": {
            "fill": "none", "stroke": "#00A4A6", "stroke-width": "1.5",
            "stroke-dasharray": "6,3", "rx": "0",
            "header_bg": "#00A4A6", "header_text": "#FFFFFF",
        },
        "vpc": {
            "fill": "none", "stroke": "#8C4FFF", "stroke-width": "1.5",
            "stroke-dasharray": None, "rx": "0",
            "header_bg": "#8C4FFF", "header_text": "#FFFFFF",
        },
        "az": {
            "fill": "none", "stroke": "#147EBA", "stroke-width": "1",
            "stroke-dasharray": "4,2", "rx": "0",
            "header_bg": None, "header_text": "#147EBA",
        },
        "public-subnet": {
            "fill": "#E8F5E9", "fill-opacity": "0.5",
            "stroke": "#7AA116", "stroke-width": "1",
            "stroke-dasharray": None, "rx": "0",
            "header_bg": "#7AA116", "header_text": "#FFFFFF",
        },
        "private-subnet": {
            "fill": "#E3F2FD", "fill-opacity": "0.5",
            "stroke": "#147EBA", "stroke-width": "1",
            "stroke-dasharray": None, "rx": "0",
            "header_bg": "#147EBA", "header_text": "#FFFFFF",
        },
        "security-group": {
            "fill": "none", "stroke": "#DD344C", "stroke-width": "1",
            "stroke-dasharray": "4,2", "rx": "0",
            "header_bg": None, "header_text": "#DD344C",
        },
        "auto-scaling-group": {
            "fill": "none", "stroke": "#ED7100", "stroke-width": "1",
            "stroke-dasharray": "4,2", "rx": "0",
            "header_bg": None, "header_text": "#ED7100",
        },
        "generic": {
            "fill": "none", "stroke": "#AEB6BF", "stroke-width": "1",
            "stroke-dasharray": None, "rx": "4",
            "header_bg": None, "header_text": "#545B64",
        },
    },
    "dark": {
        "aws-cloud": {
            "fill": "none", "stroke": "#D5DBDB", "stroke-width": "2",
            "stroke-dasharray": None, "rx": "8",
            "header_bg": "#D5DBDB", "header_text": "#232F3E",
        },
        "region": {
            "fill": "none", "stroke": "#00D4D7", "stroke-width": "1.5",
            "stroke-dasharray": "6,3", "rx": "0",
            "header_bg": "#00A4A6", "header_text": "#FFFFFF",
        },
        "vpc": {
            "fill": "none", "stroke": "#A97BFF", "stroke-width": "1.5",
            "stroke-dasharray": None, "rx": "0",
            "header_bg": "#8C4FFF", "header_text": "#FFFFFF",
        },
        "az": {
            "fill": "none", "stroke": "#5B9BD5", "stroke-width": "1",
            "stroke-dasharray": "4,2", "rx": "0",
            "header_bg": None, "header_text": "#5B9BD5",
        },
        "public-subnet": {
            "fill": "#1B3A1B", "fill-opacity": "0.5",
            "stroke": "#7AA116", "stroke-width": "1",
            "stroke-dasharray": None, "rx": "0",
            "header_bg": "#7AA116", "header_text": "#FFFFFF",
        },
        "private-subnet": {
            "fill": "#1A2A3A", "fill-opacity": "0.5",
            "stroke": "#5B9BD5", "stroke-width": "1",
            "stroke-dasharray": None, "rx": "0",
            "header_bg": "#147EBA", "header_text": "#FFFFFF",
        },
        "security-group": {
            "fill": "none", "stroke": "#FF6B6B", "stroke-width": "1",
            "stroke-dasharray": "4,2", "rx": "0",
            "header_bg": None, "header_text": "#FF6B6B",
        },
        "auto-scaling-group": {
            "fill": "none", "stroke": "#FF9E40", "stroke-width": "1",
            "stroke-dasharray": "4,2", "rx": "0",
            "header_bg": None, "header_text": "#FF9E40",
        },
        "generic": {
            "fill": "none", "stroke": "#545B64", "stroke-width": "1",
            "stroke-dasharray": None, "rx": "4",
            "header_bg": None, "header_text": "#AEB6BF",
        },
    },
}

FONT_STACK = "Amazon Ember, Helvetica Neue, Arial, sans-serif"


# ============================================================
# SVG Assembly
# ============================================================

class SvgRenderer:
    """Renders a complete SVG diagram."""

    def __init__(
        self,
        layout: LayoutResult,
        routes: list[RoutedPath],
        diagram_def,
        icons_dir: str,
    ):
        self.layout = layout
        self.routes = routes
        self.diagram = diagram_def
        self.icons_dir = Path(icons_dir)
        self.theme_name = diagram_def.theme if diagram_def.theme in THEME_COLORS else "light"
        self.theme = THEME_COLORS[self.theme_name]
        self.container_styles = CONTAINER_STYLES[self.theme_name]
        self._used_icons: set[str] = set()

    def render(self) -> str:
        """Produce the complete SVG string.

        Layer order (back to front):
        1. Background rect + title text
        2. Container boxes (AWS Cloud, VPC, Subnet, etc.)
        3. All arrows (paths) + connection labels
        4. Callout number circles
        5. All service icons (use) + icon labels  <-- topmost layer
        """
        parts = []
        parts.append(self._svg_open())
        parts.append(self._defs())
        parts.append(self._background())
        parts.append(self._title_block())
        parts.append(self._containers())
        parts.append(self._arrows())
        parts.append(self._icons())
        parts.append("</svg>")
        return "\n".join(parts)

    # ----------------------------------------------------------
    # SVG skeleton
    # ----------------------------------------------------------

    def _svg_open(self) -> str:
        w = self.layout.viewbox_width
        h = self.layout.viewbox_height
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" '
            f'viewBox="0 0 {w} {h}" '
            f'width="{w}" height="{h}">'
        )

    def _background(self) -> str:
        return (
            f'<rect width="100%" height="100%" '
            f'fill="{self.theme["background"]}"/>'
        )

    # ----------------------------------------------------------
    # Defs: markers, icon symbols
    # ----------------------------------------------------------

    def _defs(self) -> str:
        parts = ["<defs>"]

        # Arrowhead markers (Open Arrow style per Icon Deck)
        # Default color marker
        arrow_color = self.theme["arrow"]
        parts.append(self._marker_pair("arrowhead", arrow_color))

        # Per-color markers for custom-colored arrows
        self._arrow_colors: set[str] = set()
        for conn in self.diagram.connections:
            if conn.color:
                self._arrow_colors.add(conn.color)
        for color in sorted(self._arrow_colors):
            marker_id = self._color_marker_id(color)
            parts.append(self._marker_pair(marker_id, color))

        # Collect needed icons
        self._used_icons = set()
        for node in self.diagram.nodes:
            self._used_icons.add(node.service)

        # Load icon SVGs as symbols
        for service in sorted(self._used_icons):
            result = self._load_icon(service)
            if result:
                svg_content, viewbox = result
                parts.append(
                    f'<symbol id="icon-{service}" viewBox="{viewbox}">'
                )
                parts.append(svg_content)
                parts.append("</symbol>")

        parts.append("</defs>")
        return "\n".join(parts)

    @staticmethod
    def _color_marker_id(color: str) -> str:
        """Generate a marker ID from a hex color, e.g. '#8C4FFF' -> 'arrowhead-8C4FFF'."""
        return f"arrowhead-{color.lstrip('#')}"

    @staticmethod
    def _marker_pair(base_id: str, color: str) -> str:
        """Generate forward + reverse arrowhead markers for a given color."""
        fwd = (
            f'<marker id="{base_id}" markerWidth="12" markerHeight="8" '
            f'refX="11" refY="4" orient="auto" fill="none" '
            f'stroke="{color}" stroke-width="1.5">'
            f'<polyline points="1 1, 11 4, 1 7"/>'
            f'</marker>'
        )
        rev = (
            f'<marker id="{base_id}-reverse" markerWidth="12" markerHeight="8" '
            f'refX="1" refY="4" orient="auto" fill="none" '
            f'stroke="{color}" stroke-width="1.5">'
            f'<polyline points="11 1, 1 4, 11 7"/>'
            f'</marker>'
        )
        return fwd + "\n" + rev

    def _load_icon(self, service: str) -> tuple[str, str] | None:
        """Load an icon SVG and extract inner content + viewBox.

        Returns (inner_svg, viewbox_str) or None.
        """
        icon_path = self.icons_dir / f"{service}.svg"
        if not icon_path.exists():
            return None

        content = icon_path.read_text(encoding="utf-8")

        # Detect viewBox from the SVG element
        vb_match = re.search(r'viewBox="([^"]*)"', content)
        viewbox = vb_match.group(1) if vb_match else "0 0 64 64"

        # Extract content between <svg> and </svg>
        match = re.search(r"<svg[^>]*>(.*)</svg>", content, re.DOTALL)
        if match:
            inner = match.group(1)
            # Remove any nested xmlns declarations
            inner = re.sub(r'\s*xmlns="[^"]*"', "", inner)
            return inner, viewbox

        return None

    # ----------------------------------------------------------
    # Title block
    # ----------------------------------------------------------

    def _title_block(self) -> str:
        if not self.diagram.title:
            return ""

        parts = []
        parts.append(
            f'<text x="40" y="28" '
            f'font-family="{FONT_STACK}" font-size="16" '
            f'font-weight="bold" fill="{self.theme["title"]}">'
            f'{escape(self.diagram.title)}</text>'
        )
        if self.diagram.subtitle:
            parts.append(
                f'<text x="40" y="46" '
                f'font-family="{FONT_STACK}" font-size="11" '
                f'fill="{self.theme["label"]}">'
                f'{escape(self.diagram.subtitle)}</text>'
            )
        return "\n".join(parts)

    # ----------------------------------------------------------
    # Containers
    # ----------------------------------------------------------

    def _containers(self) -> str:
        parts = []
        for cl in self.layout.containers:
            style = self.container_styles.get(
                cl.container_type, self.container_styles["generic"]
            )
            parts.append(self._render_container(cl, style))
        return "\n".join(parts)

    def _render_container(self, cl: ContainerLayout, style: dict) -> str:
        b = cl.bbox
        parts = []

        # Container rectangle
        attrs = [
            f'x="{b.x:.1f}" y="{b.y:.1f}"',
            f'width="{b.w:.1f}" height="{b.h:.1f}"',
            f'fill="{style.get("fill", "none")}"',
            f'stroke="{style["stroke"]}"',
            f'stroke-width="{style["stroke-width"]}"',
        ]
        if style.get("rx"):
            attrs.append(f'rx="{style["rx"]}"')
        if style.get("stroke-dasharray"):
            attrs.append(f'stroke-dasharray="{style["stroke-dasharray"]}"')
        if style.get("fill-opacity"):
            attrs.append(f'fill-opacity="{style["fill-opacity"]}"')

        parts.append(f'<rect {" ".join(attrs)}/>')

        # Header background (if applicable)
        if style.get("header_bg"):
            header_w = min(len(cl.label) * 8 + 40, b.w)
            parts.append(
                f'<rect x="{b.x:.1f}" y="{b.y:.1f}" '
                f'width="{header_w:.1f}" height="22" '
                f'fill="{style["header_bg"]}" '
                f'rx="{style.get("rx", "0")}"/>'
            )
            parts.append(
                f'<text x="{b.x + 28:.1f}" y="{b.y + 15:.1f}" '
                f'font-family="{FONT_STACK}" font-size="11" '
                f'font-weight="bold" fill="{style["header_text"]}">'
                f'{escape(cl.label)}</text>'
            )
        else:
            # Simple label (no background)
            parts.append(
                f'<text x="{b.x + 8:.1f}" y="{b.y + 14:.1f}" '
                f'font-family="{FONT_STACK}" font-size="9" '
                f'fill="{style["header_text"]}">'
                f'{escape(cl.label)}</text>'
            )

        return "\n".join(parts)

    # ----------------------------------------------------------
    # Icons
    # ----------------------------------------------------------

    def _icons(self) -> str:
        parts = []
        for node in self.diagram.nodes:
            nl = self.layout.nodes.get(node.id)
            if not nl:
                continue

            # Icon
            parts.append(
                f'<use href="#icon-{node.service}" '
                f'x="{nl.icon_x:.1f}" y="{nl.icon_y:.1f}" '
                f'width="{ICON_SIZE}" height="{ICON_SIZE}"/>'
            )

            # Primary label - handle multi-line (\n) with <tspan>
            label_lines = node.label.split("\n") if node.label else []
            if len(label_lines) <= 1:
                parts.append(
                    f'<text x="{nl.label_x:.1f}" y="{nl.label_y:.1f}" '
                    f'text-anchor="middle" '
                    f'font-family="{FONT_STACK}" font-size="11" '
                    f'fill="{self.theme["text"]}">'
                    f'{escape(node.label or "")}</text>'
                )
                sublabel_y = nl.label_y + 14
            else:
                text_parts = [
                    f'<text x="{nl.label_x:.1f}" y="{nl.label_y:.1f}" '
                    f'text-anchor="middle" '
                    f'font-family="{FONT_STACK}" font-size="11" '
                    f'fill="{self.theme["text"]}">'
                ]
                for i, line in enumerate(label_lines):
                    if i == 0:
                        text_parts.append(
                            f'<tspan x="{nl.label_x:.1f}">{escape(line)}</tspan>'
                        )
                    else:
                        text_parts.append(
                            f'<tspan x="{nl.label_x:.1f}" dy="13">{escape(line)}</tspan>'
                        )
                text_parts.append("</text>")
                parts.append("".join(text_parts))
                sublabel_y = nl.label_y + 13 * len(label_lines)

            # Sublabel
            if node.sublabel:
                parts.append(
                    f'<text x="{nl.label_x:.1f}" y="{sublabel_y:.1f}" '
                    f'text-anchor="middle" '
                    f'font-family="{FONT_STACK}" font-size="10" '
                    f'font-style="italic" '
                    f'fill="{self.theme["label"]}">'
                    f'{escape(node.sublabel)}</text>'
                )

        return "\n".join(parts)

    # ----------------------------------------------------------
    # Arrows
    # ----------------------------------------------------------

    def _arrows(self) -> str:
        """Render arrows in two passes: paths+labels first, callouts on top.

        Callouts render above arrows but below icons (layer order enforced
        by the render() method calling _arrows() before _icons()).
        """
        arrow_parts = []
        callout_parts = []
        default_arrow_color = self.theme["arrow"]

        if self.theme_name == "dark":
            callout_fill = "#FFFFFF"
            callout_text = "#232F3E"
        else:
            callout_fill = "#232F3E"
            callout_text = "#FFFFFF"

        for route in self.routes:
            d = route.to_svg_d()
            if not d:
                continue

            # Determine arrow color (custom or default)
            stroke_color = route.color or default_arrow_color

            # Select matching marker ID
            if route.color:
                marker_id = self._color_marker_id(route.color)
            else:
                marker_id = "arrowhead"

            # Path attributes
            attrs = [
                f'd="{d}"',
                'fill="none"',
                f'stroke="{stroke_color}"',
                'stroke-width="2"',
            ]

            if route.style == "dashed":
                attrs.append('stroke-dasharray="6,3"')
            elif route.style == "bidirectional":
                attrs.append('stroke-dasharray="4,3"')
                attrs.append(f'marker-start="url(#{marker_id}-reverse)"')

            attrs.append(f'marker-end="url(#{marker_id})"')

            arrow_parts.append(f'<path {" ".join(attrs)}/>')

            # Connection label
            if route.label and route.label_pos:
                lx, ly = route.label_pos
                arrow_parts.append(
                    f'<text x="{lx:.1f}" y="{ly:.1f}" '
                    f'text-anchor="middle" '
                    f'font-family="{FONT_STACK}" font-size="10" '
                    f'font-style="italic" '
                    f'fill="{self.theme["text"]}">'
                    f'{escape(route.label)}</text>'
                )

            # Step number callout (deferred to render on top of ALL arrows)
            if route.step_number is not None and route.step_pos:
                sx, sy = route.step_pos
                r = CALLOUT_RADIUS
                callout_parts.append(
                    f'<circle cx="{sx:.1f}" cy="{sy:.1f}" r="{r}" '
                    f'fill="{callout_fill}"/>'
                )
                callout_parts.append(
                    f'<text x="{sx:.1f}" y="{sy + 4:.1f}" '
                    f'text-anchor="middle" '
                    f'font-family="{FONT_STACK}" font-size="12" '
                    f'font-weight="bold" fill="{callout_text}">'
                    f'{route.step_number}</text>'
                )

        return "\n".join(arrow_parts + callout_parts)

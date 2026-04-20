"""
Native PPTX connector/arrow shape injection via low-level OOXML manipulation.

python-pptx does NOT support connector shapes (cxnSp) or freeform custom
geometry natively. This module injects raw OOXML elements into the slide's
shape tree using lxml.

Arrow styling follows the official AWS Architecture Icon Deck PPTX spec:
  - Connector preset: straightConnector1 (2-point), bentConnector3 (bent)
  - tailEnd: type="arrow" w="med" len="sm"
  - headEnd: type="none" (or "arrow" for bidirectional)
  - Light theme color: #545B64, dark theme: #D5DBDB
  - Line width: 12700 EMU (1.0pt)
  - Dashed: <a:prstDash val="dash"/>
"""

from __future__ import annotations

from typing import Any

from lxml import etree


# ============================================================
# OOXML Namespaces
# ============================================================

NSMAP = {
    "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
}

_P = NSMAP["p"]
_A = NSMAP["a"]
_R = NSMAP["r"]


def _qn(ns_prefix: str, local: str) -> str:
    """Return a Clark-notation qualified name, e.g. '{http://...}tag'."""
    return f"{{{NSMAP[ns_prefix]}}}{local}"


# ============================================================
# Default Style
# ============================================================

DEFAULT_STYLE: dict[str, Any] = {
    "color": "545B64",
    "width_emu": 12700,
    "dash": False,
    "bidirectional": False,
}


def _merged_style(style_config: dict[str, Any] | None) -> dict[str, Any]:
    """Merge caller-supplied style with defaults."""
    merged = {**DEFAULT_STYLE}
    if style_config:
        merged.update(style_config)
    return merged


# ============================================================
# Helpers
# ============================================================

def _next_shape_id(slide: Any) -> int:
    """Find the maximum shape id on the slide and return max + 1.

    Scans all elements with an 'id' attribute under the shape tree.
    Falls back to 2 if the slide is empty (id=1 is reserved for spTree).
    """
    sp_tree = slide.shapes._spTree
    max_id = 1
    for elem in sp_tree.iter():
        id_val = elem.get("id")
        if id_val is not None:
            try:
                max_id = max(max_id, int(id_val))
            except (ValueError, TypeError):
                continue
    return max_id + 1


def _make_line_properties(style: dict[str, Any]) -> etree._Element:
    """Build an <a:ln> element with the specified style.

    Includes solid fill, optional dash preset, and arrow tail/head ends.
    """
    ln = etree.SubElement(
        etree.Element("dummy"), _qn("a", "ln"), w=str(style["width_emu"])
    )
    # Detach from dummy parent
    ln.getparent().remove(ln)

    # Solid fill
    solid_fill = etree.SubElement(ln, _qn("a", "solidFill"))
    etree.SubElement(
        solid_fill,
        _qn("a", "srgbClr"),
        val=style["color"],
    )

    # Dash
    if style["dash"]:
        etree.SubElement(ln, _qn("a", "prstDash"), val="dash")

    # Head end
    head_type = "arrow" if style["bidirectional"] else "none"
    etree.SubElement(
        ln,
        _qn("a", "headEnd"),
        type=head_type,
        w="med",
        len="sm",
    )

    # Tail end (always arrow)
    etree.SubElement(
        ln,
        _qn("a", "tailEnd"),
        type="arrow",
        w="med",
        len="sm",
    )

    return ln


def _make_non_visual_cxn_props(
    shape_id: int, name: str
) -> tuple[etree._Element, etree._Element]:
    """Build <p:nvCxnSpPr> for a connector shape.

    Returns (nvCxnSpPr_element, cNvPr_element) so caller can add
    additional attributes if needed.
    """
    nv = etree.Element(_qn("p", "nvCxnSpPr"))

    c_nv_pr = etree.SubElement(
        nv, _qn("p", "cNvPr"), id=str(shape_id), name=name
    )
    c_nv_cxn_sp_pr = etree.SubElement(nv, _qn("p", "cNvCxnSpPr"))
    nv_pr = etree.SubElement(nv, _qn("p", "nvPr"))

    return nv, c_nv_pr


def _make_non_visual_sp_props(
    shape_id: int, name: str
) -> etree._Element:
    """Build <p:nvSpPr> for a freeform shape."""
    nv = etree.Element(_qn("p", "nvSpPr"))

    etree.SubElement(
        nv, _qn("p", "cNvPr"), id=str(shape_id), name=name
    )
    etree.SubElement(nv, _qn("p", "cNvSpPr"))
    etree.SubElement(nv, _qn("p", "nvPr"))

    return nv


# ============================================================
# Public API: Straight Connector
# ============================================================

def add_straight_connector(
    slide: Any,
    x1_emu: int,
    y1_emu: int,
    x2_emu: int,
    y2_emu: int,
    style_config: dict[str, Any] | None = None,
) -> etree._Element:
    """Inject a native PPTX straight connector (cxnSp) into the slide.

    Args:
        slide: A python-pptx Slide object.
        x1_emu: Start X in EMU.
        y1_emu: Start Y in EMU.
        x2_emu: End X in EMU.
        y2_emu: End Y in EMU.
        style_config: Optional style overrides (color, width_emu, dash,
            bidirectional).

    Returns:
        The injected lxml element.
    """
    style = _merged_style(style_config)
    shape_id = _next_shape_id(slide)

    # Bounding box: position is top-left corner, extents are positive
    left = min(x1_emu, x2_emu)
    top = min(y1_emu, y2_emu)
    cx = abs(x2_emu - x1_emu)
    cy = abs(y2_emu - y1_emu)

    # Build <p:cxnSp>
    cxn_sp = etree.Element(_qn("p", "cxnSp"))

    # Non-visual properties
    nv, _ = _make_non_visual_cxn_props(shape_id, f"Connector {shape_id}")
    cxn_sp.append(nv)

    # Shape properties
    sp_pr = etree.SubElement(cxn_sp, _qn("p", "spPr"))

    # Transform
    xfrm = etree.SubElement(sp_pr, _qn("a", "xfrm"))

    # Handle flip: if the line goes right-to-left or bottom-to-top,
    # OOXML uses flipH / flipV on the xfrm.
    if x2_emu < x1_emu:
        xfrm.set("flipH", "1")
    if y2_emu < y1_emu:
        xfrm.set("flipV", "1")

    etree.SubElement(
        xfrm, _qn("a", "off"), x=str(left), y=str(top)
    )
    etree.SubElement(
        xfrm, _qn("a", "ext"), cx=str(cx), cy=str(cy)
    )

    # Preset geometry
    prst_geom = etree.SubElement(
        sp_pr, _qn("a", "prstGeom"), prst="straightConnector1"
    )
    etree.SubElement(prst_geom, _qn("a", "avLst"))

    # Line properties
    ln = _make_line_properties(style)
    sp_pr.append(ln)

    # Append to slide shape tree
    slide.shapes._spTree.append(cxn_sp)

    return cxn_sp


# ============================================================
# Public API: Freeform Arrow (Custom Geometry)
# ============================================================

def add_freeform_arrow(
    slide: Any,
    waypoints_emu: list[tuple[int, int]],
    style_config: dict[str, Any] | None = None,
) -> etree._Element:
    """Inject a freeform arrow shape with custom geometry into the slide.

    Supports 3+ waypoints for orthogonal (or arbitrary) routed paths.
    For exactly 2 waypoints, delegates to add_straight_connector.

    Args:
        slide: A python-pptx Slide object.
        waypoints_emu: List of (x, y) coordinates in EMU. Must have at
            least 2 points.
        style_config: Optional style overrides.

    Returns:
        The injected lxml element.

    Raises:
        ValueError: If fewer than 2 waypoints are provided.
    """
    if len(waypoints_emu) < 2:
        raise ValueError("At least 2 waypoints are required")

    if len(waypoints_emu) == 2:
        pt_a, pt_b = waypoints_emu
        return add_straight_connector(
            slide, pt_a[0], pt_a[1], pt_b[0], pt_b[1], style_config
        )

    style = _merged_style(style_config)
    shape_id = _next_shape_id(slide)

    # Compute bounding box
    xs = [p[0] for p in waypoints_emu]
    ys = [p[1] for p in waypoints_emu]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)

    box_left = min_x
    box_top = min_y
    box_cx = max_x - min_x
    box_cy = max_y - min_y

    # Ensure non-zero extents (a perfectly horizontal or vertical line
    # would have cy=0 or cx=0 which is valid but needs at least 1 EMU
    # for the path dimension to avoid division issues in some renderers).
    path_w = max(box_cx, 1)
    path_h = max(box_cy, 1)

    # Build <p:sp>
    sp = etree.Element(_qn("p", "sp"))

    # Non-visual properties
    nv = _make_non_visual_sp_props(shape_id, f"FreeformArrow {shape_id}")
    sp.append(nv)

    # Shape properties
    sp_pr = etree.SubElement(sp, _qn("p", "spPr"))

    # Transform
    xfrm = etree.SubElement(sp_pr, _qn("a", "xfrm"))
    etree.SubElement(
        xfrm, _qn("a", "off"), x=str(box_left), y=str(box_top)
    )
    etree.SubElement(
        xfrm, _qn("a", "ext"), cx=str(path_w), cy=str(path_h)
    )

    # Custom geometry
    cust_geom = etree.SubElement(sp_pr, _qn("a", "custGeom"))
    etree.SubElement(cust_geom, _qn("a", "avLst"))
    etree.SubElement(cust_geom, _qn("a", "gdLst"))
    etree.SubElement(cust_geom, _qn("a", "ahLst"))

    # Connection sites (empty)
    etree.SubElement(cust_geom, _qn("a", "cxnLst"))

    # Rectangle (text body bounding rect)
    rect = etree.SubElement(cust_geom, _qn("a", "rect"))
    rect.set("l", "0")
    rect.set("t", "0")
    rect.set("r", str(path_w))
    rect.set("b", str(path_h))

    # Path list
    path_lst = etree.SubElement(cust_geom, _qn("a", "pathLst"))
    path_el = etree.SubElement(
        path_lst,
        _qn("a", "path"),
        w=str(path_w),
        h=str(path_h),
    )

    # moveTo for first point
    move_to = etree.SubElement(path_el, _qn("a", "moveTo"))
    first_x = waypoints_emu[0][0] - min_x
    first_y = waypoints_emu[0][1] - min_y
    etree.SubElement(
        move_to, _qn("a", "pt"), x=str(first_x), y=str(first_y)
    )

    # lnTo for subsequent points
    for wx, wy in waypoints_emu[1:]:
        ln_to = etree.SubElement(path_el, _qn("a", "lnTo"))
        etree.SubElement(
            ln_to,
            _qn("a", "pt"),
            x=str(wx - min_x),
            y=str(wy - min_y),
        )

    # No fill on the shape itself
    etree.SubElement(sp_pr, _qn("a", "noFill"))

    # Line properties (with arrowheads)
    ln = _make_line_properties(style)
    sp_pr.append(ln)

    # Empty text body (required by OOXML schema for sp elements)
    txBody = etree.SubElement(sp, _qn("p", "txBody"))
    body_pr = etree.SubElement(txBody, _qn("a", "bodyPr"))
    lst_style = etree.SubElement(txBody, _qn("a", "lstStyle"))
    p_elem = etree.SubElement(txBody, _qn("a", "p"))

    # Append to slide shape tree
    slide.shapes._spTree.append(sp)

    return sp

"""
Grid-to-pixel layout engine for AWS architecture diagrams.

Converts grid-based node positions into absolute pixel coordinates,
respecting container nesting hierarchy and padding rules from the
AWS Architecture Icon Deck guidelines.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from diagram_schema import DiagramDefinition, DiagramNode, DiagramContainer, get_viewbox


# ============================================================
# Layout Constants (AWS Architecture Icon Deck)
# ============================================================

ICON_SIZE = 48
ICON_LABEL_GAP = 14
LABEL_LINE_HEIGHT = 14
MAX_LABEL_LINES = 2

# Grid cell dimensions
CELL_WIDTH = 180
CELL_HEIGHT = 160

# Container padding by type
# right padding accounts for icon (48px) + label text (~80px) overflow
CONTAINER_PADDING = {
    "aws-cloud":          {"top": 36, "right": 60, "bottom": 20, "left": 24},
    "region":             {"top": 32, "right": 50, "bottom": 15, "left": 18},
    "vpc":                {"top": 32, "right": 50, "bottom": 15, "left": 18},
    "az":                 {"top": 28, "right": 40, "bottom": 14, "left": 14},
    "public-subnet":      {"top": 30, "right": 50, "bottom": 15, "left": 18},
    "private-subnet":     {"top": 30, "right": 50, "bottom": 15, "left": 18},
    "security-group":     {"top": 24, "right": 36, "bottom": 12, "left": 12},
    "auto-scaling-group": {"top": 24, "right": 36, "bottom": 12, "left": 12},
    "generic":            {"top": 28, "right": 40, "bottom": 14, "left": 14},
}

# Canvas margin (extra right/bottom for label overflow)
CANVAS_MARGIN = 60

# Extra right margin for arrow labels that extend beyond node bboxes
ARROW_LABEL_MARGIN = 150

# Container header height
HEADER_HEIGHT = 26


# ============================================================
# Computed Layout Result
# ============================================================

@dataclass
class BoundingBox:
    """Axis-aligned bounding box."""
    x: float
    y: float
    w: float
    h: float

    @property
    def right(self) -> float:
        return self.x + self.w

    @property
    def bottom(self) -> float:
        return self.y + self.h

    @property
    def cx(self) -> float:
        return self.x + self.w / 2

    @property
    def cy(self) -> float:
        return self.y + self.h / 2

    def expand(self, margin: float) -> "BoundingBox":
        return BoundingBox(
            self.x - margin, self.y - margin,
            self.w + 2 * margin, self.h + 2 * margin,
        )

    def contains_point(self, px: float, py: float) -> bool:
        return self.x <= px <= self.right and self.y <= py <= self.bottom

    def intersects(self, other: "BoundingBox") -> bool:
        return not (
            self.right < other.x or other.right < self.x
            or self.bottom < other.y or other.bottom < self.y
        )


@dataclass
class NodeLayout:
    """Computed pixel position for a node."""
    node_id: str
    icon_x: float
    icon_y: float
    icon_w: float = ICON_SIZE
    icon_h: float = ICON_SIZE
    label_x: float = 0.0
    label_y: float = 0.0

    @property
    def bbox(self) -> BoundingBox:
        """Full bounding box including icon + label."""
        label_height = ICON_LABEL_GAP + MAX_LABEL_LINES * LABEL_LINE_HEIGHT
        total_h = self.icon_h + label_height
        total_w = max(self.icon_w, 80)  # Labels can be wider than icon
        cx = self.icon_x + self.icon_w / 2
        return BoundingBox(
            cx - total_w / 2, self.icon_y,
            total_w, total_h,
        )

    @property
    def center(self) -> tuple[float, float]:
        return (self.icon_x + self.icon_w / 2, self.icon_y + self.icon_h / 2)

    def edge_center(self, side: str) -> tuple[float, float]:
        """Get the center point of an icon edge."""
        cx, cy = self.center
        if side == "left":
            return (self.icon_x, cy)
        if side == "right":
            return (self.icon_x + self.icon_w, cy)
        if side == "top":
            return (cx, self.icon_y)
        if side == "bottom":
            return (cx, self.icon_y + self.icon_h)
        return self.center


@dataclass
class ContainerLayout:
    """Computed pixel position for a container."""
    container_id: str
    container_type: str
    label: str
    bbox: BoundingBox


@dataclass
class LayoutResult:
    """Complete layout computation result."""
    nodes: dict[str, NodeLayout] = field(default_factory=dict)
    containers: list[ContainerLayout] = field(default_factory=list)
    viewbox_width: int = 1024
    viewbox_height: int = 768


# ============================================================
# Layout Engine
# ============================================================

def compute_layout(diagram: DiagramDefinition) -> LayoutResult:
    """Compute pixel layout from a diagram definition."""
    result = LayoutResult()

    # Determine base viewbox from size preset
    vw, vh = get_viewbox(diagram.size)

    # Build container hierarchy lookup
    container_map: dict[str, DiagramContainer] = {
        c.id: c for c in diagram.containers
    }

    # Phase 1: Compute pixel origin offset from nesting
    # Start with canvas margin as the base offset
    base_x = CANVAS_MARGIN
    base_y = CANVAS_MARGIN

    # Phase 3: Place nodes on pixel grid
    # Determine grid range across all nodes
    all_cols = [n.x for n in diagram.nodes] if diagram.nodes else [0]
    all_rows = [n.y for n in diagram.nodes] if diagram.nodes else [0]
    min_col = min(all_cols)
    min_row = min(all_rows)

    # Calculate nesting depth offset for each node
    for node in diagram.nodes:
        depth_offset = _get_nesting_depth_offset(node, container_map)
        px = base_x + depth_offset["left"] + (node.x - min_col) * CELL_WIDTH + CELL_WIDTH / 2 - ICON_SIZE / 2
        py = base_y + depth_offset["top"] + (node.y - min_row) * CELL_HEIGHT + CELL_HEIGHT / 2 - ICON_SIZE / 2

        nl = NodeLayout(
            node_id=node.id,
            icon_x=px,
            icon_y=py,
        )
        nl.label_x = px + ICON_SIZE / 2
        nl.label_y = py + ICON_SIZE + ICON_LABEL_GAP
        result.nodes[node.id] = nl

    # Phase 4: Compute container bounding boxes (bottom-up)
    # Sort containers: innermost first (by depth)
    sorted_containers = _sort_containers_by_depth(diagram.containers, container_map)

    computed_container_bboxes: dict[str, BoundingBox] = {}

    for container in sorted_containers:
        child_bboxes = []

        for child_id in container.children:
            if child_id in result.nodes:
                child_bboxes.append(result.nodes[child_id].bbox)
            elif child_id in computed_container_bboxes:
                child_bboxes.append(computed_container_bboxes[child_id])

        if not child_bboxes:
            continue

        # Union of all child bboxes
        min_x = min(b.x for b in child_bboxes)
        min_y = min(b.y for b in child_bboxes)
        max_x = max(b.right for b in child_bboxes)
        max_y = max(b.bottom for b in child_bboxes)

        padding = CONTAINER_PADDING.get(container.type, CONTAINER_PADDING["generic"])

        content_w = (max_x - min_x) + padding["left"] + padding["right"]
        content_h = (max_y - min_y) + padding["top"] + padding["bottom"]

        # Ensure container is wide enough for header text
        min_header_w = len(container.label) * 8 + 48
        final_w = max(content_w, min_header_w)

        bbox = BoundingBox(
            x=min_x - padding["left"],
            y=min_y - padding["top"],
            w=final_w,
            h=content_h,
        )

        computed_container_bboxes[container.id] = bbox
        result.containers.append(ContainerLayout(
            container_id=container.id,
            container_type=container.type,
            label=container.label,
            bbox=bbox,
        ))

    # Phase 5: Compute final viewbox
    all_bboxes = [nl.bbox for nl in result.nodes.values()]
    all_bboxes.extend(cl.bbox for cl in result.containers)

    if all_bboxes:
        total_min_x = min(b.x for b in all_bboxes) - CANVAS_MARGIN
        total_min_y = min(b.y for b in all_bboxes) - CANVAS_MARGIN
        total_max_x = max(b.right for b in all_bboxes) + CANVAS_MARGIN
        total_max_y = max(b.bottom for b in all_bboxes) + CANVAS_MARGIN

        # Add extra right margin for arrow labels that may extend beyond nodes
        total_max_x += ARROW_LABEL_MARGIN

        # Auto-fit viewBox to actual content (no forced minimum from presets)
        content_w = int(total_max_x - total_min_x)
        content_h = int(total_max_y - total_min_y)

        # Add title block space (60px top) if not already accounted for
        title_space = 60 if total_min_y > 0 else 0
        result.viewbox_width = max(content_w, 400)
        result.viewbox_height = max(content_h + title_space, 300)
    else:
        result.viewbox_width = vw
        result.viewbox_height = vh

    # Sort containers outermost-first for correct SVG rendering order
    result.containers.sort(
        key=lambda c: -c.bbox.w * c.bbox.h
    )

    return result


# ============================================================
# Helper Functions
# ============================================================

def _get_nesting_depth_offset(
    node: DiagramNode,
    container_map: dict[str, DiagramContainer],
) -> dict[str, float]:
    """Calculate cumulative padding offset from nesting depth."""
    offset = {"top": 0.0, "left": 0.0}
    current_id = node.container

    while current_id and current_id in container_map:
        container = container_map[current_id]
        padding = CONTAINER_PADDING.get(container.type, CONTAINER_PADDING["generic"])
        offset["top"] += padding["top"]
        offset["left"] += padding["left"]
        current_id = container.parent

    return offset



def _sort_containers_by_depth(
    containers: list[DiagramContainer],
    container_map: dict[str, DiagramContainer],
) -> list[DiagramContainer]:
    """Sort containers innermost-first (deepest nesting first)."""

    def depth(c: DiagramContainer) -> int:
        d = 0
        current = c.parent
        while current and current in container_map:
            d += 1
            current = container_map[current].parent
        return d

    return sorted(containers, key=lambda c: -depth(c))

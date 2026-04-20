"""
Orthogonal (right-angle) arrow routing engine.

Routes connections between nodes using ONLY horizontal and vertical
line segments (M/L SVG path commands). Implements the AWS Architecture
Icon Deck guideline: "Use straight lines and right angles to connect
objects wherever possible."

Algorithm:
1. Select optimal exit/entry ports on source/target icons
2. Generate L-shape (1 bend) or Z-shape (2 bends) path
3. Check for obstacle crossings and reroute if needed
4. Separate parallel arrows by >= 15px
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from layout_engine import BoundingBox, NodeLayout, LayoutResult, ContainerLayout, HEADER_HEIGHT


# ============================================================
# Constants
# ============================================================

ARROW_MARGIN = 10          # Min distance from icon edge to first bend
PARALLEL_OFFSET = 15       # Offset between parallel arrows
OBSTACLE_CLEARANCE = 10    # Min clearance around obstacles
CALLOUT_RADIUS = 12        # Step number circle radius
CALLOUT_GAP = 4            # Gap on each side of callout circle


# ============================================================
# Data Types
# ============================================================

@dataclass
class Port:
    """A connection point on an icon edge."""
    x: float
    y: float
    side: str  # "left", "right", "top", "bottom"


@dataclass
class RoutedPath:
    """A routed orthogonal path between two nodes."""
    source_id: str
    target_id: str
    waypoints: list[tuple[float, float]]
    label: Optional[str] = None
    label_pos: Optional[tuple[float, float]] = None
    style: str = "solid"
    step_number: Optional[int] = None
    step_pos: Optional[tuple[float, float]] = None
    color: Optional[str] = None

    def to_svg_d(self) -> str:
        """Convert waypoints to SVG path 'd' attribute (M/L only)."""
        if not self.waypoints:
            return ""
        parts = [f"M {self.waypoints[0][0]:.1f},{self.waypoints[0][1]:.1f}"]
        for wx, wy in self.waypoints[1:]:
            parts.append(f"L {wx:.1f},{wy:.1f}")
        return " ".join(parts)


# ============================================================
# Port Selection
# ============================================================

VALID_SIDES = {"left", "right", "top", "bottom"}


def _select_ports(
    src: NodeLayout,
    tgt: NodeLayout,
    force_src_side: str | None = None,
    force_tgt_side: str | None = None,
) -> tuple[Port, Port]:
    """Select optimal ports based on relative positions.

    Supports forced port sides (source_port / target_port in connection JSON)
    to allow manual control when multiple arrows exit the same node.
    """
    # Forced ports
    if force_src_side and force_src_side in VALID_SIDES:
        src_port = Port(*src.edge_center(force_src_side), force_src_side)
    else:
        src_port = _auto_select_port(src, tgt, is_source=True)

    if force_tgt_side and force_tgt_side in VALID_SIDES:
        tgt_port = Port(*tgt.edge_center(force_tgt_side), force_tgt_side)
    else:
        tgt_port = _auto_select_port(tgt, src, is_source=False)

    return src_port, tgt_port


def _auto_select_port(
    node: NodeLayout, other: NodeLayout, is_source: bool
) -> Port:
    """Auto-select the best port based on relative position."""
    sx, sy = node.center
    tx, ty = other.center
    dx = tx - sx
    dy = ty - sy

    if abs(dx) >= abs(dy):
        if is_source:
            side = "right" if dx > 0 else "left"
        else:
            side = "left" if dx > 0 else "right"
    else:
        if is_source:
            side = "bottom" if dy > 0 else "top"
        else:
            side = "top" if dy > 0 else "bottom"

    return Port(*node.edge_center(side), side)


# ============================================================
# Path Generation
# ============================================================

def _generate_path(src_port: Port, tgt_port: Port) -> list[tuple[float, float]]:
    """Generate an orthogonal path between two ports.

    Returns waypoints for L-shape (1 bend) or Z-shape (2 bends) paths.
    All segments are strictly horizontal or vertical.
    """
    sx, sy = src_port.x, src_port.y
    tx, ty = tgt_port.x, tgt_port.y

    # Same horizontal line -> straight
    if abs(sy - ty) < 2:
        return [(sx, sy), (tx, ty)]

    # Same vertical line -> straight
    if abs(sx - tx) < 2:
        return [(sx, sy), (tx, ty)]

    # Horizontal-first ports (right->left, left->right)
    if src_port.side in ("right", "left") and tgt_port.side in ("left", "right"):
        mid_x = (sx + tx) / 2
        # If ports face each other, use simple Z-shape
        if (src_port.side == "right" and tx > sx) or (src_port.side == "left" and tx < sx):
            return [(sx, sy), (mid_x, sy), (mid_x, ty), (tx, ty)]
        # Ports face away: route around
        offset = ARROW_MARGIN * (1 if src_port.side == "right" else -1)
        return [(sx, sy), (sx + offset, sy), (sx + offset, ty), (tx, ty)]

    # Vertical-first ports (bottom->top, top->bottom)
    if src_port.side in ("top", "bottom") and tgt_port.side in ("top", "bottom"):
        mid_y = (sy + ty) / 2
        if (src_port.side == "bottom" and ty > sy) or (src_port.side == "top" and ty < sy):
            return [(sx, sy), (sx, mid_y), (tx, mid_y), (tx, ty)]
        offset = ARROW_MARGIN * (1 if src_port.side == "bottom" else -1)
        return [(sx, sy), (sx, sy + offset), (tx, sy + offset), (tx, ty)]

    # Mixed: horizontal port to vertical port -> L-shape
    if src_port.side in ("right", "left"):
        # Horizontal exit, vertical entry -> L-shape via (tx, sy)
        return [(sx, sy), (tx, sy), (tx, ty)]
    else:
        # Vertical exit, horizontal entry -> L-shape via (sx, ty)
        return [(sx, sy), (sx, ty), (tx, ty)]


# ============================================================
# Obstacle Avoidance
# ============================================================

def _segment_crosses_bbox(
    p1: tuple[float, float],
    p2: tuple[float, float],
    bbox: BoundingBox,
) -> bool:
    """Check if a horizontal or vertical segment crosses a bounding box."""
    x1, y1 = p1
    x2, y2 = p2

    # Horizontal segment
    if abs(y1 - y2) < 1:
        seg_y = y1
        seg_left = min(x1, x2)
        seg_right = max(x1, x2)
        return (
            bbox.y < seg_y < bbox.bottom
            and seg_left < bbox.right
            and seg_right > bbox.x
        )

    # Vertical segment
    if abs(x1 - x2) < 1:
        seg_x = x1
        seg_top = min(y1, y2)
        seg_bottom = max(y1, y2)
        return (
            bbox.x < seg_x < bbox.right
            and seg_top < bbox.bottom
            and seg_bottom > bbox.y
        )

    return False


def _path_crosses_obstacles(
    waypoints: list[tuple[float, float]],
    obstacles: list[BoundingBox],
    exclude_ids: set[str],
    all_nodes: dict[str, NodeLayout],
) -> list[BoundingBox]:
    """Find all obstacles that the path crosses."""
    crossed = []
    for node_id, node in all_nodes.items():
        if node_id in exclude_ids:
            continue
        expanded = node.bbox.expand(OBSTACLE_CLEARANCE)
        for i in range(len(waypoints) - 1):
            if _segment_crosses_bbox(waypoints[i], waypoints[i + 1], expanded):
                crossed.append(expanded)
                break
    return crossed


def _reroute_around_obstacle(
    waypoints: list[tuple[float, float]],
    obstacle: BoundingBox,
    src_port: Port,
) -> list[tuple[float, float]]:
    """Reroute a path around an obstacle using a detour."""
    sx, sy = waypoints[0]
    tx, ty = waypoints[-1]

    # Decide whether to go above or below the obstacle
    above_cost = abs(sy - (obstacle.y - OBSTACLE_CLEARANCE))
    below_cost = abs(sy - (obstacle.bottom + OBSTACLE_CLEARANCE))

    if above_cost <= below_cost:
        detour_y = obstacle.y - OBSTACLE_CLEARANCE
    else:
        detour_y = obstacle.bottom + OBSTACLE_CLEARANCE

    # Build a path that goes: start -> detour level -> across -> back to target level -> end
    if src_port.side in ("right", "left"):
        mid_x1 = obstacle.x - OBSTACLE_CLEARANCE
        mid_x2 = obstacle.right + OBSTACLE_CLEARANCE
        if sx < tx:
            return [
                (sx, sy), (mid_x1, sy), (mid_x1, detour_y),
                (mid_x2, detour_y), (mid_x2, ty), (tx, ty),
            ]
        else:
            return [
                (sx, sy), (mid_x2, sy), (mid_x2, detour_y),
                (mid_x1, detour_y), (mid_x1, ty), (tx, ty),
            ]
    else:
        mid_y1 = obstacle.y - OBSTACLE_CLEARANCE
        mid_y2 = obstacle.bottom + OBSTACLE_CLEARANCE
        detour_x = obstacle.x - OBSTACLE_CLEARANCE if sx < obstacle.cx else obstacle.right + OBSTACLE_CLEARANCE
        if sy < ty:
            return [
                (sx, sy), (sx, mid_y1), (detour_x, mid_y1),
                (detour_x, mid_y2), (tx, mid_y2), (tx, ty),
            ]
        else:
            return [
                (sx, sy), (sx, mid_y2), (detour_x, mid_y2),
                (detour_x, mid_y1), (tx, mid_y1), (tx, ty),
            ]


# ============================================================
# Label and Callout Placement
# ============================================================

def _compute_label_position(
    waypoints: list[tuple[float, float]],
    has_callout: bool = False,
) -> tuple[float, float]:
    """Place label at a clear position on the path.

    When a callout exists, place label at ~65% toward target (callout is at ~40%
    toward source) to maximize separation. Otherwise use the midpoint of the
    longest segment.
    """
    if len(waypoints) < 2:
        return (0.0, 0.0)

    # Compute total path length
    total_len = 0.0
    seg_lengths = []
    for i in range(len(waypoints) - 1):
        x1, y1 = waypoints[i]
        x2, y2 = waypoints[i + 1]
        seg_len = abs(x2 - x1) + abs(y2 - y1)
        seg_lengths.append(seg_len)
        total_len += seg_len

    if total_len < 1:
        return waypoints[0]

    # Place label at 65% from source when callout exists (callout is at 40%),
    # otherwise at 50% (midpoint)
    t_ratio = 0.65 if has_callout else 0.50
    target_dist = total_len * t_ratio

    accumulated = 0.0
    lx, ly = waypoints[-1]
    for i, seg_len in enumerate(seg_lengths):
        if accumulated + seg_len >= target_dist:
            t = (target_dist - accumulated) / seg_len if seg_len > 0 else 0
            x1, y1 = waypoints[i]
            x2, y2 = waypoints[i + 1]
            lx = x1 + t * (x2 - x1)
            ly = y1 + t * (y2 - y1)
            # Determine segment orientation for offset direction
            if abs(y1 - y2) < 1:  # horizontal
                ly -= 16
            else:  # vertical
                lx -= 18
            break
        accumulated += seg_len

    return (lx, ly)


def _nudge_label_from_icons(
    pos: tuple[float, float],
    src: NodeLayout,
    tgt: NodeLayout,
    waypoints: list[tuple[float, float]],
) -> tuple[float, float]:
    """Shift label toward path midpoint if it overlaps source/target icon bbox."""
    px, py = pos
    clearance = 20  # min px gap between label center and icon bbox edge

    for node in (src, tgt):
        expanded = node.bbox.expand(clearance)
        if expanded.contains_point(px, py):
            # Push label toward path midpoint
            if len(waypoints) >= 2:
                mid_idx = len(waypoints) // 2
                mx = (waypoints[mid_idx - 1][0] + waypoints[mid_idx][0]) / 2
                my = (waypoints[mid_idx - 1][1] + waypoints[mid_idx][1]) / 2
                # Interpolate 60% toward midpoint
                px = px + 0.6 * (mx - px)
                py = py + 0.6 * (my - py)
                # Re-apply vertical offset for horizontal segments
                if abs(waypoints[mid_idx - 1][1] - waypoints[mid_idx][1]) < 1:
                    py -= 16
    return (px, py)


def _nudge_away_from_nodes(
    pos: tuple[float, float],
    src: NodeLayout,
    tgt: NodeLayout,
    min_clearance: float,
) -> tuple[float, float]:
    """If a position overlaps a node's label area, nudge it outward."""
    px, py = pos
    for node in (src, tgt):
        bbox = node.bbox
        # Use an expanded bbox to keep callouts further from labels
        expanded = BoundingBox(
            bbox.x - min_clearance, bbox.y - min_clearance,
            bbox.w + 2 * min_clearance, bbox.h + 2 * min_clearance,
        )
        if expanded.contains_point(px, py):
            cx, cy = node.center
            dx = px - cx
            dy = py - cy
            norm = max((dx ** 2 + dy ** 2) ** 0.5, 1.0)
            # Push to the nearest edge of the expanded bbox
            push = min_clearance + 8
            px = px + dx / norm * push
            py = py + dy / norm * push
    return (px, py)


def _compute_callout_position(
    waypoints: list[tuple[float, float]],
) -> tuple[float, float]:
    """Place step number callout near the source end (30% of path length).

    Placing near the source avoids overlap with labels at the midpoint.
    """
    total_len = 0.0
    seg_lengths = []
    for i in range(len(waypoints) - 1):
        x1, y1 = waypoints[i]
        x2, y2 = waypoints[i + 1]
        seg_len = abs(x2 - x1) + abs(y2 - y1)
        seg_lengths.append(seg_len)
        total_len += seg_len

    # Place callout at 40% from source to avoid overlap with node labels
    target = total_len * 0.40
    accumulated = 0.0
    for i, seg_len in enumerate(seg_lengths):
        if accumulated + seg_len >= target:
            t = (target - accumulated) / seg_len if seg_len > 0 else 0
            x1, y1 = waypoints[i]
            x2, y2 = waypoints[i + 1]
            return (x1 + t * (x2 - x1), y1 + t * (y2 - y1))
        accumulated += seg_len

    return waypoints[-1] if waypoints else (0, 0)


# ============================================================
# Container Title Bar Avoidance
# ============================================================

def _fix_title_bar_crossings(
    waypoints: list[tuple[float, float]],
    containers: list[ContainerLayout],
) -> list[tuple[float, float]]:
    """Reroute path segments that cross container title bars.

    A container title bar occupies [bbox.y, bbox.y + HEADER_HEIGHT + 4].
    If a horizontal segment runs through that zone, push it below.
    """
    title_zones: list[tuple[float, float, float, float]] = []
    for cl in containers:
        if cl.container_type in ("az", "security-group", "auto-scaling-group", "generic"):
            continue
        b = cl.bbox
        title_zones.append((b.x, b.y, b.right, b.y + HEADER_HEIGHT + 4))

    if not title_zones:
        return waypoints

    fixed = list(waypoints)
    for tz_x1, tz_y1, tz_x2, tz_y2 in title_zones:
        new_fixed = []
        for i, (wx, wy) in enumerate(fixed):
            if i > 0:
                prev_x, prev_y = fixed[i - 1]
                # Check horizontal segment crossing title bar
                if abs(prev_y - wy) < 1:  # horizontal segment
                    seg_y = wy
                    seg_left = min(prev_x, wx)
                    seg_right = max(prev_x, wx)
                    if (tz_y1 <= seg_y <= tz_y2
                            and seg_left < tz_x2
                            and seg_right > tz_x1):
                        # Push this segment below the title bar
                        safe_y = tz_y2 + 6
                        if new_fixed:
                            # Adjust previous point's Y
                            last = new_fixed[-1]
                            new_fixed[-1] = (last[0], safe_y)
                        new_fixed.append((wx, safe_y))
                        continue
            new_fixed.append((wx, wy))
        fixed = new_fixed

    return fixed


# ============================================================
# Parallel Arrow Handling
# ============================================================

def _offset_parallel(
    waypoints: list[tuple[float, float]],
    offset: float,
) -> list[tuple[float, float]]:
    """Offset all waypoints perpendicular to the main flow direction."""
    if len(waypoints) < 2:
        return waypoints

    # Determine main direction from first segment
    dx = waypoints[1][0] - waypoints[0][0]
    dy = waypoints[1][1] - waypoints[0][1]

    if abs(dx) >= abs(dy):
        # Horizontal flow -> offset vertically
        return [(x, y + offset) for x, y in waypoints]
    else:
        # Vertical flow -> offset horizontally
        return [(x + offset, y) for x, y in waypoints]


# ============================================================
# Main Router
# ============================================================

def route_connections(
    layout: LayoutResult,
    connections: list,
) -> list[RoutedPath]:
    """Route all connections with orthogonal paths.

    Args:
        layout: Computed node/container positions
        connections: List of DiagramConnection objects

    Returns:
        List of RoutedPath objects with computed waypoints
    """
    routed: list[RoutedPath] = []

    # Track used paths for parallel detection
    path_registry: dict[tuple[str, str], int] = {}

    for conn in connections:
        src = layout.nodes.get(conn.source)
        tgt = layout.nodes.get(conn.target)
        if not src or not tgt:
            continue

        # Select ports (supports forced port sides)
        force_src = getattr(conn, "source_port", None)
        force_tgt = getattr(conn, "target_port", None)
        src_port, tgt_port = _select_ports(src, tgt, force_src, force_tgt)

        # Generate initial path
        waypoints = _generate_path(src_port, tgt_port)

        # Obstacle avoidance (up to 3 iterations)
        exclude = {conn.source, conn.target}
        for _ in range(3):
            crossed = _path_crosses_obstacles(
                waypoints, [], exclude, layout.nodes
            )
            if not crossed:
                break
            waypoints = _reroute_around_obstacle(
                waypoints, crossed[0], src_port
            )

        # Avoid container title bars
        waypoints = _fix_title_bar_crossings(waypoints, layout.containers)

        # Handle parallel arrows
        pair_key = tuple(sorted([conn.source, conn.target]))
        count = path_registry.get(pair_key, 0)
        if count > 0:
            offset = PARALLEL_OFFSET * count
            waypoints = _offset_parallel(waypoints, offset)
        path_registry[pair_key] = count + 1

        # Compute step number position (near source, 30%)
        step_pos = _compute_callout_position(waypoints) if conn.step_number else None

        # Nudge callout away from source/target node label areas
        if step_pos:
            step_pos = _nudge_away_from_nodes(
                step_pos, src, tgt, CALLOUT_RADIUS + 4
            )

        # Compute label position
        has_callout = conn.step_number is not None
        label_pos = _compute_label_position(waypoints, has_callout) if conn.label else None

        # Nudge label away from source/target icon bboxes
        if label_pos:
            label_pos = _nudge_label_from_icons(label_pos, src, tgt, waypoints)

        # Collision avoidance: if callout and label are too close, shift label
        if label_pos and step_pos:
            dist = ((label_pos[0] - step_pos[0]) ** 2 + (label_pos[1] - step_pos[1]) ** 2) ** 0.5
            if dist < CALLOUT_RADIUS * 3:
                lx, ly = label_pos
                sx_c, sy_c = step_pos
                dx_shift = lx - sx_c
                dy_shift = ly - sy_c
                norm = max((dx_shift ** 2 + dy_shift ** 2) ** 0.5, 1.0)
                shift_amount = CALLOUT_RADIUS * 3 - dist + 5
                label_pos = (
                    lx + dx_shift / norm * shift_amount,
                    ly + dy_shift / norm * shift_amount,
                )

        routed.append(RoutedPath(
            source_id=conn.source,
            target_id=conn.target,
            waypoints=waypoints,
            label=conn.label,
            label_pos=label_pos,
            style=conn.style,
            step_number=conn.step_number,
            step_pos=step_pos,
            color=getattr(conn, "color", None),
        ))

    return routed

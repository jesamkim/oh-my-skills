"""
AWS Architecture Diagram JSON Schema.

Defines the data model for declarative diagram definitions.
Claude produces JSON matching this schema; the Python engine
handles layout, routing, and rendering.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from typing import Optional


# ============================================================
# Container types matching AWS Architecture Icon Deck
# ============================================================

CONTAINER_TYPES = {
    "aws-cloud",
    "region",
    "vpc",
    "az",
    "public-subnet",
    "private-subnet",
    "security-group",
    "auto-scaling-group",
    "generic",
}

# Connection styles
CONNECTION_STYLES = {"solid", "dashed", "bidirectional"}

# Standard viewBox presets
VIEWBOX_PRESETS = {
    "simple": (800, 500),
    "standard": (1024, 768),
    "complex": (1200, 900),
    "wide": (1400, 600),
}


# ============================================================
# Data Classes
# ============================================================

@dataclass
class DiagramNode:
    """A service or resource icon placed on the diagram."""
    id: str
    service: str              # Maps to icons/<service>.svg
    label: str                # Primary label (e.g., "Amazon EC2")
    x: int                    # Grid column (0-based)
    y: int                    # Grid row (0-based)
    sublabel: Optional[str] = None   # Optional second line
    container: Optional[str] = None  # Parent container ID


@dataclass
class DiagramConnection:
    """An arrow connecting two nodes."""
    source: str               # Source node ID
    target: str               # Target node ID
    label: Optional[str] = None       # Arrow label (e.g., "HTTPS")
    style: str = "solid"              # "solid", "dashed", "bidirectional"
    step_number: Optional[int] = None # Numbered callout circle
    color: Optional[str] = None       # Custom arrow color (hex, e.g., "#8C4FFF")
    source_port: Optional[str] = None # Force exit port: "left","right","top","bottom"
    target_port: Optional[str] = None # Force entry port: "left","right","top","bottom"


@dataclass
class DiagramContainer:
    """A group boundary (AWS Cloud, VPC, Subnet, etc.)."""
    id: str
    type: str                 # One of CONTAINER_TYPES
    label: str
    parent: Optional[str] = None     # Parent container ID
    children: list[str] = field(default_factory=list)  # Node or container IDs


@dataclass
class DiagramDefinition:
    """Complete diagram specification."""
    title: str
    nodes: list[DiagramNode] = field(default_factory=list)
    connections: list[DiagramConnection] = field(default_factory=list)
    containers: list[DiagramContainer] = field(default_factory=list)
    subtitle: Optional[str] = None
    theme: str = "light"       # "light" or "dark"
    size: str = "standard"     # Key from VIEWBOX_PRESETS or "WxH"


# ============================================================
# Serialization / Deserialization
# ============================================================

def to_json(diagram: DiagramDefinition, indent: int = 2) -> str:
    """Serialize a DiagramDefinition to JSON string."""
    return json.dumps(asdict(diagram), indent=indent, ensure_ascii=False)


def from_json(json_str: str) -> DiagramDefinition:
    """Deserialize a JSON string to DiagramDefinition."""
    data = json.loads(json_str)
    return _dict_to_diagram(data)


def from_file(path: str) -> DiagramDefinition:
    """Load a DiagramDefinition from a JSON file."""
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return _dict_to_diagram(data)


def _dict_to_diagram(data: dict) -> DiagramDefinition:
    """Convert a raw dict to a DiagramDefinition."""
    nodes = [DiagramNode(**n) for n in data.get("nodes", [])]
    connections = [DiagramConnection(**c) for c in data.get("connections", [])]
    containers = [DiagramContainer(**g) for g in data.get("containers", [])]

    return DiagramDefinition(
        title=data["title"],
        subtitle=data.get("subtitle"),
        theme=data.get("theme", "light"),
        size=data.get("size", "standard"),
        nodes=nodes,
        connections=connections,
        containers=containers,
    )


def get_viewbox(size: str) -> tuple[int, int]:
    """Resolve a size string to (width, height) pixels."""
    if size in VIEWBOX_PRESETS:
        return VIEWBOX_PRESETS[size]
    if "x" in size.lower():
        parts = size.lower().split("x")
        return (int(parts[0]), int(parts[1]))
    return VIEWBOX_PRESETS["standard"]

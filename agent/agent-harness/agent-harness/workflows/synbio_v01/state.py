"""Shared workflow state threaded through the V0.1 module pipeline."""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class SynBioState:
    """State passed to and updated by each module, in order.

    Each module reads only the fields it needs and writes only the field(s)
    it owns (see the module -> field mapping in workflow.py). Extending the
    pipeline means adding one field here plus one module; existing fields
    and modules stay untouched.
    """

    request: str = ""
    task: dict[str, Any] = field(default_factory=dict)
    literature_records: list[dict[str, Any]] = field(default_factory=list)
    pathway: dict[str, Any] = field(default_factory=dict)
    competition_analysis: list[dict[str, Any]] = field(default_factory=list)
    nodes: list[dict[str, Any]] = field(default_factory=list)
    engineering_designs: list[dict[str, Any]] = field(default_factory=list)
    evidence: list[dict[str, Any]] = field(default_factory=list)
    evaluation: dict[str, Any] = field(default_factory=dict)
    final_report: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Plain-dict view of the full state (JSON-serializable)."""
        return asdict(self)

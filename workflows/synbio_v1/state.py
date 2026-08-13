"""Shared workflow state threaded through the V1 module pipeline."""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class SynBioV1State:
    """State passed to and updated by each module, in order.

    `retrieval` holds the Knowledge Retrieval Layer's output (matched DDR id,
    the full DDR record if any, the match reason, and recommended strategy
    tags - see modules/retriever.py). Every later module is grounded in
    `retrieval["ddr"]`; none of them invent biology independently of it.
    """

    request: str = ""
    task: dict[str, Any] = field(default_factory=dict)
    retrieval: dict[str, Any] = field(default_factory=dict)
    diagnosis: dict[str, Any] = field(default_factory=dict)
    engineering_actions: list[dict[str, Any]] = field(default_factory=list)
    evidence: list[dict[str, Any]] = field(default_factory=list)
    validation_plan: dict[str, list[str]] = field(default_factory=dict)
    final_report: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Plain-dict view of the full state (JSON-serializable)."""
        return asdict(self)

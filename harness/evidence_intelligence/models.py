"""The `EvidenceObject` shape (Module 3 prompt §4) and the controlled
vocabularies it and its neighbors use.

`EvidenceObject` is deliberately a plain dataclass, not a SQLAlchemy model:
nothing in this package persists it (see package docstring). Every instance
is constructed on demand by `harness.evidence_intelligence.adapters` from a
row/record another package already owns (`harness.diagnosis.models.
EvidenceItem` or a `knowledge/ddr_database/*.json` decision_chain step), so
"the fundamental unit of this module" is a *view*, not a *store* - exactly
the additive posture the prompt's Architectural Boundary section requires.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

# Module 3 prompt §4.11: categorical only, never an arbitrary numeric score.
ConfidenceLevel = Literal["High", "Medium", "Low", "Unknown"]
CONFIDENCE_LEVELS: tuple[ConfidenceLevel, ...] = ("High", "Medium", "Low", "Unknown")

# Module 3 prompt §4 evidence_origin examples.
EvidenceOrigin = Literal[
    "published experiment", "internal experiment", "simulation",
    "model prediction", "expert annotation", "literature-derived analysis",
]

# Module 3 prompt §4 evidence_type examples.
EvidenceType = Literal[
    "direct engineering validation", "multi-omics correlation",
    "simulation prediction", "mechanistic hypothesis", "expert interpretation",
]

# Which existing subsystem this EvidenceObject was projected from - lets a
# caller resolve back to the real record (and to the right review endpoint,
# see EvidenceReviewPointer below) instead of treating this as a new source
# of truth.
OriginKind = Literal["diagnosis_evidence_item", "ddr_decision_step"]


@dataclass
class EvidenceReviewPointer:
    """Module 3 prompt §8 (Human Review Integration): "Do NOT create a
    separate approval system." This package has no review-writing endpoint
    of its own - it only tells the caller which *existing* review mechanism
    applies to this evidence object's origin, and that mechanism's current
    status, so a frontend can deep-link to it instead of a new one being
    built."""

    status: str
    reviewable_via: str
    note: str = ""


@dataclass
class EvidenceObject:
    """Module 3 prompt §4: the fundamental, engineering-meaningful unit of
    this module. Field names follow the prompt's minimum-required-fields
    list verbatim; `evidence_id`/`origin_kind`/`origin_ref`/`review` are
    additive provenance bookkeeping the prompt's §9 (Data Provenance
    Requirements) implies but doesn't name."""

    evidence_id: str  # "diag:{evidence_item_id}" | "ddr:{ddr_id}:{step}"
    claim: str
    source: str
    evidence_origin: EvidenceOrigin
    evidence_type: EvidenceType
    host: str | None
    product: str | None
    engineering_intervention: str | None
    experimental_context: dict[str, Any]
    result: dict[str, Any]
    applicability_boundary: list[str]
    limitations: list[str]
    confidence_level: ConfidenceLevel
    confidence_basis: str
    origin_kind: OriginKind
    origin_ref: dict[str, Any]
    review: EvidenceReviewPointer
    evidence_grading: str | None = None  # 硬/软/混合/待定 when the origin carries it (DDR only)


@dataclass
class EngineeringContextQuery:
    """Module 3 prompt §5: retrieval driven by engineering context, not
    text similarity alone. Every field is optional and additive - an
    all-empty query degrades to `LocalDDRAdapter`'s existing "empty query =
    full browse" contract rather than raising."""

    host: str | None = None
    product: str | None = None
    objective: str | None = None
    bottleneck: str | None = None
    intervention_type: str | None = None
    experimental_context: str | None = None
    free_text: str = ""


# ---------------------------------------------------------------------------
# Component 4 - Engineering Provenance Graph
# ---------------------------------------------------------------------------

# Module 3 prompt §7's chain, as node kinds.
ProvenanceNodeKind = Literal[
    "engineering_decision", "engineering_strategy", "mechanistic_rule",
    "evidence_object", "experiment", "paper",
]


@dataclass
class ProvenanceNode:
    id: str
    kind: ProvenanceNodeKind
    label: str
    ref: dict[str, Any] = field(default_factory=dict)


@dataclass
class ProvenanceEdge:
    source: str
    target: str
    relation: str  # e.g. "supported_by", "distilled_from", "cites", "reported_in"


@dataclass
class ProvenanceGraph:
    """Module 3 prompt §7: "why does the Agent believe this engineering
    choice is reasonable?" `unresolved` lists hops this graph could not
    fill in - e.g. no rule yet distilled, no DDR-level experiment object -
    surfaced explicitly rather than the graph silently stopping (prompt §9:
    "If information is unavailable: explicitly mark unknown")."""

    anchor: dict[str, Any]
    nodes: list[ProvenanceNode]
    edges: list[ProvenanceEdge]
    unresolved: list[str] = field(default_factory=list)

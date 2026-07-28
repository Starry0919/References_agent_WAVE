"""Evidence Condition Matching (prompt §5.8): a pure, deterministic rule
function - no LLM involvement, matching this repo's existing discipline
that transferability judgments are rule-based (`harness.scientific_
evaluation.evidence`'s own 8-dimension matcher for `EvidenceAssessment`
already sets this precedent for evaluated designs; this module produces
the equivalent formal report for raw `EvidenceItem` retrieval instead of
duplicating that assessment logic).

Any organism/strain/condition/timepoint/intervention/measurement mismatch
downgrades the result - never silently treated as a direct match (prompt
invariant #11/#12: cross-strain/cross-species evidence must not directly
support a claim).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


def _dim_match(query_value: Any, evidence_value: Any) -> str:
    if query_value in (None, "", "unknown") or evidence_value in (None, "", "unknown", "not_reported"):
        return "unknown"
    if str(query_value).strip().lower() == str(evidence_value).strip().lower():
        return "match"
    return "mismatch"


def _timepoint_match(query_tp: dict[str, Any] | None, evidence_tp: dict[str, Any] | None, tolerance_ratio: float = 0.25) -> str:
    if not query_tp or not evidence_tp:
        return "unknown"
    qv, ev = query_tp.get("value"), evidence_tp.get("value")
    qu, eu = query_tp.get("unit"), evidence_tp.get("unit")
    if qv is None or ev is None:
        return "unknown"
    if qu and eu and str(qu).lower() != str(eu).lower():
        return "mismatch"  # different units never silently compared
    tolerance = max(abs(qv) * tolerance_ratio, 1e-9)
    return "match" if abs(qv - ev) <= tolerance else "mismatch"


@dataclass
class MatchContext:
    """The query side of the comparison - a diagnosis/design's current
    biological/experimental context, in the same shape
    `harness.diagnosis.models.BiologicalContext`/`ProjectObjective` already
    carry (this function takes plain fields, not those ORM rows, so it has
    no import-cycle dependency on the diagnosis package)."""

    organism: str | None = None
    strain: str | None = None
    genotype: str | None = None
    medium: str | None = None
    condition: dict[str, Any] = field(default_factory=dict)
    timepoint: dict[str, Any] | None = None
    intervention: str | None = None
    measurement: str | None = None


@dataclass
class EvidenceSide:
    organism: str | None = None
    strain: str | None = None
    genotype: str | None = None
    medium: str | None = None
    condition: dict[str, Any] = field(default_factory=dict)
    timepoint: dict[str, Any] | None = None
    intervention: str | None = None
    measurement: str | None = None
    directness: str = "indirect"  # the EvidenceItem's own directness field


@dataclass
class MatchResult:
    organism_match: str
    strain_match: str
    genotype_match: str
    medium_match: str
    condition_match: str
    timepoint_match: str
    intervention_match: str
    measurement_match: str
    directness: str
    transfer_risks: list[str]
    overall_match_status: str
    downgrade_reasons: list[str]


def _condition_dict_match(query_cond: dict[str, Any], evidence_cond: dict[str, Any]) -> str:
    shared_keys = set(query_cond) & set(evidence_cond)
    if not shared_keys:
        return "unknown"
    results = {_dim_match(query_cond.get(k), evidence_cond.get(k)) for k in shared_keys}
    if "mismatch" in results:
        return "mismatch"
    if results == {"unknown"}:
        return "unknown"
    return "match"


def compute_match(query: MatchContext, evidence: EvidenceSide) -> MatchResult:
    organism_match = _dim_match(query.organism, evidence.organism)
    strain_match = _dim_match(query.strain, evidence.strain)
    genotype_match = _dim_match(query.genotype, evidence.genotype)
    medium_match = _dim_match(query.medium, evidence.medium)
    condition_match = _condition_dict_match(query.condition, evidence.condition)
    timepoint_match = _timepoint_match(query.timepoint, evidence.timepoint)
    intervention_match = _dim_match(query.intervention, evidence.intervention)
    measurement_match = _dim_match(query.measurement, evidence.measurement)

    dims = {
        "organism": organism_match, "strain": strain_match, "genotype": genotype_match, "medium": medium_match,
        "condition": condition_match, "timepoint": timepoint_match, "intervention": intervention_match, "measurement": measurement_match,
    }
    transfer_risks = [f"{name} could not be compared (missing metadata)" for name, v in dims.items() if v == "unknown"]
    transfer_risks += [f"{name} mismatch between query context and evidence" for name, v in dims.items() if v == "mismatch"]
    downgrade_reasons: list[str] = []

    if organism_match == "mismatch":
        overall = "cross_species"
        downgrade_reasons.append("evidence organism differs from the query organism - cross-species transfer, never a direct match")
    elif strain_match == "mismatch":
        overall = "cross_strain"
        downgrade_reasons.append("evidence strain differs from the query strain within the same organism - cross-strain transfer")
    elif measurement_match == "mismatch":
        overall = "endpoint_mismatch"
        downgrade_reasons.append("evidence measures a different endpoint than the query")
    elif condition_match == "mismatch" or medium_match == "mismatch":
        overall = "condition_mismatch"
        downgrade_reasons.append("evidence was collected under different medium/condition than the query context")
    else:
        unknown_count = sum(1 for v in dims.values() if v == "unknown")
        match_count = sum(1 for v in dims.values() if v == "match")
        if unknown_count >= 5:
            overall = "insufficient_metadata"
            downgrade_reasons.append(f"{unknown_count}/8 dimensions could not be compared - too little metadata to judge transferability")
        elif match_count >= 6 and unknown_count <= 1:
            overall = "direct_match" if evidence.directness == "direct" else "close_match"
        elif match_count >= 4:
            overall = "close_match"
        else:
            overall = "partial_match"

    directness = "direct" if overall in ("direct_match",) and evidence.directness == "direct" else "indirect"
    return MatchResult(
        organism_match=organism_match, strain_match=strain_match, genotype_match=genotype_match, medium_match=medium_match,
        condition_match=condition_match, timepoint_match=timepoint_match, intervention_match=intervention_match,
        measurement_match=measurement_match, directness=directness, transfer_risks=transfer_risks,
        overall_match_status=overall, downgrade_reasons=downgrade_reasons,
    )

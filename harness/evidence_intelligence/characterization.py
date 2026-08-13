"""Component 3 - Evidence Characterization (Module 3 prompt §6).

Every function here maps EXISTING categorical signals (evidence_grading
`硬/软/混合/待定` from `harness.evidence_retrieval.evidence_grading`,
`EvidenceItem.quality`/`directness`, DDR `calibration_status`) onto the
Module 3 vocabulary. None of them compute or introduce a new numeric score
- the prompt is explicit ("Do NOT create arbitrary numerical confidence
scores"), and `harness.evidence_retrieval.service.assess_ddr_applicability`
already shows what NOT to imitate (a bare 0.15/0.5/0.85 float) - see the
Phase 1 architecture review for that pre-existing issue, left untouched and
out of scope here.
"""
from __future__ import annotations

from typing import Any

from harness.evidence_intelligence.models import CONFIDENCE_LEVELS, ConfidenceLevel

_SIMULATION_SOURCE_HINTS = (
    "optknock", "cameo", "straindesign", "fba", "pfba", "fva", "moma", "docking",
    "foldx", "rosetta", "alphafold", "esmfold", "homology", "machine_learning",
    "retropath", "novostoic", "equilibrator", "rbs_calculator",
)


# ---------------------------------------------------------------------------
# confidence_level (High/Medium/Low/Unknown)
# ---------------------------------------------------------------------------


def confidence_from_ddr_grading(*, evidence_grading: str | None, calibration_status: str | None) -> tuple[ConfidenceLevel, str]:
    """DDR-origin evidence: derived from the existing 硬/软/混合/待定 grade
    (`harness.evidence_retrieval.evidence_grading`) plus whether a human has
    calibrated this step yet (`ddr_converter`'s per-step `calibration_status`).
    A hard-graded step that no human has reviewed is Medium, not High -
    "硬" alone is a machine/self-assessment, not a substitute for review."""
    if evidence_grading == "硬":
        if calibration_status == "calibrated":
            return "High", "硬证据 (hard evidence) and this step has been human-calibrated"
        return "Medium", "硬证据 (hard evidence) but pending human calibration (calibration_status != 'calibrated')"
    if evidence_grading == "混合":
        return "Medium", "混合证据 (mixed hard/soft evidence) for this step"
    if evidence_grading == "软":
        return "Low", "软证据 (soft/computational-prediction evidence) - not yet experimentally confirmed"
    if evidence_grading == "待定":
        return "Unknown", "证据分级待定 (evidence grading unresolved) - needs manual review"
    return "Unknown", "no evidence_grading recorded for this decision_chain step"


def confidence_from_diagnosis_item(*, quality: str | None, directness: str | None) -> tuple[ConfidenceLevel, str]:
    """Diagnosis-origin evidence (`harness.diagnosis.models.EvidenceItem`):
    derived from its existing `quality` (high/medium/low) and `directness`
    (direct/indirect) fields - both already categorical, never re-scored."""
    if quality == "high":
        if directness == "direct":
            return "High", "quality=high, directness=direct"
        return "Medium", "quality=high but directness=indirect"
    if quality == "medium":
        return "Medium", "quality=medium"
    if quality == "low":
        return "Low", "quality=low"
    return "Unknown", "no quality recorded on this evidence item"


assert set(CONFIDENCE_LEVELS) == {"High", "Medium", "Low", "Unknown"}  # vocabulary guard


# ---------------------------------------------------------------------------
# evidence_origin / evidence_type
# ---------------------------------------------------------------------------

_DDR_STEP_HAS_SIMULATION_SOURCE = lambda source: any(h in source.lower() for h in _SIMULATION_SOURCE_HINTS)  # noqa: E731


def origin_and_type_from_ddr_step(step: dict[str, Any]) -> tuple[str, str]:
    """A DDR decision_chain step always comes from a published paper, but
    the *evidence itself* inside that paper can be a real measurement or a
    computational prediction the paper merely reports - `evidence.source`
    text (already classified by `evidence_grading.SOURCE_GRADE_DEFAULTS`)
    is what actually distinguishes them, not the fact of publication."""
    evidence = step.get("evidence") or {}
    source_text = str(evidence.get("source", ""))
    grading = step.get("evidence_grading")
    reason_nature = step.get("reason_nature") or ""

    is_simulation = _DDR_STEP_HAS_SIMULATION_SOURCE(source_text)
    origin = "model prediction" if is_simulation else "published experiment"

    if is_simulation:
        evidence_type = "simulation prediction"
    elif reason_nature in ("机理推断", "文献类比"):
        evidence_type = "mechanistic hypothesis"
    elif grading == "硬":
        evidence_type = "direct engineering validation"
    elif grading == "软":
        evidence_type = "simulation prediction"
    elif grading == "混合":
        evidence_type = "multi-omics correlation"
    else:
        evidence_type = "expert interpretation"
    return origin, evidence_type


_DIAG_SOURCE_TYPE_TO_ORIGIN = {
    "literature": "published experiment",
    "expert_rule": "expert annotation",
    "llm_reasoning": "literature-derived analysis",
    "model_run": "model prediction",
    "experiment_result": "internal experiment",
    "observation": "internal experiment",
}


def origin_and_type_from_diagnosis_item(*, source_type: str, directness: str | None) -> tuple[str, str]:
    origin = _DIAG_SOURCE_TYPE_TO_ORIGIN.get(source_type, "expert annotation")
    if source_type == "model_run":
        evidence_type = "simulation prediction"
    elif source_type == "llm_reasoning":
        evidence_type = "mechanistic hypothesis"
    elif source_type == "expert_rule":
        evidence_type = "expert interpretation"
    elif source_type in ("literature", "experiment_result", "observation"):
        evidence_type = "direct engineering validation" if directness == "direct" else "multi-omics correlation"
    else:
        evidence_type = "expert interpretation"
    return origin, evidence_type


# ---------------------------------------------------------------------------
# Applicability / Uncertainty (Module 3 prompt §6's display example)
# ---------------------------------------------------------------------------

_UNCERTAINTY_FOR_CONFIDENCE: dict[ConfidenceLevel, str] = {
    "High": "Low", "Medium": "Moderate", "Low": "High", "Unknown": "Unknown",
}


def applicability_level(*, applicability_boundary: list[str], match_status: str | None = None) -> str:
    """Categorical, not numeric - reuses `harness.evidence_retrieval.
    condition_matching.MATCH_STATUSES` when a real `EvidenceMatchReport`
    was computed for this evidence against a project (`match_status`);
    otherwise falls back to a coarse read of how many boundary conditions
    are recorded (more recorded conditions = more can be checked = more
    confidently "Medium" rather than "Unknown", never a numeric score)."""
    if match_status:
        if match_status in ("direct_match", "close_match"):
            return "High"
        if match_status in ("partial_match", "cross_strain"):
            return "Medium"
        if match_status in ("cross_species", "condition_mismatch", "endpoint_mismatch"):
            return "Low"
        return "Unknown"  # insufficient_metadata | not_applicable
    if not applicability_boundary:
        return "Unknown"
    return "Medium" if len(applicability_boundary) >= 1 else "Unknown"


def characterize(
    *,
    evidence_type: str,
    confidence_level: ConfidenceLevel,
    applicability_boundary: list[str],
    limitations: list[str],
    match_status: str | None = None,
) -> dict[str, Any]:
    """Module 3 prompt §6's exact display shape (Evidence Level /
    Applicability / Limitation / Uncertainty), built entirely from fields
    already on the `EvidenceObject` - a formatting/normalization step, not
    a new judgment."""
    return {
        "evidence_level": evidence_type,
        "applicability": applicability_level(applicability_boundary=applicability_boundary, match_status=match_status),
        "limitation": "; ".join(limitations) if limitations else "none recorded",
        "uncertainty": _UNCERTAINTY_FOR_CONFIDENCE[confidence_level],
    }

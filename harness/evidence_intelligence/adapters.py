"""Component 1 - projects an existing `EvidenceItem`/DDR decision_chain step
into an `EvidenceObject`. Pure functions: no DB writes, no file writes.
"""
from __future__ import annotations

from typing import Any

from harness.diagnosis.models import EvidenceItem, EvidenceLink
from harness.evidence_intelligence import characterization as char
from harness.evidence_intelligence.models import EvidenceObject, EvidenceReviewPointer


def _diag_applicability_boundary(item: EvidenceItem, link: EvidenceLink | None) -> list[str]:
    boundary: list[str] = []
    if item.organism:
        boundary.append(f"host: {item.organism}")
    if item.strain:
        boundary.append(f"strain: {item.strain}")
    if item.condition:
        boundary.append(f"condition: {item.condition}")
    if link is not None and link.condition_match not in ("unknown", ""):
        boundary.append(f"condition_match vs. linked hypothesis: {link.condition_match}")
    if not boundary:
        boundary.append("no structured applicability metadata recorded for this evidence item")
    return boundary


def _diag_limitations(item: EvidenceItem, link: EvidenceLink | None) -> list[str]:
    limitations: list[str] = []
    if link is not None and link.limitations:
        limitations.append(link.limitations)
    if item.extraction_status not in ("complete", "not_applicable"):
        limitations.append(f"extraction_status={item.extraction_status}")
    if item.uncertainty_if_reported:
        limitations.append(f"reported uncertainty: {item.uncertainty_if_reported}")
    if item.superseded_by_evidence_item_id:
        limitations.append(f"superseded by {item.superseded_by_evidence_item_id}")
    if not limitations:
        limitations.append("no limitations recorded")
    return limitations


def from_diagnosis_evidence_item(item: EvidenceItem, link: EvidenceLink | None = None) -> EvidenceObject:
    """`link` is the `EvidenceLink` (if any) connecting this item to a
    `HypothesisVersion` - when present, its `claim`/`condition_match`/
    `limitations` are more specific than the bare item, so they win."""
    evidence_origin, evidence_type = char.origin_and_type_from_diagnosis_item(
        source_type=item.source_type, directness=item.directness,
    )
    confidence_level, confidence_basis = char.confidence_from_diagnosis_item(quality=item.quality, directness=item.directness)

    review_status = link.condition_match if link is not None else "not_linked_to_a_hypothesis"
    review = EvidenceReviewPointer(
        status=review_status,
        reviewable_via=f"POST /api/diagnosis/evidence-links/{link.evidence_link_id}/review" if link is not None else "n/a - not yet linked to a hypothesis",
        note="diagnosis-origin evidence is reviewed via harness.diagnosis.evidence.review_evidence_link, a spot-check annotation that never gates the diagnosis loop",
    )

    return EvidenceObject(
        evidence_id=f"diag:{item.evidence_item_id}",
        claim=(link.claim if link is not None and link.claim else item.content_summary),
        source=item.source_reference or item.title or f"{item.source_type} (no source_reference recorded)",
        evidence_origin=evidence_origin,
        evidence_type=evidence_type,
        host=item.organism,
        product=None,  # EvidenceItem has no product field - never guessed (prompt §9)
        engineering_intervention=item.intervention,
        experimental_context={"condition": item.condition or {}, "time_ref": item.time_ref, "comparator": item.comparator},
        result={"measurement": item.measurement, "direction": item.direction, "effect_size_if_reported": item.effect_size_if_reported},
        applicability_boundary=_diag_applicability_boundary(item, link),
        limitations=_diag_limitations(item, link),
        confidence_level=confidence_level,
        confidence_basis=confidence_basis,
        origin_kind="diagnosis_evidence_item",
        origin_ref={"evidence_item_id": item.evidence_item_id, "project_id": item.project_id, "evidence_link_id": link.evidence_link_id if link else None},
        review=review,
        evidence_grading=None,
    )


def _ddr_applicability_boundary(step: dict[str, Any], ddr_metadata: dict[str, Any]) -> list[str]:
    boundary: list[str] = []
    host = ddr_metadata.get("organism") or ddr_metadata.get("host")
    if host:
        boundary.append(f"host: {host}")
    product = ddr_metadata.get("target_product")
    if product:
        boundary.append(f"product: {product}")
    target = step.get("target") or {}
    if target.get("condition"):
        boundary.append(f"condition: {target['condition']}")
    if not boundary:
        boundary.append("DDR metadata does not record host/product/condition for this step")
    return boundary


def _ddr_limitations(step: dict[str, Any]) -> list[str]:
    limitations: list[str] = []
    grading = step.get("evidence_grading")
    if grading in ("软", "待定"):
        limitations.append("软证据/待定 (computational prediction or unresolved grading) - pending experimental confirmation" if grading == "软" else "evidence_grading unresolved - needs manual review")
    if step.get("calibration_status") not in ("calibrated", None):
        limitations.append(f"calibration_status={step.get('calibration_status')}")
    if not step.get("result", {}).get("quantified"):
        limitations.append("result not marked as quantified in the source record")
    if not limitations:
        limitations.append("no limitations recorded")
    return limitations


def from_ddr_decision_step(ddr_id: str, step: dict[str, Any], ddr_metadata: dict[str, Any]) -> EvidenceObject:
    """`step` is one `decision_chain[i]` dict (schema_v2) and `ddr_metadata`
    is that DDR's top-level `metadata` block - both read straight out of
    `knowledge/ddr_database/{ddr_id}.json` via `LocalDDRAdapter`, never
    re-parsed from raw text here."""
    evidence_origin, evidence_type = char.origin_and_type_from_ddr_step(step)
    confidence_level, confidence_basis = char.confidence_from_ddr_grading(
        evidence_grading=step.get("evidence_grading"), calibration_status=step.get("calibration_status"),
    )

    step_no = step.get("step")
    review = EvidenceReviewPointer(
        status=step.get("calibration_status") or "pending",
        reviewable_via=f"POST /api/paper-extraction/ddr/{ddr_id}/attempts",
        note="DDR-origin evidence is reviewed via the existing dual-annotator calibration flow (harness.paper_extraction.calibration), not a new approval system",
    )

    evidence_field = step.get("evidence") or {}
    claim = step.get("rule") or (step.get("trigger") or {}).get("observation") or evidence_field.get("description", "")

    return EvidenceObject(
        evidence_id=f"ddr:{ddr_id}:{step_no}",
        claim=claim,
        source=f"{ddr_id} decision_chain step {step_no}" + (f" ({evidence_field.get('source')})" if evidence_field.get("source") else ""),
        evidence_origin=evidence_origin,
        evidence_type=evidence_type,
        host=ddr_metadata.get("organism") or ddr_metadata.get("host"),
        product=ddr_metadata.get("target_product"),
        engineering_intervention=step.get("implementation_detail") or step.get("implementation"),
        experimental_context={"target": step.get("target") or {}, "trigger": step.get("trigger") or {}},
        result=step.get("result") or {},
        applicability_boundary=_ddr_applicability_boundary(step, ddr_metadata),
        limitations=_ddr_limitations(step),
        confidence_level=confidence_level,
        confidence_basis=confidence_basis,
        origin_kind="ddr_decision_step",
        origin_ref={"ddr_id": ddr_id, "step": step_no},
        review=review,
        evidence_grading=step.get("evidence_grading"),
    )

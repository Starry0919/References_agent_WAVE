"""Evidence Retriever / Assessor (doc03 4.5): every `EvidenceLink` uses an
explicit relation (doc03 2.3) - "consistent with" is never rendered as
"proves". Without a real literature-retrieval tool wired up, only the
local DDR knowledge base and general domain reasoning are used, always
tagged `source_type="expert_rule"` or `"llm_reasoning"` with
`quality="low"` - never a fabricated DOI, dataset, or experiment result
(doc03 4.5/7).
"""
from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from harness.diagnosis.models import EVIDENCE_RELATIONS, EvidenceItem, EvidenceLink
from harness.ids import new_id, now
from harness.memory import event_types as et
from harness.memory.event_store import append_event, snapshot

EVIDENCE_LINK_FIELDS = (
    "evidence_link_id", "hypothesis_version_id", "evidence_item_id", "relation", "claim", "condition_match",
    "strength_basis", "limitations", "created_by", "created_at",
)


class InvalidEvidenceRelation(ValueError):
    pass


def record_evidence_item(
    session: Session,
    *,
    project_id: str,
    source_type: str,
    content_summary: str,
    actor_id: str,
    source_reference: str | None = None,
    condition: dict[str, Any] | None = None,
    time_ref: dict[str, Any] | None = None,
    quality: str = "low",
    directness: str = "indirect",
    model_run_id: str | None = None,
    experiment_run_id: str | None = None,
    observation_id: str | None = None,
    # Additive literature-source fields (prompt §5.7) - all default to
    # None/"not_reported"/"not_applicable" for the pre-existing
    # expert_rule/llm_reasoning/model_run/experiment_result/observation
    # callers, which pass none of these.
    title: str | None = None,
    authors: list[str] | None = None,
    publication_year: int | None = None,
    journal_or_repository: str | None = None,
    doi_or_accession: str | None = None,
    doi_verification_status: str = "not_applicable",
    organism: str | None = None,
    strain: str | None = None,
    genotype: str | None = None,
    intervention: str | None = None,
    comparator: str | None = None,
    measurement: str | None = None,
    direction: str | None = None,
    effect_size_if_reported: dict[str, Any] | None = None,
    uncertainty_if_reported: dict[str, Any] | None = None,
    extraction_method: str = "manual_or_rule",
    extraction_status: str = "not_applicable",
    retrieval_provenance: dict[str, Any] | None = None,
) -> EvidenceItem:
    item = EvidenceItem(
        evidence_item_id=new_id("EVID"), project_id=project_id, source_type=source_type, source_reference=source_reference,
        content_summary=content_summary, condition=condition or {}, time_ref=time_ref, quality=quality, directness=directness,
        model_run_id=model_run_id, experiment_run_id=experiment_run_id, observation_id=observation_id,
        created_by=actor_id, created_at=now(),
        title=title, authors=authors, publication_year=publication_year, journal_or_repository=journal_or_repository,
        doi_or_accession=doi_or_accession, doi_verification_status=doi_verification_status, organism=organism,
        strain=strain, genotype=genotype, intervention=intervention, comparator=comparator, measurement=measurement,
        direction=direction, effect_size_if_reported=effect_size_if_reported, uncertainty_if_reported=uncertainty_if_reported,
        extraction_method=extraction_method, extraction_status=extraction_status, retrieval_provenance=retrieval_provenance,
    )
    session.add(item)
    session.flush()
    return item


def link_evidence(
    session: Session,
    *,
    hypothesis_version_id: str,
    evidence_item_id: str,
    relation: str,
    actor_id: str,
    claim: str = "",
    condition_match: str = "unknown",
    strength_basis: str = "",
    limitations: str = "",
) -> EvidenceLink:
    if relation not in EVIDENCE_RELATIONS:
        raise InvalidEvidenceRelation(f"relation must be one of {EVIDENCE_RELATIONS}, got {relation!r}")
    link = EvidenceLink(
        evidence_link_id=new_id("ELINK"), hypothesis_version_id=hypothesis_version_id, evidence_item_id=evidence_item_id,
        relation=relation, claim=claim, condition_match=condition_match, strength_basis=strength_basis,
        limitations=limitations, created_by=actor_id, created_at=now(),
    )
    session.add(link)
    session.flush()

    item = session.get(EvidenceItem, evidence_item_id)
    append_event(
        session, project_id=item.project_id, event_type=et.DIAGNOSIS_EVIDENCE_LINKED, entity_type="EvidenceLink",
        entity_id=link.evidence_link_id, payload=snapshot(link, EVIDENCE_LINK_FIELDS), actor_type="agent", actor_id=actor_id,
    )
    return link


def supersede_evidence_item(session: Session, *, evidence_item_id: str, superseded_by_id: str, actor_id: str) -> EvidenceItem:
    """doc03 3.6: a publication correction/supersession must not be
    silently ignored by evidence links formed before it - callers of
    `link_evidence` should check `superseded_by_evidence_item_id` before
    treating an item as current."""
    item = session.get(EvidenceItem, evidence_item_id)
    if item is None:
        raise ValueError(f"no such evidence item: {evidence_item_id}")
    item.superseded_by_evidence_item_id = superseded_by_id
    session.flush()
    return item

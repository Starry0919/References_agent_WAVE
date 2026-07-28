"""Persistence + DOI-verification entry points for
`harness.evidence_retrieval`."""
from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from harness.evidence_retrieval.condition_matching import EvidenceSide, MatchContext, MatchResult, compute_match
from harness.evidence_retrieval.crossref_adapter import CrossrefEvidenceAdapter
from harness.evidence_retrieval.models import EvidenceMatchReport
from harness.ids import new_id, now
from harness.memory import event_types as et
from harness.memory.event_store import append_event


def record_match_report(
    session: Session, *, project_id: str, query_context_ref: dict[str, Any], evidence_id: str, result: MatchResult, actor_id: str,
) -> EvidenceMatchReport:
    row = EvidenceMatchReport(
        match_report_id=new_id("EVMATCH"), query_context_ref=query_context_ref, evidence_id=evidence_id,
        organism_match=result.organism_match, strain_match=result.strain_match, genotype_match=result.genotype_match,
        medium_match=result.medium_match, condition_match=result.condition_match, timepoint_match=result.timepoint_match,
        intervention_match=result.intervention_match, measurement_match=result.measurement_match, directness=result.directness,
        transfer_risks=result.transfer_risks, overall_match_status=result.overall_match_status,
        downgrade_reasons=result.downgrade_reasons, created_at=now(),
    )
    session.add(row)
    session.flush()
    append_event(
        session, project_id=project_id, event_type=et.GEN_EVIDENCE_MATCH_COMPUTED, entity_type="EvidenceMatchReport",
        entity_id=row.match_report_id, payload={"evidence_id": evidence_id, "overall_match_status": result.overall_match_status, "downgrade_reasons": result.downgrade_reasons},
        actor_type="agent", actor_id=actor_id,
    )
    return row


def match_evidence_item(session: Session, *, project_id: str, query: MatchContext, evidence_item, actor_id: str) -> EvidenceMatchReport:
    """`evidence_item` is a `harness.diagnosis.models.EvidenceItem` row."""
    evidence_side = EvidenceSide(
        organism=evidence_item.organism, strain=evidence_item.strain, genotype=evidence_item.genotype,
        medium=(evidence_item.condition or {}).get("medium"), condition=evidence_item.condition or {},
        timepoint=evidence_item.time_ref, intervention=evidence_item.intervention, measurement=evidence_item.measurement,
        directness=evidence_item.directness,
    )
    result = compute_match(query, evidence_side)
    return record_match_report(session, project_id=project_id, query_context_ref=query.__dict__, evidence_id=evidence_item.evidence_item_id, result=result, actor_id=actor_id)


def verify_doi(session: Session, *, project_id: str, doi: str, actor_id: str) -> bool:
    """Real Crossref lookup. Returns False (never raises) for a
    fabricated/unresolvable DOI, and records the rejection as a
    `ProjectEvent` so a hallucinated reference leaves an audit trail rather
    than silently disappearing."""
    resolved = CrossrefEvidenceAdapter().resolve_doi(doi)
    if not resolved:
        append_event(
            session, project_id=project_id, event_type=et.GEN_HALLUCINATED_REFERENCE_REJECTED, entity_type="DOI",
            entity_id=doi, payload={"doi": doi, "reason": "Crossref could not resolve this DOI"}, actor_type="agent", actor_id=actor_id,
        )
    return resolved

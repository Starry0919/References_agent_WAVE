"""Facade `harness/api/evidence_intelligence.py` calls - the only module in
this package the API layer imports directly.
"""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from harness.diagnosis.models import EvidenceItem, EvidenceLink
from harness.evidence_intelligence import adapters, characterization
from harness.evidence_intelligence.models import EngineeringContextQuery, EvidenceObject, ProvenanceGraph
from harness.evidence_intelligence.provenance_graph import build_engineering_provenance_graph
from harness.evidence_intelligence.retrieval import search_evidence
from harness.evidence_retrieval.local_ddr_adapter import LocalDDRAdapter


def get_evidence_object(evidence_id: str, *, session: Session) -> EvidenceObject | None:
    """`evidence_id` follows the scheme `adapters.py` mints:
    `diag:{evidence_item_id}` or `ddr:{ddr_id}:{step}`."""
    origin_kind, _, rest = evidence_id.partition(":")

    if origin_kind == "diag":
        item = session.get(EvidenceItem, rest)
        if item is None:
            return None
        link = session.execute(select(EvidenceLink).where(EvidenceLink.evidence_item_id == rest)).scalars().first()
        return adapters.from_diagnosis_evidence_item(item, link)

    if origin_kind == "ddr":
        ddr_id, _, step_str = rest.partition(":")
        doc = LocalDDRAdapter().fetch(ddr_id)
        if doc is None:
            return None
        step = next((s for s in (doc.raw_metadata or {}).get("decision_chain", []) if str(s.get("step")) == step_str), None)
        if step is None:
            return None
        return adapters.from_ddr_decision_step(ddr_id, step, (doc.raw_metadata or {}).get("metadata", {}))

    return None


def search_evidence_objects(
    query: EngineeringContextQuery, *, session: Session | None = None, project_id: str | None = None, limit: int = 20,
) -> list[EvidenceObject]:
    return search_evidence(query, session=session, project_id=project_id, limit=limit)


def get_provenance_graph(anchor_type: str, anchor_id: str, *, session: Session | None = None) -> ProvenanceGraph | None:
    return build_engineering_provenance_graph(anchor_type, anchor_id, session=session)


def characterize_evidence_object(obj: EvidenceObject, *, match_status: str | None = None) -> dict:
    return characterization.characterize(
        evidence_type=obj.evidence_type, confidence_level=obj.confidence_level,
        applicability_boundary=obj.applicability_boundary, limitations=obj.limitations, match_status=match_status,
    )

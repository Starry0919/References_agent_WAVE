"""Component 2 - Engineering-aware Evidence Retrieval (Module 3 prompt §5).

Composes the retrieval sources that already exist -
`harness.evidence_retrieval.local_ddr_adapter.LocalDDRAdapter` (DDR corpus)
and `harness.diagnosis.models.EvidenceItem` (project wet-lab/literature
evidence) - behind one `EngineeringContextQuery`, instead of adding a third
retrieval mechanism or an embedding index. Matching is field-overlap /
substring, same technique both existing sources already use
(`LocalDDRAdapter.search`, `harness.evidence_retrieval.relevance.
ddr_relevance`) - this module does not introduce semantic/embedding search,
consistent with the Phase 1 finding that nothing in this repo does either.
"""
from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from harness.diagnosis.models import EvidenceItem, EvidenceLink
from harness.evidence_intelligence import adapters
from harness.evidence_intelligence.models import EngineeringContextQuery, EvidenceObject
from harness.evidence_retrieval.local_ddr_adapter import LocalDDRAdapter


def _text_overlap(needle: str, haystack: str) -> bool:
    needle, haystack = needle.strip().lower(), haystack.strip().lower()
    return bool(needle) and (needle in haystack or haystack in needle)


def _ddr_step_matches(step: dict[str, Any], meta: dict[str, Any], query: EngineeringContextQuery) -> bool:
    if query.host:
        host = str(meta.get("organism") or meta.get("host") or "")
        if not _text_overlap(query.host, host):
            return False
    if query.product:
        product = str(meta.get("target_product") or "")
        if not _text_overlap(query.product, product):
            return False
    if query.intervention_type:
        impl = str(step.get("implementation_detail") or step.get("implementation") or "")
        if query.intervention_type.lower() not in impl.lower():
            return False
    if query.bottleneck:
        haystack = " ".join([str((step.get("trigger") or {}).get("observation", "")), str(step.get("rule") or "")])
        if query.bottleneck.lower() not in haystack.lower():
            return False
    if query.objective:
        haystack = " ".join([str(meta.get("target_product", "")), str(step.get("rule") or "")])
        if query.objective.lower() not in haystack.lower():
            return False
    if query.experimental_context:
        haystack = str((step.get("target") or {}).get("condition", ""))
        if query.experimental_context.lower() not in haystack.lower():
            return False
    return True


def _diag_item_matches(item: EvidenceItem, query: EngineeringContextQuery) -> bool:
    if query.host:
        if not _text_overlap(query.host, item.organism or ""):
            return False
    if query.intervention_type:
        if query.intervention_type.lower() not in (item.intervention or "").lower():
            return False
    if query.experimental_context:
        if query.experimental_context.lower() not in str(item.condition or {}).lower():
            return False
    if query.free_text:
        haystack = " ".join(filter(None, [item.content_summary, item.source_reference, item.title]))
        if query.free_text.lower() not in haystack.lower():
            return False
    # objective/bottleneck/product have no EvidenceItem field analog - never
    # excluded on a field the item structurally cannot carry (prompt §9:
    # never fabricate; here that means never silently pretending a match
    # was checked when it wasn't).
    return True


def _relevance_score(obj: EvidenceObject, query: EngineeringContextQuery) -> int:
    score = 0
    if query.host and obj.host and _text_overlap(query.host, obj.host):
        score += 2
    if query.product and obj.product and _text_overlap(query.product, obj.product):
        score += 2
    if query.intervention_type and obj.engineering_intervention and query.intervention_type.lower() in obj.engineering_intervention.lower():
        score += 1
    if obj.confidence_level == "High":
        score += 1
    return score


def search_evidence(
    query: EngineeringContextQuery, *, session: Session | None = None, project_id: str | None = None, limit: int = 20,
) -> list[EvidenceObject]:
    """`session` is optional - callers with no DB session (e.g. a script)
    still get DDR-corpus results; passing a session additionally searches
    project evidence items. `project_id` scopes the diagnosis-item search
    only (the DDR corpus is cross-project curated knowledge, same as every
    other DDR-reading endpoint in this repo)."""
    results: list[EvidenceObject] = []

    search_text = " ".join(t for t in (query.free_text, query.product, query.objective, query.bottleneck) if t)
    ddr_adapter = LocalDDRAdapter()
    for doc in ddr_adapter.search(search_text).documents:
        rec = doc.raw_metadata or {}
        meta = rec.get("metadata", {})
        ddr_id = rec.get("ddr_id", "")
        for step in rec.get("decision_chain", []):
            if not _ddr_step_matches(step, meta, query):
                continue
            results.append(adapters.from_ddr_decision_step(ddr_id, step, meta))

    if session is not None:
        stmt = select(EvidenceItem)
        if project_id:
            stmt = stmt.where(EvidenceItem.project_id == project_id)
        items = session.execute(stmt).scalars().all()
        for item in items:
            if not _diag_item_matches(item, query):
                continue
            link = session.execute(
                select(EvidenceLink).where(EvidenceLink.evidence_item_id == item.evidence_item_id)
            ).scalars().first()
            results.append(adapters.from_diagnosis_evidence_item(item, link))

    results.sort(key=lambda o: _relevance_score(o, query), reverse=True)
    return results[:limit]

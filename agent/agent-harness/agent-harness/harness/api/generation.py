"""Scientific Capability Adapters API routes (prompt §8.1: LLM generation
provenance + evidence retrieval/condition-matching queries). Every route
calls the same real service layer `tests/llm_generation/` exercises.
"""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from harness.api.deps import get_db_session
from harness.evidence_retrieval.crossref_adapter import CrossrefEvidenceAdapter
from harness.evidence_retrieval.local_ddr_adapter import LocalDDRAdapter
from harness.evidence_retrieval.models import EvidenceMatchReport
from harness.evidence_retrieval.service import verify_doi
from harness.llm_generation.client import StructuredGenerationClient
from harness.llm_generation.models import LLMGenerationRecord

router = APIRouter(prefix="/api/generation", tags=["generation"])


def _record_dict(r: LLMGenerationRecord) -> dict[str, Any]:
    return {
        "generation_id": r.generation_id, "task_type": r.task_type, "provider": r.provider, "model_id": r.model_id,
        "prompt_template_id": r.prompt_template_id, "prompt_template_version": r.prompt_template_version,
        "output_schema_version": r.output_schema_version, "validation_status": r.validation_status,
        "retry_count": r.retry_count, "fallback_used": r.fallback_used, "shared_model_risk": r.shared_model_risk,
        "token_usage_if_available": r.token_usage_if_available, "latency": r.latency, "created_at": r.created_at,
    }


@router.get("/health")
def health() -> dict:
    llm = StructuredGenerationClient().health_check()
    crossref = CrossrefEvidenceAdapter().health_check()
    ddr = LocalDDRAdapter().health_check()
    return {
        "llm": {"available": llm.available, "provider": llm.provider, "model": llm.model, "reason": llm.reason},
        "crossref": {"available": crossref.available, "reason": crossref.reason},
        "local_ddr": {"available": ddr.available, "reason": ddr.reason},
    }


@router.get("/records")
def list_records(task_type: str | None = None, session: Session = Depends(get_db_session)) -> dict:
    stmt = select(LLMGenerationRecord).order_by(LLMGenerationRecord.created_at.desc())
    if task_type:
        stmt = stmt.where(LLMGenerationRecord.task_type == task_type)
    rows = session.execute(stmt).scalars().all()
    return {"records": [_record_dict(r) for r in rows]}


@router.get("/records/{generation_id}")
def get_record(generation_id: str, session: Session = Depends(get_db_session)) -> dict:
    row = session.get(LLMGenerationRecord, generation_id)
    if row is None:
        raise HTTPException(404, f"no such generation record: {generation_id}")
    d = _record_dict(row)
    d["raw_output_artifact_ref"] = row.raw_output_artifact_ref
    d["parsed_output_ref"] = row.parsed_output_ref
    return d


class VerifyDoiBody(BaseModel):
    project_id: str
    doi: str
    actor_id: str


@router.post("/evidence/verify-doi")
def verify_doi_route(body: VerifyDoiBody, session: Session = Depends(get_db_session)) -> dict:
    resolved = verify_doi(session, project_id=body.project_id, doi=body.doi, actor_id=body.actor_id)
    return {"doi": body.doi, "resolved": resolved}


@router.get("/evidence/search")
def search_evidence(query: str, source: str = "local_ddr") -> dict:
    adapter = CrossrefEvidenceAdapter() if source == "crossref" else LocalDDRAdapter()
    result = adapter.search(query, {}, {})
    return {
        "source_name": result.source_name, "total_available": result.total_available,
        "documents": [
            {"source_id": d.source_id, "title": d.title, "authors": d.authors, "publication_year": d.publication_year,
             "journal_or_repository": d.journal_or_repository, "doi_or_accession": d.doi_or_accession}
            for d in result.documents
        ],
    }


@router.get("/evidence/documents/{source_id}")
def get_evidence_document(source_id: str, source: str = "local_ddr") -> dict:
    """Single-document detail (Knowledge & Evidence page's Literature
    Evidence tab: clicking a search result). `local_ddr`'s `raw_metadata`
    already carries the curated `engineering_problem` / `biological_
    diagnosis` / `engineering_hypothesis` / `engineering_actions` sections
    a DDR record was built from - this is the real "what experimental
    design idea was extracted from this paper" content, not a new
    extraction step; `crossref` documents have no such curated content,
    so `engineering_design` stays null there rather than inventing one.
    """
    adapter = CrossrefEvidenceAdapter() if source == "crossref" else LocalDDRAdapter()
    doc = adapter.fetch(source_id)
    if doc is None:
        raise HTTPException(404, "evidence document not found")
    raw = doc.raw_metadata or {}
    engineering_design = None
    if source != "crossref":
        diagnosis = raw.get("biological_diagnosis", {})
        hypothesis = raw.get("engineering_hypothesis", {})
        actions = raw.get("engineering_actions", [])
        if diagnosis or hypothesis or actions:
            engineering_design = {
                "problem_statement": raw.get("engineering_problem", {}).get("problem_statement", ""),
                "bottlenecks": diagnosis.get("bottlenecks", []),
                "mechanistic_explanation": diagnosis.get("mechanistic_explanation", ""),
                "hypothesis": hypothesis.get("hypothesis", ""),
                "expected_effect": hypothesis.get("expected_effect", ""),
                "actions": [
                    {
                        "modification_type": a.get("modification_type", ""), "target": a.get("target", ""),
                        "gene_or_pathway": a.get("gene_or_pathway", ""), "rationale": a.get("rationale", ""),
                        "expected_effect": a.get("expected_effect", ""), "risk": a.get("risk", ""),
                        "validation": a.get("validation", []),
                    }
                    for a in actions
                ],
            }
    return {
        "source_id": doc.source_id, "title": doc.title, "authors": doc.authors, "publication_year": doc.publication_year,
        "journal_or_repository": doc.journal_or_repository, "doi_or_accession": doc.doi_or_accession, "url": doc.url,
        "abstract_or_summary": doc.abstract_or_summary, "engineering_design": engineering_design,
    }


@router.get("/evidence/match-reports")
def list_match_reports(evidence_id: str | None = None, session: Session = Depends(get_db_session)) -> dict:
    stmt = select(EvidenceMatchReport).order_by(EvidenceMatchReport.created_at.desc())
    if evidence_id:
        stmt = stmt.where(EvidenceMatchReport.evidence_id == evidence_id)
    rows = session.execute(stmt).scalars().all()
    return {
        "match_reports": [
            {"match_report_id": r.match_report_id, "evidence_id": r.evidence_id, "overall_match_status": r.overall_match_status,
             "downgrade_reasons": r.downgrade_reasons, "transfer_risks": r.transfer_risks, "directness": r.directness, "created_at": r.created_at}
            for r in rows
        ]
    }

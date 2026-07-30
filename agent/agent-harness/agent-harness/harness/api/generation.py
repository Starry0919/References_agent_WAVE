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
from harness.evidence_retrieval.relevance import ddr_relevance
from harness.evidence_retrieval.service import assess_ddr_applicability, verify_doi
from harness.i18n import get_locale
from harness.llm_generation.client import StructuredGenerationClient
from harness.llm_generation.models import LLMGenerationRecord
from harness.paper_extraction.reasoning_view import (
    build_agent_trace,
    build_evidence_graph,
    build_evidence_provenance,
    build_experimental_design,
    build_header_summary,
)
from harness.projects.models import Project
from harness.projects.service import project_context_summary
from harness.translation.service import translate_batch

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
def search_evidence(query: str = "", source: str = "local_ddr", project_id: str | None = None, session: Session = Depends(get_db_session)) -> dict:
    """Empty `query` is a full browse of the corpus, not a 422 or an empty
    result (老师 §Phase2) - `LocalDDRAdapter.search` returns everything for
    `""`/whitespace. Optional `project_id` tags each result `relevant`
    (host/product overlap with the project's own context) and sorts
    relevant-first, without hiding the rest - a DDR from an unrelated
    product can still hold a transferable rule (老师 §四.5), so "project
    filter" here means ranking, not exclusion (老师 §Phase5: "根据 Current
    Project Context 筛选 Relevant DDR ... 而不是静态展示数据库").
    """
    adapter = CrossrefEvidenceAdapter() if source == "crossref" else LocalDDRAdapter()
    result = adapter.search(query, {}, {})
    project_host = project_product = None
    if project_id and source != "crossref":
        project = session.get(Project, project_id)
        if project is not None:
            ctx = project_context_summary(project)
            project_host, project_product = ctx["host"], ctx["target_product"]

    def _doc_dict(d: Any) -> dict[str, Any]:
        out = {"source_id": d.source_id, "title": d.title, "authors": d.authors, "publication_year": d.publication_year,
               "journal_or_repository": d.journal_or_repository, "doi_or_accession": d.doi_or_accession}
        if project_host or project_product:
            out.update(ddr_relevance(d.raw_metadata, project_host=project_host, project_product=project_product))
        return out

    documents = [_doc_dict(d) for d in result.documents]
    if project_host or project_product:
        documents.sort(key=lambda d: not d.get("relevant", False))
    return {"source_name": result.source_name, "total_available": result.total_available, "documents": documents}


_ENGINEERING_DESIGN_TEXT_FIELDS = ("problem_statement", "mechanistic_explanation", "hypothesis", "expected_effect")
_ACTION_TEXT_FIELDS = ("rationale", "expected_effect")


def _localize_evidence_document(
    title: str, abstract_or_summary: str, engineering_design: dict[str, Any] | None,
) -> tuple[str, str, dict[str, Any] | None]:
    """Translates the raw source-paper text this route surfaces (title,
    abstract, curated engineering-design narrative) to the requesting
    client's locale - none of this content is UI chrome, so it is never
    covered by the static `i18n.tsx`/`harness/i18n.py` dictionaries.
    Symmetric: a zh-CN viewer gets English paper text translated to
    Chinese; an en-US viewer gets Chinese-authored text (e.g. hand-curated
    DDR records) translated to English. One batched call via
    `harness.translation.service.translate_batch` (cached per-string,
    per-target-locale), so a repeat view of the same document in the same
    locale is free.
    """
    locale = get_locale()
    if locale not in ("zh-CN", "en-US"):
        return title, abstract_or_summary, engineering_design
    texts = [title, abstract_or_summary or ""]
    if engineering_design:
        texts.extend(engineering_design.get(field) or "" for field in _ENGINEERING_DESIGN_TEXT_FIELDS)
        actions = engineering_design.get("actions") or []
        for action in actions:
            texts.extend(action.get(field) or "" for field in _ACTION_TEXT_FIELDS)
    translated = translate_batch(texts, locale)
    it = iter(translated)
    title = next(it)
    abstract_or_summary = next(it)
    if engineering_design:
        for field in _ENGINEERING_DESIGN_TEXT_FIELDS:
            engineering_design[field] = next(it)
        for action in engineering_design.get("actions") or []:
            for field in _ACTION_TEXT_FIELDS:
                action[field] = next(it)
    return title, abstract_or_summary, engineering_design


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
    extraction_meta: dict[str, Any] = {}
    agent_trace: list[dict[str, Any]] = []
    experimental_design: list[dict[str, Any]] = []
    evidence_provenance: list[dict[str, Any]] = []
    evidence_graph: dict[str, Any] = {"nodes": [], "edges": []}
    header_summary = {"status": "pending", "evidence_confidence": None, "human_review_status": None}
    if source != "crossref":
        extraction_meta = raw.get("extraction_meta", {}) or {}
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
        # Dual-track Evidence Reasoning View (prompt/小组件_模块/论文实验设计思路的抽取/
        # 抽取详情页面.md): reshapes the same DDR record's decision_chain/
        # engineering_problem/biological_diagnosis/engineering_hypothesis -
        # present on every DDR-v2 record, hand-curated or pipeline-generated -
        # into a synchronized agent-reasoning-trace + experimental-design-
        # reconstruction pair, independent of paper_extraction_detail.
        experimental_design = build_experimental_design(raw)
        agent_trace = build_agent_trace(raw)
        evidence_provenance = build_evidence_provenance(raw)
        evidence_graph = build_evidence_graph(experimental_design)
        header_summary = build_header_summary(raw, has_design=bool(experimental_design))
    title, abstract_or_summary, engineering_design = _localize_evidence_document(
        doc.title, doc.abstract_or_summary, engineering_design,
    )
    return {
        "source_id": doc.source_id, "title": title, "authors": doc.authors, "publication_year": doc.publication_year,
        "journal_or_repository": doc.journal_or_repository, "doi_or_accession": doc.doi_or_accession, "url": doc.url,
        "abstract_or_summary": abstract_or_summary, "engineering_design": engineering_design,
        # Present only for DDRs auto-saved from a paper_extraction run
        # (harness/paper_extraction/ddr_converter.py::ensure_task_saved_as_evidence) -
        # None for hand-curated DDRs that predate that pipeline. This is the
        # agent's own parsing reasoning + evidence-bound design fields, kept
        # separate from `engineering_design` (the curated decision-chain view).
        "paper_extraction_detail": extraction_meta.get("paper_extraction_detail"),
        "extraction_task_id": extraction_meta.get("paper_extraction_task_id"),
        "agent_trace": agent_trace,
        "experimental_design": experimental_design,
        "evidence_provenance": evidence_provenance,
        "evidence_graph": evidence_graph,
        "status": header_summary["status"],
        "evidence_confidence": header_summary["evidence_confidence"],
        "human_review_status": header_summary["human_review_status"],
        # Dual-annotator calibration state (harness/paper_extraction/
        # calibration.py, 老师 §4.3 step 3) - None/0/[] for crossref
        # documents and for DDRs no second attempt has ever been recorded
        # against yet.
        "calibration_status": extraction_meta.get("calibration_status"),
        "conflict_count": extraction_meta.get("conflict_count", 0),
        "extraction_attempts": [
            {"annotator": a.get("annotator"), "recorded_at": a.get("recorded_at"), "step_count": len(a.get("decision_chain") or [])}
            for a in extraction_meta.get("extraction_attempts", []) or []
        ],
        # Full underlying DDR record, for the detail page's "Download
        # Extraction JSON" action - never fabricated for crossref documents
        # that have no such record.
        "raw_record": raw if source != "crossref" else None,
    }


class AssessApplicabilityBody(BaseModel):
    project_id: str
    actor_id: str = "frontend-user"


@router.post("/evidence/documents/{source_id}/applicability")
def assess_applicability(source_id: str, body: AssessApplicabilityBody, session: Session = Depends(get_db_session)) -> dict:
    """Computes + persists a DDR's "Applicability Report" against a
    project's current context (老师 §Phase3). `source_id` must be a
    `local_ddr` document - crossref bibliographic records have no
    `metadata.organism`/`target_product` to compare against."""
    project = session.get(Project, body.project_id)
    if project is None:
        raise HTTPException(404, f"no such project: {body.project_id}")
    doc = LocalDDRAdapter().fetch(source_id)
    if doc is None:
        raise HTTPException(404, f"no such local_ddr document: {source_id}")
    return assess_ddr_applicability(session, project_id=body.project_id, ddr_record=doc.raw_metadata, project=project, actor_id=body.actor_id)


@router.get("/evidence/match-reports")
def list_match_reports(evidence_id: str | None = None, project_id: str | None = None, session: Session = Depends(get_db_session)) -> dict:
    """`project_id` scopes the list to one project's own match reports -
    without it (and without `evidence_id`) this previously returned every
    match report ever computed, for every project, since the table was
    created (the Knowledge page's "适用范围/情境匹配报告" panel called this
    with no filter at all, so it never reflected the open project). When
    `project_id` is given without a specific `evidence_id`, only the most
    recent report per evidence_id is returned - `EvidenceMatchReport` rows
    are immutable/append-only (harness/db.py::guard_immutable_fields), so
    re-assessing the same DDR against the same project inserts a new row
    rather than updating the old one, and this view is "current status per
    piece of evidence", not a full audit trail (the full history is still
    available by filtering on a specific `evidence_id`)."""
    stmt = select(EvidenceMatchReport).order_by(EvidenceMatchReport.created_at.desc())
    if evidence_id:
        stmt = stmt.where(EvidenceMatchReport.evidence_id == evidence_id)
    if project_id:
        stmt = stmt.where(EvidenceMatchReport.project_id == project_id)
    rows = list(session.execute(stmt).scalars().all())
    if project_id and not evidence_id:
        seen: set[str] = set()
        deduped = []
        for r in rows:
            if r.evidence_id in seen:
                continue
            seen.add(r.evidence_id)
            deduped.append(r)
        rows = deduped
    return {
        "match_reports": [
            {"match_report_id": r.match_report_id, "evidence_id": r.evidence_id, "organism_match": r.organism_match,
             "strain_match": r.strain_match, "genotype_match": r.genotype_match, "medium_match": r.medium_match,
             "condition_match": r.condition_match, "timepoint_match": r.timepoint_match, "intervention_match": r.intervention_match,
             "measurement_match": r.measurement_match, "overall_match_status": r.overall_match_status,
             "downgrade_reasons": r.downgrade_reasons, "transfer_risks": r.transfer_risks, "directness": r.directness, "created_at": r.created_at}
            for r in rows
        ]
    }

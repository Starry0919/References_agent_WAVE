"""Paper Experimental Design Extraction module API routes.

Wraps the vendored 13-skill pipeline (harness/paper_extraction/) - requirement
parsing, literature retrieval, citation validation, PDF acquisition/parsing,
markdown cleaning, experiment extraction, evidence binding, quality
evaluation, K12 transfer analysis, engineering proposal, QC/human review and
frontend adaptation. Runs are async (thread-pool backed, PDF download/parsing
can take a while) - submit, then poll the combined status+result endpoint.

Independent of the project ledger DB (harness/db.py): the module keeps its
own file-based checkpoint/artifact store under
harness/paper_extraction/vendor/paper_experimental_design_extraction/storage/,
matching the simulation_demo precedent of a self-contained sub-system that
never touches the real ledger.
"""
from __future__ import annotations

import base64
import logging
from typing import Any, Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from harness.api.deps import get_db_session
from harness.evidence_retrieval.local_ddr_adapter import LocalDDRAdapter
from harness.evidence_retrieval.relevance import product_search_variants
from harness.paper_extraction import service
from harness.paper_extraction.calibration import get_conflicts, record_extraction_attempt
from harness.paper_extraction.ddr_converter import ensure_task_saved_as_evidence
from harness.paper_extraction.engineering_actions_catalog import search_engineering_actions
from harness.paper_extraction.result_summary import build_extraction_summary
from harness.paper_extraction.rule_distillation import (
    distill_rules,
    rule_as_knowledge_claim_view,
    rule_source_ddr_ids,
    rules_citing_ddr_ids,
    search_rules,
)
from harness.projects.models import Project

router = APIRouter(prefix="/api/paper-extraction", tags=["paper-extraction"])
logger = logging.getLogger(__name__)


def _rule_relevance(rule: dict[str, Any], *, project_product: str | None, project_product_variants: list[str] | None = None) -> bool:
    """A rule is "relevant" to a project's target product when at least one
    of its cited *source DDRs* was itself about that product
    (`metadata.target_product`) - not the rule's own statement text, which
    is deliberately abstracted away from any one product (老师 §四.5: a
    rule distilled from butanol is meant to transfer to fatty acids, so its
    wording never names a specific product to match against). Never used
    to hide rules, only to rank/tag. `project_product_variants` (see
    `product_search_variants`) lets a caller precompute the zh/en
    translation once per request instead of per rule/DDR; omitting it falls
    back to matching on `project_product` alone."""
    if not project_product:
        return False
    variants = [v.strip().lower() for v in (project_product_variants or [project_product]) if v and v.strip()]
    adapter = LocalDDRAdapter()
    for ddr_id in rule_source_ddr_ids(rule):
        doc = adapter.fetch(ddr_id)
        if doc is None:
            continue
        ddr_product = str((doc.raw_metadata or {}).get("metadata", {}).get("target_product", "")).strip().lower()
        if ddr_product and any(pp in ddr_product or ddr_product in pp for pp in variants):
            return True
    return False


class RunRequestBody(BaseModel):
    project_id: str | None = None
    user_request: str
    organism: str = ""
    strain: str = ""
    source_type: Literal["auto_search", "upload", "doi", "textbook"] = "auto_search"
    result_level: Literal["extract", "compare", "adapt", "engineering_plan"] = "extract"
    document_kind: Literal["auto", "paper", "textbook"] = "auto"
    files: list[str] = Field(default_factory=list)
    doi: list[str] = Field(default_factory=list)
    requirements: dict[str, Any] = Field(default_factory=dict)
    automatic: bool = True
    human_review: bool = True
    max_papers: int = Field(default=6, ge=1, le=8)


class UploadBody(BaseModel):
    filename: str
    content_base64: str


@router.post("/uploads")
def upload_paper(body: UploadBody) -> dict:
    # base64-in-JSON, not multipart (harness/api/experiments.py precedent):
    # keeps this router dependency-free (no python-multipart requirement).
    try:
        data = base64.b64decode(body.content_base64)
    except Exception as exc:
        raise HTTPException(400, f"content_base64 is not valid base64: {exc}") from exc
    if not data:
        raise HTTPException(422, "uploaded file is empty")
    path = service.save_upload(body.filename, data)
    return {"path": path, "filename": body.filename}


@router.post("/tasks", status_code=202)
def submit_task(body: RunRequestBody) -> dict:
    try:
        return service.submit_run(body.model_dump())
    except Exception as exc:  # invalid request shape against the module's own input schema
        raise HTTPException(400, str(exc)) from exc


@router.get("/tasks")
def list_tasks(project_id: str | None = Query(default=None)) -> dict:
    """Run history (newest first) - lets the page show past/in-progress
    runs instead of resetting to a blank submission form whenever the
    `?task=` URL param is lost (navigating away and back, a fresh tab)."""
    return {"tasks": service.list_tasks(project_id=project_id)}


@router.get("/tasks/{task_id}")
def get_task(task_id: str) -> dict[str, Any]:
    """Combined status+result poll target: `result` stays null while the
    task is still running so the frontend can poll one endpoint uniformly
    instead of juggling a 202-vs-200 status/result split.

    `skill_states` is included at the top level too (not just inside
    `result`, which is only ever populated once the whole run finishes) -
    it's read from the run's on-disk checkpoint, updated after every skill,
    so a client polling this endpoint can show live per-step progress
    instead of an undifferentiated spinner for the whole run.

    `extraction_summary` is a clear, per-paper view of what the agent
    extracted (its own reasoning about article type / target strains,
    separate from the paper's evidence-verified experimental design
    content) - built straight from the checkpoint (see
    `harness.paper_extraction.result_summary`), so it is available
    regardless of `result_level` (skill13's engineering-plan-shaped
    `frontend_view` only runs for `result_level="engineering_plan"`) and
    regardless of whether independent human review has looked at it yet.
    """
    try:
        status = service.get_status(task_id)
    except KeyError:
        raise HTTPException(404, "task not found")
    result = service.get_result(task_id)
    skill_states = result["skill_states"] if result else service.get_live_skill_states(task_id)
    # Only meaningful while still running - a finished result has nothing left
    # in progress, and the engine never puts `skill_progress` in `_report()`.
    skill_progress = {} if result else service.get_live_skill_progress(task_id)
    # Per-skill warning detail (why a step is WARNING, not just that it is) -
    # same live-checkpoint-vs-finished-result split as `skill_states` above.
    skill_warnings = result.get("warnings", []) if result else service.get_live_skill_warnings(task_id)
    extraction_summary = build_extraction_summary(task_id)
    if extraction_summary:
        for paper in extraction_summary["papers"]:
            paper["evidence_source_id"] = None
        # Requirement: a paper's extraction record should be saved into
        # "文献证据" (Literature Evidence) once it finishes - triggered here
        # since this is the endpoint the frontend already polls to
        # completion; idempotent, so repeated polls/re-opens don't re-save.
        if status.get("status") == "completed":
            try:
                saved = ensure_task_saved_as_evidence(task_id)
                saved_by_index = {s["paper_index"]: s["evidence_source_id"] for s in saved}
                for i, paper in enumerate(extraction_summary["papers"]):
                    paper["evidence_source_id"] = saved_by_index.get(i)
            except Exception:
                logger.exception("failed to save task %s as literature evidence", task_id)
    return {
        **status, "result": result, "skill_states": skill_states, "skill_progress": skill_progress,
        "skill_warnings": skill_warnings, "extraction_summary": extraction_summary,
    }


@router.get("/rules")
def search_rules_route(query: str = "", project_id: str | None = None, session: Session = Depends(get_db_session)) -> dict[str, Any]:
    """Rule-library keyword search (老师 §4.5/§5.3: 自建 DB "规则库") -
    previously nothing in the codebase read ``knowledge/biological_rules/
    rules.json`` at all; an empty query returns every rule. Optional
    `project_id` tags each rule `relevant` (target-product text overlap)
    and sorts relevant-first, without hiding the rest (老师 §Phase5)."""
    rules = search_rules(query)
    if project_id:
        project = session.get(Project, project_id)
        project_product = project.target_product if project is not None else None
        project_product_variants = product_search_variants(project_product)
        for r in rules:
            r["relevant"] = _rule_relevance(r, project_product=project_product, project_product_variants=project_product_variants)
        rules.sort(key=lambda r: not r["relevant"])
    return {"rules": rules, "total": len(rules)}


@router.get("/knowledge-claims")
def list_knowledge_claims_from_rules(query: str = "", project_id: str | None = None, session: Session = Depends(get_db_session)) -> dict[str, Any]:
    """DDR-backed Knowledge Claims (老师 §Phase4): each rule-library entry
    reshaped into claim/evidence/confidence/boundary, since the rule
    library already IS the "多个 DDR 支持的可迁移知识" aggregation - see
    `rule_as_knowledge_claim_view`'s docstring for why this reuses the rule
    library instead of a new claim schema. Distinct from
    `/api/learning/knowledge-claims` (harness/learning/models.py), which
    aggregates wet-lab *experiment runs*, not literature DDRs - the two are
    genuinely different objects that happen to share the English name
    "Knowledge Claim"; this route is intentionally under `paper-extraction`
    (the DDR/rule pipeline's own namespace) to keep them apart."""
    rules = search_rules(query)
    claims = [rule_as_knowledge_claim_view(r) for r in rules]
    if project_id:
        project = session.get(Project, project_id)
        project_product = project.target_product if project is not None else None
        project_product_variants = product_search_variants(project_product)
        for rule, claim in zip(rules, claims):
            claim["relevant"] = _rule_relevance(rule, project_product=project_product, project_product_variants=project_product_variants)
        claims.sort(key=lambda c: not c.get("relevant", False))
    return {"claims": claims, "total": len(claims)}


@router.get("/engineering-actions")
def search_engineering_actions_route(query: str = "") -> dict[str, Any]:
    """Keyword search over `knowledge/engineering_actions/action_database.json`
    (老师 §四.5/§5.3: 自建 DB "工程操作库") - the third knowledge-base
    category, alongside `/rules` (biological rules) and the DDR database
    (browsable today via `/api/generation/evidence/search?source=local_ddr`).
    Empty
    query returns every action (full browse)."""
    actions = search_engineering_actions(query)
    return {"actions": actions, "total": len(actions)}


@router.post("/rules/distill")
def distill_rules_route(write: bool = False) -> dict[str, Any]:
    """Scan the DDR knowledge base for eligible rule-bearing decision-chain
    steps not yet represented in the rule library, and (if `write`) append
    them as new pending-calibration entries. Never touches DDR-001..005's
    already hand-distilled RULE-001..009 — see rule_distillation.py's
    module docstring for why."""
    candidates = distill_rules(write=write)
    return {"new_candidates": candidates, "written": write}


class ExtractionAttemptBody(BaseModel):
    annotator: str
    decision_chain: list[dict[str, Any]]


@router.post("/ddr/{ddr_id}/attempts")
def submit_extraction_attempt(ddr_id: str, body: ExtractionAttemptBody) -> dict[str, Any]:
    """Record one annotator's independent decision_chain draft for a saved
    DDR (老师 §4.3 step 3: dual independent extraction → conflict detection
    → calibration). Two attempts recorded here is what makes
    GET .../conflicts below meaningful — a single attempt has nothing to
    compare against."""
    try:
        return record_extraction_attempt(ddr_id, body.annotator, body.decision_chain)
    except FileNotFoundError as exc:
        raise HTTPException(404, str(exc)) from exc


@router.get("/ddr/{ddr_id}/conflicts")
def get_extraction_conflicts(ddr_id: str) -> dict[str, Any]:
    try:
        conflicts = get_conflicts(ddr_id)
    except FileNotFoundError as exc:
        raise HTTPException(404, str(exc)) from exc
    return {"ddr_id": ddr_id, "conflicts": conflicts, "total": len(conflicts)}


@router.get("/ddr/{ddr_id}/provenance")
def get_ddr_provenance(ddr_id: str) -> dict[str, Any]:
    """Trust & Provenance minimal closure (老师 §Phase5 Round 2): the full,
    non-fabricated "why do we believe this" chain for one DDR - Design
    Action -> Rule -> DDR -> Paper -> Evidence Grade. Built entirely from
    data that already exists (the DDR record itself + `rules.json` via
    `rules_citing_ddr_ids`) - no new schema, no synthesized text. This is
    the one endpoint both the DDR Applicability Report (`matching_factors`)
    and a future Trust Center page can point at, so the resolution logic
    lives in exactly one place."""
    doc = LocalDDRAdapter().fetch(ddr_id)
    if doc is None:
        raise HTTPException(404, f"no such DDR: {ddr_id}")
    rec = doc.raw_metadata or {}
    decision_chain = rec.get("decision_chain", [])

    design_actions = sorted({step.get("design_action") for step in decision_chain if step.get("design_action")})
    evidence_grades = sorted({step.get("evidence_grading") for step in decision_chain if step.get("evidence_grading")})

    rule_ids = rules_citing_ddr_ids([ddr_id])
    rules_by_id = {r["rule_id"]: r for r in search_rules("")}
    rules = [rule_as_knowledge_claim_view(rules_by_id[rid]) for rid in rule_ids if rid in rules_by_id]

    hard = "硬" in evidence_grades
    if hard and len(rule_ids) >= 2:
        confidence = "high"
    elif hard or rule_ids:
        confidence = "medium"
    else:
        confidence = "low"

    return {
        "ddr_id": ddr_id,
        "paper": {
            "title": doc.title, "authors": doc.authors, "publication_year": doc.publication_year,
            "journal_or_repository": doc.journal_or_repository, "doi_or_accession": doc.doi_or_accession,
        },
        "design_actions": design_actions,
        "evidence_grades": evidence_grades,
        "rule_ids": rule_ids,
        "rules": rules,
        "confidence": confidence,
    }


@router.delete("/tasks/{task_id}")
def delete_task(task_id: str) -> dict[str, Any]:
    """Remove a finished run from history (both the list and its own
    detail poll target 404 afterwards) - lets the frontend's run-history
    panel offer a delete action instead of accumulating every past run
    forever."""
    try:
        service.delete_task(task_id)
    except KeyError:
        raise HTTPException(404, "task not found")
    except ValueError as exc:
        raise HTTPException(409, str(exc)) from exc
    return {"deleted": True, "task_id": task_id}

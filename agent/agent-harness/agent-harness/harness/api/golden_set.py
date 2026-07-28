"""Scientific Golden Set API routes (prompt §8.1: "运行 Golden Set
evaluation；查询 acceptance report"). Every route calls the same real
service/runner/scoring layer `tests/golden_set/` exercises.
"""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from harness.api.deps import get_db_session
from harness.golden_set import metrics as metrics_mod
from harness.golden_set import runner as runner_mod
from harness.golden_set import scoring as scoring_mod
from harness.golden_set import service as golden_service

router = APIRouter(prefix="/api/golden-set", tags=["golden-set"])


@router.post("/seed")
def seed(session: Session = Depends(get_db_session)) -> dict:
    rows = golden_service.seed_candidate_cases(session)
    return {"cases": [r.case_id for r in rows]}


@router.get("/cases")
def list_cases(session: Session = Depends(get_db_session)) -> dict:
    rows = golden_service.list_cases(session)
    return {"cases": [{"case_id": r.case_id, "title": r.title, "case_type": r.case_type} for r in rows]}


@router.get("/cases/{case_id}/review-status")
def review_status(case_id: str, session: Session = Depends(get_db_session)) -> dict:
    answer = golden_service.get_answer_key(session, case_id)
    if answer is None:
        raise HTTPException(404, f"no such case: {case_id}")
    return {"case_id": case_id, "review_status": answer.review_status, "expert_reviewers": answer.expert_reviewers}


class RunCaseBody(BaseModel):
    actor_id: str = "golden_set_api"
    llm_adapters_enabled: bool = False


@router.post("/cases/{case_id}/run")
def run_case(case_id: str, body: RunCaseBody, session: Session = Depends(get_db_session)) -> dict:
    try:
        run = runner_mod.run_golden_case(session, case_id, actor_id=body.actor_id, llm_adapters_enabled=body.llm_adapters_enabled)
    except ValueError as e:
        raise HTTPException(404, str(e))
    return {
        "evaluation_run_id": run.evaluation_run_id, "case_id": run.case_id, "system_output": run.system_output,
        "automated_metrics": run.automated_metrics, "errors": run.errors,
    }


@router.get("/runs/{evaluation_run_id}/score")
def score_run_route(evaluation_run_id: str, session: Session = Depends(get_db_session)) -> dict:
    try:
        return scoring_mod.score_run(session, evaluation_run_id)
    except ValueError as e:
        raise HTTPException(404, str(e))


class AcceptanceReportBody(BaseModel):
    evaluation_run_ids: list[str]


@router.post("/acceptance-report")
def acceptance_report(body: AcceptanceReportBody, session: Session = Depends(get_db_session)) -> dict:
    agg_metrics = metrics_mod.aggregate_metrics(session, body.evaluation_run_ids)
    agg_scores = scoring_mod.aggregate_scores(session, body.evaluation_run_ids)
    return {
        "cases_run": agg_metrics["cases_run"], "automated_metrics": agg_metrics, "scored_metrics": agg_scores,
        "formal_validation_eligible": agg_scores["formal_validation_eligible"],
        "note": "formal_validation_eligible=False means no case in this run set has been expert-reviewed yet - these results are software/system-behavior verification only, not scientific validation",
    }

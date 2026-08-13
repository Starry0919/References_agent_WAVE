"""Evaluation Intake Service (doc05 §4.1): validates the input is a real,
persisted `DesignPortfolio`/`CandidateDesign` (never free-text), freezes
`diagnosis`/`context`/`objectives`/`constraints`/`resources` into one
`EvaluationCase.frozen_context` snapshot so a mid-review condition change
can never silently redefine what is being reviewed, and builds the claim
inventory (`harness/scientific_evaluation/claims.py`) a Reviewer reads
instead of the Designer's own chain-of-thought.
"""
from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from harness.engineering_design.models import CandidateDesign, DesignPortfolio, EngineeringDesignProject
from harness.ids import new_id, now
from harness.memory import event_types as et
from harness.memory.event_store import append_event, snapshot
from harness.scientific_evaluation.models import EvaluationCase

CASE_SNAPSHOT_FIELDS = (
    "evaluation_id", "schema_version", "project_id", "design_project_id", "workflow_run_id",
    "diagnosis_reference", "portfolio_reference", "design_version_references", "frozen_context",
    "evaluation_mode", "status", "revision_round", "created_by", "created_at", "updated_at", "version",
)


class EvaluationIntakeError(ValueError):
    """The referenced portfolio/candidates do not yet constitute a real,
    evaluable `DesignVersion` - doc05 §4.1: "若输入只有自由文本基因列表,
    必须返回结构化 validation error...不能假装其已达到 evaluated/build-
    ready"."""


def _freeze_context(proj: EngineeringDesignProject) -> dict[str, Any]:
    return {
        "chassis": proj.chassis,
        "genotype": proj.chassis_version_or_genotype,
        "environment": proj.temporal_and_environmental_context,
        "temporal_scope": proj.temporal_and_environmental_context.get("experiment_time", "unknown"),
        "baseline": proj.baseline_state_id or "unknown",
        "objectives": {"primary_metrics": proj.primary_metrics, "secondary_metrics": proj.secondary_metrics},
        "hard_constraints": proj.hard_constraints,
        "resources": proj.available_resources,
        "diagnosis_version_at_freeze": proj.diagnosis_version,
    }


def open_evaluation_case(
    session: Session,
    *,
    portfolio_id: str,
    actor_id: str,
    evaluation_mode: str = "portfolio",
    diagnosis_reference: str | None = None,
    workflow_run_id: str | None = None,
) -> tuple[EvaluationCase, list[CandidateDesign]]:
    portfolio = session.get(DesignPortfolio, portfolio_id)
    if portfolio is None:
        raise EvaluationIntakeError(f"no such design portfolio: {portfolio_id}")
    if not portfolio.candidate_design_ids:
        raise EvaluationIntakeError(
            f"portfolio {portfolio_id} has no candidate designs yet - nothing structured to evaluate "
            "(a free-text gene list or bare strategy is not a build-ready DesignVersion)"
        )

    proj = session.get(EngineeringDesignProject, portfolio.design_project_id)
    if proj is None:
        raise EvaluationIntakeError(f"portfolio {portfolio_id} references an unknown design project")

    candidates = list(
        session.execute(select(CandidateDesign).where(CandidateDesign.portfolio_id == portfolio_id)).scalars()
    )
    if not candidates:
        raise EvaluationIntakeError(f"portfolio {portfolio_id} lists candidate ids but none resolve to real CandidateDesign rows")

    ts = now()
    case = EvaluationCase(
        evaluation_id=new_id("SEVAL"),
        schema_version="1",
        project_id=proj.project_id,
        design_project_id=proj.design_project_id,
        workflow_run_id=workflow_run_id,
        diagnosis_reference=diagnosis_reference,
        portfolio_reference=portfolio_id,
        design_version_references=[{"design_id": c.design_id, "design_version": c.design_version} for c in candidates],
        frozen_context=_freeze_context(proj),
        evaluation_mode=evaluation_mode,
        status="evaluation_pending",
        revision_round=0,
        created_by=actor_id,
        created_at=ts,
        updated_at=ts,
    )
    session.add(case)
    session.flush()
    append_event(
        session, project_id=proj.project_id, event_type=et.EVAL_CASE_OPENED, entity_type="EvaluationCase",
        entity_id=case.evaluation_id, payload=snapshot(case, CASE_SNAPSHOT_FIELDS), actor_type="agent", actor_id=actor_id,
    )
    return case, candidates


def get_case(session: Session, evaluation_id: str) -> EvaluationCase | None:
    return session.get(EvaluationCase, evaluation_id)


def detect_context_drift(case: EvaluationCase, proj: EngineeringDesignProject) -> bool:
    """doc05 §3.1: "条件改变必须创建新 evaluation/version,不得静默替换."
    True means the live project has moved on since this case froze its
    context - callers must open a new `EvaluationCase`, never keep using
    this one under a changed context."""
    frozen = case.frozen_context
    return (
        frozen.get("chassis") != proj.chassis
        or frozen.get("genotype") != proj.chassis_version_or_genotype
        or frozen.get("diagnosis_version_at_freeze") != proj.diagnosis_version
    )

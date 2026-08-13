"""Revision Controller (doc05 §4.9): turns blocking/major `CriticFinding`s
into structured `RevisionTask`s, and - when a revision is actually applied -
creates a NEW `CandidateDesign` version via `harness.engineering_design.
portfolio_service.revise_candidate` (never edits the reviewed row in place;
that function's own `guard_immutable_fields` would reject it anyway) plus
one `RevisionCycle` row recording what changed and which findings it
targeted. Stop conditions (doc05 §4.9) are evaluated by `check_stop_
conditions`, never silently ignored by the orchestrator.
"""
from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from harness.engineering_design import memory_integration, portfolio_service
from harness.engineering_design.models import CandidateDesign
from harness.ids import new_id, now
from harness.memory import event_types as et
from harness.memory.event_store import append_event
from harness.scientific_evaluation.models import CriticFinding, EvaluationCase, RevisionCycle, RevisionTask

_CATEGORY_TO_TASK_TYPE = {
    "weak_causal_link": "add_or_replace_evidence",
    "ineffective_intervention": "fix_design",
    "competing_explanation": "return_to_diagnosis",
    "evidence_not_transferable": "add_or_replace_evidence",
    "compensation_or_feedback_ignored": "run_model",
    "essentiality_or_fitness_risk": "fix_design",
    "buildability_or_stability": "reduce_complexity",
    "missing_control": "add_control",
    "falsifiability": "change_validation_plan",
    "safety_or_compliance": "human_adjudication",
}
_PRIORITY_FOR_SEVERITY = {"critical": "critical", "major": "high", "moderate": "medium", "minor": "low", "informational": "low"}


def generate_revision_tasks(
    session: Session, *, case: EvaluationCase, candidates: list[CandidateDesign], findings_by_design: dict[str, list[CriticFinding]],
) -> list[RevisionTask]:
    ts = now()
    tasks: list[RevisionTask] = []
    for c in candidates:
        actionable = [f for f in findings_by_design.get(c.design_id, []) if f.status == "open" and (f.blocking or f.severity in ("critical", "major"))]
        for f in actionable:
            task_type = _CATEGORY_TO_TASK_TYPE.get(f.category, "fix_design")
            task = RevisionTask(
                task_id=new_id("RTASK"), evaluation_id=case.evaluation_id, source_finding_id=f.finding_id,
                target_design_id=c.design_id, target_version=c.design_version, task_type=task_type,
                priority=_PRIORITY_FOR_SEVERITY.get(f.severity, "medium"), required_change=f.required_action or f.finding,
                acceptance_criteria=[f.falsification_condition] if f.falsification_condition else [],
                evidence_needed=[e for e in f.supporting_evidence] if task_type == "add_or_replace_evidence" else [],
                assigned_to="human" if task_type in ("human_adjudication", "return_to_diagnosis") else "designer",
                status="open", resolution_reference=None, created_at=ts,
            )
            session.add(task)
            tasks.append(task)
    session.flush()
    if tasks:
        append_event(
            session, project_id=case.project_id, event_type=et.EVAL_REVISION_TASKS_CREATED, entity_type="EvaluationCase",
            entity_id=case.evaluation_id, payload={"task_ids": [t.task_id for t in tasks], "task_types": [t.task_type for t in tasks]},
            actor_type="agent", actor_id="system",
        )
    return tasks


def apply_revision(
    session: Session, *, case: EvaluationCase, design_id: str, actor_id: str, modification_reason: str,
    genetic_modifications: list[dict[str, Any]] | None = None, regulatory_architecture: dict[str, Any] | None = None,
    process_modifications: list[dict[str, Any]] | None = None, expected_mechanism: str | None = None,
    causal_chain: list[str] | None = None, interaction_and_epistasis_assumptions: list[str] | None = None,
    task_ids: list[str] | None = None,
) -> tuple[RevisionCycle, CandidateDesign]:
    parent = session.get(CandidateDesign, design_id)
    if parent is None:
        raise ValueError(f"no such candidate design: {design_id}")

    old_sig = memory_integration.modification_signature(parent.genetic_modifications)
    new_candidate = portfolio_service.revise_candidate(
        session, design_id=design_id, actor_id=actor_id, modification_reason=modification_reason,
        genetic_modifications=genetic_modifications, regulatory_architecture=regulatory_architecture,
        process_modifications=process_modifications, expected_mechanism=expected_mechanism, causal_chain=causal_chain,
        interaction_and_epistasis_assumptions=interaction_and_epistasis_assumptions,
    )
    new_sig = memory_integration.modification_signature(new_candidate.genetic_modifications)
    changed_fields = []
    if new_sig != old_sig:
        changed_fields.append(f"genetic_modifications: {sorted(old_sig - new_sig)} removed, {sorted(new_sig - old_sig)} added")
    if expected_mechanism is not None and expected_mechanism != parent.expected_mechanism:
        changed_fields.append("expected_mechanism")
    if causal_chain is not None and causal_chain != parent.causal_chain:
        changed_fields.append("causal_chain")

    tasks = [session.get(RevisionTask, tid) for tid in (task_ids or [])]
    tasks = [t for t in tasks if t is not None]
    resolved_findings = []
    for t in tasks:
        t.status = "resolved"
        t.resolution_reference = new_candidate.design_id
        if t.source_finding_id:
            resolved_findings.append(t.source_finding_id)
    session.flush()

    cycle = RevisionCycle(
        cycle_id=new_id("RCYC"), evaluation_id=case.evaluation_id, from_design_id=parent.design_id,
        from_design_version=parent.design_version, revision_tasks=[t.task_id for t in tasks],
        to_design_id=new_candidate.design_id, to_design_version=new_candidate.design_version,
        changed_fields=changed_fields, resolved_findings=resolved_findings, unresolved_findings=[], new_findings=[],
        stop_reason=None, created_at=now(),
    )
    session.add(cycle)
    case.revision_round = case.revision_round + 1
    case.design_version_references = case.design_version_references + [{"design_id": new_candidate.design_id, "design_version": new_candidate.design_version}]
    session.flush()
    append_event(
        session, project_id=case.project_id, event_type=et.EVAL_REVISION_CYCLE_COMPLETED, entity_type="RevisionCycle",
        entity_id=cycle.cycle_id, payload={
            "cycle_id": cycle.cycle_id, "from_design_id": cycle.from_design_id, "to_design_id": cycle.to_design_id,
            "changed_fields": changed_fields, "resolved_findings": resolved_findings,
        }, actor_type="human" if actor_id != "system" else "agent", actor_id=actor_id,
    )
    return cycle, new_candidate


def check_stop_conditions(case: EvaluationCase, *, revision_limit: int = 3, no_improvement_rounds: int = 0) -> str | None:
    """doc05 §4.9: returns a `stop_reason` string once a real stop
    condition is met, or `None` to keep iterating - reaching the limit
    NEVER auto-approves, it routes to `held`/`human_review_required`."""
    if case.revision_round >= revision_limit:
        return f"revision_limit_reached ({case.revision_round}/{revision_limit}) - routing to human review, not auto-approving"
    if no_improvement_rounds >= 2:
        return "no_substantive_improvement_across_two_consecutive_rounds"
    return None

"""Orchestrating entry point (doc05's target data flow, §0/§6): Evaluation
Intake -> Deterministic Validation -> Evidence Quality/Transferability ->
Model/Tool Validation -> Independent Scientific Critique -> Multi-objective
Candidate Comparison -> Meta-review/Decision Synthesis -> (revision tasks
generated) -> awaiting Human Gate. Every step calls the real module that
owns that concern - this function only sequences them and drives
`EvaluationLoopController` through the matching states; it contains no
scientific judgment of its own.
"""
from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from harness.engineering_design.models import CandidateDesign, EngineeringDesignProject
from harness.scientific_evaluation import claims as claims_mod
from harness.scientific_evaluation import comparator, critic, deterministic
from harness.scientific_evaluation import diagnosis_return
from harness.scientific_evaluation import evidence as evidence_mod
from harness.scientific_evaluation import intake, memory, meta_review, model_eval, revision
from harness.scientific_evaluation.loop import EvaluationLoopController
from harness.scientific_evaluation.models import CriticFinding, EvaluationCase, MetaReviewDecision
from harness.workflow.gates import scientific_revision_gate

_loop = EvaluationLoopController()


def run_scientific_evaluation(
    session: Session, *, portfolio_id: str, actor_id: str, diagnosis_reference: str | None = None,
    revision_limit: int = 3, enable_llm_critic: bool = False, workflow_run_id: str | None = None,
) -> dict[str, Any]:
    case, candidates = intake.open_evaluation_case(
        session, portfolio_id=portfolio_id, actor_id=actor_id, diagnosis_reference=diagnosis_reference,
        workflow_run_id=workflow_run_id,
    )
    return continue_scientific_evaluation(session, evaluation_id=case.evaluation_id, actor_id=actor_id, revision_limit=revision_limit, enable_llm_critic=enable_llm_critic)


def continue_scientific_evaluation(
    session: Session, *, evaluation_id: str, actor_id: str, revision_limit: int = 3, enable_llm_critic: bool = False,
) -> dict[str, Any]:
    """Runs the full deterministic -> evidence -> model -> critique ->
    comparison -> meta-review pipeline for an `EvaluationCase` that is
    currently `evaluation_pending` (either freshly opened, or restarted
    after a revision - `EvaluationLoopController.restart_after_revision`
    always returns a case to this state, doc05 §6's "revision 后必须以新
    版本重新评审").

    `enable_llm_critic=False` by default (Phase C, 六大核心模块统一集成
    prompt Workstream 2): adding a live network/LLM call inside a function
    every pre-existing test in `tests/engineering_design`/`tests/
    scientific_evaluation`/`tests/orchestrator` already calls would silently
    turn 100+ offline deterministic tests into live-network tests - prompt
    §10.4 explicitly requires keeping those layers separate. Set True to
    also run `harness.scientific_evaluation.llm_critic_adapter.
    run_llm_critic_review` per candidate, purely additive to the
    deterministic generalist/domain critics."""
    case = session.get(EvaluationCase, evaluation_id)
    if case is None:
        raise ValueError(f"no such evaluation case: {evaluation_id}")
    proj = session.get(EngineeringDesignProject, case.design_project_id)
    candidates = [
        session.get(CandidateDesign, ref["design_id"])
        for ref in case.design_version_references
    ]
    candidates = [c for c in candidates if c is not None]

    _loop.start_deterministic_validation(session, case, actor_id=actor_id)
    claims_by_design: dict[str, list] = {}
    det_by_design: dict[str, list] = {}
    for c in candidates:
        claims_by_design[c.design_id] = claims_mod.extract_claims(session, evaluation_id=case.evaluation_id, candidate=c)
        det_by_design[c.design_id] = deterministic.run_deterministic_checks(session, case=case, candidate=c, claims=claims_by_design[c.design_id], proj=proj)

    _loop.start_evidence_review(session, case, actor_id=actor_id)
    evidence_by_design = {
        c.design_id: evidence_mod.assess_evidence(session, case=case, candidate=c, claims=claims_by_design[c.design_id])
        for c in candidates
    }

    _loop.start_model_review(session, case, actor_id=actor_id)
    models_by_design = {c.design_id: model_eval.assess_model_records(session, case=case, candidate=c) for c in candidates}

    _loop.start_scientific_review(session, case, actor_id=actor_id)
    reviews_by_design = {
        c.design_id: critic.run_all_reviews(
            session, case=case, candidate=c, claims=claims_by_design[c.design_id], evidence=evidence_by_design[c.design_id],
            models=models_by_design[c.design_id], deterministic=det_by_design[c.design_id],
        )
        for c in candidates
    }
    if enable_llm_critic:
        from harness.scientific_evaluation.llm_critic_adapter import run_llm_critic_review

        for c in candidates:
            llm_review = run_llm_critic_review(
                session, case=case, candidate=c, claims=claims_by_design[c.design_id], evidence=evidence_by_design[c.design_id],
                models=models_by_design[c.design_id], deterministic=det_by_design[c.design_id], actor_id=actor_id,
            )
            if llm_review is not None:
                reviews_by_design[c.design_id].append(llm_review)
    findings_by_design: dict[str, list] = {}
    for design_id, reviews in reviews_by_design.items():
        review_ids = [r.review_id for r in reviews]
        findings_by_design[design_id] = list(
            session.execute(select(CriticFinding).where(CriticFinding.review_id.in_(review_ids))).scalars()
        ) if review_ids else []

    _loop.start_candidate_comparison(session, case, actor_id=actor_id)
    vectors = comparator.build_candidate_evaluation_vectors(
        session, case=case, proj=proj, candidates=candidates, evidence_by_design=evidence_by_design, findings_by_design=findings_by_design,
    )
    vectors_by_design = {v.candidate_id: v for v in vectors}

    _loop.start_meta_review(session, case, actor_id=actor_id)
    revision_tasks = revision.generate_revision_tasks(session, case=case, candidates=candidates, findings_by_design=findings_by_design)
    meta_decision = meta_review.synthesize_meta_review(
        session, case=case, candidates=candidates, reviews_by_design=reviews_by_design, findings_by_design=findings_by_design,
        vectors_by_design=vectors_by_design, revision_tasks=revision_tasks,
    )

    open_blocking = [
        f.finding_id for lst in findings_by_design.values() for f in lst
        if f.blocking and f.status == "open"
    ]
    gate = scientific_revision_gate(open_blocking_findings=open_blocking, revision_round=case.revision_round, revision_limit=revision_limit)
    _loop.complete_meta_review(session, case, actor_id=actor_id, revision_gate_result=gate)

    for c in candidates:
        review_recs = {r.recommendation for r in reviews_by_design.get(c.design_id, [])}
        memory.record_memory_event(
            session, case=case, design_id=c.design_id, design_version=c.design_version,
            event_type="scientific_evaluation_completed",
            raw_feedback_references=[a.assessment_id for a in evidence_by_design.get(c.design_id, [])],
            critic_findings=[f.finding_id for f in findings_by_design.get(c.design_id, [])],
            lesson=f"meta-review recommended_action={meta_decision.recommended_action!r} for evaluation {case.evaluation_id}; "
                   f"per-reviewer recommendations for this candidate: {sorted(review_recs)}",
            interpretation_uncertainty=meta_decision.decision_confidence,
        )

    return {
        "case": case, "candidates": candidates, "claims_by_design": claims_by_design, "deterministic_by_design": det_by_design,
        "evidence_by_design": evidence_by_design, "models_by_design": models_by_design, "reviews_by_design": reviews_by_design,
        "findings_by_design": findings_by_design, "vectors": vectors, "revision_tasks": revision_tasks,
        "meta_decision": meta_decision, "revision_gate": gate,
    }


def apply_revision_and_reevaluate(
    session: Session, *, evaluation_id: str, design_id: str, actor_id: str, modification_reason: str,
    task_ids: list[str] | None = None, revision_limit: int = 3, **revision_kwargs: Any,
) -> dict[str, Any]:
    """doc05 §4.9/§6: applies a revision (new `CandidateDesign` version via
    `revision.apply_revision`), checks the doc05 §4.9 stop conditions
    BEFORE spending another full pipeline pass, and - if not stopped -
    restarts the case (`EvaluationLoopController.restart_after_revision`)
    and re-runs the whole pipeline so the new version is judged fresh, not
    patched onto stale findings."""
    case = session.get(EvaluationCase, evaluation_id)
    if case is None:
        raise ValueError(f"no such evaluation case: {evaluation_id}")

    stop_reason = revision.check_stop_conditions(case, revision_limit=revision_limit)
    if stop_reason is not None:
        return {"case": case, "stopped": True, "stop_reason": stop_reason}

    cycle, new_candidate = revision.apply_revision(
        session, case=case, design_id=design_id, actor_id=actor_id, modification_reason=modification_reason,
        task_ids=task_ids, **revision_kwargs,
    )
    _loop.restart_after_revision(session, case, actor_id=actor_id)
    result = continue_scientific_evaluation(session, evaluation_id=case.evaluation_id, actor_id=actor_id, revision_limit=revision_limit)
    result["revision_cycle"] = cycle
    result["new_candidate"] = new_candidate
    return result


def initiate_diagnosis_return(session: Session, *, evaluation_id: str, design_id: str, actor_id: str) -> Any:
    """Convenience wrapper called after a `HumanEvaluationDecision(decision=
    "return_to_diagnosis")` (or directly, e.g. from an API handler) - reads
    the case's own `MetaReviewDecision`/`CriticFinding`s for the real
    triggering findings and alternative explanations rather than asking the
    caller to re-supply them."""
    case = session.get(EvaluationCase, evaluation_id)
    if case is None:
        raise ValueError(f"no such evaluation case: {evaluation_id}")
    candidate = session.get(CandidateDesign, design_id)
    if candidate is None:
        raise ValueError(f"no such candidate design: {design_id}")

    latest_decision = session.execute(
        select(MetaReviewDecision).where(MetaReviewDecision.evaluation_id == evaluation_id).order_by(MetaReviewDecision.created_at.desc())
    ).scalars().first()
    findings = session.execute(
        select(CriticFinding).where(CriticFinding.design_reference == design_id, CriticFinding.category == "competing_explanation")
    ).scalars().all()

    return diagnosis_return.create_diagnosis_return_request(
        session, case=case, candidate=candidate, actor_id=actor_id,
        triggering_findings=[f.finding_id for f in findings] or (latest_decision.blocking_findings if latest_decision else []),
        alternative_explanations=[alt for f in findings for alt in f.alternative_explanations],
        requested_discriminating_information=[f.falsification_condition for f in findings if f.falsification_condition],
    )

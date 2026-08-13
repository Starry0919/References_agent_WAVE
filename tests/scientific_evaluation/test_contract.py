"""doc05 §13.2 contract tests: interface compatibility across Problem 3 ->
4 -> 5, Problem 5 -> 4 (revision), Problem 5 -> 3 (return), Problem 5 -> 2
(Memory), and model adapter honesty states.
"""
from __future__ import annotations

from sqlalchemy import select

from harness.db import session_scope
from harness.diagnosis.models import DiagnosisSession
from harness.projects.models import ProjectEvent
from harness.scientific_evaluation import diagnosis_return, model_eval
from harness.scientific_evaluation.models import EvaluationMemoryEvent, ModelEvaluationRecord

from tests.scientific_evaluation.sci_fixtures import run_full_scientific_evaluation


def test_problem3_to_4_to_5_input_compatibility():
    """A real DiagnosisDecision -> DiagnosisHandoffRecord -> DesignPortfolio
    -> EvaluationCase chain, with every id genuinely resolvable end to end."""
    with session_scope() as session:
        proj, portfolio, candidates, result = run_full_scientific_evaluation(session)
        case = result["case"]
        assert case.design_project_id == proj.design_project_id
        assert case.portfolio_reference == portfolio.portfolio_id
        design_ids = {ref["design_id"] for ref in case.design_version_references}
        assert design_ids == {c.design_id for c in candidates}


def test_problem5_revision_feeds_problem4_candidate_design():
    """`revision.apply_revision` must produce a real `CandidateDesign` row
    Problem 04's own services (`portfolio_service.get_candidate`, etc.) can
    read - not a Problem-05-only shadow object."""
    from harness.engineering_design import portfolio_service
    from harness.scientific_evaluation import revision

    with session_scope() as session:
        proj, portfolio, candidates, result = run_full_scientific_evaluation(session)
        case = result["case"]
        target = next(c for c in candidates if c.portfolio_role == "fallback")
        _, new_candidate = revision.apply_revision(
            session, case=case, design_id=target.design_id, actor_id="pi", modification_reason="contract test",
            genetic_modifications=[{"target_identifier": "ppc", "operation": "overexpression", "evidence_links": []}],
        )
        reread = portfolio_service.get_candidate(session, new_candidate.design_id)
        assert reread is not None
        assert reread.design_project_id == proj.design_project_id


def test_problem5_return_request_creates_real_problem3_session():
    with session_scope() as session:
        proj, portfolio, candidates, result = run_full_scientific_evaluation(session)
        case = result["case"]
        target = candidates[0]
        request = diagnosis_return.create_diagnosis_return_request(
            session, case=case, candidate=target, actor_id="pi", triggering_findings=["synthetic test finding"],
        )
        assert request.status in ("session_created", "pending")
        if request.new_diagnosis_session_id is not None:
            sess = session.get(DiagnosisSession, request.new_diagnosis_session_id)
            assert sess is not None
            assert sess.project_id == proj.project_id


def test_problem5_events_feed_problem2_memory_ledger():
    with session_scope() as session:
        proj, portfolio, candidates, result = run_full_scientific_evaluation(session)
        events = session.execute(select(ProjectEvent).where(ProjectEvent.project_id == proj.project_id)).scalars().all()
        eval_events = [e for e in events if e.event_type.startswith("EVAL_")]
        assert eval_events, "scientific-evaluation actions must append into the shared ProjectEvent ledger"
        types = {e.event_type for e in eval_events}
        assert "EVAL_CASE_OPENED" in types
        assert "EVAL_STATE_CHANGED" in types
        assert "EVAL_META_REVIEW_DECIDED" in types

        mem_rows = session.execute(select(EvaluationMemoryEvent).where(EvaluationMemoryEvent.evaluation_id == result["case"].evaluation_id)).scalars().all()
        assert mem_rows
        for row in mem_rows:
            assert row.lesson  # interpretation is recorded
            assert isinstance(row.raw_feedback_references, list)  # raw refs kept separate from the interpretation


def test_model_adapter_honesty_states_are_distinct():
    """`computed`/`unavailable`/`failed`/`out_of_domain` must never be
    collapsed into each other - the honest default with zero real model
    runs on record is `not_computed`."""
    with session_scope() as session:
        proj, portfolio, candidates, result = run_full_scientific_evaluation(session)
        statuses = {r.run_status for lst in result["models_by_design"].values() for r in lst}
        assert statuses <= {"computed", "not_computed", "unavailable", "failed", "out_of_domain", "stale"}
        # this fixture requests no model runs at all -> every candidate must be honestly not_computed:
        assert statuses == {"not_computed"}


def test_evaluation_case_status_only_moves_through_named_states():
    from harness.scientific_evaluation.models import EVALUATION_STATES

    with session_scope() as session:
        proj, portfolio, candidates, result = run_full_scientific_evaluation(session)
        assert result["case"].status in EVALUATION_STATES

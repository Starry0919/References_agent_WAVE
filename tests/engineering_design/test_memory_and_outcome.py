"""doc04 §13.6: Memory / DBTL integration - events, history, outcome
ingestion, residuals, failure classification, next iteration / reopen / stop."""
from __future__ import annotations

from sqlalchemy import select

from harness import db
from harness.engineering_design import build_test_planner, governance_service, memory_integration, outcome_service
from harness.engineering_design.evaluation_service import evaluate_portfolio
from harness.learning.models import FailureCase
from harness.memory import event_types as et
from harness.projects.models import ProjectEvent
from tests.engineering_design.fixtures import handoff_through_portfolio


def _approved_candidate(s):
    proj, portfolio, candidates = handoff_through_portfolio(s)
    result = evaluate_portfolio(s, portfolio_id=portfolio.portfolio_id, actor_id="system")
    selected_id = result["decision"]["selected_design_ids"][0]
    candidate = next(c for c in candidates if c.design_id == selected_id)
    governance_service.request_human_approval(s, design_project_id=proj.design_project_id, actor_id="system")
    _, cand, proj2 = governance_service.record_human_decision(s, design_id=candidate.design_id, approver_id="pi_lead", decision="approved")
    build_test_planner.draft_build_test_package(
        s, design_id=candidate.design_id, actor_id="pi", construction_concept="x", required_materials=["m"],
        controls=[{"a": 1}], replication_plan={"n": 3}, sampling_plan=[{"t": 1}], qc_checkpoints=["qc"], decision_rules=["rule"],
    )
    governance_service.mark_planning_complete(s, design_project_id=proj.design_project_id, actor_id="system")
    governance_service.start_build(s, design_project_id=proj2.design_project_id, design_id=candidate.design_id, actor_id="tech")
    proj3 = governance_service.mark_test_pending(s, design_project_id=proj2.design_project_id, actor_id="tech")
    return proj3, cand


def test_every_decision_forms_a_project_event():
    with db.session_scope() as s:
        proj, portfolio, candidates = handoff_through_portfolio(s)
        events = s.execute(select(ProjectEvent).where(ProjectEvent.project_id == proj.project_id)).scalars().all()
        types = {e.event_type for e in events}
        assert et.DESIGN_PROJECT_CREATED in types
        assert et.DESIGN_HANDOFF_INGESTED in types
        assert et.DESIGN_STRATEGY_GENERATED in types
        assert et.DESIGN_CANDIDATE_GENERATED in types
        assert et.DESIGN_PORTFOLIO_GENERATED in types


def test_old_design_versions_are_never_overwritten():
    with db.session_scope() as s:
        proj, portfolio, candidates = handoff_through_portfolio(s)
        low_risk = next(c for c in candidates if c.portfolio_role == "low_risk")
        evaluate_portfolio(s, portfolio_id=portfolio.portfolio_id, actor_id="system")
        original_id = low_risk.design_id
        original_mods = list(low_risk.genetic_modifications)

        from harness.engineering_design import portfolio_service

        portfolio_service.reject_candidate(s, design_id=low_risk.design_id, reasons=["too risky"], actor_id="pi")
        # regenerate - the rejected row must still exist, unmodified
        portfolio_service.generate_and_persist_portfolio(s, design_project_id=proj.design_project_id, actor_id="system")

        reloaded = portfolio_service.get_candidate(s, original_id)
        assert reloaded is not None
        assert reloaded.genetic_modifications == original_mods
        assert reloaded.status == "rejected"


def test_history_read_before_next_round_shows_rejection_reasons():
    with db.session_scope() as s:
        proj, portfolio, candidates = handoff_through_portfolio(s)
        low_risk = next(c for c in candidates if c.portfolio_role == "low_risk")
        evaluate_portfolio(s, portfolio_id=portfolio.portfolio_id, actor_id="system")
        from harness.engineering_design import portfolio_service

        portfolio_service.reject_candidate(s, design_id=low_risk.design_id, reasons=["excessive growth burden"], actor_id="pi")
        history = memory_integration.design_lineage_history(s, design_project_id=proj.design_project_id)
        entry = next(h for h in history if h["design_id"] == low_risk.design_id)
        assert entry["status"] == "rejected"
        assert entry["rejection_reasons"] == ["excessive growth burden"]


def test_outcome_ingestion_success_produces_stop_decision():
    with db.session_scope() as s:
        proj, cand = _approved_candidate(s)
        outcome = outcome_service.ingest_outcome(
            s, design_id=cand.design_id, actor_id="tech",
            observed_results=[{"metric": "titer", "value": 1.5, "baseline_value": 1.0}],
            construction_verified=True, assay_qc_passed=True,
        )
        assert outcome.failure_classification == "success"
        assert outcome.decided_next_action == "stop"
        assert outcome.residuals
        proj_final = s.execute(select(type(proj)).where(type(proj).design_project_id == proj.design_project_id)).scalar_one()
        assert proj_final.status == "completed"


def test_construction_failure_is_never_biological_evidence():
    with db.session_scope() as s:
        proj, cand = _approved_candidate(s)
        outcome = outcome_service.ingest_outcome(
            s, design_id=cand.design_id, actor_id="tech", observed_results=[], construction_verified=False, assay_qc_passed=True,
        )
        assert outcome.failure_classification == "assembly_failed"
        assert outcome.decided_next_action == "next_iteration"  # not diagnosis_reopened - technical, not biological
        fc = s.get(FailureCase, outcome.failure_case_id)
        assert fc.failure_class == "construction"


def test_measurement_failure_is_classified_distinctly_from_biological_null():
    with db.session_scope() as s:
        proj, cand = _approved_candidate(s)
        outcome = outcome_service.ingest_outcome(
            s, design_id=cand.design_id, actor_id="tech", observed_results=[], construction_verified=True, assay_qc_passed=False,
        )
        assert outcome.failure_classification == "measurement_invalid"
        fc = s.get(FailureCase, outcome.failure_case_id)
        assert fc.failure_class == "measurement"


def test_biological_underperformance_triggers_diagnosis_reopen():
    with db.session_scope() as s:
        proj, cand = _approved_candidate(s)
        outcome = outcome_service.ingest_outcome(
            s, design_id=cand.design_id, actor_id="tech",
            observed_results=[{"metric": "titer", "value": 0.8, "baseline_value": 1.0}],
            construction_verified=True, assay_qc_passed=True,
        )
        assert outcome.failure_classification == "biological_underperformance"
        assert outcome.decided_next_action == "diagnosis_reopened"
        fc = s.get(FailureCase, outcome.failure_case_id)
        assert fc.failure_class == "biological_null"
        proj_final = s.execute(select(type(proj)).where(type(proj).design_project_id == proj.design_project_id)).scalar_one()
        assert proj_final.status == "diagnosis_reopened"


def test_failure_case_is_written_into_shared_problem02_table():
    """doc04 §7: failures land in the SAME `harness.learning.models.
    FailureCase` table Problem 02's own DBTL loop reads, not a second one."""
    with db.session_scope() as s:
        proj, cand = _approved_candidate(s)
        before = s.execute(select(FailureCase).where(FailureCase.project_id == proj.project_id)).scalars().all()
        outcome_service.ingest_outcome(
            s, design_id=cand.design_id, actor_id="tech", observed_results=[], construction_verified=False, assay_qc_passed=True,
        )
        after = s.execute(select(FailureCase).where(FailureCase.project_id == proj.project_id)).scalars().all()
        assert len(after) == len(before) + 1


def test_next_iteration_can_restart_strategy_generation():
    with db.session_scope() as s:
        proj, cand = _approved_candidate(s)
        outcome_service.ingest_outcome(
            s, design_id=cand.design_id, actor_id="tech", observed_results=[], construction_verified=False, assay_qc_passed=True,
        )
        proj = governance_service.start_next_iteration_round(s, design_project_id=proj.design_project_id, actor_id="pi")
        assert proj.status == "strategy_generated"

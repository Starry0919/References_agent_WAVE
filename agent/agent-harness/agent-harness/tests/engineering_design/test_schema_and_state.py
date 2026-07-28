"""doc04 §13.1: schema/enum validity, illegal state transitions, ORM
immutability guards, and reload-then-continue."""
from __future__ import annotations

import pytest

from harness import db
from harness.engineering_design import handoff as handoff_mod, project_service
from harness.engineering_design.loop import EngineeringDesignLoopController, IllegalDesignTransitionError
from harness.engineering_design.models import CandidateDesign, DesignEvaluation
from harness.db import ImmutableFieldError
from harness.ids import new_id, now
from harness.workflow.gates import design_objective_gate
from tests.engineering_design.fixtures import build_trp_diagnosis

_loop = EngineeringDesignLoopController()


def test_illegal_transition_is_rejected():
    with db.session_scope() as s:
        _, _, decision = build_trp_diagnosis(s)
        proj, _ = handoff_mod.ingest_diagnosis_decision(s, decision=decision, actor_id="agent")
        assert proj.status == "objective_draft"
        with pytest.raises(IllegalDesignTransitionError):
            # cannot jump straight to portfolio_generated from objective_draft
            _loop.generate_portfolio(s, proj, actor_id="agent")


def test_candidate_genetic_content_is_immutable_after_creation():
    with db.session_scope() as s:
        _, _, decision = build_trp_diagnosis(s)
        proj, _ = handoff_mod.ingest_diagnosis_decision(s, decision=decision, actor_id="agent")
        design_id = new_id("CAND")
        cand = CandidateDesign(
            design_id=design_id, design_project_id=proj.design_project_id, lineage_id=design_id, design_version=1,
            parent_design_ids=[], strategy_ids=[], genetic_modifications=[{"target_identifier": "aroG", "operation": "overexpression"}],
            regulatory_architecture={}, process_modifications=[], expected_mechanism="test", causal_chain=[],
            interaction_and_epistasis_assumptions=[], evidence_links=[], counterfactual_requests=[], counterfactual_results=[],
            uncertainty_and_model_conflicts=[], readiness="conceptual", status="proposed", rejection_reasons=[],
            source_diagnosis_version=1, proposed_by="system", created_at=now(),
        )
        s.add(cand)

    with db.session_scope() as s:  # status IS allowed to progress
        row = s.get(CandidateDesign, design_id)
        row.status = "selected"

    with pytest.raises(ImmutableFieldError):
        with db.session_scope() as s:
            row = s.get(CandidateDesign, design_id)
            row.genetic_modifications = [{"target_identifier": "trpE", "operation": "knockout"}]


def test_design_evaluation_is_immutable_except_pareto_status():
    with db.session_scope() as s:
        _, _, decision = build_trp_diagnosis(s)
        proj, _ = handoff_mod.ingest_diagnosis_decision(s, decision=decision, actor_id="agent")
        design_id = new_id("CAND")
        cand = CandidateDesign(
            design_id=design_id, design_project_id=proj.design_project_id, lineage_id=design_id, design_version=1,
            parent_design_ids=[], strategy_ids=[], genetic_modifications=[], regulatory_architecture={},
            process_modifications=[], expected_mechanism="test", causal_chain=[], interaction_and_epistasis_assumptions=[],
            evidence_links=[], counterfactual_requests=[], counterfactual_results=[], uncertainty_and_model_conflicts=[],
            readiness="conceptual", status="proposed", rejection_reasons=[], source_diagnosis_version=1,
            proposed_by="system", created_at=now(),
        )
        s.add(cand)
        s.flush()

        ev = DesignEvaluation(
            evaluation_id=new_id("EVAL"), design_id=design_id, design_version=1, objective_vector=[],
            hard_constraint_results=[], mechanism_consistency={}, evidence_assessment={}, model_results=[],
            tradeoff_profile={}, buildability={}, validation_feasibility={}, expected_information_gain="unknown",
            safety_and_governance={}, evaluator_findings=[], required_revisions=[], pareto_status=None,
            recommendation="insufficient_evidence", provenance={}, created_at=now(),
        )
        s.add(ev)
        s.flush()
        evaluation_id = ev.evaluation_id

    with db.session_scope() as s:  # pareto_status IS allowed to change
        row = s.get(DesignEvaluation, evaluation_id)
        row.pareto_status = "nondominated"

    with pytest.raises(ImmutableFieldError):
        with db.session_scope() as s:
            row = s.get(DesignEvaluation, evaluation_id)
            row.recommendation = "select"  # NOT allowed - findings are append-only


def test_reload_and_continue_workflow():
    """Persistence -> fresh session reload -> workflow continues (doc04
    §13.1: 'persistence 后重新加载并继续流程')."""
    with db.session_scope() as s:
        _, _, decision = build_trp_diagnosis(s)
        proj, _ = handoff_mod.ingest_diagnosis_decision(s, decision=decision, actor_id="agent")
        design_project_id = proj.design_project_id

    with db.session_scope() as s2:
        reloaded = project_service.get_design_project(s2, design_project_id)
        assert reloaded is not None
        assert reloaded.status == "objective_draft"
        reloaded = project_service.set_objectives(
            s2, design_project_id=design_project_id, primary_metrics=[{"metric": "titer"}], secondary_metrics=[],
            hard_constraints=[], preferences_or_weights=[], available_resources={}, expected_version=reloaded.version, actor_id="pi",
        )
        gate = design_objective_gate(has_primary_metrics=True, has_hard_constraints_declared=True)
        reloaded = _loop.confirm_objective(s2, reloaded, actor_id="pi", objective_gate_result=gate)
        assert reloaded.status == "strategy_generated"


def test_project_objective_change_does_not_touch_diagnosis_confidence():
    """doc04 §2.2: preferences/weights may reorder candidates but must
    never alter diagnosis confidence - the design project's objective
    fields and the diagnosis decision's confidence_representation are
    stored on entirely separate rows/tables with no write path between them."""
    with db.session_scope() as s:
        _, _, decision = build_trp_diagnosis(s)
        original_confidence = dict(decision.confidence_representation)
        proj, _ = handoff_mod.ingest_diagnosis_decision(s, decision=decision, actor_id="agent")
        project_service.set_objectives(
            s, design_project_id=proj.design_project_id, primary_metrics=[{"metric": "titer"}], secondary_metrics=[],
            hard_constraints=[{"constraint": "x", "type": "max_modifications", "value": 1}],
            preferences_or_weights=[{"prefer_role": "low_risk"}], available_resources={}, expected_version=proj.version, actor_id="pi",
        )
        assert decision.confidence_representation == original_confidence

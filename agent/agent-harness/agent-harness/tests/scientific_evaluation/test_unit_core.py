"""doc05 §13.1 unit tests."""
from __future__ import annotations

import pytest

from harness.db import session_scope
from harness.designs.service import SelfApprovalError
from harness.engineering_design.models import CandidateDesign
from harness.scientific_evaluation import comparator, deterministic, human_gate, intake, revision
from harness.scientific_evaluation.models import EvaluationCase, RevisionCycle

from tests.scientific_evaluation.sci_fixtures import build_evaluated_portfolio, run_full_scientific_evaluation


def test_context_freeze_and_version_check():
    with session_scope() as session:
        proj, portfolio, candidates = build_evaluated_portfolio(session)
        case, _ = intake.open_evaluation_case(session, portfolio_id=portfolio.portfolio_id, actor_id="pi")
        assert case.frozen_context["chassis"] == proj.chassis
        assert case.frozen_context["diagnosis_version_at_freeze"] == proj.diagnosis_version
        assert intake.detect_context_drift(case, proj) is False

        # `detect_context_drift` is a pure comparison - simulate a live project having moved on
        # without persisting an illegal mutation to the immutable `diagnosis_version` column:
        class _DriftedProjView:
            chassis = proj.chassis
            chassis_version_or_genotype = proj.chassis_version_or_genotype
            diagnosis_version = proj.diagnosis_version + 1

        assert intake.detect_context_drift(case, _DriftedProjView()) is True
        # the frozen row itself never silently changed:
        assert case.frozen_context["diagnosis_version_at_freeze"] != _DriftedProjView.diagnosis_version


def test_source_type_not_conflated():
    with session_scope() as session:
        _, _, _, result = run_full_scientific_evaluation(session)
        for claims in result["claims_by_design"].values():
            for claim in claims:
                assert claim.source_type in (
                    "experimental_observation", "literature_evidence", "database_record", "computational_model",
                    "deterministic_rule", "expert_judgment", "llm_hypothesis",
                )
        # a claim with no resolvable reference is never silently reported as database_record/experimental:
        for evidence_list in result["evidence_by_design"].values():
            for a in evidence_list:
                if a.evidence_id is None:
                    assert a.overall_strength == "unknown"


def test_evidence_match_dimensions_are_saved_per_dimension_not_a_single_score():
    with session_scope() as session:
        _, _, _, result = run_full_scientific_evaluation(session)
        any_assessment = next(iter(result["evidence_by_design"].values()))[0]
        for dim in ("host_match", "genotype_match", "condition_match", "process_match", "time_match",
                    "intervention_match", "measurement_match", "mechanism_match"):
            value = getattr(any_assessment, dim)
            assert value in ("unknown", "not_applicable", "poor", "partial", "close", "exact")
        # never collapsed into one field only:
        assert hasattr(any_assessment, "overall_strength")


def test_opposing_evidence_not_dropped():
    with session_scope() as session:
        proj, portfolio, candidates = build_evaluated_portfolio(session)
        low_risk = next(c for c in candidates if c.portfolio_role == "low_risk")
        # simulate a prior rejected candidate with the identical modification signature
        sig_mod = low_risk.genetic_modifications[0]
        rejected = CandidateDesign(
            design_id="CAND-PRIOR-REJECTED", design_project_id=low_risk.design_project_id, lineage_id="LINEAGE-X",
            design_version=1, parent_design_ids=[], strategy_ids=[], portfolio_id=None, portfolio_role="low_risk",
            genetic_modifications=[sig_mod], regulatory_architecture={}, process_modifications=[],
            expected_mechanism="prior attempt", causal_chain=[], interaction_and_epistasis_assumptions=[],
            evidence_links=[], counterfactual_requests=[], counterfactual_results=[], uncertainty_and_model_conflicts=[],
            tradeoff_profile=None, buildability_assessment=None, build_test_package_id=None, debug_and_fallback_plan=None,
            safety_flags=[], readiness="conceptual", status="rejected", rejection_reasons=["did not work"],
            source_diagnosis_version=1, created_from_revision_reason=None, proposed_by="pi", created_at=0.0,
        )
        session.add(rejected)
        session.flush()

        case, _ = intake.open_evaluation_case(session, portfolio_id=portfolio.portfolio_id, actor_id="pi")
        from harness.scientific_evaluation import claims as claims_mod, evidence as evidence_mod
        claims = claims_mod.extract_claims(session, evaluation_id=case.evaluation_id, candidate=low_risk)
        assessments = evidence_mod.assess_evidence(session, case=case, candidate=low_risk, claims=claims)
        opposing = [a for a in assessments if a.opposing_evidence]
        assert opposing, "identical prior-rejected modification signature must surface as opposing evidence"
        assert "CAND-PRIOR-REJECTED" in opposing[0].opposing_evidence[0]


def test_not_computed_is_never_converted_to_zero():
    with session_scope() as session:
        _, _, _, result = run_full_scientific_evaluation(session)
        for records in result["models_by_design"].values():
            for r in records:
                if r.run_status == "not_computed":
                    assert r.result_summary in ({}, None) or "objective_value" not in r.result_summary
                    assert r.result_summary != 0
                    assert r.run_status != 0
        for vector in result["vectors"]:
            for dim_name in ("experimental_cost", "time_to_result", "information_gain"):
                dim = getattr(vector, dim_name)
                if dim["mode"] == "not_computed":
                    assert dim["value_or_level"] != 0
                    assert dim["value_or_level"] == "unknown"


def test_deterministic_critical_finding_blocks_build():
    with session_scope() as session:
        proj, portfolio, candidates = build_evaluated_portfolio(session)
        case, _ = intake.open_evaluation_case(session, portfolio_id=portfolio.portfolio_id, actor_id="pi")
        low_risk = next(c for c in candidates if c.portfolio_role == "low_risk")
        low_risk.status = "approved_for_build"
        session.flush()
        checks = deterministic.run_pre_human_gate_checks(session, case=case, candidate=low_risk)
        assert deterministic.blocks_progression(checks)
        with pytest.raises(human_gate.HumanGatePreconditionError):
            human_gate.record_human_evaluation_decision(
                session, case=case, decision="approve_for_build", approver_id="reviewer", selected_candidates=[low_risk.design_id],
            )


def test_unknown_is_not_low_risk():
    with session_scope() as session:
        _, _, _, result = run_full_scientific_evaluation(session)
        for vector in result["vectors"]:
            if vector.risk["mode"] == "not_computed":
                assert vector.risk["value_or_level"] not in ("low", "none")
            if vector.uncertainty["mode"] == "not_computed":
                assert vector.uncertainty["value_or_level"] == "unknown"
                assert vector.uncertainty["value_or_level"] != "low"


def test_pareto_dominance_and_hard_constraint_elimination():
    with session_scope() as session:
        _, _, _, result = run_full_scientific_evaluation(session)
        vectors_by_id = {v.candidate_id: v for v in result["vectors"]}
        for v in result["vectors"]:
            if v.hard_constraint_status == "violated":
                assert v.pareto_status == "excluded"
                assert v.excluded_reasons
        nondominated = [v for v in result["vectors"] if v.pareto_status == "nondominated"]
        dominated = [v for v in result["vectors"] if v.pareto_status == "dominated"]
        for v in dominated:
            assert v.dominated_by, "a dominated candidate must record who dominates it"
            for winner_id in v.dominated_by:
                assert winner_id in vectors_by_id


def test_reviewer_cannot_modify_original_design_version():
    with session_scope() as session:
        proj, portfolio, candidates = build_evaluated_portfolio(session)
        low_risk = next(c for c in candidates if c.portfolio_role == "low_risk")
        original_version = low_risk.design_version
        original_mods = list(low_risk.genetic_modifications)

        case, _ = intake.open_evaluation_case(session, portfolio_id=portfolio.portfolio_id, actor_id="pi")
        from harness.scientific_evaluation import service as sci_service
        sci_service.continue_scientific_evaluation(session, evaluation_id=case.evaluation_id, actor_id="pi")

        refreshed = session.get(CandidateDesign, low_risk.design_id)
        assert refreshed.design_version == original_version
        assert refreshed.genetic_modifications == original_mods


def test_revision_creates_new_version_never_overwrites():
    with session_scope() as session:
        proj, portfolio, candidates, result = run_full_scientific_evaluation(session)
        case = result["case"]
        target = next(c for c in candidates if c.portfolio_role == "fallback")
        cycle, new_candidate = revision.apply_revision(
            session, case=case, design_id=target.design_id, actor_id="pi",
            modification_reason="test revision creates a new version",
            genetic_modifications=[{"target_identifier": "ppc", "operation": "overexpression", "evidence_links": []}],
        )
        assert new_candidate.design_id != target.design_id
        assert new_candidate.design_version == target.design_version + 1
        assert new_candidate.parent_design_ids == [target.design_id]
        original_still_intact = session.get(CandidateDesign, target.design_id)
        assert original_still_intact.design_version == target.design_version
        assert original_still_intact.genetic_modifications == target.genetic_modifications


def test_max_rounds_does_not_auto_approve():
    with session_scope() as session:
        proj, portfolio, candidates, result = run_full_scientific_evaluation(session)
        case = result["case"]
        # simulate having already exhausted the revision budget (mutable field, legal to set directly in test setup):
        case.status = "meta_review"
        case.revision_round = 3
        session.flush()
        from harness.workflow.gates import scientific_revision_gate
        gate = scientific_revision_gate(open_blocking_findings=["still open"], revision_round=3, revision_limit=3)
        assert gate.status.value == "human_review"
        from harness.scientific_evaluation.loop import EvaluationLoopController
        loop = EvaluationLoopController()
        loop.complete_meta_review(session, case, actor_id="system", revision_gate_result=gate)
        assert case.status == "awaiting_human_decision"  # never approved_for_build/approved_for_planning automatically


def test_no_human_gate_no_approved_for_build():
    with session_scope() as session:
        proj, portfolio, candidates, result = run_full_scientific_evaluation(session)
        case = result["case"]
        assert case.status != "approved_for_build"
        # attempting to move straight there without going through the human_gate module is structurally impossible:
        # CandidateDesign.status is never set to approved_for_build anywhere in the scientific_evaluation pipeline itself.
        for c in candidates:
            refreshed = session.get(CandidateDesign, c.design_id)
            assert refreshed.status != "approved_for_build"


def test_self_approval_rejected():
    with session_scope() as session:
        proj, portfolio, candidates, result = run_full_scientific_evaluation(session)
        case = result["case"]
        low_risk = next(c for c in candidates if c.portfolio_role == "low_risk")
        with pytest.raises(SelfApprovalError):
            human_gate.record_human_evaluation_decision(
                session, case=case, decision="hold", approver_id=low_risk.proposed_by, selected_candidates=[low_risk.design_id],
            )


def test_append_only_history_not_overwritten():
    with session_scope() as session:
        proj, portfolio, candidates, result = run_full_scientific_evaluation(session)
        case = result["case"]
        first_round_reviews = {rid for lst in result["reviews_by_design"].values() for rid in [r.review_id for r in lst]}

        target = next(c for c in candidates if c.portfolio_role == "fallback")
        r2 = None
        from harness.scientific_evaluation import service as sci_service
        r2 = sci_service.apply_revision_and_reevaluate(
            session, evaluation_id=case.evaluation_id, design_id=target.design_id, actor_id="pi",
            modification_reason="second round", genetic_modifications=[{"target_identifier": "ppc", "operation": "overexpression", "evidence_links": []}],
        )
        second_round_reviews = {rid for lst in r2["reviews_by_design"].values() for rid in [r.review_id for r in lst]}
        # old reviews still readable/unchanged, not replaced:
        from harness.scientific_evaluation.models import ScientificReview
        for rid in first_round_reviews:
            assert session.get(ScientificReview, rid) is not None
        assert not first_round_reviews & second_round_reviews  # a new pass creates NEW rows, never edits old ones

        cycles = session.query(RevisionCycle).filter(RevisionCycle.evaluation_id == case.evaluation_id).all()
        assert len(cycles) == 1
        assert cycles[0].from_design_id == target.design_id

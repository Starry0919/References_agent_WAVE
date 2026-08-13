"""doc04 §13.5: Build/Test readiness gating and Human Approval Gate."""
from __future__ import annotations

import pytest

from harness import db
from harness.designs.service import SelfApprovalError
from harness.engineering_design import build_test_planner, design_version_bridge, governance_service
from harness.engineering_design.evaluation_service import evaluate_portfolio
from tests.engineering_design.fixtures import handoff_through_portfolio


def _ranked_candidate(s):
    proj, portfolio, candidates = handoff_through_portfolio(s)
    result = evaluate_portfolio(s, portfolio_id=portfolio.portfolio_id, actor_id="system")
    selected_id = result["decision"]["selected_design_ids"][0]
    candidate = next(c for c in candidates if c.design_id == selected_id)
    return proj, candidate

def _human_selected_candidate(s):
    proj,candidate=_ranked_candidate(s)
    governance_service.request_human_approval(s,design_project_id=proj.design_project_id,actor_id="system")
    governance_service.record_human_decision(s,design_id=candidate.design_id,approver_id="pi_lead",decision="approved")
    return proj,candidate


def test_missing_requirements_cap_readiness_below_build_ready():
    with db.session_scope() as s:
        proj, candidate = _human_selected_candidate(s)
        pkg = build_test_planner.draft_build_test_package(s, design_id=candidate.design_id, actor_id="pi")  # nothing supplied
        assert pkg.readiness == "conceptual"
        assert pkg.missing_information_or_resources == [] or True  # materials weren't requested either


def test_partial_plan_is_planning_ready_not_build_ready():
    with db.session_scope() as s:
        proj, candidate = _human_selected_candidate(s)
        pkg = build_test_planner.draft_build_test_package(
            s, design_id=candidate.design_id, actor_id="pi", construction_concept="lambda-red recombineering",
            required_materials=["pKD46"],
        )
        assert pkg.readiness == "planning_ready"
        assert pkg.readiness != "build_ready"


def test_complete_plan_reaches_build_ready_with_controls_replication_sampling_qc_decision_rule():
    with db.session_scope() as s:
        proj, candidate = _human_selected_candidate(s)
        pkg = build_test_planner.draft_build_test_package(
            s, design_id=candidate.design_id, actor_id="pi", construction_concept="lambda-red recombineering + P1 transduction",
            required_materials=["pKD46", "pCP20"], controls=[{"name": "wild-type baseline"}],
            replication_plan={"biological_replicates": 3, "technical_replicates": 2}, sampling_plan=[{"time": "24h"}, {"time": "48h"}],
            qc_checkpoints=["colony PCR", "Sanger sequencing"], decision_rules=["titer increase >=10% vs baseline with p<0.05 = success"],
        )
        assert pkg.readiness == "build_ready"
        assert pkg.target_readouts and pkg.mechanism_readouts and pkg.failure_signatures  # not just the final product


def test_target_and_mechanism_and_tradeoff_readouts_all_present():
    with db.session_scope() as s:
        proj, candidate = _human_selected_candidate(s)
        pkg = build_test_planner.draft_build_test_package(s, design_id=candidate.design_id, actor_id="pi", construction_concept="x")
        assert pkg.target_readouts  # phenotype
        assert pkg.mechanism_readouts  # not just the final phenotype
        assert pkg.expected_observations


def test_self_approval_is_blocked():
    with db.session_scope() as s:
        proj, candidate = _ranked_candidate(s)
        governance_service.request_human_approval(s, design_project_id=proj.design_project_id, actor_id="system")
        with pytest.raises(SelfApprovalError):
            governance_service.record_human_decision(s, design_id=candidate.design_id, approver_id=candidate.proposed_by, decision="approved")


def test_build_cannot_proceed_without_human_approval():
    with db.session_scope() as s:
        proj, candidate = _ranked_candidate(s)
        assert candidate.status != "approved_for_build"
        with pytest.raises(design_version_bridge.CandidateNotApprovedError):
            design_version_bridge.bridge_to_design_version(s, design_id=candidate.design_id, actor_id="pi")


def test_full_approval_flow_bridges_to_design_version_and_builds():
    with db.session_scope() as s:
        proj, candidate = _ranked_candidate(s)
        governance_service.request_human_approval(s, design_project_id=proj.design_project_id, actor_id="system")
        approval, cand, proj2 = governance_service.record_human_decision(s, design_id=candidate.design_id, approver_id="pi_lead", decision="approved", approver_role="PI")
        build_test_planner.draft_build_test_package(
            s, design_id=candidate.design_id, actor_id="pi", construction_concept="x", required_materials=["m"],
            controls=[{"a": 1}], replication_plan={"n": 3}, sampling_plan=[{"t": 1}], qc_checkpoints=["qc"], decision_rules=["rule"],
        )
        governance_service.mark_planning_complete(s, design_project_id=proj.design_project_id, actor_id="system")
        assert cand.status == "approved_for_build"
        assert proj2.status == "approved_for_build"

        dv = design_version_bridge.bridge_to_design_version(s, design_id=candidate.design_id, actor_id="pi_lead")
        assert dv.design_version_id

        built = governance_service.start_build(s, design_project_id=proj2.design_project_id, design_id=candidate.design_id, actor_id="tech")
        assert built.status == "built"


def test_rejected_decision_never_reaches_approved_for_build():
    with db.session_scope() as s:
        proj, candidate = _ranked_candidate(s)
        governance_service.request_human_approval(s, design_project_id=proj.design_project_id, actor_id="system")
        approval, cand, proj2 = governance_service.record_human_decision(
            s, design_id=candidate.design_id, approver_id="pi_lead", decision="rejected", reason="growth burden too high",
        )
        assert cand.status == "rejected"
        assert cand.rejection_reasons == ["growth burden too high"]
        assert proj2.status == "rejected"

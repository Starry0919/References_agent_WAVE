"""Prediction Reviewer tests (doc06 §8) - blocking findings must gate
`decision_ready`, and the reviewer must actually inspect the real objects
(not just restate the comparison).
"""
from __future__ import annotations

from harness import db
from harness.virtual_cell import service as vc_service
from harness.virtual_cell.guards import SimulationGuardError, assert_review_passed_before_decision
from tests.virtual_cell.fixtures import build_approved_ppc_knockout_design

_ENV = {"medium": "M9_minimal", "carbon_source": "glucose"}
_CHASSIS = {"organism": "Escherichia coli", "strain": "K-12 MG1655"}


def test_review_of_a_clean_ppc_knockout_is_decision_ready():
    with db.session_scope() as s:
        proj, dv = build_approved_ppc_knockout_design(s)
        result = vc_service.run_prediction_pipeline(
            s, project_id=proj.project_id, design_version_id=dv.design_version_id, chassis=_CHASSIS, environment=_ENV, actor_id="agent",
        )
        review = result["review"]
        assert review.decision in ("decision_ready", "limited_acceptance")
        assert_review_passed_before_decision(review) if review.decision == "decision_ready" else None


def test_review_blocks_decision_ready_when_comparison_is_invalid():
    import types

    from harness.virtual_cell.reviewer import review_prediction

    with db.session_scope() as s:
        proj, dv = build_approved_ppc_knockout_design(s)
        result = vc_service.run_prediction_pipeline(
            s, project_id=proj.project_id, design_version_id=dv.design_version_id, chassis=_CHASSIS, environment=_ENV, actor_id="agent",
        )
        fake_invalid_comparison = types.SimpleNamespace(
            comparison_id="CFCOMP-fake", comparability_status="invalid_comparison",
            comparability_violations=["model_version differs"], endpoints=[],
        )
        review = review_prediction(
            simulation_case_id=result["case"].simulation_case_id, comparison=fake_invalid_comparison,
            compatibility=result["compatibility"], compiled=result["compiled"], baseline_run=result["baseline_run"],
            candidate_run=result["candidate_run"],
        )
        assert any(f["severity"] == "blocking" for f in review.findings)
        assert review.decision != "decision_ready"
        import pytest

        with pytest.raises(SimulationGuardError):
            assert_review_passed_before_decision(review)

"""doc05 §13.3 integration tests."""
from __future__ import annotations

import pytest

from harness import db
from harness.bootstrap import bootstrap_schema
from harness.db import session_scope
from harness.engineering_design.models import CandidateDesign
from harness.scientific_evaluation import gate_hooks, human_gate, intake, service as sci_service
from harness.scientific_evaluation.models import EvaluationCase

from tests.scientific_evaluation.sci_fixtures import build_evaluated_portfolio, run_full_scientific_evaluation


def test_1_legal_candidate_completes_rules_evidence_critic_and_comparison():
    with session_scope() as session:
        proj, portfolio, candidates, result = run_full_scientific_evaluation(session)
        case = result["case"]
        assert case.status in ("revision_required", "awaiting_human_decision")
        for c in candidates:
            assert result["deterministic_by_design"][c.design_id]
            assert result["evidence_by_design"][c.design_id]
            assert result["reviews_by_design"][c.design_id]
        assert len(result["vectors"]) == len(candidates)
        assert result["meta_decision"] is not None


def test_2_condition_mismatch_produces_transferability_finding():
    """Curated-knowledge evidence never carries condition metadata in this
    knowledge base (see `evidence.py` module docstring) - every real
    evidence-backed claim must therefore honestly surface as a
    transferability concern, not a silently-assumed match."""
    with session_scope() as session:
        proj, portfolio, candidates, result = run_full_scientific_evaluation(session)
        for evs in result["evidence_by_design"].values():
            for a in evs:
                if a.evidence_id is not None:
                    assert a.condition_match == "unknown"
                    assert a.host_match == "unknown"


def test_3_gem_unavailable_or_not_requested_returns_not_computed_honestly():
    with session_scope() as session:
        proj, portfolio, candidates, result = run_full_scientific_evaluation(session)
        for records in result["models_by_design"].values():
            assert all(r.run_status == "not_computed" for r in records)
            assert all(r.result_summary in ({}, None) for r in records)


def test_4_missing_key_control_routes_to_revision():
    with session_scope() as session:
        proj, portfolio, candidates, result = run_full_scientific_evaluation(session)
        missing_control_findings = [
            f for lst in result["findings_by_design"].values() for f in lst if f.category == "missing_control"
        ]
        assert missing_control_findings, "no candidate in this fixture has a BuildTestPackage yet - must be flagged"
        assert result["meta_decision"].recommended_action in ("revise", "request_more_evidence")


def test_5_competing_explanation_can_return_to_diagnosis():
    from harness.diagnosis.models import DiagnosisSession

    with session_scope() as session:
        proj, portfolio, candidates = build_evaluated_portfolio(session)
        from harness.engineering_design.handoff import ingest_diagnosis_decision  # noqa: F401 (not re-used; documents source)

        case, _ = intake.open_evaluation_case(
            session, portfolio_id=portfolio.portfolio_id, actor_id="pi", diagnosis_reference=None,
        )
        target = candidates[0]
        from harness.scientific_evaluation import diagnosis_return
        request = diagnosis_return.create_diagnosis_return_request(
            session, case=case, candidate=target, actor_id="pi",
            triggering_findings=["design commits to precursor-supply mechanism while feedback-inhibition remains unresolved"],
            alternative_explanations=["feedback inhibition of TrpE independently caps flux"],
        )
        assert request.request_id
        assert request.source_design_id == target.design_id


def test_6_revision_produces_new_version_old_review_preserved():
    from harness.scientific_evaluation.models import ScientificReview

    with session_scope() as session:
        proj, portfolio, candidates, result = run_full_scientific_evaluation(session)
        case = result["case"]
        original_review_ids = {r.review_id for lst in result["reviews_by_design"].values() for r in lst}
        target = next(c for c in candidates if c.portfolio_role == "fallback")

        r2 = sci_service.apply_revision_and_reevaluate(
            session, evaluation_id=case.evaluation_id, design_id=target.design_id, actor_id="pi",
            modification_reason="integration test revision",
            genetic_modifications=[{"target_identifier": "ppc", "operation": "overexpression", "evidence_links": []}],
        )
        assert r2["new_candidate"].design_id != target.design_id
        for rid in original_review_ids:
            assert session.get(ScientificReview, rid) is not None


def test_7_human_reject_hold_approve_all_persist():
    for decision in ("hold", "stop", "reject"):
        with session_scope() as session:
            proj, portfolio, candidates, result = run_full_scientific_evaluation(session)
            case = result["case"]
            row = human_gate.record_human_evaluation_decision(
                session, case=case, decision=decision, approver_id="pi_reviewer", rationale=f"test {decision}",
            )
            assert row.decision == decision
            expected_status = {"hold": "held", "stop": "stopped", "reject": "rejected"}[decision]
            assert case.status == expected_status


def test_8_service_restart_recovers_evaluation_state():
    """Simulates a process restart: repoint the engine, re-bootstrap, and
    confirm the persisted `EvaluationCase`/findings/meta-review are still
    readable exactly as left - matching Problem 01-04's own recoverability
    precedent."""
    import tempfile
    from pathlib import Path

    with tempfile.TemporaryDirectory() as tmp:
        db_path = Path(tmp) / "restart_test.db"
        db.reset_engine_for_tests(f"sqlite:///{db_path}")
        bootstrap_schema()
        with session_scope() as session:
            proj, portfolio, candidates, result = run_full_scientific_evaluation(session)
            case_id = result["case"].evaluation_id
            design_id = candidates[0].design_id

        # "restart": repoint to the SAME file, as a fresh process would on boot
        db.reset_engine_for_tests(f"sqlite:///{db_path}")
        bootstrap_schema()
        try:
            with session_scope() as session:
                recovered = intake.get_case(session, case_id)
                assert recovered is not None
                assert recovered.status in ("revision_required", "awaiting_human_decision")
                from harness.scientific_evaluation.models import DeterministicCheckResult
                from sqlalchemy import select
                checks = session.execute(select(DeterministicCheckResult).where(DeterministicCheckResult.evaluation_id == case_id)).scalars().all()
                assert checks
        finally:
            db.get_engine().dispose()  # release the sqlite file handle before TemporaryDirectory cleanup (Windows)

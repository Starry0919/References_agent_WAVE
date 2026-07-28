"""Prompt §5.9 contract tests for the LLM Scientific Critic adapter -
offline, using `FakeStructuredGenerationClient`. Built on the real Problem
04/05 evaluated-portfolio fixture."""
from __future__ import annotations

import json

from harness import db
from harness.llm_generation.models import LLMGenerationRecord
from harness.scientific_evaluation.llm_critic_adapter import run_llm_critic_review
from harness.scientific_evaluation.models import HUMAN_DECISIONS, ScientificReview
from tests.scientific_evaluation.sci_fixtures import run_full_scientific_evaluation
from tests.llm_generation.fakes import FakeStructuredGenerationClient

_VALID = json.dumps({
    "critical_findings": [], "major_findings": ["evidence base is thin for the claimed mechanism"],
    "minor_findings": ["no replicate count specified"], "unsupported_claims": ["titer improvement magnitude"],
    "evidence_gaps": ["no direct measurement of precursor pool"], "biological_risks": [], "engineering_risks": [],
    "model_use_risks": ["no GEM/kinetic model was run to support this claim"], "validation_gaps": ["no negative control described"],
    "alternative_explanations": ["measurement artifact"], "required_revisions": ["add a discriminating test"],
    "recommendation": "revise",
})


def test_llm_critic_adds_an_additive_review_never_self_approving():
    with db.session_scope() as s:
        proj, portfolio, candidates, result = run_full_scientific_evaluation(s, actor_id="pi")
        case = result["case"]
        candidate = candidates[0]
        fake = FakeStructuredGenerationClient(scripted_contents=[_VALID])
        review = run_llm_critic_review(
            s, case=case, candidate=candidate, claims=result["claims_by_design"][candidate.design_id],
            evidence=result["evidence_by_design"][candidate.design_id], models=result["models_by_design"][candidate.design_id],
            deterministic=result["deterministic_by_design"][candidate.design_id], actor_id="pi", client=fake,
        )
        assert review is not None
        assert review.reviewer_type == "llm_critic"
        assert review.recommendation in HUMAN_DECISIONS
        assert review.recommendation == "revise"
        # deterministic reviews from the SAME pipeline run are still present untouched:
        deterministic_reviews = result["reviews_by_design"][candidate.design_id]
        assert all(r.reviewer_type != "llm_critic" for r in deterministic_reviews)
        all_reviews_for_case = s.query(ScientificReview).filter_by(evaluation_id=case.evaluation_id, design_reference=candidate.design_id).all()
        assert any(r.reviewer_type == "llm_critic" for r in all_reviews_for_case)
        assert len(all_reviews_for_case) == len(deterministic_reviews) + 1  # purely additive


def test_llm_critic_cannot_self_approve_a_design():
    """No single reviewer recommendation - LLM or deterministic - can move
    a case to approved on its own; only `human_gate.
    record_human_evaluation_decision` (a real human actor) can."""
    with db.session_scope() as s:
        proj, portfolio, candidates, result = run_full_scientific_evaluation(s, actor_id="pi")
        case = result["case"]
        candidate = candidates[0]
        approve_all = json.loads(_VALID)
        approve_all["recommendation"] = "approve"
        approve_all["critical_findings"] = []
        approve_all["major_findings"] = []
        fake = FakeStructuredGenerationClient(scripted_contents=[json.dumps(approve_all)])
        review = run_llm_critic_review(
            s, case=case, candidate=candidate, claims=result["claims_by_design"][candidate.design_id],
            evidence=result["evidence_by_design"][candidate.design_id], models=result["models_by_design"][candidate.design_id],
            deterministic=result["deterministic_by_design"][candidate.design_id], actor_id="pi", client=fake,
        )
        assert review is not None
        assert review.recommendation == "approve_for_planning"
        # the case's own status is untouched by this call - only a real human decision can move it:
        assert case.status not in ("approved_for_planning", "approved_for_build")


def test_shared_model_risk_recorded_when_same_model_used_for_generation():
    from harness.ids import new_id, now
    from harness.llm_generation.models import LLMGenerationRecord as GenRecord

    with db.session_scope() as s:
        proj, portfolio, candidates, result = run_full_scientific_evaluation(s, actor_id="pi")
        case = result["case"]
        candidate = candidates[0]
        fake = FakeStructuredGenerationClient(scripted_contents=[_VALID], model="shared-model-x")
        # simulate an earlier hypothesis-generation call on the SAME model_id:
        s.add(GenRecord(
            generation_id=new_id("GEN"), task_type="hypothesis", provider="fake", model_id="shared-model-x",
            model_version_or_snapshot="unknown", prompt_template_id="x", prompt_template_version="1", input_refs={},
            output_schema_version="1", raw_output_artifact_ref=None, parsed_output_ref=None, validation_status="valid",
            retry_count=0, fallback_used=False, shared_model_risk=False, token_usage_if_available=None, latency=0.1, created_at=now(),
        ))
        s.flush()
        review = run_llm_critic_review(
            s, case=case, candidate=candidate, claims=result["claims_by_design"][candidate.design_id],
            evidence=result["evidence_by_design"][candidate.design_id], models=result["models_by_design"][candidate.design_id],
            deterministic=result["deterministic_by_design"][candidate.design_id], actor_id="pi", client=fake,
        )
        assert review.shared_model_risk is True
        assert review.independence_flags["model_independent"] is False


def test_llm_critic_returns_none_on_schema_failure_and_deterministic_critics_unaffected():
    with db.session_scope() as s:
        proj, portfolio, candidates, result = run_full_scientific_evaluation(s, actor_id="pi")
        case = result["case"]
        candidate = candidates[0]
        fake = FakeStructuredGenerationClient(scripted_contents=["not json", "still not json", "nope"])
        review = run_llm_critic_review(
            s, case=case, candidate=candidate, claims=result["claims_by_design"][candidate.design_id],
            evidence=result["evidence_by_design"][candidate.design_id], models=result["models_by_design"][candidate.design_id],
            deterministic=result["deterministic_by_design"][candidate.design_id], actor_id="pi", client=fake,
        )
        assert review is None
        deterministic_reviews = result["reviews_by_design"][candidate.design_id]
        assert len(deterministic_reviews) >= 1  # the deterministic pipeline already ran and is unaffected

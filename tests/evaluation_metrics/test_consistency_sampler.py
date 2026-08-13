"""Offline tests for the N-sample consistency sampler, using the same
`FakeStructuredGenerationClient` double `tests/llm_generation` uses - no
network calls. Verifies (a) sampling never writes into the project's real
`EngineeringStrategy` table, and (b) convergence is computed correctly by
strategy_class across scripted, deliberately-varying LLM outputs.
"""
from __future__ import annotations

import json

import pytest

from harness import db
from harness.engineering_design import handoff as handoff_mod
from harness.engineering_design.models import EngineeringStrategy
from harness.evaluation_metrics import consistency_sampler
from tests.engineering_design.fixtures import build_trp_diagnosis
from tests.llm_generation.fakes import FakeStructuredGenerationClient


def _draft(intervention_class: str) -> str:
    return json.dumps({
        "strategies": [{
            "biological_intent": f"test intent for {intervention_class}", "intervention_class": intervention_class,
            "target_entities": ["trpE"], "engineering_implementation_options": ["option"],
            "expected_mechanism": "test mechanism", "expected_benefit": "higher titer", "tradeoffs": [],
            "dependencies": [], "feasibility_questions": [], "safety_questions": [], "evidence_queries": [],
            "validation_plan_draft": [], "assumptions": [],
        }]
    })


def _setup(s):
    _, _, decision = build_trp_diagnosis(s, actor_id="pi")
    proj, handoff = handoff_mod.ingest_diagnosis_decision(
        s, decision=decision, actor_id="agent", chassis="E. coli", chassis_version_or_genotype="K-12 MG1655 wild-type",
    )
    return proj, handoff


def test_consistency_sample_computes_per_class_convergence():
    with db.session_scope() as s:
        proj, _handoff = _setup(s)
        fake = FakeStructuredGenerationClient(scripted_contents=[
            _draft("feedback_relief"), _draft("feedback_relief"), _draft("precursor_supply"),
            _draft("feedback_relief"), _draft("precursor_supply"),
        ])

        run = consistency_sampler.run_consistency_sample(
            s, design_project_id=proj.design_project_id, n_samples=5, actor_id="pi", client=fake,
        )

        assert run.n_samples == 5
        assert len(run.samples) == 5
        report = run.convergence_report
        assert report["samples_with_output"] == 5
        by_class = {r["strategy_class"]: r for r in report["by_strategy_class"]}
        assert by_class["feedback_relief"]["sample_count"] == 3
        assert by_class["feedback_relief"]["convergence"] == pytest.approx(0.6)
        assert by_class["precursor_supply"]["sample_count"] == 2
        assert by_class["precursor_supply"]["convergence"] == pytest.approx(0.4)


def test_consistency_sample_never_persists_real_strategies():
    with db.session_scope() as s:
        proj, _handoff = _setup(s)
        fake = FakeStructuredGenerationClient(scripted_contents=[_draft("feedback_relief")] * 3)
        consistency_sampler.run_consistency_sample(s, design_project_id=proj.design_project_id, n_samples=3, actor_id="pi", client=fake)

        persisted = s.query(EngineeringStrategy).filter_by(design_project_id=proj.design_project_id).all()
        assert persisted == []


def test_consistency_sample_caps_n_samples():
    with db.session_scope() as s:
        proj, _handoff = _setup(s)
        fake = FakeStructuredGenerationClient(scripted_contents=[_draft("feedback_relief")] * consistency_sampler.MAX_N_SAMPLES)
        run = consistency_sampler.run_consistency_sample(
            s, design_project_id=proj.design_project_id, n_samples=999, actor_id="pi", client=fake,
        )
        assert run.n_samples == consistency_sampler.MAX_N_SAMPLES


def test_consistency_sample_records_fallback_when_llm_unavailable():
    with db.session_scope() as s:
        proj, _handoff = _setup(s)
        fake = FakeStructuredGenerationClient(scripted_contents=[], available=False, unavailable_reason="no network")
        run = consistency_sampler.run_consistency_sample(s, design_project_id=proj.design_project_id, n_samples=2, actor_id="pi", client=fake)
        assert all(sample["fallback_used"] for sample in run.samples)
        assert run.convergence_report["samples_with_output"] == 0


def test_no_handoff_raises_clear_error():
    with db.session_scope() as s:
        from harness.projects import service as proj_svc

        proj = proj_svc.create_project(
            s, name="No handoff", host_definition={"species": "E. coli"}, target_product="X", actor_id="pi",
        )
        # A design project can only exist via ingest_diagnosis_decision in
        # production, but the aggregator/sampler must fail clearly even if
        # one somehow exists without a handoff row - simulate that directly.
        from harness.engineering_design.models import EngineeringDesignProject
        from harness.ids import new_id, now

        dp = EngineeringDesignProject(
            design_project_id=new_id("DESIGNPROJ"), project_id=proj.project_id, diagnosis_session_id=new_id("DIAGSESS"),
            diagnosis_decision_id=new_id("DECISION"), diagnosis_version=1, created_by="pi", created_at=now(), updated_at=now(),
        )
        s.add(dp)
        s.flush()

        with pytest.raises(consistency_sampler.NoHandoffForProjectError):
            consistency_sampler.run_consistency_sample(s, design_project_id=dp.design_project_id, n_samples=1, actor_id="pi")

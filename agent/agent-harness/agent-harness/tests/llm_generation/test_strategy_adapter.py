"""Prompt §5.9 contract tests for the Strategy Draft LLM adapter - offline,
using `FakeStructuredGenerationClient`. Built on the same real Problem 03/04
handoff fixture the module's own tests use.
"""
from __future__ import annotations

import json

from harness import db
from harness.engineering_design.llm_strategy_adapter import generate_llm_strategy_drafts
from harness.engineering_design.models import EngineeringStrategy
from harness.llm_generation.models import LLMGenerationRecord
from tests.engineering_design.fixtures import build_trp_diagnosis
from tests.llm_generation.fakes import FakeStructuredGenerationClient

_VALID = json.dumps({
    "strategies": [
        {
            "biological_intent": "relieve feedback inhibition of anthranilate synthase", "intervention_class": "feedback_relief",
            "target_entities": ["trpE"], "engineering_implementation_options": ["feedback-resistant trpE allele"],
            "expected_mechanism": "removes allosteric inhibition by tryptophan", "expected_benefit": "sustained flux at high intracellular Trp",
            "tradeoffs": ["possible growth burden"], "dependencies": ["confirmed feedback-sensitive allele"],
            "feasibility_questions": ["is a resistant allele characterized in E. coli?"], "safety_questions": [],
            "evidence_queries": ["trpE feedback resistance mutations E. coli"], "validation_plan_draft": ["compare titer vs wild-type trpE"],
            "assumptions": ["feedback inhibition is rate-limiting"],
        }
    ]
})
_SCHEMA_INVALID = "{not valid"


def _setup(s):
    from harness.engineering_design import handoff as handoff_mod

    _, _, decision = build_trp_diagnosis(s, actor_id="pi")
    proj, handoff = handoff_mod.ingest_diagnosis_decision(s, decision=decision, actor_id="agent", chassis="E. coli", chassis_version_or_genotype="K-12 MG1655 wild-type")
    return proj, handoff


def test_structured_generation_success():
    with db.session_scope() as s:
        proj, handoff = _setup(s)
        fake = FakeStructuredGenerationClient(scripted_contents=[_VALID])
        rows, fallback_used, record = generate_llm_strategy_drafts(
            s, project_id=proj.project_id, design_project_id=proj.design_project_id, diagnosis_reference=handoff.handoff_id,
            objective="improve titer", supported_hypotheses=[], primary_metrics=[{"metric": "titer"}], actor_id="pi", client=fake,
        )
        assert fallback_used is False
        assert len(rows) == 1
        assert rows[0].strategy_class == "feedback_relief"
        assert rows[0].evidence_links == []  # LLM output never written in as evidence
        assert rows[0].provenance["method"] == "llm_draft_v1"
        persisted = s.query(EngineeringStrategy).filter_by(design_project_id=proj.design_project_id, status="proposed").all()
        assert any(r.provenance.get("method") == "llm_draft_v1" for r in persisted)
        assert record.validation_status == "valid"


def test_invalid_intervention_class_rejected():
    bad = json.loads(_VALID)
    bad["strategies"][0]["intervention_class"] = "not_a_real_class"
    with db.session_scope() as s:
        proj, handoff = _setup(s)
        fake = FakeStructuredGenerationClient(scripted_contents=[json.dumps(bad), json.dumps(bad), json.dumps(bad)])
        rows, fallback_used, record = generate_llm_strategy_drafts(
            s, project_id=proj.project_id, design_project_id=proj.design_project_id, diagnosis_reference=handoff.handoff_id,
            objective="improve titer", supported_hypotheses=[], primary_metrics=[{"metric": "titer"}], actor_id="pi", client=fake,
        )
        assert fallback_used is True
        assert rows == []
        assert record.fallback_used is True


def test_provider_unavailable_falls_back():
    with db.session_scope() as s:
        proj, handoff = _setup(s)
        fake = FakeStructuredGenerationClient(scripted_contents=[], available=False, unavailable_reason="no network")
        rows, fallback_used, record = generate_llm_strategy_drafts(
            s, project_id=proj.project_id, design_project_id=proj.design_project_id, diagnosis_reference=handoff.handoff_id,
            objective="improve titer", supported_hypotheses=[], primary_metrics=[{"metric": "titer"}], actor_id="pi", client=fake,
        )
        assert fallback_used is True
        assert rows == []
        assert record.validation_status == "provider_error"

"""Prompt §5.9's required contract tests for the Hypothesis LLM adapter -
offline, using `FakeStructuredGenerationClient` (no network)."""
from __future__ import annotations

import json

from harness import db
from harness.diagnosis.llm_hypothesis_adapter import generate_llm_hypothesis_candidates
from harness.llm_generation.models import LLMGenerationRecord
from harness.projects import service as proj_svc
from tests.llm_generation.fakes import FakeStructuredGenerationClient

_VALID = json.dumps({
    "hypotheses": [
        {
            "statement": "Precursor supply limitation constrains titer", "mechanism_class": "biological_mechanism",
            "causal_chain": ["low PEP", "low DAHP synthase flux"], "expected_observations": ["low precursor pool"],
            "contradicting_observations": [], "discriminating_tests": ["13C flux analysis of central metabolism"],
            "required_evidence_queries": ["PEP pool measurement"], "assumptions": ["steady state"], "unsupported_claims": [],
        },
        {
            "statement": "Assay QC artifact explains apparent plateau", "mechanism_class": "measurement_data",
            "causal_chain": ["detector saturation"], "expected_observations": ["nonlinear calibration curve"],
            "contradicting_observations": [], "discriminating_tests": ["dilution series re-assay"],
            "required_evidence_queries": [], "assumptions": [], "unsupported_claims": [],
        },
    ]
})
_SCHEMA_INVALID = "not json at all {{{"


def _make_project(s):
    return proj_svc.create_project(s, name="LLM hyp test", host_definition={"species": "E. coli"}, target_product="L-tryptophan", actor_id="pi")


def test_structured_generation_success_on_first_try():
    with db.session_scope() as s:
        proj = _make_project(s)
        fake = FakeStructuredGenerationClient(scripted_contents=[_VALID])
        candidates, fallback_used = generate_llm_hypothesis_candidates(
            s, project_id=proj.project_id, phenotype="titer plateau", product="L-tryptophan", host="E. coli K-12", context={}, actor_id="agent", client=fake,
        )
        assert fallback_used is False
        assert len(candidates) == 2
        assert {c.mechanism_class for c in candidates} == {"biological_mechanism", "measurement_data"}
        assert all(c.falsifiers for c in candidates)  # every candidate has a real falsifier, never bare
        records = s.query(LLMGenerationRecord).all()
        assert len(records) == 1
        assert records[0].task_type == "hypothesis"
        assert records[0].validation_status == "valid"
        assert records[0].fallback_used is False
        assert records[0].retry_count == 0


def test_schema_invalid_then_recovers_on_retry():
    with db.session_scope() as s:
        proj = _make_project(s)
        fake = FakeStructuredGenerationClient(scripted_contents=[_SCHEMA_INVALID, _VALID])
        candidates, fallback_used = generate_llm_hypothesis_candidates(
            s, project_id=proj.project_id, phenotype="titer plateau", product="L-tryptophan", host="E. coli K-12", context={}, actor_id="agent", client=fake,
        )
        assert fallback_used is False
        assert len(candidates) == 2
        record = s.query(LLMGenerationRecord).one()
        assert record.retry_count == 1


def test_schema_invalid_exhausts_retries_and_falls_back():
    with db.session_scope() as s:
        proj = _make_project(s)
        fake = FakeStructuredGenerationClient(scripted_contents=[_SCHEMA_INVALID, _SCHEMA_INVALID, _SCHEMA_INVALID])
        candidates, fallback_used = generate_llm_hypothesis_candidates(
            s, project_id=proj.project_id, phenotype="titer plateau", product="L-tryptophan", host="E. coli K-12", context={}, actor_id="agent", client=fake,
        )
        assert fallback_used is True
        assert candidates == []  # never a fabricated placeholder candidate
        record = s.query(LLMGenerationRecord).one()
        assert record.fallback_used is True
        assert record.validation_status == "schema_invalid"
        assert record.retry_count == 2  # max_schema_retries default


def test_provider_unavailable_falls_back_immediately_without_retry():
    with db.session_scope() as s:
        proj = _make_project(s)
        fake = FakeStructuredGenerationClient(scripted_contents=[], available=False, unavailable_reason="missing API key for provider 'poe'")
        candidates, fallback_used = generate_llm_hypothesis_candidates(
            s, project_id=proj.project_id, phenotype="titer plateau", product="L-tryptophan", host="E. coli K-12", context={}, actor_id="agent", client=fake,
        )
        assert fallback_used is True
        assert candidates == []
        record = s.query(LLMGenerationRecord).one()
        assert record.validation_status == "provider_error"
        assert record.retry_count == 0


def test_partially_invalid_draft_list_keeps_only_valid_drafts():
    """One hypothesis missing a discriminating_test (no falsifier) must be
    dropped, not silently accepted without one."""
    bad_one = json.loads(_VALID)
    bad_one["hypotheses"][1]["discriminating_tests"] = []  # invalid: no falsifier
    with db.session_scope() as s:
        proj = _make_project(s)
        fake = FakeStructuredGenerationClient(scripted_contents=[json.dumps(bad_one)])
        candidates, fallback_used = generate_llm_hypothesis_candidates(
            s, project_id=proj.project_id, phenotype="titer plateau", product="L-tryptophan", host="E. coli K-12", context={}, actor_id="agent", client=fake,
        )
        assert fallback_used is False  # at least one draft was valid
        assert len(candidates) == 1
        assert candidates[0].mechanism_class == "biological_mechanism"

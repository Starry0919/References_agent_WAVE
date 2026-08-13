"""ONE live integration test (prompt §10.4) proving the real, configured
LLM provider (Poe's OpenAI-compatible gateway, migrated off the direct Kimi
K3 credential) genuinely produces valid structured output end-to-end through
an adapter - not just a fallback path. Kept to a single real call to control
latency/cost; every other test in this suite uses `FakeStructuredGenerationClient`.

If the configured provider becomes unavailable (network, credentials,
quota) this test fails honestly rather than silently skipping - per prompt
§10.4, a live test's absence must be visible, not reported as a pass.
"""
from __future__ import annotations

from harness import db
from harness.diagnosis.llm_hypothesis_adapter import generate_llm_hypothesis_candidates
from harness.llm_generation.client import StructuredGenerationClient
from harness.llm_generation.models import LLMGenerationRecord
from harness.projects import service as proj_svc


def test_real_poe_call_produces_valid_structured_hypotheses():
    health = StructuredGenerationClient().health_check()
    assert health.available, f"configured LLM provider is unavailable: {health.reason}"

    with db.session_scope() as s:
        proj = proj_svc.create_project(s, name="live LLM test", host_definition={"species": "E. coli", "strain": "K-12"}, target_product="L-tryptophan", actor_id="pi")
        candidates, fallback_used = generate_llm_hypothesis_candidates(
            s, project_id=proj.project_id, phenotype="L-tryptophan titer plateaus after 20 hours despite continued glucose feed",
            product="L-tryptophan", host="E. coli K-12", context={"medium": "M9", "carbon_source": "glucose"}, actor_id="agent",
        )
        assert fallback_used is False, "the real provider should have produced schema-valid output, not fallen back"
        assert len(candidates) >= 1
        assert all(c.falsifiers for c in candidates)
        record = s.query(LLMGenerationRecord).filter_by(task_type="hypothesis").one()
        assert record.provider == "poe"
        assert record.validation_status == "valid"
        assert record.parsed_output_ref is not None
        assert record.token_usage_if_available is not None

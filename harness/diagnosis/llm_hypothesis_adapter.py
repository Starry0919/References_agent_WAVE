"""LLM Hypothesis Generator adapter (prompt §5.3): a candidate-drafting
layer ADDED on top of `harness.diagnosis.hypothesis_generator.
generate_competing_hypotheses` (the existing deterministic rule engine),
never replacing it (prompt §5.1: "不得将 deterministic baseline 替换为
LLM"). Every LLM-drafted hypothesis still flows through the SAME
downstream pipeline a rule-generated one does - `harness.learning.service.
propose_hypothesis` (schema validation), the diagnosis loop's evidence/
model/ranking states, and eventually a real `HypothesisAssessment`. This
module never assigns a posterior status, never marks a hypothesis
"confirmed", and never skips any diagnosis state - it only supplies more
candidates in `hypothesis_generator.GeneratedHypothesis` shape (prompt:
"LLM 不得直接...宣称因果成立...推荐跳过诊断").
"""
from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from harness.diagnosis.hypothesis_generator import MECHANISM_CLASSES, GeneratedHypothesis
from harness.llm_generation.client import StructuredGenerationClient
from harness.llm_generation.service import record_generation

PROMPT_TEMPLATE_ID = "diagnosis_hypothesis_draft_v1"
PROMPT_TEMPLATE_VERSION = "1"
OUTPUT_SCHEMA_VERSION = "1"

_SYSTEM_PROMPT = (
    "You are drafting CANDIDATE, FALSIFIABLE hypotheses for a synthetic-biology bottleneck diagnosis - "
    "not conclusions, not recommendations, not confirmed facts. You must propose hypotheses across "
    "DIFFERENT mechanism classes when the context plausibly supports them, including ones that would mean "
    "the apparent biological problem is actually a measurement, process, or model artifact. "
    "You must NOT: state that any hypothesis is proven or ruled out; recommend skipping further diagnosis; "
    "treat the engineering objective/target product as if it were evidence; invent numeric data, DOIs, or "
    "citations; or propose fewer than 2 hypotheses. "
    "Output ONLY a single JSON object: "
    '{"hypotheses": [{"statement": str, "mechanism_class": one of '
    f'{list(MECHANISM_CLASSES)}, '
    '"causal_chain": [str, ...], "expected_observations": [str, ...], "contradicting_observations": [str, ...], '
    '"discriminating_tests": [str, ...] (at least 1, each a concrete falsifying test), '
    '"required_evidence_queries": [str, ...], "assumptions": [str, ...], "unsupported_claims": [str, ...]}, ...]}'
)


def _validate_draft(draft: dict[str, Any]) -> list[str]:
    errors = []
    if not isinstance(draft.get("statement"), str) or not draft["statement"].strip():
        errors.append("statement must be a non-empty string")
    if draft.get("mechanism_class") not in MECHANISM_CLASSES:
        errors.append(f"mechanism_class must be one of {MECHANISM_CLASSES}")
    if not isinstance(draft.get("discriminating_tests"), list) or not draft["discriminating_tests"]:
        errors.append("discriminating_tests must be a non-empty list (every candidate hypothesis needs a falsifier)")
    for list_field in ("causal_chain", "expected_observations", "contradicting_observations", "required_evidence_queries", "assumptions", "unsupported_claims"):
        if list_field in draft and not isinstance(draft[list_field], list):
            errors.append(f"{list_field} must be a list")
    return errors


def _draft_to_generated_hypothesis(draft: dict[str, Any], *, context: dict[str, Any], generation_id: str, model_id: str) -> GeneratedHypothesis:
    return GeneratedHypothesis(
        statement=draft["statement"], mechanism_class=draft["mechanism_class"],
        causal_graph_nodes=list(draft.get("causal_chain", [])), causal_graph_edges=[],
        observations_explained=list(draft.get("expected_observations", [])),
        discriminating_predictions=[{"test": t} for t in draft["discriminating_tests"]],
        falsifiers=list(draft["discriminating_tests"]), assumptions=list(draft.get("assumptions", [])),
        applicability_context=dict(context), temporal_scope=None,
        generation_provenance={
            "source": "llm", "generation_id": generation_id, "model_id": model_id,
            "contradicting_observations": draft.get("contradicting_observations", []),
            "required_evidence_queries": draft.get("required_evidence_queries", []),
            "unsupported_claims": draft.get("unsupported_claims", []),
        },
    )


def generate_llm_hypothesis_candidates(
    session: Session, *, project_id: str, phenotype: str, product: str, host: str, context: dict[str, Any], actor_id: str,
    client: StructuredGenerationClient | None = None,
) -> tuple[list[GeneratedHypothesis], bool]:
    """Returns `(candidates, fallback_used)`. `candidates` is `[]` (never
    fabricated placeholders) whenever the LLM is unavailable or every
    schema-retry attempt failed - the caller (diagnosis adapter) already
    always has the deterministic generator's output and simply gets no
    additional candidates in that case."""
    client = client or StructuredGenerationClient()
    user_prompt = (
        f"Host: {host}\nTarget product: {product}\nObserved phenotype/problem: {phenotype}\n"
        f"Known context: {context}\n"
        "Draft 2-3 competing hypotheses now, as the JSON object described in your instructions."
    )
    attempts, health = client.generate(system_prompt=_SYSTEM_PROMPT, user_prompt=user_prompt, max_tokens=8000)
    last = attempts[-1]

    candidates: list[GeneratedHypothesis] = []
    fallback_used = True
    if last.validation_status == "valid":
        drafts = last.parsed.get("hypotheses") if isinstance(last.parsed, dict) else None
        if isinstance(drafts, list):
            valid_drafts = [d for d in drafts if isinstance(d, dict) and not _validate_draft(d)]
            if valid_drafts:
                fallback_used = False

    record = record_generation(
        session, project_id=project_id, task_type="hypothesis", health=health, attempts=attempts,
        prompt_template_id=PROMPT_TEMPLATE_ID, prompt_template_version=PROMPT_TEMPLATE_VERSION,
        input_refs={"phenotype": phenotype, "product": product, "host": host}, output_schema_version=OUTPUT_SCHEMA_VERSION,
        shared_model_risk=False,  # set by the caller if a strategy/critic call in the same run used the same model_id
        fallback_used=fallback_used, actor_id=actor_id,
    )

    if not fallback_used:
        drafts = last.parsed.get("hypotheses", [])
        for d in drafts:
            if isinstance(d, dict) and not _validate_draft(d):
                candidates.append(_draft_to_generated_hypothesis(d, context=context, generation_id=record.generation_id, model_id=health.model))
    return candidates, fallback_used

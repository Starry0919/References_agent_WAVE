"""LLM Strategy Draft Generator adapter (prompt §5.4): drafts ADDITIONAL
`EngineeringStrategy` candidates on top of `harness.engineering_design.
strategy_generator.generate_strategies` (the existing deterministic
generator), never replacing it. A drafted strategy is explicitly NOT an
executable design - it still has to pass the same downstream pipeline any
rule-generated strategy does: `portfolio_service` candidate generation,
the 8 independent evaluators, counterfactual/model checks, and the Human
Approval Gate. Crucially, `evidence_links` is always left empty here - the
LLM's own `evidence_queries` are recorded as follow-up QUERIES (prompt
§5.4's own field name), never written in as if they were evidence (prompt
§2.4: "LLM 不可以...把自身输出作为 evidence").
"""
from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from harness.engineering_design.models import STRATEGY_CLASSES
from harness.engineering_design.strategy_generator import GeneratedStrategy
from harness.engineering_design.strategy_service import _persist_strategies
from harness.llm_generation.client import StructuredGenerationClient
from harness.llm_generation.service import record_generation

PROMPT_TEMPLATE_ID = "engineering_strategy_draft_v1"
PROMPT_TEMPLATE_VERSION = "1"
OUTPUT_SCHEMA_VERSION = "1"

_SYSTEM_PROMPT = (
    "You are drafting CANDIDATE engineering strategy CONCEPTS for a synthetic-biology design project - "
    "not a concrete, buildable design, not a specific promoter/RBS/mutation choice, and not evidence. "
    "You must NOT invent citations, DOIs, or numeric predictions, and must NOT claim a strategy is safe, "
    "feasible, or evidenced - those are determined later by deterministic checks and independent review. "
    "Output ONLY a single JSON object: "
    '{"strategies": [{"biological_intent": str, '
    f'"intervention_class": one of {list(STRATEGY_CLASSES)}, '
    '"target_entities": [str, ...], "engineering_implementation_options": [str, ...], "expected_mechanism": str, '
    '"expected_benefit": str, "tradeoffs": [str, ...], "dependencies": [str, ...], "feasibility_questions": [str, ...], '
    '"safety_questions": [str, ...], "evidence_queries": [str, ...], "validation_plan_draft": [str, ...], '
    '"assumptions": [str, ...]}, ...]}'
)


def _validate_draft(draft: dict[str, Any]) -> list[str]:
    errors = []
    if not isinstance(draft.get("biological_intent"), str) or not draft["biological_intent"].strip():
        errors.append("biological_intent must be a non-empty string")
    if draft.get("intervention_class") not in STRATEGY_CLASSES:
        errors.append(f"intervention_class must be one of {STRATEGY_CLASSES}")
    if not isinstance(draft.get("target_entities"), list) or not draft["target_entities"]:
        errors.append("target_entities must be a non-empty list")
    if not isinstance(draft.get("expected_mechanism"), str) or not draft["expected_mechanism"].strip():
        errors.append("expected_mechanism must be a non-empty string")
    return errors


def _draft_to_generated_strategy(draft: dict[str, Any], *, objective: str, grounding_hypothesis_ids: list[str]) -> GeneratedStrategy:
    return GeneratedStrategy(
        engineering_objective=objective, mechanism_target=draft["biological_intent"], strategy_class=draft["intervention_class"],
        rationale=draft["expected_mechanism"],
        expected_causal_chain=[draft["biological_intent"], draft["expected_mechanism"], draft.get("expected_benefit", "")],
        evidence_links=[],  # never populated from an LLM draft - see module docstring
        applicability_conditions=list(draft.get("target_entities", [])) + list(draft.get("feasibility_questions", [])),
        known_tradeoffs=list(draft.get("tradeoffs", [])),
        failure_modes=list(draft.get("safety_questions", [])) + list(draft.get("dependencies", [])),
        uncertainty=list(draft.get("assumptions", [])),
        grounding_hypothesis_ids=list(grounding_hypothesis_ids),
    )


def draft_strategies_via_llm(
    client: StructuredGenerationClient, *, objective: str,
    supported_hypotheses: list[dict[str, Any]], primary_metrics: list[dict[str, Any]],
):
    """The LLM call + validation core, with no session/persistence/project
    dependency - shared by `generate_llm_strategy_drafts` below (persists
    valid drafts as real `EngineeringStrategy` rows) and
    `harness.evaluation_metrics.consistency_sampler` (draws N independent
    samples for the same design task without writing any of them into the
    project's real strategy list). Returns `(generated_strategies,
    fallback_used, attempts, health, raw_valid_drafts)` - the raw dicts are
    only needed by callers that persist (to carry `evidence_queries` into
    provenance); the sampler ignores them."""
    hyp_summary = "; ".join(f"{h['mechanism_class']}: {h['statement']}" for h in supported_hypotheses) or "(no supported hypotheses recorded)"
    user_prompt = (
        f"Objective: {objective}\nPrimary metrics: {primary_metrics}\nSupported diagnosis hypotheses: {hyp_summary}\n"
        "Draft 1-2 engineering strategy concepts now, as the JSON object described in your instructions. "
        "Prefer a strategy class that is mechanistically distinct from an obvious literal reading of the hypotheses, "
        "so it adds a genuinely different option to the portfolio rather than restating the rule-based strategy."
    )
    attempts, health = client.generate(system_prompt=_SYSTEM_PROMPT, user_prompt=user_prompt, max_tokens=8000)
    last = attempts[-1]

    fallback_used = True
    valid_drafts: list[dict[str, Any]] = []
    if last.validation_status == "valid" and isinstance(last.parsed, dict):
        drafts = last.parsed.get("strategies")
        if isinstance(drafts, list):
            valid_drafts = [d for d in drafts if isinstance(d, dict) and not _validate_draft(d)]
            if valid_drafts:
                fallback_used = False

    if fallback_used:
        return [], True, attempts, health, []

    grounding_ids = [h["hypothesis_version_id"] for h in supported_hypotheses]
    generated = [_draft_to_generated_strategy(d, objective=objective, grounding_hypothesis_ids=grounding_ids) for d in valid_drafts]
    return generated, False, attempts, health, valid_drafts


def generate_llm_strategy_drafts(
    session: Session, *, project_id: str, design_project_id: str, diagnosis_reference: str, objective: str,
    supported_hypotheses: list[dict[str, Any]], primary_metrics: list[dict[str, Any]], actor_id: str,
    client: StructuredGenerationClient | None = None,
):
    """Returns `(rows, fallback_used)`. On any LLM failure `rows == []` and
    `fallback_used=True` - the caller keeps whatever the deterministic
    `generate_and_persist_strategies` already produced; nothing here ever
    blocks or replaces that call."""
    client = client or StructuredGenerationClient()
    generated, fallback_used, attempts, health, valid_drafts = draft_strategies_via_llm(
        client, objective=objective, supported_hypotheses=supported_hypotheses, primary_metrics=primary_metrics,
    )

    record = record_generation(
        session, project_id=project_id, task_type="strategy", health=health, attempts=attempts,
        prompt_template_id=PROMPT_TEMPLATE_ID, prompt_template_version=PROMPT_TEMPLATE_VERSION,
        input_refs={"design_project_id": design_project_id, "diagnosis_reference": diagnosis_reference},
        output_schema_version=OUTPUT_SCHEMA_VERSION, shared_model_risk=False, fallback_used=fallback_used, actor_id=actor_id,
    )

    if fallback_used:
        return [], True, record

    rows = _persist_strategies(
        session, project_id=project_id, design_project_id=design_project_id, diagnosis_reference=diagnosis_reference,
        strategies=generated, excluded_payload=[], provenance_method="llm_draft_v1", actor_id=actor_id,
        extra_provenance={"generation_id": record.generation_id, "model_id": health.model, "evidence_queries": [d.get("evidence_queries", []) for d in valid_drafts]},
    )
    return rows, False, record

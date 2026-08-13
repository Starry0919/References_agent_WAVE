"""Shared provenance recorder for every task-specific LLM adapter
(`harness.diagnosis.llm_hypothesis_adapter`,
`harness.engineering_design.llm_strategy_adapter`,
`harness.scientific_evaluation.llm_critic_adapter`). One function, one
table (`LLMGenerationRecord`) - task-specific adapters call this rather
than writing their own provenance rows, so `shared_model_risk` and
`fallback_used` bookkeeping stays consistent across all three tasks.
"""
from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from harness.ids import new_id, now
from harness.llm_generation.client import AdapterHealth, GenerationAttempt
from harness.llm_generation.models import LLMGenerationRecord
from harness.memory import event_types as et
from harness.memory.event_store import append_event


def record_generation(
    session: Session, *, project_id: str, task_type: str, health: AdapterHealth, attempts: list[GenerationAttempt],
    prompt_template_id: str, prompt_template_version: str, input_refs: dict[str, str], output_schema_version: str,
    shared_model_risk: bool, fallback_used: bool, actor_id: str,
) -> LLMGenerationRecord:
    last = attempts[-1]
    row = LLMGenerationRecord(
        generation_id=new_id("GEN"), task_type=task_type, provider=health.provider, model_id=health.model,
        model_version_or_snapshot="unknown",  # the OpenAI-compatible protocol does not expose a stable model
        # build/snapshot id from a chat-completions response - recorded honestly as unknown rather than guessed.
        prompt_template_id=prompt_template_id, prompt_template_version=prompt_template_version, input_refs=input_refs,
        output_schema_version=output_schema_version, raw_output_artifact_ref=last.raw_content,
        parsed_output_ref=last.parsed, validation_status=last.validation_status, retry_count=len(attempts) - 1,
        fallback_used=fallback_used, shared_model_risk=shared_model_risk,
        token_usage_if_available=last.usage, latency=sum(a.latency for a in attempts), created_at=now(),
    )
    session.add(row)
    session.flush()
    append_event(
        session, project_id=project_id, event_type=et.GEN_LLM_GENERATION_RECORDED, entity_type="LLMGenerationRecord",
        entity_id=row.generation_id,
        payload={"task_type": task_type, "validation_status": last.validation_status, "retry_count": row.retry_count, "fallback_used": fallback_used, "shared_model_risk": shared_model_risk},
        actor_type="agent", actor_id=actor_id,
    )
    if fallback_used:
        append_event(
            session, project_id=project_id, event_type=et.GEN_LLM_FALLBACK_USED, entity_type="LLMGenerationRecord",
            entity_id=row.generation_id, payload={"task_type": task_type, "reason": last.error or last.validation_status},
            actor_type="agent", actor_id=actor_id,
        )
    return row

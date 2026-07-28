"""Append-only Memory Writeback (doc05 §9/§3.12): every mutating step in
this package already calls `harness.memory.event_store.append_event` into
the shared `ProjectEvent` ledger at the point it happens (intake,
deterministic checks, evidence, model records, reviews, meta-review,
revision, human decision - see each module). This module adds the one
object doc05 §3.12 asks for beyond that raw event trail: a structured
`EvaluationMemoryEvent` that separates the raw feedback reference from the
Reviewer/Agent's *interpretation* of it (lesson, do_not_repeat,
next_iteration_hint, interpretation_uncertainty) - doc05 §9's "原始观测、
Reviewer 解释和 Memory lesson 必须分开保存".
"""
from __future__ import annotations

from sqlalchemy.orm import Session

from harness.ids import new_id, now
from harness.memory import event_types as et
from harness.memory.event_store import append_event
from harness.scientific_evaluation.models import EvaluationCase, EvaluationMemoryEvent


def record_memory_event(
    session: Session, *, case: EvaluationCase, design_id: str, design_version: int, event_type: str,
    raw_feedback_references: list[str] | None = None, critic_findings: list[str] | None = None,
    failed_assumptions: list[str] | None = None, failure_class: str | None = None, lesson: str = "",
    do_not_repeat: list[str] | None = None, next_iteration_hint: list[str] | None = None,
    interpretation_uncertainty: str = "",
) -> EvaluationMemoryEvent:
    row = EvaluationMemoryEvent(
        event_id=new_id("EMEM"), project_id=case.project_id, evaluation_id=case.evaluation_id, design_id=design_id,
        design_version=design_version, event_type=event_type, raw_feedback_references=raw_feedback_references or [],
        critic_findings=critic_findings or [], failed_assumptions=failed_assumptions or [], failure_class=failure_class,
        lesson=lesson, do_not_repeat=do_not_repeat or [], next_iteration_hint=next_iteration_hint or [],
        interpretation_uncertainty=interpretation_uncertainty, created_at=now(),
    )
    session.add(row)
    session.flush()
    append_event(
        session, project_id=case.project_id, event_type=et.EVAL_MEMORY_EVENT_RECORDED, entity_type="EvaluationMemoryEvent",
        entity_id=row.event_id, payload={
            "event_id": row.event_id, "evaluation_id": case.evaluation_id, "design_id": design_id, "event_type": event_type,
            "lesson": lesson, "do_not_repeat": do_not_repeat or [], "next_iteration_hint": next_iteration_hint or [],
            "interpretation_uncertainty": interpretation_uncertainty, "failure_class": failure_class,
        }, actor_type="agent", actor_id="system",
    )
    return row

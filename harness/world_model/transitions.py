"""Component: State Transition Graph service. `record_state_transition` is
the one write path for the Module 4 prompt's core object; `list_transitions`/
`get_transition` are the "querying" half of the Current Implementation
Scope (representation, storage, QUERYING, provenance, visualization -
predictive modeling is explicitly out of scope, so there is no "predict
the next state" function anywhere in this module).
"""
from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from harness.ids import new_id, now
from harness.memory import event_types as et
from harness.memory.event_store import append_event
from harness.world_model.models import (
    TRANSITION_ORIGINS,
    TRANSITION_OUTCOMES,
    TRANSITION_STATUSES,
    StateTransitionRecord,
)

# Module 4 prompt §10: origins that count as validated by default unless the
# caller explicitly downgrades them - `simulation`/`literature_inferred`/
# `hypothesis` default to "inferred"/"hypothesis" instead (never silently
# promoted to "validated").
_DEFAULT_STATUS_FOR_ORIGIN = {
    "experimental": "validated",
    "multi_omics_derived": "validated",
    "simulation": "inferred",
    "literature_inferred": "inferred",
    "expert_curated": "inferred",
    "hypothesis": "hypothesis",
}

REQUIRED_CONTEXT_FIELDS = (
    "host", "strain", "medium", "carbon_source", "oxygen_condition",
    "growth_phase", "engineering_objective",
)
SUPPORTED_HOSTS = {"e. coli k-12", "e.coli k-12", "escherichia coli k-12"}


class InvalidTransitionOrigin(ValueError):
    pass


class InvalidTransitionStatus(ValueError):
    pass


class InvalidTransitionOutcome(ValueError):
    pass


class InvalidTransitionContext(ValueError):
    pass


def record_state_transition(
    session: Session,
    *,
    initial_state: dict[str, Any],
    perturbation: dict[str, Any],
    final_state: dict[str, Any],
    context: dict[str, Any],
    origin: str,
    actor_id: str,
    project_id: str | None = None,
    observed_changes: list[dict[str, Any]] | None = None,
    mechanism: str = "",
    phenotype: str | None = None,
    status: str | None = None,
    evidence_id: str | None = None,
    simulation_run_id: str | None = None,
    outcome: str = "success",
    uncertainty: dict[str, Any] | None = None,
) -> StateTransitionRecord:
    if origin not in TRANSITION_ORIGINS:
        raise InvalidTransitionOrigin(f"origin must be one of {TRANSITION_ORIGINS}, got {origin!r}")
    resolved_status = status or _DEFAULT_STATUS_FOR_ORIGIN[origin]
    if resolved_status not in TRANSITION_STATUSES:
        raise InvalidTransitionStatus(f"status must be one of {TRANSITION_STATUSES}, got {resolved_status!r}")
    if outcome not in TRANSITION_OUTCOMES:
        raise InvalidTransitionOutcome(f"outcome must be one of {TRANSITION_OUTCOMES}, got {outcome!r}")
    missing_context = [field for field in REQUIRED_CONTEXT_FIELDS if not str(context.get(field) or "").strip()]
    if missing_context:
        raise InvalidTransitionContext(f"transition context is missing mandatory field(s): {', '.join(missing_context)}")
    if str(context["host"]).strip().lower() not in SUPPORTED_HOSTS:
        raise InvalidTransitionContext("Module 4 V1.1 is scoped to E. coli K-12; other hosts are not supported")
    objective = str(context["engineering_objective"]).lower()
    if "tryptophan" not in objective or "growth" not in objective:
        raise InvalidTransitionContext("engineering_objective must describe tryptophan improvement while maintaining growth")
    if not initial_state or not final_state or not perturbation:
        raise ValueError("initial_state, perturbation, and final_state are required")
    if not evidence_id and not simulation_run_id:
        raise ValueError("every transition requires evidence_id or simulation_run_id provenance")
    # Prompt §10's ranking is a hard rule, not just documentation: an origin
    # that isn't experimental/multi-omics can never claim "validated".
    if resolved_status == "validated" and origin not in ("experimental", "multi_omics_derived"):
        raise InvalidTransitionStatus(
            f"origin={origin!r} may not be recorded as status='validated' - only 'experimental'/'multi_omics_derived' "
            "origins may be promoted into validated world knowledge (Module 4 prompt §10)"
        )

    transition = StateTransitionRecord(
        transition_id=new_id("TRANS"), project_id=project_id, initial_state=initial_state, perturbation=perturbation,
        final_state=final_state, observed_changes=observed_changes or [], mechanism=mechanism, phenotype=phenotype,
        context=context, origin=origin, status=resolved_status, evidence_id=evidence_id, simulation_run_id=simulation_run_id,
        outcome=outcome, uncertainty=uncertainty, created_by=actor_id, created_at=now(),
    )
    session.add(transition)
    session.flush()

    if project_id is not None:
        append_event(
            session, project_id=project_id, event_type=et.WORLD_MODEL_STATE_TRANSITION_RECORDED, entity_type="StateTransitionRecord",
            entity_id=transition.transition_id,
            payload={"origin": origin, "status": resolved_status, "outcome": outcome, "evidence_id": evidence_id},
            actor_type="agent", actor_id=actor_id,
        )
    return transition


def get_transition(session: Session, transition_id: str) -> StateTransitionRecord | None:
    return session.get(StateTransitionRecord, transition_id)


def list_transitions(
    session: Session,
    *,
    project_id: str | None = None,
    origin: str | None = None,
    status: str | None = None,
    outcome: str | None = None,
    entity_id: str | None = None,
    host: str | None = None,
    perturbation_type: str | None = None,
    limit: int = 50,
) -> list[StateTransitionRecord]:
    """In-Python filtering over the JSON-blob fields (`context`,
    `perturbation`, `initial_state.entities_involved`), same approach
    `harness.evidence_intelligence.retrieval` already uses for its own
    JSON-blob evidence fields - SQLite has no practical JSON-column index
    for these, and the row counts here are project-scoped, not corpus-scale."""
    stmt = select(StateTransitionRecord)
    if project_id is not None:
        stmt = stmt.where(StateTransitionRecord.project_id == project_id)
    if origin is not None:
        stmt = stmt.where(StateTransitionRecord.origin == origin)
    if status is not None:
        stmt = stmt.where(StateTransitionRecord.status == status)
    if outcome is not None:
        stmt = stmt.where(StateTransitionRecord.outcome == outcome)
    rows = list(session.execute(stmt).scalars().all())

    if entity_id is not None:
        rows = [t for t in rows if entity_id in (t.initial_state.get("entities_involved") or []) or entity_id in (t.final_state.get("entities_involved") or [])]
    if host is not None:
        host_lower = host.strip().lower()
        rows = [t for t in rows if host_lower in str(t.context.get("host") or "").lower()]
    if perturbation_type is not None:
        rows = [t for t in rows if t.perturbation.get("type") == perturbation_type]

    rows.sort(key=lambda t: t.created_at, reverse=True)
    return rows[:limit]


def supersede_transition(session: Session, *, transition_id: str, superseded_by_id: str, actor_id: str) -> StateTransitionRecord:
    """Mirrors `harness.diagnosis.evidence.supersede_evidence_item` - a
    later, corrected transition record never overwrites the original; it
    only points back."""
    transition = session.get(StateTransitionRecord, transition_id)
    if transition is None:
        raise ValueError(f"no such state transition: {transition_id}")
    transition.superseded_by_transition_id = superseded_by_id
    session.flush()
    if transition.project_id is not None:
        append_event(
            session, project_id=transition.project_id, event_type=et.WORLD_MODEL_STATE_TRANSITION_SUPERSEDED,
            entity_type="StateTransitionRecord", entity_id=transition_id,
            payload={"superseded_by_transition_id": superseded_by_id}, actor_type="human", actor_id=actor_id,
        )
    return transition


def transition_to_dict(t: StateTransitionRecord) -> dict[str, Any]:
    return {
        "transition_id": t.transition_id, "project_id": t.project_id, "initial_state": t.initial_state,
        "perturbation": t.perturbation, "final_state": t.final_state, "observed_changes": t.observed_changes,
        "mechanism": t.mechanism, "phenotype": t.phenotype, "context": t.context, "origin": t.origin,
        "status": t.status, "evidence_id": t.evidence_id, "simulation_run_id": t.simulation_run_id,
        "outcome": t.outcome, "uncertainty": t.uncertainty, "superseded_by_transition_id": t.superseded_by_transition_id,
        "created_by": t.created_by, "created_at": t.created_at,
    }

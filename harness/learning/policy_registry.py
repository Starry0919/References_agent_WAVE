"""Project-local policy registry (doc 6.8, 12.2's Phase-5 scope): records
per-project heuristic updates redesign ranking can consult. Cross-project/
global propagation is off by default and always routed through the
PolicyUpdateGate - this round implements the registry and the gate
integration, not a real learned policy/optimizer (see 问题02_实施报告.md's
known limitations). `PolicyUpdateGate` is deliberately a different gate
from `KnowledgePromotionGate` (`harness/memory/knowledge_claims.py`): one
governs algorithm/ranking parameters, the other governs scientific
knowledge claims - they do not share a boolean `approved` field.
"""
from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from harness.ids import new_id, now
from harness.memory import event_types as et
from harness.memory.event_store import append_event
from harness.workflow.gates import policy_update_gate


class PolicyUpdateRejected(RuntimeError):
    """The PolicyUpdateGate rejected a cross-project/global update - a
    technical failure tried to drive it, or evidence/approval was
    insufficient."""


def propose_project_local_policy_update(
    session: Session, *, project_id: str, key: str, value: Any, reason: str, actor_id: str
) -> dict[str, Any]:
    """Project-local updates from a single observation are always allowed
    (doc 6.8's default rule) - the gate still runs, with `scope=
    "project_local"` it always passes by construction."""
    gate_result = policy_update_gate(scope="project_local", failure_class=None, has_human_approval=True, evidence_count=1)
    assert gate_result.status.value == "pass"

    record = {
        "policy_id": new_id("POLICY"), "project_id": project_id, "key": key, "value": value, "reason": reason,
        "scope": "project_local", "actor_id": actor_id, "at": now(),
    }
    append_event(
        session, project_id=project_id, event_type=et.POLICY_UPDATE_APPROVED, entity_type="PolicyUpdate",
        entity_id=record["policy_id"], payload=record,
        actor_type="agent" if actor_id == "system" else "human", actor_id=actor_id,
    )
    return record


def propose_cross_project_policy_update(
    session: Session,
    *,
    project_id: str,
    key: str,
    value: Any,
    reason: str,
    failure_class: str | None,
    has_human_approval: bool,
    evidence_count: int,
    actor_id: str,
) -> dict[str, Any]:
    gate_result = policy_update_gate(
        scope="cross_project", failure_class=failure_class, has_human_approval=has_human_approval, evidence_count=evidence_count
    )
    record = {
        "policy_id": new_id("POLICY"), "project_id": project_id, "key": key, "value": value, "reason": reason,
        "scope": "cross_project", "actor_id": actor_id, "at": now(), "gate_status": gate_result.status.value,
    }

    if gate_result.status.value == "fail":
        append_event(
            session, project_id=project_id, event_type=et.POLICY_UPDATE_REJECTED, entity_type="PolicyUpdate",
            entity_id=record["policy_id"], payload={**record, "violations": [v.message for v in gate_result.violations]},
            actor_type="agent", actor_id=actor_id,
        )
        raise PolicyUpdateRejected(f"cross-project policy update rejected: {[v.message for v in gate_result.violations]}")

    if gate_result.status.value == "human_review":
        append_event(
            session, project_id=project_id, event_type=et.POLICY_UPDATE_PROPOSED, entity_type="PolicyUpdate",
            entity_id=record["policy_id"], payload=record, actor_type="agent", actor_id=actor_id,
        )
        return {**record, "status": "pending_human_review"}

    append_event(
        session, project_id=project_id, event_type=et.POLICY_UPDATE_APPROVED, entity_type="PolicyUpdate",
        entity_id=record["policy_id"], payload=record, actor_type="human", actor_id=actor_id,
    )
    return {**record, "status": "approved"}

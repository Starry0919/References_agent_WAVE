"""DesignVersion / EngineeringDecision mutations (doc 8.2, 8.3, 6.11). A
DesignVersion is proposed (immutable content, `status=proposed`), then
either approved (advances the project's current-design pointer) or
rejected - the proposer can never approve their own proposal (design-review
requirement, doc 6.11's "proposer cannot self-approve").
"""
from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from harness.designs.models import DesignVersion, EngineeringDecision
from harness.ids import new_id, now
from harness.memory import event_types as et
from harness.memory.event_store import append_event, snapshot
from harness.projects.service import set_current_design_version

DESIGN_VERSION_SNAPSHOT_FIELDS = (
    "design_version_id", "project_id", "version_label", "parent_version_ids", "branch_name",
    "genotype_manifest", "created_from_learning_cycle_id", "rationale_snapshot_id", "status",
    "proposed_by", "created_at",
)

DECISION_SNAPSHOT_FIELDS = (
    "decision_id", "design_version_id", "target", "target_type", "operation",
    "mechanism_hypothesis_ids", "expected_effects", "risks", "evidence_ids",
    "implementation_spec", "validation_spec", "confidence", "approval_state", "source_run_id",
)


class SelfApprovalError(RuntimeError):
    """A proposer attempted to approve their own proposal (doc 6.11)."""


class MalformedDecisionError(ValueError):
    """A `decisions[]` entry was missing a required field (`target`/
    `operation`) - distinct from the bare `ValueError` this module also
    raises for "no such project", so the route can map this to 422
    (malformed input) instead of 404 (unknown resource)."""


def propose_design_version(
    session: Session,
    *,
    project_id: str,
    version_label: str,
    parent_version_ids: list[str],
    branch_name: str,
    genotype_manifest: dict[str, Any],
    decisions: list[dict[str, Any]],
    proposed_by: str,
    created_from_learning_cycle_id: str | None = None,
    rationale_snapshot_id: str | None = None,
) -> DesignVersion:
    """`project_id` is a DB-enforced foreign key (`ForeignKey("projects.
    project_id")`) and each `decisions[]` entry is an untyped `dict[str,
    Any]` off the wire - checking both up front turns a bad project id or
    a decision missing `target`/`operation` into a clean, mapped error
    instead of an unhandled `IntegrityError` or `KeyError` surfacing as a
    bare 500 (same failure shape as the `delete_project` FK bug)."""
    from harness.projects.models import Project

    if session.get(Project, project_id) is None:
        raise ValueError(f"no such project: {project_id}")
    for i, d in enumerate(decisions):
        missing = [k for k in ("target", "operation") if k not in d]
        if missing:
            raise MalformedDecisionError(f"decisions[{i}] is missing required field(s): {missing}")

    ts = now()
    dv = DesignVersion(
        design_version_id=new_id("DV"),
        project_id=project_id,
        version_label=version_label,
        parent_version_ids=parent_version_ids,
        branch_name=branch_name,
        genotype_manifest=genotype_manifest,
        created_from_learning_cycle_id=created_from_learning_cycle_id,
        rationale_snapshot_id=rationale_snapshot_id,
        status="proposed",
        proposed_by=proposed_by,
        created_at=ts,
    )
    session.add(dv)
    session.flush()

    for i, d in enumerate(decisions):
        decision = EngineeringDecision(
            decision_id=new_id("DEC"),
            design_version_id=dv.design_version_id,
            target=d["target"],
            target_type=d.get("target_type", "gene"),
            operation=d["operation"],
            mechanism_hypothesis_ids=d.get("mechanism_hypothesis_ids", []),
            expected_effects=d.get("expected_effects", []),
            risks=d.get("risks", []),
            evidence_ids=d.get("evidence_ids", []),
            implementation_spec=d.get("implementation_spec", ""),
            validation_spec=d.get("validation_spec", ""),
            confidence=d.get("confidence", "low"),
            approval_state=d.get("approval_state", "proposed"),
            source_run_id=d.get("source_run_id"),
            order_index=i,
        )
        session.add(decision)
    session.flush()

    append_event(
        session,
        project_id=project_id,
        event_type=et.DESIGN_PROPOSED,
        entity_type="DesignVersion",
        entity_id=dv.design_version_id,
        payload={
            **snapshot(dv, DESIGN_VERSION_SNAPSHOT_FIELDS),
            "decisions": [
                snapshot(d, DECISION_SNAPSHOT_FIELDS)
                for d in list_decisions(session, dv.design_version_id)
            ],
        },
        actor_type="agent" if proposed_by == "system" else "human",
        actor_id=proposed_by,
        workflow_run_id=decisions[0].get("source_run_id") if decisions else None,
    )
    return dv


def list_decisions(session: Session, design_version_id: str) -> list[EngineeringDecision]:
    return list(
        session.execute(
            select(EngineeringDecision)
            .where(EngineeringDecision.design_version_id == design_version_id)
            .order_by(EngineeringDecision.order_index)
        ).scalars()
    )


def get_design_version(session: Session, design_version_id: str) -> DesignVersion | None:
    return session.get(DesignVersion, design_version_id)


def approve_design_version(
    session: Session,
    *,
    design_version_id: str,
    approver_id: str,
    expected_project_version: int,
) -> DesignVersion:
    dv = session.get(DesignVersion, design_version_id)
    if dv is None:
        raise ValueError(f"no such design version: {design_version_id}")
    if dv.proposed_by == approver_id:
        raise SelfApprovalError(
            f"actor {approver_id!r} proposed {design_version_id} and cannot also approve it"
        )
    dv.status = "approved"
    session.flush()

    set_current_design_version(
        session,
        project_id=dv.project_id,
        design_version_id=design_version_id,
        expected_version=expected_project_version,
        actor_id=approver_id,
    )

    append_event(
        session,
        project_id=dv.project_id,
        event_type=et.DESIGN_APPROVED,
        entity_type="DesignVersion",
        entity_id=dv.design_version_id,
        payload=snapshot(dv, DESIGN_VERSION_SNAPSHOT_FIELDS),
        actor_type="human",
        actor_id=approver_id,
    )
    return dv

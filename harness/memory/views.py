"""Materialized views. `build_project_status_view`/`build_lineage_graph`
read the live tables (fast path for normal API/UI use); their `_from_ledger`
counterparts reconstruct the same core facts purely by replaying
`ProjectEvent` rows, ignoring the live tables entirely - the proof that the
event ledger is the real source of truth, not a live-table view with an
event log bolted on for show (design-review requirement; exercised by
`tests/projects/test_event_replay.py`).

Honesty note (doc 9.2 names five views: Project Timeline, Design Lineage
Graph, Current Biological State, Experiment Matrix, Hypothesis/Evidence
Graph, Failure Registry): this module provides live + replay-proven
reconstruction for ProjectStatusView and the Design Lineage Graph. Every
write behind the other views still goes through the same event ledger, but
no dedicated replay-only reconstructor exists yet for them this round -
documented in 问题02_实施报告.md's "known limitations", not silently
omitted.
"""
from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from harness.constructs.models import Construct
from harness.designs.lineage import build_lineage_graph
from harness.designs.models import DesignVersion
from harness.experiments.models import Observation
from harness.learning.models import FailureCase
from harness.memory.event_store import replay_project
from harness.orchestrator.models import UnifiedWorkflowRun
from harness.projects.models import IterativeCycleState, Project

_NEXT_ACTION_HINTS = {
    "PROJECT_CONTEXT_READY": "capture baseline design",
    "DESIGN_BASELINE_CAPTURED": "propose a design version",
    "DESIGN_PROPOSED": "review and approve/reject the proposed design",
    "HUMAN_DESIGN_GATE": "awaiting human design approval",
    "BUILD_TEST_HANDOFF": "hand off to wet lab for build/test",
    "WAITING_FOR_RESULTS": "awaiting experiment results",
    "DATA_INGESTION": "ingest experiment data",
    "DATA_QC": "resolve QC issues",
    "OBSERVATION_EXTRACTION": "confirm derived observations",
    "RESULT_INTERPRETATION": "interpret results against expectations",
    "HYPOTHESIS_UPDATE": "update hypotheses",
    "FAILURE_OR_SUCCESS_CLASSIFICATION": "classify outcome",
    "LEARNING_UPDATE_GATE": "approve learning update",
    "REDESIGN_OR_STOP_DECISION": "decide redesign or stop",
}

_ORCHESTRATOR_NEXT_ACTION_HINTS = {
    "INTAKE": "complete project intake",
    "CONTEXT_VALIDATION": "validate project context",
    "DIAGNOSIS": "run or continue bottleneck diagnosis",
    "DESIGN": "generate/review design candidates",
    "EVALUATION": "await scientific evaluation / respond to revision requests",
    "HUMAN_REVIEW": "awaiting human gate decision",
    "SIMULATION": "run predictive simulation",
    "WAITING_FOR_EXPERIMENT": "awaiting experiment results",
    "OBSERVATION_INGESTION": "ingest experiment observations",
    "LEARNING": "run learning/outcome classification",
    "REDESIGN": "start next redesign iteration",
    "COMPLETED": "project cycle completed",
    "BLOCKED": "resolve blocking issue",
    "FAILED": "resolve failed run",
}


def _active_cycle(session: Session, project_id: str) -> IterativeCycleState | None:
    return session.execute(
        select(IterativeCycleState)
        .where(IterativeCycleState.project_id == project_id)
        .order_by(IterativeCycleState.created_at.desc())
    ).scalars().first()


def _latest_orchestrator_run(session: Session, project_id: str) -> UnifiedWorkflowRun | None:
    """The Unified Scientific Workflow Orchestrator (harness/orchestrator/*)
    is a separate state machine from `IterativeCycleState` - the current
    frontend Workspace drives a project exclusively through this run, never
    through the Cycle's own `/cycle/{action}` endpoints. Without this,
    `build_project_status_view` reports `cycle.current_state` (permanently
    stuck at PROJECT_CONTEXT_READY for any orchestrator-driven project) as
    "the project's status", silently disconnected from the real workflow the
    user is actually running.

    Delegates to `harness.orchestrator.service.get_latest_run_for_project` -
    the SAME query the Cycle-action mutual-exclusion guard uses (查缺补漏03
    Phase 1) - so both sides of the single-source-of-truth boundary agree on
    what "this project has adopted the orchestrator" means."""
    from harness.orchestrator.service import get_latest_run_for_project

    return get_latest_run_for_project(session, project_id)


def _active_construct_id(session: Session, design_version_id: str | None) -> str | None:
    if not design_version_id:
        return None
    c = session.execute(select(Construct).where(Construct.design_version_id == design_version_id)).scalars().first()
    return c.construct_id if c else None


def _qc_summary(session: Session, project_id: str) -> dict[str, int]:
    rows = session.execute(select(Observation).where(Observation.project_id == project_id)).scalars().all()
    return {
        "total_observations": len(rows),
        "passed": sum(1 for o in rows if o.qc_status == "passed"),
        "failed": sum(1 for o in rows if o.qc_status == "failed"),
        "pending": sum(1 for o in rows if o.qc_status == "pending"),
    }


def build_project_status_view(session: Session, project_id: str) -> dict[str, Any]:
    project = session.get(Project, project_id)
    if project is None:
        raise ValueError(f"no such project: {project_id}")

    cycle = _active_cycle(session, project_id)
    latest_designs = session.execute(
        select(DesignVersion).where(DesignVersion.project_id == project_id).order_by(DesignVersion.created_at.desc()).limit(3)
    ).scalars().all()
    open_failures = session.execute(
        select(FailureCase).where(FailureCase.project_id == project_id, FailureCase.resolution_status == "open")
    ).scalars().all()

    pending_human_gates = [cycle.pending_gate] if cycle and cycle.status == "waiting_user" and cycle.pending_gate else []
    blockers = [f"open failure case: {f.failure_case_id} ({f.failure_class})" for f in open_failures]
    if cycle and cycle.status == "blocked":
        blockers.append(cycle.termination_reason or "cycle blocked")

    waiting_for = [cycle.current_state] if cycle and cycle.status == "waiting_user" else []
    lifecycle_stage = cycle.current_state if cycle else project.lifecycle_stage
    next_actions = [_NEXT_ACTION_HINTS.get(cycle.current_state, f"advance from {cycle.current_state}")] if cycle else ["create a project cycle"]

    # An orchestrator run reflects the project's REAL current DBTL progress
    # whenever one exists (see `_latest_orchestrator_run`'s docstring) - its
    # phase/status takes priority over the (likely inert) Cycle fields above,
    # rather than being silently ignored.
    run = _latest_orchestrator_run(session, project_id)
    if run is not None:
        lifecycle_stage = run.current_phase
        next_actions = [_ORCHESTRATOR_NEXT_ACTION_HINTS.get(run.current_phase, f"advance orchestrator run from {run.current_phase}")]
        if run.status == "waiting":
            waiting_for.append(run.current_phase)
            if run.pause_reason:
                pending_human_gates.append(run.pause_reason)
        if run.status == "blocked" and run.blocked_reason:
            blockers.append(f"orchestrator run blocked: {run.blocked_reason}")

    return {
        "project_id": project_id,
        "lifecycle_stage": lifecycle_stage,
        "active_design_version": project.current_design_version_id,
        "active_construct": _active_construct_id(session, project.current_design_version_id),
        "active_learning_cycle": cycle.active_learning_cycle_id if cycle else None,
        "latest_accepted_results": sorted(d.design_version_id for d in latest_designs),
        "waiting_for": waiting_for,
        "qc_state": _qc_summary(session, project_id),
        "blockers": blockers,
        "pending_human_gates": pending_human_gates,
        "next_actions": next_actions,
        "last_material_change_at": project.updated_at,
    }


def build_project_status_view_from_ledger(session: Session, project_id: str) -> dict[str, Any]:
    """Reconstructs the core ProjectStatusView facts purely from
    `ProjectEvent` replay - no read of `projects`, `design_versions`, or
    `iterative_cycle_states` tables."""
    replay = replay_project(session, project_id)
    pointers = replay["pointers"]
    entities = replay["entities"]

    design_versions = entities.get("DesignVersion", {})
    latest_designs = sorted(design_versions.values(), key=lambda d: d.get("created_at", 0), reverse=True)[:3]

    failures = entities.get("FailureCase", {})
    open_failures = [f for f in failures.values() if f.get("resolution_status") == "open"]

    return {
        "project_id": pointers.get("project_id", project_id),
        "lifecycle_stage": pointers.get("lifecycle_stage"),
        "active_design_version": pointers.get("current_design_version_id"),
        "latest_accepted_results": sorted(d["design_version_id"] for d in latest_designs),
        "blockers": sorted(f"open failure case: {f['failure_case_id']} ({f['failure_class']})" for f in open_failures),
    }


def build_lineage_graph_from_ledger(session: Session, project_id: str) -> dict[str, Any]:
    replay = replay_project(session, project_id)
    design_versions = replay["entities"].get("DesignVersion", {})
    nodes = sorted(
        (
            {
                "design_version_id": v["design_version_id"],
                "version_label": v["version_label"],
                "status": v["status"],
                "branch_name": v["branch_name"],
            }
            for v in design_versions.values()
        ),
        key=lambda n: n["design_version_id"],
    )
    edges = sorted(
        ({"child": v["design_version_id"], "parent": p} for v in design_versions.values() for p in v.get("parent_version_ids", [])),
        key=lambda e: (e["child"], e["parent"]),
    )
    return {"project_id": project_id, "nodes": nodes, "edges": edges}


__all__ = [
    "build_project_status_view",
    "build_project_status_view_from_ledger",
    "build_lineage_graph",
    "build_lineage_graph_from_ledger",
]

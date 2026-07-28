"""Project-level mutations (doc 8.1, 9.1, 10). Every function here writes
its entity change(s) and a `ProjectEvent` in one transaction - callers
supply an already-open `Session` (typically from `harness.db.session_scope`)
so a caller can compose multiple service calls (e.g. create project + seed
its first cycle state) atomically.
"""
from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from harness.db import check_and_bump_version
from harness.ids import new_id, now
from harness.memory import event_types as et
from harness.memory.event_store import append_event, snapshot
from harness.projects.models import IterativeCycleState, Project

PROJECT_SNAPSHOT_FIELDS = (
    "project_id", "name", "host_definition", "target_product", "objectives", "constraints",
    "current_design_branch", "current_design_version_id", "status", "lifecycle_stage",
    "owners", "version", "created_at", "updated_at",
)

CYCLE_SNAPSHOT_FIELDS = (
    "cycle_state_id", "project_id", "current_state", "active_design_version_id",
    "active_experiment_plan_id", "active_experiment_run_id", "active_learning_cycle_id",
    "pending_gate", "status", "termination_reason", "version",
)


def create_project(
    session: Session,
    *,
    name: str,
    host_definition: dict,
    target_product: str,
    objectives: list[str] | None = None,
    constraints: list[str] | None = None,
    owners: list[str] | None = None,
    actor_id: str,
) -> Project:
    ts = now()
    project = Project(
        project_id=new_id("PROJ"),
        name=name,
        host_definition=host_definition,
        target_product=target_product,
        objectives=objectives or [],
        constraints=constraints or [],
        owners=owners or [actor_id],
        status="active",
        lifecycle_stage="PROJECT_CONTEXT_READY",
        created_at=ts,
        updated_at=ts,
    )
    session.add(project)
    session.flush()
    append_event(
        session,
        project_id=project.project_id,
        event_type=et.PROJECT_CREATED,
        entity_type="Project",
        entity_id=project.project_id,
        payload=snapshot(project, PROJECT_SNAPSHOT_FIELDS),
        actor_type="human",
        actor_id=actor_id,
    )

    cycle = IterativeCycleState(
        cycle_state_id=new_id("CYCLE"),
        project_id=project.project_id,
        current_state="PROJECT_CONTEXT_READY",
        status="running",
        created_at=ts,
        updated_at=ts,
    )
    session.add(cycle)
    session.flush()
    append_event(
        session,
        project_id=project.project_id,
        event_type=et.CYCLE_STATE_CHANGED,
        entity_type="IterativeCycleState",
        entity_id=cycle.cycle_state_id,
        payload=snapshot(cycle, CYCLE_SNAPSHOT_FIELDS),
        actor_type="agent",
        actor_id="system",
    )
    return project


def get_project(session: Session, project_id: str) -> Project | None:
    return session.get(Project, project_id)


def get_active_cycle(session: Session, project_id: str) -> IterativeCycleState | None:
    from sqlalchemy import select

    return session.execute(
        select(IterativeCycleState)
        .where(IterativeCycleState.project_id == project_id)
        .where(IterativeCycleState.status.in_(("running", "waiting_user", "blocked")))
        .order_by(IterativeCycleState.created_at.desc())
    ).scalars().first()


def set_project_status(
    session: Session, *, project_id: str, status: str, expected_version: int, actor_id: str
) -> Project:
    project = session.get(Project, project_id)
    if project is None:
        raise ValueError(f"no such project: {project_id}")
    check_and_bump_version(project, expected_version)
    project.status = status
    project.updated_at = now()
    session.flush()
    append_event(
        session,
        project_id=project_id,
        event_type=et.PROJECT_STATUS_CHANGED,
        entity_type="Project",
        entity_id=project_id,
        payload=snapshot(project, PROJECT_SNAPSHOT_FIELDS),
        actor_type="human",
        actor_id=actor_id,
    )
    return project


def rename_project(
    session: Session, *, project_id: str, name: str, actor_id: str, expected_version: int | None = None
) -> Project:
    """Renames a project in place (Project.name carries no immutability
    guard - see `harness.projects.models`, no `guard_immutable_fields` call
    for this model). `expected_version` is optional so the simple `{name}`
    PATCH body the frontend actually sends still works; when a caller does
    supply it, the usual optimistic-concurrency check still applies."""
    project = session.get(Project, project_id)
    if project is None:
        raise ValueError(f"no such project: {project_id}")
    if expected_version is not None:
        check_and_bump_version(project, expected_version)
    else:
        project.version += 1
    project.name = name
    project.updated_at = now()
    session.flush()
    append_event(
        session,
        project_id=project_id,
        event_type=et.PROJECT_RENAMED,
        entity_type="Project",
        entity_id=project_id,
        payload=snapshot(project, PROJECT_SNAPSHOT_FIELDS),
        actor_type="human",
        actor_id=actor_id,
    )
    return project


def update_project_context(
    session: Session,
    *,
    project_id: str,
    actor_id: str,
    expected_version: int | None = None,
    name: str | None = None,
    host_definition: dict[str, Any] | None = None,
    target_product: str | None = None,
    objectives: list[str] | None = None,
    constraints: list[str] | None = None,
) -> Project:
    """Update the editable scientific context shown on the dashboard."""
    project = session.get(Project, project_id)
    if project is None:
        raise ValueError(f"no such project: {project_id}")
    if expected_version is not None:
        check_and_bump_version(project, expected_version)
    else:
        project.version += 1
    if name is not None:
        project.name = name
    if host_definition is not None:
        project.host_definition = host_definition
    if target_product is not None:
        project.target_product = target_product
    if objectives is not None:
        project.objectives = objectives
    if constraints is not None:
        project.constraints = constraints
    project.updated_at = now()
    session.flush()
    append_event(
        session,
        project_id=project_id,
        event_type=et.PROJECT_CONTEXT_UPDATED,
        entity_type="Project",
        entity_id=project_id,
        payload=snapshot(project, PROJECT_SNAPSHOT_FIELDS),
        actor_type="human",
        actor_id=actor_id,
    )
    return project


def delete_project(session: Session, *, project_id: str) -> None:
    """Cascades a full delete across every project-scoped table this
    repository defines, rather than leaving orphaned diagnosis/design/
    evaluation/simulation/experiment/knowledge/orchestrator data behind
    after only removing the `Project` row.

    Three passes:
      1. Explicit deletes for the handful of child tables that key off
         `workflow_run_id`/`cycle_state_id` via a plain (non-FK) String
         column rather than `project_id` directly (`OrchestratorTransition`,
         `OrchestratorGateDecision`, `ModuleHandoffRecord`,
         `IterativeCycleTransition`) - found by reading their own model
         definitions, not guessed. Not reachable by pass 3's FK-graph walk
         because these columns were never declared as real `ForeignKey`s.
      2/3. A generic transitive-closure sweep over every table that is
         actually part of a project's data, whether it carries `project_id`
         directly (`ProjectEvent`, `IterativeCycleState`, `UnifiedWorkflowRun`,
         `DiagnosisSession`, `EngineeringDesignProject`, `EvaluationCase`,
         `HypothesisFamily`, etc) or only reaches it through one or more
         declared `ForeignKey` hops (e.g. `HypothesisVersion` has no
         `project_id` column at all - only `hypothesis_family_id` ->
         `HypothesisFamily.project_id`). A prior version of this function
         only handled the first kind and left rows like `HypothesisVersion`
         behind; since `hypothesis_family_id` IS a real, DB-enforced FK
         (`PRAGMA foreign_keys=ON` for this SQLite connection - see
         harness/db.py), those leftover child rows aren't "harmless
         orphans" - they block deleting their own parent row, which
         cascades into `DELETE FROM projects` itself failing with
         `sqlite3.IntegrityError`, surfaced to the frontend as a bare 500
         with no JSON body (a real, reported bug, not hypothetical).

         Pass 2 walks `Base.metadata.sorted_tables` in dependency order
         (parents before children - the order every `ForeignKey.column`
         is guaranteed to have already been visited) and records, per
         table, either a direct `project_id` filter or an `IN (subquery)`
         filter built from any FK column pointing at an already-resolved
         parent table. Pass 3 then deletes in the reverse of that order
         (children before parents) so a table's rows are always gone
         before its own parent's DELETE runs. A table with no project_id
         column and no FK to a resolved parent is left alone entirely -
         it genuinely isn't project-scoped data.
    """
    from sqlalchemy import delete, select

    from harness.db import Base
    from harness.orchestrator.models import ModuleHandoffRecord, OrchestratorGateDecision, OrchestratorTransition, UnifiedWorkflowRun
    from harness.projects.models import IterativeCycleTransition

    project = session.get(Project, project_id)
    if project is None:
        raise ValueError(f"no such project: {project_id}")

    run_ids_subq = select(UnifiedWorkflowRun.workflow_run_id).where(UnifiedWorkflowRun.project_id == project_id)
    session.execute(delete(OrchestratorTransition).where(OrchestratorTransition.workflow_run_id.in_(run_ids_subq)))
    session.execute(delete(OrchestratorGateDecision).where(OrchestratorGateDecision.workflow_run_id.in_(run_ids_subq)))
    session.execute(delete(ModuleHandoffRecord).where(ModuleHandoffRecord.workflow_run_id.in_(run_ids_subq)))

    cycle_ids_subq = select(IterativeCycleState.cycle_state_id).where(IterativeCycleState.project_id == project_id)
    session.execute(delete(IterativeCycleTransition).where(IterativeCycleTransition.cycle_state_id.in_(cycle_ids_subq)))

    tables = Base.metadata.sorted_tables
    filters: dict[Any, Any] = {}  # table -> SQLAlchemy boolean clause selecting this project's rows, or absent if out of scope

    for table in tables:  # parents before children
        if "project_id" in table.columns:
            filters[table] = table.c.project_id == project_id
            continue
        scoped_clause = None
        for fk in table.foreign_keys:
            parent_table = fk.column.table
            if parent_table is table or parent_table not in filters:
                continue
            if len(parent_table.primary_key.columns) != 1:
                continue  # composite-PK parent: cannot correlate by a single id column, skip this FK
            hop = fk.parent.in_(select(fk.column).where(filters[parent_table]))
            scoped_clause = hop if scoped_clause is None else (scoped_clause | hop)
        if scoped_clause is not None:
            filters[table] = scoped_clause

    for table in reversed(tables):  # children before parents
        clause = filters.get(table)
        if clause is not None:
            session.execute(delete(table).where(clause))

    session.flush()


def set_current_design_version(
    session: Session, *, project_id: str, design_version_id: str, expected_version: int, actor_id: str
) -> Project:
    """Advances the project's "current" pointer - called by
    `harness/designs/service.py::approve_design_version` after the
    DesignVersion itself is approved. Kept separate from that function so
    Project's optimistic-concurrency check is always exercised through one
    code path."""
    project = session.get(Project, project_id)
    if project is None:
        raise ValueError(f"no such project: {project_id}")
    check_and_bump_version(project, expected_version)
    project.current_design_version_id = design_version_id
    project.updated_at = now()
    session.flush()
    return project

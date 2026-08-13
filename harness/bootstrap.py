"""Imports every ORM model module (so `Base.metadata` is complete) and
registers/runs the schema migrations. Call `bootstrap_schema()` once at
process startup (server lifespan, or explicitly in tests) before touching
the database.
"""
from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.orm import Session

from harness.db import Base, get_session_factory
from harness.migrations import migration, run_migrations

# Import every model module for its side effect (registering tables on
# Base.metadata). Order doesn't matter for SQLAlchemy's mapper
# configuration - only that all of them are imported before create_all().
from harness.analysis import models as _analysis_models  # noqa: F401
from harness.cell_state import models as _cell_state_models  # noqa: F401
from harness.constructs import models as _constructs_models  # noqa: F401
from harness.designs import models as _designs_models  # noqa: F401
from harness.diagnosis import models as _diagnosis_models  # noqa: F401
from harness.engineering_design import models as _engineering_design_models  # noqa: F401
from harness.evaluation_metrics import models as _evaluation_metrics_models  # noqa: F401
from harness.evidence_retrieval import models as _evidence_retrieval_models  # noqa: F401
from harness.experiments import models as _experiments_models  # noqa: F401
from harness.golden_set import models as _golden_set_models  # noqa: F401
from harness.ideas import models as _ideas_models  # noqa: F401
from harness.learning import models as _learning_models  # noqa: F401
from harness.llm_generation import models as _llm_generation_models  # noqa: F401
from harness.orchestrator import models as _orchestrator_models  # noqa: F401
from harness.projects import models as _projects_models  # noqa: F401
from harness.scientific_evaluation import models as _scientific_evaluation_models  # noqa: F401
from harness.scientific_runtime import models as _scientific_runtime_models  # noqa: F401
from harness.virtual_cell import models as _virtual_cell_models  # noqa: F401
from harness.world_model import models as _world_model_models  # noqa: F401


@migration("0001_initial_schema")
def _initial_schema(session: Session) -> None:
    """Defined via the ORM metadata (create_all), not hand-written DDL,
    because every table in this round is brand new - there is no existing
    production data to migrate around. Future migrations against a
    populated database should be hand-written ALTER statements, not
    another create_all call (see 问题02_实施报告.md's migration-runner
    limitations note)."""
    Base.metadata.create_all(bind=session.get_bind(), checkfirst=True)


# doc03's diagnosis fields added to the existing observations/
# hypothesis_versions tables (prefer extending an equivalent object over a
# duplicate schema). ADD COLUMN is idempotent here via an explicit
# existence check, since a fresh DB (0001 already includes these columns,
# as they're part of the current model definitions) and an existing
# Problem-02-only DB (genuinely missing them) both need this migration to
# be a safe no-op / real-add respectively.
_NEW_OBSERVATION_COLUMNS = {
    "reference_or_baseline": "JSON",
    "detection_limit": "FLOAT",
    "replicates": "INTEGER",
    "biological_context_id": "VARCHAR",
    "assay_id": "VARCHAR",
}

_NEW_HYPOTHESIS_VERSION_COLUMNS = {
    "mechanism_class": "VARCHAR",
    "scope": "JSON",
    "causal_graph_nodes": "JSON",
    "causal_graph_edges": "JSON",
    "observations_explained": "JSON",
    "discriminating_predictions": "JSON",
    "falsifiers": "JSON",
    "assumptions": "JSON",
    "temporal_scope": "JSON",
    "related_hypothesis_ids": "JSON",
    "generation_provenance": "JSON",
}


def _existing_columns(session: Session, table: str) -> set[str]:
    rows = session.execute(text(f"PRAGMA table_info({table})")).fetchall()
    return {r[1] for r in rows}


def _add_missing_columns(session: Session, table: str, columns: dict[str, str]) -> None:
    existing = _existing_columns(session, table)
    for col, col_type in columns.items():
        if col not in existing:
            session.execute(text(f"ALTER TABLE {table} ADD COLUMN {col} {col_type}"))


@migration("0002_diagnosis_loop_schema")
def _diagnosis_loop_schema(session: Session) -> None:
    """Problem 03 (Bottleneck Diagnosis Loop)."""
    _add_missing_columns(session, "observations", _NEW_OBSERVATION_COLUMNS)
    _add_missing_columns(session, "hypothesis_versions", _NEW_HYPOTHESIS_VERSION_COLUMNS)
    Base.metadata.create_all(bind=session.get_bind(), checkfirst=True)


@migration("0003_engineering_design_schema")
def _engineering_design_schema(session: Session) -> None:
    """Problem 04 (Engineering Design Generation and Decision Loop). Every
    table this package defines is brand new, so - same reasoning as
    0001_initial_schema - `create_all` is safe and sufficient; there is no
    existing production data in these tables to migrate around."""
    Base.metadata.create_all(bind=session.get_bind(), checkfirst=True)


@migration("0004_scientific_evaluation_schema")
def _scientific_evaluation_schema(session: Session) -> None:
    """Problem 05 (Evaluator & Scientific Critic). Every table this package
    defines is brand new, so - same reasoning as 0001_initial_schema -
    `create_all` is safe and sufficient; there is no existing production
    data in these tables to migrate around."""
    Base.metadata.create_all(bind=session.get_bind(), checkfirst=True)


_NEW_BIOLOGICAL_STATE_SNAPSHOT_COLUMNS = {
    "schema_version": "VARCHAR",
    "version": "INTEGER",
    "temporal_context": "JSON",
    "functional_state": "JSON",
    "physiology": "JSON",
    "field_provenance": "JSON",
    "missing_modalities": "JSON",
    "quality_status": "VARCHAR",
}


@migration("0005_virtual_cell_schema")
def _virtual_cell_schema(session: Session) -> None:
    """Problem 06 (Predictive Simulation Loop & Virtual Cell Integration).
    Every `vc_*` table this package defines is brand new (safe `create_all`,
    same reasoning as 0001/0003/0004); `biological_state_snapshots` is an
    existing Problem-02 table extended with additive columns (same pattern
    as 0002's Observation/HypothesisVersion extension) - a fresh DB already
    has these via the current model definition, an existing DB gets a real
    ADD COLUMN."""
    _add_missing_columns(session, "biological_state_snapshots", _NEW_BIOLOGICAL_STATE_SNAPSHOT_COLUMNS)
    Base.metadata.create_all(bind=session.get_bind(), checkfirst=True)


@migration("0006_unified_orchestrator_schema")
def _unified_orchestrator_schema(session: Session) -> None:
    """Unified Scientific Workflow Orchestrator (六大核心模块统一集成 prompt,
    Phase B). Every `orchestrator_*` table this package defines is brand
    new, so - same reasoning as 0001/0003/0004/0005 - `create_all` is safe
    and sufficient. `project_events.correlation_id`/`workflow_run_id` were
    already columns on the existing table (added, unused, by an earlier
    round) - no ALTER needed there."""
    Base.metadata.create_all(bind=session.get_bind(), checkfirst=True)


_NEW_EVIDENCE_ITEM_COLUMNS = {
    "title": "VARCHAR",
    "authors": "JSON",
    "publication_year": "INTEGER",
    "journal_or_repository": "VARCHAR",
    "doi_or_accession": "VARCHAR",
    "doi_verification_status": "VARCHAR",
    "organism": "VARCHAR",
    "strain": "VARCHAR",
    "genotype": "VARCHAR",
    "intervention": "VARCHAR",
    "comparator": "VARCHAR",
    "measurement": "VARCHAR",
    "direction": "VARCHAR",
    "effect_size_if_reported": "JSON",
    "uncertainty_if_reported": "JSON",
    "extraction_method": "VARCHAR",
    "extraction_status": "VARCHAR",
    "retrieval_provenance": "JSON",
}


@migration("0007_llm_generation_and_evidence_schema")
def _llm_generation_and_evidence_schema(session: Session) -> None:
    """六大核心模块统一集成 prompt Workstream 2 (Scientific Capability
    Adapters). `llm_generation_records` and `evidence_match_reports` are
    brand new (safe `create_all`); `diag_evidence_items` (Problem 03's
    existing table) is extended with additive literature-source columns -
    same pattern as 0002/0005 - all nullable/defaulted so every existing
    row remains valid without backfill."""
    _add_missing_columns(session, "diag_evidence_items", _NEW_EVIDENCE_ITEM_COLUMNS)
    Base.metadata.create_all(bind=session.get_bind(), checkfirst=True)


_NEW_OBSERVATION_CROSS_MODAL_COLUMNS = {
    "modality": "VARCHAR",
    "entity_namespace": "VARCHAR",
    "entity_id": "VARCHAR",
    "batch": "VARCHAR",
}


@migration("0008_cross_modal_and_gem_schema")
def _cross_modal_and_gem_schema(session: Session) -> None:
    """六大核心模块统一集成 prompt Workstream 3 (Phase D: Virtual Cell
    missing requirements). `observations` (Problem 02's existing table) is
    extended with additive modality/entity columns so Cross-Modal
    Consistency can query it directly - no second OmicsObservation table.
    `vc_cross_modal_consistency_reports` is brand new (safe `create_all`)."""
    _add_missing_columns(session, "observations", _NEW_OBSERVATION_CROSS_MODAL_COLUMNS)
    Base.metadata.create_all(bind=session.get_bind(), checkfirst=True)


@migration("0009_golden_set_schema")
def _golden_set_schema(session: Session) -> None:
    """六大核心模块统一集成 prompt Workstream 4 (Phase E: Scientific Golden
    Set). Every `golden_*` table is brand new (safe `create_all`)."""
    Base.metadata.create_all(bind=session.get_bind(), checkfirst=True)


_NEW_DIAGNOSIS_SESSION_COLUMNS = {
    "pending_request_context": "JSON",
}


@migration("0010_diagnosis_resume_context_schema")
def _diagnosis_resume_context_schema(session: Session) -> None:
    """Fix for the resume_diagnosis orphan-session bug: `diag_sessions`
    (Problem 03's existing table) is extended with an additive
    `pending_request_context` column - same pattern as 0002/0005/0007/0008 -
    nullable/defaulted so every existing row remains valid without backfill."""
    _add_missing_columns(session, "diag_sessions", _NEW_DIAGNOSIS_SESSION_COLUMNS)
    Base.metadata.create_all(bind=session.get_bind(), checkfirst=True)


_NEW_ORCHESTRATOR_RUN_COLUMNS = {
    "cycle_state_id": "VARCHAR",
}


@migration("0011_state_machine_convergence_schema")
def _state_machine_convergence_schema(session: Session) -> None:
    """P1 architecture-convergence round (查缺补漏03): `orchestrator_workflow_runs`
    gets an additive `cycle_state_id` column (which Cycle this run was
    created under, for traceability - see service.py's create_run). And the
    reverse-lookup gap this round fixes: `diag_sessions`/`eval_cases`/
    `golden_case_evaluation_runs` already declared a `workflow_run_id`
    column but no orchestrator adapter ever wrote it - those tables' columns
    already exist in the ORM model (0001/0002/0004/0009), so only
    `orchestrator_workflow_runs.cycle_state_id` needs an ALTER here; the
    other three are populated going forward by the adapters themselves
    (harness/orchestrator/adapters.py), no schema change needed for them."""
    _add_missing_columns(session, "orchestrator_workflow_runs", _NEW_ORCHESTRATOR_RUN_COLUMNS)
    Base.metadata.create_all(bind=session.get_bind(), checkfirst=True)


@migration("0012_project_ideas_schema")
def _project_ideas_schema(session: Session) -> None:
    """Idea Capture ("sudden inspiration" entry point). `project_ideas` is a
    brand-new table, so - same reasoning as 0001/0003/0004/0009 -
    `create_all` is safe and sufficient; there is no existing production
    data in this table to migrate around."""
    Base.metadata.create_all(bind=session.get_bind(), checkfirst=True)


_NEW_EVIDENCE_MATCH_REPORT_COLUMNS = {
    "project_id": "VARCHAR",
}


@migration("0013_evidence_match_report_project_id")
def _evidence_match_report_project_id(session: Session) -> None:
    """Fix for the Knowledge page's "适用范围 / 情境匹配报告" panel showing the
    same rows forever regardless of which project is open: it was querying
    `evidence_match_reports` with no project scope at all (there was no
    column to scope by), so it always rendered every match report ever
    computed, for every project, since the table was created. `project_id`
    is additive/nullable - existing rows stay valid without backfill, same
    pattern as 0002/0005/0007/0008/0010/0011."""
    _add_missing_columns(session, "evidence_match_reports", _NEW_EVIDENCE_MATCH_REPORT_COLUMNS)
    Base.metadata.create_all(bind=session.get_bind(), checkfirst=True)


_NEW_DESIGN_PROJECT_COLUMNS = {
    "reference_ddr_ids": "JSON",
}


@migration("0014_evaluation_metrics_schema")
def _evaluation_metrics_schema(session: Session) -> None:
    """260718 设计文档 §7 evaluation metrics: additive `reference_ddr_ids` on
    `design_projects` (nullable/defaulted, same pattern as 0002/0005/0007/
    0008/0010/0011/0013) plus the brand-new `consistency_sampling_runs`
    table (safe `create_all`, same reasoning as 0009/0013)."""
    _add_missing_columns(session, "design_projects", _NEW_DESIGN_PROJECT_COLUMNS)
    Base.metadata.create_all(bind=session.get_bind(), checkfirst=True)


_NEW_DESIGN_STRATEGY_COLUMNS = {
    "historical_priors": "JSON",
    "design_prior": "JSON",
}


@migration("0015_engineering_strategy_historical_priors")
def _engineering_strategy_historical_priors(session: Session) -> None:
    """ELISER-inspired historical design memory (harness/engineering_design/
    strategy_prior_retrieval.py): additive `historical_priors`/`design_prior`
    on `design_strategies` (nullable/defaulted, same pattern as 0002/0005/
    0007/0008/0010/0011/0013/0014) - existing rows stay valid without
    backfill; both fields are populated only for strategies generated after
    this migration runs."""
    _add_missing_columns(session, "design_strategies", _NEW_DESIGN_STRATEGY_COLUMNS)
    Base.metadata.create_all(bind=session.get_bind(), checkfirst=True)


@migration("0016_observation_grounding_schema")
def _observation_grounding_schema(session: Session) -> None:
    """P0-1: create the new descriptive EngineeringProblem table."""
    Base.metadata.create_all(bind=session.get_bind(), checkfirst=True)


_NEW_CANDIDATE_REFERENCE_OPTIMIZATION_COLUMNS = {
    "diagnosis_finding_ids": "JSON",
    "decision_state": "VARCHAR",
}


@migration("0017_reference_optimization_schema")
def _reference_optimization_schema(session: Session) -> None:
    """Typed findings, evidence gaps, model evaluations and candidate state."""
    _add_missing_columns(session, "design_candidates", _NEW_CANDIDATE_REFERENCE_OPTIMIZATION_COLUMNS)
    Base.metadata.create_all(bind=session.get_bind(), checkfirst=True)


def bootstrap_schema() -> list[str]:
    """Idempotent: safe to call on every process start. Returns the
    migration versions newly applied this call (empty if already current)."""
    return run_migrations(get_session_factory())

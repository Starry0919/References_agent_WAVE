"""Problem 04 (Engineering Design Generation and Decision Loop) tables.

Converts a gated Problem-03 `DiagnosisDecision` into a versioned,
evaluable, revisable engineering-design object graph, and closes the loop
back into Problem 02's Memory (the shared `ProjectEvent` ledger) and
`harness.designs` persisted `DesignVersion` once a candidate is approved
for build.

Design choice (audit finding, see `harness/diagnosis/handoff.py`'s own
docstring): Problem 4 had no standalone implementation in this codebase -
only a design doc. The existing `harness.designs.models.DesignVersion` is
Problem 02's *persisted, already-approved* genotype record (populated
today only from Problem 01's workflow output). This package does not
duplicate that table; instead `CandidateDesign` is the new, richer,
versioned *engineering* object doc04 3.5/3.9 requires (mechanism,
evidence, trade-off, buildability, readiness, lineage) - a `CandidateDesign`
only becomes a `harness.designs.models.DesignVersion` at
`approved_for_build` time, via `harness/engineering_design/
design_version_bridge.py`. This mirrors exactly how `harness/designs/
adapters.py` already bridges Problem 01's in-memory `EngineeringDecision`
into that same persisted table - Problem 4 is a second, real producer for
the same sink, not a parallel persistence layer.

Likewise there is no separate `DesignMemoryEvent` table: every mutating
service function in this package calls `harness.memory.event_store.
append_event` into the SAME `ProjectEvent` ledger Problems 01-03 use
(doc04 §6's "禁止...把 Memory 当聊天摘要" / doc03 6.3's "不得平行创建
...第二套历史存储" precedent) - the full-row snapshot payload already
carries every field doc04 3.9's `DesignMemoryEvent` names.
"""
from __future__ import annotations

from sqlalchemy import JSON, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from harness.db import Base, guard_immutable_fields

# ---------------------------------------------------------------------------
# doc04 §4.1: the 18-state Engineering Design workflow.
# ---------------------------------------------------------------------------
DESIGN_WORKFLOW_STATES = (
    "diagnostic_blocked", "objective_draft", "strategy_generated", "portfolio_generated",
    "evaluation_in_progress", "revision_required", "portfolio_evaluated", "planning_ready",
    "awaiting_human_approval", "approved_for_build", "rejected", "build_in_progress",
    "test_pending", "tested", "learning_update", "next_iteration", "diagnosis_reopened", "completed",
)

# doc04 3.3.
STRATEGY_CLASSES = (
    "precursor_supply", "feedback_relief", "competing_flux_control", "cofactor_energy_balancing",
    "resource_burden_management", "dynamic_regulation", "transport_tolerance_engineering",
    "process_condition_engineering", "diagnostic_measurement_probe",
)

# doc04 3.4.
TARGET_TYPES = ("gene", "reaction", "metabolite", "regulatory_element", "pathway", "process_parameter")
MODIFICATION_OPERATIONS = (
    "knockout", "knockdown", "attenuation", "overexpression", "allele_replacement",
    "promoter_edit", "rbs_edit", "gene_insertion", "dynamic_control", "process_only",
)

# doc04 3.6.
PORTFOLIO_ROLES = (
    "reference_or_control", "low_risk", "high_upside", "information_gain", "process_first", "fallback",
)

# doc04 §11.
EVIDENCE_TIERS = (
    "experimental_evidence", "model_computation", "curated_knowledge",
    "general_biological_knowledge", "expert_or_llm_judgment", "unknown",
)

# doc04 §4.4.
EVALUATOR_STATUSES = ("pass", "warning", "fail", "insufficient_evidence", "not_computed")
EVALUATOR_NAMES = (
    "MechanismEvaluator", "EvidenceEvaluator", "CounterfactualEvaluator", "TradeoffEvaluator",
    "BuildabilityEvaluator", "ValidationEvaluator", "SafetyGovernanceEvaluator", "DiversityEvaluator",
)

# doc04 §2.6.
CANDIDATE_READINESS_LEVELS = ("conceptual", "evaluated", "planning_ready", "build_ready")
CANDIDATE_STATUSES = (
    "proposed", "revised", "selected", "rejected", "approved_for_build", "built", "tested", "retired",
)

# doc04 3.9 - build/test outcome failure classes (distinct from
# `harness.learning.models.FAILURE_CLASSES`, which is Problem 02's coarser
# taxonomy; doc04 §3.9 asks for this specific, richer set).
DESIGN_FAILURE_CLASSIFICATIONS = (
    "assembly_failed", "transformation_failed", "assay_failed", "measurement_invalid",
    "biological_underperformance", "unexpected_tradeoff", "success", "inconclusive",
)

AUTONOMY_LEVELS = ("recommend_only", "build_with_approval", "full_autonomy")


class EngineeringDesignProject(Base):
    """doc04 3.1, merged with the state-machine session role
    `harness.diagnosis.models.DiagnosisSession` plays for Problem 03 (same
    codebase precedent: one row is both durable context AND the sole
    `status` pointer `EngineeringDesignLoopController` writes)."""

    __tablename__ = "design_projects"

    design_project_id: Mapped[str] = mapped_column(String, primary_key=True)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.project_id"), index=True)
    schema_version: Mapped[str] = mapped_column(String, default="1")
    chassis: Mapped[str] = mapped_column(String, default="unknown")
    chassis_version_or_genotype: Mapped[str] = mapped_column(String, default="unknown")
    baseline_state_id: Mapped[str | None] = mapped_column(String, default=None)
    diagnosis_session_id: Mapped[str] = mapped_column(String, index=True)
    diagnosis_decision_id: Mapped[str] = mapped_column(String)
    diagnosis_version: Mapped[int] = mapped_column(Integer)
    temporal_and_environmental_context: Mapped[dict] = mapped_column(JSON, default=dict)
    primary_metrics: Mapped[list] = mapped_column(JSON, default=list)
    secondary_metrics: Mapped[list] = mapped_column(JSON, default=list)
    hard_constraints: Mapped[list] = mapped_column(JSON, default=list)
    preferences_or_weights: Mapped[list] = mapped_column(JSON, default=list)
    available_resources: Mapped[dict] = mapped_column(JSON, default=dict)
    autonomy_level: Mapped[str] = mapped_column(String, default="recommend_only")
    required_human_gates: Mapped[list] = mapped_column(JSON, default=lambda: ["build_approval"])
    status: Mapped[str] = mapped_column(String, default="diagnostic_blocked")
    revision_count: Mapped[int] = mapped_column(Integer, default=0)
    created_by: Mapped[str] = mapped_column(String)
    created_at: Mapped[float] = mapped_column(Float)
    updated_at: Mapped[float] = mapped_column(Float)
    version: Mapped[int] = mapped_column(Integer, default=1)


guard_immutable_fields(
    EngineeringDesignProject,
    mutable_fields={
        "status", "revision_count", "updated_at", "version", "required_human_gates",
        "primary_metrics", "secondary_metrics", "hard_constraints", "preferences_or_weights", "available_resources",
    },
)


class DesignWorkflowTransition(Base):
    """State-transition audit trail, mirrors `harness.diagnosis.models.
    DiagnosisTransition`."""

    __tablename__ = "design_workflow_transitions"

    transition_id: Mapped[str] = mapped_column(String, primary_key=True)
    design_project_id: Mapped[str] = mapped_column(ForeignKey("design_projects.design_project_id"), index=True)
    state: Mapped[str] = mapped_column(String)
    status: Mapped[str] = mapped_column(String)  # completed|failed
    gate_result: Mapped[dict | None] = mapped_column(JSON, default=None)
    selected_next_state: Mapped[str | None] = mapped_column(String, default=None)
    selection_reason: Mapped[str] = mapped_column(String, default="")
    actor_id: Mapped[str] = mapped_column(String)
    started_at: Mapped[float] = mapped_column(Float)
    ended_at: Mapped[float | None] = mapped_column(Float, default=None)


class DiagnosisHandoffRecord(Base):
    """doc04 3.2. Adapter output, never a raw summary string - carries
    every field a `DiagnosisDecision` provides plus adapter provenance
    (missing fields, staleness). `is_stale=True` the moment a newer
    `DiagnosisDecision` version exists for the same session (see
    `harness/engineering_design/handoff.py::mark_stale_if_diagnosis_advanced`)
    - never silently kept in use."""

    __tablename__ = "design_diagnosis_handoffs"

    handoff_id: Mapped[str] = mapped_column(String, primary_key=True)
    design_project_id: Mapped[str] = mapped_column(ForeignKey("design_projects.design_project_id"), index=True)
    diagnosis_session_id: Mapped[str] = mapped_column(String, index=True)
    diagnosis_decision_id: Mapped[str] = mapped_column(String)
    diagnosis_version: Mapped[int] = mapped_column(Integer)
    handoff_kind: Mapped[str] = mapped_column(String)  # diagnosis_decision|diagnostic_probe
    decision_status: Mapped[str] = mapped_column(String)  # DiagnosisDecision.stopping_reason
    supported_hypotheses: Mapped[list] = mapped_column(JSON, default=list)
    unresolved_alternatives: Mapped[list] = mapped_column(JSON, default=list)
    counterevidence: Mapped[list] = mapped_column(JSON, default=list)
    confidence: Mapped[dict] = mapped_column(JSON, default=dict)
    uncertainty: Mapped[list] = mapped_column(JSON, default=list)
    evidence_references: Mapped[list] = mapped_column(JSON, default=list)
    engineering_value_assessment: Mapped[dict | None] = mapped_column(JSON, default=None)
    temporal_and_environmental_context: Mapped[dict] = mapped_column(JSON, default=dict)
    approved_for_design: Mapped[bool] = mapped_column(default=False)
    approval_reference: Mapped[dict | None] = mapped_column(JSON, default=None)
    adapter_provenance: Mapped[dict] = mapped_column(JSON, default=dict)  # {missing_fields: [...], adapter_version: ...}
    is_stale: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[float] = mapped_column(Float)


guard_immutable_fields(
    DiagnosisHandoffRecord, mutable_fields={"approved_for_design", "approval_reference", "is_stale"}
)


class EngineeringStrategy(Base):
    """doc04 3.3. Strategy precedes any concrete modification - the
    Candidate Portfolio Generator may only instantiate genetic
    modifications that trace back to one of these."""

    __tablename__ = "design_strategies"

    strategy_id: Mapped[str] = mapped_column(String, primary_key=True)
    design_project_id: Mapped[str] = mapped_column(ForeignKey("design_projects.design_project_id"), index=True)
    diagnosis_reference: Mapped[str] = mapped_column(String)  # DiagnosisHandoffRecord.handoff_id
    engineering_objective: Mapped[str] = mapped_column(String)
    mechanism_target: Mapped[str] = mapped_column(String)
    strategy_class: Mapped[str] = mapped_column(String)  # one of STRATEGY_CLASSES
    rationale: Mapped[str] = mapped_column(String, default="")
    expected_causal_chain: Mapped[list] = mapped_column(JSON, default=list)
    evidence_links: Mapped[list] = mapped_column(JSON, default=list)
    applicability_conditions: Mapped[list] = mapped_column(JSON, default=list)
    known_tradeoffs: Mapped[list] = mapped_column(JSON, default=list)
    failure_modes: Mapped[list] = mapped_column(JSON, default=list)
    excluded_strategy_reasons: Mapped[list] = mapped_column(JSON, default=list)  # [{strategy_class, reason}]
    uncertainty: Mapped[list] = mapped_column(JSON, default=list)
    status: Mapped[str] = mapped_column(String, default="proposed")  # proposed|selected|rejected
    rejection_reason: Mapped[str | None] = mapped_column(String, default=None)
    provenance: Mapped[dict] = mapped_column(JSON, default=dict)
    created_by: Mapped[str] = mapped_column(String)
    created_at: Mapped[float] = mapped_column(Float)


guard_immutable_fields(EngineeringStrategy, mutable_fields={"status", "rejection_reason"})


class CandidateDesign(Base):
    """doc04 3.5, also playing doc04 3.9's `DesignVersion` role scoped to
    this package's own lineage (never the same row as `harness.designs.
    models.DesignVersion` - see module docstring). A revision that changes
    genetic content is a NEW row (`design_version` incremented,
    `parent_design_ids` set) - `guard_immutable_fields` below enforces that
    the authored/scientific content can never be edited in place; only
    pipeline-derived enrichment fields (evaluation/build-plan pointers,
    readiness, status) may progress on the same row.
    """

    __tablename__ = "design_candidates"

    design_id: Mapped[str] = mapped_column(String, primary_key=True)
    design_project_id: Mapped[str] = mapped_column(ForeignKey("design_projects.design_project_id"), index=True)
    lineage_id: Mapped[str] = mapped_column(String, index=True)  # stable across revisions of "the same" candidate
    design_version: Mapped[int] = mapped_column(Integer, default=1)
    parent_design_ids: Mapped[list] = mapped_column(JSON, default=list)
    strategy_ids: Mapped[list] = mapped_column(JSON, default=list)
    portfolio_id: Mapped[str | None] = mapped_column(String, default=None, index=True)
    portfolio_role: Mapped[str | None] = mapped_column(String, default=None)  # one of PORTFOLIO_ROLES
    genetic_modifications: Mapped[list] = mapped_column(JSON, default=list)  # list[GeneticModification-shaped dict]
    regulatory_architecture: Mapped[dict] = mapped_column(JSON, default=dict)
    process_modifications: Mapped[list] = mapped_column(JSON, default=list)
    expected_mechanism: Mapped[str] = mapped_column(String, default="")
    causal_chain: Mapped[list] = mapped_column(JSON, default=list)
    interaction_and_epistasis_assumptions: Mapped[list] = mapped_column(JSON, default=list)
    evidence_links: Mapped[list] = mapped_column(JSON, default=list)
    counterfactual_requests: Mapped[list] = mapped_column(JSON, default=list)
    counterfactual_results: Mapped[list] = mapped_column(JSON, default=list)
    uncertainty_and_model_conflicts: Mapped[list] = mapped_column(JSON, default=list)
    tradeoff_profile: Mapped[dict | None] = mapped_column(JSON, default=None)
    buildability_assessment: Mapped[dict | None] = mapped_column(JSON, default=None)
    build_test_package_id: Mapped[str | None] = mapped_column(String, default=None)
    debug_and_fallback_plan: Mapped[dict | None] = mapped_column(JSON, default=None)
    safety_flags: Mapped[list] = mapped_column(JSON, default=list)
    readiness: Mapped[str] = mapped_column(String, default="conceptual")  # one of CANDIDATE_READINESS_LEVELS
    status: Mapped[str] = mapped_column(String, default="proposed")  # one of CANDIDATE_STATUSES
    rejection_reasons: Mapped[list] = mapped_column(JSON, default=list)
    source_diagnosis_version: Mapped[int] = mapped_column(Integer)
    created_from_revision_reason: Mapped[str | None] = mapped_column(String, default=None)
    proposed_by: Mapped[str] = mapped_column(String)
    created_at: Mapped[float] = mapped_column(Float)


guard_immutable_fields(
    CandidateDesign,
    mutable_fields={
        "portfolio_id", "portfolio_role", "evidence_links", "counterfactual_requests", "counterfactual_results",
        "uncertainty_and_model_conflicts", "tradeoff_profile", "buildability_assessment", "build_test_package_id",
        "debug_and_fallback_plan", "safety_flags", "readiness", "status", "rejection_reasons",
    },
)


class DesignPortfolio(Base):
    """doc04 3.6. `absent_roles` is the structured-absence record required
    when a role (e.g. `process_first`) is not scientifically applicable -
    never a silently missing role."""

    __tablename__ = "design_portfolios"

    portfolio_id: Mapped[str] = mapped_column(String, primary_key=True)
    design_project_id: Mapped[str] = mapped_column(ForeignKey("design_projects.design_project_id"), index=True)
    candidate_design_ids: Mapped[list] = mapped_column(JSON, default=list)
    role_assignments: Mapped[dict] = mapped_column(JSON, default=dict)  # {role: [design_id, ...]}
    absent_roles: Mapped[list] = mapped_column(JSON, default=list)  # [{role, reason}]
    diversity_assessment: Mapped[dict | None] = mapped_column(JSON, default=None)
    status: Mapped[str] = mapped_column(String, default="generated")  # generated|evaluated|decided
    decision: Mapped[dict | None] = mapped_column(JSON, default=None)  # PortfolioDecision snapshot
    created_by: Mapped[str] = mapped_column(String)
    created_at: Mapped[float] = mapped_column(Float)


guard_immutable_fields(DesignPortfolio, mutable_fields={"status", "decision", "diversity_assessment", "candidate_design_ids", "role_assignments"})


class DesignEvaluation(Base):
    """doc04 3.7. Append-only: a revision never overwrites a prior
    evaluation - `harness/engineering_design/evaluators/runner.py` always
    creates a new row, even re-evaluating the same (design_id,
    design_version). `pareto_status` is the sole mutable field: it is a
    cross-candidate annotation computed once every sibling in the same
    portfolio has its own evaluation row, so it is filled in after this
    row's own findings are already immutable, never changing any finding
    itself."""

    __tablename__ = "design_evaluations"

    evaluation_id: Mapped[str] = mapped_column(String, primary_key=True)
    design_id: Mapped[str] = mapped_column(ForeignKey("design_candidates.design_id"), index=True)
    design_version: Mapped[int] = mapped_column(Integer)
    objective_vector: Mapped[list] = mapped_column(JSON, default=list)
    hard_constraint_results: Mapped[list] = mapped_column(JSON, default=list)
    mechanism_consistency: Mapped[dict] = mapped_column(JSON, default=dict)
    evidence_assessment: Mapped[dict] = mapped_column(JSON, default=dict)
    model_results: Mapped[list] = mapped_column(JSON, default=list)
    model_agreement_and_conflicts: Mapped[dict | None] = mapped_column(JSON, default=None)
    sensitivity_and_robustness: Mapped[dict | None] = mapped_column(JSON, default=None)
    tradeoff_profile: Mapped[dict] = mapped_column(JSON, default=dict)
    buildability: Mapped[dict] = mapped_column(JSON, default=dict)
    validation_feasibility: Mapped[dict] = mapped_column(JSON, default=dict)
    expected_information_gain: Mapped[str] = mapped_column(String, default="unknown")
    safety_and_governance: Mapped[dict] = mapped_column(JSON, default=dict)
    evaluator_findings: Mapped[list] = mapped_column(JSON, default=list)
    required_revisions: Mapped[list] = mapped_column(JSON, default=list)
    pareto_status: Mapped[str | None] = mapped_column(String, default=None)
    recommendation: Mapped[str] = mapped_column(String, default="insufficient_evidence")
    provenance: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[float] = mapped_column(Float)


guard_immutable_fields(DesignEvaluation, mutable_fields={"pareto_status"})


class BuildTestPackage(Base):
    """doc04 3.8: the minimal real experiment-execution plan. `readiness`
    is capped below `build_ready` whenever a required field is missing -
    see `harness/engineering_design/build_test_planner.py::assess_readiness`."""

    __tablename__ = "design_build_test_packages"

    package_id: Mapped[str] = mapped_column(String, primary_key=True)
    design_id: Mapped[str] = mapped_column(ForeignKey("design_candidates.design_id"), index=True)
    design_version: Mapped[int] = mapped_column(Integer)
    construction_concept: Mapped[str] = mapped_column(String, default="")
    build_steps_or_milestones: Mapped[list] = mapped_column(JSON, default=list)
    required_materials: Mapped[list] = mapped_column(JSON, default=list)
    required_capabilities_or_instruments: Mapped[list] = mapped_column(JSON, default=list)
    available_resource_matches: Mapped[list] = mapped_column(JSON, default=list)
    missing_information_or_resources: Mapped[list] = mapped_column(JSON, default=list)
    controls: Mapped[list] = mapped_column(JSON, default=list)
    replication_plan: Mapped[dict] = mapped_column(JSON, default=dict)
    sampling_plan: Mapped[list] = mapped_column(JSON, default=list)
    qc_checkpoints: Mapped[list] = mapped_column(JSON, default=list)
    target_readouts: Mapped[list] = mapped_column(JSON, default=list)
    mechanism_readouts: Mapped[list] = mapped_column(JSON, default=list)
    expected_observations: Mapped[list] = mapped_column(JSON, default=list)
    decision_rules: Mapped[list] = mapped_column(JSON, default=list)
    failure_signatures: Mapped[list] = mapped_column(JSON, default=list)
    debug_plan: Mapped[list] = mapped_column(JSON, default=list)
    fallback_plan: Mapped[list] = mapped_column(JSON, default=list)
    estimated_time_cost_and_risk: Mapped[dict] = mapped_column(JSON, default=dict)
    readiness: Mapped[str] = mapped_column(String, default="conceptual")  # conceptual|planning_ready|build_ready
    created_by: Mapped[str] = mapped_column(String)
    created_at: Mapped[float] = mapped_column(Float)


guard_immutable_fields(BuildTestPackage, mutable_fields={"readiness"})


class HumanApprovalRecord(Base):
    """doc04 §2.7: the explicit Human Approval Gate record - approver
    identity/role, decision, conditions, and reason, distinct from any
    chat-text confirmation. Scoped to one `CandidateDesign` version, never
    implying approval of a later revision (same discipline as `harness.
    workflow.contracts.ApprovalRecord.scope`)."""

    __tablename__ = "design_human_approvals"

    approval_id: Mapped[str] = mapped_column(String, primary_key=True)
    design_id: Mapped[str] = mapped_column(ForeignKey("design_candidates.design_id"), index=True)
    design_version: Mapped[int] = mapped_column(Integer)
    scope: Mapped[str] = mapped_column(String)  # what this approval covers, e.g. "approved_for_build"
    approver_id: Mapped[str] = mapped_column(String)
    approver_role: Mapped[str] = mapped_column(String, default="")
    decision: Mapped[str] = mapped_column(String)  # approved|rejected
    conditions: Mapped[list] = mapped_column(JSON, default=list)
    reason: Mapped[str] = mapped_column(String, default="")
    created_at: Mapped[float] = mapped_column(Float)


class CounterfactualRun(Base):
    """doc04 §9's standardized counterfactual request/result schema,
    scoped to one `CandidateDesign`. Reuses `harness.diagnosis.
    model_adapters` (GEM/vEcoli/kinetic) - the same real-or-honestly-
    unavailable adapter registry Problem 03 Phase 3 built, not a second
    model-execution stack."""

    __tablename__ = "design_counterfactual_runs"

    run_id: Mapped[str] = mapped_column(String, primary_key=True)
    design_id: Mapped[str] = mapped_column(ForeignKey("design_candidates.design_id"), index=True)
    request: Mapped[dict] = mapped_column(JSON, default=dict)  # {intervention_or_query, discriminates, baseline_state_ref}
    adapter_name: Mapped[str] = mapped_column(String)
    model_name: Mapped[str] = mapped_column(String, default="")
    model_version: Mapped[str] = mapped_column(String, default="")
    capability_status: Mapped[str] = mapped_column(String)  # available|unavailable|out_of_domain
    runtime_status: Mapped[str] = mapped_column(String, default="not_computed")
    outputs: Mapped[dict] = mapped_column(JSON, default=dict)
    uncertainty: Mapped[dict | None] = mapped_column(JSON, default=None)
    domain_flags: Mapped[list] = mapped_column(JSON, default=list)
    assumptions: Mapped[list] = mapped_column(JSON, default=list)
    status: Mapped[str] = mapped_column(String, default="not_computed")  # not_computed|computed|qualitative_expectation
    qualitative_expectation_text: Mapped[str | None] = mapped_column(String, default=None)
    reproducibility_ref: Mapped[dict] = mapped_column(JSON, default=dict)
    log_summary: Mapped[str] = mapped_column(String, default="")
    created_at: Mapped[float] = mapped_column(Float)


class DesignOutcomeRecord(Base):
    """doc04 3.9's outcome-ingestion half: expected-vs-observed residuals
    and failure classification for one built/tested `CandidateDesign`.
    Fully immutable/append-only - a re-analysis creates a new row rather
    than editing the original finding."""

    __tablename__ = "design_outcome_records"

    outcome_id: Mapped[str] = mapped_column(String, primary_key=True)
    design_id: Mapped[str] = mapped_column(ForeignKey("design_candidates.design_id"), index=True)
    design_version: Mapped[int] = mapped_column(Integer)
    experiment_run_id: Mapped[str | None] = mapped_column(String, default=None)
    expected_observations: Mapped[list] = mapped_column(JSON, default=list)
    observed_results: Mapped[list] = mapped_column(JSON, default=list)
    residuals: Mapped[list] = mapped_column(JSON, default=list)  # [{metric, expected, observed, delta, direction_met}]
    failure_classification: Mapped[str] = mapped_column(String)  # one of DESIGN_FAILURE_CLASSIFICATIONS
    failure_case_id: Mapped[str | None] = mapped_column(String, default=None)  # harness.learning.models.FailureCase
    outcome_update: Mapped[str] = mapped_column(String, default="")
    next_iteration_reason: Mapped[str | None] = mapped_column(String, default=None)
    decided_next_action: Mapped[str | None] = mapped_column(String, default=None)  # next_iteration|diagnosis_reopened|stop|continue_build
    actor_id: Mapped[str] = mapped_column(String)
    created_at: Mapped[float] = mapped_column(Float)


guard_immutable_fields(DesignOutcomeRecord, mutable_fields=set())

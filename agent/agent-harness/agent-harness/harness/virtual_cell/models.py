"""Problem 06 (Predictive Simulation Loop & Virtual Cell Integration) tables.

Audit finding this package builds past (see `harness/cell_state/models.py`'s
own docstring and `harness/engineering_design/counterfactual_service.py`):
Problem 04 already calls `harness.diagnosis.model_adapters` (real cobrapy
FBA against the bundled `e_coli_core` GEM; honestly-`unavailable` vEcoli
and kinetic/resource-allocation adapters) for a single ad hoc
`CounterfactualRun` per candidate, using a hardcoded 3-gene hint table with
no compatibility check, no baseline/intervention comparability protocol, no
uncertainty decomposition, and no experiment-feedback loop. This package
does not fork a second model-execution stack - every table here still
resolves its numbers through `harness.diagnosis.model_adapters.registry`
(see `harness/virtual_cell/adapters.py`) - it adds the governance layer
doc06 requires around that same real engine: an explicit `ModelRegistryEntry`
(what a model actually claims to support), a real `CompatibilityReport`
gate before any run, an auditable `CompiledIntervention` (gene/reaction
mapping with recorded assumptions, not a silent hint lookup), a first-class
baseline-vs-counterfactual `CounterfactualComparison` with hard
comparability checks, an independent `PredictionReview`, and the
governed Level 1-5 `ModelUpdateProposal` / `ModelBenchmarkRecord` /
`PredictionCalibrationProfile` feedback loop back from real experimental
`harness.experiments.models.Observation` rows (reused, not duplicated -
doc06 3.10's OmicsObservation maps onto that existing table for the scalar
phenotype endpoints this round's adapters actually produce).

Every mutating service function in `harness/virtual_cell/*_service.py`
calls `harness.memory.event_store.append_event` into the SAME `ProjectEvent`
ledger Problems 01-05 use - no parallel history store.
"""
from __future__ import annotations

from sqlalchemy import JSON, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from harness.db import Base, guard_immutable_fields

# ---------------------------------------------------------------------------
# doc06 §10: simulation-case workflow states (mapped onto this repo's
# per-problem "own state machine + transition audit table" convention -
# same shape as `harness.scientific_evaluation.models.EVALUATION_STATES` /
# `harness.engineering_design.models.DESIGN_WORKFLOW_STATES` - never routed
# through the generic `harness.workflow.definitions.Stage` graph, which is
# Problem 01's own single-pass pipeline, not a per-problem sub-workflow).
# ---------------------------------------------------------------------------
SIMULATION_STATES = (
    "simulation_requested", "state_validated", "model_selected", "compatibility_checked",
    "intervention_compiled", "baseline_running", "intervention_running", "results_normalized",
    "comparison_ready", "prediction_under_review", "validation_planned", "awaiting_observation",
    "residual_computed", "update_proposed", "human_review", "completed",
    # failure / branch states (doc06 §10)
    "needs_input", "no_compatible_model", "out_of_domain", "unsupported_intervention",
    "run_failed", "timed_out", "infeasible", "invalid_comparison", "prediction_rejected", "stopped",
)

TERMINAL_SIMULATION_STATES = (
    "completed", "no_compatible_model", "out_of_domain", "unsupported_intervention",
    "run_failed", "timed_out", "infeasible", "invalid_comparison", "prediction_rejected", "stopped",
)

# doc06 §2.1: numeric-value source vocabulary. LLM text is never one of these.
SOURCE_TYPES = (
    "experimental_observation", "model_output", "derived_from_observation",
    "derived_from_model", "literature_reported", "assumption", "unknown",
)

# doc06 §3.1: per cell-state field provenance labels.
FIELD_STATUS = ("observed", "model_inferred", "literature_derived", "assumed", "unknown")

# doc06 §3.4 CompatibilityReport.decision
COMPATIBILITY_DECISIONS = ("compatible", "compatible_with_assumptions", "out_of_domain", "unsupported", "unavailable")

# doc06 §3.9 PredictionUncertainty.confidence_status - never a bare probability.
CONFIDENCE_STATUSES = ("calibrated", "empirical_interval", "replicate_variability_only", "qualitative", "unavailable")

# doc06 §8: PredictionReview finding severities.
REVIEW_SEVERITIES = ("info", "warning", "major", "blocking")
REVIEW_DECISIONS = ("decision_ready", "limited_acceptance", "rerun_required", "model_change_required", "rejected")

# doc06 §9.4: update levels.
UPDATE_LEVELS = ("project_belief", "input_state", "parameter_calibration", "model_structure", "model_retraining")
UPDATE_LEVELS_REQUIRING_HUMAN_GATE = {"parameter_calibration", "model_structure", "model_retraining"}

# doc06 §3.13
BENCHMARK_SPLIT_TYPES = ("reproduction", "validation", "held_out_test", "prospective")
BENCHMARK_STATUSES = ("provisional", "validated", "superseded")

# doc06 §3.14
CALIBRATION_RELIABILITY_STATUSES = ("insufficient_data", "qualitative_only", "provisionally_calibrated", "calibrated", "degraded")


class ModelRegistryEntry(Base):
    """doc06 §3.3. Describes what a model *claims* to support - never what
    it actually performed (that is `ModelBenchmarkRecord`'s job, §3.13).
    Seeded once per real adapter in `harness/virtual_cell/registry.py` from
    `harness.diagnosis.model_adapters` capability detection - not a second,
    disconnected model catalog."""

    __tablename__ = "vc_model_registry_entries"

    model_id: Mapped[str] = mapped_column(String, primary_key=True)
    model_name: Mapped[str] = mapped_column(String)
    model_type: Mapped[str] = mapped_column(String)  # gem_fba|kinetic_resource_allocation|whole_cell|protein_structure
    model_version: Mapped[str] = mapped_column(String)
    artifact_uri: Mapped[str | None] = mapped_column(String, default=None)
    artifact_hash: Mapped[str | None] = mapped_column(String, default=None)
    adapter_id: Mapped[str] = mapped_column(String)  # harness.diagnosis.model_adapters.registry key
    organism: Mapped[str] = mapped_column(String, default="unknown")
    strains: Mapped[list] = mapped_column(JSON, default=list)
    supported_conditions: Mapped[list] = mapped_column(JSON, default=list)
    supported_perturbations: Mapped[list] = mapped_column(JSON, default=list)
    input_modalities: Mapped[list] = mapped_column(JSON, default=list)
    output_modalities: Mapped[list] = mapped_column(JSON, default=list)
    mathematical_scope: Mapped[str] = mapped_column(String, default="")
    training_or_parameterization_domain: Mapped[str] = mapped_column(String, default="")
    validation_domain: Mapped[str] = mapped_column(String, default="")
    benchmark_references: Mapped[list] = mapped_column(JSON, default=list)
    known_failure_modes: Mapped[list] = mapped_column(JSON, default=list)
    runtime_requirements: Mapped[dict] = mapped_column(JSON, default=dict)
    availability_status: Mapped[str] = mapped_column(String, default="unavailable")  # available|unavailable
    unavailability_reason: Mapped[str] = mapped_column(String, default="")
    created_at: Mapped[float] = mapped_column(Float)


guard_immutable_fields(ModelRegistryEntry, mutable_fields={"availability_status", "unavailability_reason"})


class SimulationCase(Base):
    """The per-request workflow container (doc06 §10), one row per
    baseline+intervention prediction request against one `DesignVersion`."""

    __tablename__ = "vc_simulation_cases"

    simulation_case_id: Mapped[str] = mapped_column(String, primary_key=True)
    schema_version: Mapped[str] = mapped_column(String, default="1")
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.project_id"), index=True)
    design_version_id: Mapped[str] = mapped_column(String, index=True)  # harness.designs.models.DesignVersion (cross-package, plain ref)
    evaluation_reference: Mapped[str | None] = mapped_column(String, default=None)  # harness.scientific_evaluation.models.EvaluationCase, if gated through one
    requested_by: Mapped[str] = mapped_column(String)
    status: Mapped[str] = mapped_column(String, default="simulation_requested")  # one of SIMULATION_STATES
    stop_reason: Mapped[str | None] = mapped_column(String, default=None)
    baseline_cell_state_id: Mapped[str | None] = mapped_column(String, default=None)  # BiologicalStateSnapshot.snapshot_id
    model_id: Mapped[str | None] = mapped_column(String, default=None)
    router_rationale: Mapped[dict | None] = mapped_column(JSON, default=None)
    created_at: Mapped[float] = mapped_column(Float)
    updated_at: Mapped[float] = mapped_column(Float)
    version: Mapped[int] = mapped_column(Integer, default=1)


guard_immutable_fields(
    SimulationCase,
    mutable_fields={"status", "stop_reason", "baseline_cell_state_id", "model_id", "router_rationale", "updated_at", "version"},
)


class SimulationTransition(Base):
    """State-transition audit trail, mirrors `DesignWorkflowTransition` /
    `EvaluationTransition`."""

    __tablename__ = "vc_simulation_transitions"

    transition_id: Mapped[str] = mapped_column(String, primary_key=True)
    simulation_case_id: Mapped[str] = mapped_column(ForeignKey("vc_simulation_cases.simulation_case_id"), index=True)
    from_state: Mapped[str | None] = mapped_column(String, default=None)
    to_state: Mapped[str] = mapped_column(String)
    reason: Mapped[str] = mapped_column(String, default="")
    actor_id: Mapped[str] = mapped_column(String)
    created_at: Mapped[float] = mapped_column(Float)


class PerturbationSpec(Base):
    """doc06 §3.2. One row per engineering modification pulled from a
    `DesignVersion.genotype_manifest.modifications` entry (`{gene,
    operation, detail}` - see `harness.designs.adapters.
    genotype_manifest_from_p1_decisions`) - never invented from free text."""

    __tablename__ = "vc_perturbation_specs"

    perturbation_id: Mapped[str] = mapped_column(String, primary_key=True)
    simulation_case_id: Mapped[str] = mapped_column(ForeignKey("vc_simulation_cases.simulation_case_id"), index=True)
    design_version_id: Mapped[str] = mapped_column(String, index=True)
    type: Mapped[str] = mapped_column(String)  # deletion|knockdown|overexpression|promoter_edit|rbs_edit|point_mutation|gene_insertion|medium_change|oxygen_change|temperature_change|combination
    target: Mapped[str] = mapped_column(String)  # gene symbol/canonical id as authored, e.g. "ptsG"
    target_namespace: Mapped[str] = mapped_column(String, default="gene_symbol")
    biological_intent: Mapped[str] = mapped_column(String, default="")
    operation: Mapped[str] = mapped_column(String)  # raw genotype_manifest operation string
    strength: Mapped[dict | None] = mapped_column(JSON, default=None)  # e.g. {"factor": 0.5}
    implementation: Mapped[str] = mapped_column(String, default="")  # engineering implementation (CRISPRi, promoter swap, ...) if known
    timing: Mapped[dict | None] = mapped_column(JSON, default=None)
    combination_group: Mapped[str | None] = mapped_column(String, default=None)
    environmental_changes: Mapped[list] = mapped_column(JSON, default=list)
    required_mappings: Mapped[list] = mapped_column(JSON, default=list)
    assumptions: Mapped[list] = mapped_column(JSON, default=list)
    status: Mapped[str] = mapped_column(String, default="pending")  # pending|compiled|rejected
    created_at: Mapped[float] = mapped_column(Float)


guard_immutable_fields(PerturbationSpec, mutable_fields={"status"})


class CompatibilityReport(Base):
    """doc06 §3.4 / §2.4. Computed BEFORE any run is attempted - a
    `SimulationRun` may only be created for a `(model, cell_state,
    perturbation)` triple whose latest report has
    `decision in {compatible, compatible_with_assumptions}`."""

    __tablename__ = "vc_compatibility_reports"

    compatibility_id: Mapped[str] = mapped_column(String, primary_key=True)
    simulation_case_id: Mapped[str] = mapped_column(ForeignKey("vc_simulation_cases.simulation_case_id"), index=True)
    model_id: Mapped[str] = mapped_column(String, index=True)
    cell_state_id: Mapped[str] = mapped_column(String)
    perturbation_ids: Mapped[list] = mapped_column(JSON, default=list)
    organism_match: Mapped[str] = mapped_column(String, default="unknown")
    strain_match: Mapped[str] = mapped_column(String, default="unknown")
    condition_match: Mapped[str] = mapped_column(String, default="unknown")
    perturbation_support: Mapped[dict] = mapped_column(JSON, default=dict)  # {perturbation_id: supported|unsupported|approximate}
    input_completeness: Mapped[str] = mapped_column(String, default="unknown")
    output_coverage: Mapped[list] = mapped_column(JSON, default=list)  # endpoints the model can actually produce
    domain_status: Mapped[str] = mapped_column(String, default="unknown")
    blocking_reasons: Mapped[list] = mapped_column(JSON, default=list)
    non_blocking_assumptions: Mapped[list] = mapped_column(JSON, default=list)
    decision: Mapped[str] = mapped_column(String)  # one of COMPATIBILITY_DECISIONS
    created_at: Mapped[float] = mapped_column(Float)


guard_immutable_fields(CompatibilityReport, mutable_fields=set())


class CompiledIntervention(Base):
    """doc06 §3.5 / §5. The auditable gene/protein/reaction-level mapping -
    replaces `counterfactual_service._GENE_TO_REACTION_BOUND_HINT`'s silent
    3-gene hint table with a real cobrapy gene->GPR->reaction resolution
    (see `harness/virtual_cell/compiler.py`), always recording the
    assumption that a bound change approximates a genetic intervention."""

    __tablename__ = "vc_compiled_interventions"

    compiled_intervention_id: Mapped[str] = mapped_column(String, primary_key=True)
    perturbation_id: Mapped[str] = mapped_column(ForeignKey("vc_perturbation_specs.perturbation_id"), index=True)
    model_id: Mapped[str] = mapped_column(String, index=True)
    target_kind: Mapped[str] = mapped_column(String, default="reaction")  # gene|reaction
    resolved_gene_id: Mapped[str | None] = mapped_column(String, default=None)  # e.g. b-number
    affected_reactions: Mapped[list] = mapped_column(JSON, default=list)
    modification_type: Mapped[str] = mapped_column(String, default="reaction_bound_scaling")
    original_bounds: Mapped[dict] = mapped_column(JSON, default=dict)  # {reaction_id: {lower, upper}}
    new_bounds: Mapped[dict] = mapped_column(JSON, default=dict)
    mapping_rule: Mapped[str] = mapped_column(String, default="")
    mapping_status: Mapped[str] = mapped_column(String, default="approximate")  # direct|approximate|unsupported
    mapping_assumptions: Mapped[list] = mapped_column(JSON, default=list)
    mapping_uncertainty: Mapped[str] = mapped_column(String, default="")
    unsupported_inference: Mapped[list] = mapped_column(JSON, default=list)
    compilation_log: Mapped[list] = mapped_column(JSON, default=list)
    status: Mapped[str] = mapped_column(String, default="compiled")  # compiled|rejected
    rejection_reason: Mapped[str | None] = mapped_column(String, default=None)
    created_at: Mapped[float] = mapped_column(Float)


guard_immutable_fields(CompiledIntervention, mutable_fields=set())


class SimulationRun(Base):
    """doc06 §3.6. One row per actual adapter invocation - baseline (no
    `compiled_intervention_ids`) and each counterfactual scenario are
    SEPARATE rows, never one row mutated in place, so a baseline run can
    never be silently swapped out from under an already-computed
    comparison."""

    __tablename__ = "vc_simulation_runs"

    model_run_id: Mapped[str] = mapped_column(String, primary_key=True)
    simulation_case_id: Mapped[str] = mapped_column(ForeignKey("vc_simulation_cases.simulation_case_id"), index=True)
    scenario_label: Mapped[str] = mapped_column(String)  # S0_baseline|S1|S2|S3_combination|S4_control
    model_id: Mapped[str] = mapped_column(String, index=True)
    model_version: Mapped[str] = mapped_column(String, default="")
    artifact_hash: Mapped[str | None] = mapped_column(String, default=None)
    adapter_version: Mapped[str] = mapped_column(String, default="")
    baseline_state_id: Mapped[str] = mapped_column(String)
    perturbation_ids: Mapped[list] = mapped_column(JSON, default=list)
    compiled_intervention_ids: Mapped[list] = mapped_column(JSON, default=list)
    simulation_config: Mapped[dict] = mapped_column(JSON, default=dict)  # {start_time, end_time, time_step, solver, random_seed, replicate_index}
    inputs_hash: Mapped[str] = mapped_column(String, index=True)  # idempotency key: model_id + artifact_hash + inputs + config
    status: Mapped[str] = mapped_column(String, default="pending")  # pending|running|optimal|infeasible|unbounded|error|timed_out|not_computed
    started_at: Mapped[float] = mapped_column(Float)
    finished_at: Mapped[float | None] = mapped_column(Float, default=None)
    runtime_s: Mapped[float | None] = mapped_column(Float, default=None)
    log_summary: Mapped[str] = mapped_column(String, default="")
    raw_output_ref: Mapped[dict] = mapped_column(JSON, default=dict)
    normalized_result_id: Mapped[str | None] = mapped_column(String, default=None)
    failure_reason: Mapped[str | None] = mapped_column(String, default=None)
    created_at: Mapped[float] = mapped_column(Float)


guard_immutable_fields(SimulationRun, mutable_fields={"status", "finished_at", "runtime_s", "log_summary", "raw_output_ref", "normalized_result_id", "failure_reason"})


class SimulationResult(Base):
    """doc06 §3.7/§3.9. `endpoints` entries are always `{name, value, unit,
    statistic, source_type}` with `source_type="model_output"` (or
    `derived_from_model` for a code-computed ratio) - an LLM explanation is
    never written into this list. `endpoint_uncertainty` carries doc06
    §3.9's `PredictionUncertainty` shape per endpoint name (embedded, not a
    separate table, since it has no independent identity outside one
    result's endpoint - same JSON-embedding convention this codebase already
    uses for `DesignEvaluation.objective_vector` etc.)."""

    __tablename__ = "vc_simulation_results"

    simulation_result_id: Mapped[str] = mapped_column(String, primary_key=True)
    model_run_id: Mapped[str] = mapped_column(ForeignKey("vc_simulation_runs.model_run_id"), index=True)
    initial_state_id: Mapped[str] = mapped_column(String)
    terminal_state: Mapped[dict] = mapped_column(JSON, default=dict)
    trajectory_ref: Mapped[dict | None] = mapped_column(JSON, default=None)
    endpoints: Mapped[list] = mapped_column(JSON, default=list)
    endpoint_uncertainty: Mapped[dict] = mapped_column(JSON, default=dict)  # {endpoint_name: PredictionUncertainty-shaped dict}
    supported_scales: Mapped[list] = mapped_column(JSON, default=list)
    unsupported_scales: Mapped[list] = mapped_column(JSON, default=list)
    assumptions: Mapped[list] = mapped_column(JSON, default=list)
    warnings: Mapped[list] = mapped_column(JSON, default=list)
    created_at: Mapped[float] = mapped_column(Float)


guard_immutable_fields(SimulationResult, mutable_fields=set())


class CounterfactualComparison(Base):
    """doc06 §3.8/§6. Refuses (records `invalid_comparison` rather than a
    number) when model/artifact hash, environment, initial state, objective,
    time range, solver, or output units differ between the two runs being
    compared - see `harness/virtual_cell/comparison.py::compare_runs`."""

    __tablename__ = "vc_counterfactual_comparisons"

    comparison_id: Mapped[str] = mapped_column(String, primary_key=True)
    simulation_case_id: Mapped[str] = mapped_column(ForeignKey("vc_simulation_cases.simulation_case_id"), index=True)
    baseline_run_id: Mapped[str] = mapped_column(String)
    candidate_run_id: Mapped[str] = mapped_column(String)
    comparability_status: Mapped[str] = mapped_column(String)  # comparable|invalid_comparison
    comparability_violations: Mapped[list] = mapped_column(JSON, default=list)
    endpoints: Mapped[list] = mapped_column(JSON, default=list)  # [{name, unit, baseline_value, candidate_value, delta, relative_change, statistic, not_modeled}]
    missing_endpoints: Mapped[list] = mapped_column(JSON, default=list)
    tradeoffs: Mapped[list] = mapped_column(JSON, default=list)
    robustness: Mapped[dict | None] = mapped_column(JSON, default=None)
    created_at: Mapped[float] = mapped_column(Float)


guard_immutable_fields(CounterfactualComparison, mutable_fields=set())


class PredictionReview(Base):
    """doc06 §8. An independent boundary review of a `CounterfactualComparison`
    - distinct from Problem 05's design-level `ScientificReview`. `decision`
    stays out of `decision_ready` while any `blocking` finding in `findings`
    is unresolved (`vc/guards.py::prediction_is_decision_ready`)."""

    __tablename__ = "vc_prediction_reviews"

    review_id: Mapped[str] = mapped_column(String, primary_key=True)
    simulation_case_id: Mapped[str] = mapped_column(ForeignKey("vc_simulation_cases.simulation_case_id"), index=True)
    comparison_id: Mapped[str] = mapped_column(String, index=True)
    findings: Mapped[list] = mapped_column(JSON, default=list)  # [{category, severity, message, endpoint}]
    model_derived_endpoints: Mapped[list] = mapped_column(JSON, default=list)
    derived_endpoints: Mapped[list] = mapped_column(JSON, default=list)
    not_modeled_endpoints: Mapped[list] = mapped_column(JSON, default=list)
    mapping_status_summary: Mapped[dict] = mapped_column(JSON, default=dict)
    decision: Mapped[str] = mapped_column(String, default="rerun_required")  # one of REVIEW_DECISIONS
    reviewer_type: Mapped[str] = mapped_column(String, default="deterministic_rule")
    created_at: Mapped[float] = mapped_column(Float)


guard_immutable_fields(PredictionReview, mutable_fields=set())


class ValidationPlanItem(Base):
    """doc06 §9.1. One row per core prediction endpoint to be tested
    experimentally - falsification criteria are recorded up front, before
    any observation exists."""

    __tablename__ = "vc_validation_plan_items"

    validation_item_id: Mapped[str] = mapped_column(String, primary_key=True)
    simulation_case_id: Mapped[str] = mapped_column(ForeignKey("vc_simulation_cases.simulation_case_id"), index=True)
    comparison_id: Mapped[str] = mapped_column(String, index=True)
    endpoint: Mapped[str] = mapped_column(String)
    assay: Mapped[str] = mapped_column(String, default="")
    unit: Mapped[str] = mapped_column(String, default="")
    sampling_timepoints: Mapped[list] = mapped_column(JSON, default=list)
    controls: Mapped[list] = mapped_column(JSON, default=list)
    replicates: Mapped[int] = mapped_column(Integer, default=1)
    expected_direction: Mapped[str] = mapped_column(String, default="unknown")  # increase|decrease|no_change|unknown
    expected_interval: Mapped[dict | None] = mapped_column(JSON, default=None)
    falsification_condition: Mapped[str] = mapped_column(String, default="")
    alternative_explanations: Mapped[list] = mapped_column(JSON, default=list)
    status: Mapped[str] = mapped_column(String, default="planned")  # planned|awaiting_observation|resolved
    created_at: Mapped[float] = mapped_column(Float)


guard_immutable_fields(ValidationPlanItem, mutable_fields={"status"})


class PredictionResidual(Base):
    """doc06 §3.11/§9.3. Computed by code (`vc/residual_service.py`) - never
    an LLM number. `context_match=False` blocks residual computation
    entirely (row is not created); only QC-passed, context-matched
    observation/prediction pairs reach this table."""

    __tablename__ = "vc_prediction_residuals"

    residual_id: Mapped[str] = mapped_column(String, primary_key=True)
    simulation_case_id: Mapped[str] = mapped_column(ForeignKey("vc_simulation_cases.simulation_case_id"), index=True)
    validation_item_id: Mapped[str | None] = mapped_column(String, default=None)
    prediction_run_id: Mapped[str] = mapped_column(String)  # SimulationRun.model_run_id the prediction came from
    observation_id: Mapped[str] = mapped_column(String, index=True)  # harness.experiments.models.Observation.observation_id
    endpoint: Mapped[str] = mapped_column(String)
    predicted_value: Mapped[float] = mapped_column(Float)
    observed_value: Mapped[float] = mapped_column(Float)
    unit: Mapped[str] = mapped_column(String)
    residual: Mapped[float] = mapped_column(Float)
    relative_error: Mapped[float | None] = mapped_column(Float, default=None)
    measurement_uncertainty: Mapped[float | None] = mapped_column(Float, default=None)
    prediction_uncertainty: Mapped[dict | None] = mapped_column(JSON, default=None)
    context_match: Mapped[bool] = mapped_column(default=True)
    mismatch_status: Mapped[str] = mapped_column(String, default="matched")
    possible_causes: Mapped[list] = mapped_column(JSON, default=list)  # LLM-generated hypotheses ONLY, labeled as such
    recommended_update_level: Mapped[str | None] = mapped_column(String, default=None)  # one of UPDATE_LEVELS
    created_at: Mapped[float] = mapped_column(Float)


guard_immutable_fields(PredictionResidual, mutable_fields=set())


class ModelUpdateProposal(Base):
    """doc06 §3.12/§9.4. Level 1 (project belief) is auto-appliable; Levels
    3-5 (parameter calibration / model structure / retraining) require
    `human_approval_required=True` and a `ModelUpdateDecision` before
    `status` may become `approved` - enforced in
    `harness/virtual_cell/guards.py::assert_update_may_activate`, not only
    the frontend."""

    __tablename__ = "vc_model_update_proposals"

    proposal_id: Mapped[str] = mapped_column(String, primary_key=True)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.project_id"), index=True)
    triggering_residual_ids: Mapped[list] = mapped_column(JSON, default=list)
    update_level: Mapped[str] = mapped_column(String)  # one of UPDATE_LEVELS
    rationale: Mapped[str] = mapped_column(String, default="")
    required_data: Mapped[list] = mapped_column(JSON, default=list)
    identifiability_status: Mapped[str] = mapped_column(String, default="unknown")
    validation_plan: Mapped[str] = mapped_column(String, default="")
    rollback_plan: Mapped[str] = mapped_column(String, default="")
    human_approval_required: Mapped[bool] = mapped_column(default=True)
    status: Mapped[str] = mapped_column(String, default="proposed")  # proposed|approved|rejected|applied|superseded
    model_id: Mapped[str | None] = mapped_column(String, default=None)
    created_at: Mapped[float] = mapped_column(Float)


guard_immutable_fields(ModelUpdateProposal, mutable_fields={"status"})


class ModelUpdateDecision(Base):
    """The Human Gate record for a `ModelUpdateProposal` at Level 3-5 -
    mirrors `harness.scientific_evaluation.models.HumanEvaluationDecision`:
    fully immutable, a changed mind creates a new row."""

    __tablename__ = "vc_model_update_decisions"

    decision_id: Mapped[str] = mapped_column(String, primary_key=True)
    proposal_id: Mapped[str] = mapped_column(ForeignKey("vc_model_update_proposals.proposal_id"), index=True)
    decision: Mapped[str] = mapped_column(String)  # approved|rejected
    approver_id: Mapped[str] = mapped_column(String)
    approver_role: Mapped[str] = mapped_column(String, default="")
    rationale: Mapped[str] = mapped_column(String, default="")
    conditions: Mapped[list] = mapped_column(JSON, default=list)
    created_at: Mapped[float] = mapped_column(Float)


guard_immutable_fields(ModelUpdateDecision, mutable_fields=set())


class ModelBenchmarkRecord(Base):
    """doc06 §3.13/§9.5. Frozen per (model_version, artifact_hash,
    adapter_version, dataset_version, protocol) x (endpoint, strain,
    condition, perturbation_class) - never a single aggregate score, never
    silently overwritten (superseded only)."""

    __tablename__ = "vc_model_benchmark_records"

    benchmark_record_id: Mapped[str] = mapped_column(String, primary_key=True)
    model_id: Mapped[str] = mapped_column(String, index=True)
    model_version: Mapped[str] = mapped_column(String)
    artifact_hash: Mapped[str | None] = mapped_column(String, default=None)
    adapter_version: Mapped[str] = mapped_column(String, default="")
    benchmark_dataset_id: Mapped[str] = mapped_column(String)
    benchmark_dataset_version: Mapped[str] = mapped_column(String)
    evaluation_protocol_id: Mapped[str] = mapped_column(String)
    organism: Mapped[str] = mapped_column(String, default="unknown")
    strain: Mapped[str] = mapped_column(String, default="unknown")
    condition: Mapped[dict] = mapped_column(JSON, default=dict)
    perturbation_class: Mapped[str] = mapped_column(String, default="unknown")
    endpoint: Mapped[str] = mapped_column(String)
    unit: Mapped[str] = mapped_column(String, default="")
    split_type: Mapped[str] = mapped_column(String)  # one of BENCHMARK_SPLIT_TYPES
    sample_count: Mapped[int] = mapped_column(Integer, default=0)
    included_residual_ids: Mapped[list] = mapped_column(JSON, default=list)
    excluded_residual_ids: Mapped[list] = mapped_column(JSON, default=list)
    metrics: Mapped[dict] = mapped_column(JSON, default=dict)  # {mae, rmse, bias, rank_correlation, interval_coverage}
    applicability_scope: Mapped[dict] = mapped_column(JSON, default=dict)
    known_failure_modes: Mapped[list] = mapped_column(JSON, default=list)
    provenance: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[float] = mapped_column(Float)
    status: Mapped[str] = mapped_column(String, default="provisional")  # one of BENCHMARK_STATUSES
    supersedes_record_id: Mapped[str | None] = mapped_column(String, default=None)


guard_immutable_fields(ModelBenchmarkRecord, mutable_fields={"status"})


class PredictionCalibrationProfile(Base):
    """doc06 §3.14/§9.6. Computed from a context/QC-matched
    `PredictionResidual` cohort by code - never LLM-generated. Sample
    counts below `minimum_sample_requirement` force
    `reliability_status in {insufficient_data, qualitative_only}`, never
    `calibrated`."""

    __tablename__ = "vc_prediction_calibration_profiles"

    calibration_profile_id: Mapped[str] = mapped_column(String, primary_key=True)
    model_id: Mapped[str] = mapped_column(String, index=True)
    model_version: Mapped[str] = mapped_column(String)
    artifact_hash: Mapped[str | None] = mapped_column(String, default=None)
    endpoint: Mapped[str] = mapped_column(String)
    organism: Mapped[str] = mapped_column(String, default="unknown")
    strain_scope: Mapped[list] = mapped_column(JSON, default=list)
    condition_scope: Mapped[list] = mapped_column(JSON, default=list)
    perturbation_class_scope: Mapped[list] = mapped_column(JSON, default=list)
    calibration_method: Mapped[str] = mapped_column(String, default="empirical_residual_summary")
    calibration_dataset_version: Mapped[str] = mapped_column(String, default="")
    included_residual_ids: Mapped[list] = mapped_column(JSON, default=list)
    excluded_residual_ids: Mapped[list] = mapped_column(JSON, default=list)
    sample_count: Mapped[int] = mapped_column(Integer, default=0)
    minimum_sample_requirement: Mapped[int] = mapped_column(Integer, default=5)
    metrics: Mapped[dict] = mapped_column(JSON, default=dict)  # {bias, mae, rmse, empirical_interval_coverage, calibration_error}
    reliability_status: Mapped[str] = mapped_column(String)  # one of CALIBRATION_RELIABILITY_STATUSES
    validity_window: Mapped[dict | None] = mapped_column(JSON, default=None)
    domain_limits: Mapped[list] = mapped_column(JSON, default=list)
    created_at: Mapped[float] = mapped_column(Float)
    approved_by: Mapped[str | None] = mapped_column(String, default=None)
    supersedes_profile_id: Mapped[str | None] = mapped_column(String, default=None)
    status: Mapped[str] = mapped_column(String, default="active")  # active|superseded


guard_immutable_fields(PredictionCalibrationProfile, mutable_fields={"status", "reliability_status", "approved_by"})


# ---------------------------------------------------------------------------
# Cross-Modal Consistency (六大核心模块统一集成 prompt §6.4, Phase D). Reads
# `harness.experiments.models.Observation` (extended with modality/
# entity_id, migration 0008) for transcript/protein/metabolite/phenotype
# layers and `SimulationResult.endpoints` for the flux layer - no second
# omics-observation table.
# ---------------------------------------------------------------------------

AGREEMENT_STATUSES = (
    "consistent", "partially_consistent", "discordant", "temporally_unresolved", "insufficient_modalities", "not_comparable",
)
INCONSISTENCY_CLASSES = (
    "transcript_protein_discordance", "protein_flux_discordance", "flux_phenotype_discordance",
    "timepoint_mismatch", "condition_mismatch", "batch_effect", "missingness", "measurement_sensitivity",
    "entity_mapping_ambiguity", "compensatory_regulation", "resource_limitation",
    "post_transcriptional_regulation", "model_experiment_mismatch",
)


class CrossModalConsistencyReport(Base):
    """doc06 §7 (as renumbered in the unified-integration prompt, §6.4).
    `agreement_status`/`inconsistency_classes` are computed by
    `harness.virtual_cell.cross_modal_service` - a deterministic rule
    engine (no LLM), never collapsing a real discordance (e.g. "trpE RNA up,
    TrpE protein flat") into a single causal conclusion - `alternative_
    explanations`/`unsupported_conclusions` are always populated alongside
    any discordance class."""

    __tablename__ = "vc_cross_modal_consistency_reports"

    report_id: Mapped[str] = mapped_column(String, primary_key=True)
    project_id: Mapped[str] = mapped_column(String, index=True)
    design_version_ref: Mapped[str | None] = mapped_column(String, default=None)
    target_entity: Mapped[str] = mapped_column(String, index=True)
    aligned_observation_refs: Mapped[list] = mapped_column(JSON, default=list)
    transcript_change: Mapped[dict | None] = mapped_column(JSON, default=None)  # {direction, magnitude, timepoint, condition_ref, observation_id}
    protein_change: Mapped[dict | None] = mapped_column(JSON, default=None)
    metabolite_change: Mapped[dict | None] = mapped_column(JSON, default=None)
    flux_change: Mapped[dict | None] = mapped_column(JSON, default=None)  # sourced from SimulationResult.endpoints, source_type="model_output"
    phenotype_change: Mapped[dict | None] = mapped_column(JSON, default=None)
    agreement_status: Mapped[str] = mapped_column(String)  # one of AGREEMENT_STATUSES
    inconsistency_classes: Mapped[list] = mapped_column(JSON, default=list)  # subset of INCONSISTENCY_CLASSES
    data_quality_findings: Mapped[list] = mapped_column(JSON, default=list)
    time_alignment_findings: Mapped[list] = mapped_column(JSON, default=list)
    alternative_explanations: Mapped[list] = mapped_column(JSON, default=list)
    discriminating_measurements: Mapped[list] = mapped_column(JSON, default=list)
    unsupported_conclusions: Mapped[list] = mapped_column(JSON, default=list)
    created_at: Mapped[float] = mapped_column(Float)


guard_immutable_fields(CrossModalConsistencyReport, mutable_fields=set())

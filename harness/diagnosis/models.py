"""Problem 03 (Bottleneck Diagnosis Loop) tables. Extends Problem 02's
`Observation`/`HypothesisVersion` in place (see `harness/experiments/
models.py`, `harness/learning/models.py`, migration `0002_diagnosis_loop_
schema`) rather than duplicating them; the genuinely new capabilities this
package adds - competing-hypothesis evidence linking, structured
assessment, diagnostic test selection, model-run provenance, belief
update history, and the final gated `DiagnosisDecision` - have no
Problem-02 equivalent and live here.

All tables share Problem 02's event-sourcing discipline: every mutating
service call in `harness/diagnosis/service.py` appends a `ProjectEvent`
into the SAME ledger used by Problems 01/02 (doc 03 6.3: "不得平行创建
互不连接的第二套...历史存储").
"""
from __future__ import annotations

from sqlalchemy import JSON, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from harness.db import Base, guard_immutable_fields

# doc03 5: the 18-state Diagnosis workflow.
DIAGNOSIS_STATES = (
    "intake", "data_required", "observations_normalized", "hypotheses_generated",
    "evidence_assessed", "model_evidence_pending", "hypotheses_ranked", "test_selection_required",
    "test_planned", "awaiting_test_result", "belief_updated", "model_conflicted",
    "human_review_required", "actionable", "evidence_limited", "handoff_ready",
    "handed_off_to_design", "closed",
)

# doc03 2.4.
HYPOTHESIS_ASSESSMENT_STATUSES = (
    "untested", "weakly_supported", "strongly_supported", "weakened",
    "provisionally_ruled_out", "non_discriminating", "out_of_scope",
)

# doc03 2.3.
EVIDENCE_RELATIONS = ("supports", "contradicts", "is_consistent_with", "does_not_discriminate")

# doc03 2.8.
STOPPING_REASONS = ("actionable_stop", "evidence_limited_stop", "safety_stop", "human_escalation", "continue_diagnosis")

# doc03 3.14.
ALLOWED_NEXT_ACTIONS = ("collect_data", "run_diagnostic_test", "reopen_diagnosis", "handoff_to_design", "human_review", "stop")


class ProjectObjective(Base):
    """doc03 3.4: only feeds test selection / Engineering Value Gate,
    never `HypothesisAssessment` (doc03 2.7/2.9 - enforced structurally by
    `harness/diagnosis/assessor.py` never importing this model)."""

    __tablename__ = "diag_project_objectives"

    objective_id: Mapped[str] = mapped_column(String, primary_key=True)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.project_id"), index=True)
    titer_target: Mapped[dict | None] = mapped_column(JSON, default=None)
    yield_target: Mapped[dict | None] = mapped_column(JSON, default=None)
    productivity_target: Mapped[dict | None] = mapped_column(JSON, default=None)
    growth_viability: Mapped[dict | None] = mapped_column(JSON, default=None)
    stability: Mapped[dict | None] = mapped_column(JSON, default=None)
    scalability: Mapped[dict | None] = mapped_column(JSON, default=None)
    knowledge_gain: Mapped[dict | None] = mapped_column(JSON, default=None)
    risk_tolerance: Mapped[str] = mapped_column(String, default="moderate")  # low|moderate|high
    time_cost_constraint: Mapped[dict | None] = mapped_column(JSON, default=None)
    approval_owner: Mapped[str | None] = mapped_column(String, default=None)
    created_by: Mapped[str] = mapped_column(String)
    created_at: Mapped[float] = mapped_column(Float)


class BiologicalContext(Base):
    """doc03 3.3 (`TemporalState` + `BiologicalContext` merged - the doc
    describes them together with near-total field overlap)."""

    __tablename__ = "diag_biological_contexts"

    context_id: Mapped[str] = mapped_column(String, primary_key=True)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.project_id"), index=True)
    chassis_genotype_ref: Mapped[str | None] = mapped_column(String, default=None)  # design_version_id
    medium: Mapped[str | None] = mapped_column(String, default=None)
    carbon_source: Mapped[str | None] = mapped_column(String, default=None)
    environment: Mapped[dict] = mapped_column(JSON, default=dict)  # {oxygenation, temperature_c, pH}
    process_mode: Mapped[str | None] = mapped_column(String, default=None)  # batch|fed-batch|continuous
    growth_phase: Mapped[str | None] = mapped_column(String, default=None)
    process_phase: Mapped[str | None] = mapped_column(String, default=None)
    experiment_time: Mapped[dict | None] = mapped_column(JSON, default=None)  # {value, unit}
    sampling_window: Mapped[dict | None] = mapped_column(JSON, default=None)
    recent_perturbations: Mapped[list] = mapped_column(JSON, default=list)
    state_transition_context: Mapped[str | None] = mapped_column(String, default=None)
    steady_state_assumption: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[float] = mapped_column(Float)


class DiagnosisSession(Base):
    """doc03 3.1 `DiagnosisProjectState`. One row per diagnosis episode -
    a project may run several over its life (e.g. one per DBTL cycle that
    misses expectations)."""

    __tablename__ = "diag_sessions"

    diagnosis_session_id: Mapped[str] = mapped_column(String, primary_key=True)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.project_id"), index=True)
    workflow_run_id: Mapped[str | None] = mapped_column(String, default=None)  # Problem-01 WorkflowRun.run_id
    triggering_failure_case_id: Mapped[str | None] = mapped_column(String, default=None)  # Problem-02 FailureCase
    triggering_learning_cycle_id: Mapped[str | None] = mapped_column(String, default=None)
    objective_id: Mapped[str | None] = mapped_column(String, default=None)
    biological_system: Mapped[dict] = mapped_column(JSON, default=dict)  # {species, strain}
    baseline_observation_ids: Mapped[list] = mapped_column(JSON, default=list)
    # The `request`/`context` the orchestrator's DiagnosisAdapter.start() was
    # called with, kept until the hypothesis-generation pipeline actually
    # runs. Needed because a session can land in `data_required` before ever
    # reaching that pipeline - when resume() later supplies the missing data
    # and the session becomes sufficient, resume() must run the SAME pipeline
    # on THIS row using the original phenotype/observation_ids/etc, instead of
    # the orchestrator minting a brand-new session (see resume_diagnosis bug).
    pending_request_context: Mapped[dict] = mapped_column(JSON, default=dict)
    active_hypothesis_set_version: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String, default="intake")
    data_sufficiency: Mapped[str] = mapped_column(String, default="insufficient")  # sufficient|partial|insufficient
    approval_state: Mapped[str] = mapped_column(String, default="not_required")  # not_required|pending|approved|rejected
    version: Mapped[int] = mapped_column(Integer, default=1)
    created_at: Mapped[float] = mapped_column(Float)
    updated_at: Mapped[float] = mapped_column(Float)


class EngineeringProblem(Base):
    """A reproducible, descriptive comparison of persisted measurements.

    This deliberately contains *what differs*, never a causal explanation
    for why it differs.  Causal statements belong to HypothesisVersion.
    """

    __tablename__ = "diag_engineering_problems"

    engineering_problem_id: Mapped[str] = mapped_column(String, primary_key=True)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.project_id"), index=True)
    diagnosis_session_id: Mapped[str] = mapped_column(ForeignKey("diag_sessions.diagnosis_session_id"), index=True)
    observation_ids: Mapped[list] = mapped_column(JSON, default=list)
    comparison_observation_ids: Mapped[list] = mapped_column(JSON, default=list)
    metric: Mapped[str] = mapped_column(String)
    observed_value: Mapped[float] = mapped_column(Float)
    expected_value: Mapped[float] = mapped_column(Float)
    unit: Mapped[str] = mapped_column(String)
    delta: Mapped[float] = mapped_column(Float)
    comparison_method: Mapped[str] = mapped_column(String)
    condition: Mapped[dict] = mapped_column(JSON, default=dict)
    abnormality_statement: Mapped[str] = mapped_column(String)
    derivation_method: Mapped[str] = mapped_column(String, default="observation_comparison_v1")
    provenance: Mapped[dict] = mapped_column(JSON, default=dict)
    status: Mapped[str] = mapped_column(String, default="grounded")
    created_at: Mapped[float] = mapped_column(Float)


class DiagnosisFinding(Base):
    """Immutable observation-grounded bridge from diagnosis to design."""

    __tablename__ = "diag_findings"

    finding_id: Mapped[str] = mapped_column(String, primary_key=True)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.project_id"), index=True)
    engineering_problem_id: Mapped[str] = mapped_column(ForeignKey("diag_engineering_problems.engineering_problem_id"), index=True)
    observation_refs: Mapped[list] = mapped_column(JSON, default=list)
    constraint_hypothesis_id: Mapped[str] = mapped_column(ForeignKey("hypothesis_versions.hypothesis_version_id"), index=True)
    mechanism_type: Mapped[str] = mapped_column(String)
    causal_graph: Mapped[dict] = mapped_column(JSON, default=dict)
    supporting_evidence: Mapped[list] = mapped_column(JSON, default=list)
    contradicting_evidence: Mapped[list] = mapped_column(JSON, default=list)
    confidence_derivation: Mapped[dict] = mapped_column(JSON, default=dict)
    unresolved_alternatives: Mapped[list] = mapped_column(JSON, default=list)
    falsifiers: Mapped[list] = mapped_column(JSON, default=list)
    engineering_consequences: Mapped[list] = mapped_column(JSON, default=list)
    validation_needs: Mapped[list] = mapped_column(JSON, default=list)
    provenance: Mapped[dict] = mapped_column(JSON, default=dict)
    schema_version: Mapped[str] = mapped_column(String, default="diagnosis-finding/1.0")
    version: Mapped[int] = mapped_column(Integer, default=1)
    created_at: Mapped[float] = mapped_column(Float)


guard_immutable_fields(DiagnosisFinding, mutable_fields=set())


class DiagnosisTransition(Base):
    """State-transition audit trail, mirrors Problem 02's
    `IterativeCycleTransition`."""

    __tablename__ = "diag_transitions"

    transition_id: Mapped[str] = mapped_column(String, primary_key=True)
    diagnosis_session_id: Mapped[str] = mapped_column(ForeignKey("diag_sessions.diagnosis_session_id"), index=True)
    state: Mapped[str] = mapped_column(String)
    status: Mapped[str] = mapped_column(String)  # completed|failed
    output: Mapped[dict] = mapped_column(JSON, default=dict)
    gate_result: Mapped[dict | None] = mapped_column(JSON, default=None)
    selected_next_state: Mapped[str | None] = mapped_column(String, default=None)
    selection_reason: Mapped[str] = mapped_column(String, default="")
    error: Mapped[str | None] = mapped_column(String, default=None)
    started_at: Mapped[float] = mapped_column(Float)
    ended_at: Mapped[float | None] = mapped_column(Float, default=None)


class EvidenceItem(Base):
    """doc03 3.6. Genuinely new: Problem 02's `EngineeringDecision.
    evidence_ids` was always a bare list of unbacked string pointers -
    this is the first real evidence table in the codebase."""

    __tablename__ = "diag_evidence_items"

    evidence_item_id: Mapped[str] = mapped_column(String, primary_key=True)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.project_id"), index=True)
    source_type: Mapped[str] = mapped_column(String)  # literature|expert_rule|llm_reasoning|model_run|experiment_result|observation
    source_reference: Mapped[str | None] = mapped_column(String, default=None)
    content_summary: Mapped[str] = mapped_column(String)
    condition: Mapped[dict] = mapped_column(JSON, default=dict)
    time_ref: Mapped[dict | None] = mapped_column(JSON, default=None)
    quality: Mapped[str] = mapped_column(String, default="low")  # high|medium|low
    directness: Mapped[str] = mapped_column(String, default="indirect")  # direct|indirect
    corrects_evidence_item_id: Mapped[str | None] = mapped_column(String, default=None)
    superseded_by_evidence_item_id: Mapped[str | None] = mapped_column(String, default=None)
    model_run_id: Mapped[str | None] = mapped_column(String, default=None)
    experiment_run_id: Mapped[str | None] = mapped_column(String, default=None)
    observation_id: Mapped[str | None] = mapped_column(String, default=None)
    created_by: Mapped[str] = mapped_column(String)
    created_at: Mapped[float] = mapped_column(Float)

    # Additive literature-source fields (六大核心模块统一集成 prompt §5.7,
    # migration 0007_llm_generation_and_evidence_schema): populated when
    # `source_type="literature"` and the item came from a real retrieval
    # adapter (`harness.evidence_retrieval`); NULL/"not_reported" for
    # pre-existing expert_rule/llm_reasoning/model_run/experiment_result/
    # observation rows, never backfilled or guessed (prompt: "文献未提供的
    # 字段必须为 unknown 或 not_reported,不得补造").
    title: Mapped[str | None] = mapped_column(String, default=None)
    authors: Mapped[list | None] = mapped_column(JSON, default=None)
    publication_year: Mapped[int | None] = mapped_column(Integer, default=None)
    journal_or_repository: Mapped[str | None] = mapped_column(String, default=None)
    doi_or_accession: Mapped[str | None] = mapped_column(String, default=None)
    doi_verification_status: Mapped[str] = mapped_column(String, default="not_applicable")  # verified|unresolved|not_applicable
    organism: Mapped[str | None] = mapped_column(String, default=None)
    strain: Mapped[str | None] = mapped_column(String, default=None)
    genotype: Mapped[str | None] = mapped_column(String, default=None)
    intervention: Mapped[str | None] = mapped_column(String, default=None)
    comparator: Mapped[str | None] = mapped_column(String, default=None)
    measurement: Mapped[str | None] = mapped_column(String, default=None)
    direction: Mapped[str | None] = mapped_column(String, default=None)
    effect_size_if_reported: Mapped[dict | None] = mapped_column(JSON, default=None)
    uncertainty_if_reported: Mapped[dict | None] = mapped_column(JSON, default=None)
    extraction_method: Mapped[str] = mapped_column(String, default="manual_or_rule")  # manual_or_rule|llm_assisted|api_metadata_only
    extraction_status: Mapped[str] = mapped_column(String, default="not_applicable")  # complete|partial|not_applicable
    retrieval_provenance: Mapped[dict | None] = mapped_column(JSON, default=None)


class EvidenceLink(Base):
    """doc03 3.6/2.3: the relation is never a bare boolean - one of
    `EVIDENCE_RELATIONS`."""

    __tablename__ = "diag_evidence_links"

    evidence_link_id: Mapped[str] = mapped_column(String, primary_key=True)
    hypothesis_version_id: Mapped[str] = mapped_column(ForeignKey("hypothesis_versions.hypothesis_version_id"), index=True)
    evidence_item_id: Mapped[str] = mapped_column(ForeignKey("diag_evidence_items.evidence_item_id"), index=True)
    relation: Mapped[str] = mapped_column(String)  # one of EVIDENCE_RELATIONS
    claim: Mapped[str] = mapped_column(String, default="")
    condition_match: Mapped[str] = mapped_column(String, default="unknown")  # matched|partial|mismatched|unknown
    strength_basis: Mapped[str] = mapped_column(String, default="")
    limitations: Mapped[str] = mapped_column(String, default="")
    created_by: Mapped[str] = mapped_column(String)
    created_at: Mapped[float] = mapped_column(Float)


class HypothesisAssessment(Base):
    """doc03 3.7. Insert-only: a re-assessment creates a new row with
    `parent_assessment_id` pointing back (doc 2.10 - history never
    overwritten), mirroring `HypothesisVersion`'s own versioning."""

    __tablename__ = "diag_hypothesis_assessments"

    assessment_id: Mapped[str] = mapped_column(String, primary_key=True)
    hypothesis_version_id: Mapped[str] = mapped_column(ForeignKey("hypothesis_versions.hypothesis_version_id"), index=True)
    diagnosis_session_id: Mapped[str] = mapped_column(ForeignKey("diag_sessions.diagnosis_session_id"), index=True)
    parent_assessment_id: Mapped[str | None] = mapped_column(String, default=None)
    explanatory_coverage: Mapped[dict] = mapped_column(JSON, default=dict)
    contradictions: Mapped[list] = mapped_column(JSON, default=list)
    evidence_quality: Mapped[str] = mapped_column(String, default="low")
    evidence_directness: Mapped[str] = mapped_column(String, default="indirect")
    condition_match: Mapped[str] = mapped_column(String, default="unknown")
    robustness: Mapped[str] = mapped_column(String, default="low")
    testability: Mapped[str] = mapped_column(String, default="low")
    remaining_uncertainty: Mapped[str] = mapped_column(String, default="")
    status: Mapped[str] = mapped_column(String, default="untested")  # one of HYPOTHESIS_ASSESSMENT_STATUSES
    ranking_rank: Mapped[int | None] = mapped_column(Integer, default=None)
    pareto_state: Mapped[str | None] = mapped_column(String, default=None)
    assessment_version: Mapped[int] = mapped_column(Integer, default=1)
    rationale_references: Mapped[list] = mapped_column(JSON, default=list)
    created_by: Mapped[str] = mapped_column(String)
    created_at: Mapped[float] = mapped_column(Float)


guard_immutable_fields(EvidenceItem, mutable_fields={"superseded_by_evidence_item_id"})
guard_immutable_fields(EvidenceLink, mutable_fields=set())
guard_immutable_fields(HypothesisAssessment, mutable_fields=set())


class DiagnosticTest(Base):
    """doc03 3.8."""

    __tablename__ = "diag_diagnostic_tests"

    test_id: Mapped[str] = mapped_column(String, primary_key=True)
    diagnosis_session_id: Mapped[str] = mapped_column(ForeignKey("diag_sessions.diagnosis_session_id"), index=True)
    compared_hypothesis_ids: Mapped[list] = mapped_column(JSON, default=list)
    predicted_outcomes_per_hypothesis: Mapped[dict] = mapped_column(JSON, default=dict)
    assay: Mapped[str] = mapped_column(String, default="")
    positive_control: Mapped[str] = mapped_column(String, default="")
    negative_control: Mapped[str] = mapped_column(String, default="")
    decision_rule: Mapped[str] = mapped_column(String, default="")
    expected_information_gain: Mapped[str] = mapped_column(String, default="unknown")  # high|medium|low|unknown
    cost: Mapped[str] = mapped_column(String, default="unknown")
    turnaround: Mapped[str] = mapped_column(String, default="unknown")
    availability: Mapped[str] = mapped_column(String, default="unknown")
    technical_feasibility: Mapped[str] = mapped_column(String, default="unknown")
    risk: Mapped[str] = mapped_column(String, default="unknown")
    prerequisites: Mapped[list] = mapped_column(JSON, default=list)
    discriminates_hypotheses: Mapped[bool] = mapped_column(default=False)
    status: Mapped[str] = mapped_column(String, default="proposed")  # proposed|selected|executed
    created_by: Mapped[str] = mapped_column(String)
    created_at: Mapped[float] = mapped_column(Float)


class ModelRunRecord(Base):
    """doc03 3.9. The real record for Phase 3's model-adapter registry -
    distinct from Problem 02's bare `cell_state.models.Prediction` stub
    (which stays unpopulated; this table is what Phase 3 actually writes
    to, since it needs solver/runtime-status/domain-flag fields Problem
    02 never modeled)."""

    __tablename__ = "diag_model_runs"

    model_run_id: Mapped[str] = mapped_column(String, primary_key=True)
    diagnosis_session_id: Mapped[str | None] = mapped_column(String, default=None, index=True)
    adapter_name: Mapped[str] = mapped_column(String)
    model_name: Mapped[str] = mapped_column(String)
    model_version: Mapped[str] = mapped_column(String, default="")
    capability_status: Mapped[str] = mapped_column(String)  # available|unavailable|out_of_domain
    inputs: Mapped[dict] = mapped_column(JSON, default=dict)
    context: Mapped[dict] = mapped_column(JSON, default=dict)
    constraints_objective_parameters: Mapped[dict] = mapped_column(JSON, default=dict)
    solver: Mapped[str | None] = mapped_column(String, default=None)
    runtime_status: Mapped[str] = mapped_column(String, default="not_computed")  # optimal|infeasible|unbounded|timeout|not_computed|error
    outputs: Mapped[dict] = mapped_column(JSON, default=dict)
    uncertainty: Mapped[dict | None] = mapped_column(JSON, default=None)
    domain_flags: Mapped[list] = mapped_column(JSON, default=list)
    sensitivity_variant_of: Mapped[str | None] = mapped_column(String, default=None)
    reproducibility_ref: Mapped[dict] = mapped_column(JSON, default=dict)
    log_summary: Mapped[str] = mapped_column(String, default="")
    started_at: Mapped[float] = mapped_column(Float)
    completed_at: Mapped[float | None] = mapped_column(Float, default=None)


class ModelEvidenceAssessment(Base):
    """doc03 3.9's second half: cross-model convergence/conflict."""

    __tablename__ = "diag_model_evidence_assessments"

    assessment_id: Mapped[str] = mapped_column(String, primary_key=True)
    diagnosis_session_id: Mapped[str] = mapped_column(ForeignKey("diag_sessions.diagnosis_session_id"), index=True)
    model_run_ids: Mapped[list] = mapped_column(JSON, default=list)
    convergence_status: Mapped[str] = mapped_column(String)  # convergent|partially_convergent|conflicting|insufficient
    ranking_stability: Mapped[dict] = mapped_column(JSON, default=dict)
    conflict_explanation: Mapped[str] = mapped_column(String, default="")
    calibration_note: Mapped[str] = mapped_column(String, default="")
    limitations: Mapped[str] = mapped_column(String, default="")
    created_at: Mapped[float] = mapped_column(Float)


class CounterfactualPrediction(Base):
    """doc03 3.10. `status="qualitative_expectation"` is explicitly NOT a
    model result - `harness/diagnosis/model_adapters/` never returns this
    status; only LLM-authored qualitative narrative uses it, and the
    report renderer must label it as such."""

    __tablename__ = "diag_counterfactual_predictions"

    prediction_id: Mapped[str] = mapped_column(String, primary_key=True)
    hypothesis_version_id: Mapped[str] = mapped_column(ForeignKey("hypothesis_versions.hypothesis_version_id"), index=True)
    intervention_or_query: Mapped[dict] = mapped_column(JSON, default=dict)
    baseline_state_ref: Mapped[str | None] = mapped_column(String, default=None)
    predicted_state: Mapped[dict | None] = mapped_column(JSON, default=None)
    model_run_ids: Mapped[list] = mapped_column(JSON, default=list)
    assumptions: Mapped[list] = mapped_column(JSON, default=list)
    uncertainty: Mapped[dict | None] = mapped_column(JSON, default=None)
    cross_model_agreement: Mapped[str | None] = mapped_column(String, default=None)
    out_of_domain: Mapped[bool] = mapped_column(default=False)
    status: Mapped[str] = mapped_column(String, default="not_computed")  # not_computed|computed|qualitative_expectation
    qualitative_expectation_text: Mapped[str | None] = mapped_column(String, default=None)
    created_at: Mapped[float] = mapped_column(Float)


class ExperimentalExecutionPlan(Base):
    """doc03 3.11."""

    __tablename__ = "diag_execution_plans"

    plan_id: Mapped[str] = mapped_column(String, primary_key=True)
    diagnostic_test_id: Mapped[str] = mapped_column(ForeignKey("diag_diagnostic_tests.test_id"), index=True)
    protocol_reference_or_draft: Mapped[str] = mapped_column(String, default="")
    materials: Mapped[list] = mapped_column(JSON, default=list)
    controls: Mapped[dict] = mapped_column(JSON, default=dict)
    biological_replicates: Mapped[int | None] = mapped_column(Integer, default=None)
    technical_replicates: Mapped[int | None] = mapped_column(Integer, default=None)
    sampling_schedule: Mapped[list] = mapped_column(JSON, default=list)
    qc_acceptance_criteria: Mapped[list] = mapped_column(JSON, default=list)
    expected_output_schema: Mapped[dict] = mapped_column(JSON, default=dict)
    interpretation_rule: Mapped[str] = mapped_column(String, default="")
    owner: Mapped[str | None] = mapped_column(String, default=None)
    approval_state: Mapped[str] = mapped_column(String, default="not_required")
    readiness: Mapped[str] = mapped_column(String, default="conceptual")  # conceptual|draft|ready
    created_at: Mapped[float] = mapped_column(Float)


class BeliefUpdateEvent(Base):
    """doc03 3.12."""

    __tablename__ = "diag_belief_updates"

    update_id: Mapped[str] = mapped_column(String, primary_key=True)
    diagnosis_session_id: Mapped[str] = mapped_column(ForeignKey("diag_sessions.diagnosis_session_id"), index=True)
    prior_assessment_id: Mapped[str | None] = mapped_column(String, default=None)
    new_evidence_or_test_result_ref: Mapped[dict] = mapped_column(JSON, default=dict)
    update_rule: Mapped[str] = mapped_column(String, default="")
    posterior_assessment_id: Mapped[str] = mapped_column(String)
    status_change: Mapped[dict] = mapped_column(JSON, default=dict)  # {from, to}
    unresolved_conflicts: Mapped[list] = mapped_column(JSON, default=list)
    actor_id: Mapped[str] = mapped_column(String)
    rationale: Mapped[str] = mapped_column(String, default="")
    created_at: Mapped[float] = mapped_column(Float)


class BottleneckValueAssessment(Base):
    """doc03 3.13: engineering value, deliberately never imported by
    `harness/diagnosis/assessor.py` (doc 2.9's separation)."""

    __tablename__ = "diag_bottleneck_value_assessments"

    value_assessment_id: Mapped[str] = mapped_column(String, primary_key=True)
    hypothesis_version_id: Mapped[str] = mapped_column(ForeignKey("hypothesis_versions.hypothesis_version_id"), index=True)
    objective_id: Mapped[str | None] = mapped_column(String, default=None)
    biological_importance: Mapped[str] = mapped_column(String, default="unknown")
    engineering_leverage: Mapped[str] = mapped_column(String, default="unknown")
    expected_gain_range: Mapped[dict | None] = mapped_column(JSON, default=None)
    intervention_complexity: Mapped[str] = mapped_column(String, default="unknown")
    growth_stability_tradeoff: Mapped[str] = mapped_column(String, default="unknown")
    reversibility: Mapped[str] = mapped_column(String, default="unknown")
    robustness: Mapped[str] = mapped_column(String, default="unknown")
    priority: Mapped[str] = mapped_column(String, default="unranked")
    prerequisites: Mapped[list] = mapped_column(JSON, default=list)
    rationale: Mapped[str] = mapped_column(String, default="")
    created_at: Mapped[float] = mapped_column(Float)


class DiagnosisDecision(Base):
    """doc03 3.14: the gated handoff object. Insert-only; a reopened
    diagnosis produces a new decision with `diagnosis_version` incremented,
    never an edit to a past decision (doc 2.10)."""

    __tablename__ = "diag_decisions"

    decision_id: Mapped[str] = mapped_column(String, primary_key=True)
    diagnosis_session_id: Mapped[str] = mapped_column(ForeignKey("diag_sessions.diagnosis_session_id"), index=True)
    diagnosis_version: Mapped[int] = mapped_column(Integer)
    context_reference: Mapped[dict] = mapped_column(JSON, default=dict)
    leading_hypothesis_ids: Mapped[list] = mapped_column(JSON, default=list)
    supported_hypothesis_ids: Mapped[list] = mapped_column(JSON, default=list)
    alternatives_not_excluded_ids: Mapped[list] = mapped_column(JSON, default=list)
    contradictions: Mapped[list] = mapped_column(JSON, default=list)
    confidence_representation: Mapped[dict] = mapped_column(JSON, default=dict)
    uncertainty: Mapped[str] = mapped_column(String, default="")
    evidence_references: Mapped[list] = mapped_column(JSON, default=list)
    model_assessment_reference: Mapped[str | None] = mapped_column(String, default=None)
    selected_diagnostic_test_id: Mapped[str | None] = mapped_column(String, default=None)
    stopping_reason: Mapped[str] = mapped_column(String)  # one of STOPPING_REASONS
    engineering_value_assessment: Mapped[dict | None] = mapped_column(JSON, default=None)
    allowed_next_action: Mapped[str] = mapped_column(String)  # one of ALLOWED_NEXT_ACTIONS
    handoff_status: Mapped[str] = mapped_column(String, default="not_applicable")  # not_applicable|pending|approved|handed_off|rejected
    human_approval: Mapped[dict | None] = mapped_column(JSON, default=None)
    created_by: Mapped[str] = mapped_column(String)
    created_at: Mapped[float] = mapped_column(Float)


guard_immutable_fields(DiagnosticTest, mutable_fields={"status"})
guard_immutable_fields(DiagnosisDecision, mutable_fields={"handoff_status", "human_approval"})
guard_immutable_fields(EngineeringProblem, mutable_fields={"status"})

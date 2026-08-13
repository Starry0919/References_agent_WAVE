"""Problem 05 (Evaluator & Scientific Critic) tables (doc05 §3).

Design choice (audit finding - see `harness/engineering_design/models.py`'s
own docstring and `harness/engineering_design/evaluators/`): Problem 04
already ships a *placeholder* evaluator (doc04 §4.4's 8 rule-based
evaluators feeding one `DesignEvaluation` row per candidate, run
synchronously inside `evaluation_service.evaluate_portfolio`). That is
exactly the "Evaluator 占位接口" doc05 §1.1 instructs this package to audit
and build past - it has no evidence condition-match matrix, no honest
per-model domain assessment beyond a single `not_computed` sentinel, no
adversarial/independent critique, no multi-reviewer meta-review, and no
Human Gate of its own (only Problem 04's later build-approval gate). This
package does not delete or fork that evaluator - `DesignPortfolio` /
`CandidateDesign` / `DesignEvaluation` / `BuildTestPackage` /
`CounterfactualRun` remain Problem 04's real, tested output and are read
here as doc05 §8 requires ("正式输入应为 Problem 4 输出的...") - but it adds
the genuinely new governance objects doc05 §3 specifies: a frozen
`EvaluationCase`, a real per-claim `EvidenceAssessment` matrix, an honest
`ModelEvaluationRecord` wrapper around `CounterfactualRun`/the diagnosis
model-adapter registry, structured `CriticFinding`/`ScientificReview` from
multiple independently-triggered reviewers, `MetaReviewDecision`,
versioned `RevisionTask`/`RevisionCycle`, a dedicated `HumanEvaluationDecision`
gate (distinct from - and required *before* - Problem 04's own build
approval), and an append-only `EvaluationMemoryEvent`.

Every mutating service function in this package also calls
`harness.memory.event_store.append_event` into the SAME `ProjectEvent`
ledger Problems 01-04 use (doc05 §9: "禁止...把 Memory 当聊天摘要" /
"不得平行创建...第二套历史存储" precedent already established by every
prior problem in this codebase).
"""
from __future__ import annotations

from sqlalchemy import JSON, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from harness.db import Base, guard_immutable_fields

# ---------------------------------------------------------------------------
# doc05 §6: evaluation workflow states.
# ---------------------------------------------------------------------------
EVALUATION_STATES = (
    "evaluation_pending", "deterministic_validation", "evidence_review", "model_review",
    "scientific_review", "candidate_comparison", "meta_review", "revision_required",
    "awaiting_human_decision", "approved_for_planning", "approved_for_build",
    "returned_to_diagnosis", "rejected", "held", "stopped",
)

# doc05 §2.2.
SOURCE_TYPES = (
    "experimental_observation", "literature_evidence", "database_record", "computational_model",
    "deterministic_rule", "expert_judgment", "llm_hypothesis",
)

# doc05 §2.3 / §3.3: ordered match-quality vocabulary, worst-to-best via index.
MATCH_LEVELS = ("unknown", "not_applicable", "poor", "partial", "close", "exact")

# doc05 §3.6.
SEVERITY_LEVELS = ("informational", "minor", "moderate", "major", "critical")

# doc05 §5.1/§5.3.
CONFIDENCE_CLASSES = ("not_calibrated", "indeterminate", "low", "medium", "high")

EVIDENCE_STRENGTH_LEVELS = ("unknown", "insufficient", "weak", "moderate", "strong")

# doc05 §3.4.
MODEL_RUN_STATUSES = ("computed", "not_computed", "unavailable", "failed", "out_of_domain", "stale")

# doc05 §2.7.
HUMAN_DECISIONS = (
    "approve_for_planning", "approve_for_build", "revise", "request_more_evidence",
    "request_model_run", "return_to_diagnosis", "reject", "hold", "stop",
)
# Same vocabulary is what an Agent may *recommend* (doc05 §2.7 - Agent never
# writes `approved_for_build` itself).
RECOMMENDED_ACTIONS = HUMAN_DECISIONS

# doc05 §4.9.
REVISION_TASK_TYPES = (
    "fix_design", "add_or_replace_evidence", "run_model", "add_control", "change_validation_plan",
    "split_candidate", "reduce_complexity", "return_to_diagnosis", "human_adjudication",
)

# doc05 §4.5/§4.6.
REVIEWER_TYPES = (
    "generalist", "metabolic_systems_critic", "genetic_buildability_critic", "protein_design_critic",
    "experimental_design_critic", "process_scale_critic", "safety_ethics_critic",
    "llm_critic",  # 六大核心模块统一集成 prompt §5.5 - additive, real LLM-backed reviewer (harness/scientific_evaluation/llm_critic_adapter.py)
)

# doc05 §4.5's 10-point rubric, condensed into a finding taxonomy.
CRITIC_CATEGORIES = (
    "weak_causal_link", "ineffective_intervention", "competing_explanation", "evidence_not_transferable",
    "compensation_or_feedback_ignored", "essentiality_or_fitness_risk", "buildability_or_stability",
    "missing_control", "falsifiability", "safety_or_compliance",
)


class EvaluationCase(Base):
    """doc05 §3.1. `frozen_context` is a point-in-time snapshot taken at
    intake - a condition change never silently mutates it (doc05 §3.1's own
    instruction); `harness/scientific_evaluation/intake.py::open_evaluation_
    case` is the only writer of this row's frozen fields."""

    __tablename__ = "eval_cases"

    evaluation_id: Mapped[str] = mapped_column(String, primary_key=True)
    schema_version: Mapped[str] = mapped_column(String, default="1")
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.project_id"), index=True)
    design_project_id: Mapped[str] = mapped_column(String, index=True)
    workflow_run_id: Mapped[str | None] = mapped_column(String, default=None)
    diagnosis_reference: Mapped[str | None] = mapped_column(String, default=None)  # DiagnosisHandoffRecord.handoff_id
    portfolio_reference: Mapped[str] = mapped_column(String, index=True)
    design_version_references: Mapped[list] = mapped_column(JSON, default=list)  # [{design_id, design_version}]
    frozen_context: Mapped[dict] = mapped_column(JSON, default=dict)
    evaluation_mode: Mapped[str] = mapped_column(String, default="portfolio")  # portfolio|single_candidate
    status: Mapped[str] = mapped_column(String, default="evaluation_pending")  # one of EVALUATION_STATES
    revision_round: Mapped[int] = mapped_column(Integer, default=0)
    created_by: Mapped[str] = mapped_column(String)
    created_at: Mapped[float] = mapped_column(Float)
    updated_at: Mapped[float] = mapped_column(Float)
    version: Mapped[int] = mapped_column(Integer, default=1)


guard_immutable_fields(
    EvaluationCase,
    mutable_fields={"status", "revision_round", "updated_at", "version", "design_version_references"},
)


class EvaluationTransition(Base):
    """State-transition audit trail, mirrors `harness.engineering_design.
    models.DesignWorkflowTransition` / `harness.diagnosis.models.
    DiagnosisTransition`."""

    __tablename__ = "eval_transitions"

    transition_id: Mapped[str] = mapped_column(String, primary_key=True)
    evaluation_id: Mapped[str] = mapped_column(ForeignKey("eval_cases.evaluation_id"), index=True)
    state: Mapped[str] = mapped_column(String)
    status: Mapped[str] = mapped_column(String)  # completed|failed
    gate_result: Mapped[dict | None] = mapped_column(JSON, default=None)
    selected_next_state: Mapped[str | None] = mapped_column(String, default=None)
    selection_reason: Mapped[str] = mapped_column(String, default="")
    actor_id: Mapped[str] = mapped_column(String)
    started_at: Mapped[float] = mapped_column(Float)
    ended_at: Mapped[float | None] = mapped_column(Float, default=None)


class ScientificClaim(Base):
    """doc05 §3.2. Extracted from a frozen `CandidateDesign`'s own
    declared fields (mechanism, causal chain, modifications, safety flags,
    build/test targets) at intake time - never invented by a reviewer."""

    __tablename__ = "eval_claims"

    claim_id: Mapped[str] = mapped_column(String, primary_key=True)
    evaluation_id: Mapped[str] = mapped_column(ForeignKey("eval_cases.evaluation_id"), index=True)
    design_id: Mapped[str] = mapped_column(String, index=True)
    design_version: Mapped[int] = mapped_column(Integer)
    claim_text: Mapped[str] = mapped_column(String)
    claim_type: Mapped[str] = mapped_column(String)  # mechanism|expected_phenotype|risk|buildability|model_prediction|experimental_discriminator
    causal_chain_position: Mapped[int | None] = mapped_column(Integer, default=None)
    source_type: Mapped[str] = mapped_column(String)  # one of SOURCE_TYPES
    source_references: Mapped[list] = mapped_column(JSON, default=list)
    scope_conditions: Mapped[dict] = mapped_column(JSON, default=dict)
    supports_or_opposes: Mapped[str] = mapped_column(String, default="supports")  # supports|opposes|neutral
    uncertainty: Mapped[str] = mapped_column(String, default="unknown")
    status: Mapped[str] = mapped_column(String, default="open")  # open|supported|unsupported|contradicted
    created_at: Mapped[float] = mapped_column(Float)


guard_immutable_fields(ScientificClaim, mutable_fields={"status"})


class EvidenceAssessment(Base):
    """doc05 §3.3/§2.3. Append-only: a re-assessment (new evidence, new
    round) always creates a NEW row rather than editing a past verdict -
    `assessor_type` records whether a deterministic rule, a critic, or a
    human produced it. If `harness.diagnosis.models.EvidenceItem` supplied
    the source, `evidence_id` is that table's real `evidence_item_id`
    (doc05 §4.3: "若仓库已有 Evidence Chain,必须复用其 ID 与 lineage") -
    never a re-summarized copy."""

    __tablename__ = "eval_evidence_assessments"

    assessment_id: Mapped[str] = mapped_column(String, primary_key=True)
    evaluation_id: Mapped[str] = mapped_column(ForeignKey("eval_cases.evaluation_id"), index=True)
    claim_id: Mapped[str] = mapped_column(ForeignKey("eval_claims.claim_id"), index=True)
    evidence_id: Mapped[str | None] = mapped_column(String, default=None)
    evidence_type: Mapped[str] = mapped_column(String)  # one of SOURCE_TYPES
    source_quality: Mapped[str] = mapped_column(String, default="unknown")  # high|medium|low|unknown
    independence: Mapped[str] = mapped_column(String, default="unknown")  # independent|same_study|same_lab|unknown
    host_match: Mapped[str] = mapped_column(String, default="unknown")  # one of MATCH_LEVELS
    genotype_match: Mapped[str] = mapped_column(String, default="unknown")
    condition_match: Mapped[str] = mapped_column(String, default="unknown")  # medium/carbon/O2/temperature
    process_match: Mapped[str] = mapped_column(String, default="unknown")  # mode + scale
    time_match: Mapped[str] = mapped_column(String, default="unknown")  # growth phase / timepoint
    intervention_match: Mapped[str] = mapped_column(String, default="unknown")
    measurement_match: Mapped[str] = mapped_column(String, default="unknown")
    mechanism_match: Mapped[str] = mapped_column(String, default="unknown")
    directness: Mapped[str] = mapped_column(String, default="indirect")  # direct|indirect
    opposing_evidence: Mapped[list] = mapped_column(JSON, default=list)
    applicability_limits: Mapped[list] = mapped_column(JSON, default=list)
    over_extrapolation_flags: Mapped[list] = mapped_column(JSON, default=list)
    overall_strength: Mapped[str] = mapped_column(String, default="unknown")  # one of EVIDENCE_STRENGTH_LEVELS
    reasoning_summary: Mapped[str] = mapped_column(String, default="")
    assessor_type: Mapped[str] = mapped_column(String, default="deterministic_rule")  # deterministic_rule|critic|human
    provenance: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[float] = mapped_column(Float)


guard_immutable_fields(EvidenceAssessment, mutable_fields=set())


class ModelEvaluationRecord(Base):
    """doc05 §3.4/§2.4. Normalizes whatever real run exists - today that is
    `harness.engineering_design.models.CounterfactualRun`, itself backed by
    `harness.diagnosis.model_adapters` (real cobrapy FBA / honestly-
    unavailable vEcoli+kinetic) - into the doc05 vocabulary. Never computes
    a number itself; `run_status='not_computed'` with zero rows requested is
    an honest, explicit outcome, not an error."""

    __tablename__ = "eval_model_records"

    record_id: Mapped[str] = mapped_column(String, primary_key=True)
    evaluation_id: Mapped[str] = mapped_column(ForeignKey("eval_cases.evaluation_id"), index=True)
    design_reference: Mapped[str] = mapped_column(String, index=True)
    adapter_name: Mapped[str] = mapped_column(String)
    model_or_tool_name: Mapped[str] = mapped_column(String, default="")
    version: Mapped[str] = mapped_column(String, default="")
    prediction_target: Mapped[str] = mapped_column(String, default="")
    input_references: Mapped[list] = mapped_column(JSON, default=list)
    parameters: Mapped[dict] = mapped_column(JSON, default=dict)
    assumptions: Mapped[list] = mapped_column(JSON, default=list)
    training_or_validity_domain: Mapped[str] = mapped_column(String, default="unknown")
    query_domain: Mapped[str] = mapped_column(String, default="unknown")
    domain_match: Mapped[str] = mapped_column(String, default="unknown")  # one of MATCH_LEVELS
    run_status: Mapped[str] = mapped_column(String, default="not_computed")  # one of MODEL_RUN_STATUSES
    result_reference: Mapped[str | None] = mapped_column(String, default=None)  # CounterfactualRun.run_id
    result_summary: Mapped[dict] = mapped_column(JSON, default=dict)
    uncertainty_available: Mapped[bool] = mapped_column(default=False)
    uncertainty: Mapped[dict | None] = mapped_column(JSON, default=None)
    warnings: Mapped[list] = mapped_column(JSON, default=list)
    provenance: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[float] = mapped_column(Float)


guard_immutable_fields(ModelEvaluationRecord, mutable_fields=set())


class DeterministicCheckResult(Base):
    """doc05 §3.5/§4.2. Rule-based, versioned, never delegated to an LLM -
    see `harness/scientific_evaluation/deterministic.py::RULES` for the
    registry `rule_id`/`rule_version` are drawn from."""

    __tablename__ = "eval_deterministic_checks"

    check_id: Mapped[str] = mapped_column(String, primary_key=True)
    evaluation_id: Mapped[str] = mapped_column(ForeignKey("eval_cases.evaluation_id"), index=True)
    rule_id: Mapped[str] = mapped_column(String)
    rule_version: Mapped[str] = mapped_column(String)
    design_reference: Mapped[str] = mapped_column(String, index=True)
    category: Mapped[str] = mapped_column(String)
    status: Mapped[str] = mapped_column(String)  # pass|fail|warning|not_applicable
    severity: Mapped[str] = mapped_column(String, default="informational")  # one of SEVERITY_LEVELS
    message: Mapped[str] = mapped_column(String)
    affected_fields: Mapped[list] = mapped_column(JSON, default=list)
    evidence_or_rule_reference: Mapped[str] = mapped_column(String, default="")
    remediation: Mapped[str] = mapped_column(String, default="")
    created_at: Mapped[float] = mapped_column(Float)


guard_immutable_fields(DeterministicCheckResult, mutable_fields=set())


class ScientificReview(Base):
    """doc05 §3.7/§4.5. One row per (evaluation, design candidate, reviewer)
    - append-only, never overwritten by a later round (doc05 §9). `shared_
    model_risk=True` whenever the same underlying LLM/base-model configured
    for this harness would back more than one reviewer role (doc05 §2.1/
    §4.5's "不能声称已经消除 same-model bias" rule) - this deployment runs a
    deterministic, rubric-driven critic (no live LLM call in any Problem
    01-04 service layer either - see `harness/scientific_evaluation/
    critic.py` module docstring for why), so it is always True here unless a
    genuinely distinct provider/model is wired in later."""

    __tablename__ = "eval_scientific_reviews"

    review_id: Mapped[str] = mapped_column(String, primary_key=True)
    evaluation_id: Mapped[str] = mapped_column(ForeignKey("eval_cases.evaluation_id"), index=True)
    design_reference: Mapped[str] = mapped_column(String, index=True)
    design_version: Mapped[int] = mapped_column(Integer)
    reviewer_id: Mapped[str] = mapped_column(String)
    reviewer_type: Mapped[str] = mapped_column(String)  # one of REVIEWER_TYPES
    model_provider_and_model: Mapped[str] = mapped_column(String, default="")
    shared_model_risk: Mapped[bool] = mapped_column(default=True)
    independence_flags: Mapped[dict] = mapped_column(JSON, default=dict)  # {context_independent, rubric_independent, evidence_independent, model_independent}
    rubric_version: Mapped[str] = mapped_column(String)
    input_snapshot_reference: Mapped[dict] = mapped_column(JSON, default=dict)
    deterministic_results: Mapped[list] = mapped_column(JSON, default=list)  # DeterministicCheckResult.check_id list
    evidence_assessments: Mapped[list] = mapped_column(JSON, default=list)  # EvidenceAssessment.assessment_id list
    model_records: Mapped[list] = mapped_column(JSON, default=list)  # ModelEvaluationRecord.record_id list
    findings: Mapped[list] = mapped_column(JSON, default=list)  # CriticFinding.finding_id list
    major_concerns: Mapped[list] = mapped_column(JSON, default=list)
    minor_concerns: Mapped[list] = mapped_column(JSON, default=list)
    unsupported_claims: Mapped[list] = mapped_column(JSON, default=list)
    missing_controls: Mapped[list] = mapped_column(JSON, default=list)
    alternative_explanations: Mapped[list] = mapped_column(JSON, default=list)
    required_revisions: Mapped[list] = mapped_column(JSON, default=list)
    recommendation: Mapped[str] = mapped_column(String, default="request_more_evidence")  # one of RECOMMENDED_ACTIONS
    confidence_class: Mapped[str] = mapped_column(String, default="not_calibrated")  # one of CONFIDENCE_CLASSES
    confidence_basis: Mapped[str] = mapped_column(String, default="")
    limitations: Mapped[list] = mapped_column(JSON, default=list)
    created_at: Mapped[float] = mapped_column(Float)


guard_immutable_fields(ScientificReview, mutable_fields=set())


class CriticFinding(Base):
    """doc05 §3.6. Belongs to exactly one `ScientificReview`; `blocking`
    is what `revision.py`/the meta-review reads to force a revision cycle
    or block `approved_for_build` - never a bare severity label alone."""

    __tablename__ = "eval_critic_findings"

    finding_id: Mapped[str] = mapped_column(String, primary_key=True)
    review_id: Mapped[str] = mapped_column(ForeignKey("eval_scientific_reviews.review_id"), index=True)
    design_reference: Mapped[str] = mapped_column(String, index=True)
    category: Mapped[str] = mapped_column(String)  # one of CRITIC_CATEGORIES
    severity: Mapped[str] = mapped_column(String)  # one of SEVERITY_LEVELS
    claim_reference: Mapped[str | None] = mapped_column(String, default=None)
    finding: Mapped[str] = mapped_column(String)
    why_it_matters: Mapped[str] = mapped_column(String, default="")
    supporting_evidence: Mapped[list] = mapped_column(JSON, default=list)
    contradictory_evidence: Mapped[list] = mapped_column(JSON, default=list)
    alternative_explanations: Mapped[list] = mapped_column(JSON, default=list)
    falsification_condition: Mapped[str] = mapped_column(String, default="")
    required_action: Mapped[str] = mapped_column(String, default="")
    blocking: Mapped[bool] = mapped_column(default=False)
    resolvable: Mapped[bool] = mapped_column(default=True)
    status: Mapped[str] = mapped_column(String, default="open")  # open|resolved|acknowledged_risk
    created_at: Mapped[float] = mapped_column(Float)


guard_immutable_fields(CriticFinding, mutable_fields={"status"})


class CandidateEvaluationVector(Base):
    """doc05 §3.8. Every dimension is a `{mode, level_or_value, unit, basis,
    source}` dict - `mode` is always one of `computed`/`qualitative`/
    `not_computed`, so an unknown dimension can never silently read as
    zero/medium risk (doc05 §5.3, §3.8's own instruction). `pareto_status`/
    `dominates`/`dominated_by` are the only fields filled in after sibling
    candidates are also scored - mirrors `harness.engineering_design.
    models.DesignEvaluation.pareto_status`'s own precedent."""

    __tablename__ = "eval_candidate_vectors"

    vector_id: Mapped[str] = mapped_column(String, primary_key=True)
    evaluation_id: Mapped[str] = mapped_column(ForeignKey("eval_cases.evaluation_id"), index=True)
    candidate_id: Mapped[str] = mapped_column(String, index=True)
    design_version: Mapped[int] = mapped_column(Integer)
    hard_constraint_status: Mapped[str] = mapped_column(String, default="unknown")  # satisfied|violated|unknown
    production_potential: Mapped[dict] = mapped_column(JSON, default=dict)
    growth_impact: Mapped[dict] = mapped_column(JSON, default=dict)
    stability: Mapped[dict] = mapped_column(JSON, default=dict)
    buildability: Mapped[dict] = mapped_column(JSON, default=dict)
    genetic_complexity: Mapped[dict] = mapped_column(JSON, default=dict)
    experimental_cost: Mapped[dict] = mapped_column(JSON, default=dict)
    time_to_result: Mapped[dict] = mapped_column(JSON, default=dict)
    evidence_strength: Mapped[dict] = mapped_column(JSON, default=dict)
    risk: Mapped[dict] = mapped_column(JSON, default=dict)
    information_gain: Mapped[dict] = mapped_column(JSON, default=dict)
    uncertainty: Mapped[dict] = mapped_column(JSON, default=dict)
    pareto_status: Mapped[str | None] = mapped_column(String, default=None)
    dominates: Mapped[list] = mapped_column(JSON, default=list)
    dominated_by: Mapped[list] = mapped_column(JSON, default=list)
    excluded_reasons: Mapped[list] = mapped_column(JSON, default=list)
    created_at: Mapped[float] = mapped_column(Float)


guard_immutable_fields(
    CandidateEvaluationVector, mutable_fields={"pareto_status", "dominates", "dominated_by", "excluded_reasons"}
)


class MetaReviewDecision(Base):
    """doc05 §3.9/§4.8. Never a majority vote over `ScientificReview`s -
    any unresolved `critical` `CriticFinding` blocks `approve_for_build`
    regardless of how many reviewers disagree (doc05 §3.9's own
    instruction, enforced in `harness/scientific_evaluation/meta_review.py`
    and re-checked by `harness/workflow/gates.py::scientific_human_gate_
    precondition`)."""

    __tablename__ = "eval_meta_reviews"

    decision_id: Mapped[str] = mapped_column(String, primary_key=True)
    evaluation_id: Mapped[str] = mapped_column(ForeignKey("eval_cases.evaluation_id"), index=True)
    review_references: Mapped[list] = mapped_column(JSON, default=list)
    candidate_comparison_reference: Mapped[str | None] = mapped_column(String, default=None)
    agreements: Mapped[list] = mapped_column(JSON, default=list)
    disagreements: Mapped[list] = mapped_column(JSON, default=list)
    unresolved_conflicts: Mapped[list] = mapped_column(JSON, default=list)
    blocking_findings: Mapped[list] = mapped_column(JSON, default=list)
    recommended_action: Mapped[str] = mapped_column(String)  # one of RECOMMENDED_ACTIONS
    recommended_candidates: Mapped[list] = mapped_column(JSON, default=list)
    required_revision_tasks: Mapped[list] = mapped_column(JSON, default=list)
    required_evidence_tasks: Mapped[list] = mapped_column(JSON, default=list)
    return_target: Mapped[str | None] = mapped_column(String, default=None)
    decision_rationale: Mapped[str] = mapped_column(String, default="")
    decision_confidence: Mapped[str] = mapped_column(String, default="not_calibrated")
    human_gate_required: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[float] = mapped_column(Float)


guard_immutable_fields(MetaReviewDecision, mutable_fields=set())


class RevisionTask(Base):
    """doc05 §3.10. Created by `revision.py::generate_revision_tasks` from
    blocking/major `CriticFinding`s and failed `DeterministicCheckResult`s."""

    __tablename__ = "eval_revision_tasks"

    task_id: Mapped[str] = mapped_column(String, primary_key=True)
    evaluation_id: Mapped[str] = mapped_column(ForeignKey("eval_cases.evaluation_id"), index=True)
    source_finding_id: Mapped[str | None] = mapped_column(String, default=None)
    target_design_id: Mapped[str] = mapped_column(String, index=True)
    target_version: Mapped[int] = mapped_column(Integer)
    task_type: Mapped[str] = mapped_column(String)  # one of REVISION_TASK_TYPES
    priority: Mapped[str] = mapped_column(String, default="medium")  # critical|high|medium|low
    required_change: Mapped[str] = mapped_column(String)
    acceptance_criteria: Mapped[list] = mapped_column(JSON, default=list)
    evidence_needed: Mapped[list] = mapped_column(JSON, default=list)
    assigned_to: Mapped[str] = mapped_column(String, default="designer")
    status: Mapped[str] = mapped_column(String, default="open")  # open|in_progress|resolved|wont_fix
    resolution_reference: Mapped[str | None] = mapped_column(String, default=None)
    created_at: Mapped[float] = mapped_column(Float)


guard_immutable_fields(RevisionTask, mutable_fields={"status", "resolution_reference"})


class RevisionCycle(Base):
    """doc05 §3.10. One row per revision round; `to_design_id`/`to_design_
    version` point at the NEW `CandidateDesign` row `harness.engineering_
    design.portfolio_service.revise_candidate` creates - the parent row is
    never edited in place (enforced by that function's own `guard_
    immutable_fields` already)."""

    __tablename__ = "eval_revision_cycles"

    cycle_id: Mapped[str] = mapped_column(String, primary_key=True)
    evaluation_id: Mapped[str] = mapped_column(ForeignKey("eval_cases.evaluation_id"), index=True)
    from_design_id: Mapped[str] = mapped_column(String)
    from_design_version: Mapped[int] = mapped_column(Integer)
    revision_tasks: Mapped[list] = mapped_column(JSON, default=list)
    to_design_id: Mapped[str | None] = mapped_column(String, default=None)
    to_design_version: Mapped[int | None] = mapped_column(Integer, default=None)
    changed_fields: Mapped[list] = mapped_column(JSON, default=list)
    resolved_findings: Mapped[list] = mapped_column(JSON, default=list)
    unresolved_findings: Mapped[list] = mapped_column(JSON, default=list)
    new_findings: Mapped[list] = mapped_column(JSON, default=list)
    stop_reason: Mapped[str | None] = mapped_column(String, default=None)
    created_at: Mapped[float] = mapped_column(Float)


guard_immutable_fields(RevisionCycle, mutable_fields=set())


class HumanEvaluationDecision(Base):
    """doc05 §3.11/§2.7. The ONE gate that may move an `EvaluationCase`
    into `approved_for_planning`/`approved_for_build` - `reviewer_or_
    approver` must be a distinct identity from the candidate's `proposed_
    by` (reuses `harness.designs.service.SelfApprovalError`, same rule
    Problem 04's own `governance_service.record_human_decision` already
    enforces at its later, narrower build-approval step). Fully immutable:
    a changed mind creates a new decision row, never an edit."""

    __tablename__ = "eval_human_decisions"

    human_decision_id: Mapped[str] = mapped_column(String, primary_key=True)
    evaluation_id: Mapped[str] = mapped_column(ForeignKey("eval_cases.evaluation_id"), index=True)
    decision: Mapped[str] = mapped_column(String)  # one of HUMAN_DECISIONS
    selected_candidates: Mapped[list] = mapped_column(JSON, default=list)
    conditions: Mapped[list] = mapped_column(JSON, default=list)
    reviewer_or_approver: Mapped[str] = mapped_column(String)
    role: Mapped[str] = mapped_column(String, default="")
    rationale: Mapped[str] = mapped_column(String, default="")
    acknowledged_risks: Mapped[list] = mapped_column(JSON, default=list)
    timestamp: Mapped[float] = mapped_column(Float)


guard_immutable_fields(HumanEvaluationDecision, mutable_fields=set())


class EvaluationMemoryEvent(Base):
    """doc05 §3.12/§9. Deliberately keeps `raw_feedback_references` (raw
    observations, e.g. a `DesignOutcomeRecord.outcome_id`) separate from
    `lesson`/`interpretation_uncertainty` (Reviewer/Agent interpretation) -
    doc05 §9's "原始观测、Reviewer 解释和 Memory lesson 必须分开保存" -
    never one collapsed into the other."""

    __tablename__ = "eval_memory_events"

    event_id: Mapped[str] = mapped_column(String, primary_key=True)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.project_id"), index=True)
    evaluation_id: Mapped[str] = mapped_column(ForeignKey("eval_cases.evaluation_id"), index=True)
    design_id: Mapped[str] = mapped_column(String, index=True)
    design_version: Mapped[int] = mapped_column(Integer)
    event_type: Mapped[str] = mapped_column(String)
    raw_feedback_references: Mapped[list] = mapped_column(JSON, default=list)
    critic_findings: Mapped[list] = mapped_column(JSON, default=list)
    failed_assumptions: Mapped[list] = mapped_column(JSON, default=list)
    failure_class: Mapped[str | None] = mapped_column(String, default=None)
    lesson: Mapped[str] = mapped_column(String, default="")
    do_not_repeat: Mapped[list] = mapped_column(JSON, default=list)
    next_iteration_hint: Mapped[list] = mapped_column(JSON, default=list)
    interpretation_uncertainty: Mapped[str] = mapped_column(String, default="")
    created_at: Mapped[float] = mapped_column(Float)


guard_immutable_fields(EvaluationMemoryEvent, mutable_fields=set())


class DiagnosisReturnRequest(Base):
    """doc05 §7. Never overwrites the original `DiagnosisDecision` - on
    creation, `diagnosis_return.py` calls the real `harness.diagnosis.
    service.start_diagnosis_session` to open a genuine new diagnosis round
    for the same project (doc05 §7's own instruction: "必须创建新诊断轮次
    或版本"), never a free-text note asking a human to go look."""

    __tablename__ = "eval_diagnosis_return_requests"

    request_id: Mapped[str] = mapped_column(String, primary_key=True)
    source_evaluation_id: Mapped[str] = mapped_column(ForeignKey("eval_cases.evaluation_id"), index=True)
    source_design_id: Mapped[str] = mapped_column(String)
    source_design_version: Mapped[int] = mapped_column(Integer)
    triggering_findings: Mapped[list] = mapped_column(JSON, default=list)
    affected_hypotheses: Mapped[list] = mapped_column(JSON, default=list)
    new_counterevidence: Mapped[list] = mapped_column(JSON, default=list)
    alternative_explanations: Mapped[list] = mapped_column(JSON, default=list)
    requested_discriminating_information: Mapped[list] = mapped_column(JSON, default=list)
    context: Mapped[dict] = mapped_column(JSON, default=dict)
    new_diagnosis_session_id: Mapped[str | None] = mapped_column(String, default=None)
    status: Mapped[str] = mapped_column(String, default="pending")  # pending|session_created|acknowledged
    created_by: Mapped[str] = mapped_column(String)
    created_at: Mapped[float] = mapped_column(Float)


guard_immutable_fields(DiagnosisReturnRequest, mutable_fields={"new_diagnosis_session_id", "status"})

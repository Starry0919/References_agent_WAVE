"""Scientific Golden Set (prompt Workstream 4, §7): schema only - never a
fixture with hardcoded production answers (prompt §7.1's own instruction).
`ScientificGoldenCase` is the PUBLIC case shape (what a runner feeds to the
real pipeline); `GoldenCaseAnswerKey` is a SEPARATE table holding the
"hidden" expectations - `harness.golden_set.runner.run_golden_case` never
queries `GoldenCaseAnswerKey` while driving a case through the system, only
`harness.golden_set.scoring` reads it afterward, so the answer key cannot
leak into (and cannot be blamed for biasing) a run's own behavior.

`review_status` defaults to `pending_expert_review` and MUST NOT be set to
`expert_reviewed` by any code path in this repository - that transition is
only ever made by a human editing `GoldenCaseAnswerKey.expert_reviewers`/
`review_status` directly (or via a future review UI), never by an
evaluation run. `harness/golden_set/service.py::mark_expert_reviewed`
enforces this by requiring a real reviewer identity string.
"""
from __future__ import annotations

from sqlalchemy import JSON, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from harness.db import Base, guard_immutable_fields

CASE_TYPES = (
    "diagnosis_trp", "diagnosis_other_product", "diagnosis_insufficient_evidence",
    "unsafe_design", "model_domain_mismatch", "observation_conflict",
)
REVIEW_STATUSES = ("pending_expert_review", "expert_reviewed", "rejected")
RECOMMENDED_METRIC_THRESHOLDS = {
    # prompt §7.6 - RECOMMENDED candidates, not pre-approved standards; a
    # project lead must ratify these before they mean "passed" in any
    # release-gating sense. Stored here as data, not silently asserted true
    # anywhere in code.
    "hallucinated_reference_rate": 0.0,
    "unsupported_numeric_prediction_rate": 0.0,
    "unsafe_design_false_approval_rate": 0.0,
    "inappropriate_model_use_rate": 0.0,
    "evidence_traceability": 1.0,
    "critical_finding_recall": 0.90,
    "false_approval_rate": 0.05,
    "workflow_branch_accuracy": 0.90,
}


class ScientificGoldenCase(Base):
    """The PUBLIC case (prompt §7.3, minus the hidden fields) - safe to
    pass into `harness.golden_set.runner.run_golden_case`."""

    __tablename__ = "golden_cases"

    case_id: Mapped[str] = mapped_column(String, primary_key=True)
    title: Mapped[str] = mapped_column(String)
    case_type: Mapped[str] = mapped_column(String, index=True)  # one of CASE_TYPES
    organism: Mapped[str] = mapped_column(String, default="Escherichia coli")
    strain: Mapped[str] = mapped_column(String, default="K-12")
    condition: Mapped[dict] = mapped_column(JSON, default=dict)
    objective: Mapped[str] = mapped_column(String)
    input_observations: Mapped[list] = mapped_column(JSON, default=list)
    available_evidence_refs: Mapped[list] = mapped_column(JSON, default=list)
    case_inputs: Mapped[dict] = mapped_column(JSON, default=dict)  # case-type-specific driver inputs (phenotype text, data_sufficiency flags, genotype under test, target gene, etc.)
    version: Mapped[int] = mapped_column(Integer, default=1)
    created_at: Mapped[float] = mapped_column(Float)


guard_immutable_fields(ScientificGoldenCase, mutable_fields={"version"})


class GoldenCaseAnswerKey(Base):
    """The HIDDEN annotations (prompt §7.3/§7.4) - `case_id` is a 1:1 FK to
    `ScientificGoldenCase.case_id`, kept in a separate table specifically so
    a runner can be handed only a `ScientificGoldenCase` object and have no
    Python-level access to this one."""

    __tablename__ = "golden_case_answer_keys"

    case_id: Mapped[str] = mapped_column(String, primary_key=True)
    expected_mechanism_categories: Mapped[list] = mapped_column(JSON, default=list)
    acceptable_competing_hypotheses: Mapped[list] = mapped_column(JSON, default=list)
    unacceptable_claims: Mapped[list] = mapped_column(JSON, default=list)
    acceptable_strategy_classes: Mapped[list] = mapped_column(JSON, default=list)
    clearly_wrong_strategies: Mapped[list] = mapped_column(JSON, default=list)
    required_critic_findings: Mapped[list] = mapped_column(JSON, default=list)
    model_applicability_expectation: Mapped[str] = mapped_column(String, default="unknown")
    expected_workflow_branch: Mapped[str] = mapped_column(String, default="unknown")
    validation_plan_requirements: Mapped[list] = mapped_column(JSON, default=list)
    expert_reviewers: Mapped[list] = mapped_column(JSON, default=list)  # [{name, affiliation, date}] - empty until a real human reviews
    review_status: Mapped[str] = mapped_column(String, default="pending_expert_review")  # one of REVIEW_STATUSES
    review_notes: Mapped[str] = mapped_column(String, default="")
    created_at: Mapped[float] = mapped_column(Float)


guard_immutable_fields(GoldenCaseAnswerKey, mutable_fields={"expert_reviewers", "review_status", "review_notes"})


class GoldenCaseEvaluationRun(Base):
    """One system-under-test pass over one `ScientificGoldenCase` -
    append-only, never overwritten (prompt §14: results must be
    reproducible/comparable across versions, not silently replaced)."""

    __tablename__ = "golden_case_evaluation_runs"

    evaluation_run_id: Mapped[str] = mapped_column(String, primary_key=True)
    case_id: Mapped[str] = mapped_column(String, index=True)
    case_version: Mapped[int] = mapped_column(Integer)
    project_id: Mapped[str | None] = mapped_column(String, default=None)
    workflow_run_id: Mapped[str | None] = mapped_column(String, default=None)
    llm_adapters_enabled: Mapped[bool] = mapped_column(default=False)
    system_output: Mapped[dict] = mapped_column(JSON, default=dict)  # normalized, structured record of what the system actually produced
    automated_metrics: Mapped[dict] = mapped_column(JSON, default=dict)  # {metric_name: {value, numerator, denominator, applicable}}
    errors: Mapped[list] = mapped_column(JSON, default=list)
    created_at: Mapped[float] = mapped_column(Float)


guard_immutable_fields(GoldenCaseEvaluationRun, mutable_fields=set())


class GoldenCaseHumanReview(Base):
    """A real human's scoring of one `GoldenCaseEvaluationRun` against
    metrics that need judgment (prompt §7.5's `human_expert_rating` and
    the qualitative recall/coverage metrics) - populated only by a human
    filling in `knowledge/golden_set/human_review_template.md`, never by
    any automated code path."""

    __tablename__ = "golden_case_human_reviews"

    review_id: Mapped[str] = mapped_column(String, primary_key=True)
    evaluation_run_id: Mapped[str] = mapped_column(String, index=True)
    reviewer_name: Mapped[str] = mapped_column(String)
    reviewer_affiliation: Mapped[str] = mapped_column(String, default="")
    review_date: Mapped[str] = mapped_column(String)  # ISO date string, human-entered
    hypothesis_category_recall_score: Mapped[float | None] = mapped_column(Float, default=None)
    critical_finding_recall_score: Mapped[float | None] = mapped_column(Float, default=None)
    validation_plan_coverage_score: Mapped[float | None] = mapped_column(Float, default=None)
    human_expert_rating: Mapped[float | None] = mapped_column(Float, default=None)  # 1-5
    notes: Mapped[str] = mapped_column(String, default="")
    created_at: Mapped[float] = mapped_column(Float)


guard_immutable_fields(GoldenCaseHumanReview, mutable_fields=set())

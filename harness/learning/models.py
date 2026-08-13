"""HypothesisVersion, FailureCase, LearningCycle (doc 8.6-8.8) and
KnowledgeClaim (doc 6.2/6.8) - the versioned scientific-reasoning layer.
New evidence never rewrites an old hypothesis or claim; it produces a new
version/status transition, always leaving the prior one readable.
"""
from __future__ import annotations

from sqlalchemy import JSON, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from harness.db import Base, guard_immutable_fields

# doc 8.7: failure_class must distinguish at least these - technical/
# construction/measurement failures must never be usable as biological
# negative evidence (enforced in harness/learning/outcome_classifier.py
# and harness/workflow/iterative_loop.py's Policy Update Gate).
FAILURE_CLASSES = (
    "construction",
    "execution",
    "measurement",
    "schema_tool",
    "biological_null",
    "hypothesis_contradiction",
    "tradeoff",
    "safety_constraint",
    "inconclusive",
)

# doc02 8.6's original 4 plus doc03 2.4's richer 7-value vocabulary
# (union, not a replacement - doc03's set is a strict refinement of doc02's
# that better resists overclaiming certainty, e.g. distinguishing
# "provisionally_ruled_out" from a bare "rejected").
HYPOTHESIS_POSTERIOR_STATUSES = (
    "supported", "weakened", "rejected", "inconclusive",
    "untested", "weakly_supported", "strongly_supported",
    "provisionally_ruled_out", "non_discriminating", "out_of_scope",
)

# doc03 2.2: the four mandatory competing-hypothesis categories.
MECHANISM_CLASSES = ("biological_mechanism", "process_environment", "measurement_data", "model_mismatch")

# doc 6.2's promotion ladder.
KNOWLEDGE_CLAIM_STATUSES = ("project_candidate", "lab_candidate", "lab_approved", "retracted")


class HypothesisFamily(Base):
    """Groups the version chain for one evolving hypothesis - referenced by
    `HypothesisVersion.hypothesis_family_id` (doc 8.6). Not itself in the
    doc's yaml, but implied by the field existing; cheap and useful for
    "show me this hypothesis's whole history" queries."""

    __tablename__ = "hypothesis_families"

    hypothesis_family_id: Mapped[str] = mapped_column(String, primary_key=True)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.project_id"), index=True)
    title: Mapped[str] = mapped_column(String)
    created_at: Mapped[float] = mapped_column(Float)


class HypothesisVersion(Base):
    __tablename__ = "hypothesis_versions"

    hypothesis_version_id: Mapped[str] = mapped_column(String, primary_key=True)
    hypothesis_family_id: Mapped[str] = mapped_column(ForeignKey("hypothesis_families.hypothesis_family_id"), index=True)
    statement: Mapped[str] = mapped_column(String)
    mechanism_graph_ref: Mapped[str | None] = mapped_column(String, default=None)
    predicted_observations: Mapped[list] = mapped_column(JSON, default=list)
    supporting_evidence_ids: Mapped[list] = mapped_column(JSON, default=list)
    contradicting_evidence_ids: Mapped[list] = mapped_column(JSON, default=list)
    alternatives: Mapped[list] = mapped_column(JSON, default=list)
    posterior_status: Mapped[str] = mapped_column(String, default="inconclusive")
    confidence: Mapped[str] = mapped_column(String, default="low")
    applicability_scope: Mapped[dict] = mapped_column(JSON, default=dict)
    parent_hypothesis_version_id: Mapped[str | None] = mapped_column(String, default=None)
    created_at: Mapped[float] = mapped_column(Float)
    # Problem 03 (Bottleneck Diagnosis) fields, added via migration 0002.
    # `applicability_scope` above already covers doc 3.5's
    # applicability_context; `predicted_observations` covers
    # expected_observations - reused, not duplicated.
    mechanism_class: Mapped[str | None] = mapped_column(String, default=None, index=True)  # one of MECHANISM_CLASSES
    scope: Mapped[dict] = mapped_column(JSON, default=dict)
    causal_graph_nodes: Mapped[list] = mapped_column(JSON, default=list)
    causal_graph_edges: Mapped[list] = mapped_column(JSON, default=list)
    observations_explained: Mapped[list] = mapped_column(JSON, default=list)  # observation_ids
    discriminating_predictions: Mapped[list] = mapped_column(JSON, default=list)
    falsifiers: Mapped[list] = mapped_column(JSON, default=list)
    assumptions: Mapped[list] = mapped_column(JSON, default=list)
    temporal_scope: Mapped[dict | None] = mapped_column(JSON, default=None)
    related_hypothesis_ids: Mapped[list] = mapped_column(JSON, default=list)
    generation_provenance: Mapped[dict] = mapped_column(JSON, default=dict)  # {"method": "rule_based_v1"|"llm_generated", ...}


# Fully immutable: new evidence never rewrites an old hypothesis judgment,
# it produces a new HypothesisVersion row with parent_hypothesis_version_id
# pointing back (doc 8.6).
guard_immutable_fields(HypothesisVersion, mutable_fields=set())


class FailureCase(Base):
    __tablename__ = "failure_cases"

    failure_case_id: Mapped[str] = mapped_column(String, primary_key=True)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.project_id"), index=True)
    design_version_id: Mapped[str | None] = mapped_column(String, default=None)
    experiment_run_id: Mapped[str | None] = mapped_column(String, default=None)
    failure_class: Mapped[str] = mapped_column(String)
    expected_outcome: Mapped[str] = mapped_column(String, default="")
    observed_outcome_ids: Mapped[list] = mapped_column(JSON, default=list)  # Observation ids
    data_qc_status: Mapped[str] = mapped_column(String, default="pending")
    candidate_causes: Mapped[list] = mapped_column(JSON, default=list)
    causal_confidence: Mapped[str] = mapped_column(String, default="low")
    applicability_scope: Mapped[dict] = mapped_column(JSON, default=dict)  # {medium, carbon_source, ...}
    policy_update_proposal: Mapped[dict | None] = mapped_column(JSON, default=None)
    human_review_state: Mapped[str] = mapped_column(String, default="not_required")  # not_required|pending|reviewed
    resolution_status: Mapped[str] = mapped_column(String, default="open")  # open|resolved|inconclusive
    created_at: Mapped[float] = mapped_column(Float)


# The causal finding itself (failure_class, candidate_causes,
# causal_confidence, applicability_scope) is immutable once classified;
# only the human-review/resolution workflow fields may progress.
guard_immutable_fields(FailureCase, mutable_fields={"human_review_state", "resolution_status", "policy_update_proposal"})


class LearningCycle(Base):
    __tablename__ = "learning_cycles"

    cycle_id: Mapped[str] = mapped_column(String, primary_key=True)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.project_id"), index=True)
    input_design_versions: Mapped[list] = mapped_column(JSON, default=list)
    experiment_run_ids: Mapped[list] = mapped_column(JSON, default=list)
    accepted_observation_ids: Mapped[list] = mapped_column(JSON, default=list)
    hypothesis_updates: Mapped[list] = mapped_column(JSON, default=list)  # hypothesis_version_ids
    model_update_ids: Mapped[list] = mapped_column(JSON, default=list)
    policy_update_ids: Mapped[list] = mapped_column(JSON, default=list)
    next_design_version_ids: Mapped[list] = mapped_column(JSON, default=list)
    human_decisions: Mapped[list] = mapped_column(JSON, default=list)
    status: Mapped[str] = mapped_column(String, default="in_progress")  # in_progress|completed
    created_at: Mapped[float] = mapped_column(Float)


class KnowledgeClaim(Base):
    """doc 6.2/6.8: experience is NOT knowledge until it survives the
    promotion ladder. `independence_groups` records which
    supporting_experiments are mutually independent (distinct batch/
    construction background) vs. technical replicates of each other -
    see `harness/memory/knowledge_claims.py` for the check that a single
    project observation, or N technical replicates of one batch, can never
    satisfy a promotion threshold."""

    __tablename__ = "knowledge_claims"

    claim_id: Mapped[str] = mapped_column(String, primary_key=True)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.project_id"), index=True)  # originating project
    statement: Mapped[str] = mapped_column(String)
    scope: Mapped[dict] = mapped_column(JSON, default=dict)  # {species, strain_background, genotype_context, medium, carbon_source, cultivation_mode, assay}
    supporting_experiments: Mapped[list] = mapped_column(JSON, default=list)  # experiment_run_ids
    contradicting_experiments: Mapped[list] = mapped_column(JSON, default=list)
    independence_groups: Mapped[list] = mapped_column(JSON, default=list)  # list[list[experiment_run_id]]
    evidence_grade: Mapped[str] = mapped_column(String, default="low")  # high|medium|low
    status: Mapped[str] = mapped_column(String, default="project_candidate")
    reviewers: Mapped[list] = mapped_column(JSON, default=list)  # actor_ids
    promotion_record: Mapped[list] = mapped_column(JSON, default=list)  # audit trail of status transitions
    supersedes_claim_id: Mapped[str | None] = mapped_column(String, default=None)
    created_by: Mapped[str] = mapped_column(String)
    created_at: Mapped[float] = mapped_column(Float)
    updated_at: Mapped[float] = mapped_column(Float)

"""HypothesisVersion / FailureCase / LearningCycle mutations (doc 8.6-8.8).
New evidence never rewrites an old hypothesis - `revise_hypothesis` always
creates a new version and requires the Hypothesis Update Gate to pass
first; `HypothesisVersion`'s ORM immutability guard (see
`harness/learning/models.py`) enforces the "never rewritten" half at the
database layer too, independent of this service's own discipline.
"""
from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from harness.ids import new_id, now
from harness.learning.models import FAILURE_CLASSES, FailureCase, HypothesisFamily, HypothesisVersion, LearningCycle
from harness.memory import event_types as et
from harness.memory.event_store import append_event, snapshot
from harness.workflow.gates import hypothesis_update_gate

HYPOTHESIS_SNAPSHOT_FIELDS = (
    "hypothesis_version_id", "hypothesis_family_id", "statement", "mechanism_graph_ref",
    "predicted_observations", "supporting_evidence_ids", "contradicting_evidence_ids", "alternatives",
    "posterior_status", "confidence", "applicability_scope", "parent_hypothesis_version_id", "created_at",
    "mechanism_class", "scope", "causal_graph_nodes", "causal_graph_edges", "observations_explained",
    "discriminating_predictions", "falsifiers", "assumptions", "temporal_scope", "related_hypothesis_ids",
    "generation_provenance",
)

FAILURE_SNAPSHOT_FIELDS = (
    "failure_case_id", "project_id", "design_version_id", "experiment_run_id", "failure_class",
    "expected_outcome", "observed_outcome_ids", "data_qc_status", "candidate_causes", "causal_confidence",
    "applicability_scope", "policy_update_proposal", "human_review_state", "resolution_status", "created_at",
)

LEARNING_CYCLE_SNAPSHOT_FIELDS = (
    "cycle_id", "project_id", "input_design_versions", "experiment_run_ids", "accepted_observation_ids",
    "hypothesis_updates", "model_update_ids", "policy_update_ids", "next_design_version_ids",
    "human_decisions", "status", "created_at",
)


class HypothesisUpdateRejected(RuntimeError):
    """The Hypothesis Update Gate rejected a proposed revision (doc 10.2):
    missing expected-vs-observed comparison, alternatives considered, or an
    explicit uncertainty statement."""


def create_hypothesis_family(session: Session, *, project_id: str, title: str) -> HypothesisFamily:
    fam = HypothesisFamily(hypothesis_family_id=new_id("HYPFAM"), project_id=project_id, title=title, created_at=now())
    session.add(fam)
    session.flush()
    return fam


def propose_hypothesis(
    session: Session,
    *,
    project_id: str,
    hypothesis_family_id: str,
    statement: str,
    actor_id: str,
    predicted_observations: list[Any] | None = None,
    supporting_evidence_ids: list[str] | None = None,
    contradicting_evidence_ids: list[str] | None = None,
    alternatives: list[str] | None = None,
    posterior_status: str = "inconclusive",
    confidence: str = "low",
    applicability_scope: dict[str, Any] | None = None,
    parent_hypothesis_version_id: str | None = None,
    mechanism_graph_ref: str | None = None,
    mechanism_class: str | None = None,
    scope: dict[str, Any] | None = None,
    causal_graph_nodes: list[Any] | None = None,
    causal_graph_edges: list[Any] | None = None,
    observations_explained: list[str] | None = None,
    discriminating_predictions: list[Any] | None = None,
    falsifiers: list[str] | None = None,
    assumptions: list[str] | None = None,
    temporal_scope: dict[str, Any] | None = None,
    related_hypothesis_ids: list[str] | None = None,
    generation_provenance: dict[str, Any] | None = None,
) -> HypothesisVersion:
    hv = HypothesisVersion(
        hypothesis_version_id=new_id("HYP"),
        hypothesis_family_id=hypothesis_family_id,
        statement=statement,
        mechanism_graph_ref=mechanism_graph_ref,
        predicted_observations=predicted_observations or [],
        supporting_evidence_ids=supporting_evidence_ids or [],
        contradicting_evidence_ids=contradicting_evidence_ids or [],
        alternatives=alternatives or [],
        posterior_status=posterior_status,
        confidence=confidence,
        applicability_scope=applicability_scope or {},
        parent_hypothesis_version_id=parent_hypothesis_version_id,
        mechanism_class=mechanism_class,
        scope=scope or {},
        causal_graph_nodes=causal_graph_nodes or [],
        causal_graph_edges=causal_graph_edges or [],
        observations_explained=observations_explained or [],
        discriminating_predictions=discriminating_predictions or [],
        falsifiers=falsifiers or [],
        assumptions=assumptions or [],
        temporal_scope=temporal_scope,
        related_hypothesis_ids=related_hypothesis_ids or [],
        generation_provenance=generation_provenance or {},
        created_at=now(),
    )
    session.add(hv)
    session.flush()
    append_event(
        session,
        project_id=project_id,
        event_type=et.HYPOTHESIS_UPDATED,
        entity_type="HypothesisVersion",
        entity_id=hv.hypothesis_version_id,
        payload=snapshot(hv, HYPOTHESIS_SNAPSHOT_FIELDS),
        actor_type="agent" if actor_id == "system" else "human",
        actor_id=actor_id,
        causation_id=parent_hypothesis_version_id,
    )
    return hv


def revise_hypothesis(
    session: Session,
    *,
    parent_hypothesis_version_id: str,
    statement: str,
    posterior_status: str,
    confidence: str,
    actor_id: str,
    has_expected_vs_observed: bool,
    has_alternatives_considered: bool,
    has_uncertainty: bool,
    predicted_observations: list[Any] | None = None,
    supporting_evidence_ids: list[str] | None = None,
    contradicting_evidence_ids: list[str] | None = None,
    alternatives: list[str] | None = None,
    applicability_scope: dict[str, Any] | None = None,
    **diagnosis_fields: Any,
) -> HypothesisVersion:
    """Enforces the Hypothesis Update Gate before creating the new version
    - a revision with no stated alternatives/uncertainty/comparison is
    rejected outright, never silently accepted as a shortcut.
    `**diagnosis_fields` forwards Problem 03's fields (mechanism_class,
    causal_graph_nodes, discriminating_predictions, ...) unchanged when a
    belief update revises one of them; omitted fields default to empty as
    in `propose_hypothesis`."""
    parent = session.get(HypothesisVersion, parent_hypothesis_version_id)
    if parent is None:
        raise ValueError(f"no such hypothesis version: {parent_hypothesis_version_id}")

    gate_result = hypothesis_update_gate(
        has_expected_vs_observed=has_expected_vs_observed,
        has_alternatives_considered=has_alternatives_considered,
        has_uncertainty=has_uncertainty,
    )
    if gate_result.status.value != "pass":
        raise HypothesisUpdateRejected(
            f"hypothesis update rejected by HypothesisUpdateGate: {[v.message for v in gate_result.violations]}"
        )

    family = session.get(HypothesisFamily, parent.hypothesis_family_id)
    return propose_hypothesis(
        session,
        project_id=family.project_id,
        hypothesis_family_id=parent.hypothesis_family_id,
        statement=statement,
        actor_id=actor_id,
        predicted_observations=predicted_observations,
        supporting_evidence_ids=supporting_evidence_ids,
        contradicting_evidence_ids=contradicting_evidence_ids,
        alternatives=alternatives,
        posterior_status=posterior_status,
        confidence=confidence,
        applicability_scope=applicability_scope,
        parent_hypothesis_version_id=parent_hypothesis_version_id,
        **diagnosis_fields,
    )


def classify_failure(
    session: Session,
    *,
    project_id: str,
    failure_class: str,
    actor_id: str,
    design_version_id: str | None = None,
    experiment_run_id: str | None = None,
    expected_outcome: str = "",
    observed_outcome_ids: list[str] | None = None,
    data_qc_status: str = "passed",
    candidate_causes: list[str] | None = None,
    causal_confidence: str = "low",
    applicability_scope: dict[str, Any] | None = None,
) -> FailureCase:
    if failure_class not in FAILURE_CLASSES:
        raise ValueError(f"unrecognized failure_class {failure_class!r}; must be one of {FAILURE_CLASSES}")
    fc = FailureCase(
        failure_case_id=new_id("FAIL"),
        project_id=project_id,
        design_version_id=design_version_id,
        experiment_run_id=experiment_run_id,
        failure_class=failure_class,
        expected_outcome=expected_outcome,
        observed_outcome_ids=observed_outcome_ids or [],
        data_qc_status=data_qc_status,
        candidate_causes=candidate_causes or [],
        causal_confidence=causal_confidence,
        applicability_scope=applicability_scope or {},
        created_at=now(),
    )
    session.add(fc)
    session.flush()
    append_event(
        session, project_id=project_id, event_type=et.FAILURE_CLASSIFIED, entity_type="FailureCase",
        entity_id=fc.failure_case_id, payload=snapshot(fc, FAILURE_SNAPSHOT_FIELDS),
        actor_type="agent", actor_id=actor_id,
    )
    return fc


def set_failure_resolution(
    session: Session, *, failure_case_id: str, resolution_status: str, actor_id: str, human_review_state: str | None = None
) -> FailureCase:
    fc = session.get(FailureCase, failure_case_id)
    if fc is None:
        raise ValueError(f"no such failure case: {failure_case_id}")
    fc.resolution_status = resolution_status
    if human_review_state is not None:
        fc.human_review_state = human_review_state
    session.flush()
    append_event(
        session, project_id=fc.project_id, event_type=et.FAILURE_CLASSIFIED, entity_type="FailureCase",
        entity_id=failure_case_id, payload=snapshot(fc, FAILURE_SNAPSHOT_FIELDS),
        actor_type="human", actor_id=actor_id,
    )
    return fc


def start_learning_cycle(
    session: Session, *, project_id: str, input_design_versions: list[str], experiment_run_ids: list[str], actor_id: str
) -> LearningCycle:
    lc = LearningCycle(
        cycle_id=new_id("LC"), project_id=project_id, input_design_versions=input_design_versions,
        experiment_run_ids=experiment_run_ids, status="in_progress", created_at=now(),
    )
    session.add(lc)
    session.flush()
    append_event(
        session, project_id=project_id, event_type=et.LEARNING_CYCLE_STARTED, entity_type="LearningCycle",
        entity_id=lc.cycle_id, payload=snapshot(lc, LEARNING_CYCLE_SNAPSHOT_FIELDS),
        actor_type="agent", actor_id=actor_id,
    )
    return lc


def complete_learning_cycle(
    session: Session,
    *,
    cycle_id: str,
    actor_id: str,
    accepted_observation_ids: list[str] | None = None,
    hypothesis_updates: list[str] | None = None,
    next_design_version_ids: list[str] | None = None,
    human_decisions: list[dict[str, Any]] | None = None,
) -> LearningCycle:
    lc = session.get(LearningCycle, cycle_id)
    if lc is None:
        raise ValueError(f"no such learning cycle: {cycle_id}")
    lc.accepted_observation_ids = accepted_observation_ids or []
    lc.hypothesis_updates = hypothesis_updates or []
    lc.next_design_version_ids = next_design_version_ids or []
    lc.human_decisions = human_decisions or []
    lc.status = "completed"
    session.flush()
    append_event(
        session, project_id=lc.project_id, event_type=et.LEARNING_CYCLE_COMPLETED, entity_type="LearningCycle",
        entity_id=lc.cycle_id, payload=snapshot(lc, LEARNING_CYCLE_SNAPSHOT_FIELDS),
        actor_type="agent", actor_id=actor_id,
    )
    return lc

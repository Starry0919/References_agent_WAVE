"""Decision-sensitive EvidenceNeed loop with typed routing and auditable stopping."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

from sqlalchemy.orm import Session

from harness.evidence_retrieval.models import EvidenceNeed
from harness.ids import new_id, now
from harness.learning.models import HypothesisFamily, HypothesisVersion
from harness.learning.service import revise_hypothesis

SOURCE_TYPES = {"primary_literature", "review_textbook", "biological_database", "model_tool", "DDR", "engineering_memory", "failure_memory", "historical_prior"}
GAP_TYPES = {"critical_claim_coverage", "unresolved_contradiction", "context_mismatch", "missing_mechanistic_edge", "quantitative_inconsistency", "alternative_not_discriminated", "candidate_specific_evidence"}


def create_evidence_need(db: Session, *, project_id: str, decision_node_id: str, claim_or_hypothesis_id: str,
                         gap_type: str, missing_relation: str, required_source_type: str, required_context: dict,
                         criticality: str = "high", expected_information_gain: str = "high") -> EvidenceNeed:
    if gap_type not in GAP_TYPES: raise ValueError(f"unsupported evidence gap: {gap_type}")
    if required_source_type not in SOURCE_TYPES: raise ValueError(f"unsupported source route: {required_source_type}")
    row = EvidenceNeed(need_id=new_id("ENEED"), project_id=project_id, decision_node_id=decision_node_id,
        claim_or_hypothesis_id=claim_or_hypothesis_id, question_type=gap_type, missing_relation=missing_relation,
        required_source_type=required_source_type, required_context=required_context, criticality=criticality,
        expected_information_gain=expected_information_gain,
        stop_rule={"allowed": ["all_critical_gaps_resolved", "decision_insensitive", "low_marginal_gain", "source_exhausted", "budget_reached", "requires_experiment", "requires_human_judgment", "unsafe_contradiction"]},
        created_at=now())
    db.add(row); db.flush(); return row


def resolve_evidence_need(db: Session, *, need_id: str, query: str,
                          retriever: Callable[[str, dict[str, Any]], list[dict[str, Any]]],
                          accept: Callable[[dict[str, Any]], tuple[bool, str]], budget_remaining: int = 1) -> EvidenceNeed:
    need = db.get(EvidenceNeed, need_id)
    if need is None: raise ValueError(f"no such EvidenceNeed: {need_id}")
    if need.status != "open": raise ValueError("EvidenceNeed is not open")
    if budget_remaining <= 0:
        need.status = "stopped_budget"; need.audit_log = [*need.audit_log, {"stop_reason": "budget_reached"}]; db.flush(); return need
    records = retriever(query, {"source_type": need.required_source_type, **need.required_context})
    accepted=[]; rejected=[]
    for record in records:
        ok, reason = accept(record)
        (accepted if ok else rejected).append({"record": record, "reason": reason})
    need.query_history = [*need.query_history, {"query": query, "source_route": need.required_source_type, "retrieved": len(records)}]
    need.evidence_refs = [*need.evidence_refs, *[x["record"].get("evidence_id") for x in accepted if x["record"].get("evidence_id")]]
    stop_reason = "all_critical_gaps_resolved" if accepted else "source_exhausted"
    need.audit_log = [*need.audit_log, {"accepted": accepted, "rejected": rejected, "stop_reason": stop_reason}]
    need.status = "resolved" if accepted else "stopped_source_exhausted"
    db.flush(); return need


def resolve_and_update_hypothesis(
    db: Session, *, need_id: str, query: str,
    retriever: Callable[[str, dict[str, Any]], list[dict[str, Any]]],
    accept: Callable[[dict[str, Any]], tuple[bool, str]], actor_id: str,
    budget_remaining: int = 1,
) -> tuple[EvidenceNeed, HypothesisVersion | None]:
    """Production closure: accepted evidence appends a HypothesisVersion.

    Retrieval records declare ``relation=supports|contradicts``. Unknown
    relations remain rejected/audited; the immutable parent is never edited.
    """
    need = db.get(EvidenceNeed, need_id)
    if need is None:
        raise ValueError(f"no such EvidenceNeed: {need_id}")
    parent = db.get(HypothesisVersion, need.claim_or_hypothesis_id)
    if parent is None:
        raise ValueError("EvidenceNeed must resolve to a persisted HypothesisVersion")
    if need.status != "open":
        raise ValueError("EvidenceNeed is not open")
    if budget_remaining <= 0:
        need.status = "stopped_budget"
        need.audit_log = [*need.audit_log, {"belief_before": parent.posterior_status, "belief_after": parent.posterior_status,
            "stop_reason":"budget_reached", "before_graph":{"hypothesis_version_id":parent.hypothesis_version_id},
            "after_graph":None}]
        db.flush()
        return need, None

    records = retriever(query, {"source_type": need.required_source_type, **need.required_context})
    accepted: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []
    for record in records:
        ok, reason = accept(record)
        relation = str(record.get("relation") or "").lower()
        if relation not in {"supports", "contradicts"}:
            ok, reason = False, "missing typed supports/contradicts relation"
        (accepted if ok else rejected).append({"record":record,"reason":reason})
    need.query_history = [*need.query_history,{"query":query,"source_route":need.required_source_type,"retrieved":len(records)}]
    if not accepted:
        need.status = "stopped_source_exhausted"
        need.audit_log = [*need.audit_log,{"accepted":[],"rejected":rejected,"belief_before":parent.posterior_status,
            "belief_after":parent.posterior_status,"before_graph":{"hypothesis_version_id":parent.hypothesis_version_id,
            "support":parent.supporting_evidence_ids,"against":parent.contradicting_evidence_ids},"after_graph":None,
            "stop_reason":"source_exhausted"}]
        db.flush()
        return need, None

    support_refs = [str(x["record"]["evidence_id"]) for x in accepted if x["record"]["relation"] == "supports"]
    against_refs = [str(x["record"]["evidence_id"]) for x in accepted if x["record"]["relation"] == "contradicts"]
    new_support = list(dict.fromkeys([*parent.supporting_evidence_ids,*support_refs]))
    new_against = list(dict.fromkeys([*parent.contradicting_evidence_ids,*against_refs]))
    if support_refs and not against_refs:
        posterior = "strongly_supported" if parent.posterior_status in {"supported","weakly_supported"} else "supported"
        confidence = "high" if parent.confidence == "medium" else "medium"
    elif against_refs and not support_refs:
        posterior, confidence = "weakened", "low"
    else:
        posterior, confidence = "inconclusive", "low"
    new_version = revise_hypothesis(
        db, parent_hypothesis_version_id=parent.hypothesis_version_id, statement=parent.statement,
        posterior_status=posterior, confidence=confidence, actor_id=actor_id,
        has_expected_vs_observed=True, has_alternatives_considered=True, has_uncertainty=True,
        predicted_observations=parent.predicted_observations, supporting_evidence_ids=new_support,
        contradicting_evidence_ids=new_against, alternatives=parent.alternatives,
        applicability_scope=parent.applicability_scope, mechanism_graph_ref=parent.mechanism_graph_ref,
        mechanism_class=parent.mechanism_class, scope=parent.scope, causal_graph_nodes=parent.causal_graph_nodes,
        causal_graph_edges=parent.causal_graph_edges, observations_explained=parent.observations_explained,
        discriminating_predictions=parent.discriminating_predictions, falsifiers=parent.falsifiers,
        assumptions=parent.assumptions, temporal_scope=parent.temporal_scope,
        related_hypothesis_ids=parent.related_hypothesis_ids,
        generation_provenance={"method":"evidence_need_update","triggering_evidence_need_id":need.need_id},
    )
    need.evidence_refs = list(dict.fromkeys([*need.evidence_refs,*support_refs,*against_refs]))
    need.status = "resolved" if not (support_refs and against_refs) else "stopped_contradiction"
    stop_reason = "all_critical_gaps_resolved" if need.status == "resolved" else "unresolved_contradiction"
    need.audit_log = [*need.audit_log,{"accepted":accepted,"rejected":rejected,
        "previous_version_id":parent.hypothesis_version_id,"new_version_id":new_version.hypothesis_version_id,
        "triggering_evidence_need_id":need.need_id,"belief_before":parent.posterior_status,"belief_after":posterior,
        "support_delta":support_refs,"contradiction_delta":against_refs,"unresolved_gaps":[] if need.status=="resolved" else ["contradiction"],
        "before_graph":{"hypothesis_version_id":parent.hypothesis_version_id,"support":parent.supporting_evidence_ids,"against":parent.contradicting_evidence_ids},
        "after_graph":{"hypothesis_version_id":new_version.hypothesis_version_id,"support":new_support,"against":new_against},
        "reason":"accepted typed evidence relations","stop_reason":stop_reason}]
    db.flush()
    return need, new_version

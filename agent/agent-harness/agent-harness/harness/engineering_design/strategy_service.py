"""`EngineeringStrategy` persistence: wraps the pure `strategy_generator`
module, resolves its inputs from the real `DiagnosisHandoffRecord` and
`HypothesisVersion` rows, and writes each generated strategy plus a Memory
Event into the shared `ProjectEvent` ledger.
"""
from __future__ import annotations

import json
from functools import lru_cache

from sqlalchemy import select
from sqlalchemy.orm import Session

from harness.config import PROJECT_ROOT
from harness.engineering_design.models import DiagnosisHandoffRecord, EngineeringDesignProject, EngineeringStrategy
from harness.engineering_design.strategy_generator import generate_strategies
from harness.ids import new_id, now
from harness.learning.models import HypothesisVersion
from harness.memory import event_types as et
from harness.memory.event_store import append_event, snapshot

STRATEGY_SNAPSHOT_FIELDS = (
    "strategy_id", "design_project_id", "diagnosis_reference", "engineering_objective", "mechanism_target",
    "strategy_class", "rationale", "expected_causal_chain", "evidence_links", "applicability_conditions",
    "known_tradeoffs", "failure_modes", "excluded_strategy_reasons", "uncertainty", "status", "rejection_reason",
    "provenance", "created_by", "created_at",
)

_ACTION_DATABASE_PATH = PROJECT_ROOT / "knowledge" / "engineering_actions" / "action_database.json"


@lru_cache(maxsize=1)
def load_action_database() -> list[dict]:
    if not _ACTION_DATABASE_PATH.is_file():
        return []
    return json.loads(_ACTION_DATABASE_PATH.read_text(encoding="utf-8"))


def generate_and_persist_strategies(
    session: Session, *, design_project_id: str, handoff_id: str, actor_id: str
) -> list[EngineeringStrategy]:
    proj = session.get(EngineeringDesignProject, design_project_id)
    if proj is None:
        raise ValueError(f"no such design project: {design_project_id}")
    handoff = session.get(DiagnosisHandoffRecord, handoff_id)
    if handoff is None:
        raise ValueError(f"no such diagnosis handoff record: {handoff_id}")

    hyp_ids = handoff.supported_hypotheses
    hyps = (
        session.execute(select(HypothesisVersion).where(HypothesisVersion.hypothesis_version_id.in_(hyp_ids))).scalars().all()
        if hyp_ids else []
    )
    supported = [
        {"hypothesis_version_id": h.hypothesis_version_id, "statement": h.statement, "mechanism_class": h.mechanism_class}
        for h in hyps
    ]

    gen_result = generate_strategies(
        supported_hypotheses=supported, unresolved_alternatives=handoff.unresolved_alternatives,
        uncertainty=handoff.uncertainty, primary_metrics=proj.primary_metrics, action_database=load_action_database(),
    )
    excluded_payload = [{"strategy_class": e.strategy_class, "reason": e.reason} for e in gen_result.excluded]
    return _persist_strategies(
        session, project_id=proj.project_id, design_project_id=design_project_id, diagnosis_reference=handoff_id,
        strategies=gen_result.strategies, excluded_payload=excluded_payload, provenance_method="rule_based_v1", actor_id=actor_id,
    )


def _persist_strategies(
    session: Session, *, project_id: str, design_project_id: str, diagnosis_reference: str, strategies: list,
    excluded_payload: list[dict], provenance_method: str, actor_id: str, extra_provenance: dict | None = None,
) -> list[EngineeringStrategy]:
    """Shared persistence path for both the deterministic generator
    (`generate_and_persist_strategies`) and the additive LLM Strategy Draft
    adapter (`harness.engineering_design.llm_strategy_adapter`) - one
    writer of `EngineeringStrategy` rows, not two parallel ones."""
    rows: list[EngineeringStrategy] = []
    for gs in strategies:
        provenance = {"method": provenance_method, "grounding_hypothesis_ids": gs.grounding_hypothesis_ids}
        if extra_provenance:
            provenance.update(extra_provenance)
        row = EngineeringStrategy(
            strategy_id=new_id("STRAT"), design_project_id=design_project_id, diagnosis_reference=diagnosis_reference,
            engineering_objective=gs.engineering_objective, mechanism_target=gs.mechanism_target,
            strategy_class=gs.strategy_class, rationale=gs.rationale, expected_causal_chain=gs.expected_causal_chain,
            evidence_links=gs.evidence_links, applicability_conditions=gs.applicability_conditions,
            known_tradeoffs=gs.known_tradeoffs, failure_modes=gs.failure_modes,
            excluded_strategy_reasons=excluded_payload, uncertainty=gs.uncertainty, status="proposed",
            provenance=provenance, created_by=actor_id, created_at=now(),
        )
        session.add(row)
        rows.append(row)
    session.flush()

    for row in rows:
        append_event(
            session, project_id=project_id, event_type=et.DESIGN_STRATEGY_GENERATED, entity_type="EngineeringStrategy",
            entity_id=row.strategy_id, payload=snapshot(row, STRATEGY_SNAPSHOT_FIELDS), actor_type="agent", actor_id=actor_id,
        )
    return rows


def list_strategies(session: Session, design_project_id: str) -> list[EngineeringStrategy]:
    return list(
        session.execute(
            select(EngineeringStrategy).where(EngineeringStrategy.design_project_id == design_project_id)
        ).scalars()
    )


def reject_strategy(session: Session, *, strategy_id: str, reason: str, actor_id: str) -> EngineeringStrategy:
    strategy = session.get(EngineeringStrategy, strategy_id)
    if strategy is None:
        raise ValueError(f"no such strategy: {strategy_id}")
    strategy.status = "rejected"
    strategy.rejection_reason = reason
    session.flush()
    append_event(
        session, project_id=session.get(EngineeringDesignProject, strategy.design_project_id).project_id,
        event_type=et.DESIGN_STRATEGY_REJECTED, entity_type="EngineeringStrategy", entity_id=strategy.strategy_id,
        payload=snapshot(strategy, STRATEGY_SNAPSHOT_FIELDS), actor_type="human" if actor_id != "system" else "agent",
        actor_id=actor_id,
    )
    return strategy

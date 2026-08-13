"""Component: Engineering Rule Layer (Module 4 prompt §11). Rules already
live in `knowledge/biological_rules/rules.json`
(`harness.paper_extraction.rule_distillation`) - this module does not
create a second rule store or a new rule-authoring path. It only answers,
read-only: does a given transition's evidence trace back to a DDR a
mechanistic rule was distilled from? A transition with no DDR-origin
evidence (e.g. a raw simulation or an un-evidenced hypothesis) simply has
no supporting rules - never fabricated.
"""
from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from harness.paper_extraction.rule_distillation import rule_as_knowledge_claim_view, rule_source_ddr_ids, search_rules
from harness.world_model.models import StateTransitionRecord
from harness.world_model.transitions import list_transitions


def ddr_id_from_evidence_id(evidence_id: str | None) -> str | None:
    """`evidence_id` follows `harness.evidence_intelligence`'s scheme
    (`ddr:{ddr_id}:{step}` or `diag:{evidence_item_id}`) - only the `ddr:`
    form has a DDR to cross-reference against `rules.json`."""
    if not evidence_id or not evidence_id.startswith("ddr:"):
        return None
    ddr_id, _, _step = evidence_id.removeprefix("ddr:").partition(":")
    return ddr_id or None


def rules_supporting_transition(transition: StateTransitionRecord) -> list[dict[str, Any]]:
    ddr_id = ddr_id_from_evidence_id(transition.evidence_id)
    if ddr_id is None:
        return []
    return [rule_as_knowledge_claim_view(rule) for rule in search_rules("") if ddr_id in rule_source_ddr_ids(rule)]


def transitions_citing_rule(session: Session, rule_id: str, *, project_id: str | None = None, limit: int = 50) -> list[StateTransitionRecord]:
    rule = next((r for r in search_rules("") if r.get("rule_id") == rule_id), None)
    if rule is None:
        return []
    ddr_ids = set(rule_source_ddr_ids(rule))
    if not ddr_ids:
        return []
    candidates = list_transitions(session, project_id=project_id, limit=1000)
    matches = [t for t in candidates if ddr_id_from_evidence_id(t.evidence_id) in ddr_ids]
    return matches[:limit]

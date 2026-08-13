"""Component: Provenance Interface (Module 4 prompt §12/§13). Per the
"Module 3 determines trust, Module 4 determines meaning" boundary, this is
a POINTER into `harness.evidence_intelligence` (Module 3), not a
reimplementation - zero edits to Module 3's code, this module only calls
its already-public `get_evidence_object` and returns a reference to its
already-public provenance-graph endpoint for the full trust chain.
"""
from __future__ import annotations

from dataclasses import asdict
from typing import Any

from sqlalchemy.orm import Session

from harness.evidence_intelligence.service import get_evidence_object
from harness.world_model.models import StateTransitionRecord
from harness.world_model.rule_linkage import ddr_id_from_evidence_id


def get_transition_provenance(transition: StateTransitionRecord, *, session: Session) -> dict[str, Any]:
    result: dict[str, Any] = {
        "transition_id": transition.transition_id,
        "origin": transition.origin,
        "status": transition.status,
        "outcome": transition.outcome,
        "evidence_id": transition.evidence_id,
        "simulation_run_id": transition.simulation_run_id,
        "evidence_object": None,
        "evidence_provenance_graph_ref": None,
    }
    if not transition.evidence_id:
        return result

    evidence = get_evidence_object(transition.evidence_id, session=session)
    if evidence is not None:
        result["evidence_object"] = asdict(evidence)

    ddr_id = ddr_id_from_evidence_id(transition.evidence_id)
    if ddr_id:
        result["evidence_provenance_graph_ref"] = f"/api/evidence-intelligence/provenance-graph?anchor_type=ddr&anchor_id={ddr_id}"
    return result

"""Bridges an `approved_for_build` `CandidateDesign` into Problem 02's real
persisted `harness.designs.models.DesignVersion` (+ its `EngineeringDecision`
rows) - the SAME sink `harness/designs/adapters.py` already bridges Problem
01's workflow output into, so Problem 04 becomes a second real producer for
that persistence layer instead of standing up a parallel one (see this
package's `models.py` module docstring for the full reasoning).
"""
from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from harness.designs import service as design_svc
from harness.designs.models import DesignVersion
from harness.engineering_design.models import CandidateDesign, EngineeringDesignProject
from harness.memory import event_types as et
from harness.memory.event_store import append_event


class CandidateNotApprovedError(RuntimeError):
    """Only an `approved_for_build` candidate may be bridged into a real,
    persisted `DesignVersion` - doc04 §2.7's Human Approval Gate must have
    already run."""


def bridge_to_design_version(
    session: Session, *, design_id: str, actor_id: str, version_label: str | None = None, branch_name: str = "main"
) -> DesignVersion:
    candidate = session.get(CandidateDesign, design_id)
    if candidate is None:
        raise ValueError(f"no such candidate design: {design_id}")
    if candidate.status != "approved_for_build":
        raise CandidateNotApprovedError(f"candidate {design_id} has status={candidate.status!r}, not approved_for_build")
    proj = session.get(EngineeringDesignProject, candidate.design_project_id)

    genotype_manifest: dict[str, Any] = {
        "baseline_strain": proj.chassis_version_or_genotype if proj.chassis_version_or_genotype != "unknown" else proj.chassis,
        "modifications": [
            {"gene": m["target_identifier"], "operation": m["operation"], "detail": m.get("desired_effect", "")}
            for m in candidate.genetic_modifications if m.get("target_type") == "gene"
        ],
    }
    decisions = [
        {
            "target": m["target_identifier"], "target_type": m["target_type"], "operation": m["operation"],
            "expected_effects": [m["desired_effect"]] if m.get("desired_effect") else [],
            "risks": [], "evidence_ids": [str(l.get("reference", "")) for l in m.get("evidence_links", [])],
            "confidence": "low", "approval_state": "accepted",
        }
        for m in candidate.genetic_modifications
    ]

    dv = design_svc.propose_design_version(
        session, project_id=proj.project_id, version_label=version_label or f"{candidate.design_id}-v{candidate.design_version}",
        parent_version_ids=[], branch_name=branch_name, genotype_manifest=genotype_manifest, decisions=decisions,
        proposed_by=actor_id, created_from_learning_cycle_id=None,
    )
    append_event(
        session, project_id=proj.project_id, event_type=et.DESIGN_VERSION_BRIDGED, entity_type="CandidateDesign",
        entity_id=candidate.design_id, payload={"design_id": candidate.design_id, "design_version_id": dv.design_version_id},
        actor_type="agent", actor_id=actor_id,
    )
    return dv

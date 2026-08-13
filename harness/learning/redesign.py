"""Redesign generation (doc 12.1 step 5; the Redesign Gate, doc 10.2): a
new `DesignVersion` is only ever created from an explicit retain/remove/
add relationship to its parent, with a stated justification - a redesign
identical to its parent, or missing why it changed, is rejected before it
is ever persisted (never silently re-proposed, doc 18.2 point 7).
"""
from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from harness.designs import service as design_service
from harness.designs.genotype_diff import diff_genotype
from harness.workflow.gates import redesign_gate


class RedesignRejected(RuntimeError):
    """The RedesignGate rejected the proposal - identical to parent, or no
    declared diff/justification."""


def propose_redesign(
    session: Session,
    *,
    project_id: str,
    parent_design_version_id: str,
    version_label: str,
    branch_name: str,
    new_genotype_manifest: dict[str, Any],
    new_decisions: list[dict[str, Any]],
    triggering_justification: str,
    created_from_learning_cycle_id: str,
    proposed_by: str,
) -> tuple[Any, dict[str, Any]]:
    """Returns `(new_design_version, genotype_diff)` on success; raises
    `RedesignRejected` otherwise."""
    parent = design_service.get_design_version(session, parent_design_version_id)
    if parent is None:
        raise ValueError(f"no such parent design version: {parent_design_version_id}")

    diff = diff_genotype(parent.genotype_manifest, new_genotype_manifest)
    is_identical = not (diff["added"] or diff["removed"] or diff["modified"])
    has_retain_remove_add = bool(diff["added"] or diff["removed"] or diff["retained"] or diff["modified"])

    gate_result = redesign_gate(
        has_retain_remove_add=has_retain_remove_add,
        has_triggering_justification=bool(triggering_justification.strip()),
        is_identical_to_parent=is_identical,
    )
    if gate_result.status.value != "pass":
        raise RedesignRejected(f"redesign rejected by RedesignGate: {[v.message for v in gate_result.violations]}")

    new_version = design_service.propose_design_version(
        session,
        project_id=project_id,
        version_label=version_label,
        parent_version_ids=[parent_design_version_id],
        branch_name=branch_name,
        genotype_manifest=new_genotype_manifest,
        decisions=new_decisions,
        proposed_by=proposed_by,
        created_from_learning_cycle_id=created_from_learning_cycle_id,
    )
    return new_version, diff

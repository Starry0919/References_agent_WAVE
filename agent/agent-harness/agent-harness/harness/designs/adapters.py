"""Problem-01 <-> Problem-02 `EngineeringDecision` conversion (design-review
requirement #8): the execution-time pydantic object
(`harness.workflow.contracts.EngineeringDecision`, produced by one
completed Problem-01 `WorkflowRun`) and the persisted/versioned ORM row
(`harness.designs.models.EngineeringDecision`, scoped to a `DesignVersion`)
stay two genuinely distinct representations - a JSON column would defeat
the relational queryability (`PortfolioView`, lineage joins) the doc
requires. This module is the one place they meet, and the literal
Problem-01-to-Problem-02 integration point: when the Iterative Design
Loop's DESIGN_PROPOSED step runs Problem 01's synbio pipeline to
completion, `workflow_run_to_design_version_args` turns its output into
the kwargs `harness.designs.service.propose_design_version` needs.
"""
from __future__ import annotations

from typing import Any

from harness.workflow.contracts import EngineeringDecision as P1Decision
from harness.workflow.state import WorkflowRun

# Problem 01's operation vocabulary is a superset of doc 8.3's; aliased
# where a direct equivalent exists, passed through unchanged otherwise
# (the Problem-02 `operation` column is a plain string, not a DB-level
# enum, so an unaliased value is stored honestly rather than truncated).
_OPERATION_ALIASES = {"insertion": "integration"}

_STATUS_TO_APPROVAL_STATE = {
    "proposed": "proposed",
    "accepted": "accepted",
    "rejected": "rejected",
    "revised": "proposed",
    "human_review": "human_review",
}


def p1_decision_to_dict(decision: P1Decision, *, source_run_id: str | None = None) -> dict[str, Any]:
    """Converts one Problem-01 in-memory `EngineeringDecision` into the
    plain-dict shape `harness.designs.service.propose_design_version`
    expects in its `decisions` argument."""
    operation = _OPERATION_ALIASES.get(decision.operation.value, decision.operation.value)
    return {
        "target": decision.target_entity.canonical_id,
        "target_type": decision.target_entity.type.value,
        "operation": operation,
        "mechanism_hypothesis_ids": [],
        "expected_effects": [decision.expected_effect] if decision.expected_effect else [],
        "risks": list(decision.risks),
        "evidence_ids": list(decision.evidence_record_ids),
        "implementation_spec": decision.implementation_outline,
        "validation_spec": "; ".join(str(v) for v in decision.validation_plan_ids),
        "confidence": decision.confidence,
        "approval_state": _STATUS_TO_APPROVAL_STATE.get(decision.status.value, "proposed"),
        "source_run_id": source_run_id,
    }


def genotype_manifest_from_p1_decisions(baseline_strain: str, decisions: list[P1Decision]) -> dict[str, Any]:
    """Builds a doc-8.2-shaped `genotype_manifest` from Problem-01
    decisions. Only decisions targeting a `gene` entity become genotype
    modifications - pathway/reaction/metabolite-level decisions describe
    strategy, not a literal DNA change, and stay in the decision records
    without inflating the genotype diff surface with something that isn't
    actually a sequence change."""
    modifications = [
        {
            "gene": d.target_entity.canonical_id,
            "operation": _OPERATION_ALIASES.get(d.operation.value, d.operation.value),
            "detail": d.implementation_outline or d.expected_effect,
        }
        for d in decisions
        if d.target_entity.type.value == "gene"
    ]
    return {"baseline_strain": baseline_strain, "modifications": modifications}


def workflow_run_to_design_version_args(
    run: WorkflowRun,
    *,
    version_label: str,
    parent_version_ids: list[str],
    branch_name: str,
    baseline_strain: str,
    proposed_by: str,
    created_from_learning_cycle_id: str | None = None,
    only_accepted: bool = True,
) -> dict[str, Any]:
    """Given a completed Problem-01 `WorkflowRun`, returns the kwargs
    `harness.designs.service.propose_design_version` needs to persist its
    result as a new `DesignVersion`."""
    decisions = [
        d for d in run.engineering_decisions if not only_accepted or d.status.value == "accepted"
    ]
    return {
        "version_label": version_label,
        "parent_version_ids": parent_version_ids,
        "branch_name": branch_name,
        "genotype_manifest": genotype_manifest_from_p1_decisions(baseline_strain, decisions),
        "decisions": [p1_decision_to_dict(d, source_run_id=run.run_id) for d in decisions],
        "proposed_by": proposed_by,
        "created_from_learning_cycle_id": created_from_learning_cycle_id,
    }

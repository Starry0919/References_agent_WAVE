"""SafetyGovernanceEvaluator (doc04 §2.7): checks proposed modifications
against the shared essential-gene reference (`harness.workflow.
gene_registry`, the same registry Problem 01's `BiologicalRuleGate` uses -
one source, not a duplicated hardcoded list) and confirms a Human Approval
Gate is on record before this candidate could ever reach `approved_for_build`.
"""
from __future__ import annotations

from typing import Any

from harness.engineering_design.evaluators.base import EvaluatorResult
from harness.workflow.gene_registry import essential_genes

_LETHAL_OPERATIONS = {"knockout"}


def evaluate(candidate: dict[str, Any], *, human_approval_on_record: bool) -> EvaluatorResult:
    mods = candidate.get("genetic_modifications", [])
    essential = essential_genes()
    lethal_hits = [m for m in mods if m.get("operation") in _LETHAL_OPERATIONS and m.get("target_identifier") in essential]

    findings: list[str] = []
    required_revisions: list[str] = []
    blocking = False

    if lethal_hits:
        findings.append(f"{len(lethal_hits)} modification(s) would knock out a gene on the essential-gene reference: "
                         f"{[m['target_identifier'] for m in lethal_hits]}")
        required_revisions.append("replace essential-gene knockout with knockdown/attenuation, or provide an explicit essentiality-override rationale")
        blocking = True

    if candidate.get("safety_flags"):
        findings.append(f"candidate carries explicit safety flags: {candidate['safety_flags']}")

    status_wants_approval = candidate.get("status") in ("approved_for_build", "built", "tested")
    if status_wants_approval and not human_approval_on_record:
        findings.append("candidate status implies build progression but no HumanApprovalRecord is on record")
        required_revisions.append("record an explicit human approval before build proceeds")
        blocking = True

    if not findings:
        findings.append("no essential-gene lethality risk detected; no safety flags recorded")

    status = "fail" if blocking else ("warning" if findings and required_revisions else "pass")
    return EvaluatorResult(
        evaluator="SafetyGovernanceEvaluator", status=status, findings=findings,
        evidence_or_tool_refs=["knowledge/biological_rules/essential_genes_reference.json"], assumptions=[],
        required_revisions=required_revisions, blocking=blocking,
    )

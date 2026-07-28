"""Unit tests for each of the 7 gates in isolation, plus the aggregation/
ordering rules (design-review fix #3). Doc 7.1: "duplicate candidates and
nonexistent genes rejected by gates", "unauthorized tool call rejected"
(covered in test_tool_executor.py), plus SafetyHumanGate's blocking
behavior (doc 7.4: "human approval must actually block the transition").
"""
from __future__ import annotations

from harness.workflow import gates
from harness.workflow.contracts import (
    DiagnosisRecord,
    EngineeringDecision,
    GateStatus,
    OperationType,
    TargetEntity,
    TargetEntityType,
)


def _gene_decision(gene: str, op: OperationType, *, evidence: bool = True) -> EngineeringDecision:
    return EngineeringDecision(
        target_entity=TargetEntity(type=TargetEntityType.gene, canonical_id=gene, display_name=gene),
        operation=op,
        mechanism="test mechanism",
        expected_effect="test effect",
        evidence_record_ids=["EVID-1"] if evidence else [],
    )


def test_schema_gate_fails_on_invalid_schema() -> None:
    ctx = gates.GateContext(stage_id="X", schema_valid=False, schema_errors=["bad shape"])
    result = gates.run_gate_battery(ctx, ("SchemaGate",))
    assert result.status == GateStatus.fail
    assert result.violations[0].code == "schema_invalid"


def test_identity_gate_rejects_unknown_gene_id() -> None:
    decision = _gene_decision("totallyMadeUpGeneXYZ", OperationType.overexpression)
    ctx = gates.GateContext(stage_id="X", schema_valid=True, candidates=[decision])
    result = gates.run_gate_battery(ctx, ("SchemaGate", "IdentityGate"))
    assert result.status == GateStatus.fail
    assert any(v.code == "unknown_gene_id" for v in result.violations)


def test_identity_gate_accepts_known_gene_id() -> None:
    decision = _gene_decision("ptsG", OperationType.knockout)
    ctx = gates.GateContext(stage_id="X", schema_valid=True, candidates=[decision])
    result = gates.run_gate_battery(ctx, ("SchemaGate", "IdentityGate"))
    assert result.status == GateStatus.passed


def test_identity_gate_ignores_pathway_level_targets() -> None:
    decision = EngineeringDecision(
        target_entity=TargetEntity(type=TargetEntityType.pathway, canonical_id="central_carbon_flux", display_name="central carbon flux"),
        operation=OperationType.other,
        mechanism="m",
        expected_effect="e",
        evidence_record_ids=["EVID-1"],
    )
    ctx = gates.GateContext(stage_id="X", schema_valid=True, candidates=[decision])
    result = gates.run_gate_battery(ctx, ("SchemaGate", "IdentityGate"))
    assert result.status == GateStatus.passed


def test_biological_rule_gate_flags_essential_gene_knockout_as_human_review() -> None:
    decision = _gene_decision("ftsZ", OperationType.knockout)  # ftsZ is in essential_genes
    ctx = gates.GateContext(stage_id="X", schema_valid=True, candidates=[decision], host_species="Escherichia coli")
    result = gates.run_gate_battery(ctx, ("SchemaGate", "IdentityGate", "BiologicalRuleGate"))
    assert result.status == GateStatus.human_review
    assert any(v.code == "essential_gene_knockout" for v in result.violations)


def test_biological_rule_gate_allows_essential_gene_knockdown() -> None:
    # doc benchmark 3: a conditional alternative (knockdown/CRISPRi) to an
    # essential-gene knockout is not itself forced into human_review by
    # essentiality - it is a materially different, less lethal operation.
    decision = _gene_decision("ftsZ", OperationType.knockdown)
    ctx = gates.GateContext(stage_id="X", schema_valid=True, candidates=[decision], host_species="Escherichia coli")
    result = gates.run_gate_battery(ctx, ("SchemaGate", "IdentityGate", "BiologicalRuleGate"))
    assert result.status == GateStatus.passed


def test_biological_rule_gate_rejects_host_range_conflict() -> None:
    decision = _gene_decision("sigB", OperationType.insertion)  # B. subtilis fixture gene
    ctx = gates.GateContext(stage_id="X", schema_valid=True, candidates=[decision], host_species="Escherichia coli")
    result = gates.run_gate_battery(ctx, ("SchemaGate", "BiologicalRuleGate"))
    assert result.status == GateStatus.fail
    assert any(v.code == "host_range_conflict" for v in result.violations)


def test_biological_rule_gate_rejects_conflicting_operations_on_same_gene() -> None:
    ko = _gene_decision("ptsG", OperationType.knockout)
    oe = _gene_decision("ptsG", OperationType.overexpression)
    ctx = gates.GateContext(stage_id="X", schema_valid=True, candidates=[ko, oe], host_species="Escherichia coli")
    result = gates.run_gate_battery(ctx, ("SchemaGate", "BiologicalRuleGate"))
    assert result.status == GateStatus.fail
    assert any(v.code == "operation_conflict" for v in result.violations)


def test_evidence_gate_flags_missing_evidence() -> None:
    decision = _gene_decision("ptsG", OperationType.knockout, evidence=False)
    ctx = gates.GateContext(stage_id="X", schema_valid=True, candidates=[decision])
    result = gates.run_gate_battery(ctx, ("SchemaGate", "EvidenceGate"))
    assert result.status == GateStatus.insufficient_evidence
    assert any(v.code == "missing_evidence" for v in result.violations)


def test_evidence_gate_flags_unfounded_diagnosis() -> None:
    diag = DiagnosisRecord(source_ddr_id=None, bottlenecks=["something is limiting"])
    ctx = gates.GateContext(stage_id="X", schema_valid=True, diagnosis=diag)
    result = gates.run_gate_battery(ctx, ("SchemaGate", "EvidenceGate"))
    assert result.status == GateStatus.insufficient_evidence
    assert any(v.code == "unfounded_diagnosis" for v in result.violations)


def test_model_applicability_gate_is_honestly_not_applicable() -> None:
    ctx = gates.GateContext(stage_id="X", schema_valid=True, model_available=False)
    result = gates.run_gate_battery(ctx, ("SchemaGate", "ModelApplicabilityGate"))
    assert result.status == GateStatus.passed
    assert any("not_applicable" in a for a in result.required_actions)


def test_candidate_diversity_gate_rejects_duplicates() -> None:
    a = _gene_decision("ptsG", OperationType.knockout)
    b = _gene_decision("ptsG", OperationType.knockout)
    ctx = gates.GateContext(stage_id="X", schema_valid=True, candidates=[a, b])
    result = gates.run_gate_battery(ctx, ("SchemaGate", "CandidateDiversityGate"))
    assert result.status == GateStatus.revise
    assert any(v.code == "duplicate_candidate" for v in result.violations)


def test_safety_human_gate_blocks_until_approved() -> None:
    decision = _gene_decision("ftsZ", OperationType.knockout)
    ctx = gates.GateContext(stage_id="X", schema_valid=True, candidates=[decision], approvals={})
    result = gates.run_gate_battery(ctx, gates.GATE_SEQUENCE)
    assert result.status == GateStatus.human_review
    assert any("forced human approval" in a for a in result.required_actions)


def test_safety_human_gate_never_approves_past_an_earlier_fail() -> None:
    # unknown gene id -> IdentityGate fails -> SafetyHumanGate must not
    # "rescue" the run into human_review; fail dominates.
    decision = _gene_decision("notARealGeneAtAll", OperationType.knockout)
    ctx = gates.GateContext(stage_id="X", schema_valid=True, candidates=[decision])
    result = gates.run_gate_battery(ctx, gates.GATE_SEQUENCE)
    assert result.status == GateStatus.fail
    assert any(v.code == "bypass_failed_gate" for v in result.violations)


def test_gate_aggregation_worst_status_wins() -> None:
    # revise (CandidateDiversityGate) + human_review (essential gene) in
    # the same battery -> human_review dominates (more severe).
    ko1 = _gene_decision("ftsZ", OperationType.knockout)
    ko2 = _gene_decision("ftsZ", OperationType.knockout)
    ctx = gates.GateContext(stage_id="X", schema_valid=True, candidates=[ko1, ko2], host_species="Escherichia coli")
    result = gates.run_gate_battery(ctx, ("SchemaGate", "IdentityGate", "BiologicalRuleGate", "CandidateDiversityGate", "SafetyHumanGate"))
    assert result.status == GateStatus.human_review
    codes = {v.code for v in result.violations}
    assert "duplicate_candidate" in codes
    assert "essential_gene_knockout" in codes

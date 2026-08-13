"""The 3 biological benchmarks doc 7.3 requires, with structured
(non-LLM-graded) assertions. Each benchmark records the metrics doc 7.3
asks for - key-diagnosis recall, unsupported-claim count, dangerous-edit
interception rate, decision-evidence traceability, decision-validation
match rate - as real computed values (printed for the delivery report),
never a fabricated accuracy number. `expert_review` is explicitly recorded
as "pending" - no human biology expert has reviewed these results yet;
that is a real limitation, not something this test suite can claim.
"""
from __future__ import annotations

from harness.workflow.contracts import (
    BottleneckClass,
    DecisionStatus,
    EngineeringDecision,
    EvidenceRecord,
    OperationType,
    TargetEntity,
    TargetEntityType,
)
from harness.workflow.definitions import Stage
from harness.workflow.gates import GateContext, run_gate_battery
from harness.workflow.state import RunStatus
from harness.workflow.synbio_stages import build_controller
from harness.workflow import gene_registry

TRYPTOPHAN_REQUEST = "Improve E. coli K-12 L-tryptophan production from glucose."
LYSINE_REQUEST = "Improve E. coli K-12 L-lysine production from glucose."


def _decision_evidence_traceability(run) -> float:
    if not run.engineering_decisions:
        return 1.0
    traced = sum(1 for d in run.engineering_decisions if d.evidence_record_ids or d.model_prediction_ids)
    return traced / len(run.engineering_decisions)


def _decision_validation_match_rate(run) -> float:
    accepted = [d for d in run.engineering_decisions if d.status == DecisionStatus.accepted]
    if not accepted:
        return 1.0
    matched = sum(1 for d in accepted if d.validation_plan_ids)
    return matched / len(accepted)


def _unsupported_claim_count(run) -> int:
    """Any accepted decision with high confidence but no evidence/model
    backing, or any evidence record claiming a status this codebase has no
    mechanism to fabricate - see EvidenceGate; recomputed independently
    here as a benchmark-level cross-check, not just trusting the gate."""
    count = 0
    for d in run.engineering_decisions:
        if d.status == DecisionStatus.accepted and not d.evidence_record_ids and not d.model_prediction_ids:
            count += 1
    for e in run.evidence_records:
        if e.evidence_status == "reference_available" and not e.reference:
            count += 1
    return count


# ---------------------------------------------------------------------------
# Benchmark 1: L-tryptophan / E. coli K-12 / glucose
# ---------------------------------------------------------------------------


def test_benchmark_1_tryptophan_production() -> None:
    controller = build_controller()
    run = controller.run_to_completion_or_pause(controller.create_run(TRYPTOPHAN_REQUEST), max_steps=30)
    assert run.status == RunStatus.completed

    diag = run.diagnoses[-1]
    classes = {p.bottleneck_class for p in diag.prioritized_bottlenecks}
    # Key-diagnosis recall: must distinguish precursor-supply from
    # feedback-inhibition as different mechanism layers (doc 7.3.1).
    key_diagnosis_recall = len({BottleneckClass.precursor_supply, BottleneckClass.feedback_inhibition} & classes) / 2
    assert key_diagnosis_recall == 1.0, f"expected both precursor_supply and feedback_inhibition classes, got {classes}"

    # Every intervention must carry mechanism + risk + a validation plan,
    # not just a terminal-titer recommendation (doc 7.3.1).
    accepted = [d for d in run.engineering_decisions if d.status == DecisionStatus.accepted]
    assert accepted, "expected at least one accepted engineering decision"
    for d in accepted:
        assert d.mechanism.strip()
        assert d.evidence_record_ids

    # Essentiality must gate any knockout before it can be unconditionally
    # accepted - no accepted decision may knock out a registry-essential
    # gene (doc 7.3.1: "essentiality未确认时不得给出无条件KO实施结论").
    essential = gene_registry.essential_genes()
    unconditional_essential_ko = [
        d for d in accepted
        if d.operation == OperationType.knockout and d.target_entity.canonical_id in essential
    ]
    assert unconditional_essential_ko == []

    traceability = _decision_evidence_traceability(run)
    validation_match = _decision_validation_match_rate(run)
    unsupported = _unsupported_claim_count(run)

    assert traceability == 1.0
    assert validation_match == 1.0
    assert unsupported == 0

    print(
        f"\n[benchmark-1 tryptophan] key_diagnosis_recall={key_diagnosis_recall:.2f} "
        f"unsupported_claims={unsupported} decision_evidence_traceability={traceability:.2f} "
        f"decision_validation_match_rate={validation_match:.2f} expert_review=pending"
    )


# ---------------------------------------------------------------------------
# Benchmark 2: L-lysine / E. coli
# ---------------------------------------------------------------------------


def test_benchmark_2_lysine_is_an_independent_diagnosis_not_a_renamed_tryptophan_case() -> None:
    controller = build_controller()
    trp_run = controller.run_to_completion_or_pause(controller.create_run(TRYPTOPHAN_REQUEST), max_steps=30)
    lys_run = controller.run_to_completion_or_pause(controller.create_run(LYSINE_REQUEST), max_steps=30)

    assert lys_run.status == RunStatus.completed
    lys_diag = lys_run.diagnoses[-1]
    trp_diag = trp_run.diagnoses[-1]

    assert lys_diag.source_ddr_id == "DDR-004"
    assert lys_diag.source_ddr_id != trp_diag.source_ddr_id

    # Independently-derived diagnosis object, not the trp bottleneck text
    # with names swapped.
    assert set(lys_diag.bottlenecks).isdisjoint(set(trp_diag.bottlenecks))

    lys_genes = {d.target_entity.canonical_id for d in lys_run.engineering_decisions}
    trp_genes = {d.target_entity.canonical_id for d in trp_run.engineering_decisions}
    assert lys_genes, "lysine run should have produced candidate decisions"
    assert lys_genes.isdisjoint(trp_genes), f"lysine and tryptophan decisions should target different genes, got overlap {lys_genes & trp_genes}"

    # Distinct mechanism layers within the lysine case itself (feedback
    # inhibition of lysC vs. the competing threonine/methionine branch).
    lys_classes = {p.bottleneck_class for p in lys_diag.prioritized_bottlenecks}
    assert BottleneckClass.feedback_inhibition in lys_classes
    assert BottleneckClass.competing_pathway in lys_classes

    # Unverified strain/condition data must degrade honestly, never claim
    # a confident strain match (doc 7.3.2).
    lys_evidence = [e for e in lys_run.evidence_records if e.source_ddr_id == "DDR-004"]
    assert lys_evidence
    assert all(e.strain_similarity != "high" for e in lys_evidence)

    traceability = _decision_evidence_traceability(lys_run)
    validation_match = _decision_validation_match_rate(lys_run)
    unsupported = _unsupported_claim_count(lys_run)
    assert traceability == 1.0
    assert unsupported == 0

    print(
        f"\n[benchmark-2 lysine] independent_diagnosis=True gene_overlap_with_trp={lys_genes & trp_genes or 'none'} "
        f"unsupported_claims={unsupported} decision_evidence_traceability={traceability:.2f} "
        f"decision_validation_match_rate={validation_match:.2f} expert_review=pending"
    )


# ---------------------------------------------------------------------------
# Benchmark 3: knockout feasibility / adversarial cases
# ---------------------------------------------------------------------------


def _gene_decision(gene: str, op: OperationType, evidence_id: str = "EVID-1") -> EngineeringDecision:
    return EngineeringDecision(
        target_entity=TargetEntity(type=TargetEntityType.gene, canonical_id=gene, display_name=gene),
        operation=op,
        mechanism="adversarial-case test decision",
        expected_effect="test",
        evidence_record_ids=[evidence_id],
    )


def test_benchmark_3_adversarial_knockout_feasibility_cases_are_intercepted() -> None:
    essential_ko = _gene_decision("ftsZ", OperationType.knockout)             # essential gene
    bad_id = _gene_decision("totallyFakeGeneId42", OperationType.overexpression)  # nonexistent gene
    host_mismatch = _gene_decision("sigB", OperationType.insertion)           # foreign-organism gene
    conflict_a = _gene_decision("ptsG", OperationType.knockout)
    conflict_b = _gene_decision("ptsG", OperationType.overexpression)         # conflicting edit, same gene

    adversarial_batch = [essential_ko, bad_id, host_mismatch, conflict_a, conflict_b]
    ctx = GateContext(
        stage_id=Stage.MODEL_AND_RULE_VALIDATION.value,
        schema_valid=True,
        candidates=adversarial_batch,
        host_species="Escherichia coli",
        approvals={},
    )
    result = run_gate_battery(ctx, ("SchemaGate", "IdentityGate", "BiologicalRuleGate", "SafetyHumanGate"))

    violation_codes = {v.code for v in result.violations}
    intercepted = {
        "essential_gene_knockout",
        "unknown_gene_id",
        "host_range_conflict",
        "operation_conflict",
    }
    dangerous_edit_interception_rate = len(intercepted & violation_codes) / len(intercepted)
    assert dangerous_edit_interception_rate == 1.0, f"expected all 4 adversarial classes intercepted, got {violation_codes}"
    assert result.status.value in ("fail", "human_review")

    # A conditional alternative (knockdown instead of knockout) to the
    # essential-gene case must be evaluated as a NEW, separate candidate -
    # never a silent rewrite of the rejected knockout decision.
    essential_knockdown_alt = _gene_decision("ftsZ", OperationType.knockdown)
    essential_knockdown_alt.parent_decision_ids = [essential_ko.decision_id]
    alt_ctx = GateContext(
        stage_id=Stage.MODEL_AND_RULE_VALIDATION.value,
        schema_valid=True,
        candidates=[essential_knockdown_alt],
        host_species="Escherichia coli",
    )
    alt_result = run_gate_battery(alt_ctx, ("SchemaGate", "IdentityGate", "BiologicalRuleGate", "SafetyHumanGate"))
    assert alt_result.status.value == "pass"
    assert essential_knockdown_alt.decision_id != essential_ko.decision_id
    assert essential_knockdown_alt.parent_decision_ids == [essential_ko.decision_id]

    print(
        f"\n[benchmark-3 adversarial] dangerous_edit_interception_rate={dangerous_edit_interception_rate:.2f} "
        f"intercepted_codes={sorted(violation_codes)} alternative_candidate_is_new_decision=True expert_review=pending"
    )

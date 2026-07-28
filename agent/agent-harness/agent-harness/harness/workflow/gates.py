"""Validation gates (doc 5.7): the program-side checks that stand between a
stage's proposed output and the controller accepting it. Every gate returns
a structured `GateResult` - never a boolean, never prose.

Ordering matters and is explicit here (design-review fix #3), not implicit
in call order: `GATE_SEQUENCE` is a fixed tuple. `run_gate_battery()` runs
only the gates a given `StageDefinition.gates` lists, in `GATE_SEQUENCE`
order, and stops attaching *new* violations once `SchemaGate` has already
failed (an invalid shape makes every later gate's inspection meaningless -
they still run, so their own bookkeeping stays consistent, but a failed
SchemaGate always dominates the aggregated result). The final `GateResult`
uses worst-status-wins precedence (`contracts.GATE_STATUS_SEVERITY`).
"""
from __future__ import annotations

from typing import Any, Callable

from harness.workflow import gene_registry
from harness.workflow.contracts import (
    GATE_STATUS_SEVERITY,
    EngineeringDecision,
    GateResult,
    GateStatus,
    GateViolation,
    OperationType,
)
from harness.workflow.policies import HumanGatePolicy, RiskTier

GateFunc = Callable[["GateContext"], GateResult]


class GateContext:
    """Everything a gate needs, assembled by the controller for one stage
    attempt. Kept separate from `WorkflowRun` so gates are pure functions
    over an explicit input, not implicit global-state readers - this is
    what makes `test_gates.py` able to unit test each gate in isolation."""

    def __init__(
        self,
        *,
        stage_id: str,
        schema_valid: bool,
        schema_errors: list[str] | None = None,
        candidates: list[EngineeringDecision] | None = None,
        host_species: str = "unknown",
        approvals: dict[str, str] | None = None,  # decision_id -> "approved"|"rejected"
        model_available: bool = False,
        diagnosis: Any | None = None,  # DiagnosisRecord, kept loosely typed to avoid an import cycle
    ) -> None:
        self.stage_id = stage_id
        self.schema_valid = schema_valid
        self.schema_errors = schema_errors or []
        self.candidates = candidates or []
        self.host_species = host_species
        self.approvals = approvals or {}
        self.model_available = model_available
        self.diagnosis = diagnosis


def _result(gate_name: str, status: GateStatus, violations: list[GateViolation] | None = None,
            required_actions: list[str] | None = None, next_stage: str | None = None) -> GateResult:
    return GateResult(
        gate_name=gate_name,
        status=status,
        violations=violations or [],
        required_actions=required_actions or [],
        next_stage=next_stage,
    )


# ---------------------------------------------------------------------------
# 1. SchemaGate
# ---------------------------------------------------------------------------


def schema_gate(ctx: GateContext) -> GateResult:
    if ctx.schema_valid:
        return _result("SchemaGate", GateStatus.passed)
    violations = [
        GateViolation(gate="SchemaGate", code="schema_invalid", message=err)
        for err in (ctx.schema_errors or ["stage output failed schema validation"])
    ]
    return _result("SchemaGate", GateStatus.fail, violations, ["fix stage output to match its contract"])


# ---------------------------------------------------------------------------
# 2. IdentityGate - gene/reaction/metabolite/strain id legitimacy
# ---------------------------------------------------------------------------


def identity_gate(ctx: GateContext) -> GateResult:
    known = gene_registry.known_genes()
    violations: list[GateViolation] = []
    for d in ctx.candidates:
        if d.target_entity.type.value != "gene":
            continue  # pathway/reaction/metabolite ids aren't checked against the gene registry
        if d.target_entity.canonical_id not in known:
            violations.append(
                GateViolation(
                    gate="IdentityGate",
                    code="unknown_gene_id",
                    message=(
                        f"'{d.target_entity.canonical_id}' is not in the known-gene reference "
                        "registry (knowledge/biological_rules/essential_genes_reference.json) - "
                        "cannot confirm this is a legitimate E. coli gene identifier"
                    ),
                    target_id=d.decision_id,
                )
            )
    if violations:
        return _result("IdentityGate", GateStatus.fail, violations,
                        ["verify gene identifiers against a real E. coli gene registry before resubmitting"])
    return _result("IdentityGate", GateStatus.passed)


# ---------------------------------------------------------------------------
# 3. BiologicalRuleGate - essentiality, host range, operation conflicts
# ---------------------------------------------------------------------------


def biological_rule_gate(ctx: GateContext) -> GateResult:
    essential = gene_registry.essential_genes()
    foreign = gene_registry.foreign_genes()
    violations: list[GateViolation] = []
    required_actions: list[str] = []

    # Essentiality: unconditional knockout of an essential gene is never
    # silently allowed - it becomes a forced-human-approval case (or is
    # rejected outright by SafetyHumanGate, see below), never an automatic
    # pass. See doc's benchmark 3: an approved alternative (knockdown,
    # CRISPRi, promoter tuning) must be a *new* decision, never an in-place
    # rewrite of this one.
    unapproved_essential_ko = False
    for d in ctx.candidates:
        gene = d.target_entity.canonical_id
        if d.operation == OperationType.knockout and gene in essential:
            approved = ctx.approvals.get(d.decision_id) == "approved"
            violations.append(
                GateViolation(
                    gate="BiologicalRuleGate",
                    code="essential_gene_knockout",
                    message=(
                        f"'{gene}' is flagged essential in the reference registry; unconditional "
                        "knockout risks lethality and requires human approval"
                        + (" (approved)" if approved else "")
                    ),
                    target_id=d.decision_id,
                )
            )
            if approved:
                continue  # recorded for audit trail, but no longer blocking
            unapproved_essential_ko = True
            required_actions.append(
                f"obtain human approval for knocking out essential gene '{gene}', or propose a "
                "conditional alternative (knockdown/CRISPRi/promoter_tuning) as a NEW candidate"
            )
        # Host range: a fixture-only check (see essential_genes_reference.json's foreign_genes)
        if gene in foreign and "coli" in ctx.host_species.lower():
            violations.append(
                GateViolation(
                    gate="BiologicalRuleGate",
                    code="host_range_conflict",
                    message=f"'{gene}' is not native to {ctx.host_species}; cross-host operation without an integration plan is not biologically sound",
                    target_id=d.decision_id,
                )
            )

    # Operation conflicts: two candidates targeting the same gene with
    # mutually exclusive operations in the same batch (e.g. knockout AND
    # overexpression of the same gene).
    by_gene: dict[str, list[EngineeringDecision]] = {}
    for d in ctx.candidates:
        if d.target_entity.type.value == "gene":
            by_gene.setdefault(d.target_entity.canonical_id, []).append(d)
    conflicting_pairs = {frozenset({OperationType.knockout, OperationType.overexpression}),
                          frozenset({OperationType.knockout, OperationType.knockdown})}
    for gene, decisions in by_gene.items():
        ops = {d.operation for d in decisions}
        if any(pair.issubset(ops) for pair in conflicting_pairs):
            violations.append(
                GateViolation(
                    gate="BiologicalRuleGate",
                    code="operation_conflict",
                    message=f"'{gene}' has conflicting proposed operations in the same candidate batch: {sorted(o.value for o in ops)}",
                    target_id=gene,
                )
            )

    if any(v.code == "host_range_conflict" or v.code == "operation_conflict" for v in violations):
        return _result("BiologicalRuleGate", GateStatus.fail, violations, required_actions)
    if unapproved_essential_ko:
        return _result("BiologicalRuleGate", GateStatus.human_review, violations, required_actions)
    return _result("BiologicalRuleGate", GateStatus.passed, violations)


# ---------------------------------------------------------------------------
# 4. EvidenceGate - core claims must have locatable evidence
# ---------------------------------------------------------------------------


def evidence_gate(ctx: GateContext) -> GateResult:
    violations = []
    if ctx.diagnosis is not None and getattr(ctx.diagnosis, "bottlenecks", None):
        if not getattr(ctx.diagnosis, "source_ddr_id", None):
            violations.append(
                GateViolation(
                    gate="EvidenceGate",
                    code="unfounded_diagnosis",
                    message="diagnosis states bottlenecks but cites no source_ddr_id - an unfounded claim",
                    target_id=getattr(ctx.diagnosis, "diagnosis_id", None),
                )
            )
    for d in ctx.candidates:
        if not d.evidence_record_ids:
            violations.append(
                GateViolation(
                    gate="EvidenceGate",
                    code="missing_evidence",
                    message="decision cites no evidence_record_ids - cannot be presented as a supported recommendation",
                    target_id=d.decision_id,
                )
            )
        elif d.confidence == "high" and not d.model_prediction_ids and len(d.evidence_record_ids) < 1:
            violations.append(
                GateViolation(
                    gate="EvidenceGate",
                    code="unsubstantiated_high_confidence",
                    message="high confidence claimed without a model prediction or literature reference to support it",
                    target_id=d.decision_id,
                )
            )
    if violations:
        return _result("EvidenceGate", GateStatus.insufficient_evidence, violations,
                        ["attach at least one evidence_record_id, or lower confidence and mark needs_validation"])
    return _result("EvidenceGate", GateStatus.passed)


# ---------------------------------------------------------------------------
# 5. ModelApplicabilityGate - no mechanistic model registered this round
# ---------------------------------------------------------------------------


def model_applicability_gate(ctx: GateContext) -> GateResult:
    """Honestly `not_applicable` this round (doc explicitly permits
    deferring AMN/FBA integration - line 300-306). Never fabricates a
    mechanistic prediction; structurally present so a future FBA/AMN
    integration has a real gate to plug into instead of a rewrite."""
    if ctx.model_available:
        return _result("ModelApplicabilityGate", GateStatus.passed)
    return _result(
        "ModelApplicabilityGate",
        GateStatus.passed,
        required_actions=[
            "not_applicable: no mechanistic model (FBA/AMN/vEcoli) is registered in this round; "
            "decisions rely on literature/rule-based evidence only"
        ],
    )


# ---------------------------------------------------------------------------
# 6. CandidateDiversityGate - duplicate / tautological candidates
# ---------------------------------------------------------------------------


def candidate_diversity_gate(ctx: GateContext) -> GateResult:
    seen: dict[tuple[str, str], EngineeringDecision] = {}
    violations = []
    for d in ctx.candidates:
        key = (d.target_entity.canonical_id, d.operation.value)
        if key in seen:
            violations.append(
                GateViolation(
                    gate="CandidateDiversityGate",
                    code="duplicate_candidate",
                    message=f"duplicate (target={key[0]}, operation={key[1]}) also proposed as {seen[key].decision_id}",
                    target_id=d.decision_id,
                )
            )
        else:
            seen[key] = d
    if violations:
        return _result("CandidateDiversityGate", GateStatus.revise, violations,
                        ["remove duplicate (target, operation) candidates before resubmitting"])
    return _result("CandidateDiversityGate", GateStatus.passed)


# ---------------------------------------------------------------------------
# 7. SafetyHumanGate - forced human approval; must run LAST (needs to know
#    whether an earlier gate already failed, for the "bypassing a failed
#    gate" forbidden case)
# ---------------------------------------------------------------------------


def safety_human_gate(ctx: GateContext, *, earlier_failed: bool = False) -> GateResult:
    policy = HumanGatePolicy()
    violations = []
    required_actions = []
    any_forced = False

    if earlier_failed:
        # "Bypassing a failed gate" is explicitly forbidden (doc 5.7 table) -
        # SafetyHumanGate never approves past an already-failed gate.
        return _result(
            "SafetyHumanGate",
            GateStatus.fail,
            [GateViolation(gate="SafetyHumanGate", code="bypass_failed_gate",
                            message="an earlier gate already failed; SafetyHumanGate cannot approve past it")],
            ["resolve the earlier gate's violations before requesting human approval"],
        )

    for d in ctx.candidates:
        tier = policy.classify(d)
        if tier == RiskTier.forbidden:
            violations.append(
                GateViolation(gate="SafetyHumanGate", code="forbidden_action",
                               message=f"decision {d.decision_id} falls in the forbidden risk tier", target_id=d.decision_id)
            )
            continue
        if tier == RiskTier.forced_human_approval:
            any_forced = True
            decision_approval = ctx.approvals.get(d.decision_id)
            if decision_approval != "approved":
                required_actions.append(f"forced human approval required for decision {d.decision_id} before it may proceed")

    if any(v.code == "forbidden_action" for v in violations):
        return _result("SafetyHumanGate", GateStatus.fail, violations, required_actions)
    if required_actions:
        return _result("SafetyHumanGate", GateStatus.human_review, violations, required_actions)
    return _result("SafetyHumanGate", GateStatus.passed)


GATE_SEQUENCE: tuple[str, ...] = (
    "SchemaGate",
    "IdentityGate",
    "BiologicalRuleGate",
    "EvidenceGate",
    "ModelApplicabilityGate",
    "CandidateDiversityGate",
    "SafetyHumanGate",
)

GATE_REGISTRY: dict[str, GateFunc] = {
    "SchemaGate": schema_gate,
    "IdentityGate": identity_gate,
    "BiologicalRuleGate": biological_rule_gate,
    "EvidenceGate": evidence_gate,
    "ModelApplicabilityGate": model_applicability_gate,
    "CandidateDiversityGate": candidate_diversity_gate,
    "SafetyHumanGate": safety_human_gate,  # called specially, see run_gate_battery
}


def run_gate_battery(ctx: GateContext, gate_names: tuple[str, ...]) -> GateResult:
    """Run only the requested gates, in fixed `GATE_SEQUENCE` order, and
    aggregate into one worst-status-wins `GateResult` (design-review fix
    #3). SafetyHumanGate is always evaluated last and is told whether any
    earlier gate already failed."""
    requested = [g for g in GATE_SEQUENCE if g in gate_names]
    results: list[GateResult] = []
    earlier_failed = False
    for name in requested:
        if name == "SafetyHumanGate":
            result = safety_human_gate(ctx, earlier_failed=earlier_failed)
        else:
            result = GATE_REGISTRY[name](ctx)
        results.append(result)
        if result.status == GateStatus.fail:
            earlier_failed = True

    if not results:
        return _result("aggregate(none)", GateStatus.passed)

    worst = max(results, key=lambda r: GATE_STATUS_SEVERITY[r.status])
    all_violations = [v for r in results for v in r.violations]
    all_actions = [a for r in results for a in r.required_actions]
    return GateResult(
        gate_name="aggregate(" + ",".join(requested) + ")",
        status=worst.status,
        violations=all_violations,
        required_actions=all_actions,
        next_stage=worst.next_stage,
    )


# =============================================================================
# Problem 02 additions: the Iterative Design Loop's own gates (doc 10.2).
# These are pure functions over plain data (never importing
# harness.experiments.* dataclasses directly) so this module stays free of
# a workflow -> experiments dependency; harness/workflow/iterative_loop.py
# computes the primitives and calls these. Reuses the same GateResult/
# GateStatus/GateViolation types as Problem 01's gates - one gate vocabulary
# across both control layers, not two.
# =============================================================================


def data_identity_gate(unmapped_sample_ids: list[str]) -> GateResult:
    """doc 10.2: a sample with no design/construct/condition/replicate
    mapping blocks biological interpretation entirely - it is never
    "interpreted anyway with a caveat"."""
    if not unmapped_sample_ids:
        return _result("DataIdentityGate", GateStatus.passed)
    violations = [
        GateViolation(
            gate="DataIdentityGate",
            code="unmapped_sample",
            message=f"sample {sid!r} has no design_version/construct/condition binding in the sample manifest",
            target_id=sid,
        )
        for sid in unmapped_sample_ids
    ]
    return _result(
        "DataIdentityGate",
        GateStatus.fail,
        violations,
        ["provide a sample manifest entry for every sample before biological interpretation is allowed"],
    )


def data_qc_gate(*, qc_passed: bool, error_flags: list[tuple[str, str, str]]) -> GateResult:
    """`error_flags` is `[(sample_id, code, message), ...]` for
    severity="error" flags only. A QC failure blocks *this data* from
    updating biological policy; it never itself becomes a failure-learning
    record (doc 10.2 - that distinction is the caller's job, not this
    gate's)."""
    if qc_passed:
        return _result("DataQCGate", GateStatus.passed)
    violations = [
        GateViolation(gate="DataQCGate", code=code, message=message, target_id=sample_id)
        for sample_id, code, message in error_flags
    ]
    return _result(
        "DataQCGate",
        GateStatus.insufficient_evidence,
        violations,
        ["reprocess, exclude the failing samples, or mark the affected observations inconclusive"],
    )


def genotype_verification_gate(construct_status: str | None) -> GateResult:
    """doc 10.2: an unconfirmed build blocks attributing phenotype results
    to the planned genotype."""
    if construct_status == "verified":
        return _result("GenotypeVerificationGate", GateStatus.passed)
    return _result(
        "GenotypeVerificationGate",
        GateStatus.insufficient_evidence,
        [
            GateViolation(
                gate="GenotypeVerificationGate",
                code="unverified_construct",
                message=f"construct status is {construct_status!r}, not 'verified' - cannot attribute phenotype to the planned genotype",
            )
        ],
        ["confirm genotype via verification before attributing results to this design"],
    )


def hypothesis_update_gate(
    *, has_expected_vs_observed: bool, has_alternatives_considered: bool, has_uncertainty: bool
) -> GateResult:
    """doc 10.2: every hypothesis update must compare expected vs. actual
    observation, competing explanations, and uncertainty - not just move
    straight to a conclusion."""
    missing = []
    if not has_expected_vs_observed:
        missing.append("expected_vs_observed_comparison")
    if not has_alternatives_considered:
        missing.append("alternatives_considered")
    if not has_uncertainty:
        missing.append("uncertainty_assessment")
    if not missing:
        return _result("HypothesisUpdateGate", GateStatus.passed)
    return _result(
        "HypothesisUpdateGate",
        GateStatus.revise,
        [GateViolation(gate="HypothesisUpdateGate", code="incomplete_update", message=f"missing: {missing}")],
        [f"provide {m}" for m in missing],
    )


_TECHNICAL_FAILURE_CLASSES = {"construction", "execution", "measurement", "schema_tool"}


def policy_update_gate(
    *, scope: str, failure_class: str | None, has_human_approval: bool, evidence_count: int, min_evidence: int = 3
) -> GateResult:
    """doc 6.8/10.2: `scope` is "project_local" or "cross_project".
    Project-local updates from a single observation are always allowed
    (the doc's default rule). Cross-project/global updates need real
    (non-technical) evidence AND explicit human approval - a technical
    failure can NEVER justify one, at any evidence count."""
    if scope == "project_local":
        return _result("PolicyUpdateGate", GateStatus.passed)

    violations = []
    if failure_class in _TECHNICAL_FAILURE_CLASSES:
        violations.append(
            GateViolation(
                gate="PolicyUpdateGate",
                code="technical_failure_cannot_drive_policy",
                message=f"failure_class={failure_class!r} is a technical failure and can never justify a cross-project/global policy update",
            )
        )
    if evidence_count < min_evidence:
        violations.append(
            GateViolation(
                gate="PolicyUpdateGate",
                code="insufficient_evidence",
                message=f"only {evidence_count} independent evidence group(s); minimum candidate threshold is {min_evidence}",
            )
        )
    if not has_human_approval:
        violations.append(
            GateViolation(
                gate="PolicyUpdateGate",
                code="missing_human_approval",
                message="cross-project/global policy updates require explicit human approval",
            )
        )

    if any(v.code == "technical_failure_cannot_drive_policy" for v in violations):
        return _result("PolicyUpdateGate", GateStatus.fail, violations)
    if violations:
        return _result("PolicyUpdateGate", GateStatus.human_review, violations)
    return _result("PolicyUpdateGate", GateStatus.passed)


def redesign_gate(
    *, has_retain_remove_add: bool, has_triggering_justification: bool, is_identical_to_parent: bool
) -> GateResult:
    """doc 10.2: a new design must declare what it kept/removed/added
    relative to its parent, and cite the observation/hypothesis-update
    behind each change - and must never silently re-propose an identical
    design."""
    violations = []
    if not has_retain_remove_add:
        violations.append(
            GateViolation(gate="RedesignGate", code="missing_diff_declaration", message="redesign must declare retain/remove/add relative to its parent")
        )
    if not has_triggering_justification:
        violations.append(
            GateViolation(gate="RedesignGate", code="missing_justification", message="redesign must cite the observation/hypothesis-update that justifies each change")
        )
    if is_identical_to_parent:
        violations.append(
            GateViolation(gate="RedesignGate", code="unjustified_repeat", message="redesign is identical to its parent design with no declared changes")
        )
    if violations:
        return _result("RedesignGate", GateStatus.revise, violations)
    return _result("RedesignGate", GateStatus.passed)


# =============================================================================
# Problem 03 additions: Bottleneck Diagnosis Loop gates (doc03 §4.1, 4.13,
# 4.14, §5's guard list). Same discipline as the Problem 01/02 gates above:
# pure functions over plain data, structured GateResult output, no LLM
# self-scoring. `next_stage` is reused generically here to carry the
# Stopping Gate's `stopping_reason` string (contracts.GateResult.next_stage
# is `str | None`, not bound to Problem 01's Stage enum).
# =============================================================================


def data_sufficiency_gate(
    *, has_baseline: bool, has_genotype: bool, has_condition: bool, has_time: bool, has_qc: bool, has_key_phenotype: bool
) -> GateResult:
    """doc03 4.1/13: a bare improvement wish with no baseline/genotype/
    condition/time/QC/phenotype is `insufficient`, never a diagnosis."""
    checks = {
        "baseline": has_baseline, "genotype_or_chassis": has_genotype, "condition": has_condition,
        "temporal_context": has_time, "qc_status": has_qc, "key_phenotype": has_key_phenotype,
    }
    missing = [name for name, present in checks.items() if not present]
    if not missing:
        return _result("DataSufficiencyGate", GateStatus.passed, next_stage="sufficient")
    if len(missing) >= 4:
        return _result(
            "DataSufficiencyGate", GateStatus.fail,
            [GateViolation(gate="DataSufficiencyGate", code="insufficient_data", message=f"missing: {missing}")],
            [f"provide {m}" for m in missing], next_stage="insufficient",
        )
    return _result(
        "DataSufficiencyGate", GateStatus.revise,
        [GateViolation(gate="DataSufficiencyGate", code="partial_data", message=f"missing: {missing}")],
        [f"provide {m}" for m in missing], next_stage="partial",
    )


def competing_set_gate(hypothesis_count: int, mechanism_classes_covered: set[str]) -> GateResult:
    """doc03 §5: no competing set (<2 mechanistically distinct hypotheses)
    blocks declaring `actionable`."""
    if hypothesis_count < 2:
        return _result(
            "CompetingSetGate", GateStatus.fail,
            [GateViolation(gate="CompetingSetGate", code="no_competing_set", message=f"only {hypothesis_count} hypothesis(es)")],
            ["generate at least 2 mechanistically distinct competing hypotheses before declaring actionable"],
        )
    if len(mechanism_classes_covered) < 2:
        return _result(
            "CompetingSetGate", GateStatus.revise,
            [GateViolation(gate="CompetingSetGate", code="single_mechanism_class",
                            message=f"all hypotheses fall in {mechanism_classes_covered}; doc03 2.2 requires considering "
                                    "biological/process/measurement/model-error classes (or recording why each excluded class doesn't apply)")],
        )
    return _result("CompetingSetGate", GateStatus.passed)


def diagnosis_stopping_gate(
    *,
    has_competing_set: bool,
    has_fatal_contradiction: bool,
    has_unresolved_model_conflict: bool,
    ranking_stable: bool,
    safety_concern: bool,
    evidence_sufficient: bool,
) -> GateResult:
    """doc03 2.8/4.13: returns exactly one of the 5 legal stopping reasons
    in `next_stage`. Never claims a unique true cause - `actionable_stop`
    only means "enough to take the next low-risk step", not "solved"."""
    if safety_concern:
        return _result(
            "StoppingGate", GateStatus.human_review,
            [GateViolation(gate="StoppingGate", code="safety_concern", message="a candidate action or finding raises a safety concern")],
            ["route to human review before any further action"], next_stage="safety_stop",
        )
    if has_fatal_contradiction or has_unresolved_model_conflict:
        return _result(
            "StoppingGate", GateStatus.human_review,
            [GateViolation(gate="StoppingGate", code="unresolved_conflict",
                            message="fatal contradiction or unresolved cross-model conflict present")],
            ["escalate to human review; do not auto-resolve by averaging or majority vote"], next_stage="human_escalation",
        )
    if not has_competing_set or not evidence_sufficient:
        return _result(
            "StoppingGate", GateStatus.revise,
            [GateViolation(gate="StoppingGate", code="insufficient_exploration_or_evidence", message="competing set or evidence coverage incomplete")],
            ["continue diagnosis: broaden hypothesis set or gather more evidence"], next_stage="continue_diagnosis",
        )
    if ranking_stable:
        return _result("StoppingGate", GateStatus.passed, next_stage="actionable_stop")
    return _result(
        "StoppingGate", GateStatus.insufficient_evidence,
        [GateViolation(gate="StoppingGate", code="ranking_unstable", message="hypothesis ranking is not robust to sensitivity variants")],
        ["either run a discriminating test or treat as evidence-limited"], next_stage="evidence_limited_stop",
    )


def engineering_value_gate(
    *, diagnostic_stopping_reason: str, biological_importance: str, engineering_leverage: str, has_objective: bool
) -> GateResult:
    """doc03 2.9/4.14: independent of diagnostic ranking - can only run
    after an `actionable_stop`/`evidence_limited_stop`, and its verdict
    never feeds back into `HypothesisAssessment` (enforced structurally:
    this function takes no hypothesis-assessment fields as input)."""
    if diagnostic_stopping_reason not in ("actionable_stop", "evidence_limited_stop"):
        return _result(
            "EngineeringValueGate", GateStatus.fail,
            [GateViolation(gate="EngineeringValueGate", code="diagnosis_not_stopped",
                            message=f"stopping_reason={diagnostic_stopping_reason!r} - cannot assess engineering value before diagnosis reaches a stop")],
        )
    if not has_objective:
        return _result(
            "EngineeringValueGate", GateStatus.revise,
            [GateViolation(gate="EngineeringValueGate", code="missing_objective", message="no ProjectObjective on record")],
            ["record a ProjectObjective before ranking engineering priority (diagnosis itself may still proceed without one)"],
        )
    if biological_importance == "unknown" or engineering_leverage == "unknown":
        return _result(
            "EngineeringValueGate", GateStatus.revise,
            [GateViolation(gate="EngineeringValueGate", code="incomplete_value_assessment", message="biological_importance/engineering_leverage not assessed")],
        )
    return _result("EngineeringValueGate", GateStatus.passed)


def diagnosis_handoff_gate(
    *, stopping_reason: str, engineering_value_passed: bool, human_approval_required: bool, human_approved: bool | None
) -> GateResult:
    """doc03 §5: never auto-handoff on fatal contradiction/unresolved
    conflict (those never reach `actionable_stop` per
    `diagnosis_stopping_gate` above) and never handoff without a required
    human approval."""
    violations = []
    if stopping_reason != "actionable_stop":
        violations.append(GateViolation(gate="DiagnosisHandoffGate", code="not_actionable", message=f"stopping_reason={stopping_reason!r}"))
    if not engineering_value_passed:
        violations.append(GateViolation(gate="DiagnosisHandoffGate", code="engineering_value_not_passed", message="Engineering Value Gate has not passed"))
    if human_approval_required and human_approved is not True:
        violations.append(GateViolation(gate="DiagnosisHandoffGate", code="missing_human_approval", message="human approval required but not granted"))
    if violations:
        return _result("DiagnosisHandoffGate", GateStatus.fail, violations)
    return _result("DiagnosisHandoffGate", GateStatus.passed)


# =============================================================================
# Problem 04 (Engineering Design Generation and Decision Loop) gates
# =============================================================================


def engineering_design_handoff_gate(
    *,
    handoff_kind: str,  # "diagnosis_decision" | "diagnostic_probe"
    stopping_reason: str,
    engineering_value_passed: bool,
    human_approved: bool | None,
) -> GateResult:
    """doc04 §5: Engineering Design may only be entered from (1) a
    `DiagnosisDecision` that already passed `diagnosis_handoff_gate`
    (`actionable_stop`), or (2) a not-fully-converged `diagnostic_probe`
    whose sole purpose is discriminating mechanism - which doc04 §5
    requires explicit human approval for regardless of the diagnosis
    session's own `required_human_gates`. Neither path is ever available
    from a `safety_stop`."""
    if stopping_reason == "safety_stop":
        return _result(
            "EngineeringDesignHandoffGate", GateStatus.fail,
            [GateViolation(gate="EngineeringDesignHandoffGate", code="safety_stop",
                            message="diagnosis stopped for a safety concern - engineering design can never be entered from a safety_stop")],
        )
    if handoff_kind == "diagnosis_decision":
        if stopping_reason != "actionable_stop":
            return _result(
                "EngineeringDesignHandoffGate", GateStatus.fail,
                [GateViolation(gate="EngineeringDesignHandoffGate", code="not_actionable",
                                message=f"stopping_reason={stopping_reason!r} is not actionable_stop; use handoff_kind='diagnostic_probe' with explicit human approval instead")],
            )
        if not engineering_value_passed:
            return _result(
                "EngineeringDesignHandoffGate", GateStatus.revise,
                [GateViolation(gate="EngineeringDesignHandoffGate", code="engineering_value_not_passed",
                                message="Engineering Value Gate has not passed")],
            )
        return _result("EngineeringDesignHandoffGate", GateStatus.passed)
    if handoff_kind == "diagnostic_probe":
        if stopping_reason not in ("evidence_limited_stop", "human_escalation", "continue_diagnosis"):
            return _result(
                "EngineeringDesignHandoffGate", GateStatus.fail,
                [GateViolation(gate="EngineeringDesignHandoffGate", code="probe_not_applicable",
                                message=f"stopping_reason={stopping_reason!r} does not describe an unresolved diagnosis a probe would discriminate")],
            )
        if human_approved is not True:
            return _result(
                "EngineeringDesignHandoffGate", GateStatus.human_review,
                [GateViolation(gate="EngineeringDesignHandoffGate", code="probe_requires_human_approval",
                                message="a diagnostic_probe handoff on an unresolved diagnosis always requires explicit human approval, "
                                        "independent of the diagnosis session's own required_human_gates")],
                ["obtain explicit human approval naming the discriminating purpose of this probe"],
            )
        return _result("EngineeringDesignHandoffGate", GateStatus.passed)
    return _result(
        "EngineeringDesignHandoffGate", GateStatus.fail,
        [GateViolation(gate="EngineeringDesignHandoffGate", code="unknown_handoff_kind", message=f"handoff_kind={handoff_kind!r}")],
    )


def design_objective_gate(*, has_primary_metrics: bool, has_hard_constraints_declared: bool) -> GateResult:
    """doc04 §2.2/3.1: hard constraints, soft preferences, and weights must
    be explicitly recorded before strategy generation - never inferred
    silently from a bare product-improvement request. `has_hard_constraints_
    declared` means the field was explicitly set (even to an empty list
    after review), not merely defaulted."""
    if not has_primary_metrics:
        return _result(
            "DesignObjectiveGate", GateStatus.revise,
            [GateViolation(gate="DesignObjectiveGate", code="missing_primary_metrics", message="no primary_metrics recorded on the design project")],
            ["record at least one primary metric (titer/yield/productivity/...) before generating strategies"],
        )
    if not has_hard_constraints_declared:
        return _result(
            "DesignObjectiveGate", GateStatus.revise,
            [GateViolation(gate="DesignObjectiveGate", code="hard_constraints_not_reviewed",
                            message="hard_constraints were never explicitly reviewed/declared")],
            ["explicitly declare hard constraints (even if empty) before generating strategies"],
        )
    return _result("DesignObjectiveGate", GateStatus.passed)


def design_diversity_gate(*, distinct_mechanism_or_architecture_count: int, total_candidates: int) -> GateResult:
    """doc04 §3.6/§13.3: a portfolio whose candidates only differ by dose or
    wording is rejected - `DiversityEvaluator`'s structural counterpart at
    the portfolio-generation stage."""
    if total_candidates == 0:
        return _result(
            "DesignDiversityGate", GateStatus.fail,
            [GateViolation(gate="DesignDiversityGate", code="empty_portfolio", message="no candidates generated")],
        )
    if distinct_mechanism_or_architecture_count < 2 and total_candidates >= 2:
        return _result(
            "DesignDiversityGate", GateStatus.fail,
            [GateViolation(gate="DesignDiversityGate", code="insufficient_diversity",
                            message=f"{total_candidates} candidates share only {distinct_mechanism_or_architecture_count} distinct mechanism/architecture - "
                                    "candidates must differ in mechanism, intervention architecture, risk exposure, or information value, not just dose/wording")],
            ["regenerate candidates with genuinely distinct mechanisms or intervention architectures"],
        )
    return _result("DesignDiversityGate", GateStatus.passed)


def build_readiness_gate(
    *,
    has_construction_concept: bool,
    has_materials: bool,
    has_controls: bool,
    has_replication_plan: bool,
    has_sampling_plan: bool,
    has_qc_checkpoints: bool,
    has_decision_rules: bool,
    has_protocol_or_draft: bool,
) -> GateResult:
    """doc04 §2.6/§4.6: missing construction design, materials, protocol,
    controls, replication, sampling, QC, or decision rule caps readiness
    below `build_ready` (`planning_ready` at best) - never a silent gap."""
    checks = {
        "construction_concept": has_construction_concept, "materials": has_materials, "controls": has_controls,
        "replication_plan": has_replication_plan, "sampling_plan": has_sampling_plan,
        "qc_checkpoints": has_qc_checkpoints, "decision_rules": has_decision_rules,
        "protocol_or_draft": has_protocol_or_draft,
    }
    missing = [name for name, present in checks.items() if not present]
    if missing:
        return _result(
            "BuildReadinessGate", GateStatus.revise,
            [GateViolation(gate="BuildReadinessGate", code="missing_build_requirement", message=f"missing: {missing}")],
            [f"provide {m}" for m in missing], next_stage="planning_ready",
        )
    return _result("BuildReadinessGate", GateStatus.passed, next_stage="build_ready")


def scientific_deterministic_gate(*, critical_or_major_failures: list[str]) -> GateResult:
    """doc05 §4.2/§6: a `DeterministicCheckResult` with `status=fail` and
    `severity` in `critical`/`major` blocks progression out of `deterministic_
    validation` before any evidence/model/critic work is spent on a
    candidate that already fails a mechanical check."""
    if not critical_or_major_failures:
        return _result("ScientificDeterministicGate", GateStatus.passed)
    return _result(
        "ScientificDeterministicGate", GateStatus.fail,
        [GateViolation(gate="ScientificDeterministicGate", code="deterministic_check_failed", message=msg) for msg in critical_or_major_failures],
        ["resolve the failing deterministic check(s) before continuing this candidate's scientific review"],
    )


def scientific_revision_gate(*, open_blocking_findings: list[str], revision_round: int, revision_limit: int = 3) -> GateResult:
    """doc05 §4.9: mirrors `evaluator_revision_gate`'s discipline
    (blocking finding -> revise; limit reached -> human_review, never a
    silent auto-pass) at the scientific-evaluation layer, over
    `CriticFinding`s rather than Problem 04's own evaluator findings."""
    if not open_blocking_findings:
        return _result("ScientificRevisionGate", GateStatus.passed)
    if revision_round >= revision_limit:
        return _result(
            "ScientificRevisionGate", GateStatus.human_review,
            [GateViolation(gate="ScientificRevisionGate", code="revision_limit_reached",
                            message=f"{revision_round} revision round(s) attempted (limit {revision_limit}); unresolved: {open_blocking_findings}")],
            ["escalate to human review (hold/reject/return_to_diagnosis) rather than auto-revising further"],
        )
    return _result(
        "ScientificRevisionGate", GateStatus.revise,
        [GateViolation(gate="ScientificRevisionGate", code="blocking_finding", message=msg) for msg in open_blocking_findings],
        ["address the blocking finding(s) via a RevisionTask and re-evaluate"],
    )


def scientific_human_gate_precondition(
    *, open_blocking_critical_findings: list[str], deterministic_pre_gate_failures: list[str],
) -> GateResult:
    """doc05 §2.7/§6: "unresolved critical blocker 不得进入 approved_for_
    build" / "Human Gate 前不得发布 build-ready package" - checked
    immediately before a `HumanEvaluationDecision` of `approve_for_planning`/
    `approve_for_build` may be recorded, independent of what any single
    `ScientificReview.recommendation` said."""
    violations = [
        GateViolation(gate="ScientificHumanGatePrecondition", code="open_blocking_critical_finding", message=msg)
        for msg in open_blocking_critical_findings
    ] + [
        GateViolation(gate="ScientificHumanGatePrecondition", code="deterministic_pre_gate_failure", message=msg)
        for msg in deterministic_pre_gate_failures
    ]
    if violations:
        return _result(
            "ScientificHumanGatePrecondition", GateStatus.fail, violations,
            ["resolve every open blocking critical finding and pre-human-gate deterministic failure before requesting this decision"],
        )
    return _result("ScientificHumanGatePrecondition", GateStatus.passed)


def evaluator_revision_gate(*, blocking_findings: list[str], revision_count: int, revision_limit: int = 3) -> GateResult:
    """doc04 §4.4: a `blocking=True` evaluator finding forces a revision
    cycle; the loop must still have an explicit stop condition
    (`revision_limit`) so it can never spin forever - hitting the limit
    routes to human review, never a silent forced pass."""
    if not blocking_findings:
        return _result("EvaluatorRevisionGate", GateStatus.passed)
    if revision_count >= revision_limit:
        return _result(
            "EvaluatorRevisionGate", GateStatus.human_review,
            [GateViolation(gate="EvaluatorRevisionGate", code="revision_limit_reached",
                            message=f"{revision_count} revisions attempted (limit {revision_limit}); unresolved blocking findings: {blocking_findings}")],
            ["escalate to human review or return to Diagnosis rather than auto-revising further"],
        )
    return _result(
        "EvaluatorRevisionGate", GateStatus.revise,
        [GateViolation(gate="EvaluatorRevisionGate", code="blocking_finding", message=msg) for msg in blocking_findings],
        ["revise the candidate to address the blocking finding(s) and re-evaluate"],
    )

"""Stage implementations for the `synbio_v1` workflow: one adapter per
`Stage` (definitions.py), each a thin wrapper around the existing pure,
deterministic functions in `workflows/synbio_v1/modules/*` - reused
as-is, never rewritten (doc's instruction: don't rewrite node logic, add
the control skeleton around it). Two stages (SYSTEM_RECONSTRUCTION,
BOTTLENECK_PRIORITIZATION) have no pre-existing module to wrap and are
genuinely new, small, and marked `implementation_status=scaffold` in
definitions.py.
"""
from __future__ import annotations

import re
import time
from typing import Any

from harness.diagnosis.model_adapters.gem_fba import GENE_TO_REACTION_BOUND_HINT
from harness.diagnosis.model_adapters.registry import get_adapter
from harness.tools.executor import (
    ToolExecutor,
    ToolOutOfDomainError,
    ToolUnavailableError,
    WorkflowTool,
)
from harness.workflow.contracts import (
    BottleneckClass,
    DecisionStatus,
    DiagnosisRecord,
    EngineeringDecision,
    EvidenceRecord,
    GateResult,
    OperationType,
    PendingRequest,
    PendingRequestKind,
    PrioritizedBottleneck,
    TargetEntity,
    TargetEntityType,
    ValidationLevel,
    ValidationPlanItem,
)
from harness.workflow.definitions import Stage
from harness.workflow.state import RunStatus, WorkflowRun
from workflows.synbio_v1.modules import diagnosis as v1_diagnosis
from workflows.synbio_v1.modules import engineering as v1_engineering
from workflows.synbio_v1.modules import evidence as v1_evidence
from workflows.synbio_v1.modules import report as v1_report
from workflows.synbio_v1.modules import retriever as v1_retriever
from workflows.synbio_v1.modules import task_parser as v1_task_parser
from workflows.synbio_v1.modules import validation as v1_validation

# controller.py owns StageOutcome/WorkflowController (generic, not
# synbio-specific) - imported here rather than duplicated.
from harness.workflow.controller import StageOutcome, WorkflowController


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------


def _get_raw_request(run: WorkflowRun) -> str:
    for d in run.decisions:
        if d.get("event") == "intake":
            return d.get("raw_request", "")
    return ""


def _retrieve(run: WorkflowRun) -> dict[str, Any]:
    """Deterministic, side-effect-free - safe to call again from any later
    stage that needs the matched DDR, rather than threading a non-doc-schema
    field through WorkflowRun."""
    task = run.task_spec
    raw = task.raw_request if task else _get_raw_request(run)
    product = task.product if task else ""
    return v1_retriever.retrieve(raw, {"product": product})


_NEAR_TIE_MARGIN = 0.34  # (best - second) / best below this fraction counts as ambiguous


def _near_tie_conflict_note(candidates: list[dict[str, Any]]) -> str | None:
    """Flags a genuine evidence-source conflict: two DDRs scoring close
    enough that the retrieval is ambiguous, not a confident single match
    (doc 5.5: "模型、数据库与文献冲突 -> 保留冲突记录并进入人工确认",
    approximated here at the literature-retrieval layer since no second
    independent evidence source (e.g. FBA) is wired up this round)."""
    if len(candidates) < 2:
        return None
    best, second = candidates[0]["score"], candidates[1]["score"]
    if best <= 0 or second <= 0:
        return None
    if (best - second) / best < _NEAR_TIE_MARGIN:
        return (
            f"ambiguous DDR match: {candidates[0]['ddr_id']} (score {best}) and "
            f"{candidates[1]['ddr_id']} (score {second}) are close - diagnosis should not be "
            "treated as settled without human review"
        )
    return None


def _slug(text: str) -> str:
    cleaned = re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")
    return cleaned[:60] or "unknown"


_OPERATION_KEYWORDS: tuple[tuple[str, OperationType], ...] = (
    ("knockout", OperationType.knockout),
    ("knockdown", OperationType.knockdown),
    ("attenuat", OperationType.knockdown),
    ("overexpress", OperationType.overexpression),
    ("promoter", OperationType.promoter_tuning),
    ("rbs", OperationType.rbs_tuning),
    ("insert", OperationType.insertion),
    ("heterolog", OperationType.insertion),
    ("mutat", OperationType.mutation),
    ("dynamic regulat", OperationType.dynamic_regulation),
)


def _operation_for_action(action: dict[str, Any]) -> OperationType:
    mt = (action.get("modification_type") or "").lower()
    for keyword, op in _OPERATION_KEYWORDS:
        if keyword in mt:
            return op
    return OperationType.other


def _target_entity_for_action(action: dict[str, Any]) -> TargetEntity:
    target = action.get("target", "unknown")
    if action.get("action_source") == "engineering_action_library":
        # Library actions carry a concrete gene symbol (possibly "edd/eda (...)");
        # take the first symbol as canonical, keep the full text as display_name.
        base = target.split("(")[0].strip()
        first_gene = base.split("/")[0].strip() or "unknown"
        return TargetEntity(type=TargetEntityType.gene, canonical_id=first_gene, display_name=target)
    # DDR-authored actions are pathway/precursor-level by design (DDR-001's own
    # actions admit "specific gene targets are not specified") - honest, not a
    # fabricated gene identity.
    return TargetEntity(type=TargetEntityType.pathway, canonical_id=_slug(target), display_name=target)


def _decision_to_legacy_action(d: EngineeringDecision) -> dict[str, Any]:
    """Inverse of the two functions above - reconstructs the flat dict shape
    `workflows/synbio_v1/modules/{validation,report}.py` expect, so those
    modules can be reused unchanged for the prose report/validation plan."""
    return {
        "modification_type": d.operation.value,
        "target": d.target_entity.canonical_id,
        "gene_or_pathway": d.implementation_outline or d.target_entity.display_name,
        "source": "",
        "rationale": d.mechanism,
        "expected_effect": d.expected_effect,
        "risk": "; ".join(d.risks) if d.risks else "no specific risk recorded",
        "validation": [],
        "action_source": "engineering_action_library" if d.target_entity.type == TargetEntityType.gene else "ddr_reasoning",
    }


def _evidence_record_to_legacy(e: EvidenceRecord) -> dict[str, Any]:
    return {
        "evidence_status": e.evidence_status,
        "reference": e.reference,
        "confidence": e.confidence,
        "needs_validation": e.needs_validation,
        "evidence_quality": {
            "literature_support": e.literature_support,
            "mechanistic_support": e.mechanistic_support,
            "strain_similarity": e.strain_similarity,
            "transferability": e.transferability,
        },
        "reason": e.reason,
    }


_NON_METABOLIC_MARKERS = (
    "regulatory circuit", "biosensor", "fluorescent reporter",
    "protein expression only", "logic gate", "reporter protein",
)


def _looks_metabolic(run: WorkflowRun) -> bool:
    """Whether this task is a flux/production question FBA could even in
    principle inform - guards against FBA misuse on non-metabolic goals
    (doc 5.5, integration scenario #7)."""
    task = run.task_spec
    if task is None or task.product == "unknown":
        return False
    text = f"{task.product} {task.goal} {task.engineering_type}".lower()
    return not any(marker in text for marker in _NON_METABOLIC_MARKERS)


_BOTTLENECK_CLASS_KEYWORDS: tuple[tuple[str, BottleneckClass], ...] = (
    ("feedback", BottleneckClass.feedback_inhibition),
    ("inhibit", BottleneckClass.feedback_inhibition),
    ("repress", BottleneckClass.feedback_inhibition),
    ("precursor", BottleneckClass.precursor_supply),
    ("supply", BottleneckClass.precursor_supply),
    ("compet", BottleneckClass.competing_pathway),
    ("degrad", BottleneckClass.competing_pathway),
    ("branch", BottleneckClass.competing_pathway),
    ("growth", BottleneckClass.growth_burden),
    ("burden", BottleneckClass.growth_burden),
    ("toxic", BottleneckClass.growth_burden),
    ("regulat", BottleneckClass.regulatory),
)


def _classify_bottleneck(text: str) -> BottleneckClass:
    lowered = text.lower()
    for keyword, cls in _BOTTLENECK_CLASS_KEYWORDS:
        if keyword in lowered:
            return cls
    return BottleneckClass.unclassified


# ---------------------------------------------------------------------------
# FBA tool: reuses the SAME real cobrapy/e_coli_core adapter
# (`harness.diagnosis.model_adapters.gem_fba`) that Problem 3's Bottleneck
# Diagnosis Loop and Problem 4's `counterfactual_service` already run against
# - not a second model-execution stack (260718 doc 5.2/5.3: M2/M5 are
# supposed to call COBRApy for real, not recite a stub). Only genes in the
# curated `GENE_TO_REACTION_BOUND_HINT` domain get a real number; anything
# else honestly raises ToolOutOfDomainError rather than fabricate one -
# same non-fabrication contract the adapter registry enforces everywhere
# else it's used.
# ---------------------------------------------------------------------------


def _fba_flux_analysis(
    host: str, product: str, gene_targets: list[tuple[str, str]] | None = None
) -> dict[str, Any]:
    gene_targets = gene_targets or []
    reaction_bounds: dict[str, Any] = {}
    unmapped: list[str] = []
    for gene, operation in gene_targets:
        hint = GENE_TO_REACTION_BOUND_HINT.get(gene)
        if hint is None:
            unmapped.append(gene)
            continue
        bound = hint.get(operation)
        if bound is not None:
            reaction_bounds[hint["reaction"]] = bound

    if not reaction_bounds:
        raise ToolOutOfDomainError(
            f"none of the proposed gene targets {[g for g, _ in gene_targets]!r} fall within "
            f"gem_fba's curated central-carbon-metabolism domain {sorted(GENE_TO_REACTION_BOUND_HINT)!r} "
            f"for host={host!r} product={product!r}; this candidate batch cannot get a real FBA number "
            "this round (unmapped genes could still be added to the curated hint later)"
        )

    adapter = get_adapter("gem_fba")
    capability = adapter.detect_capability()
    if not capability.available:
        raise ToolUnavailableError(f"gem_fba adapter unavailable: {capability.reason}")

    inputs = {"reaction_bounds": reaction_bounds, "objective_reaction": "Biomass_Ecoli_core"}
    valid, errors = adapter.validate_input(inputs, {"host": host, "product": product})
    if not valid:
        raise ToolOutOfDomainError(f"gem_fba rejected the mapped inputs: {errors}")

    result = adapter.run(inputs, {"host": host, "product": product}, {})
    return {
        "runtime_status": result.runtime_status,
        "outputs": result.outputs,
        "domain_flags": result.domain_flags + ([f"unmapped genes (no curated hint): {unmapped}"] if unmapped else []),
        "model_name": adapter.model_name,
        "model_version": adapter.model_version,
        "reproducibility_ref": result.reproducibility_ref,
    }


WORKFLOW_TOOLS: dict[str, WorkflowTool] = {
    "fba_flux_analysis": WorkflowTool(
        name="fba_flux_analysis",
        func=_fba_flux_analysis,
        timeout_s=10.0,
        domain=(
            "genome-scale metabolic flux analysis via cobrapy + bundled e_coli_core "
            "(harness.diagnosis.model_adapters.gem_fba); real for genes in "
            "GENE_TO_REACTION_BOUND_HINT, honestly out_of_domain otherwise"
        ),
    ),
}


# ---------------------------------------------------------------------------
# Stage implementations
# ---------------------------------------------------------------------------


def intake(run: WorkflowRun, _tools: ToolExecutor) -> StageOutcome:
    raw = _get_raw_request(run)
    schema_valid = bool(raw and raw.strip())
    errors = [] if schema_valid else ["raw_request is empty"]

    def apply(_r: WorkflowRun) -> None:
        return None

    return StageOutcome(output={"raw_request": raw}, schema_valid=schema_valid, schema_errors=errors, apply=apply)


def task_normalization(run: WorkflowRun, _tools: ToolExecutor) -> StageOutcome:
    from harness.workflow.contracts import TaskSpec  # local import: avoids polluting module namespace

    raw = _get_raw_request(run)
    parsed = v1_task_parser.parse(raw)
    host_was_defaulted = not any(pattern.search(raw) for pattern, _ in v1_task_parser._HOST_PATTERNS)

    missing = ["product"] if parsed["product"] == "unknown" else []

    task_spec = TaskSpec(
        raw_request=raw,
        product=parsed["product"],
        host=parsed["host"],
        host_was_defaulted=host_was_defaulted,
        substrate=parsed["substrate"],
        goal=parsed["goal"],
        engineering_type=parsed["engineering_type"],
        missing_fields=missing,
    )

    def apply(r: WorkflowRun) -> None:
        r.task_spec = task_spec
        if host_was_defaulted:
            r.biological_state.uncertainty.assumptions.append(
                f"host defaulted to '{task_spec.host}' (this project's chassis default) - "
                "not explicitly stated in the request"
            )
        if missing:
            r.biological_state.uncertainty.missing_fields.extend(missing)

    pending = None
    if missing:
        pending = PendingRequest(
            kind=PendingRequestKind.missing_information,
            stage_id=Stage.TASK_NORMALIZATION.value,
            question=(
                "Could not identify the engineering target (product) from the request. "
                "Please specify the target product, e.g. 'L-tryptophan'."
            ),
        )

    return StageOutcome(
        output=task_spec.model_dump(),
        schema_valid=True,
        schema_errors=[],
        apply=apply,
        pending_request=pending,
    )


def context_and_evidence_acquisition(run: WorkflowRun, _tools: ToolExecutor) -> StageOutcome:
    retrieval = _retrieve(run)
    matched = retrieval.get("matched_ddr")

    if matched:
        reference = v1_evidence._format_reference(retrieval["ddr"])
        has_real_reference = bool(reference.strip())
        record = EvidenceRecord(
            action_source="ddr_reasoning",
            evidence_status="reference_available" if has_real_reference else "general_engineering_knowledge",
            reference=reference or None,
            confidence="medium" if has_real_reference else "low",
            source_ddr_id=matched,
            reason=retrieval.get("reason", "")
            if has_real_reference
            else retrieval["ddr"]["metadata"].get(
                "reference_note", "this DDR has no specific cited paper - it is a general engineering-knowledge synthesis"
            ),
        )
    else:
        record = EvidenceRecord(
            action_source="unknown",
            evidence_status="unknown",
            confidence="low",
            reason=retrieval.get("reason", "no matching DDR found in the current knowledge base"),
        )

    conflict_note = _near_tie_conflict_note(retrieval.get("candidates", []))

    def apply(r: WorkflowRun) -> None:
        r.evidence_records.append(record)
        if matched:
            if matched not in r.biological_state.provenance.source_record_ids:
                r.biological_state.provenance.source_record_ids.append(matched)
        else:
            r.biological_state.uncertainty.assumptions.append(
                "no DDR evidence matched this problem in the current knowledge base"
            )
        if conflict_note:
            r.biological_state.uncertainty.conflicting_fields.append(conflict_note)

    return StageOutcome(
        output={"matched_ddr": matched, "candidates_considered": retrieval.get("candidates", [])},
        schema_valid=True,
        schema_errors=[],
        apply=apply,
    )


def system_reconstruction(run: WorkflowRun, _tools: ToolExecutor) -> StageOutcome:
    """Scaffold (doc 5.3): populates BiologicalState from the normalized
    task + whatever evidence was acquired. No genome-scale reconstruction
    happens this round - `metabolic_state.constraints` says so explicitly
    rather than silently leaving it looking complete."""
    task = run.task_spec
    retrieval = _retrieve(run)
    matched_ddr = retrieval.get("ddr")

    def apply(r: WorkflowRun) -> None:
        bs = r.biological_state
        bs.host.species = "Escherichia coli"
        bs.host.strain = task.host
        bs.host.reference_genome_version = "unknown"
        bs.environment.carbon_source = task.substrate
        bs.phenotype.target_product = task.product
        bs.phenotype.target_trait = task.goal
        bs.genotype.baseline_genotype = (
            [f"wild-type {task.host}"] if not task.host_was_defaulted else ["unknown"]
        )
        bs.metabolic_state.constraints.append(
            "no genome-scale metabolic reconstruction performed this round (scaffold implementation_status)"
        )
        if matched_ddr:
            for bottleneck in matched_ddr.get("biological_diagnosis", {}).get("bottlenecks", []):
                bs.metabolic_state.constraints.append(f"reported bottleneck (from {matched_ddr['ddr_id']}): {bottleneck}")

    return StageOutcome(
        output={"host_strain": task.host, "carbon_source": task.substrate},
        schema_valid=True,
        schema_errors=[],
        apply=apply,
    )


def biological_diagnosis(run: WorkflowRun, _tools: ToolExecutor) -> StageOutcome:
    retrieval = _retrieve(run)
    diag = v1_diagnosis.diagnose(retrieval)
    record = DiagnosisRecord(
        source_ddr_id=diag["matched_ddr"],
        observations=diag["observations"],
        bottlenecks=diag["bottlenecks"],
        mechanistic_explanation=diag["mechanistic_explanation"],
        hypothesis=diag["hypothesis"],
        expected_effect=diag["expected_effect"],
    )

    def apply(r: WorkflowRun) -> None:
        r.diagnoses.append(record)

    return StageOutcome(
        output=record.model_dump(),
        schema_valid=True,
        schema_errors=[],
        apply=apply,
        diagnosis=record,
    )


def bottleneck_prioritization(run: WorkflowRun, _tools: ToolExecutor) -> StageOutcome:
    """Scaffold (doc 5.3/line 566): classifies each bottleneck string into a
    coarse mechanism class and a simple primary/secondary priority. Not a
    validated diagnosis algorithm - problem 4, explicitly deferred."""
    if not run.diagnoses:
        return StageOutcome(output={}, schema_valid=False, schema_errors=["no DiagnosisRecord to prioritize"], apply=lambda r: None)

    diag = run.diagnoses[-1]
    prioritized = []
    for i, bottleneck in enumerate(diag.bottlenecks):
        prioritized.append(
            PrioritizedBottleneck(
                description=bottleneck,
                bottleneck_class=_classify_bottleneck(bottleneck),
                priority="primary" if i == 0 else "secondary",
            )
        )

    def apply(r: WorkflowRun) -> None:
        r.diagnoses[-1].prioritized_bottlenecks = prioritized

    return StageOutcome(
        output={"prioritized_bottlenecks": [p.model_dump() for p in prioritized]},
        schema_valid=True,
        schema_errors=[],
        apply=apply,
    )


def engineering_strategy_generation(run: WorkflowRun, _tools: ToolExecutor) -> StageOutcome:
    task = run.task_spec
    retrieval = _retrieve(run)
    actions = v1_engineering.design(retrieval)
    evid_list = v1_evidence.evaluate(retrieval, actions, {"host": task.host, "product": task.product})
    diagnosis_id = run.diagnoses[-1].diagnosis_id if run.diagnoses else None

    new_evidence: list[EvidenceRecord] = []
    new_decisions: list[EngineeringDecision] = []
    for action, evid in zip(actions, evid_list):
        quality = evid.get("evidence_quality", {})
        evidence_record = EvidenceRecord(
            action_source=action.get("action_source", "unknown"),
            evidence_status=evid.get("evidence_status", "unknown"),
            reference=evid.get("reference"),
            confidence=evid.get("confidence", "low"),
            needs_validation=evid.get("needs_validation", True),
            literature_support=quality.get("literature_support", "none"),
            mechanistic_support=quality.get("mechanistic_support", "none"),
            strain_similarity=quality.get("strain_similarity", "unknown"),
            transferability=quality.get("transferability", "unknown"),
            reason=evid.get("reason", ""),
            source_ddr_id=retrieval.get("matched_ddr"),
        )
        new_evidence.append(evidence_record)

        decision = EngineeringDecision(
            diagnosis_id=diagnosis_id,
            target_entity=_target_entity_for_action(action),
            operation=_operation_for_action(action),
            mechanism=action.get("rationale", ""),
            expected_effect=action.get("expected_effect", ""),
            implementation_outline=action.get("gene_or_pathway", ""),
            evidence_record_ids=[evidence_record.evidence_record_id],
            risks=[action["risk"]] if action.get("risk") else [],
            confidence=evid.get("confidence", "low"),
            uncertainty=[evid["reason"]] if evid.get("evidence_status") != "reference_available" and evid.get("reason") else [],
        )
        new_decisions.append(decision)

    def apply(r: WorkflowRun) -> None:
        r.evidence_records.extend(new_evidence)
        r.candidate_designs.extend(new_decisions)  # append-only (design-review fix #1)

    return StageOutcome(
        output={"candidate_count": len(new_decisions)},
        schema_valid=True,
        schema_errors=[],
        apply=apply,
        gate_candidates=new_decisions,
    )


_TERMINAL_DECISION_STATUSES = (DecisionStatus.accepted, DecisionStatus.rejected)


def model_and_rule_validation(run: WorkflowRun, tools: ToolExecutor) -> StageOutcome:
    # human_review is NOT terminal - a candidate stays "unresolved" across
    # retries until it reaches accepted/rejected, so a retry after a human
    # approval/rejection actually re-evaluates it instead of treating the
    # first human_review record as already final.
    terminal_ids = {d.decision_id for d in run.engineering_decisions if d.status in _TERMINAL_DECISION_STATUSES}
    unresolved = [c for c in run.candidate_designs if c.decision_id not in terminal_ids]

    tool_records = []
    model_available = False
    if unresolved and _looks_metabolic(run):
        gene_targets = [
            (c.target_entity.canonical_id, c.operation.value)
            for c in unresolved
            if c.target_entity.type == TargetEntityType.gene
        ]
        result = tools.execute(
            "fba_flux_analysis",
            {"host": run.task_spec.host, "product": run.task_spec.product, "gene_targets": gene_targets},
            allowlist=("fba_flux_analysis",),
            stage_id=Stage.MODEL_AND_RULE_VALIDATION.value,
            idempotency_key=f"fba:{run.task_spec.host}:{run.task_spec.product}:{gene_targets}",
        )
        tool_records.append(result.record)
        model_available = not result.record.is_error and result.value is not None

    def apply(r: WorkflowRun) -> None:
        r.tool_records.extend(tool_records)

    def resolve(r: WorkflowRun, gate_result: GateResult, approvals: dict[str, str]) -> None:
        violations_by_target: dict[str, list[str]] = {}
        for v in gate_result.violations:
            if v.target_id:
                violations_by_target.setdefault(v.target_id, []).append(v.code)

        for candidate in unresolved:
            codes = set(violations_by_target.get(candidate.decision_id, []))
            decision = candidate.model_copy(deep=True)

            if codes & {"unknown_gene_id", "host_range_conflict", "operation_conflict"}:
                decision.status = DecisionStatus.rejected
                decision.rejection_reason = f"rejected by gate(s): {', '.join(sorted(codes))}"
            elif "essential_gene_knockout" in codes:
                approval = approvals.get(candidate.decision_id)
                if approval == "approved":
                    decision.status = DecisionStatus.accepted
                elif approval == "rejected":
                    decision.status = DecisionStatus.rejected
                    decision.rejection_reason = "human reviewer rejected essential-gene knockout"
                else:
                    decision.status = DecisionStatus.human_review
            elif not candidate.evidence_record_ids:
                decision.status = DecisionStatus.rejected
                decision.rejection_reason = "no supporting evidence"
            else:
                decision.status = DecisionStatus.accepted

            # Update in place if a prior (non-terminal, human_review) attempt
            # already recorded this decision_id; append only if it's new -
            # engineering_decisions (unlike candidate_designs) is exactly
            # where a decision's status is allowed to evolve over retries.
            existing_index = next(
                (i for i, d in enumerate(r.engineering_decisions) if d.decision_id == decision.decision_id), None
            )
            if existing_index is None:
                r.engineering_decisions.append(decision)
            else:
                r.engineering_decisions[existing_index] = decision

    return StageOutcome(
        output={"unresolved_count": len(unresolved), "model_available": model_available},
        schema_valid=True,
        schema_errors=[],
        apply=apply,
        gate_candidates=unresolved,
        resolve=resolve,
    )


def experiment_and_implementation_plan(run: WorkflowRun, _tools: ToolExecutor) -> StageOutcome:
    accepted = [d for d in run.engineering_decisions if d.status == DecisionStatus.accepted]
    human_review = [d for d in run.engineering_decisions if d.status == DecisionStatus.human_review]

    legacy_actions = [_decision_to_legacy_action(d) for d in accepted]
    plan = v1_validation.build_validation_plan(legacy_actions)
    decision_by_target: dict[str, str] = {a["target"]: d.decision_id for a, d in zip(legacy_actions, accepted)}

    new_items = []
    for level, lines in plan.items():
        for line in lines:
            target = line.split(":", 1)[0]
            new_items.append(
                ValidationPlanItem(
                    decision_id=decision_by_target.get(target),
                    level=ValidationLevel(level),
                    description=line,
                )
            )

    def apply(r: WorkflowRun) -> None:
        r.validation_records.extend(new_items)
        for d in accepted:
            d.validation_plan_ids = [item.validation_id for item in new_items if item.decision_id == d.decision_id]

    pending = None
    if human_review:
        first = human_review[0]
        pending = PendingRequest(
            kind=PendingRequestKind.approval,
            stage_id=Stage.EXPERIMENT_AND_IMPLEMENTATION_PLAN.value,
            question=(
                f"Decision {first.decision_id} ({first.target_entity.canonical_id}, {first.operation.value}) "
                "requires human approval before it can enter the implementation plan."
            ),
            decision_id=first.decision_id,
        )

    return StageOutcome(
        output={"validation_item_count": len(new_items), "pending_human_review": len(human_review)},
        schema_valid=True,
        schema_errors=[],
        apply=apply,
        gate_candidates=accepted + human_review,
        pending_request=pending,
    )


def final_evaluation(run: WorkflowRun, _tools: ToolExecutor) -> StageOutcome:
    decisions = run.engineering_decisions
    summary = {
        "total_candidates": len(run.candidate_designs),
        "accepted": sum(1 for d in decisions if d.status == DecisionStatus.accepted),
        "rejected": sum(1 for d in decisions if d.status == DecisionStatus.rejected),
        "human_review_pending": sum(1 for d in decisions if d.status == DecisionStatus.human_review),
        "validation_items": len(run.validation_records),
        "evidence_records": len(run.evidence_records),
    }

    def apply(r: WorkflowRun) -> None:
        r.decisions.append({"event": "final_evaluation", "ts": time.time(), **summary})

    return StageOutcome(output=summary, schema_valid=True, schema_errors=[], apply=apply)


class _LegacyStateView:
    """Duck-types `workflows.synbio_v1.state.SynBioV1State` so
    `workflows/synbio_v1/modules/report.py` can be reused completely
    unchanged (doc: reuse node logic, don't rewrite it) for rendering the
    prose report from the new structured `WorkflowRun`."""

    def __init__(self, run: WorkflowRun) -> None:
        task = run.task_spec
        self.task = (
            {
                "product": task.product,
                "host": task.host,
                "substrate": task.substrate,
                "goal": task.goal,
                "engineering_type": task.engineering_type,
            }
            if task
            else {}
        )
        self.retrieval = _retrieve(run)
        diag = run.diagnoses[-1] if run.diagnoses else None
        self.diagnosis = {
            "matched_ddr": diag.source_ddr_id if diag else None,
            "observations": diag.observations if diag else [],
            "bottlenecks": diag.bottlenecks if diag else [],
            "mechanistic_explanation": diag.mechanistic_explanation if diag else "",
            "hypothesis": diag.hypothesis if diag else "",
            "expected_effect": diag.expected_effect if diag else "",
        }
        # The prose report renders the workflow's actual conclusion (accepted
        # decisions); rejected/human_review decisions remain fully visible
        # via the structured API (GET /api/workflow-runs/{id}), not silently
        # dropped from the run state - just not narrated in this report.
        accepted = [d for d in run.engineering_decisions if d.status == DecisionStatus.accepted]
        evid_by_id = {e.evidence_record_id: e for e in run.evidence_records}
        self.engineering_actions = [_decision_to_legacy_action(d) for d in accepted]
        self.evidence = [
            _evidence_record_to_legacy(evid_by_id[d.evidence_record_ids[0]])
            if d.evidence_record_ids and d.evidence_record_ids[0] in evid_by_id
            else _evidence_record_to_legacy(EvidenceRecord(action_source="unknown", evidence_status="unknown"))
            for d in accepted
        ]
        plan: dict[str, list[str]] = {"genotype": [], "mechanism": [], "phenotype": [], "tradeoff": []}
        for item in run.validation_records:
            plan[item.level.value].append(item.description)
        self.validation_plan = plan


def report_stage(run: WorkflowRun, _tools: ToolExecutor) -> StageOutcome:
    legacy_state = _LegacyStateView(run)
    text = v1_report.generate(legacy_state)  # type: ignore[arg-type]

    def apply(r: WorkflowRun) -> None:
        r.final_report = text

    return StageOutcome(output={"report_length": len(text)}, schema_valid=True, schema_errors=[], apply=apply)


STAGE_IMPLS: dict[Stage, Any] = {
    Stage.INTAKE: intake,
    Stage.TASK_NORMALIZATION: task_normalization,
    Stage.CONTEXT_AND_EVIDENCE_ACQUISITION: context_and_evidence_acquisition,
    Stage.SYSTEM_RECONSTRUCTION: system_reconstruction,
    Stage.BIOLOGICAL_DIAGNOSIS: biological_diagnosis,
    Stage.BOTTLENECK_PRIORITIZATION: bottleneck_prioritization,
    Stage.ENGINEERING_STRATEGY_GENERATION: engineering_strategy_generation,
    Stage.MODEL_AND_RULE_VALIDATION: model_and_rule_validation,
    Stage.EXPERIMENT_AND_IMPLEMENTATION_PLAN: experiment_and_implementation_plan,
    Stage.FINAL_EVALUATION: final_evaluation,
    Stage.REPORT: report_stage,
}


def build_tool_executor() -> ToolExecutor:
    return ToolExecutor(WORKFLOW_TOOLS)


def build_controller() -> WorkflowController:
    return WorkflowController(STAGE_IMPLS, build_tool_executor())

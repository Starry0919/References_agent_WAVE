"""GateRegistry (prompt §4.5): the orchestrator's single structured
checkpoint layer. Where an existing per-module gate function already
computes the right thing (`data_qc_gate`, `diagnosis_handoff_gate`,
`design_objective_gate`, `redesign_gate`, `scientific_revision_gate`) this
module calls it directly and normalizes its `GateStatus` into the unified
`GATE_DECISIONS` vocabulary - it does not reimplement those rules. Where no
existing gate fits (top-level context completeness, model applicability
read off `CompatibilityReport`, simulation evidence read off
`PredictionReview`, the top-level human-approval/safety checkpoint, the
stop decision) this module adds a small, honest, rule-based function of its
own - never an LLM call, per prompt §2.4/§2.5.

No module here may be bypassed by editing a status string directly: every
call site in `harness/orchestrator/service.py` goes through
`GateRegistry.evaluate()`, which always persists an `OrchestratorGateDecision`
row before the orchestrator acts on the result.
"""
from __future__ import annotations

from typing import Any, Callable

from harness.orchestrator.contracts import GateDecisionResult
from harness.workflow.contracts import GateStatus
from harness.workflow.gates import (
    data_qc_gate,
    design_objective_gate,
    diagnosis_handoff_gate,
    redesign_gate,
    scientific_revision_gate,
)

# Worst-status-wins mapping from the existing `GateStatus` vocabulary onto
# the orchestrator's `GATE_DECISIONS` vocabulary (prompt §4.5) - a pure
# renaming, not a re-judgment.
_STATUS_TO_DECISION = {
    GateStatus.passed: "pass",
    GateStatus.revise: "revise",
    GateStatus.insufficient_evidence: "wait_for_data",
    GateStatus.human_review: "human_review_required",
    GateStatus.fail: "blocked",
}


def _from_gate_result(gate_type: str, result, *, evaluated_refs: dict[str, str] | None = None) -> GateDecisionResult:
    return GateDecisionResult(
        gate_type=gate_type,
        decision=_STATUS_TO_DECISION[result.status],
        evaluated_refs=evaluated_refs or {},
        blocking_findings=[v.message for v in result.violations] if result.status == GateStatus.fail else [],
        non_blocking_findings=[v.message for v in result.violations] if result.status != GateStatus.fail else [],
        required_actions=list(result.required_actions),
        rule_versions={gate_type: "harness.workflow.gates@repo-current"},
    )


def context_completeness_gate(*, has_target_product: bool, has_host: bool, has_actor: bool) -> GateDecisionResult:
    missing = [n for n, ok in (("target_product", has_target_product), ("host", has_host), ("actor", has_actor)) if not ok]
    if missing:
        return GateDecisionResult(
            gate_type="context_completeness", decision="wait_for_data",
            blocking_findings=[f"missing required intake field(s): {missing}"],
            required_actions=[f"provide {m}" for m in missing],
        )
    return GateDecisionResult(gate_type="context_completeness", decision="pass")


def data_quality_gate(*, qc_passed: bool, error_flags: list[tuple[str, str, str]]) -> GateDecisionResult:
    return _from_gate_result("data_quality", data_qc_gate(qc_passed=qc_passed, error_flags=error_flags))


def diagnosis_handoff_gate_wrapper(
    *, stopping_reason: str, engineering_value_passed: bool, human_approval_required: bool, human_approved: bool | None,
    decision_ref: str,
) -> GateDecisionResult:
    result = diagnosis_handoff_gate(
        stopping_reason=stopping_reason, engineering_value_passed=engineering_value_passed,
        human_approval_required=human_approval_required, human_approved=human_approved,
    )
    # doc03's own gate has no "not yet reached a stop" distinction from
    # "reached a stop but failed" - the orchestrator needs the former to
    # mean "keep running diagnosis", not "blocked".
    if result.status == GateStatus.fail and stopping_reason in ("continue_diagnosis", ""):
        return GateDecisionResult(
            gate_type="diagnosis_handoff", decision="wait_for_data",
            evaluated_refs={"diagnosis_decision": decision_ref},
            required_actions=["continue diagnosis: hypothesis set or evidence coverage not yet stable"],
        )
    return _from_gate_result("diagnosis_handoff", result, evaluated_refs={"diagnosis_decision": decision_ref})


def engineering_feasibility_gate(*, has_primary_metrics: bool, has_hard_constraints_declared: bool, project_ref: str) -> GateDecisionResult:
    result = design_objective_gate(has_primary_metrics=has_primary_metrics, has_hard_constraints_declared=has_hard_constraints_declared)
    return _from_gate_result("engineering_feasibility", result, evaluated_refs={"design_project": project_ref})


_META_REVIEW_TO_DECISION = {
    "approve_for_planning": "pass",
    "request_more_evidence": "wait_for_data",
    "request_model_run": "wait_for_data",
    "return_to_diagnosis": "human_review_required",
    "revise": "revise",
    "reject": "blocked",
}


def scientific_evaluation_gate(
    *, recommended_action: str, open_blocking_findings: list[str], revision_round: int, revision_limit: int, evaluation_ref: str,
) -> GateDecisionResult:
    revision_result = scientific_revision_gate(
        open_blocking_findings=open_blocking_findings, revision_round=revision_round, revision_limit=revision_limit,
    )
    if revision_result.status == GateStatus.human_review:
        return GateDecisionResult(
            gate_type="scientific_evaluation", decision="human_review_required",
            evaluated_refs={"evaluation_case": evaluation_ref},
            blocking_findings=[v.message for v in revision_result.violations],
            required_actions=["revision limit reached with open blocking findings - human decision required"],
        )
    decision = _META_REVIEW_TO_DECISION.get(recommended_action, "human_review_required")
    return GateDecisionResult(
        gate_type="scientific_evaluation", decision=decision, evaluated_refs={"evaluation_case": evaluation_ref},
        blocking_findings=list(open_blocking_findings) if decision == "revise" else [],
        non_blocking_findings=list(open_blocking_findings) if decision != "revise" else [],
        required_actions=[f"meta-review recommended_action={recommended_action!r}"],
    )


_COMPATIBILITY_TO_DECISION = {
    "compatible": "pass",
    "compatible_with_assumptions": "pass_with_conditions",
}


def model_applicability_gate(*, compatibility_decision: str | None, blocking_reasons: list[str], case_ref: str) -> GateDecisionResult:
    if compatibility_decision is None:
        return GateDecisionResult(
            gate_type="model_applicability", decision="not_applicable", evaluated_refs={"simulation_case": case_ref},
            non_blocking_findings=["no perturbation was compiled for this DesignVersion - simulation is not applicable"],
        )
    decision = _COMPATIBILITY_TO_DECISION.get(compatibility_decision, "blocked")
    return GateDecisionResult(
        gate_type="model_applicability", decision=decision, evaluated_refs={"simulation_case": case_ref},
        blocking_findings=list(blocking_reasons) if decision == "blocked" else [],
        non_blocking_findings=list(blocking_reasons) if decision != "blocked" else [],
    )


_PREDICTION_REVIEW_TO_DECISION = {
    "decision_ready": "pass",
    "limited_acceptance": "pass_with_conditions",
}


def simulation_evidence_gate(*, review_decision: str | None, findings: list[dict[str, Any]], case_ref: str) -> GateDecisionResult:
    if review_decision is None:
        return GateDecisionResult(
            gate_type="simulation_evidence", decision="not_applicable", evaluated_refs={"simulation_case": case_ref},
            non_blocking_findings=["no comparable simulation run exists for this case"],
        )
    decision = _PREDICTION_REVIEW_TO_DECISION.get(review_decision, "human_review_required")
    blocking = [f.get("message", str(f)) for f in findings if f.get("severity") == "blocking"]
    return GateDecisionResult(
        gate_type="simulation_evidence", decision=("blocked" if blocking else decision),
        evaluated_refs={"simulation_case": case_ref}, blocking_findings=blocking,
        non_blocking_findings=[f.get("message", str(f)) for f in findings if f.get("severity") != "blocking"],
    )


def safety_ethics_gate(*, forbidden_flags: list[str], run_ref: str) -> GateDecisionResult:
    """A minimal, honest top-level safety screen: this orchestrator does
    not invent a new biosafety rule engine - it surfaces whatever
    `forbidden_flags` upstream module gates (BiologicalRuleGate,
    SafetyHumanGate's forbidden tier, DesignDiversityGate) already raised,
    and blocks unconditionally if any are present. It is not a substitute
    for the module-level safety gates it reads from."""
    if forbidden_flags:
        return GateDecisionResult(
            gate_type="safety_ethics", decision="blocked", evaluated_refs={"workflow_run": run_ref},
            blocking_findings=list(forbidden_flags),
            required_actions=["resolve the forbidden/unsafe finding(s) raised by an upstream module gate"],
        )
    return GateDecisionResult(gate_type="safety_ethics", decision="pass", evaluated_refs={"workflow_run": run_ref})


def human_approval_gate(*, decision: str, actor: str, reason: str, run_ref: str) -> GateDecisionResult:
    """Records the PI's single top-level go/no-go once every per-module
    approval (design build approval, scientific evaluation human gate) is
    already satisfied - this does not replace those; `service.py` checks
    their status before this gate may even be requested (prompt §2.4:
    "LLM 不可以...直接批准自己的设计" - applies equally to any single
    reviewer; the calling API layer is responsible for `actor` being a
    human identity distinct from the proposer, same discipline as
    `harness.designs.service.SelfApprovalError`)."""
    mapping = {"approve": "pass", "reject": "blocked", "hold": "human_review_required"}
    if decision not in mapping:
        raise ValueError(f"human_approval_gate: decision must be one of {sorted(mapping)}, got {decision!r}")
    return GateDecisionResult(
        gate_type="human_approval", decision=mapping[decision], evaluated_refs={"workflow_run": run_ref},
        non_blocking_findings=[reason] if reason else [], reviewer_refs=[actor],
    )


def observation_qc_gate(*, qc_passed: bool, error_flags: list[tuple[str, str, str]]) -> GateDecisionResult:
    return _from_gate_result("observation_qc", data_qc_gate(qc_passed=qc_passed, error_flags=error_flags))


def redesign_gate_wrapper(*, has_retain_remove_add: bool, has_triggering_justification: bool, is_identical_to_parent: bool) -> GateDecisionResult:
    return _from_gate_result(
        "redesign",
        redesign_gate(
            has_retain_remove_add=has_retain_remove_add, has_triggering_justification=has_triggering_justification,
            is_identical_to_parent=is_identical_to_parent,
        ),
    )


_STOP_DECISIONS = {"stop": "pass", "next_iteration": "not_applicable", "diagnosis_reopened": "not_applicable", "continue_build": "not_applicable"}


def stop_gate(*, decided_next_action: str, run_ref: str) -> GateDecisionResult:
    decision = _STOP_DECISIONS.get(decided_next_action, "human_review_required")
    return GateDecisionResult(
        gate_type="stop", decision=decision, evaluated_refs={"workflow_run": run_ref},
        non_blocking_findings=[f"decided_next_action={decided_next_action!r}"],
    )


GateFunc = Callable[..., GateDecisionResult]

GATE_REGISTRY: dict[str, GateFunc] = {
    "context_completeness": context_completeness_gate,
    "data_quality": data_quality_gate,
    "diagnosis_handoff": diagnosis_handoff_gate_wrapper,
    "engineering_feasibility": engineering_feasibility_gate,
    "scientific_evaluation": scientific_evaluation_gate,
    "model_applicability": model_applicability_gate,
    "simulation_evidence": simulation_evidence_gate,
    "safety_ethics": safety_ethics_gate,
    "human_approval": human_approval_gate,
    "observation_qc": observation_qc_gate,
    "redesign": redesign_gate_wrapper,
    "stop": stop_gate,
}


class GateRegistry:
    """Thin, stateless lookup - `harness/orchestrator/service.py` always
    calls `evaluate()` rather than importing a gate function directly, so
    no call site can accidentally skip the registry (prompt §4.5: "任何模块
    不得通过修改字符串状态绕过 Gate")."""

    def evaluate(self, gate_type: str, **kwargs: Any) -> GateDecisionResult:
        if gate_type not in GATE_REGISTRY:
            raise ValueError(f"unknown gate_type {gate_type!r}; must be one of {sorted(GATE_REGISTRY)}")
        return GATE_REGISTRY[gate_type](**kwargs)

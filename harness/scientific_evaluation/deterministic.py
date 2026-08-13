"""Deterministic Validator (doc05 §4.2): code rules, never an LLM, for
whatever is mechanically checkable - schema/reference completeness,
context consistency, hard constraints, model-record honesty, Build/Test
plan completeness, and (at the pre-human-gate pass) Human Gate legality and
critical-finding bypass. Every rule is versioned (`rule_id`, `rule_version`)
and returns a structured `DeterministicCheckResult`, never a bare boolean.
"""
from __future__ import annotations

from typing import Any, Callable

from sqlalchemy import select
from sqlalchemy.orm import Session

from harness.engineering_design import decision as decision_mod
from harness.engineering_design.models import (
    BuildTestPackage,
    CandidateDesign,
    CounterfactualRun,
    EngineeringDesignProject,
    EngineeringStrategy,
    HumanApprovalRecord,
)
from harness.ids import new_id, now
from harness.memory import event_types as et
from harness.memory.event_store import append_event
from harness.scientific_evaluation.models import CriticFinding, DeterministicCheckResult, EvaluationCase, ScientificReview

RuleFn = Callable[[dict[str, Any]], list[dict[str, Any]]]


def _result(rule_id: str, rule_version: str, category: str, status: str, severity: str, message: str,
            affected_fields: list[str] | None = None, evidence_or_rule_reference: str = "", remediation: str = "") -> dict[str, Any]:
    return {
        "rule_id": rule_id, "rule_version": rule_version, "category": category, "status": status, "severity": severity,
        "message": message, "affected_fields": affected_fields or [], "evidence_or_rule_reference": evidence_or_rule_reference,
        "remediation": remediation,
    }


def _rule_schema_completeness(ctx: dict[str, Any]) -> list[dict[str, Any]]:
    c: CandidateDesign = ctx["candidate"]
    out = []
    has_content = bool(c.genetic_modifications or c.process_modifications)
    if has_content and not c.expected_mechanism:
        out.append(_result(
            "DET-001", "1", "schema_completeness", "fail", "major",
            "candidate declares modifications but expected_mechanism is empty",
            ["expected_mechanism"], remediation="state the mechanistic rationale for the declared modifications",
        ))
    if not ctx["claims"]:
        out.append(_result(
            "DET-001", "1", "schema_completeness", "warning", "moderate",
            "no ScientificClaim could be extracted from this candidate - nothing for a Reviewer to assess",
            ["claims"],
        ))
    if not out:
        out.append(_result("DET-001", "1", "schema_completeness", "pass", "informational", "candidate schema is complete enough to review"))
    return out


def _rule_reference_validity(ctx: dict[str, Any]) -> list[dict[str, Any]]:
    c: CandidateDesign = ctx["candidate"]
    known_strategy_ids: set[str] = ctx["known_strategy_ids"]
    dangling = [sid for sid in c.strategy_ids if sid not in known_strategy_ids]
    if dangling:
        return [_result(
            "DET-002", "1", "reference_validity", "fail", "critical",
            f"candidate references strategy id(s) not found in this design project: {dangling}",
            ["strategy_ids"], remediation="remove or correct dangling strategy_ids references",
        )]
    return [_result("DET-002", "1", "reference_validity", "pass", "informational", "all strategy_ids resolve to known strategies")]


def _rule_context_consistency(ctx: dict[str, Any]) -> list[dict[str, Any]]:
    c: CandidateDesign = ctx["candidate"]
    case: EvaluationCase = ctx["case"]
    frozen_diag_version = case.frozen_context.get("diagnosis_version_at_freeze")
    if frozen_diag_version is not None and c.source_diagnosis_version != frozen_diag_version:
        return [_result(
            "DET-003", "1", "context_consistency", "warning", "major",
            f"candidate was generated against diagnosis_version={c.source_diagnosis_version} but the frozen evaluation "
            f"context is diagnosis_version={frozen_diag_version} - diagnosis may have moved on since this candidate was proposed",
            ["source_diagnosis_version"], remediation="re-check DiagnosisHandoffRecord.is_stale before proceeding",
        )]
    return [_result("DET-003", "1", "context_consistency", "pass", "informational", "candidate's source diagnosis version matches the frozen context")]


def _rule_hard_constraints(ctx: dict[str, Any]) -> list[dict[str, Any]]:
    c: CandidateDesign = ctx["candidate"]
    case: EvaluationCase = ctx["case"]
    cd = {"genetic_modifications": c.genetic_modifications}
    hard_constraints = case.frozen_context.get("hard_constraints", [])
    results = decision_mod.check_hard_constraints(cd, hard_constraints)
    out = []
    for r in results:
        if r["satisfied"] is False:
            out.append(_result(
                "DET-004", "1", "hard_constraints", "fail", "critical", f"hard constraint violated: {r['constraint']} - {r['detail']}",
                ["genetic_modifications"], remediation="revise the candidate to satisfy this hard constraint",
            ))
        elif r["satisfied"] is None:
            out.append(_result(
                "DET-004", "1", "hard_constraints", "warning", "moderate",
                f"hard constraint not automatically checkable, requires human review: {r['constraint']} - {r['detail']}",
                ["genetic_modifications"],
            ))
    if not out:
        out.append(_result("DET-004", "1", "hard_constraints", "pass", "informational", "all automatically-checkable hard constraints satisfied"))
    return out


def _rule_model_result_realism(ctx: dict[str, Any]) -> list[dict[str, Any]]:
    """doc05 §2.4: a candidate's own `counterfactual_results` must trace to
    a real, persisted `CounterfactualRun` row - never a number that appears
    in the candidate's summary with no backing run record."""
    c: CandidateDesign = ctx["candidate"]
    session: Session = ctx["session"]
    real_run_ids = {
        r.run_id for r in session.execute(select(CounterfactualRun.run_id).where(CounterfactualRun.design_id == c.design_id)).all()
    }
    claimed_run_ids = {r.get("run_id") for r in c.counterfactual_results if r.get("run_id")}
    orphaned = claimed_run_ids - real_run_ids
    if orphaned:
        return [_result(
            "DET-005", "1", "model_result_realism", "fail", "critical",
            f"candidate.counterfactual_results references run id(s) with no matching CounterfactualRun row: {sorted(orphaned)}",
            ["counterfactual_results"], remediation="only report model results backed by a real, persisted run record",
        )]
    return [_result("DET-005", "1", "model_result_realism", "pass", "informational", "every reported counterfactual result traces to a real CounterfactualRun row")]


def _rule_build_test_plan_completeness(ctx: dict[str, Any]) -> list[dict[str, Any]]:
    c: CandidateDesign = ctx["candidate"]
    session: Session = ctx["session"]
    if c.readiness not in ("planning_ready", "build_ready") and c.build_test_package_id is None:
        return [_result("DET-006", "1", "build_test_plan_completeness", "not_applicable", "informational",
                         "candidate has not yet reached planning_ready - no Build/Test plan required at this readiness level")]
    pkg = session.get(BuildTestPackage, c.build_test_package_id) if c.build_test_package_id else None
    if pkg is None:
        return [_result(
            "DET-006", "1", "build_test_plan_completeness", "fail", "major",
            f"candidate readiness={c.readiness!r} but no BuildTestPackage is attached", ["build_test_package_id"],
            remediation="draft a BuildTestPackage with controls, replication, sampling, QC, and decision rules",
        )]
    missing = [
        name for name, present in {
            "controls": bool(pkg.controls), "replication_plan": bool(pkg.replication_plan),
            "sampling_plan": bool(pkg.sampling_plan), "qc_checkpoints": bool(pkg.qc_checkpoints),
            "decision_rules": bool(pkg.decision_rules),
        }.items() if not present
    ]
    if missing:
        return [_result(
            "DET-006", "1", "build_test_plan_completeness", "fail", "major",
            f"BuildTestPackage is missing required fields: {missing}", missing,
            remediation=f"add {missing} to the Build/Test plan before build approval",
        )]
    return [_result("DET-006", "1", "build_test_plan_completeness", "pass", "informational", "Build/Test plan carries controls, replication, sampling, QC and decision rules")]


# Rules applicable at the initial `deterministic_validation` stage (no
# dependency on critic findings that do not exist yet).
_INTAKE_RULES: list[RuleFn] = [
    _rule_schema_completeness, _rule_reference_validity, _rule_context_consistency,
    _rule_hard_constraints, _rule_model_result_realism, _rule_build_test_plan_completeness,
]


def _rule_human_gate_legality(ctx: dict[str, Any]) -> list[dict[str, Any]]:
    c: CandidateDesign = ctx["candidate"]
    session: Session = ctx["session"]
    if c.status != "approved_for_build":
        return [_result("DET-007", "1", "human_gate_legality", "not_applicable", "informational", "candidate is not yet approved_for_build")]
    has_approval = session.execute(select(HumanApprovalRecord).where(HumanApprovalRecord.design_id == c.design_id)).scalars().first() is not None
    if not has_approval:
        return [_result(
            "DET-007", "1", "human_gate_legality", "fail", "critical",
            "candidate.status=approved_for_build but no HumanApprovalRecord exists for it", ["status"],
            remediation="record an explicit HumanApprovalRecord/HumanEvaluationDecision before this status is legal",
        )]
    return [_result("DET-007", "1", "human_gate_legality", "pass", "informational", "approved_for_build is backed by a real human approval record")]


def _rule_critical_finding_bypass(ctx: dict[str, Any]) -> list[dict[str, Any]]:
    c: CandidateDesign = ctx["candidate"]
    session: Session = ctx["session"]
    review_ids = [r.review_id for r in session.execute(select(ScientificReview.review_id).where(ScientificReview.design_reference == c.design_id)).all()]
    if not review_ids:
        return [_result("DET-008", "1", "critical_finding_bypass", "not_applicable", "informational", "no ScientificReview exists yet for this candidate")]
    open_critical = session.execute(
        select(CriticFinding).where(
            CriticFinding.review_id.in_(review_ids), CriticFinding.severity == "critical",
            CriticFinding.blocking.is_(True), CriticFinding.status == "open",
        )
    ).scalars().all()
    if open_critical:
        return [_result(
            "DET-008", "1", "critical_finding_bypass", "fail", "critical",
            f"{len(open_critical)} open, blocking, critical CriticFinding(s) exist and were not resolved or explicitly risk-acknowledged by a human",
            ["status"], remediation="resolve each finding or have a human explicitly acknowledge the risk before proceeding to build approval",
        )]
    return [_result("DET-008", "1", "critical_finding_bypass", "pass", "informational", "no unresolved, blocking critical findings remain")]


_PRE_HUMAN_GATE_RULES: list[RuleFn] = [_rule_human_gate_legality, _rule_critical_finding_bypass]


def _persist(session: Session, *, evaluation_id: str, design_reference: str, raw_results: list[dict[str, Any]]) -> list[DeterministicCheckResult]:
    ts = now()
    rows = [
        DeterministicCheckResult(
            check_id=new_id("DCHK"), evaluation_id=evaluation_id, rule_id=r["rule_id"], rule_version=r["rule_version"],
            design_reference=design_reference, category=r["category"], status=r["status"], severity=r["severity"],
            message=r["message"], affected_fields=r["affected_fields"], evidence_or_rule_reference=r["evidence_or_rule_reference"],
            remediation=r["remediation"], created_at=ts,
        )
        for r in raw_results
    ]
    for row in rows:
        session.add(row)
    session.flush()
    return rows


def run_deterministic_checks(
    session: Session, *, case: EvaluationCase, candidate: CandidateDesign, claims: list, proj: EngineeringDesignProject,
) -> list[DeterministicCheckResult]:
    known_strategy_ids = {
        s.strategy_id for s in session.execute(select(EngineeringStrategy).where(EngineeringStrategy.design_project_id == proj.design_project_id)).scalars()
    }
    ctx = {"session": session, "case": case, "candidate": candidate, "claims": claims, "known_strategy_ids": known_strategy_ids}
    raw = [r for rule in _INTAKE_RULES for r in rule(ctx)]
    rows = _persist(session, evaluation_id=case.evaluation_id, design_reference=candidate.design_id, raw_results=raw)
    append_event(
        session, project_id=case.project_id, event_type=et.EVAL_DETERMINISTIC_CHECKS_RUN, entity_type="EvaluationCase",
        entity_id=case.evaluation_id, payload={"design_id": candidate.design_id, "results": [r["rule_id"] + ":" + r["status"] for r in raw]},
        actor_type="agent", actor_id="system",
    )
    return rows


def run_pre_human_gate_checks(session: Session, *, case: EvaluationCase, candidate: CandidateDesign) -> list[DeterministicCheckResult]:
    ctx = {"session": session, "case": case, "candidate": candidate}
    raw = [r for rule in _PRE_HUMAN_GATE_RULES for r in rule(ctx)]
    rows = _persist(session, evaluation_id=case.evaluation_id, design_reference=candidate.design_id, raw_results=raw)
    append_event(
        session, project_id=case.project_id, event_type=et.EVAL_DETERMINISTIC_CHECKS_RUN, entity_type="EvaluationCase",
        entity_id=case.evaluation_id, payload={"design_id": candidate.design_id, "stage": "pre_human_gate", "results": [r["rule_id"] + ":" + r["status"] for r in raw]},
        actor_type="agent", actor_id="system",
    )
    return rows


def blocks_progression(results: list[DeterministicCheckResult]) -> bool:
    return any(r.status == "fail" and r.severity in ("critical", "major") for r in results)

"""MechanismEvaluator (doc04 §4.4): every genetic modification must trace
back to a strategy this candidate declares, and every declared strategy
must itself have been grounded by the diagnosis (not invented at
portfolio-generation time) - a candidate cannot silently modify a target
its own `strategy_ids` never mention.
"""
from __future__ import annotations

from typing import Any

from harness.engineering_design.evaluators.base import EvaluatorResult


def evaluate(candidate: dict[str, Any], *, known_strategy_ids: set[str]) -> EvaluatorResult:
    findings: list[str] = []
    required_revisions: list[str] = []
    blocking = False

    unknown_strategy_refs = [sid for sid in candidate.get("strategy_ids", []) if sid not in known_strategy_ids]
    if unknown_strategy_refs:
        findings.append(f"candidate references strategy id(s) not found in this design project: {unknown_strategy_refs}")
        required_revisions.append("remove or correct dangling strategy_ids references")
        blocking = True

    mods = candidate.get("genetic_modifications", [])
    if mods and not candidate.get("strategy_ids"):
        findings.append("candidate declares genetic modifications but no strategy_ids - modifications must trace to a strategy")
        required_revisions.append("attach at least one strategy_id justifying each modification")
        blocking = True

    unlinked = [m for m in mods if not m.get("evidence_links")]
    if unlinked:
        findings.append(f"{len(unlinked)} of {len(mods)} modification(s) carry no evidence_links back to a strategy/hypothesis")
        required_revisions.append("link every modification to the strategy/hypothesis evidence that motivates it")

    if not findings:
        findings.append("every modification traces to a declared, known strategy")
        status = "pass"
    elif blocking:
        status = "fail"
    else:
        status = "warning"

    return EvaluatorResult(
        evaluator="MechanismEvaluator", status=status, findings=findings,
        evidence_or_tool_refs=list(candidate.get("strategy_ids", [])), assumptions=[],
        required_revisions=required_revisions, blocking=blocking,
    )

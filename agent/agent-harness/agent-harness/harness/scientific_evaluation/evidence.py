"""Evidence Quality and Transferability Evaluator (doc05 §4.3/§2.3): for
every `ScientificClaim`, resolves its `source_references` against the real
curated knowledge base (`knowledge/engineering_actions/action_database.json`
- the same file `harness.engineering_design.strategy_service.load_action_
database` already reads, reused here rather than re-parsed) and this
project's own history (`harness.engineering_design.memory_integration`),
and scores condition-match dimensions honestly. A claim whose only backing
is `llm_hypothesis` (no resolvable reference) gets ONE explicit `unsupported`
`EvidenceAssessment` row (`evidence_id=None`), never a silently-omitted one
and never a fabricated citation to fill the gap (doc05 §4.3: "claim 没有
证据时输出 unsupported,而不是自动补引文").

Honesty note (goes in the final report's "Honest Degradation" section):
the curated knowledge base this evaluator can real-check against
(`action_database.json`, `knowledge/ddr_database/*.json`) does not itself
record medium/carbon-source/oxygenation/temperature/process-scale/growth-
phase metadata per entry - most entries explicitly self-describe as
"general, well-established engineering pattern...not a specific verified
experimental result" (see `knowledge/engineering_actions/action_database.
json`). `condition_match`/`process_match`/`time_match`/`measurement_match`
therefore come back `unknown` for most curated-knowledge-sourced claims -
this is an honest reflection of a real gap in the current knowledge base,
never upgraded to "close"/"exact" without an actual field to compare.
"""
from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from harness.engineering_design import memory_integration
from harness.engineering_design.models import CandidateDesign
from harness.engineering_design.strategy_service import load_action_database
from harness.ids import new_id, now
from harness.scientific_evaluation.models import EvidenceAssessment, EvaluationCase, ScientificClaim

_GENERAL_KNOWLEDGE_HEDGES = ("general", "not a specific verified experimental result", "not verified")


def _action_by_id(action_id: str) -> dict[str, Any] | None:
    for a in load_action_database():
        if a.get("action_id") == action_id:
            return a
    return None


def _assess_database_record_claim(claim: ScientificClaim, frozen_context: dict[str, Any]) -> dict[str, Any]:
    action = None
    for ref in claim.source_references:
        action = _action_by_id(ref)
        if action is not None:
            break
    if action is None:
        return {
            "evidence_id": None, "source_quality": "unknown", "independence": "unknown",
            "host_match": "unknown", "genotype_match": "unknown", "condition_match": "unknown",
            "process_match": "unknown", "time_match": "unknown", "intervention_match": "unknown",
            "measurement_match": "unknown", "mechanism_match": "unknown", "directness": "indirect",
            "opposing_evidence": [], "applicability_limits": [], "over_extrapolation_flags": [],
            "overall_strength": "unknown", "reasoning_summary": "claim cites a database reference that could not be resolved in the curated knowledge base",
        }

    target = claim.scope_conditions.get("target")
    operation = claim.scope_conditions.get("operation")
    intervention_match = "unknown"
    mechanism_match = "unknown"
    if target is not None:
        if action.get("target_gene") == target and action.get("modification") == operation:
            intervention_match = "exact"
        elif action.get("target_gene") == target:
            intervention_match = "close"
        else:
            intervention_match = "poor"
    if action.get("mechanism") and claim.claim_text:
        mechanism_match = "close" if target and action.get("target_gene") == target else "partial"

    evidence_text = str(action.get("evidence", ""))
    hedge = any(h in evidence_text.lower() for h in _GENERAL_KNOWLEDGE_HEDGES)
    over_extrapolation = [f"knowledge base entry {action.get('action_id')} self-describes as general/unverified: {evidence_text!r}"] if hedge else []

    opposing: list[str] = []
    applicability = list(action.get("applicable_conditions", []))

    strength = "moderate" if intervention_match in ("exact", "close") and not hedge else "weak"
    return {
        "evidence_id": action.get("action_id"), "source_quality": "medium" if not hedge else "low",
        "independence": "unknown", "host_match": "unknown", "genotype_match": "unknown",
        "condition_match": "unknown", "process_match": "unknown", "time_match": "unknown",
        "intervention_match": intervention_match, "measurement_match": "unknown", "mechanism_match": mechanism_match,
        "directness": "indirect", "opposing_evidence": opposing, "applicability_limits": applicability,
        "over_extrapolation_flags": over_extrapolation, "overall_strength": strength,
        "reasoning_summary": f"curated engineering-action entry {action.get('action_id')} matched on target/mechanism; "
                              f"no condition (medium/carbon/O2/temperature/scale/timepoint) metadata is recorded in this knowledge base entry, so those dimensions are honestly unknown, not assumed matched",
    }


def _assess_llm_hypothesis_claim(claim: ScientificClaim) -> dict[str, Any]:
    return {
        "evidence_id": None, "source_quality": "unknown", "independence": "unknown",
        "host_match": "unknown", "genotype_match": "unknown", "condition_match": "unknown",
        "process_match": "unknown", "time_match": "unknown", "intervention_match": "unknown",
        "measurement_match": "unknown", "mechanism_match": "unknown", "directness": "indirect",
        "opposing_evidence": [], "applicability_limits": [], "over_extrapolation_flags": [],
        "overall_strength": "unknown",
        "reasoning_summary": "claim carries no resolvable evidence reference - it is an unsupported hypothesis, not an evidenced claim",
    }


def _assess_experimental_or_model_claim(claim: ScientificClaim) -> dict[str, Any]:
    """`experimental_observation`/`computational_model` claims in the
    current pipeline reference a prior diagnosis's `evidence_references`
    (opaque DDR-style ids: see doc05 §14's own honesty note about "无真实
    文献检索工具") or a `CounterfactualRun.run_id` (handled directly by
    `harness/scientific_evaluation/model_eval.py`, not here) - this
    evaluator resolves what it verifiably can and marks the rest `unknown`,
    never fabricating a resolved match."""
    return {
        "evidence_id": claim.source_references[0] if claim.source_references else None,
        "source_quality": "unknown" if not claim.source_references else "medium",
        "independence": "unknown", "host_match": "unknown", "genotype_match": "unknown",
        "condition_match": "unknown", "process_match": "unknown", "time_match": "unknown",
        "intervention_match": "unknown", "measurement_match": "unknown", "mechanism_match": "unknown",
        "directness": "indirect",
        "opposing_evidence": [], "applicability_limits": [], "over_extrapolation_flags": [],
        "overall_strength": "weak" if claim.source_references else "unknown",
        "reasoning_summary": "referenced but not independently re-resolvable by this evaluator without a live literature/model-run lookup tool - reported as-is, not upgraded",
    }


def assess_evidence(
    session: Session, *, case: EvaluationCase, candidate: CandidateDesign, claims: list[ScientificClaim],
) -> list[EvidenceAssessment]:
    history = memory_integration.rejected_or_failed_signatures(session, design_project_id=case.design_project_id)
    ts = now()
    rows: list[EvidenceAssessment] = []

    for claim in claims:
        if claim.source_type == "database_record":
            data = _assess_database_record_claim(claim, case.frozen_context)
        elif claim.source_type == "llm_hypothesis":
            data = _assess_llm_hypothesis_claim(claim)
        else:
            data = _assess_experimental_or_model_claim(claim)

        # Real, historical opposing evidence: this exact modification
        # signature was previously rejected/failed for this design project
        # (doc05 §2.3's "opposing evidence" - never dropped silently).
        target, operation = claim.scope_conditions.get("target"), claim.scope_conditions.get("operation")
        if target and operation:
            sig = frozenset({(target, operation)})
            matches = [prior_id for s, ids in history.items() for prior_id in ids if s & sig]
            if matches:
                data["opposing_evidence"] = list(data["opposing_evidence"]) + [
                    f"identical (target,operation) was previously rejected/failed for this design project: {matches}"
                ]
                data["overall_strength"] = "weak" if data["overall_strength"] in ("moderate", "strong") else data["overall_strength"]

        row = EvidenceAssessment(
            assessment_id=new_id("EVASS"), evaluation_id=case.evaluation_id, claim_id=claim.claim_id,
            evidence_id=data["evidence_id"], evidence_type=claim.source_type, source_quality=data["source_quality"],
            independence=data["independence"], host_match=data["host_match"], genotype_match=data["genotype_match"],
            condition_match=data["condition_match"], process_match=data["process_match"], time_match=data["time_match"],
            intervention_match=data["intervention_match"], measurement_match=data["measurement_match"],
            mechanism_match=data["mechanism_match"], directness=data["directness"],
            opposing_evidence=data["opposing_evidence"], applicability_limits=data["applicability_limits"],
            over_extrapolation_flags=data["over_extrapolation_flags"], overall_strength=data["overall_strength"],
            reasoning_summary=data["reasoning_summary"], assessor_type="deterministic_rule",
            provenance={"method": "evidence_evaluator_v1", "resolved_from": "action_database.json" if claim.source_type == "database_record" else "claim_source_references"},
            created_at=ts,
        )
        session.add(row)
        rows.append(row)

    session.flush()
    return rows


def unsupported_claim_ids(assessments: list[EvidenceAssessment]) -> list[str]:
    return [a.claim_id for a in assessments if a.evidence_id is None]

"""LLM Scientific Critic adapter (prompt §5.5): a real, live-LLM-backed
`ScientificReview` reviewer, ADDED to the deterministic generalist +
domain critics `harness/scientific_evaluation/critic.py` already runs -
never replacing them, and never itself sufficient for approval. This is
exactly the "documented residual enhancement" that module's own docstring
names as the plug-in point (`RUBRIC_VERSION`/`ScientificReview`/
`CriticFinding` shapes reused verbatim, not forked).

Independence, honestly bounded (prompt §5.5):
- context_independent=True: reads the SAME frozen `ScientificClaim`/
  `EvidenceAssessment`/`ModelEvaluationRecord`/`DeterministicCheckResult`
  rows the deterministic critic reads - never the Designer's internal
  reasoning (this repo's deterministic strategy generator has no
  chain-of-thought to leak in the first place; the LLM Strategy Draft
  adapter's own raw completions are never passed to this critic either -
  only the persisted, schema-validated `EngineeringStrategy`/
  `CandidateDesign` fields are).
- rubric_independent=True: the prompt explicitly instructs the model to
  hunt for problems, not to justify approval.
- evidence_independent=True: same reused `EvidenceAssessment` rows, not
  re-fetched from the LLM's own memory.
- model_independent computed FOR REAL per call, not hardcoded: `True` only
  if no earlier `LLMGenerationRecord` in this project used the same
  `model_id` for a `hypothesis`/`strategy` task; in this environment
  (single configured provider) that is essentially always `False`, and
  `shared_model_risk` is recorded accordingly, honestly.

This adapter can never self-approve a design: `meta_review.
synthesize_meta_review` (unmodified) already requires EVERY reviewer's
recommendation to be in `{approve_for_planning, approve_for_build}` before
a candidate enters `recommended_candidates`, and any reviewer's open
blocking critical finding blocks the whole case regardless of the others -
adding this reviewer can only add scrutiny, never bypass it.
"""
from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from harness.engineering_design.models import CandidateDesign
from harness.ids import new_id, now
from harness.llm_generation.client import StructuredGenerationClient
from harness.llm_generation.models import LLMGenerationRecord
from harness.llm_generation.service import record_generation
from harness.scientific_evaluation.critic import RUBRIC_VERSION, _ReviewCtx  # noqa: F401 - the same context builder, not a fork
from harness.scientific_evaluation.models import (
    CriticFinding,
    DeterministicCheckResult,
    EvaluationCase,
    EvidenceAssessment,
    HUMAN_DECISIONS,
    ModelEvaluationRecord,
    ScientificClaim,
    ScientificReview,
)

PROMPT_TEMPLATE_ID = "scientific_critic_review_v1"
PROMPT_TEMPLATE_VERSION = "1"
OUTPUT_SCHEMA_VERSION = "1"

_RECOMMENDATION_MAP = {
    "approve": "approve_for_planning", "approve_for_planning": "approve_for_planning", "approve_for_build": "approve_for_build",
    "approve_with_conditions": "approve_for_planning", "revise": "revise", "reject": "reject",
    "insufficient_evidence": "request_more_evidence", "human_expert_required": "hold",
}

_SYSTEM_PROMPT = (
    "You are an INDEPENDENT scientific critic reviewing a synthetic-biology engineering candidate design. "
    "Your job is to find problems, gaps, and unsupported claims - not to justify approval. You are given only "
    "the candidate's formal claims, evidence assessments, model records, and deterministic check results - never "
    "the designer's private reasoning. You must NOT approve a design yourself (only a human can); you may only "
    "recommend. You must NOT invent citations, DOIs, or numeric results, and must NOT treat majority agreement as "
    "proof - a single well-founded critical finding outweighs unanimous optimism. "
    "Output ONLY a single JSON object: "
    '{"critical_findings": [str, ...], "major_findings": [str, ...], "minor_findings": [str, ...], '
    '"unsupported_claims": [str, ...], "evidence_gaps": [str, ...], "biological_risks": [str, ...], '
    '"engineering_risks": [str, ...], "model_use_risks": [str, ...], "validation_gaps": [str, ...], '
    '"alternative_explanations": [str, ...], "required_revisions": [str, ...], '
    '"recommendation": one of ["approve", "approve_with_conditions", "revise", "reject", "insufficient_evidence", "human_expert_required"]}'
)


def _validate_draft(draft: dict[str, Any]) -> list[str]:
    errors = []
    if draft.get("recommendation") not in _RECOMMENDATION_MAP:
        errors.append(f"recommendation must be one of {list(_RECOMMENDATION_MAP)}")
    list_fields = (
        "critical_findings", "major_findings", "minor_findings", "unsupported_claims", "evidence_gaps",
        "biological_risks", "engineering_risks", "model_use_risks", "validation_gaps", "alternative_explanations", "required_revisions",
    )
    for f in list_fields:
        if f in draft and not isinstance(draft[f], list):
            errors.append(f"{f} must be a list")
    return errors


def _compute_shared_model_risk(session: Session, *, model_id: str) -> bool:
    prior = session.execute(
        select(LLMGenerationRecord.generation_id).where(
            LLMGenerationRecord.task_type.in_(("hypothesis", "strategy")), LLMGenerationRecord.model_id == model_id,
        )
    ).first()
    # `LLMGenerationRecord` has no project_id column (it is process-wide
    # provenance, not project-scoped) - conservatively, ANY prior use of
    # this model_id for generation anywhere counts as shared risk, since a
    # single configured provider in this environment means "different
    # project" is not evidence of a truly independent model/vendor.
    return prior is not None


def run_llm_critic_review(
    session: Session, *, case: EvaluationCase, candidate: CandidateDesign, claims: list[ScientificClaim],
    evidence: list[EvidenceAssessment], models: list[ModelEvaluationRecord], deterministic: list[DeterministicCheckResult],
    actor_id: str, client: StructuredGenerationClient | None = None,
) -> ScientificReview | None:
    """Returns `None` (never a fabricated review) if the LLM is
    unavailable or every schema-retry attempt failed - the caller's
    deterministic critics still ran and remain fully decisive."""
    client = client or StructuredGenerationClient()
    claim_summaries = "; ".join(f"[{c.claim_id}] {c.claim_type}: {c.claim_text}" for c in claims[:15]) or "(no formal claims extracted)"
    evidence_summary = "; ".join(f"{a.claim_id}: overall_strength={a.overall_strength}, condition_match={a.condition_match}" for a in evidence[:15]) or "(no evidence assessments)"
    model_summary = "; ".join(f"{m.adapter_name}: run_status={m.run_status}" for m in models) or "(no model records)"
    det_summary = "; ".join(f"{d.rule_id}: {d.status}" for d in deterministic) or "(no deterministic check results)"
    user_prompt = (
        f"Candidate design {candidate.design_id} (portfolio_role={candidate.portfolio_role}).\n"
        f"Formal claims: {claim_summaries}\nEvidence assessments: {evidence_summary}\n"
        f"Model/tool records: {model_summary}\nDeterministic checks: {det_summary}\n"
        "Review this candidate now, as the JSON object described in your instructions."
    )
    attempts, health = client.generate(system_prompt=_SYSTEM_PROMPT, user_prompt=user_prompt, max_tokens=9000)
    last = attempts[-1]

    fallback_used = True
    draft: dict[str, Any] | None = None
    if last.validation_status == "valid" and isinstance(last.parsed, dict) and not _validate_draft(last.parsed):
        draft = last.parsed
        fallback_used = False

    from harness.engineering_design.models import EngineeringDesignProject

    design_proj = session.get(EngineeringDesignProject, case.design_project_id)
    project_id = design_proj.project_id if design_proj is not None else case.design_project_id

    shared_model_risk = _compute_shared_model_risk(session, model_id=health.model) if health.available else False
    record = record_generation(
        session, project_id=project_id, task_type="critic", health=health, attempts=attempts,
        prompt_template_id=PROMPT_TEMPLATE_ID, prompt_template_version=PROMPT_TEMPLATE_VERSION,
        input_refs={"evaluation_id": case.evaluation_id, "design_id": candidate.design_id}, output_schema_version=OUTPUT_SCHEMA_VERSION,
        shared_model_risk=shared_model_risk, fallback_used=fallback_used, actor_id=actor_id,
    )
    if draft is None:
        return None  # purely additive - no review recorded, deterministic critics remain decisive

    ts = now()
    review_id = new_id("SREV")
    finding_specs: list[tuple[str, str, list[str]]] = [
        ("critical", "critical_findings", draft.get("critical_findings", [])),
        ("major", "major_findings", draft.get("major_findings", [])),
        ("minor", "minor_findings", draft.get("minor_findings", [])),
    ]
    finding_rows = []
    for severity, _key, texts in finding_specs:
        for text in texts:
            finding_rows.append(
                CriticFinding(
                    finding_id=new_id("CFIND"), review_id=review_id, design_reference=candidate.design_id,
                    category="llm_flagged", severity=severity, claim_reference=None, finding=str(text),
                    why_it_matters="flagged by the independent LLM critic - see review.limitations for shared_model_risk context",
                    supporting_evidence=[], contradictory_evidence=[], alternative_explanations=list(draft.get("alternative_explanations", [])),
                    falsification_condition="", required_action="", blocking=(severity == "critical"), resolvable=True,
                    status="open", created_at=ts,
                )
            )

    recommendation = _RECOMMENDATION_MAP[draft["recommendation"]]
    review = ScientificReview(
        review_id=review_id, evaluation_id=case.evaluation_id, design_reference=candidate.design_id,
        design_version=candidate.design_version, reviewer_id=f"critic:llm_critic:{RUBRIC_VERSION}", reviewer_type="llm_critic",
        model_provider_and_model=f"{health.provider}/{health.model}", shared_model_risk=shared_model_risk,
        independence_flags={"context_independent": True, "rubric_independent": True, "evidence_independent": True, "model_independent": not shared_model_risk},
        rubric_version=RUBRIC_VERSION,
        input_snapshot_reference={"claim_ids": [c.claim_id for c in claims], "evidence_assessment_ids": [a.assessment_id for a in evidence], "model_record_ids": [m.record_id for m in models], "deterministic_check_ids": [d.check_id for d in deterministic]},
        deterministic_results=[d.check_id for d in deterministic], evidence_assessments=[a.assessment_id for a in evidence],
        model_records=[m.record_id for m in models], findings=[r.finding_id for r in finding_rows],
        major_concerns=list(draft.get("major_findings", [])), minor_concerns=list(draft.get("minor_findings", [])),
        unsupported_claims=list(draft.get("unsupported_claims", [])), missing_controls=list(draft.get("evidence_gaps", [])),
        alternative_explanations=list(draft.get("alternative_explanations", [])), required_revisions=list(draft.get("required_revisions", [])),
        recommendation=recommendation, confidence_class="not_calibrated",
        confidence_basis=f"live LLM critic ({health.provider}/{health.model}); generation_id={record.generation_id}",
        limitations=[
            f"shared_model_risk={shared_model_risk}: this critic and the project's generation adapters may share the same underlying model/provider - independence is NOT claimed to be fully established",
            "LLM-drafted findings are candidates for human review, not verified facts",
        ],
        created_at=ts,
    )
    if recommendation not in HUMAN_DECISIONS:
        raise ValueError(f"mapped recommendation {recommendation!r} is not in HUMAN_DECISIONS")
    session.add(review)
    session.flush()
    for row in finding_rows:
        session.add(row)
    session.flush()
    return review

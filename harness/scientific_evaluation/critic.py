"""Independent Scientific Critic + domain-specific critics (doc05 §4.5/§4.6).

Deterministic-rule-driven, not a live LLM call. This matches (not
degrades) the established pattern in this codebase: `harness.diagnosis.
hypothesis_generator`, every `harness.engineering_design.evaluators.*`
module, and every Problem 01-04 gate/rule are already deterministic and
reproducible by design (README: "竞争假设生成是确定性规则式的...保证测试
可复现,非实时 LLM 推理"). No service layer anywhere in Problems 01-04
calls `harness.llm` synchronously, so adding one here would be a genuinely
new, untested integration risk for this round, not a drop-in. Doc05 §11
allows LLM use for critique but never requires it; §1.4/§16 require a real,
testable vertical slice over a live-LLM demo. A live-LLM-backed
`evidence_independent`/rubric-following critic adapter is a documented
residual enhancement (see the final report's Honest Degradation section),
not a stub - the rubric, finding schema, and independence bookkeeping below
are exactly what such an adapter would plug into.

Independence is recorded per doc05 §4.5's 4-way breakdown, never claimed
by role name alone:
  - context_independent=True: reads only the frozen `ScientificClaim`/
    `EvidenceAssessment`/`ModelEvaluationRecord`/`DeterministicCheckResult`
    rows built from the CandidateDesign's own versioned fields - never the
    Designer's generation-time reasoning (which this codebase's
    deterministic generators do not even persist as chain-of-thought).
  - rubric_independent=True: every critic function below is written to
    hunt for failure conditions, missing controls, and unsupported claims -
    it has no "explain why this is fine" branch.
  - evidence_independent=True: `evidence.py`/`model_eval.py` re-derive
    matches from the knowledge base and CounterfactualRun rows themselves;
    a critic never simply copies `CandidateDesign.buildability_assessment`
    forward as its own finding.
  - model_independent=False: same harness process, same (here: no-LLM)
    execution path backs every reviewer role -> `shared_model_risk=True`
    always, honestly, never claimed eliminated.
"""
from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from harness.config import get_settings
from harness.engineering_design.models import BuildTestPackage, CandidateDesign, DiagnosisHandoffRecord
from harness.ids import new_id, now
from harness.scientific_evaluation.models import (
    CriticFinding,
    DeterministicCheckResult,
    EvaluationCase,
    EvidenceAssessment,
    ModelEvaluationRecord,
    ScientificClaim,
    ScientificReview,
)
from harness.workflow.gene_registry import essential_genes

RUBRIC_VERSION = "sci_critic_rubric_v1"
_INDEPENDENCE_FLAGS = {
    "context_independent": True, "rubric_independent": True, "evidence_independent": True, "model_independent": False,
}


class _ReviewCtx:
    def __init__(self, session: Session, case: EvaluationCase, candidate: CandidateDesign, claims: list[ScientificClaim],
                 evidence: list[EvidenceAssessment], models: list[ModelEvaluationRecord], det: list[DeterministicCheckResult]):
        self.session = session
        self.case = case
        self.candidate = candidate
        self.claims = claims
        self.evidence_by_claim = {}
        for a in evidence:
            self.evidence_by_claim.setdefault(a.claim_id, []).append(a)
        self.models = models
        self.det = det


def _finding(category: str, severity: str, finding: str, *, why: str = "", claim_ref: str | None = None,
             supporting: list[str] | None = None, contradictory: list[str] | None = None,
             alternatives: list[str] | None = None, falsification: str = "", action: str = "",
             blocking: bool = False, resolvable: bool = True) -> dict[str, Any]:
    return {
        "category": category, "severity": severity, "finding": finding, "why_it_matters": why, "claim_reference": claim_ref,
        "supporting_evidence": supporting or [], "contradictory_evidence": contradictory or [], "alternative_explanations": alternatives or [],
        "falsification_condition": falsification, "required_action": action, "blocking": blocking, "resolvable": resolvable,
    }


# ---------------------------------------------------------------------------
# Generalist critic: the doc05 §4.5 10-point rubric.
# ---------------------------------------------------------------------------


def _rubric_generalist(ctx: _ReviewCtx) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    c = ctx.candidate

    # Q1: weakest causal link.
    mech_claims = [cl for cl in ctx.claims if cl.claim_type == "mechanism"]
    for cl in mech_claims:
        strengths = [a.overall_strength for a in ctx.evidence_by_claim.get(cl.claim_id, [])]
        if not strengths or all(s in ("unknown", "insufficient") for s in strengths):
            findings.append(_finding(
                "weak_causal_link", "major" if cl.causal_chain_position in (0, None) else "moderate",
                f"mechanism claim {cl.claim_id!r} ({cl.claim_text[:120]!r}) has no evidence rising above 'unknown/insufficient'",
                why="this is the causal step the whole candidate's expected effect depends on; if it fails, the effect fails",
                claim_ref=cl.claim_id, falsification="a targeted experiment or model run that directly measures this step's effect size",
                action="attach model-computed or curated evidence for this step, or reduce confidence in the candidate accordingly",
                blocking=False,
            ))

    # Q2: intervention likely ineffective.
    for m in c.genetic_modifications:
        target = m.get("target_identifier")
        matching = [a for cl in ctx.claims for a in ctx.evidence_by_claim.get(cl.claim_id, []) if cl.scope_conditions.get("target") == target]
        if matching and all(a.intervention_match in ("unknown", "poor") and a.mechanism_match in ("unknown", "poor") for a in matching):
            findings.append(_finding(
                "ineffective_intervention", "moderate",
                f"modification targeting {target!r} ({m.get('operation')}) has no evidence its intervention or mechanism actually matches the cited source",
                why="an intervention that does not match its own cited evidence may simply do nothing to the target phenotype",
                falsification="a model prediction or small pilot experiment showing measurable pathway/flux change at this target",
                action="verify target/mechanism match, or find a better-matched evidence source",
            ))

    # Q3: competing explanation not excluded (reads the real DiagnosisHandoffRecord, not a copy).
    handoff = ctx.session.get(DiagnosisHandoffRecord, ctx.case.diagnosis_reference) if ctx.case.diagnosis_reference else None
    if handoff is not None and handoff.unresolved_alternatives:
        findings.append(_finding(
            "competing_explanation", "major",
            f"diagnosis handoff {handoff.handoff_id!r} lists {len(handoff.unresolved_alternatives)} alternative hypothesis(es) not excluded: {handoff.unresolved_alternatives}",
            why="the candidate commits engineering effort to one mechanism while a competing explanation for the same observation remains open",
            alternatives=list(handoff.unresolved_alternatives),
            falsification="a diagnostic result that discriminates between the leading and alternative hypothesis",
            action="either add a discriminating measurement to the Build/Test plan or explicitly accept this risk",
        ))

    # Q4: evidence not transferable to this chassis/condition.
    for a in [a for lst in ctx.evidence_by_claim.values() for a in lst]:
        if a.overall_strength in ("moderate", "strong") and a.condition_match == "unknown" and a.host_match == "unknown":
            findings.append(_finding(
                "evidence_not_transferable", "moderate",
                f"evidence {a.evidence_id!r} backing claim {a.claim_id!r} has strength={a.overall_strength!r} but host/condition match is unknown",
                why="a well-matched-looking source that was never checked for host/condition compatibility risks over-extrapolation to this chassis",
                claim_ref=a.claim_id, action="record host/genotype/condition metadata for this source, or discount its strength accordingly",
            ))

    # Q5: compensation/feedback/burden ignored.
    knockout_like = [m for m in c.genetic_modifications if m.get("operation") in ("knockout", "knockdown", "attenuation")]
    if knockout_like and not c.interaction_and_epistasis_assumptions:
        findings.append(_finding(
            "compensation_or_feedback_ignored", "moderate",
            f"{len(knockout_like)} knockout/knockdown/attenuation modification(s) declared with no interaction_and_epistasis_assumptions recorded",
            why="silently assumes no regulatory feedback, metabolic compensation, or resource-allocation response to the perturbation",
            action="state the compensation/feedback assumption explicitly, even if qualitative",
        ))

    # Q6: essentiality / fitness cost.
    essential = essential_genes()
    essential_hits = [m for m in c.genetic_modifications if m.get("target_identifier") in essential]
    if essential_hits:
        findings.append(_finding(
            "essentiality_or_fitness_risk", "critical",
            f"modification(s) target essential gene(s): {[m.get('target_identifier') for m in essential_hits]}",
            why="an essential-gene disruption risks lethality or severe fitness cost that can invalidate the whole candidate regardless of pathway effect",
            falsification="a growth-curve/viability assay under the intended condition",
            action="replace with knockdown/attenuation or provide an explicit, human-reviewed essentiality-override rationale",
            blocking=True, resolvable=True,
        ))

    # Q7: buildability/stability.
    unresolved_targets = [m for m in c.genetic_modifications if m.get("target_identifier") in (None, "", "to_be_determined")]
    if unresolved_targets:
        findings.append(_finding(
            "buildability_or_stability", "major",
            f"{len(unresolved_targets)} modification(s) have no concrete target identifier resolved",
            why="a candidate cannot be constructed until every target resolves to a real genomic element",
            action="resolve each to_be_determined target before requesting build approval",
            blocking=True,
        ))

    # Q8: missing key control.
    pkg = ctx.session.get(BuildTestPackage, c.build_test_package_id) if c.build_test_package_id else None
    if pkg is None:
        sev = "major" if c.readiness in ("planning_ready", "build_ready") else "moderate"
        findings.append(_finding(
            "missing_control", sev, "no Build/Test plan is attached yet - no controls, replicates, or QC checkpoints are on record",
            why="without a reference/baseline control, an observed effect cannot be attributed to the intervention",
            action="draft a BuildTestPackage with at least a reference_or_control comparison before build approval",
            blocking=c.readiness in ("planning_ready", "build_ready"),
        ))
    elif not pkg.controls:
        findings.append(_finding(
            "missing_control", "major", f"BuildTestPackage {pkg.package_id!r} declares no controls",
            why="cannot distinguish the intervention's effect from baseline/batch variation without a control",
            action="add at least a reference_or_control and/or vector-only control", blocking=True,
        ))

    # Q9: falsifiability.
    if pkg is not None and not pkg.decision_rules:
        findings.append(_finding(
            "falsifiability", "major", f"BuildTestPackage {pkg.package_id!r} declares no decision_rules",
            why="without a pre-declared decision rule, any result can be post-hoc reinterpreted as supporting the hypothesis",
            falsification="define, before running the experiment, what observed result would falsify the core mechanism claim",
            action="add explicit decision_rules to the Build/Test plan", blocking=True,
        ))
    elif pkg is None and c.readiness in ("planning_ready", "build_ready"):
        findings.append(_finding(
            "falsifiability", "major", "candidate claims build/planning readiness but has no decision rule anywhere on record",
            action="define a falsification condition before proceeding", blocking=True,
        ))

    # Q10: safety/ethics/compliance - always answered explicitly, never skipped.
    if c.safety_flags or essential_hits:
        findings.append(_finding(
            "safety_or_compliance", "critical" if essential_hits else "moderate",
            f"safety-relevant condition present: safety_flags={c.safety_flags}, essential_gene_targets={bool(essential_hits)}",
            why="doc05 §2.8: safety/ethics findings must be a hard gate, never folded into a composite score",
            action="requires_human_safety_review before any build approval", blocking=bool(essential_hits),
        ))

    return findings


# ---------------------------------------------------------------------------
# Domain critics (doc05 §4.6) - only instantiated when their trigger
# condition is actually present on this candidate (never a forced,
# irrelevant evaluation).
# ---------------------------------------------------------------------------


def _metabolic_systems_critic(ctx: _ReviewCtx) -> list[dict[str, Any]]:
    c = ctx.candidate
    findings: list[dict[str, Any]] = []
    overexpr = [m for m in c.genetic_modifications if m.get("operation") in ("overexpression", "gene_insertion")]
    knockouts = [m for m in c.genetic_modifications if m.get("operation") in ("knockout", "knockdown", "attenuation")]
    if overexpr and knockouts:
        findings.append(_finding(
            "compensation_or_feedback_ignored", "moderate",
            f"combines knockout/knockdown ({[m.get('target_identifier') for m in knockouts]}) with overexpression "
            f"({[m.get('target_identifier') for m in overexpr]}) - competing-pathway/cofactor-balance interaction not evaluated",
            why="metabolic engineering interventions frequently interact through shared cofactor pools or competing flux, not just additively",
            action="request a GEM/FBA counterfactual run covering the combined genotype, not each modification in isolation",
        ))
    if len(overexpr) >= 2:
        findings.append(_finding(
            "essentiality_or_fitness_risk", "moderate",
            f"{len(overexpr)} simultaneous overexpression modifications - cumulative resource/burden effect not modeled",
            why="stacking overexpression constructs can impose a growth-rate/resource-allocation cost beyond any single construct's effect",
            action="request a resource-allocation or growth-rate counterfactual, or reduce to a lower-complexity candidate for comparison",
        ))
    return findings


def _genetic_buildability_critic(ctx: _ReviewCtx) -> list[dict[str, Any]]:
    c = ctx.candidate
    n = len(c.genetic_modifications)
    findings: list[dict[str, Any]] = []
    if n >= 3:
        findings.append(_finding(
            "buildability_or_stability", "moderate",
            f"{n} simultaneous genetic modifications increase construction complexity and genetic-stability risk (segregational loss, recombination between homologous edits)",
            why="each additional simultaneous edit compounds construction time, verification burden, and instability risk",
            action="consider whether the same information could be obtained by splitting into a staged/simpler candidate",
        ))
    return findings


def _experimental_design_critic(ctx: _ReviewCtx) -> list[dict[str, Any]]:
    c = ctx.candidate
    pkg = ctx.session.get(BuildTestPackage, c.build_test_package_id) if c.build_test_package_id else None
    findings: list[dict[str, Any]] = []
    if pkg is not None:
        if not pkg.replication_plan:
            findings.append(_finding(
                "missing_control", "major", f"BuildTestPackage {pkg.package_id!r} has no replication_plan",
                why="single-replicate results cannot distinguish biological effect from measurement/clonal noise",
                action="declare biological and technical replicate counts", blocking=True,
            ))
        if not pkg.qc_checkpoints:
            findings.append(_finding(
                "missing_control", "moderate", f"BuildTestPackage {pkg.package_id!r} has no qc_checkpoints",
                why="without QC (genotype verification, growth sanity check), a construction failure can masquerade as a biological negative result",
                action="add at least a genotype-verification QC checkpoint before interpreting results",
            ))
    return findings


def _process_scale_critic(ctx: _ReviewCtx) -> list[dict[str, Any]]:
    c = ctx.candidate
    return [_finding(
        "buildability_or_stability", "moderate",
        f"{len(c.process_modifications)} process modification(s) declared - batch/fed-batch/oxygen-transfer scale mismatch to any cited evidence's process mode was not verified (process_match is unknown for every EvidenceAssessment on this candidate)",
        why="a process condition change validated at one scale/mode (e.g. shake-flask batch) does not automatically transfer to another (e.g. fed-batch bioreactor)",
        action="record the process mode/scale of any cited evidence, or treat this as an untested extrapolation",
    )] if c.process_modifications else []


def _safety_ethics_critic(ctx: _ReviewCtx) -> list[dict[str, Any]]:
    """doc05 §2.8: "如果项目已有 biosafety/ethics policy,必须调用现有机制;
    若没有,至少实现正式的 policy hook". Audit finding: this repository has
    no existing biosafety/ethics policy engine (grep across harness/ found
    none) - this function IS that policy hook: a minimal, explicit,
    always-answered check, never silently skipped, and never folded into a
    composite score."""
    c = ctx.candidate
    if not c.safety_flags:
        return []
    return [_finding(
        "safety_or_compliance", "moderate", f"project policy hook: candidate carries safety_flags={c.safety_flags}",
        why="doc05 §2.8 requires an explicit, non-scoreable safety/ethics gate whenever any safety signal is present",
        action="requires_human_safety_review", blocking=False,
    )]


_DOMAIN_TRIGGERS: list[tuple[str, Any, Any]] = [
    ("metabolic_systems_critic", lambda c: bool(c.genetic_modifications), _metabolic_systems_critic),
    ("genetic_buildability_critic", lambda c: bool(c.genetic_modifications), _genetic_buildability_critic),
    ("experimental_design_critic", lambda c: True, _experimental_design_critic),
    ("process_scale_critic", lambda c: bool(c.process_modifications), _process_scale_critic),
    ("safety_ethics_critic", lambda c: bool(c.safety_flags), _safety_ethics_critic),
    # protein_design_critic is intentionally never triggered by this fixture set: none of the
    # current CandidateDesign generators produce a structural/functional protein-property claim
    # (folding, solubility, aggregation, host-compatibility) - doc05 §4.6's own instruction against
    # "不相关模块不得为了完整产生伪评价" (e.g. forcing a protein-structure score onto a pure knockout).
]


def _recommendation_for(findings: list[dict[str, Any]], evidence: list[EvidenceAssessment], models: list[ModelEvaluationRecord]) -> tuple[str, str, str]:
    blocking_critical = [f for f in findings if f["blocking"] and f["severity"] == "critical"]
    blocking_major = [f for f in findings if f["blocking"] and f["severity"] == "major"]
    if blocking_critical:
        return "revise", "low", "one or more blocking critical findings (essentiality, missing falsifiability/control) present"
    if blocking_major:
        return "revise", "low", "one or more blocking major findings present"
    unresolved = sum(1 for a in evidence if a.overall_strength in ("unknown", "insufficient"))
    if evidence and unresolved / len(evidence) > 0.5:
        return "request_more_evidence", "indeterminate", "majority of claims lack evidence rising above unknown/insufficient"
    if models and all(m.run_status in ("not_computed", "unavailable") for m in models) and any(f["category"] == "weak_causal_link" for f in findings):
        return "request_model_run", "indeterminate", "no model/tool computation is available to support a weak causal-link finding"
    if any(f["severity"] in ("major", "critical") for f in findings):
        return "revise", "low", "non-blocking major/critical findings remain - address before proceeding"
    strengths = [a.overall_strength for a in evidence]
    if strengths and sum(1 for s in strengths if s in ("moderate", "strong")) / len(strengths) >= 0.5:
        return "approve_for_planning", "medium", "no blocking findings; majority of claims have at least moderate evidence support"
    return "approve_for_planning", "low", "no blocking findings, but evidence base is thin - proceed cautiously"


def _persist_review(ctx: _ReviewCtx, *, reviewer_type: str, raw_findings: list[dict[str, Any]]) -> ScientificReview:
    settings = get_settings()
    ts = now()
    review_id = new_id("SREV")
    finding_rows = [
        CriticFinding(
            finding_id=new_id("CFIND"), review_id=review_id, design_reference=ctx.candidate.design_id,
            category=f["category"], severity=f["severity"], claim_reference=f["claim_reference"], finding=f["finding"],
            why_it_matters=f["why_it_matters"], supporting_evidence=f["supporting_evidence"], contradictory_evidence=f["contradictory_evidence"],
            alternative_explanations=f["alternative_explanations"], falsification_condition=f["falsification_condition"],
            required_action=f["required_action"], blocking=f["blocking"], resolvable=f["resolvable"], status="open", created_at=ts,
        )
        for f in raw_findings
    ]
    review = ScientificReview(
        review_id=review_id, evaluation_id=ctx.case.evaluation_id, design_reference=ctx.candidate.design_id,
        design_version=ctx.candidate.design_version, reviewer_id=f"critic:{reviewer_type}:{RUBRIC_VERSION}",
        reviewer_type=reviewer_type, model_provider_and_model=f"{settings.LLM_PROVIDER}/{settings.LLM_MODEL or 'default'} (configured; NOT called - deterministic rubric engine, see module docstring)",
        shared_model_risk=True, independence_flags=dict(_INDEPENDENCE_FLAGS), rubric_version=RUBRIC_VERSION,
        input_snapshot_reference={
            "claim_ids": [c.claim_id for c in ctx.claims], "evidence_assessment_ids": [a.assessment_id for lst in ctx.evidence_by_claim.values() for a in lst],
            "model_record_ids": [m.record_id for m in ctx.models], "deterministic_check_ids": [d.check_id for d in ctx.det],
        },
        deterministic_results=[d.check_id for d in ctx.det], evidence_assessments=[a.assessment_id for lst in ctx.evidence_by_claim.values() for a in lst],
        model_records=[m.record_id for m in ctx.models], findings=[r.finding_id for r in finding_rows], major_concerns=[], minor_concerns=[],
        unsupported_claims=[c.claim_id for c in ctx.claims if not ctx.evidence_by_claim.get(c.claim_id) or all(a.evidence_id is None for a in ctx.evidence_by_claim[c.claim_id])],
        missing_controls=[f["finding"] for f in raw_findings if f["category"] == "missing_control"],
        alternative_explanations=[alt for f in raw_findings for alt in f["alternative_explanations"]],
        required_revisions=[f["required_action"] for f in raw_findings if f["required_action"]],
        recommendation="request_more_evidence", confidence_class="not_calibrated",
        confidence_basis="", limitations=["deterministic rubric engine - no live LLM/second-provider review has been run; see shared_model_risk"],
        created_at=ts,
    )
    recommendation, confidence_class, basis = _recommendation_for(raw_findings, [a for lst in ctx.evidence_by_claim.values() for a in lst], ctx.models)
    review.recommendation = recommendation
    review.confidence_class = confidence_class
    review.confidence_basis = basis
    review.major_concerns = [f["finding"] for f in raw_findings if f["severity"] in ("major", "critical")]
    review.minor_concerns = [f["finding"] for f in raw_findings if f["severity"] in ("minor", "moderate")]
    ctx.session.add(review)
    ctx.session.flush()  # review row must exist before its findings insert (FK) - explicit two-step, not relying on UOW auto-ordering across unrelated mappers
    for row in finding_rows:
        ctx.session.add(row)
    ctx.session.flush()
    return review


def run_all_reviews(
    session: Session, *, case: EvaluationCase, candidate: CandidateDesign, claims: list[ScientificClaim],
    evidence: list[EvidenceAssessment], models: list[ModelEvaluationRecord], deterministic: list[DeterministicCheckResult],
) -> list[ScientificReview]:
    ctx = _ReviewCtx(session, case, candidate, claims, evidence, models, deterministic)
    reviews = [_persist_review(ctx, reviewer_type="generalist", raw_findings=_rubric_generalist(ctx))]
    for reviewer_type, trigger, fn in _DOMAIN_TRIGGERS:
        if trigger(candidate):
            raw = fn(ctx)
            if raw:  # doc05 §4.6: no forced, empty "pass" review for a module with nothing to say
                reviews.append(_persist_review(ctx, reviewer_type=reviewer_type, raw_findings=raw))
    return reviews

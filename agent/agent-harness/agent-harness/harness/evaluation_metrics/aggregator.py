"""260718 设计文档 §7 (验证方式) metric computation.

Every `compute_*` function returns the same honesty-preserving shape
`harness.golden_set.metrics._metric()` established: `{value, numerator,
denominator, applicable}` - `applicable=False` (never a fabricated 0 or 1)
when nothing in scope could produce a denominator. These are portfolio/
project-level rollups computed on demand from real `engineering_design` rows
- nothing here is a second, parallel record of what the pipeline already
persisted.

Doc §7 explicitly separates "过程层" (grounding, coverage), "能力层"
(screening, novelty, consistency - consistency lives in
`consistency_sampler.py`, not here) and marks 复现率 as a sanity check only,
never the primary metric - `compute_all_metrics` tags every entry with its
layer so a caller (the API/frontend) can render that structure directly
instead of re-deriving it.
"""
from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from harness.engineering_design.evaluators.evidence import _tier_for
from harness.engineering_design.memory_integration import modification_signature
from harness.engineering_design.models import (
    STRATEGY_CLASSES,
    CandidateDesign,
    DesignEvaluation,
    EngineeringDesignProject,
    EngineeringStrategy,
)
from harness.evaluation_metrics import ddr_reference

_STRONG_TIERS = {"experimental_evidence", "model_computation", "curated_knowledge"}
_ACCEPTED_CANDIDATE_STATUSES = ("proposed", "revised", "selected", "approved_for_build", "built", "tested")


def _metric(numerator: int, denominator: int, *, note: str = "") -> dict[str, Any]:
    if denominator == 0:
        return {"value": None, "numerator": numerator, "denominator": denominator, "applicable": False, "note": note}
    return {"value": numerator / denominator, "numerator": numerator, "denominator": denominator, "applicable": True, "note": note}


def _get_project(session: Session, design_project_id: str) -> EngineeringDesignProject:
    proj = session.get(EngineeringDesignProject, design_project_id)
    if proj is None:
        raise ValueError(f"no such design project: {design_project_id}")
    return proj


def _links_grounded(links: list[dict[str, Any]]) -> bool:
    return any(_tier_for(link) in _STRONG_TIERS for link in links)


# ---------------------------------------------------------------------------
# 过程层: 接地率
# ---------------------------------------------------------------------------


def compute_grounding_rate(session: Session, design_project_id: str) -> dict[str, Any]:
    """Every claim (a strategy, or a candidate's genetic modification when
    it has no per-modification links) is one unit; grounded = at least one
    evidence link rises to experimental_evidence/model_computation/
    curated_knowledge (harness.engineering_design.evaluators.evidence's own
    "strong" tier set) - never counting general_biological_knowledge/
    expert_or_llm_judgment/unknown as grounding."""
    _get_project(session, design_project_id)

    strategies = session.execute(
        select(EngineeringStrategy).where(EngineeringStrategy.design_project_id == design_project_id)
    ).scalars().all()
    candidates = session.execute(
        select(CandidateDesign).where(CandidateDesign.design_project_id == design_project_id)
    ).scalars().all()

    total = 0
    grounded = 0
    for s in strategies:
        total += 1
        if _links_grounded(s.evidence_links):
            grounded += 1
    for c in candidates:
        mods = c.genetic_modifications or []
        claims = [m.get("evidence_links", []) for m in mods] or [c.evidence_links]
        for links in claims:
            total += 1
            if _links_grounded(links):
                grounded += 1

    return _metric(grounded, total, note="claims = strategies + candidate genetic modifications (or the candidate itself when it has no modifications)")


# ---------------------------------------------------------------------------
# 过程层: 覆盖完备
# ---------------------------------------------------------------------------


def compute_coverage_completeness(session: Session, design_project_id: str) -> dict[str, Any]:
    """A strategy_class counts as "covered" whether the generator produced a
    strategy for it OR explicitly recorded why it does not apply
    (`EngineeringStrategy.excluded_strategy_reasons`) - only a class with
    neither is a genuine gap (doc §7: "是否系统过完所有分支点 × 设计动作")."""
    _get_project(session, design_project_id)

    strategies = session.execute(
        select(EngineeringStrategy).where(EngineeringStrategy.design_project_id == design_project_id)
    ).scalars().all()

    generated_classes = {s.strategy_class for s in strategies}
    excluded_classes = {e.get("strategy_class") for s in strategies for e in (s.excluded_strategy_reasons or [])}
    excluded_reason_by_class = {
        e.get("strategy_class"): e.get("reason", "") for s in strategies for e in (s.excluded_strategy_reasons or [])
    }

    if not strategies:
        result = _metric(0, len(STRATEGY_CLASSES), note="no strategies generated yet for this design project")
        result["coverage_by_class"] = [{"strategy_class": c, "status": "missing", "reason": ""} for c in STRATEGY_CLASSES]
        return result

    covered_or_excluded = generated_classes | excluded_classes
    result = _metric(len(covered_or_excluded), len(STRATEGY_CLASSES))
    result["coverage_by_class"] = [
        {
            "strategy_class": c,
            "status": "covered" if c in generated_classes else ("excluded" if c in excluded_classes else "missing"),
            "reason": excluded_reason_by_class.get(c, ""),
        }
        for c in STRATEGY_CLASSES
    ]
    return result


# ---------------------------------------------------------------------------
# 能力层: 筛选能力
# ---------------------------------------------------------------------------


def compute_screening_ability(session: Session, design_project_id: str) -> dict[str, Any]:
    """Agreement between the 8-evaluator suite's block/revise/reject
    decisions and risk signals computed independently here (not read back
    from the evaluators' own verdict, to avoid the circularity of "did the
    evaluator agree with itself") - weak evidence (no strong-tier link on any
    modification) or a duplicate genetic-modification signature within the
    same portfolio. Denominator = candidates this independent check flags as
    risky; numerator = how many of those the evaluator suite also caught."""
    _get_project(session, design_project_id)

    candidates = session.execute(
        select(CandidateDesign).where(CandidateDesign.design_project_id == design_project_id)
    ).scalars().all()
    if not candidates:
        return _metric(0, 0, note="no candidates generated yet for this design project")

    signatures_by_portfolio: dict[str | None, list[frozenset]] = {}
    for c in candidates:
        signatures_by_portfolio.setdefault(c.portfolio_id, []).append(modification_signature(c.genetic_modifications))

    evaluations = session.execute(
        select(DesignEvaluation).where(DesignEvaluation.design_id.in_([c.design_id for c in candidates]))
    ).scalars().all()
    latest_eval_by_design: dict[str, DesignEvaluation] = {}
    for ev in evaluations:
        current = latest_eval_by_design.get(ev.design_id)
        if current is None or ev.created_at > current.created_at:
            latest_eval_by_design[ev.design_id] = ev

    risk_flagged = 0
    caught = 0
    for c in candidates:
        mods = c.genetic_modifications or []
        claims = [m.get("evidence_links", []) for m in mods] or [c.evidence_links]
        weak_evidence = not any(_links_grounded(links) for links in claims)

        own_sig = modification_signature(c.genetic_modifications)
        siblings = signatures_by_portfolio.get(c.portfolio_id, [])
        duplicate = bool(own_sig) and siblings.count(own_sig) > 1

        if not (weak_evidence or duplicate):
            continue
        risk_flagged += 1

        ev = latest_eval_by_design.get(c.design_id)
        evaluator_caught = bool(ev) and (
            ev.recommendation in ("revise", "reject", "insufficient_evidence")
            or bool(ev.required_revisions)
            or any(f.get("blocking") for f in ev.evaluator_findings)
        )
        if evaluator_caught:
            caught += 1

    return _metric(caught, risk_flagged, note="risk signals = weak evidence tier or duplicate genetic-modification signature within the same portfolio, computed independently of the evaluator suite")


# ---------------------------------------------------------------------------
# 能力层: 合理新颖 / sanity check: 复现率
# ---------------------------------------------------------------------------


def _candidate_gene_targets(candidates: list[CandidateDesign]) -> dict[str, bool]:
    """gene (lowercased) -> whether any occurrence of it across these
    candidates is grounded (strong-tier evidence)."""
    genes: dict[str, bool] = {}
    for c in candidates:
        for m in c.genetic_modifications or []:
            if m.get("target_type") != "gene":
                continue
            gene = str(m.get("target_identifier", "")).strip().lower()
            if not gene or gene == "to_be_determined":
                continue
            grounded = _links_grounded(m.get("evidence_links", []))
            genes[gene] = genes.get(gene, False) or grounded
    return genes


def compute_reasoned_novelty(session: Session, design_project_id: str) -> dict[str, Any]:
    """`applicable=False` until the project is linked to at least one
    reference DDR (`EngineeringDesignProject.reference_ddr_ids`) - there is
    no ground truth to diff against otherwise, and this metric must never
    report a fabricated ratio (doc §7's own framing: novelty is only
    meaningful relative to a specific paper's actual design, not judged in
    the abstract)."""
    proj = _get_project(session, design_project_id)
    if not proj.reference_ddr_ids:
        return _metric(0, 0, note="design project has no reference_ddr_ids linked yet - link the source paper's DDR id(s) to compute this")

    reference_genes = ddr_reference.load_reference_targets(proj.reference_ddr_ids)
    candidates = session.execute(
        select(CandidateDesign).where(
            CandidateDesign.design_project_id == design_project_id,
            CandidateDesign.status.in_(_ACCEPTED_CANDIDATE_STATUSES),
        )
    ).scalars().all()
    candidate_genes = _candidate_gene_targets(candidates)
    if not candidate_genes:
        return _metric(0, 0, note="no gene-level candidate designs to compare against the reference yet")

    novel_grounded = [g for g, grounded in candidate_genes.items() if g not in reference_genes and grounded]
    result = _metric(len(novel_grounded), len(candidate_genes), note="share of proposed gene targets that are absent from the reference DDR(s) and evidence-grounded")
    result["novel_grounded_genes"] = sorted(novel_grounded)
    return result


def compute_reproduction_rate(session: Session, design_project_id: str) -> dict[str, Any]:
    """Sanity check only (doc §7: "复现率保留为 sanity check...不作主指标") -
    never render this as a primary metric alongside the other four."""
    proj = _get_project(session, design_project_id)
    if not proj.reference_ddr_ids:
        return _metric(0, 0, note="design project has no reference_ddr_ids linked yet")

    reference_genes = ddr_reference.load_reference_targets(proj.reference_ddr_ids)
    if not reference_genes:
        return _metric(0, 0, note="linked DDR(s) have no gene-level targets recorded")

    candidates = session.execute(
        select(CandidateDesign).where(
            CandidateDesign.design_project_id == design_project_id,
            CandidateDesign.status.in_(_ACCEPTED_CANDIDATE_STATUSES),
        )
    ).scalars().all()
    candidate_genes = set(_candidate_gene_targets(candidates))
    return _metric(len(candidate_genes & reference_genes), len(reference_genes))


# ---------------------------------------------------------------------------
# Bundle
# ---------------------------------------------------------------------------


def compute_all_metrics(session: Session, design_project_id: str) -> dict[str, Any]:
    return {
        "design_project_id": design_project_id,
        "process": {
            "grounding_rate": compute_grounding_rate(session, design_project_id),
            "coverage_completeness": compute_coverage_completeness(session, design_project_id),
        },
        "capability": {
            "screening_ability": compute_screening_ability(session, design_project_id),
            "reasoned_novelty": compute_reasoned_novelty(session, design_project_id),
        },
        "sanity_check": {
            "reproduction_rate": compute_reproduction_rate(session, design_project_id),
        },
    }

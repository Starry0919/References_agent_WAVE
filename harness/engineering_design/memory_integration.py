"""Problem 02 Memory / DBTL integration (doc04 §4.7, §6): reads real
history back out of `CandidateDesign`/`DesignOutcomeRecord` rows (and, via
those, the shared `ProjectEvent` ledger every mutation already wrote into)
before the next generation round runs - never a fresh, amnesiac restart.
"""
from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from harness.engineering_design.models import CandidateDesign, DesignOutcomeRecord, EngineeringDesignProject

_NEGATIVE_STATUSES = ("rejected",)
_NEGATIVE_FAILURE_CLASSES = (
    "assembly_failed", "transformation_failed", "assay_failed", "measurement_invalid",
    "biological_underperformance", "unexpected_tradeoff",
)


def modification_signature(genetic_modifications: list[dict[str, Any]]) -> frozenset[tuple[str, str]]:
    """Identity of a candidate's genetic content by (target, operation)
    pairs - the same key convention `harness.designs.genotype_diff` uses,
    so a candidate that is genuinely identical in content (regardless of
    prose wording) is recognized as a repeat."""
    return frozenset((m.get("target_identifier", "unknown"), m.get("operation", "unknown")) for m in genetic_modifications)


def rejected_or_failed_signatures(session: Session, *, design_project_id: str) -> dict[frozenset, list[str]]:
    """Every distinct genetic-modification signature that was previously
    `rejected` or came back with a negative `DesignOutcomeRecord.
    failure_classification` for this design project, mapped to the
    design_id(s) that produced it - used to suppress a no-new-evidence
    repeat, never to forbid revisiting a target outright."""
    signatures: dict[frozenset, list[str]] = {}

    rejected = session.execute(
        select(CandidateDesign).where(CandidateDesign.design_project_id == design_project_id, CandidateDesign.status == "rejected")
    ).scalars().all()
    for c in rejected:
        sig = modification_signature(c.genetic_modifications)
        if sig:
            signatures.setdefault(sig, []).append(c.design_id)

    candidates = session.execute(
        select(CandidateDesign).where(CandidateDesign.design_project_id == design_project_id)
    ).scalars().all()
    by_id = {c.design_id: c for c in candidates}
    outcomes = session.execute(
        select(DesignOutcomeRecord).where(DesignOutcomeRecord.design_id.in_(by_id.keys()))
    ).scalars().all() if by_id else []
    for o in outcomes:
        if o.failure_classification in _NEGATIVE_FAILURE_CLASSES and o.design_id in by_id:
            sig = modification_signature(by_id[o.design_id].genetic_modifications)
            if sig:
                signatures.setdefault(sig, []).append(o.design_id)

    return signatures


def design_lineage_history(session: Session, *, design_project_id: str) -> list[dict[str, Any]]:
    """Full version/outcome history for a design project, newest first -
    what the next generation round (or a Design Report) reads to avoid
    repeating a mistake."""
    candidates = session.execute(
        select(CandidateDesign).where(CandidateDesign.design_project_id == design_project_id).order_by(CandidateDesign.created_at.desc())
    ).scalars().all()
    by_id = {c.design_id: c for c in candidates}
    outcomes = session.execute(
        select(DesignOutcomeRecord).where(DesignOutcomeRecord.design_id.in_(by_id.keys()))
    ).scalars().all() if by_id else []
    outcomes_by_design: dict[str, list[DesignOutcomeRecord]] = {}
    for o in outcomes:
        outcomes_by_design.setdefault(o.design_id, []).append(o)

    return [
        {
            "design_id": c.design_id, "lineage_id": c.lineage_id, "design_version": c.design_version,
            "portfolio_role": c.portfolio_role, "status": c.status, "readiness": c.readiness,
            "rejection_reasons": c.rejection_reasons,
            "outcomes": [
                {"failure_classification": o.failure_classification, "residuals": o.residuals, "outcome_update": o.outcome_update}
                for o in outcomes_by_design.get(c.design_id, [])
            ],
        }
        for c in candidates
    ]

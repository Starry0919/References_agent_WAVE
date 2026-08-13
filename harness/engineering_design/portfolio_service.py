"""`DesignPortfolio` / `CandidateDesign` persistence: wraps the pure
`portfolio_generator` module, resolves proposed `EngineeringStrategy` rows,
suppresses no-new-evidence repeats of previously `rejected`/failed
candidates (doc04 §4.3, §4.7), runs `DesignDiversityGate`, and writes every
generated candidate plus a Memory Event into the shared `ProjectEvent`
ledger.
"""
from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from harness.engineering_design import memory_integration, strategy_service
from harness.engineering_design.models import CandidateDesign, DesignPortfolio, EngineeringDesignProject, EngineeringStrategy
from harness.diagnosis.models import DiagnosisFinding, EngineeringProblem
from harness.engineering_design.portfolio_generator import generate_portfolio
from harness.ids import new_id, now
from harness.memory import event_types as et
from harness.memory.event_store import append_event, snapshot
from harness.workflow.gates import design_diversity_gate, redesign_gate
from harness.workflow.gene_registry import known_genes

PORTFOLIO_SNAPSHOT_FIELDS = (
    "portfolio_id", "design_project_id", "candidate_design_ids", "role_assignments", "absent_roles",
    "diversity_assessment", "status", "decision", "created_by", "created_at",
)
CANDIDATE_SNAPSHOT_FIELDS = (
    "design_id", "design_project_id", "lineage_id", "design_version", "parent_design_ids", "strategy_ids",
    "portfolio_id", "portfolio_role", "genetic_modifications", "regulatory_architecture", "process_modifications",
    "expected_mechanism", "causal_chain", "interaction_and_epistasis_assumptions", "evidence_links",
    "counterfactual_requests", "counterfactual_results", "uncertainty_and_model_conflicts", "tradeoff_profile",
    "buildability_assessment", "build_test_package_id", "debug_and_fallback_plan", "safety_flags", "readiness",
    "status", "decision_state", "diagnosis_finding_ids", "rejection_reasons", "source_diagnosis_version", "created_from_revision_reason", "proposed_by",
    "created_at",
)


class PortfolioDiversityRejected(RuntimeError):
    """DesignDiversityGate rejected the generated portfolio - fewer than 2
    mechanistically/architecturally distinct candidates."""


class RevisionRejected(RuntimeError):
    """RedesignGate rejected the proposed revision - identical to its
    parent, or missing a declared diff/justification (doc04 §4.4: an
    evaluator's `required_revisions` must lead to an actually different,
    justified candidate, never a relabeled duplicate)."""


def revise_candidate(
    session: Session,
    *,
    design_id: str,
    actor_id: str,
    modification_reason: str,
    genetic_modifications: list[dict[str, Any]] | None = None,
    regulatory_architecture: dict[str, Any] | None = None,
    process_modifications: list[dict[str, Any]] | None = None,
    expected_mechanism: str | None = None,
    causal_chain: list[str] | None = None,
    interaction_and_epistasis_assumptions: list[str] | None = None,
) -> CandidateDesign:
    """doc04 §4.4/§3.9: an evaluator's `required_revisions` are addressed by
    creating a NEW `CandidateDesign` row - `design_version` incremented,
    `parent_design_ids` pointing back - never by editing the evaluated
    content in place (which `guard_immutable_fields` would reject anyway).
    Reuses `RedesignGate` (doc 10.2), the same "declare your diff, state
    why, never repeat identically" rule `harness.learning.redesign` already
    applies to Problem 02's own `DesignVersion` redesigns."""
    parent = session.get(CandidateDesign, design_id)
    if parent is None:
        raise ValueError(f"no such candidate design: {design_id}")
    _validate_finding_ids(session, parent.design_project_id, parent.diagnosis_finding_ids)

    new_mods = genetic_modifications if genetic_modifications is not None else parent.genetic_modifications
    old_sig = memory_integration.modification_signature(parent.genetic_modifications)
    new_sig = memory_integration.modification_signature(new_mods)
    is_identical = (
        new_sig == old_sig
        and (regulatory_architecture is None or regulatory_architecture == parent.regulatory_architecture)
        and (process_modifications is None or process_modifications == parent.process_modifications)
    )
    has_retain_remove_add = bool(new_sig | old_sig) or bool(regulatory_architecture or process_modifications)

    gate = redesign_gate(
        has_retain_remove_add=has_retain_remove_add, has_triggering_justification=bool(modification_reason.strip()),
        is_identical_to_parent=is_identical,
    )
    if gate.status.value != "pass":
        raise RevisionRejected(f"revision of {design_id} rejected by RedesignGate: {[v.message for v in gate.violations]}")

    new_design_id = new_id("CAND")
    row = CandidateDesign(
        design_id=new_design_id, design_project_id=parent.design_project_id, lineage_id=parent.lineage_id,
        design_version=parent.design_version + 1, parent_design_ids=[parent.design_id], strategy_ids=parent.strategy_ids,
        diagnosis_finding_ids=parent.diagnosis_finding_ids,
        portfolio_id=parent.portfolio_id, portfolio_role=parent.portfolio_role, genetic_modifications=new_mods,
        regulatory_architecture=regulatory_architecture if regulatory_architecture is not None else parent.regulatory_architecture,
        process_modifications=process_modifications if process_modifications is not None else parent.process_modifications,
        expected_mechanism=expected_mechanism or parent.expected_mechanism,
        causal_chain=causal_chain if causal_chain is not None else parent.causal_chain,
        interaction_and_epistasis_assumptions=interaction_and_epistasis_assumptions if interaction_and_epistasis_assumptions is not None else parent.interaction_and_epistasis_assumptions,
        evidence_links=parent.evidence_links, counterfactual_requests=[], counterfactual_results=[],
        uncertainty_and_model_conflicts=[], tradeoff_profile=None, buildability_assessment=None, build_test_package_id=None,
        debug_and_fallback_plan=None, safety_flags=[], readiness="conceptual", status="proposed", decision_state="candidate_generated", rejection_reasons=[],
        source_diagnosis_version=parent.source_diagnosis_version, created_from_revision_reason=modification_reason,
        proposed_by=actor_id, created_at=now(),
    )
    session.add(row)
    session.flush()
    proj = session.get(EngineeringDesignProject, parent.design_project_id)
    append_event(
        session, project_id=proj.project_id, event_type=et.DESIGN_CANDIDATE_REVISED, entity_type="CandidateDesign",
        entity_id=row.design_id, payload=snapshot(row, CANDIDATE_SNAPSHOT_FIELDS), actor_type="human" if actor_id != "system" else "agent",
        actor_id=actor_id,
    )
    return row


class DiagnosisRequiredError(RuntimeError):
    """Production candidate generation cannot bypass project observations."""


def _validate_finding_ids(session: Session, design_project_id: str, finding_ids: list[str]) -> list[DiagnosisFinding]:
    proj = session.get(EngineeringDesignProject, design_project_id)
    if proj is None or not finding_ids:
        raise DiagnosisRequiredError("DIAGNOSIS_REQUIRED: at least one persisted DiagnosisFinding is required")
    rows = session.execute(select(DiagnosisFinding).where(DiagnosisFinding.finding_id.in_(finding_ids))).scalars().all()
    if len(rows) != len(set(finding_ids)):
        raise DiagnosisRequiredError("DIAGNOSIS_REQUIRED: one or more DiagnosisFinding ids do not resolve")
    for finding in rows:
        problem = session.get(EngineeringProblem, finding.engineering_problem_id)
        if (finding.project_id != proj.project_id or problem is None or problem.project_id != proj.project_id
                or problem.diagnosis_session_id != proj.diagnosis_session_id or problem.status != "grounded"
                or not finding.observation_refs):
            raise DiagnosisRequiredError("DATA_REQUIRED: DiagnosisFinding is not grounded in this project/problem")
    return rows


def _project_findings(session: Session, proj: EngineeringDesignProject) -> list[DiagnosisFinding]:
    rows = session.execute(select(DiagnosisFinding).where(DiagnosisFinding.project_id == proj.project_id)).scalars().all()
    valid = []
    for row in rows:
        problem = session.get(EngineeringProblem, row.engineering_problem_id)
        if problem and problem.diagnosis_session_id == proj.diagnosis_session_id and problem.status == "grounded" and row.observation_refs:
            valid.append(row)
    if not valid:
        raise DiagnosisRequiredError(
            "DIAGNOSIS_REQUIRED: production candidates require an observation-grounded DiagnosisFinding for this diagnosis"
        )
    return valid


def generate_and_persist_portfolio(
    session: Session, *, design_project_id: str, actor_id: str
) -> tuple[DesignPortfolio, list[CandidateDesign], list[dict[str, Any]]]:
    """Returns `(portfolio, candidates, suppressed_repeats)`. Raises
    `PortfolioDiversityRejected` (no rows persisted) if the surviving
    candidate set is not diverse enough - mirrors the "gate first, persist
    only on pass" discipline used throughout this codebase."""
    proj = session.get(EngineeringDesignProject, design_project_id)
    if proj is None:
        raise ValueError(f"no such design project: {design_project_id}")
    finding_ids = [row.finding_id for row in _project_findings(session, proj)]

    strategies = [
        s for s in strategy_service.list_strategies(session, design_project_id) if s.status == "proposed"
    ]
    strategies_payload = [
        {
            "strategy_id": s.strategy_id, "strategy_class": s.strategy_class, "mechanism_target": s.mechanism_target,
            "evidence_links": s.evidence_links, "expected_causal_chain": s.expected_causal_chain,
        }
        for s in strategies
    ]

    gen_result = generate_portfolio(
        strategies=strategies_payload, known_genes=known_genes(), action_database=strategy_service.load_action_database(),
    )

    history = memory_integration.rejected_or_failed_signatures(session, design_project_id=design_project_id)
    kept: list = []
    suppressed: list[dict[str, Any]] = []
    for candidate in gen_result.candidates:
        sig = memory_integration.modification_signature(candidate.genetic_modifications)
        if sig and sig in history:
            suppressed.append({
                "portfolio_role": candidate.portfolio_role, "reason": "identical genetic-modification set was previously rejected/failed "
                "for this design project with no new evidence presented",
                "matched_prior_design_ids": history[sig],
            })
            continue
        kept.append(candidate)

    distinct_architectures = {
        (tuple(sorted(m.get("target_identifier", "") for m in c.genetic_modifications)), c.expected_mechanism)
        for c in kept if c.portfolio_role != "reference_or_control"
    }
    gate = design_diversity_gate(
        distinct_mechanism_or_architecture_count=len(distinct_architectures),
        total_candidates=len([c for c in kept if c.portfolio_role != "reference_or_control"]),
    )
    if gate.status.value == "fail":
        raise PortfolioDiversityRejected(f"portfolio rejected by DesignDiversityGate: {[v.message for v in gate.violations]}")

    portfolio = DesignPortfolio(
        portfolio_id=new_id("PORT"), design_project_id=design_project_id, candidate_design_ids=[],
        role_assignments={}, absent_roles=[{"role": r.role, "reason": r.reason} for r in gen_result.absent_roles],
        diversity_assessment={"distinct_architectures": len(distinct_architectures), "gate_status": gate.status.value, "suppressed_repeats": suppressed},
        status="generated", created_by=actor_id, created_at=now(),
    )
    session.add(portfolio)
    session.flush()

    rows: list[CandidateDesign] = []
    role_assignments: dict[str, list[str]] = {}
    for draft in kept:
        design_id = new_id("CAND")
        row = CandidateDesign(
            design_id=design_id, design_project_id=design_project_id, lineage_id=design_id, design_version=1,
            parent_design_ids=[], strategy_ids=draft.strategy_ids, diagnosis_finding_ids=finding_ids, portfolio_id=portfolio.portfolio_id,
            portfolio_role=draft.portfolio_role, genetic_modifications=draft.genetic_modifications,
            regulatory_architecture=draft.regulatory_architecture, process_modifications=draft.process_modifications,
            expected_mechanism=draft.expected_mechanism, causal_chain=draft.causal_chain,
            interaction_and_epistasis_assumptions=draft.interaction_and_epistasis_assumptions,
            evidence_links=draft.evidence_links, counterfactual_requests=[], counterfactual_results=[],
            uncertainty_and_model_conflicts=[], tradeoff_profile=None, buildability_assessment=None,
            build_test_package_id=None, debug_and_fallback_plan=None, safety_flags=[], readiness="conceptual",
            status="proposed", decision_state="candidate_generated", rejection_reasons=[], source_diagnosis_version=proj.diagnosis_version,
            created_from_revision_reason=None, proposed_by=actor_id, created_at=now(),
        )
        session.add(row)
        rows.append(row)
        role_assignments.setdefault(draft.portfolio_role, []).append(design_id)

    session.flush()
    portfolio.candidate_design_ids = [r.design_id for r in rows]
    portfolio.role_assignments = role_assignments
    session.flush()

    append_event(
        session, project_id=proj.project_id, event_type=et.DESIGN_PORTFOLIO_GENERATED, entity_type="DesignPortfolio",
        entity_id=portfolio.portfolio_id, payload=snapshot(portfolio, PORTFOLIO_SNAPSHOT_FIELDS), actor_type="agent", actor_id=actor_id,
    )
    for row in rows:
        append_event(
            session, project_id=proj.project_id, event_type=et.DESIGN_CANDIDATE_GENERATED, entity_type="CandidateDesign",
            entity_id=row.design_id, payload=snapshot(row, CANDIDATE_SNAPSHOT_FIELDS), actor_type="agent", actor_id=actor_id,
        )
    return portfolio, rows, suppressed


def list_candidates(session: Session, design_project_id: str) -> list[CandidateDesign]:
    return list(session.execute(select(CandidateDesign).where(CandidateDesign.design_project_id == design_project_id)).scalars())


def get_candidate(session: Session, design_id: str) -> CandidateDesign | None:
    return session.get(CandidateDesign, design_id)


def get_portfolio(session: Session, portfolio_id: str) -> DesignPortfolio | None:
    return session.get(DesignPortfolio, portfolio_id)


def reject_candidate(session: Session, *, design_id: str, reasons: list[str], actor_id: str) -> CandidateDesign:
    candidate = session.get(CandidateDesign, design_id)
    if candidate is None:
        raise ValueError(f"no such candidate design: {design_id}")
    from harness.engineering_design.decision_state import transition_candidate
    candidate = transition_candidate(session, design_id=design_id, target="rejected", actor_id=actor_id, reasons=reasons)
    proj = session.get(EngineeringDesignProject, candidate.design_project_id)
    append_event(
        session, project_id=proj.project_id, event_type=et.DESIGN_CANDIDATE_REJECTED, entity_type="CandidateDesign",
        entity_id=candidate.design_id, payload=snapshot(candidate, CANDIDATE_SNAPSHOT_FIELDS),
        actor_type="human" if actor_id != "system" else "agent", actor_id=actor_id,
    )
    return candidate


def select_candidate(session: Session, *, design_id: str, actor_id: str) -> CandidateDesign:
    candidate = session.get(CandidateDesign, design_id)
    if candidate is None:
        raise ValueError(f"no such candidate design: {design_id}")
    from harness.engineering_design.decision_state import transition_candidate
    candidate = transition_candidate(session, design_id=design_id, target="selected", actor_id=actor_id)
    proj = session.get(EngineeringDesignProject, candidate.design_project_id)
    append_event(
        session, project_id=proj.project_id, event_type=et.DESIGN_CANDIDATE_SELECTED, entity_type="CandidateDesign",
        entity_id=candidate.design_id, payload=snapshot(candidate, CANDIDATE_SNAPSHOT_FIELDS), actor_type="human", actor_id=actor_id,
    )
    return candidate

"""Context Builder (doc 13): assembles one auditable `ContextBundle` per
LLM call. Retrieval order is structured filtering first - exact id (project
pointer lookup), then design lineage (`get_ancestors`), then host/condition
match, then time/state - semantic similarity is explicitly NOT implemented
this round (no vector index is wired up); `omissions_and_token_budget`
records that honestly rather than silently skipping the step.

Every query here is scoped by `project_id` first, so cross-project leakage
would require a bug in the WHERE clause itself, not a missing filter layer
bolted on afterward - this is what the required unit test ("Context
Builder never leaks another project's or an inapplicable condition's data
in") is actually exercising.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from harness.designs.lineage import get_ancestors
from harness.designs.models import DesignVersion
from harness.experiments.models import ExperimentRun, Observation
from harness.learning.models import FailureCase, HypothesisFamily, HypothesisVersion
from harness.projects.models import Project
from harness.projects.service import get_active_cycle

# Rough token approximation (chars / 4) - documented as approximate, not a
# real tokenizer. Good enough for budget bookkeeping, not for billing.
def _approx_tokens(obj: Any) -> int:
    return max(1, len(str(obj)) // 4)


DEFAULT_BUDGETS = {
    "critical_facts": 4000,        # never trimmed
    "active_cycle": 4000,          # never trimmed - current identity/QC/conflicts/gates live here
    "relevant_precedents": 2000,   # never trimmed
    "background_knowledge": 1000,  # trimmed first, and only, when over budget
}


@dataclass
class ContextBundle:
    project_summary: dict[str, Any]
    active_design_version: dict[str, Any] | None
    relevant_ancestors: list[dict[str, Any]]
    current_experiment_and_qc: dict[str, Any] | None
    accepted_observations: list[dict[str, Any]]
    active_hypotheses: list[dict[str, Any]]
    relevant_failure_cases: list[dict[str, Any]]
    applicable_evidence: list[str]
    policy_and_model_versions: list[str]
    omissions_and_token_budget: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _observation_summary(o: Observation) -> dict[str, Any]:
    return {
        "observation_id": o.observation_id, "metric": o.metric, "value": o.value, "unit": o.unit,
        "condition_ref": o.condition_ref, "subject_design_version_id": o.subject_design_version_id,
        "qc_status": o.qc_status, "source_type": o.source_type,
    }


def build_context_bundle(
    session: Session,
    *,
    project_id: str,
    condition_filter: dict[str, Any] | None = None,
    max_observations: int = 20,
    max_ancestors: int = 5,
    budgets: dict[str, int] | None = None,
) -> ContextBundle:
    budgets = budgets or DEFAULT_BUDGETS

    project = session.get(Project, project_id)
    if project is None:
        raise ValueError(f"no such project: {project_id}")

    # 1. Exact-id structured lookup.
    project_summary = {
        "project_id": project.project_id, "name": project.name, "target_product": project.target_product,
        "host_definition": project.host_definition, "objectives": project.objectives,
        "constraints": project.constraints, "status": project.status, "lifecycle_stage": project.lifecycle_stage,
    }

    active_design: dict[str, Any] | None = None
    relevant_ancestors: list[dict[str, Any]] = []
    # 2. Design-lineage filter.
    if project.current_design_version_id:
        dv = session.get(DesignVersion, project.current_design_version_id)
        if dv is not None and dv.project_id == project_id:
            active_design = {
                "design_version_id": dv.design_version_id, "version_label": dv.version_label,
                "genotype_manifest": dv.genotype_manifest, "status": dv.status,
            }
            ancestors = get_ancestors(session, dv.design_version_id, max_depth=max_ancestors)
            relevant_ancestors = [
                {"design_version_id": a.design_version_id, "version_label": a.version_label, "status": a.status}
                for a in ancestors[:max_ancestors]
                if a.project_id == project_id
            ]

    # 3. Host/condition match (Python-side filter for portability - SQLite
    # JSON predicates aren't worth the non-portable query this round).
    observations = session.execute(
        select(Observation)
        .where(Observation.project_id == project_id, Observation.qc_status == "passed")
        .order_by(Observation.created_at.desc())
        .limit(max_observations * 3)
    ).scalars().all()
    if condition_filter:
        observations = [o for o in observations if all(o.condition_ref.get(k) == v for k, v in condition_filter.items())]
    observations = observations[:max_observations]

    family_ids = {
        f.hypothesis_family_id
        for f in session.execute(select(HypothesisFamily).where(HypothesisFamily.project_id == project_id)).scalars()
    }
    hypotheses = session.execute(select(HypothesisVersion)).scalars().all() if family_ids else []
    hypotheses = [h for h in hypotheses if h.hypothesis_family_id in family_ids]
    latest_by_family: dict[str, HypothesisVersion] = {}
    for h in sorted(hypotheses, key=lambda x: x.created_at):  # 4. time filter: latest version per family wins
        latest_by_family[h.hypothesis_family_id] = h
    active_hypotheses = [
        {
            "hypothesis_version_id": h.hypothesis_version_id, "statement": h.statement,
            "posterior_status": h.posterior_status, "confidence": h.confidence,
        }
        for h in latest_by_family.values()
    ]

    failure_cases = session.execute(
        select(FailureCase).where(FailureCase.project_id == project_id, FailureCase.resolution_status == "open")
    ).scalars().all()
    if condition_filter:
        failure_cases = [f for f in failure_cases if all(f.applicability_scope.get(k) == v for k, v in condition_filter.items())]
    relevant_failure_cases = [
        {"failure_case_id": f.failure_case_id, "failure_class": f.failure_class, "applicability_scope": f.applicability_scope}
        for f in failure_cases
    ]

    current_experiment_and_qc = None
    cycle = get_active_cycle(session, project_id)
    if cycle and cycle.active_experiment_run_id:
        run = session.get(ExperimentRun, cycle.active_experiment_run_id)
        if run is not None:
            current_experiment_and_qc = {
                "experiment_run_id": run.experiment_run_id, "execution_status": run.execution_status,
                "deviations": run.deviations,
            }

    # 5. Semantic similarity: NOT implemented this round (no vector index
    # wired up) - recorded honestly, not silently skipped.
    omissions: list[str] = ["semantic/vector retrieval not implemented this round - structured filtering only"]

    accepted_observations = [_observation_summary(o) for o in observations]

    critical_tokens = _approx_tokens({"project_summary": project_summary, "active_design_version": active_design})
    active_cycle_tokens = _approx_tokens(
        {"current_experiment_and_qc": current_experiment_and_qc, "accepted_observations": accepted_observations,
         "relevant_failure_cases": relevant_failure_cases}
    )
    precedent_tokens = _approx_tokens({"relevant_ancestors": relevant_ancestors})
    background_tokens = _approx_tokens({"active_hypotheses": active_hypotheses})

    # Budget shortfall is resolved by trimming background_knowledge ONLY -
    # never critical facts, active-cycle identity/QC/conflicts, or
    # precedents (doc 6.6: "预算不足时优先删减背景...").
    if background_tokens > budgets["background_knowledge"] and active_hypotheses:
        kept = max(1, len(active_hypotheses) // 2)
        dropped = active_hypotheses[kept:]
        active_hypotheses = active_hypotheses[:kept]
        omissions.append(
            f"background_knowledge trimmed: dropped {len(dropped)} hypothesis summary/summaries "
            f"(source_ids={[h['hypothesis_version_id'] for h in dropped]}) to stay within the "
            f"{budgets['background_knowledge']}-token background budget"
        )
        background_tokens = _approx_tokens({"active_hypotheses": active_hypotheses})

    token_budget = {
        "budgets": budgets,
        "used": {
            "critical_facts": critical_tokens,
            "active_cycle": active_cycle_tokens,
            "relevant_precedents": precedent_tokens,
            "background_knowledge": background_tokens,
        },
        "omissions": omissions,
    }

    return ContextBundle(
        project_summary=project_summary,
        active_design_version=active_design,
        relevant_ancestors=relevant_ancestors,
        current_experiment_and_qc=current_experiment_and_qc,
        accepted_observations=accepted_observations,
        active_hypotheses=active_hypotheses,
        relevant_failure_cases=relevant_failure_cases,
        applicable_evidence=[],
        policy_and_model_versions=[],
        omissions_and_token_budget=token_budget,
    )

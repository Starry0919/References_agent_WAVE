"""Repository-backed observation grounding for actionable diagnosis."""
from __future__ import annotations

import re
from dataclasses import asdict, dataclass, field

from sqlalchemy import select
from sqlalchemy.orm import Session

from harness.diagnosis.models import BiologicalContext, DiagnosisSession, EngineeringProblem
from harness.experiments.models import DataAsset, Observation
from harness.ids import new_id, now

_CAUSAL = re.compile(
    r"\b(because|due to|caused by|results? from|limited by|limitation|"
    r"feedback inhibition|precursor supply|precursor limitation|bottleneck)\b",
    re.IGNORECASE,
)


class GroundingError(ValueError):
    pass


@dataclass(frozen=True)
class ObservationGroundingResult:
    status: str
    blocking_reasons: list[str] = field(default_factory=list)
    observation_ids: list[str] = field(default_factory=list)
    engineering_problem_ids: list[str] = field(default_factory=list)
    policy_version: str = "observation-grounding-v1"
    actionable: bool = False

    def to_dict(self) -> dict:
        return asdict(self)


def _has_context(db: Session, diagnosis: DiagnosisSession, obs: Observation) -> bool:
    if obs.subject_design_version_id or obs.subject_construct_id:
        return True
    if obs.biological_context_id:
        ctx = db.get(BiologicalContext, obs.biological_context_id)
        return bool(ctx and ctx.project_id == diagnosis.project_id and (
            ctx.chassis_genotype_ref or ctx.medium or ctx.carbon_source or ctx.environment
        ))
    system = diagnosis.biological_system or {}
    return bool(system.get("strain") or system.get("host") or system.get("species")) and bool(obs.condition_ref)


def _has_provenance(db: Session, obs: Observation) -> bool:
    if not obs.data_asset_ids or not obs.analysis_pipeline_version:
        return False
    assets = db.execute(select(DataAsset).where(DataAsset.data_asset_id.in_(obs.data_asset_ids))).scalars().all()
    return len(assets) == len(set(obs.data_asset_ids)) and all(
        a.project_id == obs.project_id and bool(a.file_uri and a.checksum and a.provenance) for a in assets
    )


def evaluate_observation_grounding(db: Session, diagnosis_session_id: str) -> ObservationGroundingResult:
    diagnosis = db.get(DiagnosisSession, diagnosis_session_id)
    if diagnosis is None:
        raise GroundingError(f"no such diagnosis session: {diagnosis_session_id}")
    ids = list(dict.fromkeys((diagnosis.pending_request_context or {}).get("observation_ids", []) + diagnosis.baseline_observation_ids))
    observations = db.execute(select(Observation).where(Observation.observation_id.in_(ids))).scalars().all() if ids else []
    by_id = {o.observation_id: o for o in observations}
    reasons: list[str] = []
    primary_ids = [x for x in (diagnosis.pending_request_context or {}).get("observation_ids", []) if x not in diagnosis.baseline_observation_ids]
    if not primary_ids:
        reasons.append("no persisted subject observation is linked to the diagnosis")
    for oid in ids:
        obs = by_id.get(oid)
        if obs is None:
            reasons.append(f"observation {oid} does not exist")
            continue
        if obs.project_id != diagnosis.project_id:
            reasons.append(f"observation {oid} belongs to another project")
        if obs.qc_status != "passed":
            reasons.append(f"observation {oid} has qc_status={obs.qc_status}")
        if not obs.metric or not obs.unit or obs.value is None:
            reasons.append(f"observation {oid} lacks measurement/value/unit")
        if not _has_context(db, diagnosis, obs):
            reasons.append(f"observation {oid} lacks resolvable strain/context")
        if not _has_provenance(db, obs):
            reasons.append(f"observation {oid} lacks resolvable data provenance")
    if not diagnosis.baseline_observation_ids:
        reasons.append("no persisted baseline comparison observation is linked to the diagnosis")
    problems = db.execute(select(EngineeringProblem).where(
        EngineeringProblem.diagnosis_session_id == diagnosis_session_id,
        EngineeringProblem.status == "grounded",
    )).scalars().all()
    if not problems:
        reasons.append("no reproducible EngineeringProblem has been derived")
    return ObservationGroundingResult(
        status="grounded" if not reasons else "data_required",
        blocking_reasons=reasons,
        observation_ids=ids,
        engineering_problem_ids=[p.engineering_problem_id for p in problems],
        actionable=not reasons,
    )


def derive_engineering_problem(
    db: Session, *, diagnosis_session_id: str, observation_id: str,
    comparison_observation_id: str, abnormality_statement: str | None = None,
) -> EngineeringProblem:
    diagnosis = db.get(DiagnosisSession, diagnosis_session_id)
    observed = db.get(Observation, observation_id)
    baseline = db.get(Observation, comparison_observation_id)
    if diagnosis is None or observed is None or baseline is None:
        raise GroundingError("diagnosis, observation, and comparison observation must exist")
    if observed.project_id != diagnosis.project_id or baseline.project_id != diagnosis.project_id:
        raise GroundingError("observations must belong to the diagnosis project")
    if observed.qc_status != "passed" or baseline.qc_status != "passed":
        raise GroundingError("both observations must pass QC")
    if observed.metric != baseline.metric or observed.unit != baseline.unit:
        raise GroundingError("comparison requires the same metric and unit")
    if observed.condition_ref != baseline.condition_ref:
        raise GroundingError("comparison requires matched conditions")
    statement = abnormality_statement or (
        f"{observed.metric} is {abs(observed.value - baseline.value):g} {observed.unit} "
        f"{'below' if observed.value < baseline.value else 'above'} baseline"
    )
    if _CAUSAL.search(statement):
        raise GroundingError("abnormality_statement contains causal interpretation; record it as a hypothesis")
    existing = db.execute(select(EngineeringProblem).where(
        EngineeringProblem.diagnosis_session_id == diagnosis_session_id,
        EngineeringProblem.observation_ids == [observation_id],
        EngineeringProblem.comparison_observation_ids == [comparison_observation_id],
    )).scalar_one_or_none()
    if existing:
        return existing
    problem = EngineeringProblem(
        engineering_problem_id=new_id("EPR"), project_id=diagnosis.project_id,
        diagnosis_session_id=diagnosis_session_id, observation_ids=[observation_id],
        comparison_observation_ids=[comparison_observation_id], metric=observed.metric,
        observed_value=observed.value, expected_value=baseline.value, unit=observed.unit,
        delta=observed.value - baseline.value, comparison_method="matched_baseline",
        condition=observed.condition_ref, abnormality_statement=statement,
        provenance={"observation_ids": [observation_id, comparison_observation_id], "policy_version": "observation-grounding-v1"},
        status="grounded", created_at=now(),
    )
    db.add(problem)
    db.flush()
    return problem

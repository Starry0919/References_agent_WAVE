"""Creation and validation of immutable, observation-grounded findings."""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from harness.diagnosis.models import DiagnosisFinding, EngineeringProblem, EvidenceLink
from harness.experiments.models import Observation
from harness.ids import new_id, now
from harness.learning.models import HypothesisVersion


def create_diagnosis_finding(
    db: Session, *, project_id: str, engineering_problem_id: str, constraint_hypothesis_id: str,
    mechanism_type: str, causal_graph: dict, confidence_derivation: dict,
    unresolved_alternatives: list[str], falsifiers: list[str], engineering_consequences: list[dict],
    validation_needs: list[dict], actor_id: str,
) -> DiagnosisFinding:
    problem = db.get(EngineeringProblem, engineering_problem_id)
    hypothesis = db.get(HypothesisVersion, constraint_hypothesis_id)
    if problem is None or hypothesis is None or problem.project_id != project_id:
        raise ValueError("finding requires a project-scoped EngineeringProblem and real HypothesisVersion")
    obs_ids = [*problem.observation_ids, *problem.comparison_observation_ids]
    observations = db.execute(select(Observation).where(Observation.observation_id.in_(obs_ids))).scalars().all()
    if len(observations) != len(set(obs_ids)) or any(o.project_id != project_id or o.qc_status != "passed" for o in observations):
        raise ValueError("finding observations must exist, belong to the project, and pass QC")
    links = db.execute(select(EvidenceLink).where(EvidenceLink.hypothesis_version_id == constraint_hypothesis_id)).scalars().all()
    supporting = [x.evidence_item_id for x in links if x.relation in {"supports", "is_consistent_with"}]
    contradicting = [x.evidence_item_id for x in links if x.relation == "contradicts"]
    finding = DiagnosisFinding(
        finding_id=new_id("DFIND"), project_id=project_id, engineering_problem_id=engineering_problem_id,
        observation_refs=obs_ids, constraint_hypothesis_id=constraint_hypothesis_id, mechanism_type=mechanism_type,
        causal_graph=causal_graph, supporting_evidence=supporting, contradicting_evidence=contradicting,
        confidence_derivation=confidence_derivation, unresolved_alternatives=unresolved_alternatives,
        falsifiers=falsifiers, engineering_consequences=engineering_consequences, validation_needs=validation_needs,
        provenance={"policy": "diagnosis-finding/1.0", "actor_id": actor_id, "observation_ids": obs_ids}, created_at=now(),
    )
    db.add(finding); db.flush(); return finding


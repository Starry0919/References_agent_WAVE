"""Build/Test Planner (doc04 §4.6, §2.6): assembles the minimal real
execution plan for one `CandidateDesign`. Protocol text, materials,
instruments, and controls are supplied by the caller (a human or an
integrated LIMS/ELN - this module never invents that they exist); what the
planner itself does is derive target/mechanism/trade-off readouts from the
candidate's own strategy rationale, run `BuildReadinessGate`, and cap
`readiness` honestly whenever something required is still missing.
"""
from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from harness.engineering_design.models import BuildTestPackage, CandidateDesign, EngineeringDesignProject
from harness.ids import new_id, now
from harness.memory import event_types as et
from harness.memory.event_store import append_event, snapshot
from harness.workflow.gates import build_readiness_gate

PACKAGE_SNAPSHOT_FIELDS = (
    "package_id", "design_id", "design_version", "construction_concept", "build_steps_or_milestones",
    "required_materials", "required_capabilities_or_instruments", "available_resource_matches",
    "missing_information_or_resources", "controls", "replication_plan", "sampling_plan", "qc_checkpoints",
    "target_readouts", "mechanism_readouts", "expected_observations", "decision_rules", "failure_signatures",
    "debug_plan", "fallback_plan", "estimated_time_cost_and_risk", "readiness", "created_by", "created_at",
)

_GENERIC_FAILURE_SIGNATURES = {
    "knockout": ["no growth after transformation (possible essential-function loss)", "PCR/sequencing shows wild-type allele (transformation/selection failed)"],
    "knockdown": ["target transcript/protein level unchanged (knockdown ineffective)"],
    "attenuation": ["regulatory element unchanged by sequencing (edit failed)"],
    "overexpression": ["no increase in target transcript/protein (expression construct silent or lost)"],
    "gene_insertion": ["insert absent or truncated by sequencing/PCR"],
    "promoter_edit": ["expression level unchanged from baseline (edit had no measurable effect)"],
    "rbs_edit": ["expression level unchanged from baseline (edit had no measurable effect)"],
    "allele_replacement": ["sequencing shows original allele (replacement failed)"],
    "dynamic_control": ["no phenotype change across the intended induction/switch condition"],
    "process_only": ["no phenotype change despite the process condition being verified changed"],
}


def _derive_readouts(candidate: CandidateDesign, primary_metrics: list[dict[str, Any]]) -> tuple[list[str], list[str], list[str]]:
    target_readouts = [str(m.get("metric", m.get("name", "unknown"))) for m in primary_metrics] or ["target phenotype (no primary_metrics recorded)"]
    mechanism_readouts = [
        f"verify {m.get('target_identifier')} genotype/expression change ({m.get('operation')})"
        for m in candidate.genetic_modifications
    ] or ["no genetic modification - mechanism readout is the process-condition parameter itself"]
    expected_observations = [
        f"if the strategy is correct: {m.get('desired_effect', 'intended effect')} at the {m.get('target_identifier')} level"
        for m in candidate.genetic_modifications
    ] or ["baseline/reference behavior expected"]
    return target_readouts, mechanism_readouts, expected_observations


def _derive_failure_signatures(candidate: CandidateDesign) -> list[str]:
    sigs: list[str] = []
    for m in candidate.genetic_modifications:
        sigs.extend(_GENERIC_FAILURE_SIGNATURES.get(m.get("operation", ""), [f"no verifiable change at {m.get('target_identifier')}"]))
    return sigs or ["no genetic modification to verify - failure signature is absence of the intended process-condition change"]


def draft_build_test_package(
    session: Session,
    *,
    design_id: str,
    actor_id: str,
    construction_concept: str = "",
    build_steps_or_milestones: list[dict[str, Any]] | None = None,
    required_materials: list[str] | None = None,
    required_capabilities_or_instruments: list[str] | None = None,
    available_resources: dict[str, Any] | None = None,
    controls: list[dict[str, Any]] | None = None,
    replication_plan: dict[str, Any] | None = None,
    sampling_plan: list[dict[str, Any]] | None = None,
    qc_checkpoints: list[str] | None = None,
    decision_rules: list[str] | None = None,
    debug_plan: list[str] | None = None,
    fallback_plan: list[str] | None = None,
    estimated_time_cost_and_risk: dict[str, Any] | None = None,
) -> BuildTestPackage:
    candidate = session.get(CandidateDesign, design_id)
    if candidate is None:
        raise ValueError(f"no such candidate design: {design_id}")
    proj = session.get(EngineeringDesignProject, candidate.design_project_id)

    required_materials = required_materials or []
    available_resources = available_resources or proj.available_resources or {}
    available_pool = set(available_resources.get("materials", [])) | set(available_resources.get("instruments", []))
    required_capabilities_or_instruments = required_capabilities_or_instruments or []
    matched = sorted((set(required_materials) | set(required_capabilities_or_instruments)) & available_pool)
    missing = sorted((set(required_materials) | set(required_capabilities_or_instruments)) - available_pool)

    target_readouts, mechanism_readouts, expected_observations = _derive_readouts(candidate, proj.primary_metrics)
    failure_signatures = _derive_failure_signatures(candidate)

    gate = build_readiness_gate(
        has_construction_concept=bool(construction_concept), has_materials=bool(required_materials),
        has_controls=bool(controls), has_replication_plan=bool(replication_plan), has_sampling_plan=bool(sampling_plan),
        has_qc_checkpoints=bool(qc_checkpoints), has_decision_rules=bool(decision_rules),
        has_protocol_or_draft=bool(construction_concept),
    )
    if gate.status.value == "pass":
        readiness = "build_ready"
    elif construction_concept or required_materials or controls:
        readiness = "planning_ready"  # a real, if incomplete, draft exists
    else:
        readiness = "conceptual"  # essentially nothing supplied yet

    package = BuildTestPackage(
        package_id=new_id("BTP"), design_id=design_id, design_version=candidate.design_version,
        construction_concept=construction_concept, build_steps_or_milestones=build_steps_or_milestones or [],
        required_materials=required_materials, required_capabilities_or_instruments=required_capabilities_or_instruments,
        available_resource_matches=matched, missing_information_or_resources=missing, controls=controls or [],
        replication_plan=replication_plan or {}, sampling_plan=sampling_plan or [], qc_checkpoints=qc_checkpoints or [],
        target_readouts=target_readouts, mechanism_readouts=mechanism_readouts, expected_observations=expected_observations,
        decision_rules=decision_rules or [], failure_signatures=failure_signatures, debug_plan=debug_plan or [],
        fallback_plan=fallback_plan or [], estimated_time_cost_and_risk=estimated_time_cost_and_risk or {},
        readiness=readiness, created_by=actor_id, created_at=now(),
    )
    session.add(package)
    session.flush()

    candidate.build_test_package_id = package.package_id
    if readiness in ("planning_ready", "build_ready") and candidate.readiness in ("conceptual", "evaluated"):
        candidate.readiness = readiness
    session.flush()

    append_event(
        session, project_id=proj.project_id, event_type=et.DESIGN_BUILD_TEST_PACKAGE_DRAFTED, entity_type="BuildTestPackage",
        entity_id=package.package_id, payload=snapshot(package, PACKAGE_SNAPSHOT_FIELDS), actor_type="human" if actor_id != "system" else "agent",
        actor_id=actor_id,
    )
    return package


def get_build_test_package(session: Session, package_id: str) -> BuildTestPackage | None:
    return session.get(BuildTestPackage, package_id)

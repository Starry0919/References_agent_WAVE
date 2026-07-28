"""Golden Set evaluation runner (prompt §7.5/§14): drives each
`ScientificGoldenCase` through the REAL system component its `case_type`
exercises - never a mock, never a hardcoded expected answer echoed back.
Reuses exactly the same adapters/functions Phase B-D's own test suites
already exercise (`harness.orchestrator.adapters.DiagnosisAdapter`,
`harness.engineering_design.evaluators.safety_governance`,
`harness.virtual_cell.compiler.resolve_gene`/`compile_intervention`,
`harness.virtual_cell.cross_modal_service`).

Blind separation (prompt §7.1/§7.3): this module imports
`harness.golden_set.models.ScientificGoldenCase` only - never
`GoldenCaseAnswerKey` - so a case's hidden expectations cannot influence
how it is driven through the system, even by accident. Scoring against the
answer key happens afterward, in `harness.golden_set.scoring`, which is
never imported here.
"""
from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from harness.golden_set.models import GoldenCaseEvaluationRun, ScientificGoldenCase
from harness.ids import new_id, now
from harness.projects import service as proj_svc


def _run_diagnosis_case(session: Session, case: ScientificGoldenCase, *, actor_id: str, llm_adapters_enabled: bool) -> dict[str, Any]:
    from harness.orchestrator.adapters import DiagnosisAdapter

    proj = proj_svc.create_project(
        session, name=f"golden:{case.case_id}", host_definition={"species": case.organism, "strain": case.strain},
        target_product=case.case_inputs.get("target_product", "unknown"), actor_id=actor_id,
    )
    request = {
        "project_id": proj.project_id, "actor_id": actor_id,
        "phenotype": case.case_inputs.get("phenotype", case.objective),
        "target_product": case.case_inputs.get("target_product", "unknown"), "host": f"{case.organism} {case.strain}",
        "data_sufficiency": case.case_inputs.get("data_sufficiency", {}),
        "enable_llm_hypothesis": llm_adapters_enabled,
    }
    adapter = DiagnosisAdapter()
    module_ref = adapter.start(session, request=request, context=case.condition)
    status = adapter.get_status(session, module_ref.run_id)
    handoff = adapter.get_handoff(session, module_ref.run_id)

    from harness.diagnosis import service as diag_svc
    from harness.learning.models import HypothesisFamily, HypothesisVersion
    from sqlalchemy import select

    sess = diag_svc.get_session(session, module_ref.run_id)
    hyps = session.execute(
        select(HypothesisVersion).join(HypothesisFamily, HypothesisVersion.hypothesis_family_id == HypothesisFamily.hypothesis_family_id)
        .where(HypothesisFamily.project_id == proj.project_id)
    ).scalars().all()
    mechanism_classes = sorted({h.mechanism_class for h in hyps})

    return {
        "project_id": proj.project_id, "diagnosis_run_ref": module_ref.run_id, "native_status": status.native_status,
        "normalized_status": status.normalized, "mechanism_classes_represented": mechanism_classes,
        "hypothesis_count": len(hyps), "handoff_confidence_status": handoff.confidence_status,
        "handoff_unresolved_items": handoff.unresolved_items,
    }


def _run_unsafe_design_case(session: Session, case: ScientificGoldenCase, *, actor_id: str) -> dict[str, Any]:
    from harness.engineering_design.evaluators import safety_governance

    candidate = {"genetic_modifications": case.case_inputs.get("genetic_modifications", []), "status": "proposed"}
    result = safety_governance.evaluate(candidate, human_approval_on_record=False)
    return {
        "evaluator": result.evaluator, "status": result.status, "blocking": result.blocking,
        "findings": result.findings, "required_revisions": result.required_revisions,
    }


def _run_model_domain_case(session: Session, case: ScientificGoldenCase, *, actor_id: str) -> dict[str, Any]:
    from harness.diagnosis.model_adapters.registry import get_adapter
    from harness.virtual_cell.compiler import _load_gem_model, resolve_gene

    adapter_name = case.case_inputs.get("adapter_name", "gem_fba")
    model_id = {"gem_fba": "MREG-gem_fba", "gem_fba_iml1515": "MREG-gem_fba_iml1515"}[adapter_name]
    model = _load_gem_model(model_id)
    gene = resolve_gene(model, case.case_inputs["target_gene"])
    adapter = get_adapter(adapter_name)
    capability = adapter.detect_capability()
    return {
        "adapter_name": adapter_name, "model_id": model_id, "model_gene_count": len(model.genes),
        "capability_available": capability.available, "gene_resolved": gene is not None,
        "domain_status": "in_domain" if gene is not None else "out_of_domain",
    }


def _run_cross_modal_conflict_case(session: Session, case: ScientificGoldenCase, *, actor_id: str) -> dict[str, Any]:
    from harness.designs.service import approve_design_version, propose_design_version
    from harness.diagnosis import service as diag_svc
    from harness.diagnosis.normalizer import RawObservationInput, normalize_and_commit
    from harness.virtual_cell.cross_modal_service import build_cross_modal_consistency_report
    from harness.virtual_cell.service import run_prediction_pipeline

    proj = proj_svc.create_project(session, name=f"golden:{case.case_id}", host_definition={"species": case.organism, "strain": case.strain}, target_product="x", actor_id=actor_id)
    dv = propose_design_version(
        session, project_id=proj.project_id, version_label="v1", parent_version_ids=[], branch_name="main",
        genotype_manifest={"baseline_strain": f"{case.organism} {case.strain}", "modifications": [
            {"gene": case.case_inputs["target_gene"], "operation": case.case_inputs["operation"], "detail": "golden case"},
        ]}, decisions=[], proposed_by=actor_id,
    )
    dv = approve_design_version(session, design_version_id=dv.design_version_id, approver_id=f"{actor_id}_approver", expected_project_version=proj.version)
    sim_result = run_prediction_pipeline(
        session, project_id=proj.project_id, design_version_id=dv.design_version_id, chassis={"species": case.organism, "strain": case.strain},
        environment=case.condition, model_id=f"MREG-{case.case_inputs.get('adapter_name', 'gem_fba_iml1515')}", actor_id=actor_id,
    )
    ctx = diag_svc.create_biological_context(session, project_id=proj.project_id, medium=case.condition.get("medium"), carbon_source=case.condition.get("carbon_source"))
    phen = case.case_inputs.get("phenotype_observation")
    if phen:
        raw = RawObservationInput(
            feature_or_phenotype=phen["metric"], value=phen["value"], unit=phen.get("unit", "a.u."), qc_status="passed",
            condition_id=ctx.context_id, timepoint={"value": 24, "unit": "h"}, reference_or_baseline={"value": phen["baseline_value"]},
            modality="phenotypic", entity_namespace="phenotype", entity_id=case.case_inputs["target_gene"],
        )
        normalize_and_commit(session, project_id=proj.project_id, raw=raw, actor_id=actor_id)
    report = build_cross_modal_consistency_report(session, project_id=proj.project_id, target_entity=case.case_inputs["target_gene"], design_version_id=dv.design_version_id, actor_id=actor_id)
    return {
        "project_id": proj.project_id, "design_version_id": dv.design_version_id,
        "simulation_compatible": sim_result.get("candidate_run") is not None,
        "agreement_status": report.agreement_status, "inconsistency_classes": report.inconsistency_classes,
        "alternative_explanations": report.alternative_explanations, "unsupported_conclusions": report.unsupported_conclusions,
    }


def run_golden_case(session: Session, case_id: str, *, actor_id: str = "golden_set_runner", llm_adapters_enabled: bool = False) -> GoldenCaseEvaluationRun:
    case = session.get(ScientificGoldenCase, case_id)
    if case is None:
        raise ValueError(f"no such golden case: {case_id}")

    errors: list[str] = []
    output: dict[str, Any] = {}
    try:
        if case.case_type == "unsafe_design":
            output = _run_unsafe_design_case(session, case, actor_id=actor_id)
        elif case.case_type == "model_domain_mismatch":
            output = _run_model_domain_case(session, case, actor_id=actor_id)
        elif case.case_type == "observation_conflict" and "target_gene" in case.case_inputs:
            output = _run_cross_modal_conflict_case(session, case, actor_id=actor_id)
        elif case.case_type in ("diagnosis_trp", "diagnosis_other_product", "diagnosis_insufficient_evidence", "observation_conflict"):
            output = _run_diagnosis_case(session, case, actor_id=actor_id, llm_adapters_enabled=llm_adapters_enabled)
        else:
            errors.append(f"unknown case_type: {case.case_type}")
    except Exception as exc:  # noqa: BLE001 - a driver crash is a real, reportable evaluation-run error, not silently swallowed
        errors.append(f"{type(exc).__name__}: {exc}")

    from harness.golden_set.metrics import compute_automated_metrics

    metrics = compute_automated_metrics(session, case=case, system_output=output, errors=errors)

    row = GoldenCaseEvaluationRun(
        evaluation_run_id=new_id("GCRUN"), case_id=case.case_id, case_version=case.version,
        project_id=output.get("project_id"), workflow_run_id=None, llm_adapters_enabled=llm_adapters_enabled,
        system_output=output, automated_metrics=metrics, errors=errors, created_at=now(),
    )
    session.add(row)
    session.flush()
    return row

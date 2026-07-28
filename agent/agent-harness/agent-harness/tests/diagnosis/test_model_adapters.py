"""Model Adapter Registry (doc03 4.7/2.6): capability detection, real FBA
execution against cobrapy's bundled e_coli_core, honest unavailable
adapters, and cross-model convergence/conflict analysis.
"""
from __future__ import annotations

from harness import db
from harness.diagnosis import model_service as model_svc
from harness.diagnosis import service as diag_svc
from harness.diagnosis.model_adapters.registry import detect_all_capabilities, get_adapter
from harness.projects import service as proj_svc


def _project_and_session():
    with db.session_scope() as s:
        p = proj_svc.create_project(s, name="t", host_definition={}, target_product="trp", actor_id="pi")
        sess = diag_svc.start_diagnosis_session(s, project_id=p.project_id, actor_id="pi")
        return p.project_id, sess.diagnosis_session_id


def test_gem_fba_adapter_is_genuinely_available():
    caps = detect_all_capabilities()
    assert caps["gem_fba"].available is True
    assert caps["vecoli"].available is False
    assert caps["kinetic_resource"].available is False


def test_real_fba_run_produces_optimal_solution():
    project_id, sess_id = _project_and_session()
    with db.session_scope() as s:
        record = model_svc.execute_model_run(
            s, project_id=project_id, diagnosis_session_id=sess_id, adapter_name="gem_fba", inputs={}, context={},
            constraints_objective_parameters={}, actor_id="agent",
        )
        assert record.capability_status == "available"
        assert record.runtime_status == "optimal"
        assert record.outputs["objective_value"] > 0
        assert record.reproducibility_ref.get("model_id") == "e_coli_core"


def test_fba_sensitivity_variant_changes_result_under_tighter_bound():
    project_id, sess_id = _project_and_session()
    with db.session_scope() as s:
        baseline = model_svc.execute_model_run(
            s, project_id=project_id, diagnosis_session_id=sess_id, adapter_name="gem_fba", inputs={}, context={},
            constraints_objective_parameters={}, actor_id="agent",
        )
        restricted = model_svc.execute_model_run(
            s, project_id=project_id, diagnosis_session_id=sess_id, adapter_name="gem_fba",
            inputs={"reaction_bounds": {"EX_glc__D_e": {"lower": -2, "upper": 1000}}}, context={},
            constraints_objective_parameters={}, actor_id="agent", sensitivity_variant_of=baseline.model_run_id,
        )
        assert restricted.runtime_status == "optimal"
        assert restricted.outputs["objective_value"] < baseline.outputs["objective_value"]
        assert restricted.sensitivity_variant_of == baseline.model_run_id


def test_contradictory_bounds_returns_structured_error_not_a_crash():
    project_id, sess_id = _project_and_session()
    with db.session_scope() as s:
        record = model_svc.execute_model_run(
            s, project_id=project_id, diagnosis_session_id=sess_id, adapter_name="gem_fba",
            inputs={"reaction_bounds": {"EX_glc__D_e": {"lower": 5, "upper": -5}}}, context={},
            constraints_objective_parameters={}, actor_id="agent",
        )
        assert record.runtime_status == "error"


def test_unknown_reaction_id_is_out_of_domain():
    project_id, sess_id = _project_and_session()
    with db.session_scope() as s:
        record = model_svc.execute_model_run(
            s, project_id=project_id, diagnosis_session_id=sess_id, adapter_name="gem_fba",
            inputs={"objective_reaction": "NOT_A_REAL_REACTION_ID"}, context={},
            constraints_objective_parameters={}, actor_id="agent",
        )
        assert record.capability_status == "out_of_domain"
        assert record.runtime_status == "not_computed"


def test_unavailable_adapter_returns_not_computed_never_fabricated_value():
    project_id, sess_id = _project_and_session()
    with db.session_scope() as s:
        record = model_svc.execute_model_run(
            s, project_id=project_id, diagnosis_session_id=sess_id, adapter_name="vecoli", inputs={}, context={},
            constraints_objective_parameters={}, actor_id="agent",
        )
        assert record.capability_status == "unavailable"
        assert record.runtime_status == "not_computed"
        assert record.outputs == {}


def test_cross_model_conflict_is_preserved_not_averaged():
    project_id, sess_id = _project_and_session()
    with db.session_scope() as s:
        baseline = model_svc.execute_model_run(
            s, project_id=project_id, diagnosis_session_id=sess_id, adapter_name="gem_fba", inputs={}, context={},
            constraints_objective_parameters={}, actor_id="agent",
        )
        restricted = model_svc.execute_model_run(
            s, project_id=project_id, diagnosis_session_id=sess_id, adapter_name="gem_fba",
            inputs={"reaction_bounds": {"EX_glc__D_e": {"lower": -2, "upper": 1000}}}, context={},
            constraints_objective_parameters={}, actor_id="agent",
        )
        assessment = model_svc.assess_cross_model_convergence(s, diagnosis_session_id=sess_id, model_run_ids=[baseline.model_run_id, restricted.model_run_id])
        assert assessment.convergence_status == "conflicting"
        # both original run outputs remain readable, unaveraged
        assert baseline.outputs["objective_value"] != restricted.outputs["objective_value"]


def test_registry_rejects_unknown_adapter_name():
    import pytest
    with pytest.raises(KeyError):
        get_adapter("not_a_real_adapter")

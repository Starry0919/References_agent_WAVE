"""CompatibilityReport tests (doc06 §2.4/§3.4) - the gate that must pass
before any run is attempted.
"""
from __future__ import annotations

from harness import db
from harness.virtual_cell import registry as registry_mod
from harness.virtual_cell import service as vc_service
from tests.virtual_cell.fixtures import build_approved_ppc_knockout_design, build_out_of_domain_design


def test_ppc_design_is_compatible_with_assumptions_or_compatible():
    with db.session_scope() as s:
        proj, dv = build_approved_ppc_knockout_design(s)
        case = vc_service.open_simulation_case(s, project_id=proj.project_id, design_version_id=dv.design_version_id, requested_by="agent")
        perturbations = vc_service.extract_perturbations(s, case=case, design_version=dv, actor_id="agent")
        report = vc_service.run_compatibility_check(
            s, case=case, model_id="MREG-gem_fba", cell_state_id="SNAP-fake", chassis={"organism": "Escherichia coli", "strain": "K-12"},
            perturbations=perturbations, actor_id="agent",
        )
        assert report.decision in ("compatible", "compatible_with_assumptions")
        assert report.perturbation_support[perturbations[0].perturbation_id] == "supported"


def test_arog_design_is_out_of_domain():
    with db.session_scope() as s:
        proj, dv = build_out_of_domain_design(s)
        case = vc_service.open_simulation_case(s, project_id=proj.project_id, design_version_id=dv.design_version_id, requested_by="agent")
        perturbations = vc_service.extract_perturbations(s, case=case, design_version=dv, actor_id="agent")
        report = vc_service.run_compatibility_check(
            s, case=case, model_id="MREG-gem_fba", cell_state_id="SNAP-fake", chassis={"organism": "Escherichia coli", "strain": "K-12"},
            perturbations=perturbations, actor_id="agent",
        )
        assert report.decision == "out_of_domain"
        assert report.blocking_reasons


def test_non_ecoli_organism_is_blocked():
    with db.session_scope() as s:
        proj, dv = build_approved_ppc_knockout_design(s)
        case = vc_service.open_simulation_case(s, project_id=proj.project_id, design_version_id=dv.design_version_id, requested_by="agent")
        perturbations = vc_service.extract_perturbations(s, case=case, design_version=dv, actor_id="agent")
        report = vc_service.run_compatibility_check(
            s, case=case, model_id="MREG-gem_fba", cell_state_id="SNAP-fake", chassis={"organism": "Saccharomyces cerevisiae", "strain": "BY4741"},
            perturbations=perturbations, actor_id="agent",
        )
        assert report.decision in ("out_of_domain", "unsupported")


def test_unavailable_model_is_honestly_reported():
    with db.session_scope() as s:
        proj, dv = build_approved_ppc_knockout_design(s)
        case = vc_service.open_simulation_case(s, project_id=proj.project_id, design_version_id=dv.design_version_id, requested_by="agent")
        perturbations = vc_service.extract_perturbations(s, case=case, design_version=dv, actor_id="agent")
        report = vc_service.run_compatibility_check(
            s, case=case, model_id="MREG-vecoli", cell_state_id="SNAP-fake", chassis={"organism": "Escherichia coli", "strain": "K-12"},
            perturbations=perturbations, actor_id="agent",
        )
        assert report.decision == "unavailable"


def test_registry_entries_reflect_real_adapter_capability():
    with db.session_scope() as s:
        entries = {e.adapter_id: e for e in registry_mod.list_registry_entries(s)}
        assert entries["gem_fba"].availability_status == "available"
        assert entries["vecoli"].availability_status == "unavailable"
        assert entries["kinetic_resource"].availability_status == "unavailable"
        assert entries["vecoli"].unavailability_reason

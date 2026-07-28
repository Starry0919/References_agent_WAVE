"""Shared, real fixture builders for the Problem-06 test suite - a formal
(approved) `DesignVersion` built through the actual Problem 02 service
functions, never a bare dict standing in for one. `ppc` is used as the
real single-gene knockout case (see `harness/virtual_cell/compiler.py`'s
own docstring for why `ppc` - not `ptsG` - is the honest choice: `ppc` has
a single-gene GPR in cobrapy's bundled e_coli_core model, so its knockout
genuinely blocks a reaction, whereas `ptsG`'s isozyme-redundant GPR means a
single-gene knockout has no real flux-bound effect under this model).
"""
from __future__ import annotations

from harness.designs.service import approve_design_version, propose_design_version
from harness.projects import service as proj_svc


def build_approved_ppc_knockout_design(session, *, actor_id: str = "pi", approver_id: str = "approver"):
    proj = proj_svc.create_project(
        session, name="Trp engineering", host_definition={"species": "Escherichia coli", "strain": "K-12"},
        target_product="L-tryptophan", actor_id=actor_id,
    )
    dv = propose_design_version(
        session, project_id=proj.project_id, version_label="v1_ppc_ko", parent_version_ids=[], branch_name="main",
        genotype_manifest={"baseline_strain": "K-12 MG1655", "modifications": [
            {"gene": "ppc", "operation": "knockout", "detail": "delete phosphoenolpyruvate carboxylase (anaplerotic node)"},
        ]},
        decisions=[], proposed_by=actor_id,
    )
    dv = approve_design_version(session, design_version_id=dv.design_version_id, approver_id=approver_id, expected_project_version=proj.version)
    return proj, dv


def build_unapproved_design(session, *, actor_id: str = "pi"):
    proj = proj_svc.create_project(
        session, name="Trp engineering (unapproved)", host_definition={"species": "Escherichia coli", "strain": "K-12"},
        target_product="L-tryptophan", actor_id=actor_id,
    )
    dv = propose_design_version(
        session, project_id=proj.project_id, version_label="v1_draft", parent_version_ids=[], branch_name="main",
        genotype_manifest={"baseline_strain": "K-12 MG1655", "modifications": [{"gene": "ppc", "operation": "knockout", "detail": "draft"}]},
        decisions=[], proposed_by=actor_id,
    )
    return proj, dv


def build_out_of_domain_design(session, *, actor_id: str = "pi", approver_id: str = "approver"):
    """`aroG` is a real aromatic-amino-acid-pathway gene, not part of the
    137-gene core-metabolism e_coli_core model - the honest out-of-domain
    case doc06 explicitly asks not to fake a numeric answer for."""
    proj = proj_svc.create_project(
        session, name="Trp engineering (aroG OE)", host_definition={"species": "Escherichia coli", "strain": "K-12"},
        target_product="L-tryptophan", actor_id=actor_id,
    )
    dv = propose_design_version(
        session, project_id=proj.project_id, version_label="v1_arog_oe", parent_version_ids=[], branch_name="main",
        genotype_manifest={"baseline_strain": "K-12 MG1655", "modifications": [
            {"gene": "aroG", "operation": "overexpression", "detail": "feedback-resistant aroG overexpression"},
        ]},
        decisions=[], proposed_by=actor_id,
    )
    dv = approve_design_version(session, design_version_id=dv.design_version_id, approver_id=approver_id, expected_project_version=proj.version)
    return proj, dv

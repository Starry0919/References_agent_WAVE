"""doc 6.11's minimal collaboration-governance acceptance: two users
concurrently submitting mutually exclusive changes against the same
Project version get an explicit conflict, never silent last-write-wins;
a proposer can never approve their own design.
"""
from __future__ import annotations

import pytest

from harness import db
from harness.db import ConcurrencyConflictError
from harness.designs import service as design_svc
from harness.designs.service import SelfApprovalError
from harness.projects import service as proj_svc


def test_concurrent_design_approval_conflict_is_explicit_not_silent():
    with db.session_scope() as s:
        p = proj_svc.create_project(s, name="t", host_definition={}, target_product="trp", actor_id="pi")
        project_id = p.project_id
        seen_version = p.version  # both "users" load the project at version 1

        dv_a = design_svc.propose_design_version(
            s, project_id=project_id, version_label="v0a", parent_version_ids=[], branch_name="main",
            genotype_manifest={"baseline_strain": "K-12", "modifications": [{"gene": "trpE", "operation": "mutation", "detail": "A"}]},
            decisions=[], proposed_by="agent_a",
        )
        dv_b = design_svc.propose_design_version(
            s, project_id=project_id, version_label="v0b", parent_version_ids=[], branch_name="main",
            genotype_manifest={"baseline_strain": "K-12", "modifications": [{"gene": "trpE", "operation": "mutation", "detail": "B"}]},
            decisions=[], proposed_by="agent_b",
        )

    # User 1 approves dv_a using the version they originally loaded - succeeds, bumps version.
    with db.session_scope() as s:
        design_svc.approve_design_version(s, design_version_id=dv_a.design_version_id, approver_id="pi", expected_project_version=seen_version)

    # User 2 approves dv_b using the SAME stale version they loaded before user 1's change -
    # must be rejected with an explicit conflict, not silently overwrite user 1's approval.
    with pytest.raises(ConcurrencyConflictError):
        with db.session_scope() as s:
            design_svc.approve_design_version(s, design_version_id=dv_b.design_version_id, approver_id="pi", expected_project_version=seen_version)

    with db.session_scope() as s:
        project = proj_svc.get_project(s, project_id)
        assert project.current_design_version_id == dv_a.design_version_id  # user 2's write never landed


def test_proposer_cannot_approve_own_design():
    with db.session_scope() as s:
        p = proj_svc.create_project(s, name="t", host_definition={}, target_product="trp", actor_id="pi")
        project_id = p.project_id
        dv = design_svc.propose_design_version(
            s, project_id=project_id, version_label="v0", parent_version_ids=[], branch_name="main",
            genotype_manifest={"baseline_strain": "K-12", "modifications": []}, decisions=[], proposed_by="agent_a",
        )
        with pytest.raises(SelfApprovalError):
            design_svc.approve_design_version(s, design_version_id=dv.design_version_id, approver_id="agent_a", expected_project_version=1)

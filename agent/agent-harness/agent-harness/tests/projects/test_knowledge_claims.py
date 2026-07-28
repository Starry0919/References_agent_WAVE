"""doc 6.8/18.6: a single observation (or N technical replicates of one
batch) must never satisfy a promotion threshold; a submitter cannot
self-approve; retraction preserves history.
"""
from __future__ import annotations

import pytest

from harness import db
from harness.memory import knowledge_claims as kc
from harness.projects import service as proj_svc


def _project():
    with db.session_scope() as s:
        p = proj_svc.create_project(s, name="t", host_definition={}, target_product="trp", actor_id="pi")
        return p.project_id


def test_single_observation_cannot_be_promoted_to_lab_candidate():
    project_id = _project()
    with db.session_scope() as s:
        claim = kc.submit_claim(
            s, project_id=project_id, statement="pykF KO reduces growth", scope={"species": "E. coli"},
            supporting_experiments=["RUN-1"], independence_groups=[["RUN-1"]], created_by="agent",
        )
        with pytest.raises(kc.PromotionRejected):
            kc.promote_claim(s, claim_id=claim.claim_id, target_status="lab_candidate", reviewer_id="pi")


def test_technical_replicates_of_one_batch_do_not_count_as_independent():
    project_id = _project()
    with db.session_scope() as s:
        # 6 technical replicates, but all in ONE batch -> independence_groups has 1 group, not 6.
        claim = kc.submit_claim(
            s, project_id=project_id, statement="pykF KO reduces growth", scope={"species": "E. coli"},
            supporting_experiments=[f"RUN-{i}" for i in range(6)],
            independence_groups=[[f"RUN-{i}" for i in range(6)]],  # one batch
            created_by="agent",
        )
        assert kc.count_independent_groups(claim.independence_groups) == 1
        with pytest.raises(kc.PromotionRejected):
            kc.promote_claim(s, claim_id=claim.claim_id, target_status="lab_candidate", reviewer_id="pi")


def test_three_independent_groups_can_be_promoted_to_lab_candidate():
    project_id = _project()
    with db.session_scope() as s:
        claim = kc.submit_claim(
            s, project_id=project_id, statement="pykF KO reduces growth", scope={"species": "E. coli"},
            supporting_experiments=["RUN-1", "RUN-2", "RUN-3"],
            independence_groups=[["RUN-1"], ["RUN-2"], ["RUN-3"]],  # 3 genuinely independent batches
            created_by="agent",
        )
        promoted = kc.promote_claim(s, claim_id=claim.claim_id, target_status="lab_candidate", reviewer_id="pi")
        assert promoted.status == "lab_candidate"
        assert len(promoted.promotion_record) == 2  # submitted + promoted


def test_submitter_cannot_self_promote():
    project_id = _project()
    with db.session_scope() as s:
        claim = kc.submit_claim(
            s, project_id=project_id, statement="x", scope={}, supporting_experiments=["RUN-1", "RUN-2", "RUN-3"],
            independence_groups=[["RUN-1"], ["RUN-2"], ["RUN-3"]], created_by="agent",
        )
        with pytest.raises(kc.PromotionRejected):
            kc.promote_claim(s, claim_id=claim.claim_id, target_status="lab_candidate", reviewer_id="agent")


def test_conflicting_evidence_requires_explicit_reason_to_promote():
    project_id = _project()
    with db.session_scope() as s:
        claim = kc.submit_claim(
            s, project_id=project_id, statement="x", scope={}, supporting_experiments=["RUN-1", "RUN-2", "RUN-3"],
            independence_groups=[["RUN-1"], ["RUN-2"], ["RUN-3"]], created_by="agent",
            contradicting_experiments=["RUN-9"],
        )
        with pytest.raises(kc.PromotionRejected):
            kc.promote_claim(s, claim_id=claim.claim_id, target_status="lab_candidate", reviewer_id="pi", reason="")
        promoted = kc.promote_claim(s, claim_id=claim.claim_id, target_status="lab_candidate", reviewer_id="pi",
                                     reason="RUN-9 used a different carbon source; not a true counter-example")
        assert promoted.status == "lab_candidate"


def test_retraction_preserves_promotion_history():
    project_id = _project()
    with db.session_scope() as s:
        claim = kc.submit_claim(
            s, project_id=project_id, statement="x", scope={}, supporting_experiments=["RUN-1", "RUN-2", "RUN-3"],
            independence_groups=[["RUN-1"], ["RUN-2"], ["RUN-3"]], created_by="agent",
        )
        kc.promote_claim(s, claim_id=claim.claim_id, target_status="lab_candidate", reviewer_id="pi")
        retracted = kc.retract_claim(s, claim_id=claim.claim_id, reviewer_id="pi", reason="new counter-evidence found")
        assert retracted.status == "retracted"
        statuses = [r["status"] for r in retracted.promotion_record]
        assert statuses == ["project_candidate", "lab_candidate", "retracted"]  # full history intact

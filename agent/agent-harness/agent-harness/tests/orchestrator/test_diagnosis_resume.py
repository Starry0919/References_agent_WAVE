"""Regression test for the resume_diagnosis orphan-session bug.

Root cause (see harness/orchestrator/service.py's
`resume_diagnosis_with_data`): once a resumed `DiagnosisSession` cleared the
data-sufficiency gate, the orchestrator fell through to `self.start_diagnosis`,
which unconditionally calls `DiagnosisAdapter.start()` and mints a brand-new
`DiagnosisSession` - silently orphaning the session that had just been
correctly resumed, and losing the user's just-submitted data in the process.

This test drives the real bug scenario end-to-end through the orchestrator
(never mocking diagnosis/gates): start diagnosis with insufficient data
(lands in `data_required`), then resume with sufficient data, and asserts the
SAME `DiagnosisSession` row is the one that reaches hypotheses/handoff - not
a second, orphaned one.
"""
from __future__ import annotations

from sqlalchemy import select

from harness import db
from harness.diagnosis import service as diag_svc
from harness.diagnosis.models import DiagnosisSession
from harness.orchestrator.models import UnifiedWorkflowRun
from harness.orchestrator.service import UnifiedScientificWorkflowOrchestrator
from harness.projects import service as proj_svc

ORC = UnifiedScientificWorkflowOrchestrator()

_SUFFICIENT = {"has_baseline": True, "has_genotype": True, "has_condition": True, "has_time": True, "has_qc": True, "has_key_phenotype": True}
_INSUFFICIENT = {"has_baseline": False, "has_genotype": False, "has_condition": False, "has_time": False, "has_qc": False, "has_key_phenotype": False}


def test_resume_diagnosis_continues_same_session_instead_of_orphaning_it():
    with db.session_scope() as s:
        proj = proj_svc.create_project(
            s, name="Resume bug regression", host_definition={"species": "E. coli", "strain": "K-12"},
            target_product="L-tryptophan", actor_id="pi",
        )
        run = ORC.create_run(s, project_id=proj.project_id, actor_id="pi", target_product="L-tryptophan", host="E. coli K-12")
        project_id = proj.project_id
        run_id = run.workflow_run_id

    # -- start diagnosis with genuinely insufficient data: must land in data_required, waiting --
    with db.session_scope() as s:
        run = ORC.start_diagnosis(
            s, run_id, expected_version=1, actor_id="agent",
            request={"biological_system": {"species": "E. coli", "strain": "K-12"}, "phenotype": "L-tryptophan titer plateaus below target",
                     "target_product": "L-tryptophan", "host": "E. coli K-12", "data_sufficiency": _INSUFFICIENT},
            context={"medium": "M9", "carbon_source": "glucose"},
        )
        assert run.status == "waiting"
        assert run.current_phase == "DIAGNOSIS"
        original_session_id = run.diagnosis_run_ref
        assert original_session_id is not None
        v_after_start = run.version

    with db.session_scope() as s:
        sess = diag_svc.get_session(s, original_session_id)
        assert sess.status == "data_required"
        # the original request was captured so resume can finish the job on this row
        assert sess.pending_request_context.get("request", {}).get("phenotype") == "L-tryptophan titer plateaus below target"

    # -- resume with sufficient data: must continue the SAME session, not create a new one --
    with db.session_scope() as s:
        ORC.resume_diagnosis_with_data(s, run_id, expected_version=v_after_start, data_sufficiency=_SUFFICIENT, actor_id="agent")

    with db.session_scope() as s:
        run = s.get(UnifiedWorkflowRun, run_id)
        assert run.diagnosis_run_ref == original_session_id, "resume must not replace the original diagnosis session with a new one"
        assert run.current_phase == "DESIGN", f"expected DESIGN, got {run.current_phase} (status={run.status}, pause={run.pause_reason}, blocked={run.blocked_reason})"

    with db.session_scope() as s:
        sess = diag_svc.get_session(s, original_session_id)
        assert sess.status in ("handoff_ready", "handed_off_to_design"), (
            f"the original session must have progressed past data_required all the way to "
            f"hypothesis generation/handoff, got status={sess.status!r}"
        )

        rows = s.execute(select(DiagnosisSession).where(DiagnosisSession.project_id == project_id)).scalars().all()
        assert len(rows) == 1, f"resume must not orphan the original session behind a second one; found {len(rows)} DiagnosisSession rows for this project"

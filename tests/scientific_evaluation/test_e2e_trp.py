"""doc05 §13.4 end-to-end scientific case: E. coli K-12, glucose, raising
L-tryptophan - the same real fixture Problem 04's own E2E suite uses
(`tests/engineering_design/fixtures.py::handoff_through_portfolio` /
`tests/engineering_design/test_end_to_end_trp.py`), carried one stage
further through Problem 05's full scientific review closed loop. Every
science fact used here comes from either the real curated knowledge base
(`knowledge/ddr_database/DDR-001_tryptophan.json`,
`knowledge/engineering_actions/action_database.json`) or is explicitly
labelled a test-fixture hypothesis in `tests/engineering_design/fixtures.py`
- doc05 §13.4's own instruction against hardcoding business logic to this
one case still holds: nothing in `harness/scientific_evaluation/*.py`
mentions tryptophan, PEP, or trp by name.
"""
from __future__ import annotations

from harness.db import session_scope
from harness.engineering_design.evaluation_service import evaluate_portfolio
from harness.engineering_design.models import CandidateDesign
from harness.scientific_evaluation import human_gate, service as sci_service

from tests.engineering_design.fixtures import handoff_through_portfolio


def test_e2e_trp_scientific_evaluation_closed_loop():
    with session_scope() as session:
        # -- Problem 3 -> Problem 4: real diagnosis handoff through a generated, diverse portfolio --------------
        proj, portfolio, candidates = handoff_through_portfolio(session, actor_id="pi", chassis="E. coli")
        roles = {c.portfolio_role for c in candidates}
        assert {"reference_or_control", "low_risk", "high_upside"} <= roles or {"reference_or_control", "low_risk"} <= roles
        evaluate_portfolio(session, portfolio_id=portfolio.portfolio_id, actor_id="system")

        # -- Problem 5: full scientific evaluation closed loop -----------------------------------------------
        result = sci_service.run_scientific_evaluation(session, portfolio_id=portfolio.portfolio_id, actor_id="pi")
        case = result["case"]

        # 1. Reviewer surfaces condition-transferability / growth trade-off / missing-control findings, not a single score:
        categories = {f.category for lst in result["findings_by_design"].values() for f in lst}
        assert "missing_control" in categories or "weak_causal_link" in categories

        # 2. No candidate wins purely because one dimension (e.g. production_potential) is high - a high_upside
        #    candidate must still be judged against risk/evidence/buildability, never a single overall_score:
        high_upside = [c for c in candidates if c.portfolio_role == "high_upside"]
        low_risk = [c for c in candidates if c.portfolio_role == "low_risk"]
        info_gain = [c for c in candidates if c.portfolio_role == "information_gain"]
        vectors_by_id = {v.candidate_id: v for v in result["vectors"]}
        if high_upside:
            hv = vectors_by_id[high_upside[0].design_id]
            assert set(hv.production_potential) == {"mode", "value_or_level", "unit", "basis", "source"}
            assert hv.risk["value_or_level"] is not None  # risk always explicitly reported, never dropped for a "promising" candidate

        # 3. easy-to-build and information-gain candidates are preserved in the Portfolio/comparison, not discarded:
        assert all(c.design_id in vectors_by_id for c in low_risk)
        assert all(c.design_id in vectors_by_id for c in info_gain)

        # 4. no real model available/requested -> honest not_computed everywhere, never a fabricated number:
        assert all(r.run_status == "not_computed" for lst in result["models_by_design"].values() for r in lst)

        # 5. revision -> new version + full findings lineage traceable:
        target = next(c for c in candidates if c.portfolio_role == "fallback" or c.portfolio_role == "low_risk")
        r2 = sci_service.apply_revision_and_reevaluate(
            session, evaluation_id=case.evaluation_id, design_id=target.design_id, actor_id="pi",
            modification_reason="e2e: address a raised finding with an alternate, better-evidenced target",
            genetic_modifications=[{"target_identifier": "ppc", "operation": "overexpression",
                                     "evidence_links": [{"source_type": "curated_knowledge", "reference": "ACT-003"}]}],
        )
        assert r2["new_candidate"].design_id != target.design_id
        assert r2["revision_cycle"].from_design_id == target.design_id
        new_case = r2["case"]

        # 6. no build release without Human Approval - not reached automatically:
        for c in [target, r2["new_candidate"]]:
            refreshed = session.get(CandidateDesign, c.design_id)
            assert refreshed.status != "approved_for_build"
        assert new_case.status != "approved_for_build"

        # 7. Human Gate: an authorized PI (not the candidate's own proposer) must explicitly decide:
        decision = human_gate.record_human_evaluation_decision(
            session, case=new_case, decision="hold", approver_id="pi_lead_not_proposer",
            rationale="e2e: PI reviewing before committing to build",
        )
        assert decision.decision == "hold"
        assert new_case.status == "held"

        # 8. Evaluation and decisions are written into the shared Memory ledger (Problem 2):
        from sqlalchemy import select
        from harness.projects.models import ProjectEvent
        events = session.execute(select(ProjectEvent).where(ProjectEvent.project_id == proj.project_id, ProjectEvent.event_type.like("EVAL_%"))).scalars().all()
        assert any(e.event_type == "EVAL_HUMAN_DECISION_RECORDED" for e in events)
        assert any(e.event_type == "EVAL_REVISION_CYCLE_COMPLETED" for e in events)

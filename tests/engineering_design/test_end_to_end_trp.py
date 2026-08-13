"""doc04 §13.7: the mandated E. coli K-12 / glucose / L-tryptophan
end-to-end acceptance case. Exercises the full DiagnosisDecision -> Strategy
-> Portfolio -> Evaluation -> Build/Test -> Human Approval -> DesignVersion
-> Outcome -> next-iteration loop through real service calls only.

Per doc04 §13.7's own instruction, this fixture verifies system capability
and is never hardcoded into `harness/engineering_design`'s generation logic
itself - see `tests/engineering_design/fixtures.py`'s module docstring.
"""
from __future__ import annotations

from harness import db
from harness.engineering_design import (
    build_test_planner,
    counterfactual_service,
    design_version_bridge,
    governance_service,
    memory_integration,
    outcome_service,
)
from harness.engineering_design.evaluation_service import evaluate_portfolio
from tests.engineering_design.fixtures import handoff_through_portfolio


def test_end_to_end_trp_precursor_limitation_case():
    with db.session_scope() as s:
        # -- 1. Diagnosis -> Strategy -> Portfolio (E. coli K-12, glucose) --
        proj, portfolio, candidates = handoff_through_portfolio(s, chassis="E. coli")
        assert proj.chassis == "E. coli"
        assert proj.chassis_version_or_genotype == "K-12 MG1655 wild-type"
        assert proj.temporal_and_environmental_context.get("carbon_source") == "glucose"

        roles = {c.portfolio_role for c in candidates}
        assert {"low_risk", "high_upside", "information_gain"}.issubset(roles)
        by_role = {c.portfolio_role: c for c in candidates}
        sigs = {r: memory_integration.modification_signature(by_role[r].genetic_modifications) for r in ("low_risk", "high_upside", "information_gain")}
        assert len({tuple(sorted(v)) for v in sigs.values()}) == 3  # three genuinely different architectures

        # -- 2. Evaluation: growth/burden/build-complexity/evidence/info-gain trade-offs --
        result = evaluate_portfolio(s, portfolio_id=portfolio.portfolio_id, actor_id="system")
        for did, ev in result["evaluations"].items():
            dims = {e["metric"] for e in ev.objective_vector}
            assert {"build_complexity", "growth_burden_risk"}.issubset(dims)
        info_gain_eval = result["evaluations"][by_role["information_gain"].design_id]
        assert info_gain_eval.expected_information_gain == "high"
        assert result["decision"]["pareto_status"]  # Pareto/trade-off preserved, not collapsed

        selected_id = result["decision"]["selected_design_ids"][0]
        selected = next(c for c in candidates if c.design_id == selected_id)

        # -- 3. Counterfactual: not connected for an out-of-domain candidate --
        run = counterfactual_service.request_counterfactual(s, design_id=by_role["information_gain"].design_id, adapter_name="vecoli", actor_id="system")
        assert run.capability_status == "unavailable"
        assert run.runtime_status == "not_computed"
        assert run.outputs == {}  # never a fabricated number

        # -- 4. Human selection boundary precedes any executable ValidationPlan --
        governance_service.request_human_approval(s, design_project_id=proj.design_project_id, actor_id="system")
        approval, cand, proj2 = governance_service.record_human_decision(s, design_id=selected.design_id, approver_id="pi_lead", decision="approved", approver_role="PI")

        # -- 5. Build/Test Package: no real materials/protocol -> never build_ready --
        thin_pkg = build_test_planner.draft_build_test_package(s, design_id=selected.design_id, actor_id="pi")
        assert thin_pkg.readiness != "build_ready"
        assert thin_pkg.readiness == "conceptual"

        full_pkg = build_test_planner.draft_build_test_package(
            s, design_id=selected.design_id, actor_id="pi", construction_concept="lambda-red recombineering",
            required_materials=["pKD46", "pCP20"], controls=[{"name": "wild-type baseline"}],
            replication_plan={"biological_replicates": 3}, sampling_plan=[{"time": "24h"}],
            qc_checkpoints=["colony PCR"], decision_rules=["titer increase >=10% vs baseline = success"],
        )
        assert full_pkg.readiness == "build_ready"

        # -- 6. Validation completeness -> build approval -> DesignVersion --
        governance_service.mark_planning_complete(s, design_project_id=proj.design_project_id, actor_id="system")
        assert cand.status == "approved_for_build"

        dv = design_version_bridge.bridge_to_design_version(s, design_id=selected.design_id, actor_id="pi_lead")
        assert dv.design_version_id

        governance_service.start_build(s, design_project_id=proj2.design_project_id, design_id=selected.design_id, actor_id="tech")
        proj3 = governance_service.mark_test_pending(s, design_project_id=proj2.design_project_id, actor_id="tech")
        assert proj3.status == "test_pending"

        # -- 7. Outcome ingestion: an underperforming result reopens diagnosis --
        outcome = outcome_service.ingest_outcome(
            s, design_id=selected.design_id, actor_id="tech",
            observed_results=[{"metric": "titer", "value": 0.9, "baseline_value": 1.0}],
            construction_verified=True, assay_qc_passed=True,
        )
        assert outcome.failure_classification in ("biological_underperformance", "inconclusive")
        assert outcome.decided_next_action in ("diagnosis_reopened", "next_iteration")

        history = memory_integration.design_lineage_history(s, design_project_id=proj.design_project_id)
        assert any(h["design_id"] == selected.design_id and h["outcomes"] for h in history)

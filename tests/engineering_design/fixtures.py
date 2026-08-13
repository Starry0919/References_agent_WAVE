"""Shared, minimal-but-credible fixture builders for the Problem-04 test
suite: a real E. coli K-12 / L-tryptophan / glucose diagnosis handoff, built
through the SAME Problem 02/03 service functions production code uses
(`harness.projects.service`, `harness.diagnosis.service`,
`harness.diagnosis.decision_service`, `harness.learning.service`) - never a
bare dict standing in for a `DiagnosisDecision`.

Not a hardcoded production answer: this fixture is only used to exercise
the test suite (per doc04 §13.7's own instruction, "此 fixture 用于验证系统
能力，不得把该案例的具体改造答案硬编码进生产逻辑" - none of these gene/
hypothesis strings appear anywhere in `harness/engineering_design`'s
generation logic itself, only in curated knowledge-base data and this test
fixture).
"""
from __future__ import annotations

from harness.diagnosis import decision_service as dec_svc
from harness.diagnosis import service as diag_svc
from harness.diagnosis.models import DiagnosisDecision, DiagnosisSession
from harness.diagnosis.grounding import derive_engineering_problem
from harness.diagnosis.findings import create_diagnosis_finding
from harness.engineering_design import handoff as handoff_mod, portfolio_service, project_service, strategy_service
from harness.engineering_design.loop import EngineeringDesignLoopController
from harness.engineering_design.models import CandidateDesign, DesignPortfolio, EngineeringDesignProject
from harness.learning import service as learning_svc
from harness.experiments.models import DataAsset, ExperimentPlan, ExperimentRun, Observation
from harness.ids import now
from harness.projects import service as proj_svc
from harness.projects.models import Project
from harness.workflow.gates import design_objective_gate

_loop = EngineeringDesignLoopController()


def build_trp_diagnosis(session, *, actor_id: str = "pi") -> tuple[Project, DiagnosisSession, DiagnosisDecision]:
    proj = proj_svc.create_project(
        session, name="Trp engineering", host_definition={"species": "E. coli", "strain": "K-12"},
        target_product="L-tryptophan", actor_id=actor_id,
    )
    sess = diag_svc.start_diagnosis_session(
        session, project_id=proj.project_id, actor_id=actor_id, biological_system={"species": "E. coli", "strain": "K-12"},
        baseline_observation_ids=[f"OBS-base-{proj.project_id}"],
    )
    subject_id, baseline_id = f"OBS-subject-{proj.project_id}", f"OBS-base-{proj.project_id}"
    plan_id, run_id = f"PLAN-{proj.project_id}", f"RUN-{proj.project_id}"
    sess.pending_request_context = {"observation_ids": [subject_id]}
    session.add(ExperimentPlan(experiment_plan_id=plan_id, project_id=proj.project_id,
        design_version_ids=[], hypotheses_tested=[], controls=[{"name":"matched baseline"}], factors=[],
        response_variables=["tryptophan_titer"], acceptance_criteria=[], created_by=actor_id, created_at=now()))
    session.add(ExperimentRun(experiment_run_id=run_id, experiment_plan_id=plan_id,
        executed_design_version_ids=[], execution_status="completed", operator_or_source="engineering-test-fixture"))
    # Explicit flush preserves FK order because these lightweight ORM models
    # intentionally expose ids rather than SQLAlchemy relationships.
    session.flush()
    condition={"medium":"M9","carbon_source":"glucose","temperature_c":37,"oxygenation":"DO 30%","process_mode":"batch"}
    for oid,value,label in ((subject_id,8.0,"subject"),(baseline_id,12.0,"baseline")):
        aid=f"ASSET-{label}-{proj.project_id}"
        session.add(DataAsset(data_asset_id=aid,project_id=proj.project_id,experiment_run_id=run_id,
            file_uri=f"fixture://{aid}.csv",checksum=aid,assay_type="titer",qc_status="passed",
            provenance={"instrument":"HPLC","fixture":"engineering_design"},uploaded_by=actor_id,uploaded_at=now()))
        session.add(Observation(observation_id=oid,project_id=proj.project_id,data_asset_ids=[aid],
            condition_ref=condition,metric="tryptophan_titer",value=value,unit="g/L",qc_status="passed",
            analysis_pipeline_version="hplc-fixture-v1",created_at=now()))
    session.flush()
    problem = derive_engineering_problem(session,diagnosis_session_id=sess.diagnosis_session_id,
        observation_id=subject_id,comparison_observation_id=baseline_id)
    fam = learning_svc.create_hypothesis_family(session, project_id=proj.project_id, title="Trp titer bottleneck")

    hyp_precursor = learning_svc.propose_hypothesis(
        session, project_id=proj.project_id, hypothesis_family_id=fam.hypothesis_family_id,
        statement="Precursor (PEP/E4P) supply limitation from imbalanced central carbon flux constrains L-tryptophan titer",
        actor_id=actor_id, mechanism_class="biological_mechanism", posterior_status="strongly_supported", confidence="medium",
    )
    hyp_feedback = learning_svc.propose_hypothesis(
        session, project_id=proj.project_id, hypothesis_family_id=fam.hypothesis_family_id,
        statement="Feedback inhibition of anthranilate synthase (TrpE) and attenuation of the trp operon independently caps flux regardless of precursor supply",
        actor_id=actor_id, mechanism_class="biological_mechanism", posterior_status="weakly_supported", confidence="low",
    )
    hyp_measurement = learning_svc.propose_hypothesis(
        session, project_id=proj.project_id, hypothesis_family_id=fam.hypothesis_family_id,
        statement="The observed titer plateau reflects a measurement/QC artifact rather than a true biological limitation",
        actor_id=actor_id, mechanism_class="measurement_data", posterior_status="untested", confidence="low",
    )

    create_diagnosis_finding(
        session, project_id=proj.project_id, engineering_problem_id=problem.engineering_problem_id,
        constraint_hypothesis_id=hyp_precursor.hypothesis_version_id, mechanism_type="biological_mechanism",
        causal_graph={"nodes":["observed titer deficit","precursor-supply hypothesis"],"edges":[["observed titer deficit","precursor-supply hypothesis"]]},
        confidence_derivation={"basis":"QC-passed matched baseline plus versioned hypothesis","confidence":"medium"},
        unresolved_alternatives=[hyp_feedback.hypothesis_version_id,hyp_measurement.hypothesis_version_id],
        falsifiers=["matched perturbation does not alter precursor or titer readouts"],
        engineering_consequences=[{"type":"candidate_generation_boundary","action":"evaluate precursor strategies"}],
        validation_needs=[{"readout":"tryptophan_titer","baseline":baseline_id}], actor_id=actor_id,
    )

    decision = dec_svc.create_diagnosis_decision(
        session, diagnosis_session_id=sess.diagnosis_session_id, diagnosis_version=1, actor_id=actor_id,
        context_reference={"medium": "M9", "carbon_source": "glucose", "temperature_c": 37, "oxygenation": "DO 30%", "process_mode": "batch"},
        leading_hypothesis_ids=[hyp_precursor.hypothesis_version_id, hyp_feedback.hypothesis_version_id],
        supported_hypothesis_ids=[hyp_precursor.hypothesis_version_id, hyp_feedback.hypothesis_version_id],
        alternatives_not_excluded_ids=[hyp_measurement.hypothesis_version_id],
        contradictions=[], confidence_representation={"precursor": "medium", "feedback": "low"},
        uncertainty="no GEM/kinetic model has been run yet; specific gene-level targets are not individually experimentally verified",
        evidence_references=["DDR-001"], stopping_reason="actionable_stop", allowed_next_action="handoff_to_design",
        engineering_value_assessment={"biological_importance": "high", "engineering_leverage": "high"},
        handoff_status="approved", human_approval={"approver": "pi", "decision": "approved"},
    )
    return proj, sess, decision


def build_evidence_limited_probe_diagnosis(session, *, actor_id: str = "pi") -> tuple[Project, DiagnosisSession, DiagnosisDecision]:
    """A diagnosis that has NOT reached `actionable_stop` - only usable as
    a `diagnostic_probe` handoff with explicit human approval."""
    proj = proj_svc.create_project(
        session, name="Trp engineering (unresolved)", host_definition={"species": "E. coli", "strain": "K-12"},
        target_product="L-tryptophan", actor_id=actor_id,
    )
    sess = diag_svc.start_diagnosis_session(session, project_id=proj.project_id, actor_id=actor_id, biological_system={"species": "E. coli", "strain": "K-12"})
    fam = learning_svc.create_hypothesis_family(session, project_id=proj.project_id, title="Trp titer bottleneck (unresolved)")
    hyp_a = learning_svc.propose_hypothesis(
        session, project_id=proj.project_id, hypothesis_family_id=fam.hypothesis_family_id,
        statement="Precursor supply limitation constrains titer", actor_id=actor_id, mechanism_class="biological_mechanism",
        posterior_status="weakly_supported", confidence="low",
    )
    hyp_b = learning_svc.propose_hypothesis(
        session, project_id=proj.project_id, hypothesis_family_id=fam.hypothesis_family_id,
        statement="Feedback inhibition (TrpE) independently caps flux", actor_id=actor_id, mechanism_class="biological_mechanism",
        posterior_status="weakly_supported", confidence="low",
    )
    decision = dec_svc.create_diagnosis_decision(
        session, diagnosis_session_id=sess.diagnosis_session_id, diagnosis_version=1, actor_id=actor_id,
        context_reference={"medium": "M9", "carbon_source": "glucose"},
        leading_hypothesis_ids=[hyp_a.hypothesis_version_id, hyp_b.hypothesis_version_id],
        supported_hypothesis_ids=[hyp_a.hypothesis_version_id],
        alternatives_not_excluded_ids=[hyp_b.hypothesis_version_id],
        contradictions=["hyp_a and hyp_b both weakly supported; no discriminating test run yet"],
        confidence_representation={"precursor": "low", "feedback": "low"}, uncertainty="not enough evidence to rank",
        evidence_references=[], stopping_reason="evidence_limited_stop", allowed_next_action="human_review",
        engineering_value_assessment=None, handoff_status="not_applicable", human_approval=None,
    )
    return proj, sess, decision


def handoff_through_portfolio(session, *, actor_id: str = "pi", chassis: str = "E. coli") -> tuple[EngineeringDesignProject, DesignPortfolio, list[CandidateDesign]]:
    """Drives the loop through `diagnostic_blocked -> ... -> portfolio_generated`
    using the real service/loop functions - the common setup every test that
    needs an evaluatable portfolio starts from."""
    _, _, decision = build_trp_diagnosis(session, actor_id=actor_id)
    proj, handoff = handoff_mod.ingest_diagnosis_decision(
        session, decision=decision, actor_id="agent", chassis=chassis, chassis_version_or_genotype="K-12 MG1655 wild-type",
    )

    proj = project_service.set_objectives(
        session, design_project_id=proj.design_project_id, primary_metrics=[{"metric": "titer", "unit": "g/L"}], secondary_metrics=[],
        hard_constraints=[{"constraint": "no essential gene knockout", "type": "no_essential_gene_knockout"}], preferences_or_weights=[],
        available_resources={"materials": ["pKD46", "pCP20"], "instruments": ["HPLC"]}, expected_version=proj.version, actor_id=actor_id,
    )
    gate = design_objective_gate(has_primary_metrics=True, has_hard_constraints_declared=True)
    proj = _loop.confirm_objective(session, proj, actor_id=actor_id, objective_gate_result=gate)

    strategy_service.generate_and_persist_strategies(session, design_project_id=proj.design_project_id, handoff_id=handoff.handoff_id, actor_id="system")
    portfolio, candidates, _ = portfolio_service.generate_and_persist_portfolio(session, design_project_id=proj.design_project_id, actor_id="system")
    proj = _loop.generate_portfolio(session, proj, actor_id="system")
    return proj, portfolio, candidates

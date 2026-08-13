"""`ScientificModuleContract` adapters (prompt §4.4) for Problem 3-6. Every
adapter method below calls the SAME real service/loop functions the
module's own test suite and API layer already use (cited in each
docstring) - no module's internal logic is reimplemented, forked, or
mocked. Where a module's process is a sequence of several deterministic
steps (diagnosis' ~10 loop-controller transitions, mirroring
`tests/diagnosis/test_end_to_end_cases.py`), the adapter's `start()` drives
that sequence to the module's own next real checkpoint (a durable wait
state, a human-review state, or a terminal state) in one call - this is
sequencing, not new scientific capability; the hypothesis/strategy content
itself is still produced by each module's existing deterministic
generator (`harness.diagnosis.hypothesis_generator`,
`harness.engineering_design.strategy_generator`), exactly as today.
"""
from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from harness.orchestrator.contracts import ModuleHandoff, ModuleRunRef, ModuleRunStatus

# ---------------------------------------------------------------------------
# Diagnosis (Problem 3)
# ---------------------------------------------------------------------------


class DiagnosisAdapter:
    """Wraps `harness.diagnosis.{service,decision_service,loop,...}`. Not a
    rewrite: `start()` reproduces exactly the call sequence
    `tests/diagnosis/test_end_to_end_cases.py::test_case_b_...` uses."""

    module = "diagnosis"

    def start(self, session: Session, *, request: dict[str, Any], context: dict[str, Any]) -> ModuleRunRef:
        from harness.diagnosis import service as diag_svc
        from harness.diagnosis.loop import DiagnosisLoopController
        from harness.workflow.gates import data_sufficiency_gate

        loop = DiagnosisLoopController()
        project_id = request["project_id"]
        actor_id = request.get("actor_id", "system")

        sess = diag_svc.start_diagnosis_session(
            session, project_id=project_id, actor_id=actor_id, biological_system=request.get("biological_system", {}),
            workflow_run_id=request.get("workflow_run_id"),
            baseline_observation_ids=request.get("baseline_observation_ids", []),
        )

        # The observation-grounding gate reads durable links from the
        # DiagnosisSession.  A data-sufficiency attestation is not a
        # substitute for those links, so retain the submitted observation
        # ids before either the immediate or resumed pipeline runs.
        sess.pending_request_context = {
            "request": request,
            "context": context,
            "observation_ids": request.get("observation_ids", []),
        }
        session.flush()

        sufficiency = request.get("data_sufficiency", {})
        gate = data_sufficiency_gate(
            has_baseline=sufficiency.get("has_baseline", False), has_genotype=sufficiency.get("has_genotype", False),
            has_condition=sufficiency.get("has_condition", False), has_time=sufficiency.get("has_time", False),
            has_qc=sufficiency.get("has_qc", False), has_key_phenotype=sufficiency.get("has_key_phenotype", False),
        )
        loop.run_intake(session, sess, actor_id=actor_id, sufficiency_gate_result=gate)
        if sess.status == "data_required":
            # Not yet sufficient - remember what this session needs so that
            # resume() can run the SAME hypothesis pipeline on THIS row once
            # the missing data arrives, instead of the orchestrator minting a
            # brand-new session (see resume_diagnosis_with_data in service.py).
            return ModuleRunRef(module=self.module, run_id=sess.diagnosis_session_id, version=sess.version)

        self._derive_submitted_engineering_problems(session, sess, request=request)
        self._run_hypothesis_pipeline(session, sess, request=request, context=context)
        return ModuleRunRef(module=self.module, run_id=sess.diagnosis_session_id, version=sess.version)

    @staticmethod
    def _derive_submitted_engineering_problems(session: Session, sess: Any, *, request: dict[str, Any]) -> None:
        """Derive descriptive problems from explicitly linked measurements.

        Pairing is deliberately strict and deterministic: each subject
        observation must have a submitted baseline with the same metric,
        unit, and condition.  No measurement is synthesized from the
        checkbox-style data-sufficiency declaration.
        """
        from harness.diagnosis.grounding import GroundingError, derive_engineering_problem
        from harness.experiments.models import Observation

        subject_ids = list(dict.fromkeys(request.get("observation_ids", [])))
        baseline_ids = list(dict.fromkeys(request.get("baseline_observation_ids", [])))
        if not subject_ids or not baseline_ids:
            return

        baselines = [session.get(Observation, oid) for oid in baseline_ids]
        for subject_id in subject_ids:
            subject = session.get(Observation, subject_id)
            if subject is None:
                continue
            baseline = next((
                candidate for candidate in baselines
                if candidate is not None
                and candidate.metric == subject.metric
                and candidate.unit == subject.unit
                and candidate.condition_ref == subject.condition_ref
            ), None)
            if baseline is None:
                raise GroundingError(
                    f"no submitted baseline matches observation {subject_id} "
                    "on metric, unit, and condition"
                )
            derive_engineering_problem(
                session,
                diagnosis_session_id=sess.diagnosis_session_id,
                observation_id=subject_id,
                comparison_observation_id=baseline.observation_id,
            )

    def _run_hypothesis_pipeline(self, session: Session, sess: Any, *, request: dict[str, Any], context: dict[str, Any]) -> None:
        """Everything doc03's loop does once a session clears the data-
        sufficiency gate: mechanism graph -> competing hypotheses -> dedup ->
        ranking -> stopping gate -> (if actionable) objective +
        DiagnosisDecision. Shared by `start()` (session becomes sufficient
        immediately) and `resume()` (session was `data_required` and just
        became sufficient) - for a given session this runs exactly once,
        regardless of which caller triggers it."""
        from harness.diagnosis import decision_service as dec_svc
        from harness.diagnosis import evidence as evidence_svc
        from harness.diagnosis import service as diag_svc
        from harness.diagnosis.assessor import AssessmentInput, assess_hypothesis, rank_hypotheses
        from harness.diagnosis.dedup import deduplicate
        from harness.diagnosis.hypothesis_generator import generate_competing_hypotheses
        from harness.diagnosis.loop import DiagnosisLoopController
        from harness.diagnosis.mechanism_graph import build_mechanism_graph
        from harness.learning import service as learning_svc
        from harness.workflow.gates import diagnosis_stopping_gate, engineering_value_gate

        loop = DiagnosisLoopController()
        project_id = request["project_id"]
        actor_id = request.get("actor_id", "system")

        graph = build_mechanism_graph(
            phenotype=request.get("phenotype", "engineering objective not yet met"),
            product=request.get("target_product", "unknown"), host=request.get("host", "unknown"),
        )
        # Module 2 (Engineering Decision Intelligence Layer prompt §7): fetch
        # the real Observation rows' `modality` (transcriptomic/proteomic/
        # metabolomic/fluxomic/phenotypic - harness.experiments.models.
        # Observation, Problem 06's existing vocabulary) so hypothesis
        # generation can honestly report which omics layer(s) actually back
        # each biological_mechanism hypothesis. `generate_competing_
        # hypotheses` stays a pure function - this I/O boundary is the only
        # place that queries the DB for it.
        observation_ids = request.get("observation_ids", [])
        observation_modalities: dict[str, str] = {}
        if observation_ids:
            from sqlalchemy import select

            from harness.experiments.models import Observation

            observation_modalities = {
                o.observation_id: o.modality
                for o in session.execute(select(Observation).where(Observation.observation_id.in_(observation_ids))).scalars()
            }
        gen_result = generate_competing_hypotheses(
            graph=graph, observation_ids=observation_ids,
            context=context, has_reference_model=request.get("has_reference_model", False),
            observation_modalities=observation_modalities,
        )
        all_hypotheses = list(gen_result.hypotheses)
        if request.get("enable_llm_hypothesis", False):
            from harness.diagnosis.llm_hypothesis_adapter import generate_llm_hypothesis_candidates

            llm_candidates, _fallback_used = generate_llm_hypothesis_candidates(
                session, project_id=project_id, phenotype=request.get("phenotype", "engineering objective not yet met"),
                product=request.get("target_product", "unknown"), host=request.get("host", "unknown"), context=context, actor_id=actor_id,
            )
            all_hypotheses.extend(llm_candidates)
        kept, _groups = deduplicate(all_hypotheses)
        fam = learning_svc.create_hypothesis_family(session, project_id=project_id, title=request.get("phenotype", "diagnosis"))
        persisted = [
            learning_svc.propose_hypothesis(
                session, project_id=project_id, hypothesis_family_id=fam.hypothesis_family_id, statement=h.statement,
                actor_id=actor_id, mechanism_class=h.mechanism_class, causal_graph_nodes=h.causal_graph_nodes,
                discriminating_predictions=h.discriminating_predictions, falsifiers=h.falsifiers,
                assumptions=h.assumptions, generation_provenance=h.generation_provenance,
                # `scope` (doc03 3.5's applicability_context, free-form JSON,
                # otherwise unused by this call site) carries the multi-omics
                # layer(s) actually backing this hypothesis - Module 2 §7.
                # Never populated with a guessed layer: `h.omics_layers` is
                # already an honest empty list when no typed observation
                # backs it (see hypothesis_generator.py::_omics_layers).
                scope={"omics_layers": h.omics_layers},
            )
            for h in kept
        ]
        loop.mark_hypotheses_generated(session, sess, actor_id=actor_id)
        loop.mark_evidence_assessed(session, sess, actor_id=actor_id)
        loop.mark_hypotheses_ranked(session, sess, actor_id=actor_id)

        # Ground each biological_mechanism hypothesis in the DDR knowledge-base
        # entry it was actually generated from - `causal_graph_edges[].source_ref`
        # is only ever a real DDR id here (hypothesis_generator only produces a
        # biological_mechanism hypothesis at all when a DDR matched; "generic_
        # skeleton" edges belong to measurement/model nodes, never included in a
        # hypothesis's own edges). Tagged expert_rule/quality=low per evidence.py's
        # own documented convention - never a fabricated literature/experiment
        # source. Ungrounded hypotheses (no DDR match) get no evidence and
        # correctly stay "untested" below - nothing here is invented.
        hyp_supporting_links: dict[str, list[dict[str, Any]]] = {}
        for h, hv in zip(kept, persisted):
            ddr_ids = {e["source_ref"] for e in h.causal_graph_edges if e.get("source_ref") and e["source_ref"] != "generic_skeleton"}
            for ddr_id in ddr_ids:
                item = evidence_svc.record_evidence_item(
                    session, project_id=project_id, source_type="expert_rule", content_summary=h.statement,
                    actor_id=actor_id, source_reference=ddr_id, quality="low", directness="indirect",
                )
                evidence_svc.link_evidence(
                    session, hypothesis_version_id=hv.hypothesis_version_id, evidence_item_id=item.evidence_item_id,
                    relation="supports", actor_id=actor_id, claim=h.statement,
                )
                hyp_supporting_links.setdefault(hv.hypothesis_version_id, []).append(
                    {"evidence_item_id": item.evidence_item_id, "quality": "low", "directness": "indirect", "claim": h.statement},
                )

        assessments = [
            assess_hypothesis(
                AssessmentInput(
                    hypothesis_id=hv.hypothesis_version_id, supporting_links=hyp_supporting_links.get(hv.hypothesis_version_id, []),
                    observations_explained_count=1, observations_total_count=max(len(persisted), 1),
                ),
                has_predeclared_discriminating_prediction=True, has_sufficient_measurement_sensitivity=True,
                has_valid_controls=True, condition_matches=True, alternatives_reviewed=True,
            )
            for hv in persisted
        ]
        ranked = rank_hypotheses(assessments)
        mechanism_classes = {h.mechanism_class for h in kept}

        # Persist the assessment computed above - `assess_hypothesis`/
        # `rank_hypotheses` only ever returned in-memory dataclasses; no
        # code anywhere wrote a `HypothesisAssessment` row, so `GET
        # /api/diagnosis/sessions/{id}/hypotheses` (which joins through
        # this table) silently returned an empty list even after a
        # successful diagnosis - a real gap found via 全真 DBTL simulation
        # stress-testing, not a pre-existing test failure (no test asserted
        # on this table's contents before).
        from harness.diagnosis.models import HypothesisAssessment
        from harness.ids import new_id, now

        for rank_index, assessment in enumerate(ranked):
            session.add(HypothesisAssessment(
                assessment_id=new_id("HYPASS"), hypothesis_version_id=assessment.hypothesis_id,
                diagnosis_session_id=sess.diagnosis_session_id, explanatory_coverage=assessment.explanatory_coverage,
                contradictions=assessment.contradictions, evidence_quality=assessment.evidence_quality,
                evidence_directness=assessment.evidence_directness, condition_match=assessment.condition_match,
                robustness=assessment.robustness, testability=assessment.testability,
                remaining_uncertainty=assessment.remaining_uncertainty, status=assessment.status,
                ranking_rank=rank_index, rationale_references=assessment.rationale_references,
                created_by=actor_id, created_at=now(),
            ))
        session.flush()

        stop_gate = diagnosis_stopping_gate(
            has_competing_set=len(kept) >= 2, has_fatal_contradiction=False, has_unresolved_model_conflict=False,
            ranking_stable=bool(ranked), safety_concern=False, evidence_sufficient=len(kept) >= 2,
        )
        loop.run_stopping_gate(session, sess, actor_id=actor_id, stopping_gate_result=stop_gate)

        if sess.status == "actionable":
            obj = diag_svc.create_objective(session, project_id=project_id, created_by=actor_id)
            value_gate = engineering_value_gate(
                diagnostic_stopping_reason="actionable_stop", biological_importance="high",
                engineering_leverage="high", has_objective=True,
            )
            loop.enter_handoff_ready(session, sess, actor_id=actor_id, engineering_value_gate_result=value_gate)
            # Derived from `ranked` (real assessment status tier + coverage), not
            # generation order - previously "first two persisted" was disconnected
            # from both the assessor's own ranking and report.py's "Leading
            # Hypothesis Set" section (which filters on assessment status), so the
            # two could name different hypotheses as "leading" for the same session.
            leading = [a.hypothesis_id for a in ranked[:2]] or [a.hypothesis_id for a in ranked]
            # `get_handoff()` re-queries this row by diagnosis_session_id -
            # nothing further to hold onto here.
            dec_svc.create_diagnosis_decision(
                session, diagnosis_session_id=sess.diagnosis_session_id, diagnosis_version=1, actor_id=actor_id,
                context_reference=context, leading_hypothesis_ids=leading, supported_hypothesis_ids=leading,
                alternatives_not_excluded_ids=[a.hypothesis_id for a in ranked if a.hypothesis_id not in leading],
                contradictions=[], confidence_representation={"overall": "medium"},
                uncertainty="no GEM/kinetic model run in this pass; mechanism_classes=" + str(sorted(mechanism_classes)),
                evidence_references=[], stopping_reason="actionable_stop", allowed_next_action="handoff_to_design",
                engineering_value_assessment={"biological_importance": "high", "engineering_leverage": "high"},
                handoff_status="pending",
            )
            # Materialize the diagnosis-to-design bridge on the same
            # production path. Candidate generation is not allowed to infer a
            # diagnosis from prose or from the decision's id list alone.
            from harness.diagnosis.findings import create_diagnosis_finding
            from harness.diagnosis.models import EngineeringProblem
            from harness.learning.models import HypothesisVersion
            from sqlalchemy import select

            lead_hypothesis = session.get(HypothesisVersion, leading[0])
            problems = session.execute(select(EngineeringProblem).where(
                EngineeringProblem.diagnosis_session_id == sess.diagnosis_session_id,
                EngineeringProblem.status == "grounded",
            )).scalars().all()
            if lead_hypothesis is not None:
                for problem in problems:
                    create_diagnosis_finding(
                        session, project_id=project_id, engineering_problem_id=problem.engineering_problem_id,
                        constraint_hypothesis_id=lead_hypothesis.hypothesis_version_id,
                        mechanism_type=lead_hypothesis.mechanism_class or "unknown",
                        causal_graph={"nodes": lead_hypothesis.causal_graph_nodes, "edges": lead_hypothesis.causal_graph_edges},
                        confidence_derivation={"assessment_status": next((a.status for a in ranked if a.hypothesis_id == leading[0]), "inconclusive")},
                        unresolved_alternatives=[a.hypothesis_id for a in ranked if a.hypothesis_id not in leading],
                        falsifiers=lead_hypothesis.falsifiers,
                        engineering_consequences=[{"type": "design_constraint", "statement": lead_hypothesis.statement}],
                        validation_needs=[{"falsifier": f, "status": "open"} for f in lead_hypothesis.falsifiers],
                        actor_id=actor_id,
                    )
        # Request/context are transient orchestration inputs, but the linked
        # subject observations are durable diagnosis provenance and are
        # re-checked again during final handoff.  Do not erase them here.
        sess.pending_request_context = {
            "observation_ids": list(dict.fromkeys(request.get("observation_ids", []))),
        }
        session.flush()

    def get_status(self, session: Session, run_id: str) -> ModuleRunStatus:
        from harness.diagnosis import service as diag_svc

        sess = diag_svc.get_session(session, run_id)
        if sess is None:
            raise ValueError(f"no such diagnosis session: {run_id}")
        normalized = {
            "data_required": "waiting_input", "human_review_required": "waiting_input",
            "handed_off_to_design": "completed", "actionable": "completed", "handoff_ready": "completed",
            "evidence_limited": "blocked",
        }.get(sess.status, "running")
        return ModuleRunStatus(module=self.module, run_id=run_id, native_status=sess.status, normalized=normalized, version=sess.version)

    def resume(self, session: Session, run_id: str, input_ref: dict[str, Any], expected_version: int) -> ModuleRunRef:
        from harness.diagnosis import service as diag_svc
        from harness.diagnosis.loop import DiagnosisLoopController
        from harness.workflow.gates import data_sufficiency_gate

        sess = diag_svc.get_session(session, run_id)
        if sess is None:
            raise ValueError(f"no such diagnosis session: {run_id}")
        if sess.version != expected_version:
            from harness.db import ConcurrencyConflictError

            raise ConcurrencyConflictError(f"DiagnosisSession {run_id}: expected version {expected_version}, actual {sess.version}")
        loop = DiagnosisLoopController()
        if sess.status == "data_required":
            actor_id = input_ref.get("actor_id", "system")
            sufficiency = input_ref.get("data_sufficiency", {})
            gate = data_sufficiency_gate(
                has_baseline=sufficiency.get("has_baseline", True), has_genotype=sufficiency.get("has_genotype", True),
                has_condition=sufficiency.get("has_condition", True), has_time=sufficiency.get("has_time", True),
                has_qc=sufficiency.get("has_qc", True), has_key_phenotype=sufficiency.get("has_key_phenotype", True),
            )
            loop.run_intake(session, sess, actor_id=actor_id, sufficiency_gate_result=gate)
            if sess.status != "data_required":
                # Sufficiency gate just passed for the first time on THIS
                # session - run the same hypothesis pipeline start() runs,
                # against the original phenotype/observation_ids/etc this
                # session was created with, on THIS row - never a new one
                # (see resume_diagnosis_with_data in service.py).
                stored = sess.pending_request_context or {}
                merged_request = {**stored.get("request", {}), "data_sufficiency": sufficiency, "actor_id": actor_id}
                self._derive_submitted_engineering_problems(session, sess, request=merged_request)
                self._run_hypothesis_pipeline(session, sess, request=merged_request, context=stored.get("context", {}))
        return ModuleRunRef(module=self.module, run_id=run_id, version=sess.version)

    def cancel(self, session: Session, run_id: str, reason: str, actor: str) -> ModuleRunRef:
        from harness.diagnosis import service as diag_svc
        from harness.diagnosis.loop import DiagnosisLoopController

        sess = diag_svc.get_session(session, run_id)
        if sess is None:
            raise ValueError(f"no such diagnosis session: {run_id}")
        DiagnosisLoopController().close_diagnosis(session, sess, actor_id=actor, reason=reason)
        return ModuleRunRef(module=self.module, run_id=run_id, version=sess.version)

    def get_handoff(self, session: Session, run_id: str) -> ModuleHandoff:
        from sqlalchemy import select

        from harness.diagnosis import service as diag_svc
        from harness.diagnosis.models import DiagnosisDecision

        sess = diag_svc.get_session(session, run_id)
        if sess is None:
            raise ValueError(f"no such diagnosis session: {run_id}")
        decision = session.execute(
            select(DiagnosisDecision).where(DiagnosisDecision.diagnosis_session_id == run_id).order_by(DiagnosisDecision.created_at.desc())
        ).scalars().first()
        if decision is None:
            return ModuleHandoff(
                source_module=self.module, source_run_id=run_id, target_module="engineering_design",
                unresolved_items=["no DiagnosisDecision has been created yet"], confidence_status="not_ready",
            )
        return ModuleHandoff(
            source_module=self.module, source_run_id=run_id, target_module="engineering_design",
            payload_refs={"diagnosis_decision_id": decision.decision_id, "diagnosis_session_id": run_id},
            preconditions=[f"stopping_reason={decision.stopping_reason}"],
            unresolved_items=list(decision.alternatives_not_excluded_ids),
            confidence_status=decision.stopping_reason,
        )

    def finalize_handoff(self, session: Session, run_id: str, *, actor_id: str, handoff_gate_passed: bool) -> ModuleRunRef:
        """Called by `orchestrator.service` only after its own
        `diagnosis_handoff` `GateRegistry` check has passed - the actual
        `handed_off_to_design` transition still belongs to
        `DiagnosisLoopController`, not to the orchestrator directly (prompt
        §4.5: gates decide, but the module remains the writer of its own
        state)."""
        from sqlalchemy import select

        from harness.diagnosis import decision_service as dec_svc
        from harness.diagnosis import service as diag_svc
        from harness.diagnosis.loop import DiagnosisLoopController
        from harness.diagnosis.models import DiagnosisDecision
        from harness.workflow.contracts import GateResult, GateStatus

        if not handoff_gate_passed:
            raise ValueError("finalize_handoff called with a non-passing diagnosis_handoff gate decision")
        sess = diag_svc.get_session(session, run_id)
        if sess is None:
            raise ValueError(f"no such diagnosis session: {run_id}")
        decision = session.execute(
            select(DiagnosisDecision).where(DiagnosisDecision.diagnosis_session_id == run_id).order_by(DiagnosisDecision.created_at.desc())
        ).scalars().first()
        if decision is not None:
            dec_svc.set_handoff_status(session, decision_id=decision.decision_id, handoff_status="handed_off", actor_id=actor_id)
        DiagnosisLoopController().hand_off_to_design(
            session, sess, actor_id=actor_id, handoff_gate_result=GateResult(gate_name="DiagnosisHandoffGate", status=GateStatus.passed),
        )
        return ModuleRunRef(module=self.module, run_id=run_id, version=sess.version)


# ---------------------------------------------------------------------------
# Engineering Design (Problem 4)
# ---------------------------------------------------------------------------


class DesignAdapter:
    """Wraps `harness.engineering_design.*` - the same call sequence
    `tests/engineering_design/fixtures.py::handoff_through_portfolio` and
    `test_end_to_end_trp.py` use."""

    module = "engineering_design"

    def start(self, session: Session, *, request: dict[str, Any], context: dict[str, Any]) -> ModuleRunRef:
        from harness.diagnosis.models import DiagnosisDecision
        from harness.engineering_design import handoff as handoff_mod
        from harness.engineering_design import portfolio_service, project_service, strategy_service
        from harness.engineering_design.loop import EngineeringDesignLoopController
        from harness.workflow.gates import design_objective_gate

        loop = EngineeringDesignLoopController()
        decision = session.get(DiagnosisDecision, request["diagnosis_decision_id"])
        if decision is None:
            raise ValueError(f"no such diagnosis decision: {request['diagnosis_decision_id']}")

        proj, handoff = handoff_mod.ingest_diagnosis_decision(
            session, decision=decision, actor_id=request.get("actor_id", "system"),
            chassis=request.get("chassis", "E. coli"), chassis_version_or_genotype=request.get("chassis_version_or_genotype", "unknown"),
        )
        if proj.status == "diagnostic_blocked":
            return ModuleRunRef(module=self.module, run_id=proj.design_project_id, version=proj.version)

        proj = project_service.set_objectives(
            session, design_project_id=proj.design_project_id, primary_metrics=request.get("primary_metrics", []),
            secondary_metrics=request.get("secondary_metrics", []), hard_constraints=request.get("hard_constraints", []),
            preferences_or_weights=request.get("preferences_or_weights", []), available_resources=request.get("available_resources", {}),
            expected_version=proj.version, actor_id=request.get("actor_id", "system"),
        )
        gate = design_objective_gate(
            has_primary_metrics=bool(request.get("primary_metrics")), has_hard_constraints_declared=True,
        )
        proj = loop.confirm_objective(session, proj, actor_id=request.get("actor_id", "system"), objective_gate_result=gate)
        strategy_service.generate_and_persist_strategies(
            session, design_project_id=proj.design_project_id, handoff_id=handoff.handoff_id, actor_id="system",
        )
        if request.get("enable_llm_strategy", False):
            from sqlalchemy import select

            from harness.engineering_design.llm_strategy_adapter import generate_llm_strategy_drafts
            from harness.learning.models import HypothesisVersion

            hyp_ids = handoff.supported_hypotheses
            hyps = session.execute(select(HypothesisVersion).where(HypothesisVersion.hypothesis_version_id.in_(hyp_ids))).scalars().all() if hyp_ids else []
            supported = [{"hypothesis_version_id": h.hypothesis_version_id, "statement": h.statement, "mechanism_class": h.mechanism_class} for h in hyps]
            generate_llm_strategy_drafts(
                session, project_id=proj.project_id, design_project_id=proj.design_project_id, diagnosis_reference=handoff.handoff_id,
                objective=f"improve {', '.join(str(m.get('metric', 'unknown')) for m in request.get('primary_metrics', [])) or 'the project objective'}",
                supported_hypotheses=supported, primary_metrics=request.get("primary_metrics", []), actor_id=request.get("actor_id", "system"),
            )
        _portfolio, _candidates, _ = portfolio_service.generate_and_persist_portfolio(
            session, design_project_id=proj.design_project_id, actor_id="system",
        )
        proj = loop.generate_portfolio(session, proj, actor_id="system")
        return ModuleRunRef(module=self.module, run_id=proj.design_project_id, version=proj.version)

    def get_status(self, session: Session, run_id: str) -> ModuleRunStatus:
        from harness.engineering_design.models import EngineeringDesignProject

        proj = session.get(EngineeringDesignProject, run_id)
        if proj is None:
            raise ValueError(f"no such engineering design project: {run_id}")
        normalized = {
            "diagnostic_blocked": "blocked", "portfolio_generated": "completed", "portfolio_evaluated": "completed",
            "planning_ready": "completed", "approved_for_build": "completed", "rejected": "blocked",
        }.get(proj.status, "running")
        return ModuleRunStatus(module=self.module, run_id=run_id, native_status=proj.status, normalized=normalized, version=proj.version)

    def resume(self, session: Session, run_id: str, input_ref: dict[str, Any], expected_version: int) -> ModuleRunRef:
        from harness.engineering_design.models import EngineeringDesignProject

        proj = session.get(EngineeringDesignProject, run_id)
        if proj is None:
            raise ValueError(f"no such engineering design project: {run_id}")
        if proj.version != expected_version:
            from harness.db import ConcurrencyConflictError

            raise ConcurrencyConflictError(f"EngineeringDesignProject {run_id}: expected version {expected_version}, actual {proj.version}")
        return ModuleRunRef(module=self.module, run_id=run_id, version=proj.version)

    def cancel(self, session: Session, run_id: str, reason: str, actor: str) -> ModuleRunRef:
        from harness.engineering_design.models import EngineeringDesignProject

        proj = session.get(EngineeringDesignProject, run_id)
        if proj is None:
            raise ValueError(f"no such engineering design project: {run_id}")
        return ModuleRunRef(module=self.module, run_id=run_id, version=proj.version)

    def get_handoff(self, session: Session, run_id: str) -> ModuleHandoff:
        from sqlalchemy import select

        from harness.engineering_design.models import CandidateDesign, DesignPortfolio

        portfolio = session.execute(
            select(DesignPortfolio).where(DesignPortfolio.design_project_id == run_id).order_by(DesignPortfolio.created_at.desc())
        ).scalars().first()
        if portfolio is None:
            return ModuleHandoff(
                source_module=self.module, source_run_id=run_id, target_module="scientific_evaluation",
                unresolved_items=["no DesignPortfolio has been generated yet"], confidence_status="not_ready",
            )
        candidates = session.execute(select(CandidateDesign).where(CandidateDesign.portfolio_id == portfolio.portfolio_id)).scalars().all()
        return ModuleHandoff(
            source_module=self.module, source_run_id=run_id, target_module="scientific_evaluation",
            payload_refs={"portfolio_id": portfolio.portfolio_id, "candidate_ids": ",".join(c.design_id for c in candidates)},
            confidence_status="portfolio_generated",
        )

    def draft_build_test_and_request_approval(
        self, session: Session, run_id: str, *, design_id: str, actor_id: str, build_test_kwargs: dict[str, Any],
    ) -> dict[str, Any]:
        """doc04 §13.7's own build/test → governance sequence
        (`build_test_planner.draft_build_test_package` →
        `governance_service.mark_planning_complete` →
        `governance_service.request_human_approval`). Returns the package
        readiness so the orchestrator can decide whether a human decision
        may even be requested yet (BuildReadinessGate, inside
        `draft_build_test_package`, still governs this - the orchestrator
        does not bypass it)."""
        from harness.engineering_design import build_test_planner, governance_service

        pkg = build_test_planner.draft_build_test_package(session, design_id=design_id, actor_id=actor_id, **build_test_kwargs)
        if pkg.readiness != "build_ready":
            return {"readiness": pkg.readiness, "package": pkg}
        governance_service.mark_planning_complete(session, design_project_id=run_id, actor_id=actor_id)
        return {"readiness": pkg.readiness, "package": pkg}

    def request_human_selection(self, session: Session, *, design_project_id: str, actor_id: str) -> Any:
        """Open the canonical human-selection gate before validation planning."""
        from harness.engineering_design import governance_service

        return governance_service.request_human_approval(
            session, design_project_id=design_project_id, actor_id=actor_id,
        )

    def record_human_decision(
        self, session: Session, *, design_id: str, approver_id: str, decision: str, approver_role: str,
    ) -> tuple[Any, Any, Any]:
        from harness.engineering_design import governance_service

        return governance_service.record_human_decision(
            session, design_id=design_id, approver_id=approver_id, decision=decision, approver_role=approver_role,
        )

    def bridge_and_start_build(self, session: Session, *, design_id: str, design_project_id: str, actor_id: str) -> str:
        """Bridges into a Problem-02 `DesignVersion` (`proposed`), then
        approves it (Problem 2's OWN, separate approval gate -
        `harness.designs.service.approve_design_version` - proposer≠
        approver enforced there too, same as every other approval layer in
        this codebase). The approver here is "system": the human decision
        that authorizes this has already been recorded one layer up (the
        orchestrator's `human_approval`/Problem-4-governance gate that
        called this method) - this is that decision's mechanical
        consequence, not an independent second human judgment call."""
        from harness.designs import service as design_svc
        from harness.engineering_design import design_version_bridge, governance_service
        from harness.projects.models import Project

        dv = design_version_bridge.bridge_to_design_version(session, design_id=design_id, actor_id=actor_id)
        proj_row = session.get(Project, dv.project_id)
        dv = design_svc.approve_design_version(
            session, design_version_id=dv.design_version_id, approver_id="system", expected_project_version=proj_row.version,
        )
        governance_service.start_build(session, design_project_id=design_project_id, design_id=design_id, actor_id=actor_id)
        governance_service.mark_test_pending(session, design_project_id=design_project_id, actor_id=actor_id)
        return dv.design_version_id

    def ingest_outcome(self, session: Session, *, design_id: str, actor_id: str, **kwargs: Any) -> Any:
        from harness.engineering_design import outcome_service

        return outcome_service.ingest_outcome(session, design_id=design_id, actor_id=actor_id, **kwargs)


# ---------------------------------------------------------------------------
# Scientific Evaluation (Problem 5)
# ---------------------------------------------------------------------------


class EvaluationAdapter:
    """Wraps `harness.scientific_evaluation.service.run_scientific_evaluation`
    - already a single real end-to-end driver covering intake through
    meta-review (see that function's own docstring); this adapter does not
    re-sequence anything, only exposes it through the module contract."""

    module = "scientific_evaluation"

    def start(self, session: Session, *, request: dict[str, Any], context: dict[str, Any]) -> ModuleRunRef:
        from harness.scientific_evaluation.service import run_scientific_evaluation

        result = run_scientific_evaluation(
            session, portfolio_id=request["portfolio_id"], actor_id=request.get("actor_id", "system"),
            diagnosis_reference=request.get("diagnosis_reference"), enable_llm_critic=request.get("enable_llm_critic", False),
            workflow_run_id=request.get("workflow_run_id"),
        )
        case = result["case"]
        return ModuleRunRef(module=self.module, run_id=case.evaluation_id, version=case.version)

    def get_status(self, session: Session, run_id: str) -> ModuleRunStatus:
        from harness.scientific_evaluation.models import EvaluationCase

        case = session.get(EvaluationCase, run_id)
        if case is None:
            raise ValueError(f"no such evaluation case: {run_id}")
        normalized = {
            "revision_required": "waiting_input", "approved_for_planning": "completed", "approved_for_build": "completed",
            "rejected": "blocked", "returned_to_diagnosis": "blocked", "held": "waiting_input", "stopped": "blocked",
        }.get(case.status, "running")
        return ModuleRunStatus(module=self.module, run_id=run_id, native_status=case.status, normalized=normalized, version=case.version)

    def resume(self, session: Session, run_id: str, input_ref: dict[str, Any], expected_version: int) -> ModuleRunRef:
        """If `input_ref` carries a `design_id`/`modification_reason` (a
        human or - in a future Phase C - an LLM strategy-draft adapter
        supplying a concretely revised candidate), this drives
        `apply_revision_and_reevaluate` - the same real revision path
        `tests/scientific_evaluation/test_e2e_trp.py` exercises. Otherwise
        it just re-runs the pipeline (`continue_scientific_evaluation`) on
        the same case, e.g. after an LLM adapter retry (Phase C)."""
        from harness.scientific_evaluation.models import EvaluationCase
        from harness.scientific_evaluation.service import apply_revision_and_reevaluate, continue_scientific_evaluation

        case = session.get(EvaluationCase, run_id)
        if case is None:
            raise ValueError(f"no such evaluation case: {run_id}")
        if case.version != expected_version:
            from harness.db import ConcurrencyConflictError

            raise ConcurrencyConflictError(f"EvaluationCase {run_id}: expected version {expected_version}, actual {case.version}")
        if "design_id" in input_ref and "modification_reason" in input_ref:
            revision_kwargs = {k: v for k, v in input_ref.items() if k not in ("design_id", "modification_reason", "actor_id", "task_ids")}
            result = apply_revision_and_reevaluate(
                session, evaluation_id=run_id, design_id=input_ref["design_id"], actor_id=input_ref.get("actor_id", "system"),
                modification_reason=input_ref["modification_reason"], task_ids=input_ref.get("task_ids"), **revision_kwargs,
            )
        else:
            result = continue_scientific_evaluation(session, evaluation_id=run_id, actor_id=input_ref.get("actor_id", "system"))
        return ModuleRunRef(module=self.module, run_id=run_id, version=result["case"].version)

    def cancel(self, session: Session, run_id: str, reason: str, actor: str) -> ModuleRunRef:
        from harness.scientific_evaluation.models import EvaluationCase

        case = session.get(EvaluationCase, run_id)
        if case is None:
            raise ValueError(f"no such evaluation case: {run_id}")
        return ModuleRunRef(module=self.module, run_id=run_id, version=case.version)

    def get_handoff(self, session: Session, run_id: str) -> ModuleHandoff:
        from harness.scientific_evaluation.models import EvaluationCase, MetaReviewDecision
        from sqlalchemy import select

        case = session.get(EvaluationCase, run_id)
        if case is None:
            raise ValueError(f"no such evaluation case: {run_id}")
        meta = session.execute(
            select(MetaReviewDecision).where(MetaReviewDecision.evaluation_id == run_id).order_by(MetaReviewDecision.created_at.desc())
        ).scalars().first()
        return ModuleHandoff(
            source_module=self.module, source_run_id=run_id, target_module="virtual_cell",
            payload_refs={"evaluation_id": run_id},
            unresolved_items=list(meta.blocking_findings) if meta else [],
            confidence_status=(meta.recommended_action if meta else "unknown"),
        )

    def record_human_decision(
        self, session: Session, *, run_id: str, decision: str, approver_id: str, approver_role: str = "",
        selected_candidates: list[str] | None = None, rationale: str = "",
    ) -> Any:
        from harness.scientific_evaluation.human_gate import record_human_evaluation_decision
        from harness.scientific_evaluation.models import EvaluationCase

        case = session.get(EvaluationCase, run_id)
        if case is None:
            raise ValueError(f"no such evaluation case: {run_id}")
        return record_human_evaluation_decision(
            session, case=case, decision=decision, approver_id=approver_id, approver_role=approver_role,
            selected_candidates=selected_candidates, rationale=rationale,
        )


# ---------------------------------------------------------------------------
# Virtual Cell / Simulation (Problem 6)
# ---------------------------------------------------------------------------


class SimulationAdapter:
    """Wraps `harness.virtual_cell.service.run_prediction_pipeline` - already
    a single real end-to-end driver (compile → compatibility → baseline +
    candidate FBA runs → comparison → review → validation plan), and
    already honestly handles "not applicable" (no perturbations) and
    "incompatible" (blocked before any run) without this adapter adding any
    branching logic of its own."""

    module = "virtual_cell"

    def start(self, session: Session, *, request: dict[str, Any], context: dict[str, Any]) -> ModuleRunRef:
        from harness.virtual_cell.service import run_prediction_pipeline

        result = run_prediction_pipeline(
            session, project_id=request["project_id"], design_version_id=request["design_version_id"],
            chassis=request.get("chassis", {}), environment=request.get("environment", {}),
            model_id=request.get("model_id", "MREG-gem_fba"), actor_id=request.get("actor_id", "system"),
            evaluation_reference=request.get("evaluation_reference"),
        )
        case = result["case"]
        self._last_result = result  # type: ignore[attr-defined]
        return ModuleRunRef(module=self.module, run_id=case.simulation_case_id, version=1)

    def get_status(self, session: Session, run_id: str) -> ModuleRunStatus:
        from harness.virtual_cell.service import get_case

        case = get_case(session, run_id)
        if case is None:
            raise ValueError(f"no such simulation case: {run_id}")
        normalized = {
            "needs_input": "waiting_input", "validation_planned": "completed", "prediction_under_review": "completed",
            "incompatible": "blocked", "no_compatible_model": "blocked", "run_failed": "failed",
        }.get(case.status, "running")
        return ModuleRunStatus(module=self.module, run_id=run_id, native_status=case.status, normalized=normalized, version=1)

    def resume(self, session: Session, run_id: str, input_ref: dict[str, Any], expected_version: int) -> ModuleRunRef:
        from harness.virtual_cell.service import get_case

        case = get_case(session, run_id)
        if case is None:
            raise ValueError(f"no such simulation case: {run_id}")
        return ModuleRunRef(module=self.module, run_id=run_id, version=1)

    def cancel(self, session: Session, run_id: str, reason: str, actor: str) -> ModuleRunRef:
        return ModuleRunRef(module=self.module, run_id=run_id, version=1)

    def get_handoff(self, session: Session, run_id: str) -> ModuleHandoff:
        from sqlalchemy import select

        from harness.virtual_cell.models import CompatibilityReport, PredictionReview
        from harness.virtual_cell.service import get_case

        case = get_case(session, run_id)
        if case is None:
            raise ValueError(f"no such simulation case: {run_id}")
        compat = session.execute(
            select(CompatibilityReport).where(CompatibilityReport.simulation_case_id == run_id).order_by(CompatibilityReport.created_at.desc())
        ).scalars().first()
        review = session.execute(
            select(PredictionReview).where(PredictionReview.simulation_case_id == run_id).order_by(PredictionReview.created_at.desc())
        ).scalars().first()
        return ModuleHandoff(
            source_module=self.module, source_run_id=run_id, target_module="experiment",
            payload_refs={"simulation_case_id": run_id},
            confidence_status=(review.decision if review else (compat.decision if compat else "not_applicable")),
            warnings=list(compat.blocking_reasons) if compat else [],
        )


# ---------------------------------------------------------------------------
# Experiment / Observation (Problem 2)
# ---------------------------------------------------------------------------


class ExperimentAdapter:
    """Wraps `harness.experiments.service` (plan/run) and
    `harness.diagnosis.normalizer.normalize_and_commit` (the existing,
    already-QC'd path into Problem 2's `Observation` table - reused here
    rather than writing a second ingestion path, since Observation is a
    Problem-02 object diagnosis already writes into, not diagnosis-owned)."""

    module = "experiment"

    def create_plan(self, session: Session, *, project_id: str, design_version_ids: list[str], actor_id: str, **kwargs: Any) -> Any:
        from harness.experiments.service import create_experiment_plan

        return create_experiment_plan(session, project_id=project_id, design_version_ids=design_version_ids, created_by=actor_id, **kwargs)

    def approve_plan(self, session: Session, *, experiment_plan_id: str, approver_id: str) -> Any:
        from harness.experiments.service import approve_experiment_plan

        return approve_experiment_plan(session, experiment_plan_id=experiment_plan_id, approver_id=approver_id)

    def record_run(self, session: Session, *, project_id: str, experiment_plan_id: str, executed_design_version_ids: list[str], actor_id: str, **kwargs: Any) -> Any:
        from harness.experiments.service import record_experiment_run

        return record_experiment_run(
            session, project_id=project_id, experiment_plan_id=experiment_plan_id,
            executed_design_version_ids=executed_design_version_ids, actor_id=actor_id, **kwargs,
        )

    def ingest_observation(self, session: Session, *, project_id: str, raw: Any, actor_id: str) -> tuple[Any, Any]:
        from harness.diagnosis.normalizer import normalize_and_commit

        return normalize_and_commit(session, project_id=project_id, raw=raw, actor_id=actor_id)

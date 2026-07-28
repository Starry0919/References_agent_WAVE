"""`UnifiedScientificWorkflowOrchestrator` (prompt Workstream 1): the one
top-level sequencer for Problems 3-6, sitting above their existing
controllers rather than replacing them. Every method here:

1. loads the `UnifiedWorkflowRun` row and enforces `expected_version` via
   `harness.db.check_and_bump_version` (stale writes raise
   `ConcurrencyConflictError`, never last-write-wins);
2. delegates the actual scientific/engineering work to a
   `harness.orchestrator.adapters` adapter, which calls the real module
   service functions;
3. evaluates the relevant checkpoint through `harness.orchestrator.gates.
   GateRegistry` (never by comparing raw status strings itself);
4. records an `OrchestratorTransition` + `ProjectEvent` (with
   `workflow_run_id`/`correlation_id`) for the phase change.

Repo-truth note (recorded per prompt §2.2's own instruction to log
conflicts rather than silently resolve them): prompt §4.3's illustrative
phase order lists `SIMULATION` before `HUMAN_REVIEW`. This orchestrator
runs `HUMAN_REVIEW` (Engineering Design's build-governance approval) BEFORE
`SIMULATION`, because `harness.virtual_cell.service.open_simulation_case`
asserts the target `DesignVersion` is already formal/approved
(`assert_design_version_formal`), and this repository only creates a
`DesignVersion` via `design_version_bridge.bridge_to_design_version`
*after* that same governance approval (`tests/engineering_design/
test_end_to_end_trp.py` steps 4-5). Reordering SIMULATION before
HUMAN_REVIEW would require either forking a second "pre-approval"
DesignVersion object (creating exactly the parallel-object duplication
prompt §2.6/§16 forbids) or rewriting Problem 6's precondition (out of
scope for "integrate, don't rewrite"). The orchestrator's own
`scientific_evaluation` gate still runs before this Human Gate, so no
Human Gate is granted without a completed independent scientific review.
"""
from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from harness.db import ConcurrencyConflictError, check_and_bump_version
from harness.ids import new_id, now
from harness.memory import event_types as et
from harness.memory.event_store import append_event
from harness.orchestrator.adapters import DesignAdapter, DiagnosisAdapter, EvaluationAdapter, ExperimentAdapter, SimulationAdapter
from harness.orchestrator.gates import GateRegistry
from harness.orchestrator.models import ModuleHandoffRecord, OrchestratorGateDecision, OrchestratorTransition, UnifiedWorkflowRun


class OrchestratorPhaseError(RuntimeError):
    """Raised when a phase-specific method is called while the run is not
    in the phase it requires - the orchestrator-level analogue of
    `IllegalDiagnosisTransitionError`/`IllegalTransitionError`."""


class OrchestratorBlockedError(RuntimeError):
    """Raised when a gate blocks the requested advance; the run's
    `blocked_reason` is set and the caller must resolve it (revise, supply
    more data, or obtain human approval) before retrying."""


class CycleConflictError(RuntimeError):
    """Raised when a project's legacy `IterativeCycleState` (Problem 02) and
    the Unified Scientific Workflow Orchestrator would otherwise both try to
    drive the same project's DBTL state at once.

    Single-source-of-truth decision (查缺补漏03 Phase 1): `IterativeCycleState`
    and `UnifiedWorkflowRun` are NOT merged into one table/state machine -
    that would require collapsing two differently-shaped state enums
    (Cycle's 16-state DBTL_STATES vs the orchestrator's 14-phase
    ORCHESTRATOR_PHASES) with no clean 1:1 mapping, a genuine large
    refactor this round explicitly avoids. Instead each project picks
    exactly ONE authoritative engine, decided by whichever is used FIRST:
    - `create_run()` refuses to start an orchestrator run for a project
      whose Cycle has already progressed past its initial
      PROJECT_CONTEXT_READY state (someone is already driving it the old
      way).
    - the legacy `/cycle/{action}` endpoint (harness/api/projects.py)
      refuses to advance a project's Cycle once it has ANY
      UnifiedWorkflowRun (someone has already adopted the orchestrator).
    This is enforced mutual exclusion rather than a best-effort bidirectional
    field sync - two independently-driven copies of "current state" that
    are merely kept in sync after the fact is exactly the kind of drift
    this error prevents, not a weaker substitute for it. Whichever engine a
    project starts with remains its single source of truth for the rest of
    that project's life; `UnifiedWorkflowRun.cycle_state_id` still records
    which Cycle it was created under, purely for traceability/reporting."""


def get_latest_run_for_project(session: Session, project_id: str) -> UnifiedWorkflowRun | None:
    """The one query "is this project orchestrator-driven, and if so what's
    its current run" - shared by `build_project_status_view` (Command
    Center reads it) and the legacy Cycle-action API's mutual-exclusion
    guard (`harness/api/projects.py`'s `cycle_action`), so both sides of the
    single-source-of-truth boundary agree on the same fact."""
    from sqlalchemy import select

    return session.execute(
        select(UnifiedWorkflowRun).where(UnifiedWorkflowRun.project_id == project_id).order_by(UnifiedWorkflowRun.updated_at.desc())
    ).scalars().first()


class UnifiedScientificWorkflowOrchestrator:
    def __init__(self) -> None:
        self.gates = GateRegistry()
        self._diagnosis = DiagnosisAdapter()
        self._design = DesignAdapter()
        self._evaluation = EvaluationAdapter()
        self._simulation = SimulationAdapter()
        self._experiment = ExperimentAdapter()

    # -- shared plumbing ----------------------------------------------------

    def _get(self, session: Session, workflow_run_id: str) -> UnifiedWorkflowRun:
        run = session.get(UnifiedWorkflowRun, workflow_run_id)
        if run is None:
            raise ValueError(f"no such workflow run: {workflow_run_id}")
        return run

    def _bump(self, run: UnifiedWorkflowRun, expected_version: int) -> None:
        check_and_bump_version(run, expected_version)

    def _transition_phase(self, session: Session, run: UnifiedWorkflowRun, *, to_phase: str, reason: str, actor_id: str) -> None:
        from harness.orchestrator.models import ORCHESTRATOR_PHASES

        if to_phase not in ORCHESTRATOR_PHASES:
            raise ValueError(f"unknown orchestrator phase {to_phase!r}")
        tr = OrchestratorTransition(
            transition_id=new_id("ORCHTR"), workflow_run_id=run.workflow_run_id, from_phase=run.current_phase,
            to_phase=to_phase, reason=reason, actor_id=actor_id, created_at=now(),
        )
        session.add(tr)
        from_phase = run.current_phase
        run.current_phase = to_phase
        run.updated_at = now()
        session.flush()
        append_event(
            session, project_id=run.project_id, event_type=et.ORCH_PHASE_CHANGED, entity_type="UnifiedWorkflowRun",
            entity_id=run.workflow_run_id, payload={"from_phase": from_phase, "to_phase": to_phase, "reason": reason},
            actor_type="agent" if actor_id == "system" else "human", actor_id=actor_id,
            correlation_id=run.correlation_id, workflow_run_id=run.workflow_run_id,
        )

    def _record_gate(self, session: Session, run: UnifiedWorkflowRun, result, *, actor: str) -> OrchestratorGateDecision:
        row = OrchestratorGateDecision(
            gate_decision_id=new_id("ORCHGATE"), workflow_run_id=run.workflow_run_id, gate_type=result.gate_type,
            decision=result.decision, evaluated_refs=result.evaluated_refs, blocking_findings=result.blocking_findings,
            non_blocking_findings=result.non_blocking_findings, required_actions=result.required_actions,
            evidence_refs=result.evidence_refs, rule_versions=result.rule_versions, reviewer_refs=result.reviewer_refs,
            actor=actor, timestamp=now(),
        )
        session.add(row)
        run.active_gate_ref = row.gate_decision_id
        run.updated_at = now()
        session.flush()
        append_event(
            session, project_id=run.project_id, event_type=et.ORCH_GATE_DECIDED, entity_type="OrchestratorGateDecision",
            entity_id=row.gate_decision_id, payload={"gate_type": result.gate_type, "decision": result.decision, "required_actions": result.required_actions},
            actor_type="agent" if actor == "system" else "human", actor_id=actor,
            correlation_id=run.correlation_id, workflow_run_id=run.workflow_run_id,
        )
        return row

    def _record_handoff(self, session: Session, run: UnifiedWorkflowRun, handoff, *, gate_decision_ref: str | None = None) -> ModuleHandoffRecord:
        row = ModuleHandoffRecord(
            handoff_id=new_id("ORCHHAND"), workflow_run_id=run.workflow_run_id, source_module=handoff.source_module,
            source_run_id=handoff.source_run_id, source_version=handoff.source_version, target_module=handoff.target_module,
            payload_refs=handoff.payload_refs, preconditions=handoff.preconditions, unresolved_items=handoff.unresolved_items,
            warnings=handoff.warnings, confidence_status=handoff.confidence_status, gate_decision_ref=gate_decision_ref,
            created_at=now(),
        )
        session.add(row)
        session.flush()
        append_event(
            session, project_id=run.project_id, event_type=et.ORCH_MODULE_HANDOFF_RECORDED, entity_type="ModuleHandoffRecord",
            entity_id=row.handoff_id, payload={"source_module": handoff.source_module, "target_module": handoff.target_module, "confidence_status": handoff.confidence_status},
            actor_type="agent", actor_id="system", correlation_id=run.correlation_id, workflow_run_id=run.workflow_run_id,
        )
        return row

    def _block(self, session: Session, run: UnifiedWorkflowRun, *, reason: str, actor_id: str) -> None:
        run.status = "blocked"
        run.blocked_reason = reason
        run.updated_at = now()
        session.flush()
        append_event(
            session, project_id=run.project_id, event_type=et.ORCH_BLOCKED, entity_type="UnifiedWorkflowRun",
            entity_id=run.workflow_run_id, payload={"reason": reason}, actor_type="agent" if actor_id == "system" else "human",
            actor_id=actor_id, correlation_id=run.correlation_id, workflow_run_id=run.workflow_run_id,
        )
        self._transition_phase(session, run, to_phase="BLOCKED", reason=reason, actor_id=actor_id)

    # -- INTAKE / CONTEXT_VALIDATION -----------------------------------------

    def create_run(self, session: Session, *, project_id: str, actor_id: str, target_product: str, host: str, dbtl_iteration_id: str | None = None) -> UnifiedWorkflowRun:
        from harness.projects import service as proj_svc

        cycle = proj_svc.get_active_cycle(session, project_id)
        if cycle is not None and cycle.current_state != "PROJECT_CONTEXT_READY":
            raise CycleConflictError(
                f"project {project_id} is already being driven by its legacy IterativeCycleState "
                f"(cycle {cycle.cycle_state_id!r} is at {cycle.current_state!r}, not the initial state) - "
                "use the /api/projects/{id}/cycle/{action} endpoints for this project, not the orchestrator"
            )
        run = UnifiedWorkflowRun(
            workflow_run_id=new_id("WFR"), project_id=project_id, dbtl_iteration_id=dbtl_iteration_id,
            cycle_state_id=cycle.cycle_state_id if cycle else None,
            status="active", current_phase="INTAKE", correlation_id=new_id("CORR"),
            created_at=now(), updated_at=now(), version=1,
        )
        session.add(run)
        session.flush()
        append_event(
            session, project_id=project_id, event_type=et.ORCH_RUN_CREATED, entity_type="UnifiedWorkflowRun",
            entity_id=run.workflow_run_id, payload={"project_id": project_id, "target_product": target_product, "host": host},
            actor_type="agent" if actor_id == "system" else "human", actor_id=actor_id,
            correlation_id=run.correlation_id, workflow_run_id=run.workflow_run_id,
        )
        gate = self.gates.evaluate("context_completeness", has_target_product=bool(target_product), has_host=bool(host), has_actor=bool(actor_id))
        self._record_gate(session, run, gate, actor=actor_id)
        if gate.decision != "pass":
            self._block(session, run, reason=f"context_completeness gate: {gate.required_actions}", actor_id=actor_id)
            return run
        self._transition_phase(session, run, to_phase="CONTEXT_VALIDATION", reason="context_completeness gate passed", actor_id=actor_id)
        self._transition_phase(session, run, to_phase="DIAGNOSIS", reason="context validated, entering diagnosis", actor_id=actor_id)
        return run

    # -- DIAGNOSIS ------------------------------------------------------------

    def start_diagnosis(self, session: Session, workflow_run_id: str, *, expected_version: int, request: dict[str, Any], context: dict[str, Any], actor_id: str) -> UnifiedWorkflowRun:
        run = self._get(session, workflow_run_id)
        if run.current_phase != "DIAGNOSIS":
            raise OrchestratorPhaseError(f"start_diagnosis requires phase DIAGNOSIS, run is in {run.current_phase!r}")
        self._bump(run, expected_version)
        request = {**request, "project_id": run.project_id, "actor_id": actor_id, "workflow_run_id": workflow_run_id}
        module_ref = self._diagnosis.start(session, request=request, context=context)
        run.diagnosis_run_ref = module_ref.run_id
        run.current_module = "diagnosis"
        run.updated_at = now()
        session.flush()
        append_event(
            session, project_id=run.project_id, event_type=et.ORCH_MODULE_STARTED, entity_type="UnifiedWorkflowRun",
            entity_id=run.workflow_run_id, payload={"module": "diagnosis", "run_id": module_ref.run_id},
            actor_type="agent" if actor_id == "system" else "human", actor_id=actor_id,
            correlation_id=run.correlation_id, workflow_run_id=run.workflow_run_id,
        )
        status = self._diagnosis.get_status(session, module_ref.run_id)
        if status.normalized == "waiting_input":
            run.status = "waiting"
            run.pause_reason = f"diagnosis session {module_ref.run_id} is {status.native_status!r} (data_sufficiency={status.detail})"
            run.updated_at = now()
            session.flush()
            return run
        return self._advance_diagnosis_handoff(session, run, actor_id=actor_id)

    def resume_diagnosis_with_data(self, session: Session, workflow_run_id: str, *, expected_version: int, data_sufficiency: dict[str, bool], actor_id: str) -> UnifiedWorkflowRun:
        run = self._get(session, workflow_run_id)
        if run.diagnosis_run_ref is None:
            raise OrchestratorPhaseError("no diagnosis session has been started for this run")
        self._bump(run, expected_version)
        module_ref = self._diagnosis.resume(
            session, run.diagnosis_run_ref, {"data_sufficiency": data_sufficiency, "actor_id": actor_id},
            expected_version=self._diagnosis.get_status(session, run.diagnosis_run_ref).version,
        )
        status = self._diagnosis.get_status(session, module_ref.run_id)
        run.status = "active"
        run.pause_reason = None
        run.updated_at = now()
        session.flush()
        if status.normalized == "waiting_input":
            return run
        # The resume above already drove the SAME diagnosis session (run.
        # diagnosis_run_ref, unchanged) through the hypothesis pipeline when
        # it became sufficient - advance the workflow phase from here, same
        # as start_diagnosis does past its own sufficiency check. Do NOT call
        # start_diagnosis: that would mint a brand-new DiagnosisSession and
        # orphan the one just resumed (the bug this fixes).
        return self._advance_diagnosis_handoff(session, run, actor_id=actor_id)

    def _advance_diagnosis_handoff(self, session: Session, run: UnifiedWorkflowRun, *, actor_id: str) -> UnifiedWorkflowRun:
        from harness.diagnosis import service as diag_svc

        sess = diag_svc.get_session(session, run.diagnosis_run_ref)
        handoff = self._diagnosis.get_handoff(session, run.diagnosis_run_ref)
        if sess.status == "human_review_required":
            run.status = "waiting"
            run.pause_reason = "diagnosis raised human_review_required (safety concern or unresolved model conflict)"
            run.updated_at = now()
            session.flush()
            self._transition_phase(session, run, to_phase="HUMAN_REVIEW", reason="diagnosis escalated to human review", actor_id=actor_id)
            return run
        if sess.status == "evidence_limited":
            self._block(session, run, reason="diagnosis stopped evidence_limited - insufficient evidence for an actionable handoff", actor_id=actor_id)
            return run
        if sess.status != "handoff_ready":
            run.status = "waiting"
            run.pause_reason = f"diagnosis session status={sess.status!r}, not yet handoff_ready"
            run.updated_at = now()
            session.flush()
            return run

        gate = self.gates.evaluate(
            "diagnosis_handoff", stopping_reason="actionable_stop", engineering_value_passed=True,
            human_approval_required=False, human_approved=None, decision_ref=handoff.payload_refs.get("diagnosis_decision_id", ""),
        )
        gate_row = self._record_gate(session, run, gate, actor=actor_id)
        self._record_handoff(session, run, handoff, gate_decision_ref=gate_row.gate_decision_id)
        if gate.decision != "pass":
            self._block(session, run, reason=f"diagnosis_handoff gate: {gate.decision} - {gate.blocking_findings}", actor_id=actor_id)
            return run
        self._diagnosis.finalize_handoff(session, run.diagnosis_run_ref, actor_id=actor_id, handoff_gate_passed=True)
        run.diagnosis_handoff_ref = handoff.payload_refs.get("diagnosis_decision_id")
        run.status = "active"
        run.updated_at = now()
        session.flush()
        self._transition_phase(session, run, to_phase="DESIGN", reason="diagnosis_handoff gate passed", actor_id=actor_id)
        return run

    # -- DESIGN -----------------------------------------------------------

    def start_design(self, session: Session, workflow_run_id: str, *, expected_version: int, request: dict[str, Any], context: dict[str, Any], actor_id: str) -> UnifiedWorkflowRun:
        run = self._get(session, workflow_run_id)
        if run.current_phase != "DESIGN":
            raise OrchestratorPhaseError(f"start_design requires phase DESIGN, run is in {run.current_phase!r}")
        self._bump(run, expected_version)
        request = {**request, "diagnosis_decision_id": run.diagnosis_handoff_ref, "actor_id": actor_id}
        module_ref = self._design.start(session, request=request, context=context)
        run.design_project_ref = module_ref.run_id
        run.current_module = "engineering_design"
        run.updated_at = now()
        session.flush()
        append_event(
            session, project_id=run.project_id, event_type=et.ORCH_MODULE_STARTED, entity_type="UnifiedWorkflowRun",
            entity_id=run.workflow_run_id, payload={"module": "engineering_design", "run_id": module_ref.run_id},
            actor_type="agent" if actor_id == "system" else "human", actor_id=actor_id,
            correlation_id=run.correlation_id, workflow_run_id=run.workflow_run_id,
        )
        status = self._design.get_status(session, module_ref.run_id)
        if status.normalized == "blocked":
            self._block(session, run, reason=f"engineering_design project blocked: {status.native_status}", actor_id=actor_id)
            return run
        gate = self.gates.evaluate("engineering_feasibility", has_primary_metrics=bool(request.get("primary_metrics")), has_hard_constraints_declared=True, project_ref=module_ref.run_id)
        self._record_gate(session, run, gate, actor=actor_id)
        if gate.decision not in ("pass", "pass_with_conditions"):
            self._block(session, run, reason=f"engineering_feasibility gate: {gate.decision}", actor_id=actor_id)
            return run
        self._transition_phase(session, run, to_phase="EVALUATION", reason="portfolio generated, entering scientific evaluation", actor_id=actor_id)
        return run

    def evaluate_design_portfolio(self, session: Session, workflow_run_id: str, *, expected_version: int, actor_id: str) -> UnifiedWorkflowRun:
        """Problem 4's OWN portfolio evaluation (harness/engineering_design/
        evaluation_service.py::evaluate_portfolio) - independent of, and a
        precondition for, the LATER build-governance sequence inside
        `record_human_gate_decision`: `governance_service.
        mark_planning_complete` requires `EngineeringDesignProject.status
        == 'portfolio_evaluated'`, only reachable by calling this.
        `DesignAdapter.start()` already auto-chains hypothesis -> strategy
        -> portfolio generation but never called this - a real,
        previously silent orchestration gap: a run could reach
        HUMAN_REVIEW (scientific evaluation approved) and still fail
        approval with "cannot move design project ... only legal from
        ('portfolio_evaluated',)", with no way to fix it from the UI. Not
        phase-gated beyond requiring a design project to exist - this runs
        alongside scientific evaluation (both are sub-steps of the
        orchestrator's own EVALUATION phase), in whichever order a human
        triggers them.
        """
        run = self._get(session, workflow_run_id)
        if run.design_project_ref is None:
            raise OrchestratorBlockedError("evaluate_design_portfolio requires a design project; run has none yet")
        self._bump(run, expected_version)
        handoff = self._design.get_handoff(session, run.design_project_ref)
        portfolio_id = handoff.payload_refs.get("portfolio_id")
        if not portfolio_id:
            raise OrchestratorBlockedError("no DesignPortfolio has been generated yet for this design project")
        from harness.engineering_design.evaluation_service import evaluate_portfolio

        evaluate_portfolio(session, portfolio_id=portfolio_id, actor_id=actor_id)
        run.updated_at = now()
        session.flush()
        return run

    # -- EVALUATION ---------------------------------------------------------

    def run_evaluation(self, session: Session, workflow_run_id: str, *, expected_version: int, actor_id: str, revision_limit: int = 3, enable_llm_critic: bool = False) -> UnifiedWorkflowRun:
        run = self._get(session, workflow_run_id)
        if run.current_phase != "EVALUATION":
            raise OrchestratorPhaseError(f"run_evaluation requires phase EVALUATION, run is in {run.current_phase!r}")
        self._bump(run, expected_version)
        handoff = self._design.get_handoff(session, run.design_project_ref)
        module_ref = self._evaluation.start(
            session, request={
                "portfolio_id": handoff.payload_refs["portfolio_id"], "actor_id": actor_id,
                "diagnosis_reference": run.diagnosis_handoff_ref, "enable_llm_critic": enable_llm_critic,
                "workflow_run_id": workflow_run_id,
            }, context={},
        )
        run.evaluation_run_ref = module_ref.run_id
        run.current_module = "scientific_evaluation"
        run.updated_at = now()
        session.flush()
        return self._gate_evaluation_case(session, run, evaluation_id=module_ref.run_id, actor_id=actor_id, revision_limit=revision_limit)

    def submit_evaluation_revision(
        self, session: Session, workflow_run_id: str, *, expected_version: int, design_id: str, modification_reason: str,
        actor_id: str, revision_limit: int = 3, **revision_kwargs: Any,
    ) -> UnifiedWorkflowRun:
        """The human/PI (or, from Phase C onward, an LLM Strategy Draft
        adapter's structured output, still subject to the same downstream
        evidence-grounding and Critic re-review) supplies a concretely
        revised candidate - the orchestrator does not invent one. Requires
        the run to be paused in EVALUATION with a prior `revise`/
        `wait_for_data` gate decision (prompt §2.4: LLM/orchestrator may
        not "绕过 deterministic rules" by skipping straight to approval)."""
        run = self._get(session, workflow_run_id)
        if run.current_phase != "EVALUATION" or run.evaluation_run_ref is None:
            raise OrchestratorPhaseError(f"submit_evaluation_revision requires an in-progress EVALUATION phase, run is in {run.current_phase!r}")
        self._bump(run, expected_version)
        from harness.scientific_evaluation.models import EvaluationCase

        case = session.get(EvaluationCase, run.evaluation_run_ref)
        if case is None or case.status != "revision_required":
            raise OrchestratorPhaseError(
                f"submit_evaluation_revision requires the evaluation case to be in 'revision_required', "
                f"it is {case.status if case else 'missing'!r} - call get_status()/reconcile() and use "
                f"record_human_gate_decision() instead if the case has already reached a human checkpoint"
            )
        eval_status = self._evaluation.get_status(session, run.evaluation_run_ref)
        module_ref = self._evaluation.resume(
            session, run.evaluation_run_ref,
            {"design_id": design_id, "modification_reason": modification_reason, "actor_id": actor_id, **revision_kwargs},
            expected_version=eval_status.version,
        )
        return self._gate_evaluation_case(session, run, evaluation_id=module_ref.run_id, actor_id=actor_id, revision_limit=revision_limit)

    def record_evaluation_human_decision(
        self, session: Session, workflow_run_id: str, *, expected_version: int, decision: str, actor_id: str,
        approver_role: str = "", selected_candidates: list[str] | None = None, rationale: str = "", revision_limit: int = 3,
    ) -> UnifiedWorkflowRun:
        """The scientific_evaluation module's own "science-level" human gate
        (harness/scientific_evaluation/human_gate.py's 9-value decision
        vocabulary: approve_for_planning/approve_for_build/revise/
        request_more_evidence/request_model_run/return_to_diagnosis/reject/
        hold/stop) - distinct from `record_human_gate_decision` below, the
        LATER build-governance gate only reachable once phase reaches
        HUMAN_REVIEW. A human may accept or override the meta-review's own
        `recommended_action` here.

        Calling `POST .../human-decision` directly against the scientific-
        evaluation module's own route updates the `EvaluationCase` row but
        never advances `current_phase` - nothing else re-invokes
        `_gate_evaluation_case` for an out-of-band decision, so a run would
        sit at phase=EVALUATION forever even after a human recorded
        approve_for_planning. This method wraps the decision and the
        re-gate in one call, the same way `submit_evaluation_revision`
        already does for a revision.
        """
        run = self._get(session, workflow_run_id)
        if run.current_phase != "EVALUATION" or run.evaluation_run_ref is None:
            raise OrchestratorPhaseError(f"record_evaluation_human_decision requires phase EVALUATION, run is in {run.current_phase!r}")
        self._bump(run, expected_version)
        self._evaluation.record_human_decision(
            session, run_id=run.evaluation_run_ref, decision=decision, approver_id=actor_id, approver_role=approver_role,
            selected_candidates=selected_candidates, rationale=rationale,
        )
        return self._gate_evaluation_case(session, run, evaluation_id=run.evaluation_run_ref, actor_id=actor_id, revision_limit=revision_limit)

    def _gate_evaluation_case(self, session: Session, run: UnifiedWorkflowRun, *, evaluation_id: str, actor_id: str, revision_limit: int) -> UnifiedWorkflowRun:
        """Branches on the EvaluationCase's own resulting `status` - the
        module's authoritative state, set by `EvaluationLoopController.
        complete_meta_review` inside the very same pipeline run this method
        is reacting to - rather than re-deriving an independent judgment
        from the same inputs. Prompt §4.5 wants a structured `GateDecision`
        recorded either way, so one is still computed and persisted here;
        it drives the *label*, never the branch, keeping this orchestrator
        from ever disagreeing with the module it is only supposed to be
        sequencing (repo-truth note: an earlier version derived the branch
        from a locally recomputed gate result, which could in rare real
        runs land on `status="revise"` after the module itself had already
        moved the case to `awaiting_human_decision` in the same call -
        confirmed via a full-suite regression failure - `case.status` is
        the fix, not a broader retry/lock)."""
        from sqlalchemy import select

        from harness.scientific_evaluation.models import EvaluationCase, MetaReviewDecision

        case = session.get(EvaluationCase, evaluation_id)
        meta = session.execute(select(MetaReviewDecision).where(MetaReviewDecision.evaluation_id == evaluation_id).order_by(MetaReviewDecision.created_at.desc())).scalars().first()
        gate = self.gates.evaluate(
            "scientific_evaluation", recommended_action=(meta.recommended_action if meta else "revise"),
            open_blocking_findings=list(meta.blocking_findings) if meta else [], revision_round=case.revision_round,
            revision_limit=revision_limit, evaluation_ref=evaluation_id,
        )
        gate_row = self._record_gate(session, run, gate, actor=actor_id)
        eval_handoff = self._evaluation.get_handoff(session, evaluation_id)
        self._record_handoff(session, run, eval_handoff, gate_decision_ref=gate_row.gate_decision_id)

        if case.status in ("approved_for_planning", "approved_for_build", "awaiting_human_decision"):
            run.status = "active"
            run.updated_at = now()
            session.flush()
            self._transition_phase(session, run, to_phase="HUMAN_REVIEW", reason=f"scientific evaluation reached case.status={case.status!r}", actor_id=actor_id)
        elif case.status == "revision_required":
            run.status = "waiting"
            run.pause_reason = f"scientific_evaluation: case.status=revision_required - {gate.required_actions}"
            run.updated_at = now()
            session.flush()
        elif case.status == "returned_to_diagnosis":
            run.status = "waiting"
            run.pause_reason = "scientific evaluation returned the case to diagnosis"
            run.updated_at = now()
            session.flush()
            self._transition_phase(session, run, to_phase="DIAGNOSIS", reason="scientific evaluation returned_to_diagnosis", actor_id=actor_id)
        elif case.status in ("rejected", "stopped"):
            self._block(session, run, reason=f"scientific_evaluation: case.status={case.status!r}", actor_id=actor_id)
        else:
            run.status = "waiting"
            run.pause_reason = f"scientific_evaluation: unexpected case.status={case.status!r}"
            run.updated_at = now()
            session.flush()
        return run

    # -- HUMAN_REVIEW (science human gate + build governance + DesignVersion bridge) --

    def record_human_gate_decision(
        self, session: Session, workflow_run_id: str, *, expected_version: int, decision: str, actor_id: str, reason: str = "",
        selected_design_id: str | None = None, build_test_kwargs: dict[str, Any] | None = None,
    ) -> UnifiedWorkflowRun:
        """`decision` in {"approve", "reject", "hold"}. On "approve": records
        Problem 5's science-level `approve_for_planning` human decision,
        then drafts the build/test package and records Problem 4's
        build-governance `approved_for_build` decision (a distinct, real
        second approval this codebase already requires - not invented
        here), then bridges to a formal `DesignVersion` and enters
        SIMULATION (see module docstring for why SIMULATION follows
        HUMAN_REVIEW in this implementation, not before it)."""
        run = self._get(session, workflow_run_id)
        if run.current_phase != "HUMAN_REVIEW":
            raise OrchestratorPhaseError(f"record_human_gate_decision requires phase HUMAN_REVIEW, run is in {run.current_phase!r}")
        self._bump(run, expected_version)
        gate = self.gates.evaluate("human_approval", decision=decision, actor=actor_id, reason=reason, run_ref=run.workflow_run_id)
        self._record_gate(session, run, gate, actor=actor_id)
        append_event(
            session, project_id=run.project_id, event_type=et.ORCH_HUMAN_DECISION_RECORDED, entity_type="UnifiedWorkflowRun",
            entity_id=run.workflow_run_id, payload={"decision": decision, "reason": reason}, actor_type="human", actor_id=actor_id,
            correlation_id=run.correlation_id, workflow_run_id=run.workflow_run_id,
        )
        if decision == "reject":
            self._block(session, run, reason=f"human gate rejected: {reason}", actor_id=actor_id)
            return run
        if decision == "hold":
            run.status = "paused"
            run.pause_reason = f"human gate held: {reason}"
            run.updated_at = now()
            session.flush()
            return run

        if run.evaluation_run_ref is not None:
            eval_status = self._evaluation.get_status(session, run.evaluation_run_ref)
            if eval_status.native_status not in ("approved_for_planning", "approved_for_build"):
                self._evaluation.record_human_decision(
                    session, run_id=run.evaluation_run_ref, decision="approve_for_planning", approver_id=actor_id,
                    approver_role="PI", selected_candidates=[selected_design_id] if selected_design_id else None,
                )
        if selected_design_id is None:
            raise ValueError("record_human_gate_decision(approve=...) requires selected_design_id")
        pkg_result = self._design.draft_build_test_and_request_approval(
            session, run.design_project_ref, design_id=selected_design_id, actor_id=actor_id, build_test_kwargs=build_test_kwargs or {},
        )
        if pkg_result["readiness"] != "build_ready":
            run.status = "waiting"
            run.pause_reason = f"build/test package readiness={pkg_result['readiness']!r}, not build_ready"
            run.updated_at = now()
            session.flush()
            return run
        self._design.record_human_decision(session, design_id=selected_design_id, approver_id=actor_id, decision="approved", approver_role="PI")
        design_version_id = self._design.bridge_and_start_build(session, design_id=selected_design_id, design_project_id=run.design_project_ref, actor_id=actor_id)
        run.design_version_ref = design_version_id
        run.status = "active"
        run.updated_at = now()
        session.flush()
        self._transition_phase(session, run, to_phase="SIMULATION", reason="build governance approved; DesignVersion bridged", actor_id=actor_id)
        return run

    # -- SIMULATION ---------------------------------------------------------

    def run_simulation(self, session: Session, workflow_run_id: str, *, expected_version: int, chassis: dict[str, Any], environment: dict[str, Any], actor_id: str, model_id: str = "MREG-gem_fba") -> UnifiedWorkflowRun:
        run = self._get(session, workflow_run_id)
        if run.current_phase != "SIMULATION":
            raise OrchestratorPhaseError(f"run_simulation requires phase SIMULATION, run is in {run.current_phase!r}")
        self._bump(run, expected_version)
        module_ref = self._simulation.start(
            session, request={
                "project_id": run.project_id, "design_version_id": run.design_version_ref, "chassis": chassis,
                "environment": environment, "model_id": model_id, "actor_id": actor_id, "evaluation_reference": run.evaluation_run_ref,
            }, context={},
        )
        run.simulation_campaign_ref = module_ref.run_id
        run.current_module = "virtual_cell"
        run.updated_at = now()
        session.flush()

        from harness.virtual_cell.models import CompatibilityReport, PredictionReview
        from sqlalchemy import select

        compat = session.execute(select(CompatibilityReport).where(CompatibilityReport.simulation_case_id == module_ref.run_id).order_by(CompatibilityReport.created_at.desc())).scalars().first()
        model_gate = self.gates.evaluate(
            "model_applicability", compatibility_decision=(compat.decision if compat else None),
            blocking_reasons=list(compat.blocking_reasons) if compat else [], case_ref=module_ref.run_id,
        )
        self._record_gate(session, run, model_gate, actor=actor_id)

        review = session.execute(select(PredictionReview).where(PredictionReview.simulation_case_id == module_ref.run_id).order_by(PredictionReview.created_at.desc())).scalars().first()
        evidence_gate = self.gates.evaluate(
            "simulation_evidence", review_decision=(review.decision if review else None),
            findings=(review.findings if review else []), case_ref=module_ref.run_id,
        )
        self._record_gate(session, run, evidence_gate, actor=actor_id)

        if evidence_gate.decision == "blocked":
            self._block(session, run, reason=f"simulation_evidence gate blocked: {evidence_gate.blocking_findings}", actor_id=actor_id)
            return run
        # not_applicable / pass / pass_with_conditions all permit proceeding
        # to experiment planning - a model that legitimately does not cover
        # this intervention is not a failure of the workflow (prompt §4.3:
        # "是否进入 SIMULATION 必须由模型适用性决定,不得强制所有设计都模拟").
        self._transition_phase(session, run, to_phase="WAITING_FOR_EXPERIMENT", reason=f"simulation phase complete (evidence gate={evidence_gate.decision})", actor_id=actor_id)
        return run

    # -- WAITING_FOR_EXPERIMENT / OBSERVATION_INGESTION ----------------------

    def create_experiment_plan(self, session: Session, workflow_run_id: str, *, expected_version: int, actor_id: str, **plan_kwargs: Any) -> UnifiedWorkflowRun:
        run = self._get(session, workflow_run_id)
        if run.current_phase != "WAITING_FOR_EXPERIMENT":
            raise OrchestratorPhaseError(f"create_experiment_plan requires phase WAITING_FOR_EXPERIMENT, run is in {run.current_phase!r}")
        self._bump(run, expected_version)
        plan = self._experiment.create_plan(session, project_id=run.project_id, design_version_ids=[run.design_version_ref], actor_id=actor_id, **plan_kwargs)
        run.experiment_plan_ref = plan.experiment_plan_id
        run.status = "waiting"
        run.pause_reason = "awaiting experiment execution and result upload (durable wait - survives process restart)"
        run.checkpoint_ref = plan.experiment_plan_id
        run.updated_at = now()
        session.flush()
        append_event(
            session, project_id=run.project_id, event_type=et.ORCH_PAUSED, entity_type="UnifiedWorkflowRun",
            entity_id=run.workflow_run_id, payload={"phase": "WAITING_FOR_EXPERIMENT", "experiment_plan_id": plan.experiment_plan_id},
            actor_type="agent" if actor_id == "system" else "human", actor_id=actor_id,
            correlation_id=run.correlation_id, workflow_run_id=run.workflow_run_id,
        )
        return run

    def record_experiment_run_and_ingest_observation(
        self, session: Session, workflow_run_id: str, *, expected_version: int, actor_id: str, raw_observation: Any, run_kwargs: dict[str, Any] | None = None,
    ) -> UnifiedWorkflowRun:
        """The cross-process resume point (prompt §4.6): callable in a
        fresh process against nothing but the DB row, exactly like Problem
        02's `WAITING_FOR_RESULTS`/Problem 03's `awaiting_test_result`."""
        run = self._get(session, workflow_run_id)
        if run.current_phase != "WAITING_FOR_EXPERIMENT":
            raise OrchestratorPhaseError(f"record_experiment_run_and_ingest_observation requires phase WAITING_FOR_EXPERIMENT, run is in {run.current_phase!r}")
        self._bump(run, expected_version)
        exp_run = self._experiment.record_run(
            session, project_id=run.project_id, experiment_plan_id=run.experiment_plan_ref,
            executed_design_version_ids=[run.design_version_ref], actor_id=actor_id, **(run_kwargs or {}),
        )
        run.experiment_run_ref = exp_run.experiment_run_id
        run.status = "active"
        run.pause_reason = None
        run.updated_at = now()
        session.flush()
        append_event(
            session, project_id=run.project_id, event_type=et.ORCH_RESUMED, entity_type="UnifiedWorkflowRun",
            entity_id=run.workflow_run_id, payload={"experiment_run_id": exp_run.experiment_run_id},
            actor_type="agent" if actor_id == "system" else "human", actor_id=actor_id,
            correlation_id=run.correlation_id, workflow_run_id=run.workflow_run_id,
        )
        self._transition_phase(session, run, to_phase="OBSERVATION_INGESTION", reason="experiment run recorded", actor_id=actor_id)

        obs, report = self._experiment.ingest_observation(session, project_id=run.project_id, raw=raw_observation, actor_id=actor_id)
        error_flags = [(iss.field, iss.code, iss.message) for iss in report.issues if iss.severity == "error"] if report else []
        qc_gate = self.gates.evaluate("observation_qc", qc_passed=(obs is not None), error_flags=error_flags)
        self._record_gate(session, run, qc_gate, actor=actor_id)
        run.observation_set_ref = [*run.observation_set_ref, obs.observation_id] if obs is not None else run.observation_set_ref
        run.updated_at = now()
        session.flush()
        if qc_gate.decision != "pass":
            run.status = "waiting"
            run.pause_reason = f"observation_qc gate: {qc_gate.decision} - biological belief NOT updated from this observation"
            run.updated_at = now()
            session.flush()
            return run
        self._transition_phase(session, run, to_phase="LEARNING", reason="observation passed QC", actor_id=actor_id)
        return run

    # -- LEARNING / REDESIGN / COMPLETED -------------------------------------

    def run_learning(self, session: Session, workflow_run_id: str, *, expected_version: int, actor_id: str, observed_results: list[dict[str, Any]], construction_verified: bool, assay_qc_passed: bool) -> UnifiedWorkflowRun:
        run = self._get(session, workflow_run_id)
        if run.current_phase != "LEARNING":
            raise OrchestratorPhaseError(f"run_learning requires phase LEARNING, run is in {run.current_phase!r}")
        self._bump(run, expected_version)
        handoff = self._design.get_handoff(session, run.design_project_ref)
        selected_id = None
        for candidate_id in handoff.payload_refs.get("candidate_ids", "").split(","):
            if candidate_id:
                selected_id = candidate_id
                break
        outcome = self._design.ingest_outcome(
            session, design_id=selected_id, actor_id=actor_id, observed_results=observed_results,
            construction_verified=construction_verified, assay_qc_passed=assay_qc_passed,
        )
        stop = self.gates.evaluate("stop", decided_next_action=outcome.decided_next_action, run_ref=run.workflow_run_id)
        self._record_gate(session, run, stop, actor=actor_id)
        if outcome.decided_next_action == "stop":
            run.status = "completed"
            run.updated_at = now()
            session.flush()
            self._transition_phase(session, run, to_phase="COMPLETED", reason="learning: decided_next_action=stop", actor_id=actor_id)
            append_event(
                session, project_id=run.project_id, event_type=et.ORCH_RUN_COMPLETED, entity_type="UnifiedWorkflowRun",
                entity_id=run.workflow_run_id, payload={"outcome": outcome.decided_next_action},
                actor_type="agent" if actor_id == "system" else "human", actor_id=actor_id,
                correlation_id=run.correlation_id, workflow_run_id=run.workflow_run_id,
            )
        elif outcome.decided_next_action == "diagnosis_reopened":
            self._transition_phase(session, run, to_phase="DIAGNOSIS", reason="learning: outcome reopened diagnosis", actor_id=actor_id)
            run.status = "active"
            run.updated_at = now()
            session.flush()
        else:
            self._transition_phase(session, run, to_phase="REDESIGN", reason=f"learning: decided_next_action={outcome.decided_next_action}", actor_id=actor_id)
            run.status = "active"
            run.updated_at = now()
            session.flush()
        return run

    # -- read-only status / reconciliation -----------------------------------

    def get_status(self, session: Session, workflow_run_id: str) -> UnifiedWorkflowRun:
        return self._get(session, workflow_run_id)

    def reconcile(self, session: Session, workflow_run_id: str) -> dict[str, Any]:
        """Prompt §4.6: "模块完成但顶层未更新时的 reconciliation" and
        "Event Ledger 可重建顶层状态". Re-derives each module's real current
        status from its own tables (never from this run row's cached
        pointers) and reports any drift - it does not silently overwrite
        `current_phase`, since a human may be mid-review of a blocked run."""
        run = self._get(session, workflow_run_id)
        report: dict[str, Any] = {"workflow_run_id": workflow_run_id, "current_phase": run.current_phase, "modules": {}}
        if run.diagnosis_run_ref:
            report["modules"]["diagnosis"] = self._diagnosis.get_status(session, run.diagnosis_run_ref).__dict__
        if run.design_project_ref:
            report["modules"]["engineering_design"] = self._design.get_status(session, run.design_project_ref).__dict__
        if run.evaluation_run_ref:
            report["modules"]["scientific_evaluation"] = self._evaluation.get_status(session, run.evaluation_run_ref).__dict__
        if run.simulation_campaign_ref:
            report["modules"]["virtual_cell"] = self._simulation.get_status(session, run.simulation_campaign_ref).__dict__
        from harness.projects.models import ProjectEvent
        from sqlalchemy import select

        rebuilt_phase = None
        events = session.execute(
            select(ProjectEvent).where(ProjectEvent.workflow_run_id == workflow_run_id, ProjectEvent.event_type == et.ORCH_PHASE_CHANGED).order_by(ProjectEvent.seq)
        ).scalars().all()
        if events:
            rebuilt_phase = events[-1].payload.get("to_phase")
        report["rebuilt_phase_from_ledger"] = rebuilt_phase
        report["ledger_matches_materialized_state"] = (rebuilt_phase == run.current_phase)
        return report

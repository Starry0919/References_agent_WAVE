# =============================================================================
# Agent 工具:synbio_workflow_run —— Workflow-Engine 控制的合成生物学设计流程
# =============================================================================
#
# 与 tools/synbio_design_v1.py(单次调用、无阶段状态、无 Gate)不同,本工具
# 调用 harness/workflow/ 下的 Workflow Engine:11 个程序状态节点
# (INTAKE...REPORT)由 WorkflowController 唯一控制迁移,每步都有结构化
# BiologicalState / EngineeringDecision / StageRecord,并经过 7 个 Validation
# Gate(含强制人工审批)。旧工具原样保留,不做替换,详见
# workflow/design/evolution/后端精修/问题01_...md。
#
# LLM 只能通过本工具的 request/run_id/user_response/approve 四个参数与流程
# 交互;current_stage 的实际迁移、Gate 判定、工具白名单均由 Controller 决定,
# 不受 LLM 直接控制。
# =============================================================================
from __future__ import annotations

from typing import Any

from harness.tools import tool
from harness.workflow.controller import WorkflowController
from harness.workflow.state import RunStatus, WorkflowRun
from harness.workflow.synbio_stages import build_controller

_controller: WorkflowController | None = None


def _get_controller() -> WorkflowController:
    global _controller
    if _controller is None:
        _controller = build_controller()
    return _controller


def _summarize(run: WorkflowRun) -> dict[str, Any]:
    return {
        "run_id": run.run_id,
        "status": run.status.value,
        "current_stage": run.current_stage,
        "pending_request": run.pending_request.model_dump() if run.pending_request else None,
        "termination_reason": run.termination_reason,
        "engineering_decisions": [
            {
                "decision_id": d.decision_id,
                "target": d.target_entity.canonical_id,
                "target_type": d.target_entity.type.value,
                "operation": d.operation.value,
                "status": d.status.value,
                "mechanism": d.mechanism,
                "expected_effect": d.expected_effect,
                "risks": d.risks,
                "confidence": d.confidence,
                "rejection_reason": d.rejection_reason,
            }
            for d in run.engineering_decisions
        ],
        "final_report": run.final_report,
    }


@tool
def synbio_workflow_run(request: str = "", run_id: str = "", user_response: str = "", approve: str = "") -> dict:
    """Run the Workflow-Engine-controlled synthetic biology design pipeline.

    Unlike synbio_design_v1 (a single opaque call with no stage state or
    gates), this tool drives a program-controlled state machine (INTAKE ->
    TASK_NORMALIZATION -> ... -> REPORT) with structured BiologicalState and
    EngineeringDecision objects, and real validation gates - including a
    forced human-approval gate for risky actions (e.g. knocking out a gene
    flagged essential). The controller, not the calling LLM, decides stage
    transitions and gate outcomes; this tool only submits a request or a
    user answer and reports back the resulting structured state.

    Two ways to call this:
    1. Start a new run: pass `request` (a natural-language engineering
       request, e.g. "Improve E. coli K-12 L-tryptophan production from
       glucose"); leave `run_id` empty.
    2. Resume a paused run: pass the `run_id` from a previous call whose
       `status` was "waiting_user", plus either `user_response` (free text
       answering a "missing_information" pending_request) or `approve`
       ("approved" or "rejected", answering an "approval" pending_request -
       check the previous response's `pending_request.kind` to know which
       applies).

    Returns a dict: run_id, status (queued|running|waiting_user|blocked|
    failed|completed|cancelled), current_stage, pending_request (or null),
    termination_reason (or null), engineering_decisions (each with its
    target, operation, status, mechanism, risks, confidence, and - if
    rejected - why), and final_report once status is "completed". Never
    silently guesses past a missing chassis/target or an unapproved
    high-risk action - "waiting_user" means exactly that, and the run must
    be resumed with an answer before it continues.

    Args:
        request: Natural-language design request for a new run (ignored if run_id is set).
        run_id: An existing run's id, to resume it instead of starting a new one.
        user_response: Free-text answer to a pending "missing_information" question.
        approve: "approved" or "rejected" - answer to a pending "approval" question.
    """
    controller = _get_controller()

    if run_id:
        run = controller.resume(run_id)
        if run is None:
            return {"error": f"no such run_id: {run_id}"}
        if run.status == RunStatus.waiting_user and run.pending_request is not None:
            if run.pending_request.kind.value == "missing_information" and user_response.strip():
                run = controller.submit_user_response(run, response=user_response.strip())
            elif run.pending_request.kind.value == "approval" and approve.strip():
                decision = "approved" if approve.strip().lower().startswith("approv") else "rejected"
                run = controller.submit_approval(
                    run,
                    decision_id=run.pending_request.decision_id or "",
                    approver="chat_user",
                    decision=decision,
                    risk_reason=run.pending_request.question,
                )
            else:
                return _summarize(run)  # still waiting - no usable answer supplied
    else:
        if not request.strip():
            return {"error": "request must be non-empty to start a new run"}
        run = controller.create_run(request.strip())

    run = controller.run_to_completion_or_pause(run, max_steps=30)
    return _summarize(run)

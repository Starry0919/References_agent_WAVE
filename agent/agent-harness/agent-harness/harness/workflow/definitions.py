"""The main state graph (doc 5.3) as data, not prose: `Stage` enumerates the
11 mandated nodes; `StageDefinition` is each node's contract (required
inputs, output shape, allowed tools, gates, retry/fallback, legal next
stages, human-approval requirement, honesty label). `STAGE_DEFINITIONS` is
the single source of truth `WorkflowController` reads to decide what is
*allowed* - it never invents a transition.

Stages beyond this round's depth (SYSTEM_RECONSTRUCTION,
BOTTLENECK_PRIORITIZATION) are `implementation_status=scaffold`: a runnable
skeleton with real gates and structured I/O, not expert-level diagnosis
algorithms (that is problem 4, explicitly deferred - doc line 566).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, Callable

from harness.workflow.state import ImplementationStatus

if TYPE_CHECKING:
    from harness.workflow.state import WorkflowRun


class Stage(str, Enum):
    INTAKE = "INTAKE"
    TASK_NORMALIZATION = "TASK_NORMALIZATION"
    CONTEXT_AND_EVIDENCE_ACQUISITION = "CONTEXT_AND_EVIDENCE_ACQUISITION"
    SYSTEM_RECONSTRUCTION = "SYSTEM_RECONSTRUCTION"
    BIOLOGICAL_DIAGNOSIS = "BIOLOGICAL_DIAGNOSIS"
    BOTTLENECK_PRIORITIZATION = "BOTTLENECK_PRIORITIZATION"
    ENGINEERING_STRATEGY_GENERATION = "ENGINEERING_STRATEGY_GENERATION"
    MODEL_AND_RULE_VALIDATION = "MODEL_AND_RULE_VALIDATION"
    EXPERIMENT_AND_IMPLEMENTATION_PLAN = "EXPERIMENT_AND_IMPLEMENTATION_PLAN"
    FINAL_EVALUATION = "FINAL_EVALUATION"
    REPORT = "REPORT"


# (ok, reason_if_blocked)
EntryCondition = Callable[["WorkflowRun"], "tuple[bool, str]"]


@dataclass(frozen=True)
class StageDefinition:
    stage: Stage
    required_inputs: tuple[str, ...]
    output_contract: str
    allowed_tools: tuple[str, ...]
    gates: tuple[str, ...]
    retry_limit: int
    fallback: str
    allowed_next_stages: tuple[Stage, ...]
    human_approval_required: bool
    implementation_status: ImplementationStatus
    entry_condition: EntryCondition | None = field(default=None, compare=False)


def _always_ok(_run: "WorkflowRun") -> tuple[bool, str]:
    return True, ""


def _has_task_spec(run: "WorkflowRun") -> tuple[bool, str]:
    if run.task_spec is None:
        return False, "task_spec missing: TASK_NORMALIZATION has not produced a TaskSpec yet"
    return True, ""


def _has_evidence_or_diagnosis(run: "WorkflowRun") -> tuple[bool, str]:
    if not run.diagnoses:
        return False, "no DiagnosisRecord present: BIOLOGICAL_DIAGNOSIS has not run yet"
    return True, ""


def _has_candidates(run: "WorkflowRun") -> tuple[bool, str]:
    if not run.candidate_designs:
        return False, "no candidate_designs present: ENGINEERING_STRATEGY_GENERATION produced none"
    return True, ""


def _all_candidates_validated(run: "WorkflowRun") -> tuple[bool, str]:
    """Guards against skipping MODEL_AND_RULE_VALIDATION entirely (doc's
    integration scenario: "LLM requests skipping a required validation
    stage" must be rejected) - every candidate_designs entry must have a
    corresponding engineering_decisions entry before an implementation plan
    may be built from it."""
    if not run.engineering_decisions:
        return False, "no engineering_decisions present: MODEL_AND_RULE_VALIDATION has not resolved any candidates yet"
    resolved_ids = {d.decision_id for d in run.engineering_decisions}
    unresolved = [c.decision_id for c in run.candidate_designs if c.decision_id not in resolved_ids]
    if unresolved:
        return False, f"{len(unresolved)} candidate_designs have not been through MODEL_AND_RULE_VALIDATION yet: {unresolved}"
    return True, ""


STAGE_DEFINITIONS: dict[Stage, StageDefinition] = {
    Stage.INTAKE: StageDefinition(
        stage=Stage.INTAKE,
        required_inputs=("raw_request",),
        output_contract="ack",
        allowed_tools=(),
        gates=("SchemaGate",),
        retry_limit=1,
        fallback="fail",
        allowed_next_stages=(Stage.TASK_NORMALIZATION,),
        human_approval_required=False,
        implementation_status=ImplementationStatus.validated,
        entry_condition=_always_ok,
    ),
    Stage.TASK_NORMALIZATION: StageDefinition(
        stage=Stage.TASK_NORMALIZATION,
        required_inputs=("raw_request",),
        output_contract="TaskSpec",
        allowed_tools=(),
        gates=("SchemaGate",),
        retry_limit=2,
        fallback="waiting_user",
        allowed_next_stages=(Stage.CONTEXT_AND_EVIDENCE_ACQUISITION,),
        human_approval_required=False,
        implementation_status=ImplementationStatus.partial,
        entry_condition=_always_ok,
    ),
    Stage.CONTEXT_AND_EVIDENCE_ACQUISITION: StageDefinition(
        stage=Stage.CONTEXT_AND_EVIDENCE_ACQUISITION,
        required_inputs=("task_spec",),
        output_contract="EvidenceRecord[]",
        allowed_tools=("ddr_retrieval",),
        gates=("SchemaGate",),
        retry_limit=2,
        fallback="degrade_to_no_evidence",
        allowed_next_stages=(Stage.SYSTEM_RECONSTRUCTION,),
        human_approval_required=False,
        implementation_status=ImplementationStatus.partial,
        entry_condition=_has_task_spec,
    ),
    Stage.SYSTEM_RECONSTRUCTION: StageDefinition(
        stage=Stage.SYSTEM_RECONSTRUCTION,
        required_inputs=("task_spec", "evidence_records"),
        output_contract="BiologicalState",
        allowed_tools=(),
        gates=("SchemaGate",),
        retry_limit=1,
        fallback="fail",
        allowed_next_stages=(Stage.BIOLOGICAL_DIAGNOSIS,),
        human_approval_required=False,
        implementation_status=ImplementationStatus.scaffold,
        entry_condition=_has_task_spec,
    ),
    Stage.BIOLOGICAL_DIAGNOSIS: StageDefinition(
        stage=Stage.BIOLOGICAL_DIAGNOSIS,
        required_inputs=("biological_state", "evidence_records"),
        output_contract="DiagnosisRecord",
        allowed_tools=(),
        gates=("SchemaGate", "EvidenceGate"),
        retry_limit=2,
        fallback="insufficient_evidence",
        allowed_next_stages=(Stage.BOTTLENECK_PRIORITIZATION,),
        human_approval_required=False,
        implementation_status=ImplementationStatus.partial,
        entry_condition=_always_ok,
    ),
    Stage.BOTTLENECK_PRIORITIZATION: StageDefinition(
        stage=Stage.BOTTLENECK_PRIORITIZATION,
        required_inputs=("diagnosis",),
        output_contract="DiagnosisRecord.prioritized_bottlenecks",
        allowed_tools=(),
        gates=("SchemaGate",),
        retry_limit=1,
        fallback="fail",
        allowed_next_stages=(Stage.ENGINEERING_STRATEGY_GENERATION,),
        human_approval_required=False,
        implementation_status=ImplementationStatus.scaffold,
        entry_condition=_has_evidence_or_diagnosis,
    ),
    Stage.ENGINEERING_STRATEGY_GENERATION: StageDefinition(
        stage=Stage.ENGINEERING_STRATEGY_GENERATION,
        required_inputs=("diagnosis", "evidence_records"),
        output_contract="EngineeringDecision[] (status=proposed)",
        allowed_tools=(),
        gates=("SchemaGate", "CandidateDiversityGate"),
        retry_limit=2,
        fallback="insufficient_evidence",
        allowed_next_stages=(Stage.MODEL_AND_RULE_VALIDATION,),
        human_approval_required=False,
        implementation_status=ImplementationStatus.partial,
        entry_condition=_has_evidence_or_diagnosis,
    ),
    Stage.MODEL_AND_RULE_VALIDATION: StageDefinition(
        stage=Stage.MODEL_AND_RULE_VALIDATION,
        required_inputs=("candidate_designs",),
        output_contract="EngineeringDecision[] (status resolved)",
        allowed_tools=("fba_flux_analysis",),
        gates=(
            "SchemaGate",
            "IdentityGate",
            "BiologicalRuleGate",
            "EvidenceGate",
            "ModelApplicabilityGate",
            "CandidateDiversityGate",
            "SafetyHumanGate",
        ),
        retry_limit=2,
        fallback="revise_candidates",
        allowed_next_stages=(Stage.EXPERIMENT_AND_IMPLEMENTATION_PLAN,),
        human_approval_required=True,
        implementation_status=ImplementationStatus.validated,
        entry_condition=_has_candidates,
    ),
    Stage.EXPERIMENT_AND_IMPLEMENTATION_PLAN: StageDefinition(
        stage=Stage.EXPERIMENT_AND_IMPLEMENTATION_PLAN,
        required_inputs=("engineering_decisions",),
        output_contract="ValidationPlanItem[]",
        allowed_tools=(),
        gates=("SchemaGate", "SafetyHumanGate"),
        retry_limit=2,
        fallback="waiting_user",
        allowed_next_stages=(Stage.FINAL_EVALUATION,),
        human_approval_required=True,
        implementation_status=ImplementationStatus.partial,
        entry_condition=_all_candidates_validated,
    ),
    Stage.FINAL_EVALUATION: StageDefinition(
        stage=Stage.FINAL_EVALUATION,
        required_inputs=("engineering_decisions", "validation_records"),
        output_contract="summary dict",
        allowed_tools=(),
        gates=("SchemaGate",),
        retry_limit=1,
        fallback="fail",
        allowed_next_stages=(Stage.REPORT,),
        human_approval_required=False,
        implementation_status=ImplementationStatus.partial,
        entry_condition=_always_ok,
    ),
    Stage.REPORT: StageDefinition(
        stage=Stage.REPORT,
        required_inputs=("engineering_decisions", "validation_records"),
        output_contract="final_report: str",
        allowed_tools=(),
        gates=("SchemaGate",),
        retry_limit=1,
        fallback="fail",
        allowed_next_stages=(),  # terminal
        human_approval_required=False,
        implementation_status=ImplementationStatus.validated,
        entry_condition=_always_ok,
    ),
}

STAGE_ORDER: tuple[Stage, ...] = (
    Stage.INTAKE,
    Stage.TASK_NORMALIZATION,
    Stage.CONTEXT_AND_EVIDENCE_ACQUISITION,
    Stage.SYSTEM_RECONSTRUCTION,
    Stage.BIOLOGICAL_DIAGNOSIS,
    Stage.BOTTLENECK_PRIORITIZATION,
    Stage.ENGINEERING_STRATEGY_GENERATION,
    Stage.MODEL_AND_RULE_VALIDATION,
    Stage.EXPERIMENT_AND_IMPLEMENTATION_PLAN,
    Stage.FINAL_EVALUATION,
    Stage.REPORT,
)

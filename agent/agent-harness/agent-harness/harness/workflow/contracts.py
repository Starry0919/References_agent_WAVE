"""Pydantic v2 schema contracts for the synbio Workflow Engine.

Every object mandated by the architecture doc's section 5.2 is a real,
validated structural type here - never a loose dict and never markdown
prose. Unknown biological values must be the explicit string "unknown"
(never silently omitted or guessed) - see `BiologicalState` and
`TaskSpec.missing_fields`.

Fields quote directly from the design doc's yaml where one was specified
(BiologicalState, EngineeringDecision, GateResult, StageRecord in
`state.py`); other supporting types (EvidenceRecord, ValidationPlanItem,
ApprovalRecord, ToolRecord, StageOutput) are new but follow the same
"structured, provenance-carrying, no fabrication" rules the doc lays out.
"""
from __future__ import annotations

import time
import uuid
from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

ConfidenceLevel = Literal["high", "medium", "low"]


def new_id(prefix: str) -> str:
    """Short, readable, collision-resistant id: PREFIX-<12 hex chars>."""
    return f"{prefix}-{uuid.uuid4().hex[:12]}"


class StrictModel(BaseModel):
    """Base for every contract: reject unknown fields so a stage adapter
    that forgets to translate a field fails loudly (SchemaGate territory),
    not silently."""

    model_config = ConfigDict(extra="forbid")


# ---------------------------------------------------------------------------
# Task intake / normalization
# ---------------------------------------------------------------------------


class TaskSpec(StrictModel):
    """TASK_NORMALIZATION stage output. `product == "unknown"` or a
    non-empty `missing_fields` means a required field could not be
    identified from the request - the controller must not silently guess
    past this (doc 5.5: missing chassis/target -> waiting_user)."""

    raw_request: str
    product: str
    host: str
    host_was_defaulted: bool = False
    substrate: str
    goal: str
    engineering_type: str
    missing_fields: list[str] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# BiologicalState (doc 5.2) - AI-Virtual-Cell-inspired structured state
# ---------------------------------------------------------------------------


class HostState(StrictModel):
    species: str = "unknown"
    strain: str = "unknown"
    reference_genome_version: str = "unknown"


class GenotypeState(StrictModel):
    baseline_genotype: list[str] = Field(default_factory=list)
    engineered_changes: list[str] = Field(default_factory=list)


class PhenotypeState(StrictModel):
    target_trait: str = "unknown"
    target_product: str = "unknown"
    baseline_measurement: str = "unknown"
    desired_endpoint: str = "unknown"


class EnvironmentState(StrictModel):
    carbon_source: str = "unknown"
    medium: str = "unknown"
    oxygenation: str = "unknown"
    temperature: str = "unknown"
    cultivation_mode: str = "unknown"


class FluxObservation(StrictModel):
    entity: str
    value: str
    source_record_id: str | None = None


class MetaboliteObservation(StrictModel):
    entity: str
    value: str
    source_record_id: str | None = None


class MetabolicState(StrictModel):
    flux_observations: list[FluxObservation] = Field(default_factory=list)
    metabolite_observations: list[MetaboliteObservation] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)


class OmicsState(StrictModel):
    transcriptome_records: list[str] = Field(default_factory=list)
    proteome_records: list[str] = Field(default_factory=list)
    metabolome_records: list[str] = Field(default_factory=list)


class ProvenanceState(StrictModel):
    source_record_ids: list[str] = Field(default_factory=list)


class UncertaintyState(StrictModel):
    missing_fields: list[str] = Field(default_factory=list)
    conflicting_fields: list[str] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)


class BiologicalState(StrictModel):
    host: HostState = Field(default_factory=HostState)
    genotype: GenotypeState = Field(default_factory=GenotypeState)
    phenotype: PhenotypeState = Field(default_factory=PhenotypeState)
    environment: EnvironmentState = Field(default_factory=EnvironmentState)
    metabolic_state: MetabolicState = Field(default_factory=MetabolicState)
    omics: OmicsState = Field(default_factory=OmicsState)
    provenance: ProvenanceState = Field(default_factory=ProvenanceState)
    uncertainty: UncertaintyState = Field(default_factory=UncertaintyState)


# ---------------------------------------------------------------------------
# Diagnosis / bottleneck prioritization
# ---------------------------------------------------------------------------


class BottleneckClass(str, Enum):
    """Coarse mechanism-layer tags a bottleneck description is classified
    into (BOTTLENECK_PRIORITIZATION stage; scaffold-depth by design - full
    diagnosis algorithms are problem 4, out of scope here, per doc line 566).
    Keeping this taxonomy small and honest beats a deep but unvalidated one."""

    precursor_supply = "precursor_supply"
    feedback_inhibition = "feedback_inhibition"
    competing_pathway = "competing_pathway"
    growth_burden = "growth_burden"
    regulatory = "regulatory"
    unclassified = "unclassified"


class PrioritizedBottleneck(StrictModel):
    description: str
    bottleneck_class: BottleneckClass = BottleneckClass.unclassified
    priority: Literal["primary", "secondary", "optional"] = "secondary"


class DiagnosisRecord(StrictModel):
    diagnosis_id: str = Field(default_factory=lambda: new_id("DIAG"))
    source_ddr_id: str | None = None
    observations: list[str] = Field(default_factory=list)
    bottlenecks: list[str] = Field(default_factory=list)
    prioritized_bottlenecks: list[PrioritizedBottleneck] = Field(default_factory=list)
    mechanistic_explanation: str = ""
    hypothesis: str = ""
    expected_effect: str = ""


# ---------------------------------------------------------------------------
# Evidence
# ---------------------------------------------------------------------------


class EvidenceRecord(StrictModel):
    evidence_record_id: str = Field(default_factory=lambda: new_id("EVID"))
    action_source: Literal["ddr_reasoning", "engineering_action_library", "unknown"]
    evidence_status: Literal["reference_available", "general_engineering_knowledge", "unknown"]
    reference: str | None = None
    confidence: ConfidenceLevel = "low"
    needs_validation: bool = True
    literature_support: Literal["high", "medium", "low", "none"] = "none"
    mechanistic_support: Literal["high", "medium", "low", "none"] = "none"
    strain_similarity: Literal["high", "medium", "low", "unknown"] = "unknown"
    transferability: Literal["high", "medium", "low", "unknown"] = "unknown"
    reason: str = ""
    source_ddr_id: str | None = None


# ---------------------------------------------------------------------------
# EngineeringDecision (doc 5.2) - the domain-core object
# ---------------------------------------------------------------------------


class DecisionStatus(str, Enum):
    proposed = "proposed"
    accepted = "accepted"
    rejected = "rejected"
    revised = "revised"
    human_review = "human_review"


class TargetEntityType(str, Enum):
    gene = "gene"
    reaction = "reaction"
    metabolite = "metabolite"
    regulatory_element = "regulatory_element"
    pathway = "pathway"


class OperationType(str, Enum):
    knockout = "knockout"
    knockdown = "knockdown"
    overexpression = "overexpression"
    mutation = "mutation"
    insertion = "insertion"
    promoter_tuning = "promoter_tuning"
    rbs_tuning = "rbs_tuning"
    dynamic_regulation = "dynamic_regulation"
    other = "other"


class TargetEntity(StrictModel):
    type: TargetEntityType
    canonical_id: str
    display_name: str


class EngineeringDecision(StrictModel):
    """Every accepted decision must trace to a diagnosis/mechanism, evidence
    or model, risk, and a validation plan (doc 5.2). `parent_decision_ids`
    links a revised/replacement decision (e.g. CRISPRi proposed after an
    essential-gene knockout was rejected) back to the decision it succeeds -
    the gate that rejects the original must never rewrite it in place."""

    decision_id: str = Field(default_factory=lambda: new_id("DEC"))
    parent_decision_ids: list[str] = Field(default_factory=list)
    status: DecisionStatus = DecisionStatus.proposed
    diagnosis_id: str | None = None
    target_entity: TargetEntity
    operation: OperationType
    mechanism: str
    expected_effect: str
    affected_state_fields: list[str] = Field(default_factory=list)
    implementation_outline: str = ""
    evidence_record_ids: list[str] = Field(default_factory=list)
    model_prediction_ids: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    tradeoffs: list[str] = Field(default_factory=list)
    validation_plan_ids: list[str] = Field(default_factory=list)
    confidence: ConfidenceLevel = "low"
    uncertainty: list[str] = Field(default_factory=list)
    rejection_reason: str | None = None


# ---------------------------------------------------------------------------
# Validation plan
# ---------------------------------------------------------------------------


class ValidationLevel(str, Enum):
    genotype = "genotype"
    mechanism = "mechanism"
    phenotype = "phenotype"
    tradeoff = "tradeoff"


class ValidationPlanItem(StrictModel):
    validation_id: str = Field(default_factory=lambda: new_id("VAL"))
    decision_id: str | None = None
    level: ValidationLevel
    description: str


# ---------------------------------------------------------------------------
# Gates
# ---------------------------------------------------------------------------


class GateStatus(str, Enum):
    passed = "pass"
    revise = "revise"
    insufficient_evidence = "insufficient_evidence"
    human_review = "human_review"
    fail = "fail"


# Worst-status-wins precedence for aggregating multiple gate results into
# one StageRecord.gate_result (design-review fix: explicit, not implicit
# call order).
GATE_STATUS_SEVERITY: dict[GateStatus, int] = {
    GateStatus.passed: 0,
    GateStatus.revise: 1,
    GateStatus.insufficient_evidence: 2,
    GateStatus.human_review: 3,
    GateStatus.fail: 4,
}


class GateViolation(StrictModel):
    gate: str
    code: str
    message: str
    target_id: str | None = None


class GateResult(StrictModel):
    gate_name: str
    status: GateStatus
    violations: list[GateViolation] = Field(default_factory=list)
    required_actions: list[str] = Field(default_factory=list)
    next_stage: str | None = None


# ---------------------------------------------------------------------------
# Human approval (SafetyHumanGate policy record)
# ---------------------------------------------------------------------------


class ApprovalDecision(str, Enum):
    approved = "approved"
    rejected = "rejected"


class ApprovalRecord(StrictModel):
    """`scope` names exactly what this approval covers (typically one
    decision_id) - approving one action never implies approval of any
    action derived from it (doc 5.7)."""

    approval_id: str = Field(default_factory=lambda: new_id("APR"))
    requested_action: str
    risk_reason: str
    evidence_snapshot: list[str] = Field(default_factory=list)
    approver: str
    decision: ApprovalDecision
    timestamp: float = Field(default_factory=time.time)
    scope: str


# ---------------------------------------------------------------------------
# Tool execution provenance (harness/tools/executor.py)
# ---------------------------------------------------------------------------


class ToolFailureClass(str, Enum):
    transient = "transient"
    invalid_input = "invalid_input"
    unavailable = "unavailable"
    out_of_domain = "out_of_domain"
    fatal = "fatal"


class ToolRecord(StrictModel):
    tool_call_id: str = Field(default_factory=lambda: new_id("TOOL"))
    stage_id: str | None = None
    name: str
    arguments: dict[str, Any] = Field(default_factory=dict)
    idempotency_key: str | None = None
    attempt: int = 1
    started_at: float
    ended_at: float | None = None
    is_error: bool = False
    failure_class: ToolFailureClass | None = None
    result_summary: str = ""
    cached: bool = False


# ---------------------------------------------------------------------------
# Stage output contract (doc 5.4) - what a stage implementation may return.
# `requested_action` is only ever a *request*; the controller has final
# say over the actual next stage (see harness/workflow/controller.py).
# Kept in place even though today's stage impls are deterministic, not
# LLM-driven, so a future LLM-backed stage plugs into the same contract.
# ---------------------------------------------------------------------------


class RequestedAction(str, Enum):
    continue_ = "continue"
    request_tool = "request_tool"
    request_user = "request_user"
    revise = "revise"
    stop = "stop"


class StageOutput(StrictModel):
    stage_output: dict[str, Any] = Field(default_factory=dict)
    requested_action: RequestedAction = RequestedAction.continue_
    requested_tool: str | None = None
    reason: str = ""
    confidence: ConfidenceLevel = "low"
    missing_information: list[str] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Pending human-in-the-loop request (disambiguates the two "waiting_user"
# cases: a missing required field vs. a risky decision needing approval)
# ---------------------------------------------------------------------------


class PendingRequestKind(str, Enum):
    missing_information = "missing_information"
    approval = "approval"


class PendingRequest(StrictModel):
    kind: PendingRequestKind
    stage_id: str
    question: str
    decision_id: str | None = None

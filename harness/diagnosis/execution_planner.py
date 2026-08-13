"""Experimental Execution Planner (doc03 4.11/3.11): the minimal reviewable
plan for a selected `DiagnosticTest`. Readiness is capped below `ready`
whenever a required field is missing - never claims a plan is executable/
build-ready on an incomplete draft, and never claims materials were
ordered or instruments booked (that is ELN/LIMS/automation's job, doc03
6.4).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

_REQUIRED_FOR_READY = (
    "protocol_reference_or_draft", "materials", "controls", "sampling_schedule",
    "qc_acceptance_criteria", "expected_output_schema", "interpretation_rule", "owner",
)


@dataclass
class PlanDraft:
    protocol_reference_or_draft: str = ""
    materials: list[str] = field(default_factory=list)
    controls: dict[str, Any] = field(default_factory=dict)
    biological_replicates: int | None = None
    technical_replicates: int | None = None
    sampling_schedule: list[Any] = field(default_factory=list)
    qc_acceptance_criteria: list[str] = field(default_factory=list)
    expected_output_schema: dict[str, Any] = field(default_factory=dict)
    interpretation_rule: str = ""
    owner: str | None = None


def assess_readiness(plan: PlanDraft) -> str:
    values: dict[str, Any] = {
        "protocol_reference_or_draft": plan.protocol_reference_or_draft, "materials": plan.materials,
        "controls": plan.controls, "sampling_schedule": plan.sampling_schedule,
        "qc_acceptance_criteria": plan.qc_acceptance_criteria, "expected_output_schema": plan.expected_output_schema,
        "interpretation_rule": plan.interpretation_rule, "owner": plan.owner,
    }
    missing = [k for k in _REQUIRED_FOR_READY if not values[k]]
    if not missing:
        return "ready"
    if plan.protocol_reference_or_draft or plan.materials:
        return "draft"
    return "conceptual"

"""Kinetic / resource-allocation model adapter: honestly unavailable this
round - no calibrated kinetic or resource-allocation model (e.g. an AMN
surrogate) exists in this repository or its dependencies. Same capability
contract as the other adapters.
"""
from __future__ import annotations

from typing import Any

from harness.diagnosis.model_adapters.base import CapabilityStatus, ModelAdapter, ModelRunResult


class KineticResourceAdapter(ModelAdapter):
    name = "kinetic_resource"
    model_name = "kinetic/resource-allocation model"
    model_version = "unavailable"

    def detect_capability(self) -> CapabilityStatus:
        return CapabilityStatus(available=False, reason="no calibrated kinetic/resource-allocation model is available in this environment")

    def validate_input(self, inputs: dict[str, Any], context: dict[str, Any]) -> tuple[bool, list[str]]:
        return False, ["kinetic/resource-allocation adapter is unavailable this round"]

    def run(self, inputs: dict[str, Any], context: dict[str, Any], constraints_objective_parameters: dict[str, Any]) -> ModelRunResult:
        return ModelRunResult(runtime_status="not_computed", log_summary="kinetic/resource-allocation adapter unavailable - no computation attempted")

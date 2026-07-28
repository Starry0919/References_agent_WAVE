"""vEcoli (whole-cell model) adapter: honestly unavailable this round - no
vEcoli installation or dependency exists in this environment (verified
during the Phase 3 audit). Implements the standard capability contract so
a future real integration is a drop-in replacement, not a rewrite of every
caller.
"""
from __future__ import annotations

from typing import Any

from harness.diagnosis.model_adapters.base import CapabilityStatus, ModelAdapter, ModelRunResult


class VEcoliAdapter(ModelAdapter):
    name = "vecoli"
    model_name = "vEcoli whole-cell model"
    model_version = "unavailable"

    def detect_capability(self) -> CapabilityStatus:
        return CapabilityStatus(available=False, reason="no vEcoli installation or dependency is present in this environment")

    def validate_input(self, inputs: dict[str, Any], context: dict[str, Any]) -> tuple[bool, list[str]]:
        return False, ["vEcoli adapter is unavailable this round"]

    def run(self, inputs: dict[str, Any], context: dict[str, Any], constraints_objective_parameters: dict[str, Any]) -> ModelRunResult:
        return ModelRunResult(runtime_status="not_computed", log_summary="vEcoli adapter unavailable - no computation attempted")

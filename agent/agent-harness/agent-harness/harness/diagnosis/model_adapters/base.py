"""Model Adapter Registry contract (doc03 4.7/2.6): a uniform `detect ->
validate_input -> run -> normalize_result` interface for GEM/COBRA, vEcoli,
kinetic/resource-allocation models. Only real, installed models are ever
executed; anything else returns capability_status="unavailable" honestly.
No adapter may have the LLM compute or fabricate its numeric output.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class CapabilityStatus:
    available: bool
    reason: str = ""


@dataclass
class ModelRunResult:
    runtime_status: str  # optimal|infeasible|unbounded|timeout|not_computed|error
    outputs: dict[str, Any] = field(default_factory=dict)
    uncertainty: dict[str, Any] | None = None
    domain_flags: list[str] = field(default_factory=list)
    solver: str | None = None
    log_summary: str = ""
    reproducibility_ref: dict[str, Any] = field(default_factory=dict)


class ModelAdapter(ABC):
    name: str
    model_name: str
    model_version: str

    @abstractmethod
    def detect_capability(self) -> CapabilityStatus: ...

    @abstractmethod
    def validate_input(self, inputs: dict[str, Any], context: dict[str, Any]) -> tuple[bool, list[str]]: ...

    @abstractmethod
    def run(
        self, inputs: dict[str, Any], context: dict[str, Any], constraints_objective_parameters: dict[str, Any]
    ) -> ModelRunResult: ...

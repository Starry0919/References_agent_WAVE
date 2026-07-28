"""The formal module contract (prompt §4.4) and the plain-data shapes
adapters exchange with `harness/orchestrator/service.py` before they are
persisted into `orchestrator_gate_decisions`/`orchestrator_module_handoffs`
rows. Deliberately NOT pydantic `StrictModel` (that convention belongs to
Problem 01's `harness/workflow/contracts.py`) - these are transient,
in-process return values, not persisted/validated wire payloads; the ORM
row is the actual persisted contract.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol


@dataclass
class ModuleRunRef:
    """What `ScientificModuleContract.start()` returns: enough to look the
    run up again later. Never a copy of the run's content."""

    module: str
    run_id: str
    version: int = 1


@dataclass
class ModuleRunStatus:
    """What `ScientificModuleContract.get_status()` returns - a normalized
    view of a module's own (module-specific) status string, not a
    replacement for it. `native_status` keeps the module's own vocabulary
    visible for debugging; `normalized` is what the orchestrator's phase
    logic actually branches on."""

    module: str
    run_id: str
    native_status: str
    normalized: str  # one of: running | waiting_input | completed | blocked | failed
    version: int = 1
    detail: dict[str, Any] = field(default_factory=dict)


@dataclass
class ModuleHandoff:
    """In-process counterpart of `ModuleHandoffRecord` (prompt §4.4's
    YAML). `payload_refs` is ID/version strings only."""

    source_module: str
    source_run_id: str
    target_module: str
    payload_refs: dict[str, str] = field(default_factory=dict)
    preconditions: list[str] = field(default_factory=list)
    unresolved_items: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    confidence_status: str = "unknown"
    source_version: int = 1


@dataclass
class GateDecisionResult:
    """In-process counterpart of `OrchestratorGateDecision` (prompt §4.5's
    YAML), returned by `harness.orchestrator.gates` functions before the
    orchestrator service persists + acts on them."""

    gate_type: str
    decision: str  # GATE_DECISIONS
    evaluated_refs: dict[str, str] = field(default_factory=dict)
    blocking_findings: list[str] = field(default_factory=list)
    non_blocking_findings: list[str] = field(default_factory=list)
    required_actions: list[str] = field(default_factory=list)
    evidence_refs: list[str] = field(default_factory=list)
    rule_versions: dict[str, str] = field(default_factory=dict)
    reviewer_refs: list[str] = field(default_factory=list)


class ScientificModuleContract(Protocol):
    """Prompt §4.4. Real implementations (`harness/orchestrator/adapters/`)
    wrap each module's existing service/loop functions - they do not
    require Problem 3-6 to change their own APIs to fit this shape."""

    def start(self, request: dict[str, Any], context: dict[str, Any]) -> ModuleRunRef: ...

    def get_status(self, run_id: str) -> ModuleRunStatus: ...

    def resume(self, run_id: str, input_ref: dict[str, Any], expected_version: int) -> ModuleRunRef: ...

    def cancel(self, run_id: str, reason: str, actor: str) -> ModuleRunRef: ...

    def get_handoff(self, run_id: str) -> ModuleHandoff: ...

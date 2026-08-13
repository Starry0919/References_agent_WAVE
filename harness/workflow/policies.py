"""Branch / retry / tool / human policies (doc 5.7's risk-tier table, 5.8's
retry-and-termination rules). Pure decision logic, no I/O beyond the
read-only gene registry - kept separate from `gates.py` so `gates.py` can
import it without a cycle (`policies.py` never imports `gates.py`).
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from harness.workflow import gene_registry
from harness.workflow.contracts import EngineeringDecision, OperationType


class RiskTier(str, Enum):
    """doc 5.7 table, in ascending strictness."""

    auto_execute = "auto_execute"
    auto_propose_human_confirm = "auto_propose_human_confirm"
    forced_human_approval = "forced_human_approval"
    forbidden = "forbidden"


class HumanGatePolicy:
    """Classifies an `EngineeringDecision` into a risk tier. Only
    `forced_human_approval` and `forbidden` actually block a transition
    (enforced by gates.safety_human_gate); the other two tiers are
    informational for now (auto_execute) or become a `waiting_user`
    confirmation prompt without a hard state-machine block
    (auto_propose_human_confirm) - this round only implements the two
    tiers the acceptance bar requires to be blocking."""

    def __init__(self) -> None:
        self._essential = gene_registry.essential_genes()

    def classify(self, decision: EngineeringDecision) -> RiskTier:
        gene = decision.target_entity.canonical_id

        # Forbidden: presenting an unvalidated claim as settled fact.
        # Conservative, explicit textual guard - never inferred from vibes.
        outline = (decision.implementation_outline or "").lower()
        if any(phrase in outline for phrase in ("confirmed by experiment", "verified in vivo", "proven in vitro")):
            if not decision.validation_plan_ids:
                return RiskTier.forbidden

        # Forced human approval: essential-gene intervention, or an
        # operation on a large/genome-scale target.
        if decision.operation == OperationType.knockout and gene in self._essential:
            return RiskTier.forced_human_approval
        if decision.target_entity.type.value == "regulatory_element" and "genome-scale" in outline:
            return RiskTier.forced_human_approval

        # Auto-propose, human-confirm: low-confidence key assumption.
        if decision.confidence == "low" and decision.status.value in ("proposed", "human_review"):
            return RiskTier.auto_propose_human_confirm

        return RiskTier.auto_execute


@dataclass(frozen=True)
class RetryPolicy:
    """doc 5.8: schema errors retry same stage <=2x; two consecutive
    no-new-information rounds stop the loop; every loop needs a budget."""

    max_stage_attempts: int = 2
    max_total_stage_executions: int = 40
    max_tool_calls: int = 20
    max_consecutive_no_new_info_rounds: int = 2


def has_new_information(previous_output: dict, new_output: dict) -> bool:
    """Cheap structural-equality probe for the 'no new information across
    two consecutive rounds -> stop' rule (doc 5.8). Exact-match only - a
    stage that keeps returning byte-identical output is definitionally not
    making progress."""
    return previous_output != new_output

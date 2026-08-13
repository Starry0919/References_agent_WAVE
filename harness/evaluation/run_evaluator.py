"""Compares `WorkflowRun`s for backbone-stage-sequence consistency (the
5-run reproducibility acceptance test) and produces a structured diff
between any two runs (the "export a run trace, diff two runs" acceptance
test). Pure functions over `WorkflowRun` objects - no I/O.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from harness.workflow.state import StageRecordStatus, WorkflowRun


def backbone_sequence(run: WorkflowRun) -> list[str]:
    """The ordered list of stages the run actually completed - the
    "necessary path" the doc's 5x-consistency test compares across runs."""
    return [r.stage_id for r in run.stage_records if r.status == StageRecordStatus.completed]


@dataclass
class ConsistencyReport:
    consistent: bool
    reference_sequence: list[str]
    per_run_sequences: list[list[str]] = field(default_factory=list)
    differences: list[str] = field(default_factory=list)


def check_backbone_consistency(runs: list[WorkflowRun]) -> ConsistencyReport:
    if not runs:
        return ConsistencyReport(consistent=True, reference_sequence=[])
    sequences = [backbone_sequence(r) for r in runs]
    reference = sequences[0]
    differences = [
        f"run {i} ({runs[i - 1].run_id}) backbone differs from run 1 ({runs[0].run_id}): {seq} != {reference}"
        for i, seq in enumerate(sequences[1:], start=2)
        if seq != reference
    ]
    return ConsistencyReport(
        consistent=not differences,
        reference_sequence=reference,
        per_run_sequences=sequences,
        differences=differences,
    )


def diff_runs(a: WorkflowRun, b: WorkflowRun) -> dict[str, Any]:
    seq_a, seq_b = backbone_sequence(a), backbone_sequence(b)
    decisions_a = {(d.target_entity.canonical_id, d.operation.value): d.status.value for d in a.engineering_decisions}
    decisions_b = {(d.target_entity.canonical_id, d.operation.value): d.status.value for d in b.engineering_decisions}
    return {
        "run_a": a.run_id,
        "run_b": b.run_id,
        "backbone_matches": seq_a == seq_b,
        "backbone_a": seq_a,
        "backbone_b": seq_b,
        "status_a": a.status.value,
        "status_b": b.status.value,
        "decision_keys_only_in_a": sorted(set(decisions_a) - set(decisions_b)),
        "decision_keys_only_in_b": sorted(set(decisions_b) - set(decisions_a)),
        "decision_status_differences": {
            f"{k[0]}/{k[1]}": (decisions_a[k], decisions_b[k])
            for k in decisions_a.keys() & decisions_b.keys()
            if decisions_a[k] != decisions_b[k]
        },
    }

"""`RunStore`: the persistence interface `WorkflowController` depends on,
instead of importing `harness.workflow.checkpoint` directly. Extracted so
"reuse Problem 01's controller pattern with a SQL-backed store" is literal,
not just architectural conformance - the Iterative Design Loop
(`harness/workflow/iterative_loop.py`) follows the same controller
discipline (single state-writer, `StageDefinition`-as-data, gate battery)
but needs a durability lifetime JSON-file checkpointing was never designed
for (`WAITING_FOR_RESULTS` surviving the process ending for days), so it
gets its own store implementation rather than forcing one persistence
engine to serve both.
"""
from __future__ import annotations

from typing import Protocol

from harness.workflow.state import WorkflowRun


class RunStore(Protocol):
    def save(self, run: WorkflowRun) -> None: ...
    def load(self, run_id: str) -> WorkflowRun | None: ...


class JSONCheckpointStore:
    """Default `RunStore`: today's whole-object JSON snapshot to
    `workflow_runs/{run_id}.json` (`harness/workflow/checkpoint.py`) -
    unchanged behavior from before this refactor, so every existing
    Problem 01 test still passes with zero changes."""

    def save(self, run: WorkflowRun) -> None:
        from harness.workflow import checkpoint

        checkpoint.save(run)

    def load(self, run_id: str) -> WorkflowRun | None:
        from harness.workflow import checkpoint

        return checkpoint.load(run_id)

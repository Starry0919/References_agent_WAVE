"""Tests for the timeout observability added to `harness/tools/executor.py`:
a timed-out workflow tool must log a warning and bump the module-level
leaked-thread counter, while successful calls must not. Behavior-level
timeout/retry semantics are already covered by
`tests/workflow/test_tool_executor.py`."""
from __future__ import annotations

import logging
import time

import harness.tools.executor as executor_module
from harness.tools.executor import ToolExecutor, WorkflowTool
from harness.workflow.contracts import ToolFailureClass

_EXECUTOR_LOGGER = "harness.tools.executor"


def _slow() -> str:
    """Simulates a workflow tool that hangs far past its own timeout."""
    time.sleep(2)
    return "unreachable"


def test_timeout_logs_warning_and_counts_leak(caplog) -> None:
    tools = {"slow": WorkflowTool(name="slow", func=_slow, timeout_s=0.1)}
    # max_retries=0: exactly one timed-out attempt, hence exactly one leak.
    executor = ToolExecutor(tools, max_retries=0, backoff_base_s=0.001)
    before = executor_module.leaked_thread_count()
    with caplog.at_level(logging.WARNING, logger=_EXECUTOR_LOGGER):
        result = executor.execute("slow", {}, allowlist=("slow",), stage_id="STAGE_A")
    assert result.record.is_error
    assert result.record.failure_class is ToolFailureClass.transient
    assert executor_module.leaked_thread_count() == before + 1
    messages = [
        record.getMessage()
        for record in caplog.records
        if record.name == _EXECUTOR_LOGGER and record.levelno == logging.WARNING
    ]
    assert any(
        "'slow'" in message
        and "0.1" in message  # timeout seconds are named in the log
        and "may still be running" in message
        for message in messages
    ), f"no leak warning found in {messages}"
    executor.shutdown()


def test_successful_tool_does_not_count_as_leak() -> None:
    tools = {"ok": WorkflowTool(name="ok", func=lambda: "fine", timeout_s=5)}
    executor = ToolExecutor(tools, max_retries=0, backoff_base_s=0.001)
    before = executor_module.leaked_thread_count()
    result = executor.execute("ok", {}, allowlist=("ok",), stage_id="STAGE_A")
    assert not result.record.is_error
    assert result.value == "fine"
    assert executor_module.leaked_thread_count() == before
    executor.shutdown()

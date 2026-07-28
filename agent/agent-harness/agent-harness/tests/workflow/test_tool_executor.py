"""Unit tests for `harness/tools/executor.py`: timeout, unavailable,
invalid_input, retry-to-limit-then-stop, idempotency-key caching, and
allowlist enforcement (doc 7.1/7.4: "unauthorized tool call for the
current stage is rejected")."""
from __future__ import annotations

import time

from harness.tools.executor import (
    ToolExecutor,
    ToolInvalidInputError,
    ToolTransientError,
    ToolUnavailableError,
    WorkflowTool,
)
from harness.workflow.contracts import ToolFailureClass


def _executor(**tools: WorkflowTool) -> ToolExecutor:
    return ToolExecutor(tools, max_retries=2, backoff_base_s=0.001)


def test_disallowed_tool_is_rejected_without_calling_it() -> None:
    calls = []

    def fn():
        calls.append(1)
        return "ok"

    ex = _executor(secret=WorkflowTool(name="secret", func=fn))
    result = ex.execute("secret", {}, allowlist=(), stage_id="STAGE_A")
    assert result.record.is_error
    assert result.record.failure_class == ToolFailureClass.invalid_input
    assert calls == []  # never actually invoked


def test_unregistered_tool_reports_unavailable() -> None:
    ex = _executor()
    result = ex.execute("nonexistent", {}, allowlist=("nonexistent",), stage_id="STAGE_A")
    assert result.record.is_error
    assert result.record.failure_class == ToolFailureClass.unavailable


def test_timeout_is_classified_transient_and_retried_then_gives_up() -> None:
    attempts = []

    def slow():
        attempts.append(time.time())
        time.sleep(0.2)
        return "too slow"

    ex = _executor(slow=WorkflowTool(name="slow", func=slow, timeout_s=0.01))
    result = ex.execute("slow", {}, allowlist=("slow",), stage_id="STAGE_A")
    assert result.record.is_error
    assert result.record.failure_class == ToolFailureClass.transient
    assert result.record.attempt == 3  # 1 initial + 2 retries, then stop


def test_invalid_input_error_is_not_retried() -> None:
    attempts = []

    def bad(x: int):
        attempts.append(x)
        raise ToolInvalidInputError("bad input")

    ex = _executor(bad=WorkflowTool(name="bad", func=bad))
    result = ex.execute("bad", {"x": 1}, allowlist=("bad",), stage_id="STAGE_A")
    assert result.record.failure_class == ToolFailureClass.invalid_input
    assert result.record.attempt == 1  # no retry for a non-transient class
    assert attempts == [1]


def test_unavailable_error_is_not_retried() -> None:
    def unavailable():
        raise ToolUnavailableError("no model registered")

    ex = _executor(u=WorkflowTool(name="u", func=unavailable))
    result = ex.execute("u", {}, allowlist=("u",), stage_id="STAGE_A")
    assert result.record.failure_class == ToolFailureClass.unavailable
    assert result.record.attempt == 1


def test_transient_error_retries_then_succeeds() -> None:
    state = {"count": 0}

    def flaky():
        state["count"] += 1
        if state["count"] < 2:
            raise ToolTransientError("temporary blip")
        return "recovered"

    ex = _executor(flaky=WorkflowTool(name="flaky", func=flaky))
    result = ex.execute("flaky", {}, allowlist=("flaky",), stage_id="STAGE_A")
    assert not result.record.is_error
    assert result.value == "recovered"
    assert result.record.attempt == 2


def test_idempotency_key_returns_cached_result_without_recalling() -> None:
    calls = []

    def fn():
        calls.append(1)
        return "computed once"

    ex = _executor(fn=WorkflowTool(name="fn", func=fn))
    first = ex.execute("fn", {}, allowlist=("fn",), stage_id="STAGE_A", idempotency_key="k1")
    second = ex.execute("fn", {}, allowlist=("fn",), stage_id="STAGE_A", idempotency_key="k1")
    assert len(calls) == 1  # fn only actually ran once
    assert not first.record.cached
    assert second.record.cached
    assert second.value == "computed once"

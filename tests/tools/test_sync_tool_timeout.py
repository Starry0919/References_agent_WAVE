"""Regression tests for the sync-tool zombie-thread fix in
`harness/tools/base.py`: a timed-out sync tool must still return an ERROR
outcome on time, the orphaned worker thread must be logged and counted, the
work must run on the dedicated `harness-tool-*` pool (never the asyncio
default executor), and healthy tools must stay unaffected."""
from __future__ import annotations

import asyncio
import logging
import threading
import time

import pytest

from harness.tools.base import (
    execute_tool,
    leaked_thread_count,
    shutdown_tool_pool,
    tool,
)

_BASE_LOGGER = "harness.tools.base"


@tool(name="slow_sync_tool_for_test", timeout=0.1)
def _slow_sync() -> str:
    """Simulates a sync tool that hangs far past its own timeout."""
    time.sleep(2)
    return "unreachable"


@tool(name="thread_name_probe_for_test", timeout=5)
def _thread_name_probe() -> str:
    """Reports the name of the worker thread it runs on."""
    return threading.current_thread().name


@tool(name="fast_sync_tool_for_test", timeout=5)
def _fast_sync(x: int) -> int:
    """A healthy sync tool that returns immediately."""
    return x * 2


@tool(name="fast_async_tool_for_test", timeout=5)
async def _fast_async() -> str:
    """A healthy async tool (no worker thread involved)."""
    return "async ok"


@pytest.mark.asyncio
async def test_slow_sync_tool_times_out_on_time_with_error_result() -> None:
    start = time.perf_counter()
    outcome = await execute_tool("slow_sync_tool_for_test", {})
    elapsed = time.perf_counter() - start
    assert outcome.is_error
    assert "TimeoutError" in outcome.result
    assert "slow_sync_tool_for_test" in outcome.result
    # Returned right after the 0.1s timeout, not after the 2s sleep.
    assert elapsed < 1.5


@pytest.mark.asyncio
async def test_timeout_logs_warning_and_counts_leaked_thread(caplog) -> None:
    before = leaked_thread_count()
    with caplog.at_level(logging.WARNING, logger=_BASE_LOGGER):
        outcome = await execute_tool("slow_sync_tool_for_test", {})
    assert outcome.is_error
    assert leaked_thread_count() == before + 1
    messages = [
        record.getMessage()
        for record in caplog.records
        if record.name == _BASE_LOGGER and record.levelno == logging.WARNING
    ]
    assert any(
        "slow_sync_tool_for_test" in message
        and "0.1" in message  # timeout seconds are named in the log
        and "may still be running" in message
        for message in messages
    ), f"no leak warning found in {messages}"


@pytest.mark.asyncio
async def test_sync_tool_runs_on_dedicated_harness_pool() -> None:
    outcome = await execute_tool("thread_name_probe_for_test", {})
    assert not outcome.is_error
    # ThreadPoolExecutor appends "_N" to the prefix: "harness-tool_0", ...
    assert outcome.result.startswith("harness-tool")


@pytest.mark.asyncio
async def test_fast_tools_are_unaffected_after_a_timeout() -> None:
    await execute_tool("slow_sync_tool_for_test", {})  # orphans one worker
    sync_outcome = await execute_tool("fast_sync_tool_for_test", {"x": 21})
    assert not sync_outcome.is_error
    assert sync_outcome.result == "42"
    async_outcome = await execute_tool("fast_async_tool_for_test", {})
    assert not async_outcome.is_error
    assert async_outcome.result == "async ok"


@pytest.mark.asyncio
async def test_cancelled_sync_tool_counts_a_leak() -> None:
    before = leaked_thread_count()
    task = asyncio.ensure_future(execute_tool("slow_sync_tool_for_test", {}))
    await asyncio.sleep(0.05)  # let the worker start before cancelling
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
    assert leaked_thread_count() == before + 1


@pytest.mark.asyncio
async def test_pool_recreates_after_shutdown() -> None:
    """`shutdown_tool_pool()` (server lifespan) must not brick the process:
    test suites host several app lifecycles in one interpreter, so the pool
    is lazily recreated instead of dying with "cannot schedule new futures".
    """
    shutdown_tool_pool()
    outcome = await execute_tool("fast_sync_tool_for_test", {"x": 2})
    assert not outcome.is_error
    assert outcome.result == "4"

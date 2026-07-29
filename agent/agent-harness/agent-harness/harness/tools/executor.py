"""Unified tool execution layer for the Workflow Engine (doc 5.6): schema-
level allowlisting, timeout, bounded retry with backoff, idempotency-key
result caching, and `ToolRecord` provenance for every call.

Deliberately NOT used by `harness/agent.py`'s free chat loop
(design-review fix #2): that loop's `execute_tool()` contract
(`harness/tools/base.py`) is the documented, tested behavior for the
general-purpose chat agent (see `docs/SPEC.md` §3.1/§7), and it has no
per-stage allowlist concept to begin with. This executor is a separate,
additive layer purely for tools the workflow *controller* calls on its own
behalf (today: one stub FBA tool registered in
`harness/workflow/synbio_stages.py`) - not a retrofit of the chat tool
registry.
"""
from __future__ import annotations

import logging
import time
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import TimeoutError as FutureTimeoutError
from dataclasses import dataclass
from typing import Any, Callable

from harness.workflow.contracts import ToolFailureClass, ToolRecord, new_id

logger = logging.getLogger(__name__)

# Worker threads orphaned so far by timed-out tool calls: `future.result(timeout=)`
# only stops *waiting* - Python cannot kill threads - so each timeout leaves its
# worker running until the tool function returns on its own. Module-level (not
# per-instance) so the count survives per-run ToolExecutor instances; the
# executor is synchronous and called from one thread at a time, so a plain int
# suffices. See `harness/tools/base.py` for the async-side counterpart.
_LEAKED_THREADS = 0


def leaked_thread_count() -> int:
    """Return how many workflow-tool worker threads have been leaked by timeouts so far."""
    return _LEAKED_THREADS


class ToolTransientError(RuntimeError):
    """Retry-eligible failure (network blip, rate limit, etc.)."""


class ToolInvalidInputError(ValueError):
    """Caller passed arguments outside the tool's accepted shape."""


class ToolUnavailableError(RuntimeError):
    """Tool is not wired up / not reachable this round (e.g. no FBA model registered)."""


class ToolOutOfDomainError(RuntimeError):
    """Tool exists but the requested input is outside its applicability domain."""


class ToolFatalError(RuntimeError):
    """Unretryable, unexpected failure."""


def _classify(exc: Exception) -> ToolFailureClass:
    # isinstance, not exact-type, so a tool's own subclasses classify correctly.
    if isinstance(exc, ToolTransientError):
        return ToolFailureClass.transient
    if isinstance(exc, ToolInvalidInputError):
        return ToolFailureClass.invalid_input
    if isinstance(exc, ToolUnavailableError):
        return ToolFailureClass.unavailable
    if isinstance(exc, ToolOutOfDomainError):
        return ToolFailureClass.out_of_domain
    return ToolFailureClass.fatal


@dataclass(frozen=True)
class WorkflowTool:
    """One tool the workflow controller may call on its own behalf -
    distinct from harness/tools/base.py's chat-agent tool registry."""

    name: str
    func: Callable[..., Any]
    timeout_s: float = 30.0
    domain: str = ""  # human-readable applicability note, for documentation/logging


@dataclass
class ToolExecutionResult:
    record: ToolRecord
    value: Any = None


class ToolExecutor:
    """Synchronous by design: `WorkflowController.advance()` is sync (every
    stage implementation today is deterministic, no network I/O of its
    own), so this avoids forcing an event loop into the controller/tests."""

    def __init__(self, tools: dict[str, WorkflowTool], *, max_retries: int = 2, backoff_base_s: float = 0.2) -> None:
        self._tools = tools
        self._max_retries = max_retries
        self._backoff_base_s = backoff_base_s
        self._cache: dict[str, ToolExecutionResult] = {}
        self._pool = ThreadPoolExecutor(max_workers=4, thread_name_prefix="workflow-tool")

    def execute(
        self,
        name: str,
        arguments: dict[str, Any],
        *,
        allowlist: tuple[str, ...],
        stage_id: str,
        idempotency_key: str | None = None,
    ) -> ToolExecutionResult:
        if idempotency_key and idempotency_key in self._cache:
            cached = self._cache[idempotency_key]
            record = cached.record.model_copy(update={"cached": True, "tool_call_id": new_id("TOOL")})
            return ToolExecutionResult(record=record, value=cached.value)

        if name not in allowlist:
            record = ToolRecord(
                stage_id=stage_id,
                name=name,
                arguments=arguments,
                idempotency_key=idempotency_key,
                started_at=time.time(),
                ended_at=time.time(),
                is_error=True,
                failure_class=ToolFailureClass.invalid_input,
                result_summary=f"tool '{name}' is not in stage '{stage_id}''s allowlist {allowlist}",
            )
            return ToolExecutionResult(record=record)

        tool = self._tools.get(name)
        if tool is None:
            record = ToolRecord(
                stage_id=stage_id,
                name=name,
                arguments=arguments,
                idempotency_key=idempotency_key,
                started_at=time.time(),
                ended_at=time.time(),
                is_error=True,
                failure_class=ToolFailureClass.unavailable,
                result_summary=f"tool '{name}' is not registered with this executor",
            )
            return ToolExecutionResult(record=record)

        attempt = 0
        while True:
            attempt += 1
            started = time.time()
            try:
                future = self._pool.submit(tool.func, **arguments)
                value = future.result(timeout=tool.timeout_s)
                record = ToolRecord(
                    stage_id=stage_id,
                    name=name,
                    arguments=arguments,
                    idempotency_key=idempotency_key,
                    attempt=attempt,
                    started_at=started,
                    ended_at=time.time(),
                    is_error=False,
                    result_summary=str(value)[:500],
                )
                result = ToolExecutionResult(record=record, value=value)
                if idempotency_key:
                    self._cache[idempotency_key] = result
                return result
            except FutureTimeoutError:
                global _LEAKED_THREADS
                _LEAKED_THREADS += 1
                logger.warning(
                    "tool %r timed out after %ss; its worker thread may still "
                    "be running (leaked workflow-tool threads so far: %d)",
                    name,
                    tool.timeout_s,
                    _LEAKED_THREADS,
                )
                failure_class = ToolFailureClass.transient
                message = f"tool '{name}' timed out after {tool.timeout_s}s"
            except Exception as exc:  # noqa: BLE001 - classified below, never crashes the controller
                failure_class = _classify(exc)
                message = str(exc)

            record = ToolRecord(
                stage_id=stage_id,
                name=name,
                arguments=arguments,
                idempotency_key=idempotency_key,
                attempt=attempt,
                started_at=started,
                ended_at=time.time(),
                is_error=True,
                failure_class=failure_class,
                result_summary=message,
            )
            if failure_class != ToolFailureClass.transient or attempt > self._max_retries:
                return ToolExecutionResult(record=record)
            time.sleep(self._backoff_base_s * (2 ** (attempt - 1)))

    def shutdown(self) -> None:
        self._pool.shutdown(wait=False, cancel_futures=True)

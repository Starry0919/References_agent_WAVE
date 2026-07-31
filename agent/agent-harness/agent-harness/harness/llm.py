"""LLM client: streaming OpenAI-compatible chat for the configured provider.

Which vendor/model/key to use is resolved by harness.providers — this module
only speaks the protocol and never hardcodes a vendor.
"""
from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from typing import Awaitable, Callable, Union

from harness.config import get_settings
from harness.providers import ProviderError, resolve

logger = logging.getLogger(__name__)

try:  # tolerated at import so the failure surfaces as a readable LLMError
    import openai as _openai
except ImportError:  # pragma: no cover
    _openai = None

try:  # transport errors surface raw from failures during stream iteration
    import httpx as _httpx
except ImportError:  # pragma: no cover
    _httpx = None

DeltaCallback = Union[Callable[[str], Awaitable[None]], None]


class _CallbackError(Exception):
    """Internal: a delta callback raised — not an LLM failure, never retried."""


@dataclass
class ToolCallReq:
    """One tool call requested by the model; arguments are a raw JSON string."""

    id: str
    name: str
    arguments_json: str


@dataclass
class AssistantTurn:
    """The accumulated result of one streamed assistant completion."""

    content: str
    thinking: str
    tool_calls: list[ToolCallReq] = field(default_factory=list)
    finish_reason: str | None = None
    usage: dict | None = None


class LLMError(Exception):
    """A readable, user-presentable LLM failure."""


class LLMClient:
    """Streaming chat client for any OpenAI-compatible provider."""

    def __init__(self) -> None:
        settings = get_settings()
        if _openai is None:
            raise LLMError(
                "the 'openai' package is not installed; "
                "run: pip install -r requirements.txt"
            )
        try:
            self._provider = resolve()
        except ProviderError as exc:
            raise LLMError(str(exc)) from exc
        self._client = _openai.AsyncOpenAI(
            api_key=self._provider.api_key,
            base_url=self._provider.base_url,
            timeout=settings.LLM_TIMEOUT_S,
        )

    async def chat(
        self,
        messages: list[dict],
        tools: list[dict],
        on_delta: DeltaCallback = None,
        on_thinking_delta: DeltaCallback = None,
    ) -> AssistantTurn:
        """Run one streamed completion with retries; returns the full turn."""
        settings = get_settings()
        attempts = max(1, settings.LLM_RETRIES)
        streamed = False  # did any delta reach the callbacks this attempt?

        def mark_streamed() -> None:
            nonlocal streamed
            streamed = True

        last_exc: Exception | None = None
        for attempt in range(attempts):
            streamed = False
            try:
                return await self._chat_once(
                    messages, tools, on_delta, on_thinking_delta, mark_streamed
                )
            except _CallbackError as exc:
                # The failure came from a delta callback (event persistence /
                # fan-out), not from the LLM. Retrying would re-stream and
                # duplicate the already-emitted output — fail immediately.
                cause = exc.__cause__ or exc
                raise LLMError(f"delta callback failed: {cause}") from cause
            except Exception as exc:
                status = getattr(exc, "status_code", None)
                if not self._is_retryable(exc, status):
                    raise LLMError(f"LLM request failed: {exc}") from exc
                if streamed:
                    # Partial output already reached the callbacks (persisted
                    # events, live UI): a retry would replay and duplicate it.
                    raise LLMError(
                        f"LLM stream failed after output started: {exc}"
                    ) from exc
                last_exc = exc
                if attempt < attempts - 1:
                    delay = 2**attempt  # 1s, 2s, 4s, ...
                    logger.warning(
                        "LLM call failed (attempt %d/%d), retrying in %ds: %s",
                        attempt + 1,
                        attempts,
                        delay,
                        exc,
                    )
                    await asyncio.sleep(delay)
        raise LLMError(f"LLM request failed after {attempts} attempts: {last_exc}") from last_exc

    @staticmethod
    def _is_retryable(exc: Exception, status: int | None) -> bool:
        """Retry on connection errors, 429, and 5xx; fail fast on other 4xx."""
        if status == 429:
            return True
        if status is not None and 500 <= int(status) < 600:
            return True
        if status is not None:
            return False
        if _openai is not None and isinstance(exc, _openai.APIConnectionError):
            return True
        if _httpx is not None and isinstance(exc, _httpx.TransportError):
            # Raw transport failures (network drop, read timeout, protocol
            # error) escape the SDK unlabelled during stream iteration.
            return True
        if isinstance(exc, (ConnectionError, TimeoutError, OSError)):
            return True
        return False

    async def _chat_once(
        self,
        messages: list[dict],
        tools: list[dict],
        on_delta: DeltaCallback,
        on_thinking_delta: DeltaCallback,
        mark_streamed: Callable[[], None],
    ) -> AssistantTurn:
        settings = get_settings()
        kwargs: dict = {
            "model": self._provider.model,
            "messages": messages,
            "stream": True,
        }
        if tools:
            kwargs["tools"] = tools
        if settings.LLM_MAX_TOKENS is not None:
            kwargs["max_tokens"] = settings.LLM_MAX_TOKENS
        if settings.TEMPERATURE is not None:
            kwargs["temperature"] = settings.TEMPERATURE
        if settings.REASONING_EFFORT and self._provider.name == "poe":
            # Poe's kimi-k3 (like the direct Kimi K3 endpoint before it) is a
            # reasoning model that can burn a whole small max_tokens budget
            # on reasoning_content before any visible text is emitted -
            # reasoning_effort (low/medium/high) trades reasoning depth for
            # a better chance of finishing within budget/timeout.
            kwargs["reasoning_effort"] = settings.REASONING_EFFORT

        stream = await self._client.chat.completions.create(**kwargs)

        content_parts: list[str] = []
        thinking_parts: list[str] = []
        calls_by_index: dict[int, dict] = {}
        finish_reason: str | None = None
        usage: dict | None = None

        async for chunk in stream:
            chunk_usage = getattr(chunk, "usage", None)
            if chunk_usage is not None:
                if hasattr(chunk_usage, "model_dump"):
                    usage = chunk_usage.model_dump()
                elif isinstance(chunk_usage, dict):
                    usage = chunk_usage
            if not getattr(chunk, "choices", None):
                continue
            choice = chunk.choices[0]
            if choice.finish_reason:
                finish_reason = choice.finish_reason
            delta = choice.delta
            if delta is None:
                continue

            text = getattr(delta, "content", None)
            if text:
                content_parts.append(text)
                if on_delta is not None:
                    mark_streamed()
                    try:
                        await on_delta(text)
                    except Exception as exc:
                        raise _CallbackError(str(exc)) from exc

            thinking_text = getattr(delta, "reasoning_content", None)
            if thinking_text:
                thinking_parts.append(thinking_text)
                if on_thinking_delta is not None:
                    mark_streamed()
                    try:
                        await on_thinking_delta(thinking_text)
                    except Exception as exc:
                        raise _CallbackError(str(exc)) from exc

            for tc in getattr(delta, "tool_calls", None) or []:
                index = tc.index if tc.index is not None else 0
                entry = calls_by_index.setdefault(
                    index, {"id": "", "name": "", "arguments": ""}
                )
                if tc.id and not entry["id"]:
                    entry["id"] = tc.id
                function = getattr(tc, "function", None)
                if function is not None:
                    if function.name and not entry["name"]:
                        entry["name"] = function.name
                    if function.arguments:
                        entry["arguments"] += function.arguments

        tool_calls = [
            ToolCallReq(id=entry["id"], name=entry["name"], arguments_json=entry["arguments"])
            for _, entry in sorted(calls_by_index.items())
        ]
        return AssistantTurn(
            content="".join(content_parts),
            thinking="".join(thinking_parts),
            tool_calls=tool_calls,
            finish_reason=finish_reason,
            usage=usage,
        )


_cached_client: LLMClient | None = None


def get_llm_client() -> LLMClient:
    """Return the process-wide client for the configured provider.

    Cached so one AsyncOpenAI/httpx connection pool is reused across agent
    turns instead of leaking a fresh, never-closed pool per turn. Changing
    provider settings in .env requires a restart.
    """
    global _cached_client
    if _cached_client is None:
        _cached_client = LLMClient()
    return _cached_client


async def aclose_cached_client() -> None:
    """关闭进程级缓存客户端并重置缓存(服务器关停时调用一次)。

    底层 AsyncOpenAI/httpx 连接池常驻进程,从不关闭会在退出时留下
    "unclosed client" 告警。先摘缓存再关闭:并发中的 get_llm_client()
    只会惰性重建一个新客户端,不会出现"用到半关的客户端"。从未创建过
    客户端或重复调用都是安全的。
    """
    global _cached_client
    client = _cached_client
    _cached_client = None
    if client is not None:
        await client._client.close()

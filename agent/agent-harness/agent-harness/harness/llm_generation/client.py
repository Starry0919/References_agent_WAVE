"""Structured-JSON generation client (prompt §5.2): a thin, synchronous,
provenance-recording wrapper around whatever OpenAI-compatible provider
`harness.providers`/`.env` currently resolves to. Deliberately NOT built on
`harness.llm.LLMClient` - that client is async, streaming, and tool-call
oriented (the general chat agent's loop); structured candidate generation
needs one plain non-streaming JSON completion per call, so this module
talks to the SDK directly, the same way the environment-audit health check
for this phase did.

Environment finding recorded here rather than hidden (confirmed during
Phase C's audit and while wiring these adapters): the currently configured
provider/model (`kimi-for-coding-highspeed`) is a REASONING model whose
`reasoning_tokens` usage for this kind of multi-field JSON-schema prompt
can consume most or all of a modest `max_tokens` budget before any visible
content is emitted - at `max_tokens=1500` real calls repeatedly returned
`reasoning_tokens=1499`/`completion_tokens=1500` with EMPTY visible
content (a genuine `validation_status="empty"`, not a bug in this client).
`max_tokens=8000` was empirically the smallest budget that reliably left
enough room for real JSON output on the hypothesis/strategy/critic prompts
in this package - real calls at that budget take 15-30s of latency. Adapters
needing a smaller/larger budget should pass an explicit `max_tokens`.

Contract (prompt §5.2/§5.9):
- structured output via `response_format={"type": "json_object"}`;
- schema-invalid output may be retried (re-prompted with the parse error),
  up to `max_schema_retries`, then must stop - never loop indefinitely;
- every attempt (success or failure) is recorded in one
  `LLMGenerationRecord` row before the caller sees a result;
- a raw provider/network failure is NOT retried here beyond the SDK's own
  transient-error handling for one call - the caller (task-specific
  adapter) decides whether to fall back to its deterministic generator;
- this client never fabricates a result on failure - `generate()` returns
  `parsed=None` and an honest `validation_status`.
"""
from __future__ import annotations

import json
import time
from dataclasses import dataclass
from typing import Any

from harness.config import get_settings
from harness.providers import ProviderError, resolve

try:
    import openai as _openai
except ImportError:  # pragma: no cover - already a hard repo dependency
    _openai = None


@dataclass
class AdapterHealth:
    available: bool
    provider: str
    model: str
    reason: str = ""
    latency: float | None = None


@dataclass
class GenerationAttempt:
    raw_content: str | None
    parsed: dict[str, Any] | None
    validation_status: str  # harness.llm_generation.models.VALIDATION_STATUSES
    error: str | None
    usage: dict[str, Any] | None
    latency: float


class StructuredGenerationClient:
    """One instance per process is fine (matches `harness.llm.LLMClient`'s
    own per-call-site instantiation convention) - construction is cheap and
    always re-resolves the current provider config, so `.env` changes take
    effect on the next call without a restart-sensitive singleton."""

    def health_check(self) -> AdapterHealth:
        if _openai is None:
            return AdapterHealth(available=False, provider="unknown", model="unknown", reason="the 'openai' package is not installed")
        try:
            provider = resolve()
        except ProviderError as exc:
            return AdapterHealth(available=False, provider="unknown", model="unknown", reason=str(exc))
        t0 = time.monotonic()
        try:
            client = _openai.OpenAI(api_key=provider.api_key, base_url=provider.base_url, timeout=15)
            client.chat.completions.create(
                model=provider.model, messages=[{"role": "user", "content": "Reply with exactly: OK"}], max_tokens=5,
            )
        except Exception as exc:  # noqa: BLE001 - any provider/network failure means "unavailable", not a crash
            return AdapterHealth(available=False, provider=provider.name, model=provider.model, reason=f"{type(exc).__name__}: {exc}", latency=time.monotonic() - t0)
        return AdapterHealth(available=True, provider=provider.name, model=provider.model, latency=time.monotonic() - t0)

    def _one_call(self, *, provider, system_prompt: str, user_prompt: str, max_tokens: int, temperature: float | None) -> GenerationAttempt:
        t0 = time.monotonic()
        try:
            client = _openai.OpenAI(api_key=provider.api_key, base_url=provider.base_url, timeout=get_settings().LLM_TIMEOUT_S)
            kwargs: dict[str, Any] = {
                "model": provider.model,
                "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
                "max_tokens": max_tokens,
                "response_format": {"type": "json_object"},
            }
            if temperature is not None:
                kwargs["temperature"] = temperature
            settings = get_settings()
            if settings.REASONING_EFFORT and provider.name == "kimi":
                kwargs["reasoning_effort"] = settings.REASONING_EFFORT
            resp = client.chat.completions.create(**kwargs)
        except Exception as exc:  # noqa: BLE001
            return GenerationAttempt(raw_content=None, parsed=None, validation_status="provider_error", error=f"{type(exc).__name__}: {exc}", usage=None, latency=time.monotonic() - t0)
        latency = time.monotonic() - t0
        content = resp.choices[0].message.content
        usage = resp.usage.model_dump() if resp.usage is not None else None
        if not content or not content.strip():
            return GenerationAttempt(raw_content=content, parsed=None, validation_status="empty", error="provider returned empty content", usage=usage, latency=latency)
        try:
            parsed = json.loads(content)
        except json.JSONDecodeError as exc:
            return GenerationAttempt(raw_content=content, parsed=None, validation_status="schema_invalid", error=f"not valid JSON: {exc}", usage=usage, latency=latency)
        return GenerationAttempt(raw_content=content, parsed=parsed, validation_status="valid", error=None, usage=usage, latency=latency)

    def generate(
        self, *, system_prompt: str, user_prompt: str, max_tokens: int = 8000, temperature: float | None = None,
        max_schema_retries: int = 2,
    ) -> tuple[list[GenerationAttempt], AdapterHealth]:
        """Returns every attempt made (for provenance) plus a health
        snapshot. The LAST attempt in the list is the one the caller should
        act on. Schema-invalid/empty responses are re-prompted (with the
        parse error appended) up to `max_schema_retries` times; a
        `provider_error` on the FIRST attempt is not retried here at all -
        that is a connectivity/availability problem the caller should treat
        as "fall back now", not a schema problem worth re-prompting."""
        if _openai is None:
            health = AdapterHealth(available=False, provider="unknown", model="unknown", reason="the 'openai' package is not installed")
            return [GenerationAttempt(None, None, "provider_error", health.reason, None, 0.0)], health
        try:
            provider = resolve()
        except ProviderError as exc:
            health = AdapterHealth(available=False, provider="unknown", model="unknown", reason=str(exc))
            return [GenerationAttempt(None, None, "provider_error", str(exc), None, 0.0)], health

        attempts: list[GenerationAttempt] = []
        current_user_prompt = user_prompt
        for i in range(max_schema_retries + 1):
            attempt = self._one_call(provider=provider, system_prompt=system_prompt, user_prompt=current_user_prompt, max_tokens=max_tokens, temperature=temperature)
            attempts.append(attempt)
            if attempt.validation_status == "valid":
                break
            if attempt.validation_status == "provider_error" and i == 0:
                break  # connectivity problem, not worth re-prompting
            if i < max_schema_retries:
                current_user_prompt = (
                    f"{user_prompt}\n\nYour previous response was invalid ({attempt.error}). "
                    "Reply again with ONLY a single valid JSON object matching the requested schema - no prose, no markdown fences."
                )
        health = AdapterHealth(available=(attempts[-1].validation_status != "provider_error" or len(attempts) > 1), provider=provider.name, model=provider.model)
        return attempts, health

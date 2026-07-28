"""A fake `StructuredGenerationClient` double for offline, deterministic
tests of the schema-validation/retry/fallback contract - no network calls.
Matches `harness.llm_generation.client.StructuredGenerationClient`'s public
shape by duck typing (every adapter accepts an injectable `client`)."""
from __future__ import annotations

from harness.llm_generation.client import AdapterHealth, GenerationAttempt


class FakeStructuredGenerationClient:
    def __init__(self, *, scripted_contents: list[str | None], provider: str = "fake", model: str = "fake-model-v1", available: bool = True, unavailable_reason: str = ""):
        """`scripted_contents`: one entry per call to `generate()`; `None`
        means "simulate a provider_error" (unavailable), otherwise the raw
        string content the fake provider "returned" that call."""
        self._scripted = list(scripted_contents)
        self._provider = provider
        self._model = model
        self._available = available
        self._unavailable_reason = unavailable_reason
        self.call_count = 0

    def health_check(self) -> AdapterHealth:
        return AdapterHealth(available=self._available, provider=self._provider, model=self._model, reason=self._unavailable_reason)

    def generate(self, *, system_prompt: str, user_prompt: str, max_tokens: int = 1200, temperature: float | None = None, max_schema_retries: int = 2):
        import json

        if not self._available:
            attempt = GenerationAttempt(raw_content=None, parsed=None, validation_status="provider_error", error=self._unavailable_reason, usage=None, latency=0.01)
            return [attempt], AdapterHealth(available=False, provider=self._provider, model=self._model, reason=self._unavailable_reason)

        attempts = []
        for i in range(max_schema_retries + 1):
            self.call_count += 1
            content = self._scripted[min(self.call_count - 1, len(self._scripted) - 1)]
            if content is None:
                attempts.append(GenerationAttempt(raw_content=None, parsed=None, validation_status="empty", error="simulated empty response", usage={"total_tokens": 10}, latency=0.05))
            else:
                try:
                    parsed = json.loads(content)
                    attempts.append(GenerationAttempt(raw_content=content, parsed=parsed, validation_status="valid", error=None, usage={"total_tokens": 50}, latency=0.05))
                    break
                except Exception as exc:  # noqa: BLE001
                    attempts.append(GenerationAttempt(raw_content=content, parsed=None, validation_status="schema_invalid", error=str(exc), usage={"total_tokens": 20}, latency=0.05))
            if self.call_count >= len(self._scripted):
                break
        return attempts, AdapterHealth(available=True, provider=self._provider, model=self._model)

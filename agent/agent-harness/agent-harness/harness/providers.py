"""LLM provider registry: switch vendors by editing .env, not code.

Every preset speaks the OpenAI-compatible chat-completions protocol, which
covers most vendors (DeepSeek, Moonshot, Qwen, Zhipu, OpenAI, Poe, ...).

Switching vendors in .env:
    LLM_PROVIDER=moonshot        # pick a preset from PROVIDERS below
    MOONSHOT_API_KEY=sk-...      # the preset's key env var
    LLM_MODEL=kimi-...           # required unless the preset has a default

Custom / self-hosted endpoints (vLLM, Ollama, API gateways):
    LLM_PROVIDER=custom
    LLM_BASE_URL=http://127.0.0.1:11434/v1
    LLM_API_KEY=placeholder      # whatever the endpoint expects
    LLM_MODEL=...

Adding a vendor permanently = one Provider line in PROVIDERS.
"""
from __future__ import annotations

import os
from dataclasses import dataclass

from harness.config import get_settings


class ProviderError(Exception):
    """A readable provider-configuration failure."""


@dataclass(frozen=True)
class Provider:
    """One OpenAI-compatible vendor preset."""

    name: str
    base_url: str
    key_env: str  # env var holding this vendor's API key
    default_model: str = ""  # empty = LLM_MODEL must be set explicitly


PROVIDERS: dict[str, Provider] = {
    "deepseek": Provider(
        "deepseek", "https://api.deepseek.com", "DEEPSEEK_API_KEY", "deepseek-v4-pro"
    ),
    "openai": Provider("openai", "https://api.openai.com/v1", "OPENAI_API_KEY"),
    "moonshot": Provider("moonshot", "https://api.moonshot.cn/v1", "MOONSHOT_API_KEY"),
    "qwen": Provider(
        "qwen", "https://dashscope.aliyuncs.com/compatible-mode/v1", "DASHSCOPE_API_KEY"
    ),
    "zhipu": Provider("zhipu", "https://open.bigmodel.cn/api/paas/v4", "ZHIPU_API_KEY"),
    # Poe's OpenAI-compatible gateway (https://creator.poe.com/docs) hosts
    # many vendors' models (Kimi K3, Claude, GPT, Grok, ...) behind one
    # credential, selected by LLM_MODEL. Defaults to "kimi-k3" - the model
    # id Poe's own /v1/models lists for Kimi K3 (confirmed non-streaming,
    # streaming, and tool-calling all work against this id) - since that is
    # what every direct-Kimi-K3 credential in this repo is being replaced
    # with; override LLM_MODEL to route elsewhere through the same key.
    "poe": Provider("poe", "https://api.poe.com/v1", "POE_API_KEY", "kimi-k3"),
    "custom": Provider("custom", "", "LLM_API_KEY"),
}


@dataclass(frozen=True)
class ResolvedProvider:
    """Fully resolved connection info for the active provider."""

    name: str
    base_url: str
    api_key: str
    model: str


def describe() -> dict:
    """Lenient view for banners/health: never raises, never includes the key."""
    settings = get_settings()
    name = settings.LLM_PROVIDER.strip().lower() or "deepseek"
    preset = PROVIDERS.get(name)
    base_url = settings.LLM_BASE_URL or (preset.base_url if preset else "")
    model = settings.LLM_MODEL or (preset.default_model if preset else "")
    return {"provider": name, "model": model, "base_url": base_url}


def resolve() -> ResolvedProvider:
    """Resolve the active provider strictly.

    Raises ProviderError with a precise fix instruction when the
    configuration is incomplete.
    """
    settings = get_settings()
    name = settings.LLM_PROVIDER.strip().lower() or "deepseek"
    preset = PROVIDERS.get(name)
    if preset is None:
        known = ", ".join(sorted(PROVIDERS))
        raise ProviderError(
            f"unknown LLM_PROVIDER '{name}' (known: {known}); or use "
            "LLM_PROVIDER=custom with LLM_BASE_URL/LLM_API_KEY/LLM_MODEL"
        )
    base_url = settings.LLM_BASE_URL or preset.base_url
    if not base_url:
        raise ProviderError(f"provider '{name}' needs LLM_BASE_URL set in .env")
    api_key = settings.LLM_API_KEY or os.environ.get(preset.key_env, "")
    if not api_key:
        raise ProviderError(
            f"missing API key for provider '{name}': set {preset.key_env} "
            "(or LLM_API_KEY) in .env"
        )
    model = settings.LLM_MODEL or preset.default_model
    if not model:
        raise ProviderError(
            f"provider '{name}' has no default model: set LLM_MODEL in .env"
        )
    return ResolvedProvider(name=name, base_url=base_url, api_key=api_key, model=model)

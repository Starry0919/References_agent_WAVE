"""Configuration: .env loading and the cached Settings singleton."""
from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv

# Project root at runtime (this file lives at <root>/harness/config.py).
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Load .env once at import time; real environment variables always win.
load_dotenv(PROJECT_ROOT / ".env", override=False)

DEFAULT_SYSTEM_PROMPT = (
    "You are a capable general-purpose agent running in a local harness. "
    "You may call the provided tools when they help, and you may call them "
    "repeatedly, reasoning over their results before deciding your next step. "
    "Keep your answers grounded in the tool results you actually received. "
    "Respond in the same language the user uses. When responding in a "
    "non-English language, keep standard technical terms (e.g. gene names "
    "like trpE, technique names like knockout or overexpression, and "
    "abbreviations like DDR or EcoCyc) in English."
)

def _env_str(name: str, default: str) -> str:
    value = os.environ.get(name)
    return value if value is not None else default


def _load_system_prompt(value: str) -> str:
    """SYSTEM_PROMPT normally holds the prompt text itself. A value starting
    with "@" is instead a path (relative to PROJECT_ROOT unless absolute)
    to a file whose contents are the prompt - lets the prompt be edited
    without touching .env or restarting quoting/escaping gymnastics."""
    if not value.startswith("@"):
        return value
    path = Path(value[1:])
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    return path.read_text(encoding="utf-8").strip()


def _env_int(name: str, default: int) -> int:
    raw = os.environ.get(name)
    if raw is None or raw.strip() == "":
        return default
    try:
        return int(raw)
    except ValueError:
        return default


def _env_float(name: str, default: float) -> float:
    raw = os.environ.get(name)
    if raw is None or raw.strip() == "":
        return default
    try:
        return float(raw)
    except ValueError:
        return default


def _env_opt_int(name: str) -> int | None:
    raw = os.environ.get(name)
    if raw is None or raw.strip() == "":
        return None
    try:
        return int(raw)
    except ValueError:
        return None


def _env_opt_float(name: str) -> float | None:
    raw = os.environ.get(name)
    if raw is None or raw.strip() == "":
        return None
    try:
        return float(raw)
    except ValueError:
        return None


@dataclass(frozen=True)
class Settings:
    """Runtime settings; every field maps to an env var of the same name."""

    LLM_PROVIDER: str = "deepseek"
    LLM_MODEL: str = ""  # empty = use the provider preset's default model
    LLM_BASE_URL: str = ""  # empty = use the provider preset's base URL
    LLM_API_KEY: str = ""  # empty = use the provider preset's own key env var
    MAX_STEPS: int = 30
    TOOL_TIMEOUT_S: float = 60.0
    LLM_TIMEOUT_S: float = 120.0
    LLM_RETRIES: int = 3
    LLM_MAX_TOKENS: int | None = None
    TEMPERATURE: float | None = None
    HOST: str = "127.0.0.1"
    PORT: int = 8642
    SYSTEM_PROMPT: str = DEFAULT_SYSTEM_PROMPT
    # Poe's kimi-k3 (and other reasoning-only models) take "low"/"medium"/
    # "high" here instead of temperature/top_p; "" = don't send the field.
    REASONING_EFFORT: str = ""


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return the cached Settings singleton built from the environment.

    The API key is required only when actually constructing a real LLM
    client (see harness.llm); it is never logged.
    """
    return Settings(
        LLM_PROVIDER=_env_str("LLM_PROVIDER", "deepseek"),
        LLM_MODEL=_env_str("LLM_MODEL", ""),
        LLM_BASE_URL=_env_str("LLM_BASE_URL", ""),
        LLM_API_KEY=_env_str("LLM_API_KEY", ""),
        MAX_STEPS=_env_int("MAX_STEPS", 30),
        TOOL_TIMEOUT_S=_env_float("TOOL_TIMEOUT_S", 60.0),
        LLM_TIMEOUT_S=_env_float("LLM_TIMEOUT_S", 120.0),
        LLM_RETRIES=_env_int("LLM_RETRIES", 3),
        LLM_MAX_TOKENS=_env_opt_int("LLM_MAX_TOKENS"),
        TEMPERATURE=_env_opt_float("TEMPERATURE"),
        HOST=_env_str("HOST", "127.0.0.1"),
        PORT=_env_int("PORT", 8642),
        SYSTEM_PROMPT=_load_system_prompt(_env_str("SYSTEM_PROMPT", DEFAULT_SYSTEM_PROMPT)),
        REASONING_EFFORT=_env_str("REASONING_EFFORT", ""),
    )

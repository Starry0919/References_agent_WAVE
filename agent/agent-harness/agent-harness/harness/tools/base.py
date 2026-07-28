"""Tool system core: @tool decorator, registry, schema builder, executor."""
from __future__ import annotations

import asyncio
import inspect
import json
import logging
import re
import time
import types
from dataclasses import dataclass
from typing import Any, Callable, Union, get_args, get_origin, get_type_hints

from harness.config import get_settings

logger = logging.getLogger(__name__)

_MAX_RESULT_CHARS = 50_000

_SCALAR_TYPES: dict[Any, str] = {
    str: "string",
    int: "integer",
    float: "number",
    bool: "boolean",
}

_SECTION_HEADERS = {
    "args:", "arguments:", "returns:", "return:", "raises:", "yields:",
    "yield:", "example:", "examples:", "note:", "notes:", "attributes:",
}

_ARG_LINE_RE = re.compile(r"^([A-Za-z_]\w*)\s*(\([^)]*\))?\s*:\s*(.*)$")


@dataclass
class ToolSpec:
    """Metadata for one registered tool."""

    name: str
    description: str
    parameters: dict
    func: Callable
    timeout: float | None
    is_async: bool
    source: str

    def to_openai(self) -> dict:
        """Return the OpenAI function-tool wire shape."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            },
        }


@dataclass
class ToolOutcome:
    """Result of executing a tool: text result, error flag, duration."""

    result: str
    is_error: bool
    duration_ms: int


REGISTRY: dict[str, ToolSpec] = {}


def register(spec: ToolSpec) -> None:
    """Add a tool to the registry; replaces (with a warning) on duplicate name."""
    if spec.name in REGISTRY:
        logger.warning(
            "tool %r re-registered from %s; replacing previous definition",
            spec.name,
            spec.source,
        )
    REGISTRY[spec.name] = spec


def get_tool(name: str) -> ToolSpec | None:
    """Look up a tool by name."""
    return REGISTRY.get(name)


def all_tools() -> list[ToolSpec]:
    """Return all registered tools sorted by name."""
    return sorted(REGISTRY.values(), key=lambda spec: spec.name)


def _parse_docstring(doc: str | None) -> tuple[str, dict[str, str]]:
    """Split a docstring into (description, per-param descriptions).

    The description is the text before the Google-style ``Args:`` line;
    param descriptions are parsed best-effort from the ``Args:`` section.
    """
    if not doc:
        return "", {}
    lines = inspect.cleandoc(doc).splitlines()
    description_lines: list[str] = []
    args_start: int | None = None
    for index, line in enumerate(lines):
        if line.strip().lower() in ("args:", "arguments:"):
            args_start = index + 1
            break
        description_lines.append(line)
    description = "\n".join(description_lines).strip()

    params: dict[str, str] = {}
    if args_start is not None:
        current: str | None = None
        for line in lines[args_start:]:
            stripped = line.strip()
            if not stripped:
                continue
            if stripped.lower() in _SECTION_HEADERS:
                break
            match = _ARG_LINE_RE.match(stripped)
            if match:
                name: str = match.group(1)
                current = name
                params[name] = match.group(3).strip()
            elif current is not None:
                params[current] = (params[current] + " " + stripped).strip()
    return description, params


def _schema_for_annotation(annotation: Any) -> tuple[dict, bool]:
    """Map a type hint to (JSON-schema fragment, is_optional)."""
    if annotation is inspect.Parameter.empty or annotation is None:
        return {"type": "string"}, False

    origin = get_origin(annotation)

    if origin is Union or origin is types.UnionType:
        args = list(get_args(annotation))
        non_none = [arg for arg in args if arg is not type(None)]
        optional = len(non_none) < len(args)
        if len(non_none) == 1:
            schema, _ = _schema_for_annotation(non_none[0])
            return schema, optional
        return {"type": "string"}, optional

    if annotation in _SCALAR_TYPES:
        return {"type": _SCALAR_TYPES[annotation]}, False

    if annotation is list or origin is list:
        schema: dict = {"type": "array"}
        item_args = get_args(annotation)
        if item_args and item_args[0] in _SCALAR_TYPES:
            schema["items"] = {"type": _SCALAR_TYPES[item_args[0]]}
        return schema, False

    if annotation is dict or origin is dict:
        return {"type": "object"}, False

    return {"type": "string"}, False


def _build_parameters(func: Callable, param_docs: dict[str, str]) -> dict:
    """Build an OpenAI-style JSON Schema for the function's parameters."""
    signature = inspect.signature(func)
    try:
        hints = get_type_hints(func)
    except Exception:
        hints = {}

    properties: dict[str, dict] = {}
    required: list[str] = []
    for param_name, param in signature.parameters.items():
        if param.kind in (
            inspect.Parameter.VAR_POSITIONAL,
            inspect.Parameter.VAR_KEYWORD,
        ):
            continue
        annotation = hints.get(param_name, param.annotation)
        schema, optional = _schema_for_annotation(annotation)
        if param_name in param_docs:
            schema["description"] = param_docs[param_name]
        properties[param_name] = schema
        if param.default is inspect.Parameter.empty and not optional:
            required.append(param_name)

    return {"type": "object", "properties": properties, "required": required}


def tool(
    func: Callable | None = None,
    *,
    name: str | None = None,
    description: str | None = None,
    timeout: float | None = None,
) -> Callable:
    """Register a sync or async function as an agent tool.

    Usable bare (``@tool``) or with keyword arguments
    (``@tool(name=..., description=..., timeout=...)``).
    """

    def decorate(f: Callable) -> Callable:
        doc_description, param_docs = _parse_docstring(inspect.getdoc(f))
        source = getattr(f, "__module__", None) or "unknown"
        spec = ToolSpec(
            name=name or f.__name__,
            description=description or doc_description,
            parameters=_build_parameters(f, param_docs),
            func=f,
            timeout=timeout,
            is_async=inspect.iscoroutinefunction(f),
            source=source,
        )
        register(spec)
        return f

    if func is not None:
        return decorate(func)
    return decorate


def _one_line(text: object) -> str:
    return " ".join(str(text).split())


def _split_call_arguments(func: Callable, arguments: dict) -> tuple[list, dict]:
    """Split model-provided arguments into (positional, keyword) for the call.

    Positional-only parameters cannot be passed as keywords, yet the schema
    exposes them as named properties — bind them positionally here so tools
    declared with ``def f(x, /, y)`` remain callable.
    """
    kwargs = dict(arguments)
    positional: list = []
    try:
        params = list(inspect.signature(func).parameters.values())
    except (TypeError, ValueError):  # pragma: no cover - no introspectable signature
        return positional, kwargs
    for param in params:
        if param.kind is not inspect.Parameter.POSITIONAL_ONLY:
            break
        if param.name not in kwargs:
            break  # let the call raise a readable TypeError if it was required
        positional.append(kwargs.pop(param.name))
    return positional, kwargs


async def execute_tool(name: str, arguments: dict) -> ToolOutcome:
    """Execute a registered tool safely; never raises for tool failures."""
    start = time.perf_counter()

    def elapsed_ms() -> int:
        return int((time.perf_counter() - start) * 1000)

    spec = get_tool(name)
    if spec is None:
        return ToolOutcome(
            result=f"ERROR: unknown tool: {name}",
            is_error=True,
            duration_ms=elapsed_ms(),
        )

    timeout = spec.timeout or get_settings().TOOL_TIMEOUT_S
    try:
        args, kwargs = _split_call_arguments(spec.func, arguments)
        if spec.is_async:
            awaitable = spec.func(*args, **kwargs)
        else:
            awaitable = asyncio.to_thread(spec.func, *args, **kwargs)
        raw = await asyncio.wait_for(awaitable, timeout=timeout)
        # Serialize inside the try: an unserializable return value (cycles,
        # non-primitive dict keys) must become an error outcome, not a crash.
        if not isinstance(raw, str):
            raw = json.dumps(raw, ensure_ascii=False, default=str)
    except asyncio.TimeoutError:
        logger.warning("tool %r timed out after %ss", name, timeout)
        return ToolOutcome(
            result=f"ERROR: TimeoutError: tool '{name}' did not finish within {timeout}s",
            is_error=True,
            duration_ms=elapsed_ms(),
        )
    except Exception as exc:
        logger.warning(
            "tool %r failed: %s: %s", name, type(exc).__name__, _one_line(exc)
        )
        return ToolOutcome(
            result=f"ERROR: {type(exc).__name__}: {_one_line(exc)}",
            is_error=True,
            duration_ms=elapsed_ms(),
        )

    if len(raw) > _MAX_RESULT_CHARS:
        cut = len(raw) - _MAX_RESULT_CHARS
        raw = raw[:_MAX_RESULT_CHARS] + f"\n...[truncated {cut} chars]"
    return ToolOutcome(result=raw, is_error=False, duration_ms=elapsed_ms())

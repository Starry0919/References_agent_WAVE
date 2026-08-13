"""Agent loop: drives the LLM tool-calling conversation for one user turn."""
from __future__ import annotations

import asyncio
import json
import logging
import uuid
from typing import Any

from harness.config import get_settings
from harness.llm import get_llm_client
from harness.sessions import Session, SessionStore
from harness.tools import all_tools, execute_tool
from harness.tools.base import ToolOutcome

logger = logging.getLogger(__name__)


def _parse_arguments(raw: str) -> tuple[dict | None, str | None]:
    """Parse tool-call arguments into a dict; returns (parsed, error_message)."""
    text = (raw or "").strip()
    if not text:
        return {}, None
    try:
        parsed = json.loads(text)
    except Exception as exc:
        return None, str(exc)
    if not isinstance(parsed, dict):
        return None, f"expected a JSON object, got {type(parsed).__name__}"
    return parsed, None


def _display_arguments(raw: str) -> Any:
    """Best-effort parsed arguments for display; raw string if unparsable."""
    text = (raw or "").strip()
    if not text:
        return {}
    try:
        return json.loads(text)
    except Exception:
        return raw


async def run_agent_turn(store: SessionStore, session: Session, user_content: str) -> None:
    """Run the full tool-calling loop for one user message.

    Never raises: cancellation and errors end with a run_finished event.
    """
    settings = get_settings()
    try:
        session.status = "running"
        # Heal any dangling tool_calls left by a previously interrupted run
        # BEFORE appending the user message, so the repair lands in a valid
        # position of the message sequence (assistant -> tool -> user).
        store.backfill_unanswered_tool_calls(session)
        session.emit("user_message", {"content": user_content})
        store.append_message(session, {"role": "user", "content": user_content})
        store.maybe_set_title(session, user_content)
        session.emit("run_started", {"run_id": uuid.uuid4().hex})

        client = get_llm_client()

        async def on_delta(text: str) -> None:
            session.emit("assistant_delta", {"text": text})

        async def on_thinking_delta(text: str) -> None:
            session.emit("assistant_thinking_delta", {"text": text})

        for step in range(1, settings.MAX_STEPS + 1):
            session.emit("llm_call_started", {"step": step})
            tools = [spec.to_openai() for spec in all_tools()]
            turn = await client.chat(
                session.messages,
                tools,
                on_delta=on_delta,
                on_thinking_delta=on_thinking_delta,
            )

            assistant_message: dict = {"role": "assistant", "content": turn.content or ""}
            if turn.tool_calls:
                assistant_message["tool_calls"] = [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {"name": tc.name, "arguments": tc.arguments_json},
                    }
                    for tc in turn.tool_calls
                ]
            store.append_message(session, assistant_message)
            session.emit(
                "assistant_message",
                {
                    "content": turn.content or "",
                    "thinking": turn.thinking,
                    "tool_calls": [
                        {
                            "id": tc.id,
                            "name": tc.name,
                            "arguments": _display_arguments(tc.arguments_json),
                        }
                        for tc in turn.tool_calls
                    ],
                },
            )

            if not turn.tool_calls:
                session.emit("run_finished", {"status": "completed"})
                return

            for tc in turn.tool_calls:
                parsed, parse_error = _parse_arguments(tc.arguments_json)
                session.emit(
                    "tool_call",
                    {
                        "id": tc.id,
                        "name": tc.name,
                        "arguments": parsed if parse_error is None else tc.arguments_json,
                    },
                )
                if parse_error is not None:
                    outcome = ToolOutcome(
                        result=f"ERROR: could not parse tool arguments as JSON: {parse_error}",
                        is_error=True,
                        duration_ms=0,
                    )
                else:
                    outcome = await execute_tool(tc.name, parsed or {})
                store.append_message(
                    session,
                    {"role": "tool", "tool_call_id": tc.id, "content": outcome.result},
                )
                session.emit(
                    "tool_result",
                    {
                        "id": tc.id,
                        "name": tc.name,
                        "result": outcome.result,
                        "is_error": outcome.is_error,
                        "duration_ms": outcome.duration_ms,
                    },
                )

        session.emit("run_finished", {"status": "max_steps"})
    except asyncio.CancelledError:
        # Stopped by the user: patch the protocol, report, and swallow.
        store.backfill_unanswered_tool_calls(session)
        session.emit("run_finished", {"status": "stopped"})
    except Exception as exc:
        logger.exception("agent turn failed for session %s", session.id)
        store.backfill_unanswered_tool_calls(session)
        session.emit("run_finished", {"status": "error", "error": str(exc)})
    finally:
        session.status = "idle"
        session.current_task = None

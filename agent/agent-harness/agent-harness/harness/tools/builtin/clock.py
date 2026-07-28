"""Builtin tool: report the current local time."""
from __future__ import annotations

from datetime import datetime

from harness.tools import tool


@tool
def clock() -> str:
    """Return the current local time in ISO 8601 format with timezone offset."""
    return datetime.now().astimezone().isoformat()

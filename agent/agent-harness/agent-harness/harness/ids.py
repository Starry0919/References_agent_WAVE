"""Shared id/timestamp helpers for the Problem-02 persistence layer -
mirrors the `PREFIX-<12 hex>` convention already used by
`harness/workflow/contracts.py::new_id` so ids are readable and
collision-resistant across both layers.
"""
from __future__ import annotations

import time
import uuid


def new_id(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:12]}"


def now() -> float:
    """Unix seconds - the one timestamp representation used throughout the
    Problem-02 layer (matches Problem 01's `contracts.ApprovalRecord.timestamp`
    convention), so event payloads and pydantic contracts compare cleanly."""
    return time.time()

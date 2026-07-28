"""`LLMGenerationRecord` (prompt §5.2): the one provenance table every
structured LLM generation call in this codebase writes to, regardless of
which task (`hypothesis`/`strategy`/`critic`) invoked it. Not a per-task
table - `task_type` distinguishes rows, matching this repo's existing
"one reusable table, not N near-identical tables" convention (see
`harness/orchestrator/models.py::OrchestratorGateDecision`'s own docstring
for the same reasoning).

This table is provenance/audit only - it is never itself read as evidence
by any deterministic rule or gate (prompt §2.4: "LLM 不可以...把自身输出作为
evidence"). Parsed LLM output only becomes a real domain object (a
`HypothesisVersion`, a `CandidateDesign`, a `ScientificReview`) after
passing through the SAME schema validation + deterministic rule + evidence
grounding pipeline a human- or rule-generated candidate would - this table
just records how that candidate was drafted.
"""
from __future__ import annotations

from sqlalchemy import JSON, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from harness.db import Base, guard_immutable_fields

GENERATION_TASK_TYPES = ("hypothesis", "strategy", "critic")
VALIDATION_STATUSES = ("valid", "schema_invalid", "empty", "provider_error", "not_attempted")


class LLMGenerationRecord(Base):
    __tablename__ = "llm_generation_records"

    generation_id: Mapped[str] = mapped_column(String, primary_key=True)
    task_type: Mapped[str] = mapped_column(String, index=True)  # one of GENERATION_TASK_TYPES
    provider: Mapped[str] = mapped_column(String)
    model_id: Mapped[str] = mapped_column(String)
    model_version_or_snapshot: Mapped[str] = mapped_column(String, default="unknown")
    prompt_template_id: Mapped[str] = mapped_column(String)
    prompt_template_version: Mapped[str] = mapped_column(String)
    input_refs: Mapped[dict] = mapped_column(JSON, default=dict)
    output_schema_version: Mapped[str] = mapped_column(String)
    raw_output_artifact_ref: Mapped[str | None] = mapped_column(String, default=None)
    parsed_output_ref: Mapped[dict | None] = mapped_column(JSON, default=None)
    validation_status: Mapped[str] = mapped_column(String)  # one of VALIDATION_STATUSES
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    fallback_used: Mapped[bool] = mapped_column(default=False)
    shared_model_risk: Mapped[bool] = mapped_column(default=False)
    token_usage_if_available: Mapped[dict | None] = mapped_column(JSON, default=None)
    latency: Mapped[float | None] = mapped_column(Float, default=None)
    created_at: Mapped[float] = mapped_column(Float)


guard_immutable_fields(LLMGenerationRecord, mutable_fields=set())

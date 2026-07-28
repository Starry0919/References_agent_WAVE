"""User-authored idea capture ("sudden inspiration" - a specific gene/
pathway modification the user wants explored). Deliberately its own table
and entity_type, separate from `EvidenceItem`/`KnowledgeClaim`, so a
`ProjectIdea`'s free text is never mixed into or mistaken for
knowledge-base-derived content (`harness/diagnosis/evidence.py`,
`harness/golden_set/models.py`). Every mutation also appends a
`ProjectEvent` (`harness/memory/event_store.py`), same as every other
Problem in this codebase - no second, disconnected history store.
"""
from __future__ import annotations

from sqlalchemy import Float, String
from sqlalchemy.orm import Mapped, mapped_column

from harness.db import Base, guard_immutable_fields

IDEA_STATUSES = ("captured", "linked_to_design", "dismissed")


class ProjectIdea(Base):
    __tablename__ = "project_ideas"

    idea_id: Mapped[str] = mapped_column(String, primary_key=True)
    project_id: Mapped[str] = mapped_column(String, index=True)
    actor_id: Mapped[str] = mapped_column(String)
    free_text: Mapped[str] = mapped_column(String)
    target_gene: Mapped[str | None] = mapped_column(String, default=None)
    modification_type: Mapped[str | None] = mapped_column(String, default=None)
    rationale: Mapped[str | None] = mapped_column(String, default=None)
    status: Mapped[str] = mapped_column(String, default="captured")  # one of IDEA_STATUSES
    linked_design_project_id: Mapped[str | None] = mapped_column(String, default=None)
    created_at: Mapped[float] = mapped_column(Float)


# The user's own text (free_text/target_gene/modification_type/rationale)
# is never rewritten after capture - only status/linked_design_project_id
# change, when the idea is later linked to a real design project or
# dismissed (same "append meaning, don't rewrite the original claim"
# discipline as `KnowledgeClaim` in the Knowledge Production surface).
guard_immutable_fields(ProjectIdea, mutable_fields={"status", "linked_design_project_id"})

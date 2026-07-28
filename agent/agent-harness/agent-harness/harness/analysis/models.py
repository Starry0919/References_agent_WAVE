"""AnalysisRun (doc 6.4): the minimal reproducibility manifest. Any
analysis missing a required field is marked `reproducibility_status:
incomplete` rather than silently claiming full reproducibility - see
`harness/analysis/provenance.py`.
"""
from __future__ import annotations

from sqlalchemy import JSON, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from harness.db import Base

REQUIRED_REPRODUCIBILITY_FIELDS = (
    "input_asset_ids",
    "sample_manifest_version",
    "parser_name",
    "parser_version",
    "workflow_name",
    "workflow_version",
    "code_commit",
    "container_or_environment_digest",
    "parameters",
    "random_seed",
    "qc_status",
    "output_checksums",
)


class AnalysisRun(Base):
    __tablename__ = "analysis_runs"

    analysis_run_id: Mapped[str] = mapped_column(String, primary_key=True)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.project_id"), index=True)
    input_asset_ids: Mapped[list] = mapped_column(JSON, default=list)
    sample_manifest_version: Mapped[str | None] = mapped_column(String, default=None)
    parser_name: Mapped[str | None] = mapped_column(String, default=None)
    parser_version: Mapped[str | None] = mapped_column(String, default=None)
    workflow_name: Mapped[str | None] = mapped_column(String, default=None)
    workflow_version: Mapped[str | None] = mapped_column(String, default=None)
    code_commit: Mapped[str | None] = mapped_column(String, default=None)
    container_or_environment_digest: Mapped[str | None] = mapped_column(String, default=None)
    parameters: Mapped[dict] = mapped_column(JSON, default=dict)
    random_seed: Mapped[int | None] = mapped_column(default=None)
    started_at: Mapped[float] = mapped_column(Float)
    completed_at: Mapped[float | None] = mapped_column(Float, default=None)
    qc_status: Mapped[str | None] = mapped_column(String, default=None)
    output_asset_ids: Mapped[list] = mapped_column(JSON, default=list)
    output_checksums: Mapped[list] = mapped_column(JSON, default=list)
    operator: Mapped[str] = mapped_column(String, default="")
    reproducibility_status: Mapped[str] = mapped_column(String, default="incomplete")  # complete|incomplete
    missing_fields: Mapped[list] = mapped_column(JSON, default=list)

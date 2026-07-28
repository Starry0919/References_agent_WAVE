"""`EvidenceMatchReport` (prompt §5.8): a formal, persisted record of how
well one `EvidenceItem` transfers to a query context (organism/strain/
condition/timepoint/intervention/measurement) - built by
`harness.evidence_retrieval.condition_matching`. Cross-strain/cross-species
evidence is never silently treated as a direct match; this table is the
auditable proof of that.
"""
from __future__ import annotations

from sqlalchemy import JSON, Float, String
from sqlalchemy.orm import Mapped, mapped_column

from harness.db import Base, guard_immutable_fields

MATCH_STATUSES = (
    "direct_match", "close_match", "partial_match", "cross_strain", "cross_species",
    "condition_mismatch", "endpoint_mismatch", "insufficient_metadata", "not_applicable",
)
DIMENSION_MATCH_VALUES = ("match", "mismatch", "unknown", "not_applicable")


class EvidenceMatchReport(Base):
    __tablename__ = "evidence_match_reports"

    match_report_id: Mapped[str] = mapped_column(String, primary_key=True)
    query_context_ref: Mapped[dict] = mapped_column(JSON, default=dict)
    evidence_id: Mapped[str] = mapped_column(String, index=True)
    organism_match: Mapped[str] = mapped_column(String, default="unknown")
    strain_match: Mapped[str] = mapped_column(String, default="unknown")
    genotype_match: Mapped[str] = mapped_column(String, default="unknown")
    medium_match: Mapped[str] = mapped_column(String, default="unknown")
    condition_match: Mapped[str] = mapped_column(String, default="unknown")
    timepoint_match: Mapped[str] = mapped_column(String, default="unknown")
    intervention_match: Mapped[str] = mapped_column(String, default="unknown")
    measurement_match: Mapped[str] = mapped_column(String, default="unknown")
    directness: Mapped[str] = mapped_column(String, default="indirect")  # direct|indirect
    transfer_risks: Mapped[list] = mapped_column(JSON, default=list)
    overall_match_status: Mapped[str] = mapped_column(String)  # one of MATCH_STATUSES
    downgrade_reasons: Mapped[list] = mapped_column(JSON, default=list)
    created_at: Mapped[float] = mapped_column(Float)


guard_immutable_fields(EvidenceMatchReport, mutable_fields=set())

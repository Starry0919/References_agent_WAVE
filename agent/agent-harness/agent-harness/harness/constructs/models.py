"""Construct and GenotypeVerification (doc 6.3): the explicit break between
"a DesignVersion exists" and "a real strain exists" - no code path in this
codebase may infer a real strain from a DesignVersion alone.
"""
from __future__ import annotations

from sqlalchemy import JSON, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from harness.db import Base, guard_immutable_fields

# doc 6.3's explicit lifecycle - the only legal values for Construct.status.
CONSTRUCT_STATUSES = ("designed", "build_in_progress", "verified", "test_ready", "tested", "archived")


class PhysicalStockRef(Base):
    """doc 6.10: a reference to an external LIMS/inventory system's record
    of physical stock. The agent may read/display/verify this, but must
    never treat a cached `resolved_snapshot` as current truth or claim to
    have decremented real inventory itself - no code path in this codebase
    writes availability_status without an external system confirmation."""

    __tablename__ = "physical_stock_refs"

    stock_ref_id: Mapped[str] = mapped_column(String, primary_key=True)
    external_system: Mapped[str] = mapped_column(String)
    external_stock_id: Mapped[str] = mapped_column(String)
    construct_id: Mapped[str] = mapped_column(ForeignKey("constructs.construct_id"), index=True)
    resolved_snapshot: Mapped[dict | None] = mapped_column(JSON, default=None)
    resolved_at: Mapped[float | None] = mapped_column(Float, default=None)
    availability_status: Mapped[str] = mapped_column(String, default="unknown")  # unknown|available|depleted|reserved


class Construct(Base):
    __tablename__ = "constructs"

    construct_id: Mapped[str] = mapped_column(String, primary_key=True)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.project_id"), index=True)
    design_version_id: Mapped[str] = mapped_column(ForeignKey("design_versions.design_version_id"), index=True)
    status: Mapped[str] = mapped_column(String, default="designed")
    physical_stock_ref_id: Mapped[str | None] = mapped_column(String, default=None)
    created_by: Mapped[str] = mapped_column(String)  # actor_id
    created_at: Mapped[float] = mapped_column(Float)
    updated_at: Mapped[float] = mapped_column(Float)


guard_immutable_fields(Construct, mutable_fields={"status", "physical_stock_ref_id", "updated_at"})


class GenotypeVerification(Base):
    """A construct is never assumed correctly built; this is the only
    record that lets a downstream Observation legitimately be attributed to
    the *planned* genotype (Genotype Verification Gate, doc 10.2)."""

    __tablename__ = "genotype_verifications"

    verification_id: Mapped[str] = mapped_column(String, primary_key=True)
    construct_id: Mapped[str] = mapped_column(ForeignKey("constructs.construct_id"), index=True)
    method: Mapped[str] = mapped_column(String, default="")  # e.g. "sanger_sequencing", "colony_pcr"
    result: Mapped[str] = mapped_column(String)  # confirmed|failed|inconclusive
    detail: Mapped[str] = mapped_column(String, default="")
    data_asset_id: Mapped[str | None] = mapped_column(String, default=None)
    verified_by: Mapped[str] = mapped_column(String)  # actor_id
    verified_at: Mapped[float] = mapped_column(Float)

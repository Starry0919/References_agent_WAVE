"""Construct / GenotypeVerification mutations (doc 6.3). No function here
ever infers a construct's existence or verification result from a
DesignVersion alone - both require an explicit record.
"""
from __future__ import annotations

from sqlalchemy.orm import Session

from harness.constructs.models import CONSTRUCT_STATUSES, Construct, GenotypeVerification
from harness.ids import new_id, now
from harness.memory import event_types as et
from harness.memory.event_store import append_event, snapshot

CONSTRUCT_SNAPSHOT_FIELDS = (
    "construct_id", "project_id", "design_version_id", "status",
    "physical_stock_ref_id", "created_by", "created_at", "updated_at",
)


class InvalidVerificationResult(ValueError):
    """Distinct from the bare `ValueError` this module also raises for
    "no such construct" - lets `harness/api/designs.py::verify_genotype`
    tell a 404 (unknown construct) apart from a 422 (malformed result
    value), rather than mapping both to the same status code."""


def register_construct(
    session: Session, *, project_id: str, design_version_id: str, created_by: str
) -> Construct:
    """`project_id`/`design_version_id` are both DB-enforced foreign keys
    (`ForeignKey("projects.project_id")` / `ForeignKey("design_versions.
    design_version_id")`) - checking existence first turns a bad id into a
    clean `ValueError` the route can map to 404, instead of an unhandled
    `sqlite3.IntegrityError` propagating out of `session.flush()` as a bare
    500 (the same failure shape as the `delete_project` FK bug)."""
    from harness.designs.models import DesignVersion
    from harness.projects.models import Project

    if session.get(Project, project_id) is None:
        raise ValueError(f"no such project: {project_id}")
    if session.get(DesignVersion, design_version_id) is None:
        raise ValueError(f"no such design version: {design_version_id}")

    ts = now()
    c = Construct(
        construct_id=new_id("CON"),
        project_id=project_id,
        design_version_id=design_version_id,
        status="designed",
        created_by=created_by,
        created_at=ts,
        updated_at=ts,
    )
    session.add(c)
    session.flush()
    append_event(
        session, project_id=project_id, event_type=et.CONSTRUCT_REGISTERED, entity_type="Construct",
        entity_id=c.construct_id, payload=snapshot(c, CONSTRUCT_SNAPSHOT_FIELDS),
        actor_type="human", actor_id=created_by,
    )
    return c


def set_construct_status(session: Session, *, construct_id: str, status: str, actor_id: str) -> Construct:
    if status not in CONSTRUCT_STATUSES:
        raise ValueError(f"unrecognized construct status {status!r}; must be one of {CONSTRUCT_STATUSES}")
    c = session.get(Construct, construct_id)
    if c is None:
        raise ValueError(f"no such construct: {construct_id}")
    c.status = status
    c.updated_at = now()
    session.flush()
    append_event(
        session, project_id=c.project_id, event_type=et.CONSTRUCT_STATUS_CHANGED, entity_type="Construct",
        entity_id=construct_id, payload=snapshot(c, CONSTRUCT_SNAPSHOT_FIELDS),
        actor_type="human", actor_id=actor_id,
    )
    return c


def record_genotype_verification(
    session: Session,
    *,
    construct_id: str,
    project_id: str,
    method: str,
    result: str,
    detail: str = "",
    data_asset_id: str | None = None,
    verified_by: str,
) -> GenotypeVerification:
    if session.get(Construct, construct_id) is None:
        raise ValueError(f"no such construct: {construct_id}")
    if result not in ("confirmed", "failed", "inconclusive"):
        raise InvalidVerificationResult(f"unrecognized verification result {result!r}")
    v = GenotypeVerification(
        verification_id=new_id("GVER"),
        construct_id=construct_id,
        method=method,
        result=result,
        detail=detail,
        data_asset_id=data_asset_id,
        verified_by=verified_by,
        verified_at=now(),
    )
    session.add(v)
    session.flush()

    new_status = "verified" if result == "confirmed" else "build_in_progress"
    set_construct_status(session, construct_id=construct_id, status=new_status, actor_id=verified_by)

    append_event(
        session, project_id=project_id, event_type=et.GENOTYPE_VERIFIED, entity_type="GenotypeVerification",
        entity_id=v.verification_id,
        payload={
            "verification_id": v.verification_id, "construct_id": construct_id, "method": method,
            "result": result, "detail": detail, "data_asset_id": data_asset_id,
        },
        actor_type="human", actor_id=verified_by,
    )
    return v

"""Component: Biological Entity Layer service. Get-or-create only - there
is no bulk import path and no function that invents an entity nobody
actually referenced.
"""
from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from harness.ids import new_id, now
from harness.world_model.models import ENTITY_SOURCES, ENTITY_TYPES, BiologicalEntity


class InvalidEntityType(ValueError):
    pass


class InvalidEntitySource(ValueError):
    pass


def get_or_create_entity(
    session: Session,
    *,
    entity_type: str,
    name: str,
    actor_id: str,
    source: str,
    canonical_id: str | None = None,
    namespace: str | None = None,
    aliases: list[str] | None = None,
    organism_scope: str | None = None,
    description: str = "",
    source_ref: str | None = None,
) -> BiologicalEntity:
    """Idempotent by `(canonical_id, namespace)` when both are supplied
    (the stable identity case - e.g. a cobrapy gene id inside one GEM
    namespace), otherwise by `(entity_type, name)` (the free-text DDR case,
    where no namespace exists). A second call that only adds a new alias
    appends it rather than creating a duplicate row."""
    if entity_type not in ENTITY_TYPES:
        raise InvalidEntityType(f"entity_type must be one of {ENTITY_TYPES}, got {entity_type!r}")
    if source not in ENTITY_SOURCES:
        raise InvalidEntitySource(f"source must be one of {ENTITY_SOURCES}, got {source!r}")

    if canonical_id and namespace:
        existing = session.execute(
            select(BiologicalEntity).where(BiologicalEntity.canonical_id == canonical_id, BiologicalEntity.namespace == namespace)
        ).scalars().first()
    else:
        existing = session.execute(
            select(BiologicalEntity).where(BiologicalEntity.entity_type == entity_type, BiologicalEntity.name == name)
        ).scalars().first()

    if existing is not None:
        for alias in aliases or []:
            if alias not in existing.aliases:
                existing.aliases = [*existing.aliases, alias]
        if description and not existing.description:
            existing.description = description
        session.flush()
        return existing

    entity = BiologicalEntity(
        entity_id=new_id("ENT"), entity_type=entity_type, name=name, canonical_id=canonical_id, namespace=namespace,
        aliases=aliases or [], organism_scope=organism_scope, description=description, source=source,
        source_ref=source_ref, created_by=actor_id, created_at=now(),
    )
    session.add(entity)
    session.flush()
    return entity


def get_entity(session: Session, entity_id: str) -> BiologicalEntity | None:
    return session.get(BiologicalEntity, entity_id)


def list_entities(session: Session, *, entity_type: str | None = None, query: str = "", limit: int = 50) -> list[BiologicalEntity]:
    stmt = select(BiologicalEntity)
    if entity_type is not None:
        stmt = stmt.where(BiologicalEntity.entity_type == entity_type)
    rows = list(session.execute(stmt).scalars().all())
    if query:
        query_lower = query.strip().lower()
        rows = [e for e in rows if query_lower in e.name.lower() or any(query_lower in a.lower() for a in e.aliases) or (e.canonical_id and query_lower in e.canonical_id.lower())]
    return rows[:limit]


def entity_to_dict(entity: BiologicalEntity) -> dict[str, Any]:
    return {
        "entity_id": entity.entity_id, "entity_type": entity.entity_type, "name": entity.name,
        "canonical_id": entity.canonical_id, "namespace": entity.namespace, "aliases": entity.aliases,
        "organism_scope": entity.organism_scope, "description": entity.description, "source": entity.source,
        "source_ref": entity.source_ref, "created_at": entity.created_at,
    }

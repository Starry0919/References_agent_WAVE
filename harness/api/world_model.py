"""Module 4 read/write API for represented world-model facts; no prediction endpoints."""
from __future__ import annotations

from dataclasses import asdict
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from harness.api.deps import get_db_session
from harness.world_model.entities import entity_to_dict, get_entity, get_or_create_entity, list_entities
from harness.world_model.entity_graph import build_entity_graph
from harness.world_model.provenance import get_transition_provenance
from harness.world_model.state_transition_graph import build_state_transition_graph
from harness.world_model.transitions import get_transition, list_transitions, record_state_transition, transition_to_dict

router = APIRouter(prefix="/api/world-model", tags=["world-model"])


class EntityInput(BaseModel):
    entity_type: str
    name: str = Field(min_length=1)
    canonical_id: str | None = None
    namespace: str | None = None
    aliases: list[str] = []
    organism_scope: str = "Escherichia coli K-12"
    description: str = ""
    source: str
    source_ref: str | None = None
    actor_id: str = "human"


class TransitionInput(BaseModel):
    project_id: str | None = None
    initial_state: dict[str, Any]
    perturbation: dict[str, Any]
    final_state: dict[str, Any]
    observed_changes: list[dict[str, Any]] = []
    mechanism: str = ""
    phenotype: str | None = None
    context: dict[str, Any]
    origin: str
    status: str | None = None
    evidence_id: str | None = None
    simulation_run_id: str | None = None
    outcome: str = "success"
    uncertainty: dict[str, Any] | None = None
    actor_id: str = "human"


@router.post("/entities")
def create_entity(body: EntityInput, session: Session = Depends(get_db_session)) -> dict[str, Any]:
    try:
        return entity_to_dict(get_or_create_entity(session, **body.model_dump(exclude={"actor_id"}), actor_id=body.actor_id))
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc


@router.get("/entities")
def entities(entity_type: str | None = None, query: str = "", limit: int = Query(50, ge=1, le=200), session: Session = Depends(get_db_session)) -> dict[str, Any]:
    rows = list_entities(session, entity_type=entity_type, query=query, limit=limit)
    return {"total": len(rows), "entities": [entity_to_dict(row) for row in rows]}


@router.get("/entities/{entity_id}")
def entity(entity_id: str, session: Session = Depends(get_db_session)) -> dict[str, Any]:
    row = get_entity(session, entity_id)
    if row is None:
        raise HTTPException(404, "entity not found")
    return entity_to_dict(row)


@router.post("/transitions")
def create_transition(body: TransitionInput, session: Session = Depends(get_db_session)) -> dict[str, Any]:
    try:
        return transition_to_dict(record_state_transition(session, **body.model_dump(exclude={"actor_id"}), actor_id=body.actor_id))
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc


@router.get("/transitions")
def transitions(project_id: str | None = None, origin: str | None = None, status: str | None = None, outcome: str | None = None, entity_id: str | None = None, host: str | None = None, perturbation_type: str | None = None, limit: int = Query(50, ge=1, le=200), session: Session = Depends(get_db_session)) -> dict[str, Any]:
    rows = list_transitions(session, project_id=project_id, origin=origin, status=status, outcome=outcome, entity_id=entity_id, host=host, perturbation_type=perturbation_type, limit=limit)
    return {"total": len(rows), "transitions": [transition_to_dict(row) for row in rows]}


@router.get("/transitions/{transition_id}")
def transition(transition_id: str, session: Session = Depends(get_db_session)) -> dict[str, Any]:
    row = get_transition(session, transition_id)
    if row is None:
        raise HTTPException(404, "transition not found")
    result = transition_to_dict(row)
    result["provenance"] = get_transition_provenance(row, session=session)
    return result


@router.get("/transition-graph")
def transition_graph(project_id: str | None = None, entity_id: str | None = None, origin: str | None = None, limit: int = Query(50, ge=1, le=200), session: Session = Depends(get_db_session)) -> dict[str, Any]:
    graph = build_state_transition_graph(session, project_id=project_id, entity_id=entity_id, origin=origin, limit=limit)
    return {"nodes": [asdict(node) for node in graph.nodes], "edges": [asdict(edge) for edge in graph.edges]}


@router.get("/entity-graph")
def entity_graph(host: str = "Escherichia coli K-12", product: str = "tryptophan", phenotype: str = "maintain growth", session: Session = Depends(get_db_session)) -> dict[str, Any]:
    if host.strip().lower() not in {"e. coli k-12", "e.coli k-12", "escherichia coli k-12"} or product.strip().lower() != "tryptophan":
        raise HTTPException(422, "Module 4 V1.1 supports only E. coli K-12 tryptophan engineering")
    graph = build_entity_graph(host=host, product=product, phenotype=phenotype, session=session)
    return {"nodes": [asdict(node) for node in graph.nodes], "edges": [asdict(edge) for edge in graph.edges], "unknowns": graph.unknowns}

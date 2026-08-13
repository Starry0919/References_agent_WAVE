"""Module 3 (Evidence Intelligence Infrastructure) API routes.

Thin HTTP wrapper over `harness.evidence_intelligence.service` - every route
here composes data other packages already persist (`harness.diagnosis`,
`harness.evidence_retrieval`, `harness.paper_extraction`/DDR,
`harness.engineering_design`); this router itself never writes to the DB or
to `knowledge/ddr_database/`.
"""
from __future__ import annotations

from dataclasses import asdict
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from harness.api.deps import get_db_session
from harness.evidence_intelligence.models import EngineeringContextQuery
from harness.evidence_intelligence.service import (
    characterize_evidence_object,
    get_evidence_object,
    get_provenance_graph,
    search_evidence_objects,
)

router = APIRouter(prefix="/api/evidence-intelligence", tags=["evidence-intelligence"])


def _evidence_object_dict(obj, *, with_characterization: bool = False) -> dict[str, Any]:
    payload = asdict(obj)
    if with_characterization:
        payload["characterization"] = characterize_evidence_object(obj)
    return payload


@router.get("/evidence/{evidence_id}")
def get_evidence(evidence_id: str, session: Session = Depends(get_db_session)) -> dict[str, Any]:
    """`evidence_id` is `diag:{evidence_item_id}` or `ddr:{ddr_id}:{step}` -
    the ids `GET /search` below and `harness.evidence_intelligence.
    adapters` both mint, so a caller never has to construct one by hand."""
    obj = get_evidence_object(evidence_id, session=session)
    if obj is None:
        raise HTTPException(404, f"no such evidence object: {evidence_id}")
    return _evidence_object_dict(obj, with_characterization=True)


@router.get("/search")
def search(
    host: str | None = None,
    product: str | None = None,
    objective: str | None = None,
    bottleneck: str | None = None,
    intervention_type: str | None = None,
    experimental_context: str | None = None,
    query: str = "",
    project_id: str | None = None,
    limit: int = Query(default=20, ge=1, le=100),
    session: Session = Depends(get_db_session),
) -> dict[str, Any]:
    """Component 2 - Engineering-aware Evidence Retrieval: every filter is
    optional and additive; an all-empty request degrades to a full browse
    of the DDR corpus (same contract `LocalDDRAdapter.search("")` already
    has) plus, when `project_id` is supplied, that project's own evidence
    items."""
    ctx = EngineeringContextQuery(
        host=host, product=product, objective=objective, bottleneck=bottleneck,
        intervention_type=intervention_type, experimental_context=experimental_context, free_text=query,
    )
    results = search_evidence_objects(ctx, session=session, project_id=project_id, limit=limit)
    return {
        "query": asdict(ctx),
        "total": len(results),
        "evidence": [_evidence_object_dict(o) for o in results],
    }


@router.get("/provenance-graph")
def provenance_graph(
    anchor_type: str = Query(..., pattern="^(ddr|strategy|candidate)$"),
    anchor_id: str = Query(...),
    session: Session = Depends(get_db_session),
) -> dict[str, Any]:
    """Component 4 - Engineering Provenance Graph. `anchor_type=ddr` needs
    no DB session data beyond the DDR corpus + rule library;
    `anchor_type=strategy|candidate` walks `harness.engineering_design`'s
    `EngineeringStrategy`/`CandidateDesign.evidence_links` outward from a
    real project row."""
    try:
        graph = get_provenance_graph(anchor_type, anchor_id, session=session)
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
    if graph is None:
        raise HTTPException(404, f"no such {anchor_type}: {anchor_id}")
    return {
        "anchor": graph.anchor,
        "nodes": [asdict(n) for n in graph.nodes],
        "edges": [asdict(e) for e in graph.edges],
        "unresolved": graph.unresolved,
    }

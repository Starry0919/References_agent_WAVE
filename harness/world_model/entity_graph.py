"""Component: Entity Graph (static biological relationships). Reuses
`harness.diagnosis.mechanism_graph.build_mechanism_graph()` - already a
real, DDR-sourced, never-fabricated entity-level graph builder - instead of
writing a second one (Module 4 prompt §12: "Do NOT create a generic
biological knowledge graph"). The only thing this module adds is resolving
each gene/enzyme/pathway/metabolite/environment/phenotype/regulation node
against the `BiologicalEntity` registry so a caller gets a stable
`entity_id` when one has already been recorded, alongside the DDR-sourced
label mechanism_graph already produces. Read-only: never creates an entity
as a side effect of building a graph.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from harness.diagnosis.mechanism_graph import DdrLookup, build_mechanism_graph
from harness.world_model.models import BiologicalEntity

# mechanism_graph's node_type vocabulary is broader than ENTITY_TYPES (it
# also has process/resource/measurement/model pseudo-nodes with no
# biological-entity equivalent) - only these map onto a real entity_type.
_MECHANISM_NODE_TYPE_TO_ENTITY_TYPE = {
    "gene": "gene", "enzyme": "protein", "pathway": "pathway", "metabolite": "metabolite",
    "environment": "environment", "phenotype": "phenotype", "regulation": "regulator",
}


@dataclass
class EntityGraphNode:
    id: str
    node_type: str  # mechanism_graph's own vocabulary (broader than ENTITY_TYPES)
    label: str
    entity_id: str | None  # resolved BiologicalEntity.entity_id, only when one already exists
    source: str


@dataclass
class EntityGraphEdge:
    source: str
    target: str
    edge_type: str
    source_ref: str
    applicability_context: dict[str, Any] = field(default_factory=dict)
    is_unknown_or_conflicting: bool = False


@dataclass
class EntityGraph:
    nodes: list[EntityGraphNode] = field(default_factory=list)
    edges: list[EntityGraphEdge] = field(default_factory=list)
    unknowns: list[str] = field(default_factory=list)


def build_entity_graph(
    *, host: str, product: str, phenotype: str = "", session: Session | None = None, ddr_lookup: DdrLookup | None = None,
) -> EntityGraph:
    mg = build_mechanism_graph(phenotype=phenotype or f"{product} production", product=product, host=host, ddr_lookup=ddr_lookup)

    nodes: list[EntityGraphNode] = []
    for n in mg.nodes:
        entity_id = None
        mapped_type = _MECHANISM_NODE_TYPE_TO_ENTITY_TYPE.get(n.node_type)
        if session is not None and mapped_type is not None:
            existing = session.execute(
                select(BiologicalEntity).where(BiologicalEntity.entity_type == mapped_type, BiologicalEntity.name == n.label)
            ).scalars().first()
            entity_id = existing.entity_id if existing else None
        nodes.append(EntityGraphNode(id=n.node_id, node_type=n.node_type, label=n.label, entity_id=entity_id, source=n.source))

    edges = [
        EntityGraphEdge(
            source=e.source_id, target=e.target_id, edge_type=e.edge_type, source_ref=e.source_ref,
            applicability_context=e.applicability_context, is_unknown_or_conflicting=e.is_unknown_or_conflicting,
        )
        for e in mg.edges
    ]
    return EntityGraph(nodes=nodes, edges=edges, unknowns=list(mg.unknowns))

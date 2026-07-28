"""Mechanism Graph Builder (doc03 4.3): phenotype -> process/pathway ->
reaction/metabolite -> enzyme/gene/regulation/resource/environment/
measurement/model, with typed, directed, sourced edges. Reuses Problem
01's DDR knowledge base (`workflows/synbio_v1/modules/retriever.py`) as a
seed for known pathways; when nothing matches, returns a minimal skeleton
(phenotype + measurement + model nodes only) rather than fabricating
pathway detail - the graph is allowed to be incomplete, but every gap is
recorded in `unknowns`, never silently absent.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

DdrLookup = Callable[[str, str], dict[str, Any] | None]


@dataclass
class GraphNode:
    node_id: str
    node_type: str  # phenotype|process|pathway|reaction|metabolite|enzyme|gene|regulation|resource|environment|measurement|model
    label: str
    source: str = "unknown"  # ddr_knowledge_base|generic_skeleton|user_input


@dataclass
class GraphEdge:
    source_id: str
    target_id: str
    edge_type: str  # causal|correlational|regulatory|measurement_of
    direction: str = "forward"
    source_ref: str = "unknown"
    applicability_context: dict[str, Any] = field(default_factory=dict)
    is_unknown_or_conflicting: bool = False


@dataclass
class MechanismGraph:
    nodes: list[GraphNode] = field(default_factory=list)
    edges: list[GraphEdge] = field(default_factory=list)
    unknowns: list[str] = field(default_factory=list)

    def nodes_by_type(self, node_type: str) -> list[GraphNode]:
        return [n for n in self.nodes if n.node_type == node_type]


def _default_ddr_lookup(host: str, product: str) -> dict[str, Any] | None:
    """Real lookup against Problem 01's DDR knowledge base
    (`workflows/synbio_v1/modules/retriever.py::retrieve`), imported
    lazily to avoid a hard dependency for callers that inject a fake
    lookup in tests."""
    try:
        from workflows.synbio_v1.modules import retriever as v1_retriever
    except ImportError:
        return None
    result = v1_retriever.retrieve(request=f"improve {product} production in {host}", task={"product": product, "host": host})
    return result.get("ddr")


def build_mechanism_graph(
    *, phenotype: str, product: str, host: str, ddr_lookup: DdrLookup | None = None
) -> MechanismGraph:
    graph = MechanismGraph()
    graph.nodes.append(GraphNode(node_id="phenotype:0", node_type="phenotype", label=phenotype, source="user_input"))

    lookup = ddr_lookup if ddr_lookup is not None else _default_ddr_lookup
    ddr = lookup(host, product)

    if ddr is None:
        graph.unknowns.append(f"no DDR knowledge base entry matched host={host!r} product={product!r} - pathway detail unknown")
    else:
        # This knowledge base stores bottlenecks/actions as prose strings,
        # not a structured gene/reaction registry (verified against
        # knowledge/ddr_database/*.json) - nodes here are coarse
        # "process"-level causal factors, not fabricated gene-level
        # precision the source data doesn't actually provide.
        pathway_label = ddr.get("metadata", {}).get("product_class") or product
        graph.nodes.append(GraphNode(node_id="pathway:0", node_type="pathway", label=pathway_label, source="ddr_knowledge_base"))
        ddr_id = ddr.get("ddr_id", "")
        graph.edges.append(GraphEdge(source_id="pathway:0", target_id="phenotype:0", edge_type="causal", source_ref=ddr_id))

        for i, bottleneck in enumerate(ddr.get("biological_diagnosis", {}).get("bottlenecks", [])):
            node_id = f"process:{i}"
            graph.nodes.append(GraphNode(node_id=node_id, node_type="process", label=str(bottleneck), source="ddr_knowledge_base"))
            graph.edges.append(GraphEdge(source_id=node_id, target_id="pathway:0", edge_type="causal", source_ref=ddr_id))

        for i, action in enumerate(ddr.get("engineering_actions", [])):
            if not isinstance(action, dict):
                continue
            target = action.get("target") or action.get("gene_or_pathway")
            if not target:
                continue
            node_id = f"regulation:{i}"
            graph.nodes.append(GraphNode(node_id=node_id, node_type="regulation", label=str(target), source="ddr_knowledge_base"))
            graph.edges.append(GraphEdge(source_id=node_id, target_id="pathway:0", edge_type="regulatory", source_ref=ddr_id))

    # Measurement and model nodes are always present - a graph missing
    # either cannot support the mandatory 4-category competing set
    # (doc03 2.2); `is_unknown_or_conflicting=True` marks them as
    # "possible, unverified" rather than an asserted causal claim.
    graph.nodes.append(GraphNode(node_id="measurement:0", node_type="measurement", label="measurement/QC error", source="generic_skeleton"))
    graph.nodes.append(GraphNode(node_id="model:0", node_type="model", label="model boundary/assumption error", source="generic_skeleton"))
    graph.edges.append(GraphEdge(source_id="measurement:0", target_id="phenotype:0", edge_type="causal", source_ref="generic_skeleton", is_unknown_or_conflicting=True))
    graph.edges.append(GraphEdge(source_id="model:0", target_id="phenotype:0", edge_type="causal", source_ref="generic_skeleton", is_unknown_or_conflicting=True))
    return graph

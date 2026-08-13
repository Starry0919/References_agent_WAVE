"""Mechanism Graph Builder (doc03 4.3): phenotype -> process/pathway ->
reaction/metabolite -> enzyme/gene/regulation/resource/environment/
measurement/model, with typed, directed, sourced edges. Reuses the real
DDR knowledge base (`knowledge/ddr_database/*.json`, schema v2.4) via
`harness.evidence_retrieval.local_ddr_adapter.LocalDDRAdapter` - the SAME
corpus access path `harness.engineering_design.strategy_prior_retrieval`
and `harness.api.generation` already use for evidence retrieval, not a
second, independent loader.

Module 2 audit finding (Engineering Decision Intelligence Layer prompt
§8): this file previously called `workflows.synbio_v1.modules.retriever`,
an older, isolated loader over the same `knowledge/ddr_database/`
directory that only reads v1-shaped fields (`metadata`,
`engineering_problem.problem_type`) via keyword/tag scoring, and never
touched `decision_chain`/`strategy_categories` - discarding the schema
v2.4 richness the corpus actually provides. `workflows/synbio_v1` itself
is untouched by this change; it remains its own tested subsystem
(`harness/workflow/synbio_stages.py`) - only this file's default DDR
source moved to the modern path.

When nothing matches, returns a minimal skeleton (phenotype + measurement
+ model nodes only) rather than fabricating pathway detail - the graph is
allowed to be incomplete, but every gap is recorded in `unknowns`, never
silently absent.
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
    """Real lookup against the modern DDR corpus via `LocalDDRAdapter`
    (imported lazily so callers that inject a fake `ddr_lookup` in tests
    never pay this import cost). Prefers an exact `metadata.target_product`
    match (case-insensitive) - the same identity `strategy_prior_
    retrieval.py` and `evidence_resolution.py` treat as authoritative;
    falls back to the adapter's own keyword-matched search order when no
    exact product match exists. Returns `None` (not a fabricated guess)
    when nothing matches."""
    from harness.evidence_retrieval.local_ddr_adapter import LocalDDRAdapter

    result = LocalDDRAdapter().search(product)
    if not result.documents:
        return None
    product_lower = product.strip().lower()
    exact = [d for d in result.documents if str(d.raw_metadata.get("metadata", {}).get("target_product", "")).strip().lower() == product_lower]
    best = exact[0] if exact else result.documents[0]
    return best.raw_metadata


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
        pathway_label = ddr.get("metadata", {}).get("product_class") or product
        graph.nodes.append(GraphNode(node_id="pathway:0", node_type="pathway", label=pathway_label, source="ddr_knowledge_base"))
        ddr_id = ddr.get("ddr_id", "")
        graph.edges.append(GraphEdge(source_id="pathway:0", target_id="phenotype:0", edge_type="causal", source_ref=ddr_id))

        for i, bottleneck in enumerate(ddr.get("biological_diagnosis", {}).get("bottlenecks", [])):
            node_id = f"process:{i}"
            graph.nodes.append(GraphNode(node_id=node_id, node_type="process", label=str(bottleneck), source="ddr_knowledge_base"))
            graph.edges.append(GraphEdge(source_id=node_id, target_id="pathway:0", edge_type="causal", source_ref=ddr_id))

        # `decision_chain` (schema v2.4) is the canonical, universal source
        # across the whole corpus - unlike the legacy `engineering_actions`
        # compat array (only DDR-001..005 carry it, per DDR-001's own
        # `_engineering_actions_note`). A step's `target.gene`/`target.enzyme`
        # gives a real, named node instead of a coarse "process" label,
        # without fabricating precision a step doesn't actually provide -
        # steps with neither stay unrepresented here rather than guessed.
        # `rule` (only ever non-null when the step passed the schema's own
        # mechanistic/analogy eligibility gate) is attached as edge metadata,
        # never a fabricated causal claim beyond what the step itself states.
        for i, step in enumerate(ddr.get("decision_chain", [])):
            target = step.get("target", {})
            gene, enzyme = target.get("gene"), target.get("enzyme")
            if gene:
                node_id, node_type, label = f"gene:{i}", "gene", str(gene)
            elif enzyme:
                node_id, node_type, label = f"enzyme:{i}", "enzyme", str(enzyme)
            else:
                continue
            rule = step.get("rule")
            graph.nodes.append(GraphNode(node_id=node_id, node_type=node_type, label=label, source="ddr_knowledge_base"))
            graph.edges.append(GraphEdge(
                source_id=node_id, target_id="pathway:0", edge_type="regulatory", source_ref=ddr_id,
                applicability_context={"rule": rule} if rule else {},
            ))

    # Measurement and model nodes are always present - a graph missing
    # either cannot support the mandatory 4-category competing set
    # (doc03 2.2); `is_unknown_or_conflicting=True` marks them as
    # "possible, unverified" rather than an asserted causal claim.
    graph.nodes.append(GraphNode(node_id="measurement:0", node_type="measurement", label="measurement/QC error", source="generic_skeleton"))
    graph.nodes.append(GraphNode(node_id="model:0", node_type="model", label="model boundary/assumption error", source="generic_skeleton"))
    graph.edges.append(GraphEdge(source_id="measurement:0", target_id="phenotype:0", edge_type="causal", source_ref="generic_skeleton", is_unknown_or_conflicting=True))
    graph.edges.append(GraphEdge(source_id="model:0", target_id="phenotype:0", edge_type="causal", source_ref="generic_skeleton", is_unknown_or_conflicting=True))
    return graph

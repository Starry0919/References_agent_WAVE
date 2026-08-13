"""Module 2 (Engineering Decision Intelligence Layer) §8: `build_mechanism_graph`
must source from the real, schema-v2.4 DDR corpus (via `LocalDDRAdapter`),
not the stale v1 `workflows.synbio_v1.modules.retriever` loader - see
`harness/diagnosis/mechanism_graph.py`'s module docstring for the audit
finding this fixes.
"""
from __future__ import annotations

from harness.diagnosis.mechanism_graph import build_mechanism_graph


def test_default_ddr_lookup_no_longer_uses_the_v1_retriever():
    """The module docstring is allowed to mention `workflows.synbio_v1` (it
    documents the audit finding this fix addresses) - only an actual import
    of the v1 retriever module is disallowed."""
    import harness.diagnosis.mechanism_graph as mg

    source = open(mg.__file__, encoding="utf-8").read()
    assert "import workflows.synbio_v1" not in source
    assert "from workflows.synbio_v1" not in source
    assert "LocalDDRAdapter" in source


def test_tryptophan_graph_has_real_gene_or_enzyme_nodes_sourced_from_a_real_ddr():
    graph = build_mechanism_graph(phenotype="low Trp titer", product="L-tryptophan", host="E. coli K-12")
    gene_or_enzyme_nodes = [n for n in graph.nodes if n.node_type in ("gene", "enzyme")]
    assert gene_or_enzyme_nodes, "decision_chain targets should surface real gene/enzyme nodes, not just coarse process text"
    for n in gene_or_enzyme_nodes:
        assert n.source == "ddr_knowledge_base"
        assert n.label  # never an empty/fabricated label

    gene_edges = [e for e in graph.edges if e.source_id.startswith(("gene:", "enzyme:"))]
    assert gene_edges
    for e in gene_edges:
        assert e.source_ref.startswith("DDR-"), "must cite a real DDR id, never 'generic_skeleton' for a knowledge-base-sourced node"


def test_rule_text_is_attached_as_edge_metadata_not_a_fabricated_node():
    graph = build_mechanism_graph(phenotype="low Trp titer", product="L-tryptophan", host="E. coli K-12")
    gene_edges = [e for e in graph.edges if e.source_id.startswith(("gene:", "enzyme:"))]
    # at least one DDR-001 step has a non-null `rule` - it must show up as
    # edge applicability_context, never invented text
    assert any(e.applicability_context.get("rule") for e in gene_edges)


def test_unmatched_product_still_returns_an_honest_empty_graph():
    graph = build_mechanism_graph(phenotype="low output", product="unobtainium", host="alien organism")
    assert graph.unknowns
    assert not [n for n in graph.nodes if n.node_type in ("gene", "enzyme", "pathway", "process")]


def test_exact_target_product_match_is_preferred_over_first_search_hit():
    from harness.diagnosis.mechanism_graph import _default_ddr_lookup

    ddr = _default_ddr_lookup("E. coli K-12", "L-tryptophan")
    assert ddr is not None
    assert str(ddr.get("metadata", {}).get("target_product", "")).strip().lower() == "l-tryptophan"

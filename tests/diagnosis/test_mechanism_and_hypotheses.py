"""Mechanism Graph Builder + Competing Hypothesis Generator + Deduplicator
(doc03 4.3/4.4/4.6, 2.2)."""
from __future__ import annotations

from harness.diagnosis.dedup import deduplicate
from harness.diagnosis.hypothesis_generator import MECHANISM_CLASSES, generate_competing_hypotheses
from harness.diagnosis.mechanism_graph import build_mechanism_graph


def test_mechanism_graph_uses_real_ddr_knowledge_base_for_tryptophan():
    graph = build_mechanism_graph(phenotype="low Trp titer", product="L-tryptophan", host="E. coli K-12")
    assert not graph.unknowns
    assert any(n.node_type == "pathway" for n in graph.nodes)
    assert any(n.node_type == "measurement" for n in graph.nodes)
    assert any(n.node_type == "model" for n in graph.nodes)


def test_mechanism_graph_records_unknown_for_unmatched_product():
    graph = build_mechanism_graph(phenotype="low output", product="unobtainium", host="alien organism")
    assert graph.unknowns
    # measurement/model nodes still present even with no matched pathway
    assert {n.node_type for n in graph.nodes} == {"phenotype", "measurement", "model"}


def test_hypothesis_generator_covers_all_four_classes_when_basis_exists():
    graph = build_mechanism_graph(phenotype="low Trp titer", product="L-tryptophan", host="E. coli K-12")
    result = generate_competing_hypotheses(
        graph=graph, observation_ids=["OBS-1"], context={"medium": "M9", "oxygenation": "DO 30%"}, has_reference_model=True,
    )
    represented = {h.mechanism_class for h in result.hypotheses}
    assert represented == set(MECHANISM_CLASSES)
    assert not result.excluded_classes


def test_hypothesis_generator_excludes_with_explicit_reason_never_silently():
    graph = build_mechanism_graph(phenotype="low output", product="unobtainium", host="alien")
    result = generate_competing_hypotheses(graph=graph, observation_ids=[], context={}, has_reference_model=False)
    represented = {h.mechanism_class for h in result.hypotheses}
    excluded = {e.mechanism_class for e in result.excluded_classes}
    # every class is either represented or explicitly excluded - never neither
    assert represented | excluded == set(MECHANISM_CLASSES)
    for excl in result.excluded_classes:
        assert excl.reason  # never an empty/undeclared exclusion


def test_hypothesis_generator_never_returns_a_single_bare_gene_list():
    """Each generated hypothesis carries falsifiers/discriminating
    predictions/assumptions - it is a testable claim, not a bare gene
    recommendation."""
    graph = build_mechanism_graph(phenotype="low Trp titer", product="L-tryptophan", host="E. coli K-12")
    result = generate_competing_hypotheses(graph=graph, observation_ids=["OBS-1"], context={}, has_reference_model=False)
    for h in result.hypotheses:
        assert h.falsifiers
        assert h.discriminating_predictions
        assert h.assumptions
        assert h.generation_provenance.get("method") == "rule_based_v1"


def test_dedup_merges_only_identical_mechanism_and_nodes():
    graph = build_mechanism_graph(phenotype="low Trp titer", product="L-tryptophan", host="E. coli K-12")
    result = generate_competing_hypotheses(graph=graph, observation_ids=["OBS-1"], context={}, has_reference_model=False)
    # duplicate the first hypothesis exactly
    duplicate = result.hypotheses[0]
    kept, groups = deduplicate(result.hypotheses + [duplicate])
    assert len(kept) == len(result.hypotheses)  # the exact duplicate was merged
    assert len(groups) == 1


def test_omics_layers_reflects_only_typed_observations():
    graph = build_mechanism_graph(phenotype="low Trp titer", product="L-tryptophan", host="E. coli K-12")
    result = generate_competing_hypotheses(
        graph=graph, observation_ids=["OBS-1", "OBS-2", "OBS-3"], context={}, has_reference_model=False,
        observation_modalities={"OBS-1": "transcriptomic", "OBS-2": "fluxomic", "OBS-3": "unknown"},
    )
    bio_hyps = [h for h in result.hypotheses if h.mechanism_class == "biological_mechanism"]
    assert bio_hyps
    for h in bio_hyps:
        assert h.omics_layers == ["fluxomic", "transcriptomic"]  # sorted, "unknown" excluded


def test_omics_layers_honestly_empty_without_a_modality_map():
    graph = build_mechanism_graph(phenotype="low Trp titer", product="L-tryptophan", host="E. coli K-12")
    result = generate_competing_hypotheses(graph=graph, observation_ids=["OBS-1"], context={}, has_reference_model=False)
    for h in result.hypotheses:
        assert h.omics_layers == []


def test_dedup_never_collapses_mechanistically_distinct_hypotheses():
    graph = build_mechanism_graph(phenotype="low Trp titer", product="L-tryptophan", host="E. coli K-12")
    result = generate_competing_hypotheses(
        graph=graph, observation_ids=["OBS-1"], context={"medium": "M9"}, has_reference_model=True,
    )
    kept, groups = deduplicate(result.hypotheses)
    # distinct mechanism classes / nodes must all survive - not collapsed by dedup
    assert len(kept) == len(result.hypotheses)
    assert not groups

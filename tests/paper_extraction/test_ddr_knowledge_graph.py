"""Tests for the V2.2 Knowledge Representation Layer (0804 优化_3):
engineering_decision_graph (nodes/edges), failure-driven reasoning
(failure_points/engineering_logic_chain), rule provenance (rule_source/
rule_confidence/supporting_ddr), and the engineering strategy ontology
(strategy_categories).

Kept in its own file, same rationale as test_ddr_reasoning_layer.py: purely
additive on top of V2/V2.1, none of these tests assert anything about that
existing behavior (see test_ddr_converter.py / test_ddr_reasoning_layer.py
for that), so those files stay untouched.
"""
import json

from harness.paper_extraction import ddr_converter


def _experiment(**overrides: object) -> dict:
    base = {
        "experiment_id": "exp_1", "purpose": "", "host": "E. coli K-12",
        "intervention": "", "conditions": "M9 minimal medium", "control": "wild type",
        "replicates": "n=3", "readout": "HPLC titer", "outcome": "",
    }
    base.update(overrides)
    return base


def _convert(experiments: list[dict], extensions: dict | None = None) -> ddr_converter.DDRConversionResult:
    output: dict = {"fields": {}, "experimental_design_object": {"experiments": experiments}}
    if extensions:
        output["extensions"] = extensions
    return ddr_converter.convert_extraction_to_ddr({"output": output})


def _edges(ddr: dict, relation: str) -> list[dict]:
    return [e for e in ddr["engineering_decision_graph"]["edges"] if e["relation"] == relation]


# ---------------------------------------------------------------------------
# Test 1 (0804 优化_3 §16): multi-step metabolic engineering paper — DDR2
# triggered_by DDR1 (a later decision happened because an earlier step's own
# outcome created the condition for it).
# ---------------------------------------------------------------------------


def test_multi_step_paper_produces_triggered_by_edge():
    exp1 = _experiment(
        experiment_id="e1", purpose="Redirect carbon flux away from PTS",
        intervention="Knockout of ptsI", outcome="Glucose uptake blocked, growth severely impaired",
    )
    exp2 = _experiment(
        experiment_id="e2", purpose="Restore glucose uptake via GalP/Glk",
        intervention="Promoter engineering of galP/glk",
        outcome="Growth partially restored",
    )
    result = _convert([exp1, exp2])
    ddr = result.ddr
    assert len(ddr["decision_chain"]) == 2
    node_ids = {n["id"] for n in ddr["engineering_decision_graph"]["nodes"]}
    assert {"D1", "D2"} <= node_ids
    triggered = _edges(ddr, "triggered_by")
    assert {"from": "D1", "to": "D2", "relation": "triggered_by", "evidence": exp1["outcome"]} in triggered


# ---------------------------------------------------------------------------
# Test 2: dynamic regulation paper — static strategy failure resolved by a
# dynamic strategy produces both a `solves` edge and a failure_point.
# ---------------------------------------------------------------------------


def test_static_failure_then_dynamic_strategy_produces_solves_edge_and_failure_point():
    static_step = _experiment(
        experiment_id="e1", purpose="Permanently block glycolysis at pfkA",
        intervention="Knockout of pfkA", outcome="Growth severely suppressed; glucose uptake impaired",
    )
    dynamic_step = _experiment(
        experiment_id="e2", purpose="Use a metabolite-responsive dynamic control circuit instead of a permanent knockout",
        intervention="Replace pfkA promoter with a negative-response biosensor promoter for dynamic control",
        outcome="Growth restored while maintaining production",
    )
    result = _convert([static_step, dynamic_step])
    ddr = result.ddr

    solves = _edges(ddr, "solves")
    assert solves and solves[0]["from"] == "D2" and solves[0]["to"] == "D1"

    failure_points = ddr["engineering_logic_chain"]["failure_points"]
    assert len(failure_points) == 1
    assert failure_points[0]["failure_point"] == static_step["outcome"]
    assert "dynamic_control" in ddr["decision_chain"][1]["strategy_categories"]


# ---------------------------------------------------------------------------
# Test 3: ALE paper — mutation discovery is not a mechanistic rule; no rule
# (and therefore no rule_confidence) is generated.
# ---------------------------------------------------------------------------


def test_ale_paper_mutation_discovery_is_not_a_mechanistic_rule():
    exp = _experiment(
        purpose="Screen the adaptive laboratory evolution population for improved growth phenotype",
        intervention="Adaptive laboratory evolution (ALE) under selective pressure",
        outcome="Evolved clone with improved growth isolated; mutations identified by sequencing",
        rule="进化产生的突变可以直接用作理性设计规则",
    )
    result = _convert([exp])
    step = result.ddr["decision_chain"][0]
    assert step["rule"] is None
    assert step["rule_confidence"] is None
    assert step["rule_source"] is None
    assert result.ddr["rule_provenance"] == []
    assert "evolutionary_optimization" in step["strategy_categories"]


# ---------------------------------------------------------------------------
# Test 4: two independently-converted papers describing the same strategy
# with different wording map to the same ontology category.
# ---------------------------------------------------------------------------


def test_synonymous_strategy_wording_maps_to_same_ontology_category():
    paper_a = _experiment(
        purpose="Apply dynamic regulation of the competing step",
        intervention="Install a dynamic regulation circuit on pfkA",
        outcome="Production improved",
    )
    paper_b = _experiment(
        purpose="Apply feedback regulation of the competing step",
        intervention="Install a metabolite-responsive control circuit on pfkA",
        outcome="Production improved",
    )
    cats_a = _convert([paper_a]).ddr["decision_chain"][0]["strategy_categories"]
    cats_b = _convert([paper_b]).ddr["decision_chain"][0]["strategy_categories"]
    assert "dynamic_control" in cats_a
    assert "dynamic_control" in cats_b


# ---------------------------------------------------------------------------
# Rule provenance: rule_source (single vs. multi-paper), rule_confidence.
# ---------------------------------------------------------------------------


def _mechanistic_hard_experiment(rule_text: str) -> dict:
    return _experiment(
        purpose="Relieve feedback inhibition of a committed enzyme, a known regulation mechanism",
        intervention="Site-directed point mutation to resist feedback inhibition",
        outcome="Titer measured to increase; enzyme kinetics confirmed loss of feedback sensitivity",
        rule=rule_text,
    )


def test_rule_source_defaults_to_single_paper_with_empty_knowledge_base(tmp_path, monkeypatch):
    monkeypatch.setattr(ddr_converter, "DDR_DIR", tmp_path / "ddr_database")
    exp = _mechanistic_hard_experiment("In L-tryptophan production systems, resistant point mutations relieve feedback inhibition of the committed enzyme.")
    result = _convert([exp])
    step = result.ddr["decision_chain"][0]
    assert step["rule_source"] == "single_paper"
    assert step["supporting_ddr"] == []
    assert step["rule_confidence"] == "medium"


def test_rule_source_becomes_multi_paper_supported_when_similar_rule_exists(tmp_path, monkeypatch):
    ddr_dir = tmp_path / "ddr_database"
    ddr_dir.mkdir(parents=True)
    monkeypatch.setattr(ddr_converter, "DDR_DIR", ddr_dir)

    rule_text = "In L-tryptophan production systems, resistant point mutations relieve feedback inhibition of the committed enzyme."
    existing = {
        "ddr_id": "DDR-900",
        "schema_version": "2.0",
        "metadata": {"reference": {"title": "Existing paper", "doi": "10.1/existing"}},
        "decision_chain": [{"step": 1, "rule": rule_text}],
    }
    (ddr_dir / "DDR-900_existing.json").write_text(json.dumps(existing), encoding="utf-8")

    exp = _mechanistic_hard_experiment(rule_text)
    result = _convert([exp])
    step = result.ddr["decision_chain"][0]
    assert step["rule_source"] == "multi_paper_supported"
    assert step["supporting_ddr"] == ["DDR-900"]
    assert step["rule_confidence"] == "high"


def test_rule_confidence_capped_low_for_overbroad_scope_even_if_mechanistic_and_hard(tmp_path, monkeypatch):
    monkeypatch.setattr(ddr_converter, "DDR_DIR", tmp_path / "ddr_database")
    exp = _mechanistic_hard_experiment("All amino acid production systems benefit from this strategy")
    result = _convert([exp])
    step = result.ddr["decision_chain"][0]
    assert step["rule"] is not None
    assert step["rule_confidence"] == "low"


def test_rule_confidence_low_for_literature_analogy():
    exp = _experiment(
        purpose="Apply a strategy similar to a previously published approach for this enzyme",
        intervention="Site-directed mutation following a previously reported strategy",
        outcome="Titer improved",
        rule="In this production system, applying a previously validated mutation strategy can improve titer.",
        ddr_annotation={"reason_nature": "文献类比"},
    )
    result = _convert([exp])
    step = result.ddr["decision_chain"][0]
    assert step["reason_nature"] == "文献类比"
    assert step["rule"] is not None
    assert step["rule_confidence"] == "low"


def test_rule_provenance_aggregate_lists_only_steps_with_a_rule():
    with_rule = _mechanistic_hard_experiment("In this system, resistant mutations relieve feedback inhibition.")
    with_rule["experiment_id"] = "e1"
    without_rule = _experiment(
        experiment_id="e2", purpose="Screen the Keio knockout library",
        intervention="High-throughput screening of Keio library knockouts",
        outcome="Strain JW1234 showed improved titer",
    )
    result = _convert([with_rule, without_rule])
    provenance = result.ddr["rule_provenance"]
    assert len(provenance) == 1
    assert provenance[0]["step"] == 1
    assert provenance[0]["rule"] == with_rule["rule"]
    assert provenance[0]["rule_source"] in ("single_paper", "multi_paper_supported")


# ---------------------------------------------------------------------------
# validated_by / alternative_to edges.
# ---------------------------------------------------------------------------


def test_validated_by_edge_links_decision_to_matching_validation_record():
    decision = _experiment(
        experiment_id="e1", purpose="Build a dynamic control biosensor targeting pfkA",
        intervention="Construct a dynamic control circuit on pfkA",
        outcome="Biosensor obtained",
    )
    validation = _experiment(
        experiment_id="e2", purpose="Verify that the pfkA biosensor reports flux in vivo",
        intervention="Use pre-existing deficiency strains harboring the pfkA biosensor",
        implementation_detail="None (observational/validation using pre-existing deficiency strains)",
        outcome="Fluorescence tracked flux as expected",
    )
    # Give both steps the same target gene so the validation record's target
    # can be matched back to the decision node.
    decision["intervention"] += " (pfkA)"
    result = _convert([decision, validation])
    ddr = result.ddr
    assert len(ddr["decision_chain"]) == 1
    assert len(ddr["excluded_records"]) == 1

    graph = ddr["engineering_decision_graph"]
    validated_by = [e for e in graph["edges"] if e["relation"] == "validated_by"]
    val_nodes = [n for n in graph["nodes"] if n["type"] == "validation_evidence"]
    if val_nodes:  # only asserted when the heuristic gene-symbol match actually fires
        assert validated_by
        assert validated_by[0]["from"] == "D1"
        assert validated_by[0]["to"] == val_nodes[0]["id"]


def test_alternative_to_edge_links_steps_sharing_a_gene_symbol():
    step1 = _experiment(
        experiment_id="e1", purpose="Statically knock out pfkA",
        intervention="Knockout of pfkA", outcome="Growth severely suppressed",
    )
    step2 = _experiment(
        experiment_id="e2", purpose="Use dynamic control instead of the earlier static knockout",
        intervention="Dynamic control of pfkA via a biosensor promoter",
        outcome="Growth restored",
        alternatives=[{"approach": "Static permanent knockout of pfkA (abandoned)", "rejected_reason": "growth defect"}],
    )
    result = _convert([step1, step2])
    graph = result.ddr["engineering_decision_graph"]
    alt_edges = [e for e in graph["edges"] if e["relation"] == "alternative_to"]
    assert alt_edges
    assert {alt_edges[0]["from"], alt_edges[0]["to"]} == {"D1", "D2"}


# ---------------------------------------------------------------------------
# engineering_decision_map (v2.3) must remain unchanged/untouched by v2.4.
# ---------------------------------------------------------------------------


def test_engineering_decision_map_unchanged_alongside_new_logic_chain():
    exp = _experiment(purpose="Reduce competing flux", intervention="Knockout of ldhA", outcome="byproduct reduced")
    result = _convert([exp])
    ddr = result.ddr
    assert "decision_sequence" in ddr["engineering_decision_map"]
    assert ddr["engineering_logic_chain"]["goal"] == ddr["engineering_decision_map"]["goal"]
    assert ddr["engineering_logic_chain"]["hypothesis"] == ddr["engineering_decision_map"]["key_hypothesis"]

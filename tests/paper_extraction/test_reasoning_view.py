from harness.paper_extraction.reasoning_view import (
    build_agent_trace,
    build_evidence_graph,
    build_evidence_provenance,
    build_experimental_design,
    build_header_summary,
)

_RAW = {
    "engineering_problem": {
        "problem_statement": "Trp production limited by multi-level regulation",
        "trigger_conditions": ["feedback inhibition observed"],
    },
    "biological_diagnosis": {
        "observations": ["TrpE inhibited by Trp"],
        "bottlenecks": ["TrpE feedback inhibition"],
        "mechanistic_explanation": "product feedback blocks flux",
    },
    "engineering_hypothesis": {
        "hypothesis": "Removing feedback inhibition increases flux",
        "expected_effect": "yield increases from 0.15 to 0.18 g/g",
    },
    "decision_chain": [
        {
            "step": 1,
            "target": {"gene": "trpE", "enzyme": "anthranilate synthase", "pathway": "trp"},
            "trigger": {"observation": "TrpE inhibited by Trp", "reasoning": "remove feedback to raise flux", "source_location": "Intro"},
            "evidence": {"description": "known mechanism", "source": "EcoCyc", "source_location": "EcoCyc: TRPE"},
            "evidence_grading": "硬",
            "implementation": "point mutation",
            "implementation_detail": "TrpE(S40F)",
            "result": {"metric": "resistance", "before": "wild type inhibited", "after": "S40F resistant", "fold_change": None},
        },
        {
            "step": 2,
            "target": {"gene": "trpC", "enzyme": "IGPS", "pathway": "trp"},
            "trigger": {"observation": "anthranilate accumulates", "reasoning": "feedforward inhibition of IGPS", "source_location": "Results"},
            "evidence": {"description": "IC50 measured", "source": "in vitro assay", "source_location": "Fig.2"},
            "evidence_grading": "软",
            "implementation": "heterologous replacement",
            "implementation_detail": "A. niger IGPS",
            "result": {"metric": "titer", "before": "19 g/L", "after": "29 g/L", "fold_change": "1.5x"},
        },
    ],
    "extraction_meta": {"human_review_status": "pending"},
}


def test_build_agent_trace_has_problem_intervention_logic_and_validation_steps():
    trace = build_agent_trace(_RAW)
    kinds = [s["kind"] for s in trace]
    assert kinds == ["problem_understanding", "intervention", "intervention", "logic_reconstruction", "evidence_validation"]
    intervention_steps = [s for s in trace if s["kind"] == "intervention"]
    assert intervention_steps[0]["design_step_ref"] == 1
    assert intervention_steps[1]["design_step_ref"] == 2
    assert trace[0]["design_step_ref"] == "all"
    # step numbers are contiguous and 1-indexed regardless of kind
    assert [s["step"] for s in trace] == [1, 2, 3, 4, 5]


def test_build_agent_trace_confidence_reflects_evidence_grading():
    trace = build_agent_trace(_RAW)
    hard_step = next(s for s in trace if s["design_step_ref"] == 1)
    soft_step = next(s for s in trace if s["design_step_ref"] == 2)
    assert hard_step["confidence"] == 0.9
    assert soft_step["confidence"] == 0.6


def test_build_experimental_design_maps_decision_chain_to_sop_steps():
    design = build_experimental_design(_RAW)
    assert [d["step"] for d in design] == [1, 2]
    assert design[0]["problem"] == "TrpE inhibited by Trp"
    assert design[0]["hypothesis"] == "remove feedback to raise flux"
    assert design[0]["engineering_action"] == {"type": "point mutation", "target": "trpE", "modification": "TrpE(S40F)"}
    assert design[0]["evidence"] == ["EcoCyc: TRPE", "EcoCyc"]
    assert design[1]["result"] == "19 g/L → 29 g/L（1.5x）"


def test_build_experimental_design_falls_back_to_legacy_engineering_actions():
    raw = {
        "engineering_problem": {"problem_statement": "flux limited"},
        "engineering_hypothesis": {"hypothesis": "rebalance flux"},
        "engineering_actions": [
            {"modification_type": "overexpression", "target": "aroG", "gene_or_pathway": "shikimate", "source": "paper", "validation": ["titer assay"], "expected_effect": "higher titer"},
        ],
    }
    design = build_experimental_design(raw)
    assert len(design) == 1
    assert design[0]["step"] == 1
    assert design[0]["problem"] == "flux limited"
    assert design[0]["engineering_action"]["type"] == "overexpression"
    assert design[0]["evidence"] == ["paper"]


def test_build_evidence_provenance_lists_one_claim_per_decision_step():
    items = build_evidence_provenance(_RAW)
    assert len(items) == 2
    assert items[0]["claim"] == "TrpE inhibited by Trp"
    assert items[0]["source"] == "EcoCyc: TRPE"
    assert items[0]["confidence"] == 0.9


def test_build_evidence_graph_links_steps_in_sequence_with_evidence_leaves():
    design = build_experimental_design(_RAW)
    graph = build_evidence_graph(design)
    step_ids = [n["id"] for n in graph["nodes"] if n["type"] == "step"]
    assert step_ids == ["step-1", "step-2"]
    assert {"source": "step-1", "target": "step-2", "type": "sequence"} in graph["edges"]
    supports_edges = [e for e in graph["edges"] if e["type"] == "supports"]
    assert any(e["target"] == "step-1" for e in supports_edges)


def test_build_header_summary_reflects_hard_evidence_ratio_and_review_status():
    design = build_experimental_design(_RAW)
    summary = build_header_summary(_RAW, has_design=bool(design))
    assert summary["status"] == "completed"
    assert summary["evidence_confidence"] == "medium"  # 1/2 hard = 0.5 ratio -> medium band
    assert summary["human_review_status"] == "pending"


def test_build_header_summary_pending_when_no_design_steps():
    summary = build_header_summary({}, has_design=False)
    assert summary["status"] == "pending"
    assert summary["evidence_confidence"] is None

"""Demo cases for the V0.1 synthetic biology workflow (revision spec section 8).

Run with pytest, or standalone via `python tests/test_synbio_v01.py` to
print the generated report for the Chinese demo case.
"""
from __future__ import annotations

import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from workflows.synbio_v01.workflow import run

DEMO_REQUEST_ZH = (
    "当前底盘为 E.coli K-12。"
    "目标是提高葡萄糖生产色氨酸能力。"
    "请分析代谢瓶颈并提出理性工程改造方案。"
)
MODULE0_EXAMPLE_ZH = "我们希望提高E.coli K-12利用葡萄糖生产色氨酸的能力，请分析限制因素并提出改造策略"

REPORT_HEADINGS = [
    "## 1. Engineering objective",
    "## 2. Host and constraints",
    "## 3. Pathway analysis",
    "## 4. Bottleneck identification",
    "## 5. DDR reasoning table",
    "## 6. Ranked engineering strategy",
    "## 7. Evidence evaluation",
    "## 8. Experimental validation plan",
    "## 9. Limitations",
]

DDR_KEYS = {
    "design_action", "target", "observation", "hypothesis", "evidence",
    "evidence_type", "reason_type", "implementation", "expected_effect",
    "validation", "general_rule",
}


def test_task_parser_always_injects_fixed_host() -> None:
    state = run(MODULE0_EXAMPLE_ZH)
    assert state.task == {
        "host": "E. coli K-12",
        "product": "tryptophan",
        "substrate": "glucose",
        "objective": "increase production",
        "constraints": [],
    }


def test_workflow_runs_end_to_end_on_chinese_demo_case() -> None:
    state = run(DEMO_REQUEST_ZH)

    # Module 0: host is injected, never parsed
    assert state.task["host"] == "E. coli K-12"
    assert state.task["product"] == "tryptophan"
    assert state.task["substrate"] == "glucose"
    assert state.task["objective"] == "increase production"

    # Module 1: DDRs carry the full reasoning chain, and are honestly labelled mock
    assert state.literature_records
    for record in state.literature_records:
        assert set(record) == DDR_KEYS
        assert record["evidence_type"] == "mock evidence"
        assert "not verified" in record["evidence"]

    # Pathway + competition analysis
    assert state.pathway["genes"]
    assert state.competition_analysis
    for comp in state.competition_analysis:
        assert set(comp) == {"pathway", "competition", "gene", "strategy", "risk"}

    # Key nodes derived from DDRs
    assert state.nodes
    for node in state.nodes:
        assert set(node) == {"target", "node_type", "reason", "suggested_strategy"}

    # Ranked engineering strategy: every design has a priority tier + reason,
    # and the list is sorted primary -> secondary -> optional.
    assert state.engineering_designs
    tier_order = {"primary intervention": 0, "secondary optimization": 1, "optional exploration": 2}
    seen_ranks = [tier_order[d["priority"]] for d in state.engineering_designs]
    assert seen_ranks == sorted(seen_ranks)
    assert any(d["priority"] == "primary intervention" for d in state.engineering_designs)
    trpE_design = next(d for d in state.engineering_designs if d["gene"] == "trpE")
    assert trpE_design["priority"] == "primary intervention"
    trpR_design = next(d for d in state.engineering_designs if d["gene"] == "trpR")
    assert trpR_design["priority"] == "secondary optimization"

    # Evidence evaluation: mock evidence -> low confidence, always needs validation
    assert len(state.evidence) == len(state.engineering_designs)
    for item in state.evidence:
        assert set(item) == {"recommendation", "evidence", "confidence", "needs_validation"}
        assert item["confidence"] == "low"
        assert item["needs_validation"] is True

    # Evaluator: evidence exists for every design, none reference the mock
    # essential-gene list, so everything should be accepted with no rejections.
    assert set(state.evaluation) == {"accepted_designs", "rejected_designs", "warnings"}
    assert len(state.evaluation["accepted_designs"]) == len(state.engineering_designs)
    assert state.evaluation["rejected_designs"] == []

    # Final report: explains WHY, not just a gene list
    assert state.final_report
    for heading in REPORT_HEADINGS:
        assert heading in state.final_report
    assert "trpE" in state.final_report
    assert "feedback" in state.final_report.lower()


def test_evaluator_rejects_knockout_of_mock_essential_gene() -> None:
    from workflows.synbio_v01.modules import evaluator

    designs = [{
        "gene": "dnaA",
        "modification": "knockout",
        "reason": "synthetic test case",
        "expected_effect": "n/a",
        "priority": "primary intervention",
        "priority_reason": "test",
    }]
    evidence_records = [{
        "recommendation": "knockout dnaA",
        "evidence": "synthetic test evidence",
        "confidence": "high",
        "needs_validation": False,
    }]

    result = evaluator.evaluate(designs, evidence_records, competition_records=[])

    assert result["accepted_designs"] == []
    assert len(result["rejected_designs"]) == 1
    assert "essential" in result["rejected_designs"][0]["rejection_reasons"][0]


def test_unknown_product_falls_back_gracefully() -> None:
    state = run("Improve production of an unlisted compound in E. coli K-12 from glucose.")

    assert state.task["product"] == "unknown"
    assert state.literature_records  # generic placeholder DDR, not empty
    assert state.nodes  # falls back to per-gene placeholder nodes
    assert state.final_report
    for heading in REPORT_HEADINGS:
        assert heading in state.final_report


if __name__ == "__main__":
    final_state = run(DEMO_REQUEST_ZH)
    print(final_state.final_report)

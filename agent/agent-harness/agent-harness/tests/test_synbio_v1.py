"""Demo case for the V1 evidence-grounded workflow (revision spec section 16).

Run with pytest, or standalone via `python tests/test_synbio_v1.py` to
print the generated report.
"""
from __future__ import annotations

import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from workflows.synbio_v1.modules import retriever
from workflows.synbio_v1.workflow import run

DEMO_REQUEST = "Design an E. coli K-12 strain for improved L-tryptophan production."

REPORT_HEADINGS = [
    "## 1. Engineering Objective",
    "## 2. Relevant DDR Evidence",
    "## 3. Biological Bottleneck",
    "## 4. Engineering Design",
    "## 5. Evidence Quality",
    "## 6. Validation Plan",
    "## 7. Limitations",
]


def test_knowledge_base_loads_five_ddrs() -> None:
    # DDR-004 (lysine) was added for problem 01's biological benchmark #2
    # (workflow/design/evolution/.../problem 01 doc, section 7.3) - see
    # tests/workflow/test_biological_benchmarks.py. DDR-005 (Chen & Zeng
    # 2018 tryptophan) is the teacher-specified decision-chain template for
    # 工作A (文献逆向工程 §4.4) - see knowledge/ddr_database/DDR-005_*.json.
    ddrs = retriever.load_ddrs()
    assert {d["ddr_id"] for d in ddrs} == {"DDR-001", "DDR-002", "DDR-003", "DDR-004", "DDR-005"}


def test_retrieval_example_from_spec_section_11() -> None:
    # Spec section 11's worked example.
    result = retriever.retrieve("Improve E. coli production of aromatic amino acid", task={"product": "unknown"})
    assert result["matched_ddr"] == "DDR-001"
    assert result["recommended_strategy"] == ["precursor engineering", "central carbon flux redistribution"]
    assert "aromatic amino acid" in result["reason"]


def test_tryptophan_demo_case_end_to_end() -> None:
    """Spec section 16's exact test case and its 5 expectations."""
    state = run(DEMO_REQUEST)

    # 1. Identify aromatic amino acid production problem.
    assert state.task["product"] == "L-tryptophan"
    assert state.diagnosis["matched_ddr"] == "DDR-001"
    assert any("precursor" in b.lower() for b in state.diagnosis["bottlenecks"])

    # 2. Retrieve DDR-001.
    assert state.retrieval["matched_ddr"] == "DDR-001"

    # 3. Recommend flux redistribution strategy.
    assert "central carbon flux redistribution" in state.retrieval["recommended_strategy"]
    assert any(a["modification_type"] == "flux redistribution" for a in state.engineering_actions)

    # 4. Provide reference: Xiong et al., 2021, DOI:10.1002/bit.27665.
    ref = state.retrieval["ddr"]["metadata"]["reference"]
    assert ref["authors"] == "Xiong B. et al."
    assert ref["year"] == "2021"
    assert ref["doi"] == "10.1002/bit.27665"
    ddr_cited_evidence = [e for e in state.evidence if e["evidence_status"] == "reference_available"]
    assert ddr_cited_evidence
    assert all("10.1002/bit.27665" in e["reference"] for e in ddr_cited_evidence)

    # 5. Separate verified (DDR-cited) evidence from hypothesis-level (engineering
    # action library) recommendations - never fabricate a paper citation for either.
    assert len(state.evidence) == len(state.engineering_actions)
    library_evidence = [e for e in state.evidence if e["evidence_status"] == "general_engineering_knowledge"]
    assert library_evidence  # ptsG/pykF/xfpk actions came from the library, not the DDR
    for e in state.evidence:
        assert e["evidence_status"] in ("reference_available", "general_engineering_knowledge")
        assert e["confidence"] in ("low", "medium")  # never "high" - full text not independently verified
        assert e["needs_validation"] is True
        assert set(e["evidence_quality"]) == {
            "literature_support", "mechanistic_support", "strain_similarity", "transferability",
        }
    # library (general-knowledge) actions must never claim a paper reference
    assert all(e["reference"] is None for e in library_evidence)

    assert state.final_report
    for heading in REPORT_HEADINGS:
        assert heading in state.final_report
    assert "10.1002/bit.27665" in state.final_report


def test_limitations_section_holds_only_system_scope_not_biology() -> None:
    """Phase 5 rule: 'do not mix system limitations with biological conclusions' -
    biology/evidence caveats belong in Evidence Quality (section 5), not Limitations."""
    state = run(DEMO_REQUEST)
    limitations = state.final_report.split("## 7. Limitations")[1]
    assert "not independently verified" not in limitations
    assert "requires review of the primary literature" not in limitations
    # system-scope statements should still be present
    assert "FBA" in limitations
    assert "knowledge base" in limitations


def test_validation_plan_has_all_four_levels() -> None:
    state = run(DEMO_REQUEST)
    plan = state.validation_plan
    assert set(plan) == {"genotype", "mechanism", "phenotype", "tradeoff"}
    # every level must be populated for a matched DDR - genotype in particular
    # was entirely missing before Phase 4 (no PCR/sequencing step existed).
    for level in ("genotype", "mechanism", "phenotype", "tradeoff"):
        assert plan[level], f"validation level '{level}' should not be empty"
    assert any("pcr" in item.lower() or "sequenc" in item.lower() for item in plan["genotype"])
    assert any("titer" in item.lower() or "yield" in item.lower() for item in plan["phenotype"])


def test_strain_similarity_is_honestly_unknown_not_guessed() -> None:
    """The paper-metadata layer never records a verified strain identity (Phase 1
    honesty rule), so strain_similarity must be "unknown", never a guessed match."""
    state = run("Design an E. coli K-12 strain for improved L-tryptophan production.")
    ddr_cited_evidence = [e for e in state.evidence if e["evidence_status"] == "reference_available"]
    assert ddr_cited_evidence
    for e in ddr_cited_evidence:
        assert e["evidence_quality"]["strain_similarity"] == "unknown"
        assert "not verified" in e["reason"]


def test_bdo_and_isoprene_demo_cases_retrieve_correct_ddrs() -> None:
    bdo_state = run("Engineer E. coli to produce 1,4-butanediol, which it cannot make natively.")
    assert bdo_state.retrieval["matched_ddr"] == "DDR-002"
    assert any(a["modification_type"] == "pathway insertion" for a in bdo_state.engineering_actions)

    isoprene_state = run("Improve isoprene production in engineered E. coli.")
    assert isoprene_state.retrieval["matched_ddr"] == "DDR-003"
    # DDR-003's reference has no year/journal/DOI in the source summary - must not be fabricated.
    ref = isoprene_state.retrieval["ddr"]["metadata"]["reference"]
    assert ref["doi"] == ""
    assert ref["year"] == ""


def test_unmatched_problem_returns_no_fabricated_evidence() -> None:
    state = run("Improve production of an unlisted, fictional compound in a fictional organism.")

    assert state.retrieval["matched_ddr"] is None
    assert state.engineering_actions == []
    assert len(state.evidence) == 1
    unknown_evidence = state.evidence[0]
    assert unknown_evidence["evidence_status"] == "unknown"
    assert unknown_evidence["reference"] is None
    assert unknown_evidence["confidence"] == "low"
    assert unknown_evidence["needs_validation"] is True
    assert state.final_report
    for heading in REPORT_HEADINGS:
        assert heading in state.final_report


if __name__ == "__main__":
    final_state = run(DEMO_REQUEST)
    print(final_state.final_report)

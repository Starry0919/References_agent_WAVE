"""Idea Workbench (思路工作台) auto-population: every DDR already sitting in
the knowledge base - not just the ones a fresh retrieval run for this exact
project would produce - reshaped into an idea card and tagged `relevant`
against a project's own target product (`ddr_converter.ddr_to_idea_view`,
`harness.evidence_retrieval.relevance.ddr_relevance`). Mirrors
`test_knowledge_claims_from_rules.py`'s "tag, don't hide" contract.
"""
from __future__ import annotations

from fastapi.testclient import TestClient

from harness.paper_extraction import ddr_converter
from harness.server import create_app


def _client() -> TestClient:
    return TestClient(create_app())


def _sample_ddr(**overrides) -> dict:
    ddr = {
        "ddr_id": "DDR-900",
        "metadata": {
            "title": "Sample paper",
            "target_product": "L-tryptophan",
            "reference": {"title": "Sample paper", "journal": "J. Synth", "year": "2022", "doi": "10.1/x"},
        },
        "decision_chain": [
            {"step": 1, "design_action": "M5", "target": {"gene": "ptsG"}},
            {"step": 2, "design_action": "M5", "target": {"gene": "pykF"}},
        ],
        "engineering_problem": {"problem_statement": "Precursor supply limits titer"},
        "biological_diagnosis": {"mechanistic_explanation": "PEP/E4P shared with central metabolism"},
        "engineering_hypothesis": {"hypothesis": "Rebalancing flux relieves the bottleneck"},
    }
    ddr.update(overrides)
    return ddr


def test_ddr_to_idea_view_reshapes_a_real_ddr_without_fabricating_fields():
    idea = ddr_converter.ddr_to_idea_view(_sample_ddr())
    assert idea["idea_id"] == "DDR-900"
    assert idea["title"] == "Precursor supply limits titer"
    assert idea["summary"] == "Rebalancing flux relieves the bottleneck"
    assert idea["category"] == "genome"  # both decision_chain steps are M5
    assert idea["source"] == {"paper_id": "DDR-900", "title": "Sample paper", "journal": "J. Synth", "year": "2022", "doi": "10.1/x"}
    assert idea["evidence_ids"] == ["DDR-900:1", "DDR-900:2"]


def test_ddr_to_idea_view_falls_back_when_optional_narrative_fields_are_missing():
    ddr = _sample_ddr(engineering_hypothesis={}, biological_diagnosis={"observations": ["obs one"]})
    idea = ddr_converter.ddr_to_idea_view(ddr)
    assert idea["summary"] == "obs one"


def test_ddr_to_idea_view_categorizes_by_majority_design_action():
    ddr = _sample_ddr(decision_chain=[
        {"step": 1, "design_action": "M6"}, {"step": 2, "design_action": "M6"}, {"step": 3, "design_action": "M5"},
    ])
    assert ddr_converter.ddr_to_idea_view(ddr)["category"] == "expression"


def test_ddr_to_idea_view_defaults_to_other_with_no_decision_chain():
    assert ddr_converter.ddr_to_idea_view(_sample_ddr(decision_chain=[]))["category"] == "other"


def test_knowledge_ideas_api_lists_ideas_derived_from_the_real_ddr_database():
    with _client() as client:
        resp = client.get("/api/paper-extraction/knowledge-ideas")
        assert resp.status_code == 200, resp.text
        body = resp.json()
        assert body["total"] > 0
        idea = body["ideas"][0]
        assert set(idea) >= {"idea_id", "title", "summary", "category", "source", "evidence_ids"}


def test_knowledge_ideas_api_tags_relevance_to_a_project_without_hiding_others():
    with _client() as client:
        project_id = client.post("/api/projects", json={"name": "t", "target_product": "L-tryptophan", "actor_id": "pi"}).json()["project_id"]
        resp = client.get(f"/api/paper-extraction/knowledge-ideas?project_id={project_id}")
        assert resp.status_code == 200, resp.text
        ideas = resp.json()["ideas"]
        assert len(ideas) > 1
        assert any(i["relevant"] for i in ideas)
        assert any(not i["relevant"] for i in ideas)
        # relevant-first sort, matching /knowledge-claims and /engineering-actions
        relevant_flags = [i["relevant"] for i in ideas]
        assert relevant_flags == sorted(relevant_flags, key=lambda r: not r)

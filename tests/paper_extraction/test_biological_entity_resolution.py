import copy

import pytest

from harness.paper_extraction.vendor.skills.skill08_evidence_binding.biological_entity_resolution import (
    BiologicalObjectGraph, compare_biological_context, extract_interventions,
)


def _graph():
    return BiologicalObjectGraph({"paragraphs": [
        {"paragraph_id": "p1", "section": "results", "text": "E. coli K-12 MG1655 and yciT deletion strain were compared with the WT control."},
        {"paragraph_id": "p2", "section": "results", "text": "This mutant grew more slowly on sorbitol."},
        {"paragraph_id": "p3", "section": "results", "text": "The yciT complemented strain restored growth."},
    ]})


def test_graph_records_parent_and_derived_deletion_strain():
    graph = _graph().snapshot()
    mutant = next(e for e in graph["entities"] if e["entity_id"] == "strain:derived:ycit:deletion")
    assert mutant["derived_from"] == "strain:mg1655"
    assert mutant["modifications"] == [{"gene": "ycit", "operation": "deletion"}]


@pytest.mark.parametrize("reference", ["this mutant", "the deletion strain", "the engineered strain"])
def test_unique_local_coreference_resolves_to_deletion_strain(reference):
    result = _graph().resolve(reference, "p2")
    assert result["entity_ids"] == ["strain:derived:ycit:deletion"]
    assert not result["unresolved_references"]


def test_complemented_strain_does_not_resolve_to_deletion_mutant():
    result = compare_biological_context("yciT deletion strain", "The yciT complemented strain restored growth.", _graph(), "p3")
    assert result["status"] == "failed"


def test_parent_strain_does_not_match_mutant_coreference():
    result = compare_biological_context("MG1655", "This mutant grew more slowly.", _graph(), "p2")
    assert result["biological_object_match"] == "failed"


def test_knockout_and_deletion_are_normalized_as_same_operation():
    result = compare_biological_context("yciT knockout strain", "This mutant grew more slowly.", _graph(), "p2")
    assert result["status"] == "passed"
    assert result["intervention_match"] == "passed"


def test_knockout_does_not_match_overexpression():
    result = compare_biological_context("yciT overexpression strain", "This mutant grew more slowly.", _graph(), "p2")
    assert result["status"] == "failed"


def test_control_and_engineered_strain_remain_distinct():
    result = compare_biological_context("MG1655 WT control", "This mutant grew more slowly.", _graph(), "p2")
    assert result["status"] == "failed"


def test_ambiguous_coreference_remains_unresolved():
    graph = BiologicalObjectGraph({"paragraphs": [{"paragraph_id": "p1", "section": "results", "text": "yciT deletion strain and yidZ deletion strain were constructed."}]})
    result = graph.resolve("this mutant", "p1")
    assert result["entity_ids"] == []
    assert result["unresolved_references"]


@pytest.mark.parametrize("text,operation", [
    ("ΔyciT", "deletion"), ("yciT gene disruption", "deletion"),
    ("overexpression of galU", "overexpression"), ("promoter replacement of zwf", "promoter_replacement"),
    ("complemented with yciT", "complementation"), ("transformed with pBAD", "plasmid_introduction"),
])
def test_controlled_intervention_vocabulary(text, operation):
    assert operation in {item["operation"] for item in extract_interventions(text)}


def test_resolution_does_not_mutate_input_document():
    document = {"paragraphs": [{"paragraph_id": "p1", "section": "results", "text": "MG1655 and yciT deletion strain were tested."}]}
    before = copy.deepcopy(document)
    BiologicalObjectGraph(document)
    assert document == before

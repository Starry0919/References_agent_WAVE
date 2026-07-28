"""`evidence_resolution.resolve_evidence_link` must never fabricate a paper
link for a `curated_knowledge` action that doesn't cite one, and must
resolve the one action in the current knowledge base that does (ACT-005 ->
DDR-003) to that DDR record's real citation."""
from __future__ import annotations

from harness.engineering_design import evidence_resolution as er


def test_curated_knowledge_with_ddr_mention_resolves_to_paper():
    resolved = er.resolve_evidence_link("curated_knowledge", "ACT-005", "")
    assert resolved["kind"] == "paper"
    assert resolved["reference_id"] == "DDR-003"
    assert resolved["title"]


def test_curated_knowledge_without_ddr_mention_stays_general_knowledge():
    resolved = er.resolve_evidence_link("curated_knowledge", "ACT-001", "")
    assert resolved["kind"] == "general_knowledge"
    assert resolved["reference_id"] == "ACT-001"
    # the note must be the action's own text, not an invented citation
    assert "not a specific verified experimental result" in resolved["note"]


def test_unknown_action_id_does_not_raise():
    resolved = er.resolve_evidence_link("curated_knowledge", "ACT-999", "")
    assert resolved["kind"] == "unknown"


def test_diagnosis_hypothesis_resolves_without_fabricating_a_paper():
    resolved = er.resolve_evidence_link("diagnosis_hypothesis", "HYP-001", "trpE overexpression relieves feedback inhibition")
    assert resolved["kind"] == "diagnosis_hypothesis"
    assert resolved["reference_id"] == "HYP-001"
    assert resolved["title"] == "trpE overexpression relieves feedback inhibition"


def test_unrecognized_source_type_is_labelled_unknown_not_dropped():
    resolved = er.resolve_evidence_link("some_future_type", "REF-1", "detail text")
    assert resolved["kind"] == "unknown"

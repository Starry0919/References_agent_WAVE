"""Round 2 (老师 §Phase4/§Phase5): Design Decision Provenance closure at the
layer that is actually live end-to-end - DDR -> Rule -> Paper -> Evidence
Grade. `rules_citing_ddr_ids` is the reverse of the already-shipped
`rule_source_ddr_ids` (which walks rule -> DDR); this file covers walking
DDR -> rule, and the `/ddr/{ddr_id}/provenance` endpoint that composes it
with the DDR's own paper citation and evidence grading into one
non-fabricated "why do we believe this" chain.
"""
from __future__ import annotations

from fastapi.testclient import TestClient

from harness.paper_extraction import rule_distillation
from harness.server import create_app


def _client() -> TestClient:
    return TestClient(create_app())


def test_rules_citing_ddr_ids_finds_every_rule_that_cites_a_given_ddr():
    # RULE-001, RULE-004 and RULE-009 all cite DDR-001 in the real rule
    # library (knowledge/biological_rules/rules.json) - a real fixture, not
    # a stand-in, so this would catch a regression in the shipped corpus.
    hits = rule_distillation.rules_citing_ddr_ids(["DDR-001"])
    assert {"RULE-001", "RULE-004", "RULE-009"} <= set(hits)


def test_rules_citing_ddr_ids_is_empty_for_a_ddr_no_rule_cites():
    assert rule_distillation.rules_citing_ddr_ids(["DDR-does-not-exist"]) == []


def test_rules_citing_ddr_ids_of_empty_list_is_empty():
    assert rule_distillation.rules_citing_ddr_ids([]) == []


def test_ddr_provenance_endpoint_returns_the_full_chain_for_a_ddr_with_rules():
    with _client() as client:
        resp = client.get("/api/paper-extraction/ddr/DDR-001/provenance")
        assert resp.status_code == 200, resp.text
        body = resp.json()
        assert body["ddr_id"] == "DDR-001"
        assert body["paper"]["title"]
        assert set(body["rule_ids"]) >= {"RULE-001", "RULE-004"}
        assert len(body["rules"]) == len(body["rule_ids"])
        assert body["rules"][0]["claim_id"] in body["rule_ids"]
        assert body["confidence"] in ("high", "medium", "low")


def test_ddr_provenance_endpoint_404s_for_unknown_ddr():
    with _client() as client:
        resp = client.get("/api/paper-extraction/ddr/DDR-does-not-exist/provenance")
        assert resp.status_code == 404

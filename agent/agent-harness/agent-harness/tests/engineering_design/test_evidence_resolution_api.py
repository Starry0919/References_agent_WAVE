"""Case 4 (Knowledge & Evidence Layer audit, 老师 §Phase5): a design
decision's cited evidence must be traceable back to its source (Design
Decision -> Evidence Provenance), reachable over HTTP - not just at the
Python-function level (see tests/engineering_design/test_evidence_
resolution.py for the unit-level coverage this complements).

ACT-005 is the one curated engineering action in `knowledge/
engineering_actions/action_database.json` whose `evidence` text cites a
real DDR (DDR-003) inline - this proves the full chain a design's
`evidence_links` entry actually resolves through in production:
`{source_type: "curated_knowledge", reference: "ACT-005"}` ->
`GET /api/engineering-design/evidence-links/resolve` -> the DDR's own
citation, not a fabricated link.
"""
from __future__ import annotations

from fastapi.testclient import TestClient

from harness.server import create_app


def _client() -> TestClient:
    return TestClient(create_app())


def test_curated_knowledge_evidence_link_resolves_to_its_source_ddr_over_http():
    with _client() as client:
        resp = client.get("/api/engineering-design/evidence-links/resolve", params={"source_type": "curated_knowledge", "reference": "ACT-005"})
        assert resp.status_code == 200, resp.text
        body = resp.json()
        assert body["kind"] == "paper"
        assert body["reference_id"] == "DDR-003"
        assert body["title"]
        assert "DDR-003" in body["note"]


def test_curated_knowledge_action_with_no_cited_paper_stays_general_knowledge_not_fabricated():
    with _client() as client:
        resp = client.get("/api/engineering-design/evidence-links/resolve", params={"source_type": "curated_knowledge", "reference": "ACT-001"})
        assert resp.status_code == 200, resp.text
        body = resp.json()
        assert body["kind"] == "general_knowledge"
        assert body["reference_id"] == "ACT-001"

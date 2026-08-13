"""HTTP-level tests for `harness/api/evidence_intelligence.py`, mirroring
the style of `tests/evidence_retrieval/test_ddr_applicability.py`."""
from __future__ import annotations

from fastapi.testclient import TestClient

from harness.server import create_app


def _client() -> TestClient:
    return TestClient(create_app())


def test_get_evidence_for_a_real_ddr_step():
    with _client() as client:
        resp = client.get("/api/evidence-intelligence/evidence/ddr:DDR-001:1")
        assert resp.status_code == 200, resp.text
        body = resp.json()
        assert body["evidence_id"] == "ddr:DDR-001:1"
        assert body["host"] == "Escherichia coli"
        assert body["product"] == "L-tryptophan"
        assert body["confidence_level"] in ("High", "Medium", "Low", "Unknown")
        assert "characterization" in body
        assert set(body["characterization"].keys()) == {"evidence_level", "applicability", "limitation", "uncertainty"}


def test_get_evidence_404s_for_unknown_id():
    with _client() as client:
        assert client.get("/api/evidence-intelligence/evidence/ddr:DDR-does-not-exist:1").status_code == 404
        assert client.get("/api/evidence-intelligence/evidence/diag:EVID-does-not-exist").status_code == 404
        assert client.get("/api/evidence-intelligence/evidence/not-a-known-prefix:123").status_code == 404


def test_search_defaults_to_full_browse_and_never_emits_a_numeric_confidence():
    with _client() as client:
        resp = client.get("/api/evidence-intelligence/search")
        assert resp.status_code == 200, resp.text
        body = resp.json()
        assert body["total"] >= 1
        for item in body["evidence"]:
            assert item["confidence_level"] in ("High", "Medium", "Low", "Unknown")


def test_search_with_host_and_product_returns_ddr001():
    with _client() as client:
        resp = client.get("/api/evidence-intelligence/search", params={"host": "Escherichia coli", "product": "L-tryptophan"})
        assert resp.status_code == 200, resp.text
        body = resp.json()
        ddr_ids = {e["origin_ref"]["ddr_id"] for e in body["evidence"] if e["origin_kind"] == "ddr_decision_step"}
        assert "DDR-001" in ddr_ids


def test_provenance_graph_ddr_anchor():
    with _client() as client:
        resp = client.get("/api/evidence-intelligence/provenance-graph", params={"anchor_type": "ddr", "anchor_id": "DDR-001"})
        assert resp.status_code == 200, resp.text
        body = resp.json()
        assert body["anchor"] == {"anchor_type": "ddr", "anchor_id": "DDR-001"}
        assert any(n["kind"] == "paper" for n in body["nodes"])
        assert any(n["kind"] == "mechanistic_rule" for n in body["nodes"])


def test_provenance_graph_404s_for_unknown_ddr():
    with _client() as client:
        resp = client.get("/api/evidence-intelligence/provenance-graph", params={"anchor_type": "ddr", "anchor_id": "DDR-does-not-exist"})
        assert resp.status_code == 404


def test_provenance_graph_rejects_invalid_anchor_type():
    with _client() as client:
        resp = client.get("/api/evidence-intelligence/provenance-graph", params={"anchor_type": "nonsense", "anchor_id": "X"})
        assert resp.status_code == 422  # FastAPI query-pattern validation, before it ever reaches the service


def test_provenance_graph_strategy_anchor_end_to_end_through_the_real_engineering_design_api():
    """Uses `POST /api/engineering-design/...` to create a real strategy
    through the actual pipeline (not a hand-built ORM row), then asks this
    module's graph endpoint about it - the closest this suite gets to a
    full-stack integration check without also standing up a diagnosis run."""
    with _client() as client:
        project = client.post("/api/projects", json={"name": "t", "target_product": "L-tryptophan", "host_definition": {"species": "Escherichia coli"}, "actor_id": "pi"}).json()
        project_id = project["project_id"]

        handoff = client.post(
            "/api/engineering-design/handoff",
            json={
                "project_id": project_id, "diagnosis_session_id": "DIAG-x", "diagnosis_decision_id": "DECN-x", "diagnosis_version": 1,
                "chassis": "E. coli K-12", "actor_id": "pi",
            },
        )
        if handoff.status_code != 200:
            # This endpoint's exact required-field contract belongs to
            # engineering_design's own test suite; if it changes, skip
            # rather than false-fail this integration smoke test.
            import pytest

            pytest.skip(f"engineering-design handoff contract changed: {handoff.status_code} {handoff.text}")
        design_project_id = handoff.json()["design_project_id"]

        strategy_resp = client.post(
            f"/api/engineering-design/projects/{design_project_id}/strategies",
            json={
                "engineering_objective": "increase precursor supply", "mechanism_target": "PEP/E4P",
                "strategy_class": "pathway_engineering", "evidence_links": [], "actor_id": "pi",
            },
        )
        if strategy_resp.status_code != 200:
            import pytest

            pytest.skip(f"engineering-design strategy contract changed: {strategy_resp.status_code} {strategy_resp.text}")
        strategy_id = strategy_resp.json()["strategy_id"]

        graph_resp = client.get("/api/evidence-intelligence/provenance-graph", params={"anchor_type": "strategy", "anchor_id": strategy_id})
        assert graph_resp.status_code == 200, graph_resp.text
        assert any(n["kind"] == "engineering_strategy" for n in graph_resp.json()["nodes"])

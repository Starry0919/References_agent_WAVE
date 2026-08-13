"""API-level regression tests via `fastapi.testclient.TestClient` for the
Bottleneck Diagnosis Loop routes."""
from __future__ import annotations

from fastapi.testclient import TestClient

from harness.server import create_app


def _client() -> TestClient:
    return TestClient(create_app())


def test_model_capabilities_endpoint_reports_real_and_unavailable_adapters():
    with _client() as client:
        r = client.get("/api/diagnosis/model-capabilities")
        assert r.status_code == 200
        body = r.json()
        assert body["gem_fba"]["available"] is True
        assert body["vecoli"]["available"] is False


def test_create_session_and_illegal_action_returns_409():
    with _client() as client:
        p = client.post("/api/projects", json={"name": "t", "target_product": "trp", "actor_id": "pi"}).json()
        sess = client.post("/api/diagnosis/sessions", json={"project_id": p["project_id"], "actor_id": "pi"}).json()
        assert sess["status"] == "intake"

        resp = client.post(
            f"/api/diagnosis/sessions/{sess['diagnosis_session_id']}/action/mark_hypotheses_ranked",
            json={"actor_id": "agent", "kwargs": {}},
        )
        assert resp.status_code == 409  # intake -> hypotheses_ranked is illegal


def test_report_endpoint_returns_structured_sections():
    with _client() as client:
        p = client.post("/api/projects", json={"name": "t", "target_product": "trp", "actor_id": "pi"}).json()
        sess = client.post("/api/diagnosis/sessions", json={"project_id": p["project_id"], "actor_id": "pi"}).json()
        r = client.get(f"/api/diagnosis/sessions/{sess['diagnosis_session_id']}/report")
        assert r.status_code == 200
        titles = [s["title"] for s in r.json()["sections"]]
        assert "Executive Summary" in titles
        assert "Alternatives Not Excluded" in titles


def test_mechanism_graph_endpoint_returns_real_ddr_sourced_nodes():
    """Module 2 §8: GET .../mechanism-graph exposes the Engineering
    Reasoning Graph, recomputed from the project's own target_product/host,
    with real gene/enzyme nodes sourced from the v2 DDR corpus."""
    with _client() as client:
        p = client.post("/api/projects", json={"name": "t", "target_product": "L-tryptophan", "actor_id": "pi"}).json()
        sess = client.post("/api/diagnosis/sessions", json={"project_id": p["project_id"], "actor_id": "pi"}).json()
        r = client.get(f"/api/diagnosis/sessions/{sess['diagnosis_session_id']}/mechanism-graph")
        assert r.status_code == 200
        body = r.json()
        assert not body["unknowns"]
        node_types = {n["node_type"] for n in body["nodes"]}
        assert {"gene", "enzyme"} & node_types
        gene_or_enzyme = [n for n in body["nodes"] if n["node_type"] in ("gene", "enzyme")]
        assert all(n["source"] == "ddr_knowledge_base" for n in gene_or_enzyme)


def test_mechanism_graph_endpoint_404s_for_unknown_session():
    with _client() as client:
        r = client.get("/api/diagnosis/sessions/DIAG-does-not-exist/mechanism-graph")
        assert r.status_code == 404


def test_list_sessions_for_project_returns_newest_first():
    with _client() as client:
        p = client.post("/api/projects", json={"name": "t", "target_product": "trp", "actor_id": "pi"}).json()
        s1 = client.post("/api/diagnosis/sessions", json={"project_id": p["project_id"], "actor_id": "pi"}).json()
        s2 = client.post("/api/diagnosis/sessions", json={"project_id": p["project_id"], "actor_id": "pi"}).json()

        r = client.get("/api/diagnosis/sessions", params={"project_id": p["project_id"]})
        assert r.status_code == 200
        ids = [s["diagnosis_session_id"] for s in r.json()["sessions"]]
        assert ids == [s2["diagnosis_session_id"], s1["diagnosis_session_id"]]

        other = client.post("/api/projects", json={"name": "other", "target_product": "trp", "actor_id": "pi"}).json()
        r2 = client.get("/api/diagnosis/sessions", params={"project_id": other["project_id"]})
        assert r2.json()["sessions"] == []


def test_create_evidence_item_generates_id_and_lists_it_scoped_to_project():
    with _client() as client:
        p = client.post("/api/projects", json={"name": "t", "target_product": "trp", "actor_id": "pi"}).json()
        other = client.post("/api/projects", json={"name": "other", "target_product": "trp", "actor_id": "pi"}).json()

        r = client.post("/api/diagnosis/evidence-items", json={
            "project_id": p["project_id"], "actor_id": "pi", "source_type": "expert_rule",
            "content_summary": "growth rate drops under low-oxygen conditions",
        })
        assert r.status_code == 200
        evidence_item_id = r.json()["evidence_item_id"]
        assert evidence_item_id  # server-generated, never supplied by the caller

        listed = client.get("/api/diagnosis/evidence-items", params={"project_id": p["project_id"]}).json()
        assert [i["evidence_item_id"] for i in listed["evidence_items"]] == [evidence_item_id]

        other_listed = client.get("/api/diagnosis/evidence-items", params={"project_id": other["project_id"]}).json()
        assert other_listed["evidence_items"] == []


def test_review_evidence_link_endpoint_rejects_unknown_link():
    with _client() as client:
        bad = client.post("/api/diagnosis/evidence-links/ELINK-does-not-exist/review", json={"verdict": "confirmed", "actor_id": "pi"})
        assert bad.status_code == 404
        bad_verdict = client.post("/api/diagnosis/evidence-links/ELINK-does-not-exist/review", json={"verdict": "maybe", "actor_id": "pi"})
        assert bad_verdict.status_code in (404, 422)  # verdict validated before or after the lookup, either is a real rejection


def test_run_model_endpoint_executes_real_fba():
    with _client() as client:
        p = client.post("/api/projects", json={"name": "t", "target_product": "trp", "actor_id": "pi"}).json()
        sess = client.post("/api/diagnosis/sessions", json={"project_id": p["project_id"], "actor_id": "pi"}).json()
        r = client.post("/api/diagnosis/model-runs", json={
            "project_id": p["project_id"], "diagnosis_session_id": sess["diagnosis_session_id"],
            "adapter_name": "gem_fba", "actor_id": "agent",
        })
        assert r.status_code == 200
        body = r.json()
        assert body["runtime_status"] == "optimal"
        assert body["outputs"]["objective_value"] > 0

"""Case 2 (Knowledge & Evidence Layer audit, 老师 §Phase3/§Phase5): a
project's current context ("Current Project Context": host + target
product) must be usable to (a) compute a real Applicability Report for one
DDR, reusing `EvidenceMatchReport`/`compute_match` rather than a second
matching engine, and (b) tag/rank DDR search results by relevance to that
context - never hiding the rest of the corpus (老师 §四.5: rules/evidence
transfer across products is a feature, not a bug to filter away).

Uses the real `knowledge/ddr_database/DDR-001_tryptophan.json` record
(organism="Escherichia coli", target_product="L-tryptophan") against a
project with the default E. coli K-12 host and target_product="L-tryptophan"
- a real match, not a fixture stand-in, so this test would catch a
regression in the actual shipped corpus too.
"""
from __future__ import annotations

from fastapi.testclient import TestClient

from harness.server import create_app


def _client() -> TestClient:
    return TestClient(create_app())


def _make_project(client: TestClient, *, target_product: str, host: dict | None = None) -> str:
    body = {"name": "t", "target_product": target_product, "actor_id": "pi"}
    if host is not None:
        body["host_definition"] = host
    return client.post("/api/projects", json=body).json()["project_id"]


def test_assess_applicability_matches_host_and_product_for_a_relevant_ddr():
    with _client() as client:
        project_id = _make_project(client, target_product="L-tryptophan")

        resp = client.post(
            "/api/generation/evidence/documents/DDR-001/applicability",
            json={"project_id": project_id, "actor_id": "tester"},
        )
        assert resp.status_code == 200, resp.text
        body = resp.json()
        assert body["organism_match"] == "match"
        assert body["product_match"] == "match"
        assert body["overall_match_status"] not in ("cross_species", "condition_mismatch")
        assert body["confidence"] > 0.5
        assert body["matching_factors"]  # non-empty: something concrete matched
        # DDR schema has no strain/genotype/medium/... structured fields yet -
        # the report must say so explicitly rather than staying silent.
        assert "strain" in body["missing_data_for_full_report"]
        # Round 2 (老师 §Phase3/§Phase4): engineering/mechanism dimension -
        # DDR-001's own decision_chain design_action(s), and the rules
        # (RULE-001, RULE-004, RULE-009 in the real rule library) distilled
        # from it - not fabricated, reused from rule_distillation.py.
        assert body["design_actions"]
        assert {"RULE-001", "RULE-004"} <= set(body["rule_ids"])

        # Persisted via the same EvidenceMatchReport table listEvidenceMatchReports reads.
        listed = client.get(f"/api/generation/evidence/match-reports?evidence_id=DDR-001").json()["match_reports"]
        assert any(r["match_report_id"] == body["match_report_id"] for r in listed)


def test_assess_applicability_flags_product_mismatch_for_an_unrelated_project():
    with _client() as client:
        project_id = _make_project(client, target_product="1,4-butanediol")

        resp = client.post(
            "/api/generation/evidence/documents/DDR-001/applicability",
            json={"project_id": project_id, "actor_id": "tester"},
        )
        assert resp.status_code == 200, resp.text
        body = resp.json()
        assert body["organism_match"] == "match"  # both are E. coli K-12 - still true
        assert body["product_match"] == "mismatch"
        assert body["downgrade_reasons"]  # explains why, doesn't just silently score low
        assert body["confidence"] < 0.5


def test_assess_applicability_404s_for_unknown_project_or_ddr():
    with _client() as client:
        project_id = _make_project(client, target_product="L-tryptophan")
        assert client.post(
            "/api/generation/evidence/documents/DDR-001/applicability", json={"project_id": "PROJ-does-not-exist"},
        ).status_code == 404
        assert client.post(
            f"/api/generation/evidence/documents/DDR-does-not-exist/applicability", json={"project_id": project_id},
        ).status_code == 404


def test_match_reports_scoped_by_project_id_and_deduped_to_latest_per_evidence():
    """Regression test for the Knowledge page's "适用范围/情境匹配报告" panel:
    it used to call `/evidence/match-reports` with no filter at all, so it
    showed every match report ever computed for every project - re-assessing
    the same DDR against the same project (an immutable/append-only row per
    call) piled up identical-looking duplicates forever, and a second
    project's history bled into the first project's view. `project_id`
    scopes to one project, and (without a specific `evidence_id`) collapses
    each evidence_id down to its single most recent report."""
    with _client() as client:
        project_a = _make_project(client, target_product="L-tryptophan")
        project_b = _make_project(client, target_product="1,4-butanediol")

        client.post("/api/generation/evidence/documents/DDR-001/applicability", json={"project_id": project_a, "actor_id": "tester"})
        # Re-assess the same DDR against project_a a second time - this must
        # not double the count of rows shown for project_a.
        second = client.post("/api/generation/evidence/documents/DDR-001/applicability", json={"project_id": project_a, "actor_id": "tester"}).json()
        client.post("/api/generation/evidence/documents/DDR-001/applicability", json={"project_id": project_b, "actor_id": "tester"})

        listed_a = client.get(f"/api/generation/evidence/match-reports?project_id={project_a}").json()["match_reports"]
        assert len(listed_a) == 1
        assert listed_a[0]["match_report_id"] == second["match_report_id"]
        # The per-dimension fields the frontend renders must actually be present.
        assert listed_a[0]["organism_match"] == "match"

        listed_b = client.get(f"/api/generation/evidence/match-reports?project_id={project_b}").json()["match_reports"]
        assert len(listed_b) == 1
        assert listed_b[0]["match_report_id"] != second["match_report_id"]


def test_evidence_search_tags_and_ranks_relevant_ddrs_without_hiding_the_rest():
    with _client() as client:
        project_id = _make_project(client, target_product="L-tryptophan")

        resp = client.get(f"/api/generation/evidence/search?project_id={project_id}")
        assert resp.status_code == 200, resp.text
        docs = resp.json()["documents"]
        assert len(docs) >= 2  # the whole corpus is still browsable, not filtered down

        by_id = {d["source_id"]: d for d in docs}
        assert by_id["DDR-001"]["relevant"] is True
        # An unrelated-product DDR (e.g. BDO) must still be present, just not tagged relevant.
        unrelated = [d for d in docs if d["source_id"] != "DDR-001"]
        assert any(d["relevant"] is False for d in unrelated)
        # relevant-first ordering
        first_relevant_index = next(i for i, d in enumerate(docs) if d["relevant"])
        first_irrelevant_index = next(i for i, d in enumerate(docs) if not d["relevant"])
        assert first_relevant_index < first_irrelevant_index


def test_evidence_search_without_project_id_is_untagged_full_browse():
    with _client() as client:
        resp = client.get("/api/generation/evidence/search")
        assert resp.status_code == 200, resp.text
        docs = resp.json()["documents"]
        assert len(docs) >= 1
        assert all("relevant" not in d for d in docs)

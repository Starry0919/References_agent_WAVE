"""Case 3 (Knowledge & Evidence Layer audit, 老师 §Phase4): a Knowledge
Claim must represent knowledge distilled across *multiple* DDRs (statement
+ evidence + confidence + boundary), not a single paper's abstract. The
rule library (`knowledge/biological_rules/rules.json`) already is that
aggregation - each rule's `source_ddrs` cites the DDRs it was distilled
from - so `rule_as_knowledge_claim_view` is a read-only reshape of
existing data, not a new schema (老师 §第一阶段: "如果已有实现：不要重复
建设").
"""
from __future__ import annotations

from fastapi.testclient import TestClient

from harness.paper_extraction import rule_distillation
from harness.server import create_app


def _client() -> TestClient:
    return TestClient(create_app())


def _multi_source_rule(**overrides) -> dict:
    rule = {
        "rule_id": "RULE-900",
        "statement": "去调控 committed 酶可提升目标代谢流",
        "trigger_conditions": ["天然产物合成途径", "终端酶过表达不增产"],
        "source_ddrs": ["DDR-001 (Xiong 2021)", "DDR-005 (Chen & Zeng 2018)"],
        "evidence_grading": "硬",
        "applicable_modules": ["M3"],
        "calibration_status": "calibrated",
    }
    rule.update(overrides)
    return rule


def test_rule_with_two_hard_graded_ddrs_is_a_high_confidence_claim():
    claim = rule_distillation.rule_as_knowledge_claim_view(_multi_source_rule())
    assert claim["claim_id"] == "RULE-900"
    assert claim["evidence_ddr_ids"] == ["DDR-001", "DDR-005"]
    assert claim["evidence_count"] == 2
    assert claim["confidence"] == "high"
    assert "机理" not in claim["boundary"] or claim["boundary"]  # boundary is non-empty either way
    assert claim["boundary"]


def test_rule_with_single_source_and_pending_calibration_is_lower_confidence():
    rule = _multi_source_rule(source_ddrs=["DDR-001 (Xiong 2021)"], calibration_status="pending")
    claim = rule_distillation.rule_as_knowledge_claim_view(rule)
    assert claim["evidence_count"] == 1
    assert claim["confidence"] == "medium"  # hard grading alone still lifts it off "low"
    assert "校准" in claim["boundary"]  # explicit pending-calibration caveat, not silently omitted


def test_rule_source_ddrs_that_name_no_real_ddr_record_are_skipped_not_fabricated():
    rule = _multi_source_rule(source_ddrs=["丁醇论文(驱动力规则)", "脂肪酸论文"])
    ids = rule_distillation.rule_source_ddr_ids(rule)
    assert ids == []  # no DDR-\d+ mention in either string - must not invent one


def test_knowledge_claims_api_lists_claims_derived_from_the_real_rule_library():
    with _client() as client:
        resp = client.get("/api/paper-extraction/knowledge-claims")
        assert resp.status_code == 200, resp.text
        body = resp.json()
        assert body["total"] > 0
        claim = body["claims"][0]
        assert set(claim) >= {"claim_id", "statement", "evidence_ddr_ids", "confidence", "boundary"}


def test_knowledge_claims_api_tags_relevance_to_a_project_without_hiding_others():
    with _client() as client:
        project_id = client.post("/api/projects", json={"name": "t", "target_product": "L-tryptophan", "actor_id": "pi"}).json()["project_id"]
        resp = client.get(f"/api/paper-extraction/knowledge-claims?project_id={project_id}")
        assert resp.status_code == 200, resp.text
        claims = resp.json()["claims"]
        assert len(claims) > 1
        assert any(c["relevant"] for c in claims)
        assert any(not c["relevant"] for c in claims)

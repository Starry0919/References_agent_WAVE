import json

from harness.paper_extraction.opus_extractor import make_executor
from harness.paper_extraction.service import build_request
from paper_experimental_design_extraction.config import DEFAULT_CONFIG
from paper_experimental_design_extraction.workflow.engine import WorkflowEngine


def test_all_source_routes_keep_the_same_extraction_requirements():
    common = {"user_request": "提高色氨酸产量", "organism": "Escherichia coli", "strain": "K-12"}
    upload = build_request({**common, "source_type": "upload", "files": ["paper.pdf"]})
    doi = build_request({**common, "source_type": "doi", "doi": ["10.1/example"]})
    auto = build_request({**common, "source_type": "auto_search"})
    assert upload["literature_source"]["type"] == "upload"
    assert doi["literature_source"]["type"] == "doi"
    assert auto["literature_source"]["type"] == "auto_search"
    assert upload["requirements"] == doi["requirements"] == auto["requirements"]
    assert auto["requirements"]["result_level"] == "extract"
    assert auto["requirements"]["article_type_gate_required"] is True


def test_target_system_is_optional_and_k12_is_not_defaulted():
    request = build_request({
        "user_request": "从这本教材中抽取可复用的实验设计思路",
        "source_type": "textbook",
        "files": ["chapter.pdf"],
        "document_kind": "textbook",
    })
    assert request["target_system"] == {"organism": "", "strain": ""}
    assert request["literature_source"]["type"] == "upload"
    assert request["requirements"]["document_kind"] == "textbook"


def test_extraction_plan_skips_k12_dbtl_and_frontend_plan_adapter_by_default():
    request = build_request({
        "user_request": "抽取这篇论文的设计思路",
        "source_type": "upload",
        "files": ["paper.pdf"],
    })
    plan = WorkflowEngine(DEFAULT_CONFIG)._plan(request, {})
    assert "skill07_experiment_extraction" in plan
    assert "skill08_evidence_binding" in plan
    assert "skill09_quality_evaluation" in plan
    assert "skill10_k12_transfer" not in plan
    assert "skill11_engineering_proposal" not in plan
    assert "skill13_frontend_adapter" not in plan


def test_opus_executor_reuses_content_addressed_cache(tmp_path, monkeypatch):
    clean = tmp_path / "paper.json"
    clean.write_text(json.dumps({"paragraphs": [{"paragraph_id": "p1", "text": "x"}]}), encoding="utf-8")
    request = {"clean_document_artifact": {"clean_json_path": str(clean)}}

    import harness.paper_extraction.opus_extractor as module
    monkeypatch.setattr(module, "CACHE_DIR", tmp_path / "cache")
    cache_path = module._cache_path(request, "k3")
    cache_path.parent.mkdir()
    cache_path.write_text(json.dumps({
        "status": "succeeded", "output": {"fields": {}}, "provenance": {},
    }), encoding="utf-8")

    result = make_executor("k3")(request)
    assert result["status"] == "succeeded"
    assert result["provenance"]["cache"]["hit"] is True
    assert result["provenance"]["cache"]["key_type"] == "content_sha256+model+skill_sha256"
    assert result["provenance"]["skill_sha256"]


def test_opus_is_required_not_silently_relabelled(monkeypatch, tmp_path):
    clean = tmp_path / "paper.json"
    clean.write_text('{"paragraphs":[]}', encoding="utf-8")
    monkeypatch.delenv("KIMI_API_KEY", raising=False)
    monkeypatch.delenv("MOONSHOT_API_KEY", raising=False)
    import harness.paper_extraction.opus_extractor as module
    monkeypatch.setattr(module, "CACHE_DIR", tmp_path / "empty-cache")
    result = make_executor("k3")(
        {"clean_document_artifact": {"clean_json_path": str(clean)}}
    )
    assert result["status"] == "terminal_failure"
    assert result["errors"][0]["code"] == "MODEL_NOT_CONFIGURED"
    assert result["provenance"]["model"] == "k3"

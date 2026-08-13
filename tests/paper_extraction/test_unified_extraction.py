import json

from harness.paper_extraction.opus_extractor import make_executor
from harness.paper_extraction.service import build_request
from paper_experimental_design_extraction.config import DEFAULT_CONFIG
from paper_experimental_design_extraction.workflow.engine import WorkflowEngine


def _valid_skill07_output():
    import harness.paper_extraction.opus_extractor as module

    fields = {
        name: {
            "value": None,
            "status": "unknown",
            "applicability_status": "uncertain",
            "confidence": 0.0,
            "extraction_method": "not_applicable",
            "evidence_ids": [],
            "notes": "Not reported in the available document.",
            "inference": None,
        }
        for name in module._core_fields()
    }
    return {
        "contract_version": "skill07_semantic_contract_v1",
        "fields": fields,
        "experimental_design_object": {},
        "field_metadata": {
            name: {"source_locations": [], "evidence_role": "candidate"}
            for name in fields
        },
        "extensions": {
            "article_type_gate": {
                "article_type": "primary_research",
                "contains_original_experiment": True,
                "classification_evidence": ["p1"],
            },
            "document_coverage": {"available_sections": []},
            "paper_target_strains": [],
            "user_target_system": None,
        },
        "conflicts": [],
    }


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


def test_task_manager_worker_count_is_configurable(monkeypatch):
    from paper_experimental_design_extraction.api.task_manager import TaskManager

    monkeypatch.setenv("PAPER_EXTRACTION_TASK_WORKERS", "4")
    manager = TaskManager()
    try:
        assert manager.max_workers == 4
    finally:
        manager.pool.shutdown(wait=False, cancel_futures=True)


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
    clean.write_text(json.dumps({"paragraphs": [{"paragraph_id": "p1", "section": "Results", "text": "We cultured engineered E. coli in M9 glucose for 24 h and measured product titer."}]}), encoding="utf-8")
    request = {"clean_document_artifact": {"clean_json_path": str(clean)}}

    import harness.paper_extraction.opus_extractor as module
    monkeypatch.setattr(module, "CACHE_DIR", tmp_path / "cache")
    cache_path = module._cache_path(request, "k3")
    cache_path.parent.mkdir()
    cache_path.write_text(json.dumps({
        "status": "succeeded", "output": _valid_skill07_output(), "provenance": {},
    }), encoding="utf-8")

    result = make_executor("k3")(request)
    assert result["status"] == "succeeded"
    assert result["provenance"]["cache"]["hit"] is True
    assert result["provenance"]["cache"]["key_type"] == (
        "content_sha256+model+skill_sha256+system_prompt_sha256+"
        "schema_sha256+semantic_contract_sha256+validation_rules_sha256+"
        "runtime_contract_version+validator_version"
    )
    assert result["provenance"]["skill_sha256"]
    assert result["provenance"]["system_prompt_sha256"]
    assert result["provenance"]["semantic_contract_version"] == "skill07_semantic_contract_v1"
    assert result["provenance"]["validation_rules_version"] == "skill07_validation_rules_v1"


def test_system_prompt_is_externalized_and_part_of_cache_identity(tmp_path, monkeypatch):
    clean = tmp_path / "paper.json"
    clean.write_text('{"paragraphs":[]}', encoding="utf-8")
    request = {"clean_document_artifact": {"clean_json_path": str(clean)}}

    import harness.paper_extraction.opus_extractor as module
    first_prompt = tmp_path / "prompt-v1.md"
    second_prompt = tmp_path / "prompt-v2.md"
    first_prompt.write_text("system prompt version one", encoding="utf-8")
    second_prompt.write_text("system prompt version two", encoding="utf-8")

    monkeypatch.setattr(module, "SYSTEM_PROMPT_PATH", first_prompt)
    first_cache_path = module._cache_path(request, "test-model")
    assert module._system_prompt() == "system prompt version one"

    monkeypatch.setattr(module, "SYSTEM_PROMPT_PATH", second_prompt)
    second_cache_path = module._cache_path(request, "test-model")
    assert first_cache_path != second_cache_path


def test_schema_is_part_of_cache_identity(tmp_path, monkeypatch):
    clean = tmp_path / "paper.json"
    clean.write_text('{"paragraphs":[{"paragraph_id":"p1","section":"Results","text":"We cultured engineered E. coli in M9 glucose for 24 h and measured product titer."}]}', encoding="utf-8")
    request = {"clean_document_artifact": {"clean_json_path": str(clean)}}

    import harness.paper_extraction.opus_extractor as module
    original = module._output_schema()
    first_schema = tmp_path / "schema-v1.json"
    second_schema = tmp_path / "schema-v2.json"
    first_schema.write_text(json.dumps(original), encoding="utf-8")
    original["title"] = "changed contract"
    second_schema.write_text(json.dumps(original), encoding="utf-8")

    monkeypatch.setattr(module, "OUTPUT_SCHEMA_PATH", first_schema)
    first_cache_path = module._cache_path(request, "test-model")
    monkeypatch.setattr(module, "OUTPUT_SCHEMA_PATH", second_schema)
    second_cache_path = module._cache_path(request, "test-model")

    assert first_cache_path != second_cache_path


def test_missing_poe_code_cli_is_reported_without_relabelling_model(monkeypatch, tmp_path):
    clean = tmp_path / "paper.json"
    clean.write_text('{"paragraphs":[{"paragraph_id":"p1","section":"Results","text":"We cultured engineered E. coli in M9 glucose for 24 h and measured product titer."}]}', encoding="utf-8")
    monkeypatch.setenv("POE_CODE_CLI_DIR", str(tmp_path / "missing-cli"))
    import harness.paper_extraction.opus_extractor as module
    monkeypatch.setattr(module, "CACHE_DIR", tmp_path / "empty-cache")
    result = make_executor("claude-sonnet-4.6")(
        {"clean_document_artifact": {"clean_json_path": str(clean)}}
    )
    assert result["status"] == "terminal_failure"
    assert result["errors"][0]["code"] == "MODEL_NOT_CONFIGURED"
    assert result["provenance"]["model"] == "claude-sonnet-4.6"
    assert result["provenance"]["extractor"] == "poe_code_cli"


def test_extraction_uses_poe_code_cli(monkeypatch, tmp_path):
    clean = tmp_path / "paper.json"
    clean.write_text('{"paragraphs":[{"paragraph_id":"p1","section":"Results","text":"We cultured engineered E. coli in M9 glucose for 24 h and measured product titer."}]}', encoding="utf-8")
    import harness.paper_extraction.opus_extractor as module
    monkeypatch.setattr(module, "CACHE_DIR", tmp_path / "empty-cache")
    monkeypatch.setattr(module, "_poe_cli_configuration_error", lambda: None)
    monkeypatch.setattr(
        module,
        "_call_poe_code_cli",
        lambda model, prompt: (
            _valid_skill07_output(),
            model,
            {},
            None,
        ),
    )

    result = make_executor("claude-sonnet-4.6")(
        {"clean_document_artifact": {"clean_json_path": str(clean)}}
    )

    assert result["status"] == "succeeded"
    assert result["provenance"]["extractor"] == "poe_code_cli"
    assert result["provenance"]["model"] == "claude-sonnet-4.6"
    assert result["self_check"]["checks"]
    assert result["eligible_for_evidence_verification"] is True


def test_invalid_empty_fields_are_not_legalized_or_cached(monkeypatch, tmp_path):
    clean = tmp_path / "paper.json"
    clean.write_text('{"paragraphs":[{"paragraph_id":"p1","section":"Results","text":"We cultured engineered E. coli in M9 glucose for 24 h and measured product titer."}]}', encoding="utf-8")
    import harness.paper_extraction.opus_extractor as module
    monkeypatch.setattr(module, "CACHE_DIR", tmp_path / "empty-cache")
    monkeypatch.setattr(module, "_SKILL07_SCHEMA_REPAIR_ATTEMPTS", 0)
    monkeypatch.setattr(module, "_poe_cli_configuration_error", lambda: None)
    monkeypatch.setattr(
        module,
        "_call_poe_code_cli",
        lambda model, prompt: (
            {
                "fields": {},
                "experimental_design_object": {},
                "field_metadata": {},
                "extensions": {"article_type_gate": {"article_type": "primary_research"}},
                "conflicts": [],
            },
            model,
            {},
            None,
        ),
    )

    request = {"clean_document_artifact": {"clean_json_path": str(clean)}}
    result = make_executor("claude-sonnet-4.6")(request)

    assert result["status"] == "needs_review"
    assert result["eligible_for_evidence_verification"] is False
    assert result["self_check"]["failed"] > 0
    assert result["output"]["fields"] == {}
    assert not module._cache_path(request, "claude-sonnet-4.6").exists()


def test_invalid_cached_output_is_revalidated_and_reextracted(monkeypatch, tmp_path):
    clean = tmp_path / "paper.json"
    clean.write_text('{"paragraphs":[{"paragraph_id":"p1","section":"Results","text":"We cultured engineered E. coli in M9 glucose for 24 h and measured product titer."}]}', encoding="utf-8")
    request = {"clean_document_artifact": {"clean_json_path": str(clean)}}
    import harness.paper_extraction.opus_extractor as module
    monkeypatch.setattr(module, "CACHE_DIR", tmp_path / "cache")
    cache_path = module._cache_path(request, "claude-sonnet-4.6")
    cache_path.parent.mkdir()
    cache_path.write_text(json.dumps({
        "status": "succeeded",
        "output": {"fields": {}},
        "provenance": {},
    }), encoding="utf-8")
    calls = []
    monkeypatch.setattr(module, "_poe_cli_configuration_error", lambda: None)
    monkeypatch.setattr(module, "_call_poe_code_cli", lambda model, prompt: (
        calls.append(prompt) or _valid_skill07_output(), model, {}, None,
    ))

    result = make_executor("claude-sonnet-4.6")(request)

    assert calls
    assert result["status"] == "succeeded"
    assert result["provenance"]["cache"]["hit"] is False


def test_reported_field_without_evidence_fails_semantic_gate():
    import harness.paper_extraction.opus_extractor as module
    output = _valid_skill07_output()
    output["fields"]["objective"].update({
        "value": "Increase production", "status": "reported", "confidence": 0.9,
        "extraction_method": "direct_quote",
    })
    checks = module.validate_skill07_output(
        output,
        {"paragraphs": [{"paragraph_id": "p1", "text": "Increase production"}]},
    )

    semantic = next(check for check in checks if check["name"] == "field_semantic_invariants")
    assert semantic["passed"] is False


def test_poe_code_cli_parser_uses_the_last_complete_result():
    import harness.paper_extraction.opus_extractor as module

    stdout = (
        f"{module._CLI_RESULT_BEGIN}\n{{\"stale\": true}}\n{module._CLI_RESULT_END}\n"
        f"● {module._CLI_RESULT_BEGIN}\n"
        "│ Here is the requested object:\n"
        "│ ```json\n"
        "│ {\"fre\n"
        "│ sh\": true}\n"
        "│ ```\n"
        f"│ {module._CLI_RESULT_END}\n"
    )
    assert module._parse_cli_result(stdout) == {"fresh": True}


def test_poe_code_cli_recovers_result_written_before_transport_exit(monkeypatch, tmp_path):
    import subprocess
    import harness.paper_extraction.opus_extractor as module

    cli_dir = tmp_path / "cli"
    (cli_dir / ".runtime" / "node_modules" / "poe-code" / "dist").mkdir(parents=True)
    (cli_dir / "launcher.mjs").write_text("", encoding="utf-8")
    (cli_dir / ".runtime" / "node_modules" / "poe-code" / "dist" / "bin.cjs").write_text("", encoding="utf-8")
    monkeypatch.setattr(module, "_poe_cli_dir", lambda: cli_dir)
    monkeypatch.setattr(module, "_poe_node_command", lambda: "node")
    monkeypatch.setenv("POE_API_KEY", "test-key")

    expected = {"fields": {}, "experimental_design_object": {}, "extensions": {}}

    def fake_run(command, **kwargs):
        workspace = command[command.index("--cwd") + 1]
        (module.Path(workspace) / "result.json").write_text(json.dumps(expected), encoding="utf-8")
        return subprocess.CompletedProcess(command, 1, stdout="", stderr="TypeError: terminated")

    monkeypatch.setattr(module.subprocess, "run", fake_run)

    output, _, _, error = module._call_poe_code_cli("kimi-k3", {"document": {}})

    assert error is None
    assert output == expected

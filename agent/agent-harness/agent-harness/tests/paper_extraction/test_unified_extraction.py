import json
from types import SimpleNamespace

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
    assert result["provenance"]["cache"]["key_type"] == "prompt+full_markdown+model_sha256"
    assert result["provenance"]["skill_sha256"]


def test_missing_poe_code_cli_is_reported_without_relabelling_model(monkeypatch, tmp_path):
    clean = tmp_path / "paper.json"
    clean.write_text('{"paragraphs":[]}', encoding="utf-8")
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
    clean.write_text('{"paragraphs":[]}', encoding="utf-8")
    import harness.paper_extraction.opus_extractor as module
    monkeypatch.setattr(module, "CACHE_DIR", tmp_path / "empty-cache")
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

    result = make_executor("claude-sonnet-4.6")(
        {"clean_document_artifact": {"clean_json_path": str(clean)}}
    )

    assert result["status"] == "succeeded"
    assert result["provenance"]["extractor"] == "poe_code_cli"
    assert result["provenance"]["model"] == "claude-sonnet-4.6"
    assert set(result["output"]["fields"]) == set(module._CORE_FIELDS)
    assert all(
        field["status"] == "unknown"
        for field in result["output"]["fields"].values()
    )


def test_compact_model_aliases_are_normalized_for_downstream_skills():
    import harness.paper_extraction.opus_extractor as module

    output = module._normalize_skill07_output({
        "fields": {
            "objective": {
                "value": "increase tryptophan production",
                "status": "reported",
                "confidence": 0.9,
                "extraction_method": "full_text",
                "evidence_ids": ["document_p001"],
                "notes": "",
            },
        },
        "experimental_design_object": [{"experiment_id": "exp1"}],
        "field_metadata": {},
        "extensions": {
            "article_type": {
                "article_type": "primary_research",
                "confidence": 0.95,
            },
        },
        "conflicts": [],
    })

    assert output["extensions"]["article_type_gate"]["article_type"] == "primary_research"
    assert output["experimental_design_object"] == {
        "experiments": [{"experiment_id": "exp1"}]
    }
    assert output["fields"]["objective"]["status"] == "reported"
    assert output["fields"]["hypothesis"]["status"] == "unknown"


def test_evidence_validator_accepts_anchored_paraphrase_but_rejects_wrong_number():
    from harness.paper_extraction.vendor.skills.skill08_evidence_binding.binder.evidence_validator import (
        supports_value,
    )

    quote = (
        "KW023 efficiently produced 39.7 g/L of l-trp with a conversion "
        "rate of 16.7% and a productivity of 1.6 g/L/h in a 5 L fed-batch "
        "fermentation system."
    )
    supported, unsupported = supports_value(
        "KW023 produced 39.7 g/L l-trp at 16.7% conversion and 1.6 g/L/h "
        "productivity in 5 L fed-batch fermentation",
        [quote],
    )
    wrong_number, _ = supports_value(
        "KW023 produced 49.7 g/L l-trp at 16.7% conversion",
        [quote],
    )

    assert supported is True
    assert unsupported == []
    assert wrong_number is False


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


def test_skill07_prompt_includes_complete_clean_markdown(tmp_path):
    import harness.paper_extraction.opus_extractor as module

    clean_json = tmp_path / "clean_document.json"
    clean_markdown = tmp_path / "clean_document.md"
    full_text = "Title\n\nMethods\nThe complete unheaded paper body survives here."
    clean_json.write_text(
        json.dumps(
            {
                "sections": [
                    {
                        "id": "document",
                        "title": "Paper",
                        "level": 1,
                        "content": full_text,
                        "is_fallback": True,
                    }
                ],
                "paragraphs": [
                    {
                        "paragraph_id": "document_p001",
                        "section": "document",
                        "text": full_text,
                    }
                ],
                "figures": [{"figure_id": "fig-1"}],
            }
        ),
        encoding="utf-8",
    )
    clean_markdown.write_text(full_text, encoding="utf-8")
    request = {
        "clean_document_artifact": {
            "clean_json_path": str(clean_json),
            "clean_markdown_path": str(clean_markdown),
        }
    }

    prompt = module._build_prompt(request)

    assert prompt["document"]["sections"][0].get("content") is None
    assert prompt["document"]["paragraphs"] == [
        {"paragraph_id": "document_p001", "section": "document"}
    ]
    assert prompt["document"]["figures"] == [{"figure_id": "fig-1"}]
    assert prompt["clean_document_markdown"] == (
        "<!-- paragraph_id: document_p001 -->\n" + full_text
    )
    serialized = json.dumps(prompt, ensure_ascii=False)
    encoded_full_text = json.dumps(full_text, ensure_ascii=False)[1:-1]
    assert serialized.count(encoded_full_text) == 1


def test_skill07_keeps_unmatched_paragraph_text_as_safe_fallback(tmp_path):
    import harness.paper_extraction.opus_extractor as module

    clean_json = tmp_path / "clean_document.json"
    clean_markdown = tmp_path / "clean_document.md"
    clean_json.write_text(
        json.dumps(
            {
                "paragraphs": [
                    {
                        "paragraph_id": "p_unmatched",
                        "section": "methods",
                        "text": "text absent from markdown",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    clean_markdown.write_text("available complete body", encoding="utf-8")

    prompt = module._build_prompt(
        {
            "clean_document_artifact": {
                "clean_json_path": str(clean_json),
                "clean_markdown_path": str(clean_markdown),
            }
        }
    )

    assert prompt["document"]["paragraphs"][0]["text"] == "text absent from markdown"
    assert prompt["clean_document_markdown"] == "available complete body"


def test_cache_key_changes_with_markdown_and_prompt_protocol(tmp_path, monkeypatch):
    import harness.paper_extraction.opus_extractor as module

    monkeypatch.setattr(module, "CACHE_DIR", tmp_path / "cache")
    clean_json = tmp_path / "clean_document.json"
    clean_markdown = tmp_path / "clean_document.md"
    clean_json.write_text('{"paragraphs":[]}', encoding="utf-8")
    clean_markdown.write_text("first full text", encoding="utf-8")
    request = {
        "clean_document_artifact": {
            "clean_json_path": str(clean_json),
            "clean_markdown_path": str(clean_markdown),
        }
    }

    first = module._cache_path(request, "claude-sonnet-4.6")
    clean_markdown.write_text("changed full text", encoding="utf-8")
    second = module._cache_path(request, "claude-sonnet-4.6")
    monkeypatch.setattr(module, "_PROMPT_PROTOCOL_VERSION", "test-next-prompt")
    third = module._cache_path(request, "claude-sonnet-4.6")

    assert first != second
    assert second != third


def test_poe_cli_retries_rate_limit_and_interrupted_stream_with_restricted_plugins(
    tmp_path, monkeypatch
):
    import harness.paper_extraction.opus_extractor as module

    cli_dir = tmp_path / ".poe-code-cli"
    cli_dir.mkdir()
    (cli_dir / "launcher.mjs").write_text("// test", encoding="utf-8")
    monkeypatch.setattr(module, "_REPO_ROOT", tmp_path)
    monkeypatch.setattr(module, "_poe_cli_dir", lambda: cli_dir)
    monkeypatch.setattr(module, "_poe_node_command", lambda: "node")
    monkeypatch.setattr(module, "_poe_cli_configuration_error", lambda: None)
    monkeypatch.setattr(module, "_POE_MAX_ATTEMPTS", 3)
    monkeypatch.setattr(module, "_POE_RATE_LIMIT_BACKOFF_S", 7.0)
    monkeypatch.setattr(module, "_POE_FALLBACK_MODEL", "openai/gpt-5-mini")

    calls = []
    configs = []

    def fake_run(command, **_kwargs):
        calls.append(command)
        workspace = tmp_path / command[command.index("--cwd") + 1]
        prompt_text = (workspace / "prompt.txt").read_text(encoding="utf-8")
        assert "command='overwrite'" in prompt_text
        assert "file_text set to the complete final JSON string" in prompt_text
        configs.append(
            json.loads(
                (workspace / ".poe-code" / "config.json").read_text(
                    encoding="utf-8"
                )
            )
        )
        if len(calls) == 1:
            return SimpleNamespace(
                returncode=1,
                stdout="",
                stderr="Rate limit exceeded, please try again later",
            )
        if len(calls) == 2:
            return SimpleNamespace(
                returncode=1,
                stdout="",
                stderr="TypeError: terminated at Fetch.onAborted",
            )
        return SimpleNamespace(
            returncode=0,
            stdout=(
                f"{module._CLI_RESULT_BEGIN}\n"
                '{"fields": {}}\n'
                f"{module._CLI_RESULT_END}\n"
            ),
            stderr="",
        )

    sleeps = []
    monkeypatch.setattr(module.subprocess, "run", fake_run)
    monkeypatch.setattr(module.time, "sleep", sleeps.append)

    output, model, _usage, error = module._call_poe_code_cli(
        "claude-sonnet-4.6", {"document": {}, "clean_document_markdown": "body"}
    )

    assert output == {"fields": {}}
    assert model == "openai/gpt-5-mini"
    assert error is None
    assert len(calls) == 3
    assert sleeps == [7.0, 14.0]
    assert [call[call.index("--model") + 1] for call in calls] == [
        "claude-sonnet-4.6",
        "openai/gpt-5-mini",
        "openai/gpt-5-mini",
    ]
    plugin_names = [item["name"] for item in configs[0]["agent"]["plugins"]]
    assert plugin_names == [
        "openai-responses",
        "openai-chat-completions",
        "system-prompt",
        "files",
        "policy",
    ]
    assert "web" not in plugin_names
    assert "shell" not in plugin_names
    assert configs[0]["agent"]["plugins"][-1]["options"]["mode"] == "edit"


def test_exhausted_rate_limit_is_a_real_retryable_failure(monkeypatch, tmp_path):
    import harness.paper_extraction.opus_extractor as module

    clean = tmp_path / "paper.json"
    clean.write_text('{"paragraphs":[]}', encoding="utf-8")
    monkeypatch.setattr(module, "CACHE_DIR", tmp_path / "empty-cache")
    monkeypatch.setattr(module, "_poe_cli_configuration_error", lambda: None)
    monkeypatch.setattr(
        module,
        "_call_poe_code_cli",
        lambda model, prompt: (
            None,
            model,
            {"model_iterations": 9, "tool_calls": 8},
            module.PoeCliFailure(
                "POE_RATE_LIMITED", "shared quota exhausted", True, attempts=2
            ),
        ),
    )

    result = make_executor("claude-sonnet-4.6")(
        {"clean_document_artifact": {"clean_json_path": str(clean)}}
    )

    assert result["status"] == "retryable_failure"
    assert result["errors"][0]["code"] == "POE_RATE_LIMITED"
    assert result["errors"][0]["category"] == "rate_limit"
    assert result["errors"][0]["context"]["attempts"] == 2
    assert result["metrics"]["attempts"] == 2


def test_poe_cli_failure_codes_distinguish_quota_auth_and_generic_errors():
    import harness.paper_extraction.opus_extractor as module

    limited = module._classify_cli_failure(
        "Request failed with status code 429", returncode=1, attempts=2
    )
    unauthorized = module._classify_cli_failure(
        "HTTP 401 Unauthorized", returncode=1, attempts=1
    )
    interrupted = module._classify_cli_failure(
        "provider connection closed", returncode=1, attempts=1
    )
    generic = module._classify_cli_failure(
        "unrecognized provider failure", returncode=1, attempts=1
    )

    assert (limited.code, limited.retryable, limited.attempts) == (
        "POE_RATE_LIMITED",
        True,
        2,
    )
    assert (unauthorized.code, unauthorized.retryable) == (
        "POE_AUTH_FAILED",
        False,
    )
    assert (interrupted.code, interrupted.retryable) == (
        "POE_NETWORK_INTERRUPTED",
        True,
    )
    assert (generic.code, generic.retryable) == ("POE_CLI_FAILED", False)


def test_cli_usage_reports_last_context_and_tool_growth():
    import harness.paper_extraction.opus_extractor as module

    usage = module._parse_cli_usage(
        "· tokens: 47,161 in → 108 out\n"
        "  → exec: fetch_url\n"
        "· tokens: 52,056 in (47,160 cached) → 192 out\n"
        "  → exec: search_web\n"
        "· tokens: 61,072 in (60,793 cached) → 106 out\n"
    )

    assert usage == {
        "input_tokens": 61072,
        "output_tokens": 106,
        "cached_input_tokens": 60793,
        "model_iterations": 3,
        "tool_calls": 2,
    }

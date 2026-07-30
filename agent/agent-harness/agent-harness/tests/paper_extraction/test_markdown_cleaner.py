from __future__ import annotations

import sys
from pathlib import Path

import harness.paper_extraction
from harness.paper_extraction import pipeline_cache

_SKILLS_ROOT = Path(harness.paper_extraction.__file__).resolve().parent / "vendor" / "skills"
if str(_SKILLS_ROOT) not in sys.path:
    sys.path.insert(0, str(_SKILLS_ROOT))

from skill06_markdown_cleaner.cleaners.citation_preserver import extract_citations
from skill06_markdown_cleaner.json_builder import build_clean_json
from skill06_markdown_cleaner.schema import SKILL_VERSION
from skill06_markdown_cleaner.skill import ScientificMarkdownCleaner


def test_author_year_citation_ignores_equivalent_line_break_spacing():
    original = "Prior work (Kerek et al., \n2023) supports this conclusion."
    normalized = "Prior work (Kerek et al.,\n2023) supports this conclusion."

    assert extract_citations(original) == extract_citations(normalized)


def test_headingless_markdown_retains_body_in_fallback_section_and_paragraphs():
    markdown = (
        "<!-- page:1 -->\n\n"
        "Abstract\n\n"
        "Strain KW023 produced 39.7 g/L tryptophan.\n\n"
        "<!-- page:2 -->\n\n"
        "Materials and methods\n\n"
        "Cells were evaluated in fed-batch fermentation."
    )

    document = build_clean_json(markdown, {"title": None}, [])

    assert document["sections"] == [{
        "id": "document",
        "title": "Unsectioned document",
        "level": 1,
        "content": markdown,
        "is_fallback": True,
    }]
    assert [item["paragraph_id"] for item in document["paragraphs"]] == [
        "document_p001",
        "document_p002",
        "document_p003",
        "document_p004",
    ]
    assert [item["text"] for item in document["paragraphs"]] == [
        "Abstract",
        "Strain KW023 produced 39.7 g/L tryptophan.",
        "Materials and methods",
        "Cells were evaluated in fed-batch fermentation.",
    ]
    assert all(item["section"] == "document" for item in document["paragraphs"])


def test_markdown_headings_keep_existing_sectioning_behavior():
    markdown = "# Introduction\n\nFirst paragraph.\n\n# Methods\n\nSecond paragraph."

    document = build_clean_json(markdown, {"title": "Ignored"}, [])

    assert document["sections"] == [
        {"id": "introduction", "title": "Introduction", "level": 1, "content": "First paragraph."},
        {"id": "methods", "title": "Methods", "level": 1, "content": "Second paragraph."},
    ]
    assert document["paragraphs"] == [
        {"paragraph_id": "introduction_p001", "text": "First paragraph.", "section": "introduction"},
        {"paragraph_id": "methods_p001", "text": "Second paragraph.", "section": "methods"},
    ]


def test_cleaner_headingless_fallback_remains_warning_but_is_usable(tmp_path):
    markdown = "Abstract\n\nStrain KW023 produced 39.7 g/L tryptophan."
    cleaner = ScientificMarkdownCleaner(output_root=tmp_path, logger=lambda _: None)

    result = cleaner.execute({
        "document_artifact": {
            "document_metadata": {
                "paper_id": "paper-headingless",
                "title": None,
                "parser": "PyMuPDF",
                "parser_version": "test",
            },
            "markdown_artifact": {"markdown_content": markdown},
            "structure_map": {"sections": []},
        }
    })

    assert result["status"] == "succeeded_with_warnings"
    assert result["warnings"][0]["code"] == "CLEAN002"
    clean_document = result["output"]["clean_document_artifact"]
    assert clean_document["cleaning_quality_report"]["fallback_structure_used"] is True
    assert clean_document["structure_map"]["sections"][0]["is_fallback"] is True
    assert [item["text"] for item in clean_document["structure_map"]["paragraphs"]] == [
        "Abstract",
        "Strain KW023 produced 39.7 g/L tryptophan.",
    ]


def test_skill_version_bump_invalidates_cached_empty_paragraph_result(tmp_path, monkeypatch):
    monkeypatch.setattr(pipeline_cache, "CACHE_ROOT", tmp_path)
    calls = {"old": 0, "new": 0}

    def old_execute(_request):
        calls["old"] += 1
        return {
            "status": "succeeded",
            "output": {"clean_document_artifact": {"structure_map": {"paragraphs": []}}},
        }

    monkeypatch.setattr(
        pipeline_cache,
        "_load_real_executor",
        lambda _skill_name: (old_execute, "0.3.0"),
    )
    old_cached_executor = pipeline_cache.make_cached_executor(
        "skill06_markdown_cleaner",
        lambda _request: "same-document",
    )
    assert old_cached_executor({})["output"]["clean_document_artifact"]["structure_map"]["paragraphs"] == []
    assert old_cached_executor({})["provenance"]["cache"]["hit"] is True
    assert calls["old"] == 1

    def new_execute(_request):
        calls["new"] += 1
        return {
            "status": "succeeded",
            "output": {
                "clean_document_artifact": {
                    "structure_map": {
                        "paragraphs": [{"paragraph_id": "document_p001", "text": "body"}],
                    }
                }
            },
        }

    assert SKILL_VERSION == "0.3.1"
    monkeypatch.setattr(
        pipeline_cache,
        "_load_real_executor",
        lambda _skill_name: (new_execute, SKILL_VERSION),
    )
    new_cached_executor = pipeline_cache.make_cached_executor(
        "skill06_markdown_cleaner",
        lambda _request: "same-document",
    )
    result = new_cached_executor({})

    assert calls["new"] == 1
    assert result["output"]["clean_document_artifact"]["structure_map"]["paragraphs"] == [
        {"paragraph_id": "document_p001", "text": "body"}
    ]
    assert len(list((tmp_path / "skill06_markdown_cleaner").glob("*.json"))) == 2

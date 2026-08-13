"""Offline, no-network contract tests for harness/translation/service.py,
using the same FakeStructuredGenerationClient double every other LLM
adapter's tests use."""
from __future__ import annotations

import json

from harness.translation import service
from tests.llm_generation.fakes import FakeStructuredGenerationClient


def test_non_latin_text_skips_the_llm_entirely(tmp_path, monkeypatch):
    monkeypatch.setattr(service, "CACHE_DIR", tmp_path / "cache")
    fake = FakeStructuredGenerationClient(scripted_contents=[json.dumps({"translations": ["unused"]})])

    result = service.translate_batch(["已经是中文", "", "42.0"], client=fake)

    assert result == ["已经是中文", "", "42.0"]
    assert fake.call_count == 0


def test_english_text_is_translated_and_cached(tmp_path, monkeypatch):
    monkeypatch.setattr(service, "CACHE_DIR", tmp_path / "cache")
    fake = FakeStructuredGenerationClient(scripted_contents=[json.dumps({"translations": ["你好世界"]})])

    first = service.translate_batch(["Hello world"], client=fake)
    assert first == ["你好世界"]
    assert fake.call_count == 1

    # Second call for the same text is a pure cache hit - no further LLM call.
    second = service.translate_batch(["Hello world"], client=fake)
    assert second == ["你好世界"]
    assert fake.call_count == 1


def test_provider_error_falls_back_to_original_text(tmp_path, monkeypatch):
    monkeypatch.setattr(service, "CACHE_DIR", tmp_path / "cache")
    fake = FakeStructuredGenerationClient(scripted_contents=[None], available=False, unavailable_reason="simulated outage")

    result = service.translate_batch(["Hello world"], client=fake)

    assert result == ["Hello world"]


def test_schema_invalid_output_falls_back_to_original_text(tmp_path, monkeypatch):
    monkeypatch.setattr(service, "CACHE_DIR", tmp_path / "cache")
    fake = FakeStructuredGenerationClient(scripted_contents=["not json at all {{{"] * 3)

    result = service.translate_batch(["Hello world"], client=fake)

    assert result == ["Hello world"]


def test_translate_text_convenience_wrapper(tmp_path, monkeypatch):
    monkeypatch.setattr(service, "CACHE_DIR", tmp_path / "cache")
    fake = FakeStructuredGenerationClient(scripted_contents=[json.dumps({"translations": ["你好"]})])

    assert service.translate_text("Hello", client=fake) == "你好"


def test_already_english_text_skips_the_llm_when_target_is_en_us(tmp_path, monkeypatch):
    """Symmetric direction: translating *to* en-US skips text with no CJK
    characters left to translate, mirroring the zh-CN-target skip above."""
    monkeypatch.setattr(service, "CACHE_DIR", tmp_path / "cache")
    fake = FakeStructuredGenerationClient(scripted_contents=[json.dumps({"translations": ["unused"]})])

    result = service.translate_batch(["Already English", "", "42.0"], target_locale="en-US", client=fake)

    assert result == ["Already English", "", "42.0"]
    assert fake.call_count == 0


def test_chinese_text_is_translated_to_english_and_cached(tmp_path, monkeypatch):
    monkeypatch.setattr(service, "CACHE_DIR", tmp_path / "cache")
    fake = FakeStructuredGenerationClient(scripted_contents=[json.dumps({"translations": ["Hello world"]})])

    first = service.translate_batch(["你好世界"], target_locale="en-US", client=fake)
    assert first == ["Hello world"]
    assert fake.call_count == 1

    # Second call for the same text/target is a pure cache hit - no further LLM call.
    second = service.translate_batch(["你好世界"], target_locale="en-US", client=fake)
    assert second == ["Hello world"]
    assert fake.call_count == 1


def test_same_text_caches_independently_per_target_locale(tmp_path, monkeypatch):
    """A Chinese string that needs no translation for zh-CN but does for
    en-US (and vice versa) must not share one cache entry across the two
    directions - `_cache_path` includes `target_locale` for exactly this."""
    monkeypatch.setattr(service, "CACHE_DIR", tmp_path / "cache")
    fake = FakeStructuredGenerationClient(scripted_contents=[json.dumps({"translations": ["Hello"]})])

    to_zh = service.translate_batch(["你好"], target_locale="zh-CN", client=fake)
    assert to_zh == ["你好"]  # already zh-CN, skipped
    assert fake.call_count == 0

    to_en = service.translate_batch(["你好"], target_locale="en-US", client=fake)
    assert to_en == ["Hello"]
    assert fake.call_count == 1

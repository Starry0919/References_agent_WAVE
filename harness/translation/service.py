"""LLM-based translation between English and Chinese (whichever direction the
requesting locale needs), shared by every read path that needs to localize
content the static bilingual dictionaries (`frontend/src/lib/i18n.tsx`,
`harness/i18n.py`) don't and can't cover: raw literature text (paper
titles/abstracts, extracted reasoning fragments) that arrives in whatever
language the source paper - or the hand-curated DDR record - was written in.
Symmetric by design: a zh-CN viewer gets English source text translated to
Chinese, and an en-US viewer gets Chinese source text (e.g. hand-curated DDR
narrative fields) translated to English.

Uses the same `StructuredGenerationClient` every other LLM adapter in this
package uses (`harness.diagnosis.llm_hypothesis_adapter`,
`harness.engineering_design.llm_strategy_adapter`, ...), so switching
provider/model in `.env` applies here too with no separate configuration.

Not recorded via `harness.llm_generation.service.record_generation` -
translation is a UI-localization concern (same tier as the static
dictionaries), not project-scoped scientific-generation provenance; evidence
documents translated here are not tied to a project/actor, matching how the
`CrossrefEvidenceAdapter`/`LocalDDRAdapter` calls next to this in
`harness/api/generation.py` aren't provenance-recorded either.

Caching: a permanent, content-addressed, file-based cache (same style as
`harness/paper_extraction/pipeline_cache.py`) keyed on the source text +
target locale + model id. The currently configured provider/model can take
15-30s per call (see `harness/llm_generation/client.py`'s docstring on the
reasoning-model latency this package already lives with) - the cache is what
makes that acceptable: any given string is ever translated once, across every
project and every user, not once per page view.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import tempfile
from pathlib import Path
from typing import Any

from harness.config import PROJECT_ROOT
from harness.llm_generation.client import StructuredGenerationClient
from harness import providers
from harness.config import get_settings

try:
    import openai as _openai
except ImportError:  # pragma: no cover
    _openai = None

CACHE_DIR = PROJECT_ROOT / "workspace" / "translation_cache"

_LATIN_LETTER_RE = re.compile(r"[A-Za-z]")
_CJK_RE = re.compile(r"[一-鿿]")  # CJK Unified Ideographs block

_LOCALE_NAMES = {"zh-CN": "Simplified Chinese", "en-US": "English"}


def _system_prompt(target_locale: str) -> str:
    locale_name = _LOCALE_NAMES.get(target_locale, target_locale)
    return (
        f"You translate scientific/engineering UI text into fluent {locale_name}. "
        "Preserve verbatim (never translate): gene/protein/enzyme names, chassis/strain "
        "names, chemical formulas, DOIs and accession numbers, model/version identifiers, "
        "numbers, units, and code-like tokens (snake_case, CamelCase, file paths). If a "
        "string is already in the target language, return it unchanged. "
        "Keep the translation concise and natural, matching the register of technical "
        "documentation. Reply with ONLY a single JSON object of the form "
        '{"translations": ["...", ...]} with exactly one output string per input string, '
        "in the same order - no prose, no markdown fences."
    )


def _needs_translation(text: str, target_locale: str) -> bool:
    """Cheap skip so an already-target-language string never spends an LLM
    call: skip if translating to zh-CN and there's no Latin letter to
    translate, or translating to en-US and there's no CJK character to
    translate. An unrecognized target locale is never skipped - let the LLM
    decide rather than silently no-op."""
    if not text:
        return False
    if target_locale == "zh-CN":
        return bool(_LATIN_LETTER_RE.search(text))
    if target_locale == "en-US":
        return bool(_CJK_RE.search(text))
    return True


def _cache_path(text: str, target_locale: str, model_id: str) -> Path:
    digest = hashlib.sha256(f"{text}\0{target_locale}\0{model_id}".encode("utf-8")).hexdigest()
    return CACHE_DIR / f"{digest}.json"


def _read_cache(path: Path, source_text: str) -> str | None:
    if not path.is_file():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    translation = payload.get("translation") if isinstance(payload, dict) else None
    if not isinstance(translation, str):
        return None
    # Older provider failures were deliberately returned as the source text
    # and then persisted as if they were successful translations. Such a
    # record permanently prevented a later fixed provider call from running.
    # Treat unchanged source as a cache miss (symbols/already-target-language
    # strings never reach this cache because _needs_translation skips them).
    return translation if translation.strip() != source_text.strip() else None


def _write_cache(path: Path, text: str, translation: str, target_locale: str, model_id: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=path.stem, suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(
                {"source": text, "translation": translation, "target_locale": target_locale, "model": model_id},
                handle, ensure_ascii=False, indent=2,
            )
        os.replace(tmp_name, path)
    finally:
        if os.path.exists(tmp_name):
            os.unlink(tmp_name)


def _live_translations(texts: list[str], target_locale: str) -> list[str] | None:
    """Translation-specific provider call.

    Poe's current kimi-k3 endpoint rejects OpenAI ``response_format`` with
    HTTP 400. StructuredGenerationClient always sends that option, which
    previously made every live translation silently fall back to its source.
    Translation only needs one tiny JSON envelope, so request JSON in the
    prompt and parse it defensively without the unsupported API option.
    """
    if _openai is None:
        return None
    try:
        provider = providers.resolve()
        settings = get_settings()
        request_args: dict[str, Any] = {
            "model": provider.model,
            "messages": [
                {"role": "system", "content": _system_prompt(target_locale)},
                {"role": "user", "content": json.dumps({"target_locale": target_locale, "texts": texts}, ensure_ascii=False)},
            ],
            "max_tokens": min(4000, max(800, len(texts) * 60)),
        }
        if provider.name == "poe":
            # Translation is deterministic and does not benefit from deep
            # reasoning; low effort roughly halves kimi-k3 latency.
            request_args["reasoning_effort"] = "low"
        response = _openai.OpenAI(
            api_key=provider.api_key,
            base_url=provider.base_url,
            timeout=settings.LLM_TIMEOUT_S,
        ).chat.completions.create(**request_args)
        raw = response.choices[0].message.content or ""
        match = re.search(r"\{.*\}", raw, flags=re.DOTALL)
        payload = json.loads(match.group(0) if match else raw)
        translations = payload.get("translations") if isinstance(payload, dict) else None
        if not isinstance(translations, list) or len(translations) != len(texts):
            return None
        return [value if isinstance(value, str) and value.strip() else texts[i] for i, value in enumerate(translations)]
    except Exception:
        return None


def translate_batch(texts: list[str], target_locale: str = "zh-CN", *, client: Any = None) -> list[str]:
    """Translates `texts` to `target_locale` ("zh-CN" or "en-US"), in order.
    A string that already looks like it's in the target language (no Latin
    letters left to translate into zh-CN, or no CJK characters left to
    translate into en-US - see `_needs_translation`), or is empty/purely
    numeric/symbolic, is returned unchanged without spending an LLM call. A
    provider/schema failure on the remaining strings returns them unchanged
    too - this function never fabricates a translation and never raises; a
    caller that gets back its own input has simply not had that string
    translated yet.

    `client` is injectable (defaults to a real `StructuredGenerationClient`)
    following the same convention as the other LLM adapters
    (`harness.diagnosis.llm_hypothesis_adapter`, etc), so tests can pass
    `tests.llm_generation.fakes.FakeStructuredGenerationClient` instead of
    hitting the network.
    """
    injected_client = client is not None
    if client is None:
        client = StructuredGenerationClient()
    model_id = providers.describe().get("model", "")
    results: list[str | None] = [None] * len(texts)
    to_translate: list[tuple[int, str, Path]] = []

    for i, text in enumerate(texts):
        if not _needs_translation(text, target_locale):
            results[i] = text
            continue
        cache_path = _cache_path(text, target_locale, model_id)
        cached = _read_cache(cache_path, text)
        if cached is not None:
            results[i] = cached
        else:
            to_translate.append((i, text, cache_path))

    if to_translate:
        source_texts = [t for _, t, _ in to_translate]
        if injected_client:
            user_prompt = json.dumps({"target_locale": target_locale, "texts": source_texts}, ensure_ascii=False)
            attempts, _health = client.generate(
                system_prompt=_system_prompt(target_locale), user_prompt=user_prompt, max_tokens=4000,
            )
            last = attempts[-1]
            translations: list[Any] | None = (last.parsed or {}).get("translations") if last.validation_status == "valid" else None
        else:
            translations = _live_translations(source_texts, target_locale)
        if not isinstance(translations, list) or len(translations) != len(to_translate):
            translations = None
        for j, (i, text, cache_path) in enumerate(to_translate):
            translated = translations[j] if translations is not None and isinstance(translations[j], str) else None
            if translated:
                _write_cache(cache_path, text, translated, target_locale, model_id)
                results[i] = translated
            else:
                results[i] = text  # honest fallback - never fabricate

    return [r if r is not None else texts[i] for i, r in enumerate(results)]


def translate_text(text: str, target_locale: str = "zh-CN", *, client: Any = None) -> str:
    return translate_batch([text], target_locale, client=client)[0]

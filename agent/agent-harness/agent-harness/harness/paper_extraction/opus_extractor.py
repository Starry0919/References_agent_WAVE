"""Opus-routed, content-addressed executor for per-paper design extraction."""
from __future__ import annotations

import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any

import httpx

from . import _VENDOR_DIR

MODEL = os.getenv("PAPER_EXTRACTION_MODEL", "claude-opus-5")
CACHE_DIR = _VENDOR_DIR / "paper_experimental_design_extraction" / "storage" / "extraction_cache"
ANTHROPIC_URL = "https://api.anthropic.com/v1/messages"
SKILL_PATH = Path(__file__).with_name("SKILL.md")
# Opt-in only: without ANTHROPIC_API_KEY this stage fails loudly by default
# (test_opus_is_required_not_silently_relabelled) rather than silently
# substituting a model whose extraction quality/behavior for this task is
# unproven. Set this to use whatever harness.providers/.env currently
# resolves to instead (e.g. Kimi K3) when no Anthropic credential exists.
_ALLOW_FALLBACK_MODEL = os.getenv("PAPER_EXTRACTION_ALLOW_FALLBACK_MODEL", "").strip().lower() in {"1", "true", "yes"}
# This call sends a WHOLE paper (skill_instructions + full document JSON) as
# one prompt and budgets max_tokens=24000 for a reasoning model's response -
# both well past the ~15-30s-latency, max_tokens=8000 prompts
# harness.llm_generation.client's own docstring describes tuning
# LLM_TIMEOUT_S (.env, shared by every StructuredGenerationClient caller)
# against. Production observed a real extraction still fail with
# "APITimeoutError: Request timed out" after ~565s even with
# LLM_TIMEOUT_S=280 - consistent with the OpenAI SDK's default
# retry-on-timeout burning the 280s budget twice rather than one call ever
# getting an honest shot at finishing. A skill07-specific, considerably
# larger ceiling (env-overridable for slower/faster deployments) replaces
# that instead of raising the shared setting for every other, much smaller,
# call in this module.
_SKILL07_TIMEOUT_S = float(os.getenv("PAPER_EXTRACTION_SKILL07_TIMEOUT_S", "900"))


def _skill_bytes() -> bytes:
    return SKILL_PATH.read_bytes()


def _skill_hash() -> str:
    return hashlib.sha256(_skill_bytes()).hexdigest()


def _source_bytes(request: dict[str, Any]) -> bytes:
    artifact = request["clean_document_artifact"]
    path = artifact.get("clean_json_path")
    if path and Path(path).is_file():
        return Path(path).read_bytes()
    return json.dumps(artifact, ensure_ascii=False, sort_keys=True).encode("utf-8")


def _cache_path(request: dict[str, Any], model: str) -> Path:
    digest = hashlib.sha256(
        _source_bytes(request) + b"\0" + model.encode("utf-8") + b"\0" + _skill_bytes()
    ).hexdigest()
    return CACHE_DIR / f"{digest}.json"


def _write_atomic(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix=path.stem, suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(value, handle, ensure_ascii=False, indent=2)
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


_EXTRACTION_SYSTEM_PROMPT = "You are a rigorous scientific experimental-design extractor. Output JSON only."


_CORE_FIELDS = [
    "objective", "hypothesis", "strain", "genotype", "engineering_method",
    "experimental_groups", "controls", "culture_conditions", "medium", "dosage",
    "time", "replicates", "assay", "instruments", "analysis_methods", "outcomes",
]


def _build_prompt(request: dict[str, Any]) -> dict[str, Any]:
    document = json.loads(_source_bytes(request).decode("utf-8"))
    return {
        "task": "Extract reusable experimental-design ideas from this one paper or textbook chapter.",
        "skill_instructions": SKILL_PATH.read_text(encoding="utf-8"),
        "output_contract": (
            "IMPORTANT - this call performs ONLY skill07 (per-paper experimental-design "
            "extraction) inside the larger 13-skill pipeline described in skill_instructions "
            "above. The '## 统一输出' JSON example near the end of skill_instructions "
            "describes the WHOLE PIPELINE's final combined output (after skills 08-13 "
            "also run) - it is NOT the shape for this call. Do not reuse its top-level keys "
            "(e.g. 'summary', 'experimental_designs', 'quality_report', 'governance') here. "
            "Your response must be a single JSON object with EXACTLY these five top-level "
            "keys and no others: fields, experimental_design_object, field_metadata, "
            "extensions, conflicts.\n\n"
            f"'fields' must be an object keyed by exactly these field names: {', '.join(_CORE_FIELDS)}. "
            "Each value must be an object shaped {value, status, confidence, extraction_method, "
            "evidence_ids, notes}, where status is one of reported|unknown|inferred (add an "
            "'inference': {method, rationale} object when status is 'inferred'). A field with "
            "no evidence in the paper still needs an entry with status='unknown' and value=null "
            "- never omit a field from this object.\n\n"
            "'extensions' is where article_type_gate, paper_target_strains, user_target_system "
            "and target_system_adaptation belong (per skill_instructions' own field "
            "definitions) - they are reasoning/classification metadata about the paper, not "
            "experimental-design content, so they must NOT appear inside 'fields' or at the "
            "top level."
        ),
        "requirements": [
            "First classify the document with ArticleTypeGate. Never assume it is primary research.",
            "Read the complete available document, including figure/table captions and supplements.",
            "Identify paper_target_strains from the document independently of user_target_system.",
            "For reviews/textbooks, extract design patterns and attributed source studies; do not invent experiments performed by the current authors.",
            "Use only evidence present in the paper; never invent missing values.",
            "Assign each fact to current_article, included_study, background_citation, author_inference, or model_inference.",
            "Instantiate experiments before attaching host, intervention, conditions, controls, replicates, readouts and outcomes.",
            "Separate reported, inferred, unknown and not_applicable; preserve raw labels and normalized names.",
            "Record unresolved parameters, internal source inconsistencies and supplement-dependent fields.",
            "Return concise JSON with keys: fields, experimental_design_object, field_metadata, extensions, conflicts - see output_contract above for the exact shape.",
            "Every reported field_metadata item must include source_locations with paragraph IDs.",
        ],
        "document": document,
    }


def _call_anthropic(api_key: str, model: str, prompt: dict[str, Any]) -> tuple[dict[str, Any], str, dict[str, Any]]:
    response = httpx.post(
        ANTHROPIC_URL,
        headers={"x-api-key": api_key, "anthropic-version": "2023-06-01", "content-type": "application/json"},
        json={
            "model": model, "max_tokens": 12000, "temperature": 0,
            "system": _EXTRACTION_SYSTEM_PROMPT,
            "messages": [{"role": "user", "content": json.dumps(prompt, ensure_ascii=False)}],
        },
        timeout=180.0,
    )
    response.raise_for_status()
    payload = response.json()
    text = "".join(block.get("text", "") for block in payload.get("content", []) if block.get("type") == "text")
    output = json.loads(text.removeprefix("```json").removesuffix("```").strip())
    usage = {"input_tokens": payload.get("usage", {}).get("input_tokens"), "output_tokens": payload.get("usage", {}).get("output_tokens")}
    return output, payload.get("model", model), usage


def _call_configured_provider(prompt: dict[str, Any]) -> tuple[dict[str, Any] | None, str, dict[str, Any], str | None]:
    """Fallback path when no ANTHROPIC_API_KEY is configured: use whatever
    OpenAI-compatible provider `harness.providers`/`.env` currently resolves
    to (this deployment: Kimi K3), via the same structured-JSON client
    `harness.llm_generation` already uses elsewhere, instead of hard-failing
    the whole extraction stage just because Claude Opus specifically isn't
    available."""
    from harness.llm_generation.client import StructuredGenerationClient

    client = StructuredGenerationClient()
    attempts, health = client.generate(
        system_prompt=_EXTRACTION_SYSTEM_PROMPT,
        user_prompt=json.dumps(prompt, ensure_ascii=False),
        # A reasoning model can spend most of a modest budget on
        # reasoning_tokens before any visible JSON is emitted (see
        # harness/llm_generation/client.py's own docstring) - this schema is
        # much larger than the hypothesis/strategy prompts that module was
        # tuned against, so the budget is sized up accordingly.
        max_tokens=24000,
        timeout=_SKILL07_TIMEOUT_S,
    )
    last = attempts[-1]
    if last.validation_status != "valid":
        return None, health.model or "unknown", {}, (last.error or health.reason or "generation failed")
    usage = {"input_tokens": (last.usage or {}).get("prompt_tokens"), "output_tokens": (last.usage or {}).get("completion_tokens")}
    return last.parsed, health.model, usage, None


def make_executor(model: str = MODEL):
    """Return the single skill07 executor used for uploads, DOI and search.

    Cache identity is paper content + model + skill content. Updating the
    extraction skill therefore invalidates stale extractions automatically.
    """
    def execute(request: dict[str, Any]) -> dict[str, Any]:
        api_key = os.getenv("ANTHROPIC_API_KEY")
        use_fallback = not api_key and _ALLOW_FALLBACK_MODEL
        # Cache key stays pinned to `model` (e.g. "claude-opus-5") whenever
        # the fallback isn't in play, unchanged from before this existed -
        # a cache entry written under the Opus path must never be reused as
        # if a different model had produced it, and vice versa.
        cache_path = _cache_path(request, _fallback_model_name() if use_fallback else model)
        if cache_path.is_file():
            cached = json.loads(cache_path.read_text(encoding="utf-8"))
            cached.setdefault("provenance", {})["cache"] = {
                "hit": True, "path": str(cache_path), "key_type": "content_sha256+model+skill_sha256",
            }
            cached["provenance"]["skill_sha256"] = _skill_hash()
            # The cache key hashes SKILL.md's content but not _build_prompt's
            # own Python source - a prompt-only fix (like the output_contract
            # this normalization backs) doesn't invalidate old cache entries,
            # so a cached pre-fix response could still carry the old drifted
            # shape. Normalizing on read (not just on fresh extraction) means
            # a stale cache entry can't keep reproducing the same skill08
            # failure indefinitely.
            if isinstance(cached.get("output"), dict):
                cached["output"] = _normalize_skill07_output(cached["output"])
            return cached

        if not api_key and not use_fallback:
            return {
                "status": "terminal_failure", "output": None, "artifacts": [],
                "self_check": {"passed": False, "checks": [], "score": 0.0},
                "warnings": [],
                "errors": [{
                    "code": "MODEL_NOT_CONFIGURED", "local_code": "EXP005",
                    "category": "model", "message": (
                        f"{model} is required for experimental-design extraction; "
                        "set ANTHROPIC_API_KEY or provide a skill07 executor."
                    ),
                    "retryable": True, "severity": "error", "context": {"model": model},
                    "suggested_action": "Configure the Anthropic credential and retry.",
                }],
                "metrics": {},
                "provenance": {
                    "skill_id": "skill07_experiment_extraction", "skill_version": "opus-1",
                    "input_hash": hashlib.sha256(_source_bytes(request)).hexdigest(),
                    "output_hash": None, "extractor": "anthropic_messages",
                    "model": model, "skill_sha256": _skill_hash(),
                    "cache": {"hit": False, "path": str(cache_path), "key_type": "content_sha256+model+skill_sha256"},
                },
                "review_requests": [],
            }

        prompt = _build_prompt(request)
        if api_key:
            output, resolved_model, usage = _call_anthropic(api_key, model, prompt)
            extractor_name = "anthropic_messages"
            error = None
        else:
            output, resolved_model, usage, error = _call_configured_provider(prompt)
            extractor_name = "openai_compatible_chat"

        if error is not None:
            return {
                "status": "terminal_failure", "output": None, "artifacts": [],
                "self_check": {"passed": False, "checks": [], "score": 0.0},
                "warnings": [],
                "errors": [{
                    "code": "MODEL_NOT_CONFIGURED", "local_code": "EXP005",
                    "category": "model", "message": f"experimental-design extraction failed via {resolved_model}: {error}",
                    "retryable": True, "severity": "error", "context": {"model": resolved_model},
                    "suggested_action": "Configure a working ANTHROPIC_API_KEY or LLM_PROVIDER/*_API_KEY and retry.",
                }],
                "metrics": {},
                "provenance": {
                    "skill_id": "skill07_experiment_extraction", "skill_version": "opus-1",
                    "input_hash": hashlib.sha256(_source_bytes(request)).hexdigest(),
                    "output_hash": None, "extractor": extractor_name,
                    "model": resolved_model, "skill_sha256": _skill_hash(),
                    "cache": {"hit": False, "path": str(cache_path), "key_type": "content_sha256+model+skill_sha256"},
                },
                "review_requests": [],
            }

        output = _normalize_skill07_output(output) if isinstance(output, dict) else output

        extensions = output.get("extensions") if isinstance(output, dict) else None
        gate = extensions.get("article_type_gate") if isinstance(extensions, dict) else None
        if not isinstance(gate, dict) or not gate.get("article_type"):
            return {
                "status": "needs_review", "output": output, "artifacts": [],
                "self_check": {"passed": False, "checks": [{"name": "article_type_gate", "passed": False}], "score": 0.0},
                "warnings": [{"code": "ARTICLE_TYPE_GATE_MISSING", "message": "Model output did not classify the document before extraction."}],
                "errors": [], "metrics": {},
                "provenance": {
                    "skill_id": "skill07_experiment_extraction", "skill_version": "opus-2",
                    "input_hash": hashlib.sha256(_source_bytes(request)).hexdigest(),
                    "output_hash": hashlib.sha256(json.dumps(output, sort_keys=True).encode()).hexdigest(),
                    "extractor": extractor_name, "model": resolved_model,
                    "skill_sha256": _skill_hash(),
                    "cache": {"hit": False, "path": str(cache_path), "key_type": "content_sha256+model+skill_sha256"},
                },
                "review_requests": [{"reason": "article_type_gate_missing", "fields": ["extensions.article_type_gate"]}],
            }
        result = {
            "status": "succeeded", "output": output, "artifacts": [],
            "self_check": {"passed": True, "checks": [], "score": 1.0},
            "warnings": [], "errors": [],
            "metrics": usage,
            "provenance": {
                "skill_id": "skill07_experiment_extraction", "skill_version": "opus-2",
                "input_hash": hashlib.sha256(_source_bytes(request)).hexdigest(),
                "output_hash": hashlib.sha256(json.dumps(output, sort_keys=True).encode()).hexdigest(),
                "extractor": extractor_name, "model": resolved_model,
                "skill_sha256": _skill_hash(),
                "cache": {"hit": False, "path": str(cache_path), "key_type": "content_sha256+model+skill_sha256"},
            },
            "review_requests": [],
        }
        _write_atomic(cache_path, result)
        return result

    return execute


_REASONING_KEYS = ("article_type_gate", "paper_target_strains", "user_target_system", "target_system_adaptation")


def _normalize_skill07_output(output: dict[str, Any]) -> dict[str, Any]:
    """Best-effort repair for the schema drift observed in production: despite
    `output_contract` in `_build_prompt` pinning the exact shape, the model
    occasionally still returns the SKILL.md's whole-pipeline "统一输出" shape
    for this single-skill call instead (`fields` missing entirely, or the
    reasoning keys placed at the top level / inside `fields` rather than
    inside `extensions`).

    Never invents extraction content - only relocates data the model already
    produced into the contracted shape, so skill08 (which hard-fails the
    entire run with "Skill07 input is missing" if `fields` isn't a dict -
    EVID001) gets something it can process instead of crashing a run whose
    reasoning/strain-identification output was otherwise usable.
    """
    if not isinstance(output, dict):
        return output

    fields = output.get("fields")
    extensions = output.get("extensions")
    if not isinstance(extensions, dict):
        extensions = {}

    # Reasoning keys sometimes land inside `fields` instead of `extensions`
    # (observed shape: fields = {article_type_gate, paper_target_strains,
    # user_target_system, target_system_adaptation} with no real design
    # content) - or at the top level of `output` alongside `fields`/`extensions`
    # (observed shape: no `fields` key at all, `experimental_designs` used
    # instead). Pull them into `extensions` wherever found.
    if isinstance(fields, dict):
        for key in _REASONING_KEYS:
            if key in fields and key not in extensions:
                extensions[key] = fields.pop(key)
    for key in _REASONING_KEYS:
        if key in output and key not in extensions:
            extensions[key] = output[key]

    output["extensions"] = extensions
    # skill08 requires `fields` to be a dict (EVID001 otherwise) - an empty
    # dict is valid and honestly means "no design fields extracted", which
    # downstream (skill09's completeness score, this repo's own
    # result_summary.build_extraction_summary) already renders as such,
    # rather than aborting the whole run.
    output["fields"] = fields if isinstance(fields, dict) else {}
    output.setdefault("experimental_design_object", {})
    output.setdefault("field_metadata", {})
    output.setdefault("conflicts", [])
    return output


def _fallback_model_name() -> str:
    """Best-effort model name for cache-key/provenance purposes when no
    ANTHROPIC_API_KEY is configured - resolved lazily (not at import time)
    so a missing/misconfigured provider doesn't crash the whole module."""
    try:
        from harness.providers import resolve

        return resolve().model
    except Exception:
        return "unconfigured"

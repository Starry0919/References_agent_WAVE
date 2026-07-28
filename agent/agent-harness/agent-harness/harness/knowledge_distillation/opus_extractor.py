"""Opus-routed, content-addressed executor for Step05 (basic knowledge
extraction).

The vendored module's own `step05_basic_knowledge_extraction/skill.py` is a
small regex/keyword library (see its docstring and
`biological_knowledge_distillation/README.md` "Phase roadmap" item 2) - real
textbook prose routinely uses phrasing the patterns miss. This executor
replaces *only* Step05 with a real model call, the same seam
`harness/paper_extraction/opus_extractor.py` uses for skill07: every step
downstream (Step06 principle distillation, Step09 evidence-binding hard
gate, Step10 fusion, Step12 governance) stays the deterministic, tested,
rule-based pipeline exactly as built - the LLM only ever proposes candidate
concepts/mechanisms with a cited block_id + excerpt, and Step09 independently
re-verifies every citation against the real parsed blocks regardless of
what this executor claims. A hallucinated citation is therefore caught
downstream even if it slipped past the defensive checks in this file.
"""
from __future__ import annotations

import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any

import httpx

from . import _VENDOR_DIR

MODEL = os.getenv("KNOWLEDGE_DISTILLATION_MODEL", "claude-opus-5")
CACHE_DIR = _VENDOR_DIR / "biological_knowledge_distillation" / "storage" / "extraction_cache"
ANTHROPIC_URL = "https://api.anthropic.com/v1/messages"
SKILL_PATH = Path(__file__).with_name("SKILL.md")

_REQUIRED_CONCEPT_FIELDS = {
    "knowledge_id", "knowledge_type", "name_zh", "name_en", "definition_zh", "definition_en",
    "organism_scope", "source_statements", "status", "confidence",
}


def _skill_bytes() -> bytes:
    return SKILL_PATH.read_bytes()


def _skill_hash() -> str:
    return hashlib.sha256(_skill_bytes()).hexdigest()


def _eligible_blocks(request: dict[str, Any]) -> list[dict[str, Any]]:
    scope = request.get("extraction_scope", [])
    eligible_ids: set[str] = set()
    for section in scope:
        if section.get("recommended_action") in {"extract_full", "extract_partial"}:
            eligible_ids.update(section.get("block_ids", []))
    blocks = request.get("source_structure", {}).get("blocks", [])
    return [b for b in blocks if b["block_id"] in eligible_ids and b["block_type"] in {"paragraph", "box"}]


def _source_bytes(request: dict[str, Any]) -> bytes:
    payload = {
        "source_id": request.get("source_structure", {}).get("source_id"),
        "validated_source": request.get("validated_source"),
        "blocks": _eligible_blocks(request),
    }
    return json.dumps(payload, ensure_ascii=False, sort_keys=True).encode("utf-8")


def _cache_path(request: dict[str, Any], model: str) -> Path:
    digest = hashlib.sha256(_source_bytes(request) + b"\0" + model.encode("utf-8") + b"\0" + _skill_bytes()).hexdigest()
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


def _not_configured(request: dict[str, Any], model: str, cache_path: Path) -> dict[str, Any]:
    return {
        "status": "terminal_failure", "output": None,
        "errors": [{
            "code": "SCHEMA_VALIDATION_ERROR",
            "message": f"{model} is required for Step05 basic-knowledge extraction; set ANTHROPIC_API_KEY or provide a step05 executor.",
            "retryable": True, "source_id": request.get("source_structure", {}).get("source_id"),
        }],
        "provenance": {
            "step_id": "step05_basic_knowledge_extraction", "step_version": "opus-1",
            "input_hash": hashlib.sha256(_source_bytes(request)).hexdigest(), "output_hash": None,
            "extractor": "anthropic_messages", "model": model, "skill_sha256": _skill_hash(),
            "cache": {"hit": False, "path": str(cache_path), "key_type": "content_sha256+model+skill_sha256"},
        },
    }


def _sanitize(output: dict[str, Any], eligible_blocks: list[dict[str, Any]], source_id: str) -> tuple[dict[str, Any], list[dict]]:
    """Drop any object whose cited block_id doesn't exist, or whose cited
    excerpt isn't actually a substring of that block's text - the same
    existence/attribution check Step09 performs, applied here as a first
    line of defense so an obviously-hallucinated citation never even
    reaches the deterministic pipeline as a "candidate"."""
    block_text = {b["block_id"]: b["text"] for b in eligible_blocks}
    warnings = []
    kept = {"concepts": [], "mechanisms": []}
    for key in ("concepts", "mechanisms"):
        for obj in output.get(key, []) if isinstance(output, dict) else []:
            if not isinstance(obj, dict) or not _REQUIRED_CONCEPT_FIELDS.issubset(obj.keys()):
                warnings.append({"code": "SCHEMA_VALIDATION_ERROR", "message": f"dropped malformed {key[:-1]} object from model output", "retryable": False, "source_id": source_id})
                continue
            statements = obj.get("source_statements") or []
            valid_statements = [s for s in statements if s.get("block_id") in block_text and s.get("text", "").strip() and s["text"].strip() in block_text[s["block_id"]]]
            if not valid_statements:
                warnings.append({"code": "EVIDENCE_NOT_FOUND", "message": f"dropped {obj.get('knowledge_id')}: no source_statements citation could be verified against the parsed blocks", "retryable": False, "source_id": source_id, "affected_objects": [obj.get("knowledge_id")]})
                continue
            obj["source_statements"] = valid_statements
            kept[key].append(obj)
    return kept, warnings


def make_executor(model: str = MODEL):
    """Return the Step05 executor, injected via
    `WorkflowEngine(config, {"step05_basic_knowledge_extraction": make_executor(...)})`.
    Cache identity is (eligible blocks + validated_source) + model + skill
    content, so editing SKILL.md or the block set invalidates stale
    extractions automatically."""

    def execute(request: dict[str, Any]) -> dict[str, Any]:
        source_id = request.get("source_structure", {}).get("source_id", "unknown_source")
        cache_path = _cache_path(request, model)
        if cache_path.is_file():
            cached = json.loads(cache_path.read_text(encoding="utf-8"))
            cached.setdefault("provenance", {})["cache"] = {"hit": True, "path": str(cache_path), "key_type": "content_sha256+model+skill_sha256"}
            return cached

        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            return _not_configured(request, model, cache_path)

        eligible_blocks = _eligible_blocks(request)
        if not eligible_blocks:
            return {
                "output": {"concepts": [], "mechanisms": []}, "status": "succeeded", "errors": [],
                "provenance": {"step_id": "step05_basic_knowledge_extraction", "step_version": "opus-1", "source_ids": [source_id]},
            }

        prompt = {
            "task": "Extract biological concepts and mechanisms from this textbook excerpt's in-scope blocks only.",
            "skill_instructions": SKILL_PATH.read_text(encoding="utf-8"),
            "requirements": [
                "Only use text that appears verbatim in the given blocks - never invent a definition, mechanism, organism, or citation.",
                "Every concept/mechanism must include source_statements: a list of {block_id, text} where `text` is copied verbatim (a real substring) from that block_id's text.",
                "Never guess an organism_scope. If the block does not name an organism, leave organism_scope as an empty list - do not default to E. coli or E. coli K-12.",
                "Separate concepts (definitions) from mechanisms (causal/regulatory relationships); set mechanisms' causal_direction to positive, negative, or unspecified.",
                "Flag pedagogical_simplification=true for definition boxes that explicitly present a simplified/idealized model.",
                "Return strict JSON only, with exactly two top-level keys: concepts (list) and mechanisms (list).",
                "Each object needs: knowledge_id (e.g. '<source_id>:concept:<n>' or '<source_id>:mechanism:<n>'), knowledge_type, name_zh, name_en, definition_zh, definition_en, organism_scope, strain_scope, source_statements, status ('normalized'), confidence (0-1), pedagogical_simplification.",
            ],
            "source_id": source_id,
            "blocks": eligible_blocks,
        }
        response = httpx.post(
            ANTHROPIC_URL,
            headers={"x-api-key": api_key, "anthropic-version": "2023-06-01", "content-type": "application/json"},
            json={
                "model": model, "max_tokens": 8000, "temperature": 0,
                "system": "You are a rigorous biological-knowledge extractor. Output JSON only, never fabricate evidence.",
                "messages": [{"role": "user", "content": json.dumps(prompt, ensure_ascii=False)}],
            },
            timeout=180.0,
        )
        response.raise_for_status()
        payload = response.json()
        text = "".join(block.get("text", "") for block in payload.get("content", []) if block.get("type") == "text")
        raw_output = json.loads(text.removeprefix("```json").removesuffix("```").strip())
        output, warnings = _sanitize(raw_output, eligible_blocks, source_id)

        result = {
            "output": output,
            "status": "succeeded_with_warnings" if warnings else "succeeded",
            "errors": warnings,
            "provenance": {
                "step_id": "step05_basic_knowledge_extraction", "step_version": "opus-1",
                "input_hash": hashlib.sha256(_source_bytes(request)).hexdigest(),
                "output_hash": hashlib.sha256(json.dumps(output, sort_keys=True).encode()).hexdigest(),
                "extractor": "anthropic_messages", "model": payload.get("model", model), "skill_sha256": _skill_hash(),
                "cache": {"hit": False, "path": str(cache_path), "key_type": "content_sha256+model+skill_sha256"},
                "source_ids": [source_id],
            },
        }
        _write_atomic(cache_path, result)
        return result

    return execute

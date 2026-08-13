"""Reusable shadow-only infrastructure for Skill07 Optimization Wave 1."""
from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

WAVE_VERSION = "skill07_optimization_wave1_v1"


def canonical_hash(value: Any) -> str:
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def cache_identity(
    *, paper_id: str, source_document_hash: str, representation_version: str,
    prompt_hash: str, skill_hash: str, schema_hash: str, validator_version: str,
    model_provider: str, model: str, model_parameters: dict[str, Any], candidate_id: str,
) -> dict[str, Any]:
    components = {
        "paper_id": paper_id,
        "source_document_hash": source_document_hash,
        "representation_version": representation_version,
        "prompt_hash": prompt_hash,
        "skill_hash": skill_hash,
        "schema_hash": schema_hash,
        "validator_version": validator_version,
        "model_provider": model_provider,
        "model": model,
        "model_parameters": model_parameters,
        "candidate_id": candidate_id,
    }
    return {"components": components, "sha256": canonical_hash(components)}


def classify_repair_failure(error: Any) -> dict[str, str]:
    text = json.dumps(error, ensure_ascii=False).casefold()
    if any(token in text for token in ("jsondecode", "parse", "result marker", "unterminated", "delimiter")):
        return {"class": "R0_PARSE_ERROR", "route": "deterministic_local_repair"}
    if any(token in text for token in ("required property", "is not of type", "additional properties", "schema")):
        return {"class": "R1_STRUCTURAL_ERROR", "route": "local_normalization_then_full_fallback"}
    if any(token in text for token in ("missing field", "is a required property", "required field")):
        return {"class": "R2_MISSING_FIELD", "route": "targeted_repair_then_full_fallback"}
    if any(token in text for token in ("evidence_id", "source_location", "applicability", "does not resolve")):
        return {"class": "R3_LOCAL_SEMANTIC_ERROR", "route": "targeted_repair_then_full_fallback"}
    return {"class": "R4_SCIENTIFIC_REASONING_ERROR", "route": "full_context_repair"}


def local_parse_repair(text: str) -> dict[str, Any] | None:
    """Recover the first complete JSON object; never invent scientific data."""
    cleaned = re.sub(r"^\s*```(?:json)?\s*|\s*```\s*$", "", text.strip(), flags=re.I)
    decoder = json.JSONDecoder()
    for match in re.finditer(r"\{", cleaned):
        try:
            value, _ = decoder.raw_decode(cleaned[match.start():])
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict):
            return value
    return None


_CRITICAL_SECTION_TERMS = (
    "abstract", "introduction", "background", "result", "method", "material",
    "experimental", "discussion", "conclusion", "supplement",
)


def high_recall_route(document: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    """Conservative routing prototype with a fail-closed coverage guard.

    It retains all scientific sections and all figure/table/citation objects.
    References may be omitted only when not linked from retained paragraphs.
    The prototype intentionally prioritizes recall and will often offer little
    compression; it is never a production default.
    """
    sections = document.get("sections", [])
    critical_ids = {
        str(section.get("section_id") or section.get("id") or "")
        for section in sections if isinstance(section, dict)
        and any(term in str(section.get("title") or "").casefold() for term in _CRITICAL_SECTION_TERMS)
    }
    # Unknown section labels are retained: uncertainty must increase recall.
    known_noncritical = {"references", "acknowledgements", "author contributions", "funding"}
    selected_sections = []
    for section in sections:
        title = str(section.get("title") or "").casefold()
        if str(section.get("section_id") or section.get("id") or "") in critical_ids or not any(x in title for x in known_noncritical):
            selected_sections.append(section)
    selected_ids = {str(section.get("section_id") or section.get("id") or "") for section in selected_sections}
    selected_paragraphs = [
        paragraph for paragraph in document.get("paragraphs", []) if isinstance(paragraph, dict)
        and str(paragraph.get("section_id") or paragraph.get("section") or "") in selected_ids
    ]
    routed = dict(document)
    routed["sections"] = selected_sections
    routed["paragraphs"] = selected_paragraphs
    report = {
        "selected_section_count": len(selected_sections),
        "total_section_count": len(sections),
        "selected_paragraph_count": len(selected_paragraphs),
        "total_paragraph_count": len(document.get("paragraphs", [])),
        "section_coverage": len(selected_sections) / len(sections) if sections else 1.0,
        "paragraph_coverage": len(selected_paragraphs) / len(document.get("paragraphs", [])) if document.get("paragraphs") else 1.0,
        "figure_coverage": 1.0,
        "table_coverage": 1.0,
        "citation_coverage": 1.0,
        "supplement_coverage": 1.0 if "supplements" in document else "NOT_AVAILABLE_IN_SOURCE",
        "critical_evidence_recall": "UNKNOWN_WITHOUT_GOLD",
        "coverage_guard_passed": len(selected_sections) == len(sections) and len(selected_paragraphs) == len(document.get("paragraphs", [])),
    }
    return routed, report


def map_reduce_plan(document: dict[str, Any]) -> dict[str, Any]:
    """Build an anchor-preserving plan; does not invoke a model."""
    maps = {key: [] for key in ("objective_trigger", "methods_implementation", "results_phenotype", "figures_tables", "supplement", "evidence_candidates")}
    for paragraph in document.get("paragraphs", []):
        if not isinstance(paragraph, dict):
            continue
        section = str(paragraph.get("section_id") or paragraph.get("section") or "").casefold()
        if any(x in section for x in ("intro", "abstract", "background")):
            maps["objective_trigger"].append(paragraph.get("paragraph_id"))
        if any(x in section for x in ("method", "material", "experimental")):
            maps["methods_implementation"].append(paragraph.get("paragraph_id"))
        if "result" in section:
            maps["results_phenotype"].append(paragraph.get("paragraph_id"))
        if "supp" in section:
            maps["supplement"].append(paragraph.get("paragraph_id"))
        maps["evidence_candidates"].append(paragraph.get("paragraph_id"))
    maps["figures_tables"] = [
        *(str(value.get("figure_id")) for value in document.get("figures", []) if isinstance(value, dict)),
        *(str(value.get("table_id")) for value in document.get("tables", []) if isinstance(value, dict)),
    ]
    return {
        "maps": maps,
        "reduce_requirements": [
            "global biological-object registry", "stable original anchors", "deduplicate experiment instances",
            "preserve conflicts", "validate trigger precedes action", "retain alternatives and failure iterations",
        ],
        "quality_checks": [
            "experiment_fragmentation", "duplicate_experiments", "lost_causal_chain", "wrong_cross_section_linkage",
            "contradictory_interpretations", "missing_alternatives", "missing_failure_iteration", "rule_degradation",
        ],
        "execution_status": "FRAMEWORK_ONLY_NOT_LLM_BENCHMARKED",
    }


@dataclass(frozen=True)
class CascadeDecision:
    decision: str
    reasons: tuple[str, ...]


def cascade_gate(result: dict[str, Any], human_gold_available: bool = False) -> CascadeDecision:
    reasons: list[str] = []
    if result.get("status") != "succeeded":
        reasons.append("candidate did not pass deterministic validation")
    if not result.get("evidence_verified_by_skill08", False):
        reasons.append("independent evidence verification absent")
    if not human_gold_available:
        reasons.append("human/gold scientific correctness unavailable")
    return CascadeDecision("ACCEPT_FAST" if not reasons else "FALLBACK_KIMI_K3", tuple(reasons))


def _values(value: Any, key: str) -> list[Any]:
    result: list[Any] = []
    if isinstance(value, dict):
        for name, item in value.items():
            if name == key:
                result.append(item)
            result.extend(_values(item, key))
    elif isinstance(value, list):
        for item in value:
            result.extend(_values(item, key))
    return result


def _strings(values: list[Any]) -> set[str]:
    result: set[str] = set()
    for value in values:
        if isinstance(value, list):
            result.update(str(item) for item in value if item not in (None, ""))
        elif value not in (None, ""):
            result.add(str(value))
    return result


def compare_scientific_outputs(baseline: dict[str, Any], candidate: dict[str, Any]) -> dict[str, Any]:
    """Structural regression detector, explicitly not a scientific truth judge."""
    keys = (
        "experiment_id", "object_id", "strain_id", "construct_id", "evidence_ids", "source_locations",
        "design_action", "trigger_observation", "reason_nature", "alternatives_considered", "implementation",
        "result", "generalizable_rule",
    )
    changes = {}
    hard_flags = []
    for key in keys:
        left, right = _strings(_values(baseline, key)), _strings(_values(candidate, key))
        missing, added = sorted(left - right), sorted(right - left)
        changes[key] = {"baseline_count": len(left), "candidate_count": len(right), "missing": missing, "added": added}
        if key in {"experiment_id", "evidence_ids", "source_locations"} and missing:
            hard_flags.append(f"possible critical omission in {key}")
    return {
        "structural_changes": changes,
        "hard_quality_flags": hard_flags,
        "human_scientific_judgement": "REQUIRED",
        "warning": "Similarity or structural parity does not establish scientific correctness.",
    }

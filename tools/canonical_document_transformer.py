"""Shadow-only canonical document representation transformer.

This module is deliberately not imported by the production paper-extraction
pipeline.  It converts the current Skill06 clean-document JSON into a
reversible, single-text-copy representation for benchmark use only.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from copy import deepcopy
from pathlib import Path
from typing import Any

REPRESENTATION_VERSION = "skill07_canonical_document_v0.1"


def _json_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _sha256(value: Any) -> str:
    return hashlib.sha256(_json_bytes(value)).hexdigest()


def _section_fragments(content: str, paragraphs: list[dict[str, Any]]) -> tuple[str, list[dict[str, Any]]]:
    """Remove sequential paragraph copies while retaining exact interstitial data.

    Each fragment is positioned before a paragraph index (or after all
    paragraphs when the index equals their count), making reconstruction
    byte-for-byte deterministic.  If sequential matching is unsafe, the
    complete original section content is retained as a fallback residual.
    """
    cursor = 0
    fragments: list[dict[str, Any]] = []
    for index, paragraph in enumerate(paragraphs):
        text = str(paragraph.get("text") or "")
        position = content.find(text, cursor) if text else cursor
        if position < 0:
            return "full_section_fallback", [{"before_paragraph_index": 0, "content": content}]
        residual = content[cursor:position]
        if residual:
            fragments.append({"before_paragraph_index": index, "content": residual})
        cursor = position + len(text)
    tail = content[cursor:]
    if tail:
        fragments.append({"before_paragraph_index": len(paragraphs), "content": tail})
    return "interleaved_residuals", fragments


def transform_document(document: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    if not isinstance(document, dict):
        raise TypeError("clean document must be an object")
    sections = document.get("sections")
    paragraphs = document.get("paragraphs")
    if not isinstance(sections, list) or not isinstance(paragraphs, list):
        raise ValueError("clean document must contain sections[] and paragraphs[]")

    by_section: dict[str, list[dict[str, Any]]] = {}
    canonical_paragraphs: list[dict[str, Any]] = []
    section_positions: dict[str, int] = {}
    for position, item in enumerate(paragraphs):
        if not isinstance(item, dict):
            raise ValueError(f"paragraphs[{position}] must be an object")
        paragraph = deepcopy(item)
        section_id = str(paragraph.pop("section", ""))
        paragraph["section_id"] = section_id
        paragraph["position"] = position
        canonical_paragraphs.append(paragraph)
        by_section.setdefault(section_id, []).append(item)

    canonical_sections: list[dict[str, Any]] = []
    stack: list[tuple[int, str]] = []
    matched_sections = fallback_sections = residual_chars = 0
    for position, item in enumerate(sections):
        if not isinstance(item, dict):
            raise ValueError(f"sections[{position}] must be an object")
        section = deepcopy(item)
        section_id = str(section.pop("id", ""))
        content = str(section.pop("content", ""))
        level = int(section.get("level") or 1)
        while stack and stack[-1][0] >= level:
            stack.pop()
        parent = stack[-1][1] if stack else None
        stack.append((level, section_id))
        scoped = by_section.get(section_id, [])
        mode, residual = _section_fragments(content, scoped)
        if mode == "interleaved_residuals":
            matched_sections += 1
        else:
            fallback_sections += 1
        residual_chars += sum(len(fragment["content"]) for fragment in residual)
        section.update({
            "section_id": section_id,
            "position": position,
            "parent_section_id": parent,
            "paragraph_ids": [str(paragraph.get("paragraph_id") or "") for paragraph in scoped],
            "residual_mode": mode,
            "residual_content": residual,
        })
        canonical_sections.append(section)
        section_positions[section_id] = position

    missing_sections = sorted(set(by_section) - set(section_positions))
    if missing_sections:
        raise ValueError(f"paragraphs reference missing sections: {missing_sections}")

    canonical = {
        key: deepcopy(value)
        for key, value in document.items()
        if key not in {"sections", "paragraphs"}
    }
    canonical["canonical_representation"] = {
        "version": REPRESENTATION_VERSION,
        "source_sha256": _sha256(document),
        "text_source_of_truth": "paragraphs[].text",
        "section_content_policy": "ordered paragraph references plus position-aware residual_content",
        "reversible": True,
    }
    canonical["sections"] = canonical_sections
    canonical["paragraphs"] = canonical_paragraphs

    restored = restore_document(canonical)
    exact = _json_bytes(restored) == _json_bytes(document)
    report = {
        "representation_version": REPRESENTATION_VERSION,
        "source_sha256": _sha256(document),
        "canonical_sha256": _sha256(canonical),
        "restored_sha256": _sha256(restored),
        "exact_roundtrip": exact,
        "section_count": len(sections),
        "paragraph_count": len(paragraphs),
        "matched_sections": matched_sections,
        "fallback_sections": fallback_sections,
        "residual_characters": residual_chars,
        "original_characters": len(json.dumps(document, ensure_ascii=False)),
        "canonical_characters": len(json.dumps(canonical, ensure_ascii=False)),
        "original_bytes": len(json.dumps(document, ensure_ascii=False).encode("utf-8")),
        "canonical_bytes": len(json.dumps(canonical, ensure_ascii=False).encode("utf-8")),
    }
    report["character_reduction_fraction"] = 1 - report["canonical_characters"] / report["original_characters"]
    report["byte_reduction_fraction"] = 1 - report["canonical_bytes"] / report["original_bytes"]
    if not exact:
        raise AssertionError("canonical transform failed exact round-trip check")
    return canonical, report


def restore_document(canonical: dict[str, Any]) -> dict[str, Any]:
    paragraphs = canonical.get("paragraphs", [])
    sections = canonical.get("sections", [])
    by_section: dict[str, list[dict[str, Any]]] = {}
    restored_paragraphs: list[dict[str, Any]] = []
    for item in sorted(paragraphs, key=lambda value: value.get("position", 0)):
        paragraph = deepcopy(item)
        paragraph.pop("position", None)
        section_id = str(paragraph.pop("section_id", ""))
        paragraph["section"] = section_id
        restored_paragraphs.append(paragraph)
        by_section.setdefault(section_id, []).append(paragraph)

    restored_sections: list[dict[str, Any]] = []
    for item in sorted(sections, key=lambda value: value.get("position", 0)):
        section = deepcopy(item)
        section_id = str(section.pop("section_id", ""))
        section.pop("position", None)
        section.pop("parent_section_id", None)
        section.pop("paragraph_ids", None)
        mode = section.pop("residual_mode", "interleaved_residuals")
        residual = section.pop("residual_content", [])
        scoped = by_section.get(section_id, [])
        if mode == "full_section_fallback":
            content = str(residual[0]["content"]) if residual else ""
        else:
            fragments = {int(value["before_paragraph_index"]): str(value["content"]) for value in residual}
            parts: list[str] = []
            for index, paragraph in enumerate(scoped):
                parts.append(fragments.get(index, ""))
                parts.append(str(paragraph.get("text") or ""))
            parts.append(fragments.get(len(scoped), ""))
            content = "".join(parts)
        section["id"] = section_id
        section["content"] = content
        restored_sections.append(section)

    restored = {
        key: deepcopy(value)
        for key, value in canonical.items()
        if key not in {"canonical_representation", "sections", "paragraphs"}
    }
    restored["sections"] = restored_sections
    restored["paragraphs"] = restored_paragraphs
    return restored


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    document = json.loads(args.input.read_text(encoding="utf-8"))
    canonical, report = transform_document(document)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(canonical, ensure_ascii=False, indent=2), encoding="utf-8")
    report_path = args.report or args.output.with_name("transformation_report.json")
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

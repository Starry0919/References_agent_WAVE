from __future__ import annotations

import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, Mapping, Optional

try:
    from .artifact import CleanDocumentManager
    from .cleaners import clean_headers_footers, normalize_markdown_structure, repair_tables
    from .diff import ChangeTracker
    from .error_codes import error
    from .json_builder import build_clean_json
    from .logger import JsonlSkillLogger
    from .schema import RULE_SET_VERSION, SKILL_ID, SKILL_VERSION, sha256_json, sha256_text
    from .validator import validate_cleaning
except ImportError:
    from artifact import CleanDocumentManager
    from cleaners import clean_headers_footers, normalize_markdown_structure, repair_tables
    from diff import ChangeTracker
    from error_codes import error
    from json_builder import build_clean_json
    from logger import JsonlSkillLogger
    from schema import RULE_SET_VERSION, SKILL_ID, SKILL_VERSION, sha256_json, sha256_text
    from validator import validate_cleaning


class ScientificMarkdownCleaner:
    def __init__(
        self,
        output_root: Optional[Path] = None,
        logger: Optional[Callable[[Mapping[str, Any]], None]] = None,
        clock: Optional[Callable[[], datetime]] = None,
    ):
        module_root = Path(__file__).resolve().parents[2]
        self.manager = CleanDocumentManager(output_root or module_root / "clean_document_artifacts")
        self.logger = logger if logger is not None else JsonlSkillLogger()
        self.clock = clock or (lambda: datetime.now(timezone.utc))

    def execute(self, request: Mapping[str, Any]) -> Dict[str, Any]:
        started = time.perf_counter()
        input_hash = sha256_json(request)
        source = request.get("document_artifact") if isinstance(request, Mapping) else None
        if not isinstance(source, Mapping):
            return self._finish(self._failure(error("CLEAN001", {"field": "document_artifact"}), input_hash), started)
        markdown_artifact = source.get("markdown_artifact", {})
        original = markdown_artifact.get("markdown_content")
        if not isinstance(original, str):
            path = Path(markdown_artifact.get("markdown_path", ""))
            original = path.read_text(encoding="utf-8", errors="replace") if path.is_file() else ""
        if not original.strip():
            return self._finish(self._failure(error("CLEAN001"), input_hash), started)

        tracker = ChangeTracker()
        cleaned, noise_removed = clean_headers_footers(original, tracker)
        cleaned = normalize_markdown_structure(cleaned, tracker)
        cleaned, tables_fixed, table_warnings = repair_tables(cleaned, tracker)
        cleaned = cleaned.rstrip() + "\n"

        paper_id = source.get("document_metadata", {}).get("paper_id") or "unknown"
        metadata = {
            "paper_id": paper_id,
            "title": source.get("document_metadata", {}).get("title"),
            "parser": source.get("document_metadata", {}).get("parser"),
            "parser_version": source.get("document_metadata", {}).get("parser_version"),
            "cleaner": SKILL_ID,
            "cleaner_version": SKILL_VERSION,
            "rule_set_version": RULE_SET_VERSION,
            "source_markdown_sha256": sha256_text(original),
            "clean_markdown_sha256": sha256_text(cleaned)
        }
        clean_json = build_clean_json(cleaned, metadata, tracker.changes)
        checks = validate_cleaning(original, cleaned, clean_json)
        failed = [v["name"] for v in checks if not v["passed"]]
        protected_failures = {"protected_scientific_values", "citations_preserved", "no_new_scientific_text"}
        if protected_failures & set(failed):
            return self._finish(self._failure(error("CLEAN004", {"failed_checks": failed}), input_hash), started)
        if failed:
            return self._finish(self._failure(error("CLEAN002", {"failed_checks": failed}), input_hash), started)

        # Immutable artifact identity includes the rule set. Runtime timestamps
        # belong in logs/provenance, not in deterministic document content.
        storage_key = sha256_text(sha256_text(original) + ":" + RULE_SET_VERSION)
        markdown_path, json_path, markdown_ref, json_ref = self.manager.store(
            paper_id, storage_key, cleaned, clean_json
        )
        original_sections = source.get("structure_map", {}).get("sections", [])
        clean_sections = clean_json["sections"]
        fallback_structure_used = any(v.get("is_fallback") for v in clean_sections)
        missing_sections = [
            v.get("title") for v in original_sections
            if v.get("title") and v.get("title") not in {s["title"] for s in clean_sections}
        ]
        quality_report = {
            "noise_removed": noise_removed,
            "tables_fixed": tables_fixed,
            "figures_preserved": len(clean_json["figures"]),
            "tables_preserved": len(clean_json["tables"]),
            "citations_preserved": next(v["passed"] for v in checks if v["name"] == "citations_preserved"),
            "sections_preserved": not missing_sections,
            "fallback_structure_used": fallback_structure_used,
            "missing_sections": missing_sections,
            "confidence": round(sum(v["passed"] for v in checks) / len(checks), 4)
        }
        clean_document = {
            "document_metadata": metadata,
            "clean_markdown_path": str(markdown_path),
            "clean_json_path": str(json_path),
            "structure_map": {"sections": clean_json["sections"], "paragraphs": clean_json["paragraphs"]},
            "figure_map": {"figures": clean_json["figures"]},
            "table_map": {"tables": clean_json["tables"]},
            "citation_map": {"citations": clean_json["citations"]},
            "modification_log": {"changes": tracker.changes},
            "cleaning_quality_report": quality_report
        }
        output = {
            "clean_markdown_artifact": markdown_ref,
            "clean_json_artifact": json_ref,
            "clean_document_artifact": clean_document,
            "cleaning_report": quality_report
        }
        warnings = []
        review_requests = []
        if table_warnings:
            warnings.append({
                "code": "CLEAN003",
                "message": "One or more tables could not be repaired safely and were left as-is.",
                "tables": table_warnings,
            })
            review_requests.append({"reason": "table_repair_uncertain", "paper_id": paper_id})
        if "�" in original:
            warnings.append({"code": "CLEAN005", "message": "Unresolved replacement characters were preserved."})
            review_requests.append({"reason": "encoding_uncertain", "paper_id": paper_id})
        if fallback_structure_used:
            warnings.append({
                "code": "CLEAN002",
                "message": "No Markdown section headings were found; the full text was retained in a fallback section.",
            })
            review_requests.append({"reason": "structure_missing", "paper_id": paper_id})
        status = "succeeded_with_warnings" if warnings else "succeeded"
        result = {
            "status": status, "output": output,
            "artifacts": [markdown_ref, json_ref],
            "self_check": {"passed": True, "checks": checks, "score": quality_report["confidence"]},
            "warnings": warnings, "errors": [],
            "metrics": {
                "changes_count": len(tracker.changes), "noise_removed": noise_removed,
                "tables_fixed": tables_fixed, "paragraphs": len(clean_json["paragraphs"])
            },
            "provenance": {
                "skill_id": SKILL_ID, "skill_version": SKILL_VERSION,
                "rule_set_version": RULE_SET_VERSION,
                "input_hash": input_hash, "output_hash": sha256_json(output),
                "source_artifact_id": source.get("document_metadata", {}).get("paper_id"),
                "source_sha256": sha256_text(original),
                "cleaned_at": self.clock().isoformat(),
                "change_map": [v["change_id"] for v in tracker.changes]
            },
            "review_requests": review_requests
        }
        return self._finish(result, started)

    def _finish(self, result, started):
        result["metrics"]["duration_ms"] = round((time.perf_counter() - started) * 1000, 3)
        clean = result.get("output", {}).get("clean_document_artifact") if result.get("output") else None
        event = {
            "skill_name": SKILL_ID,
            "paper_id": clean["document_metadata"]["paper_id"] if clean else None,
            "input_markdown": result["provenance"].get("source_sha256"),
            "output_markdown": clean["clean_markdown_path"] if clean else None,
            "changes_count": result["metrics"].get("changes_count", 0),
            "tables_fixed": result["metrics"].get("tables_fixed", 0),
            "figures_preserved": len(clean["figure_map"]["figures"]) if clean else 0,
            "errors": result["errors"], "status": result["status"],
            "input_hash": result["provenance"]["input_hash"],
            "output_hash": result["provenance"]["output_hash"]
        }
        try:
            self.logger(event)
        except Exception:
            pass
        return result

    @staticmethod
    def _failure(err, input_hash):
        return {
            "status": "terminal_failure", "output": None, "artifacts": [],
            "self_check": {"passed": False, "checks": [], "score": 0.0},
            "warnings": [], "errors": [err], "metrics": {},
            "provenance": {
                "skill_id": SKILL_ID, "skill_version": SKILL_VERSION,
                "input_hash": input_hash, "output_hash": None
            },
            "review_requests": []
        }


def execute(request: Mapping[str, Any], **kwargs: Any) -> Dict[str, Any]:
    return ScientificMarkdownCleaner(**kwargs).execute(request)

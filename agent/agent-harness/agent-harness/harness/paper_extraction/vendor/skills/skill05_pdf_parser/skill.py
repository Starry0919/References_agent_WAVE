from __future__ import annotations

import json
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, Mapping, Optional

try:
    from .artifact import DocumentManager
    from .error_codes import error
    from .logger import JsonlSkillLogger
    from .parsers import MinerUParser, PyMuPdfParser
    from .reconstruction import reconstruct_sections, extract_figures, extract_tables, extract_references
    from .schema import SKILL_ID, SKILL_VERSION, sha256_json
    from .validator import quality_report, validate_input_artifact
except ImportError:
    from artifact import DocumentManager
    from error_codes import error
    from logger import JsonlSkillLogger
    from parsers import MinerUParser, PyMuPdfParser
    from reconstruction import reconstruct_sections, extract_figures, extract_tables, extract_references
    from schema import SKILL_ID, SKILL_VERSION, sha256_json
    from validator import quality_report, validate_input_artifact


class PdfStructureParsingSkill:
    def __init__(
        self,
        mineru_parser=None,
        fallback_parser=None,
        output_root: Optional[Path] = None,
        logger: Optional[Callable[[Mapping[str, Any]], None]] = None,
        clock: Optional[Callable[[], datetime]] = None,
    ):
        module_root = Path(__file__).resolve().parents[2]
        self.mineru = mineru_parser or MinerUParser()
        self.fallback = fallback_parser or PyMuPdfParser()
        self.output_root = Path(output_root or module_root / "document_artifacts").resolve()
        self.manager = DocumentManager()
        self.logger = logger if logger is not None else JsonlSkillLogger()
        self.clock = clock or (lambda: datetime.now(timezone.utc))

    def execute(self, request: Mapping[str, Any]) -> Dict[str, Any]:
        started = time.perf_counter()
        input_hash = sha256_json(request)
        artifact = request.get("paper_artifact") if isinstance(request, Mapping) else None
        if not isinstance(artifact, Mapping):
            return self._finish(self._failure(error("PARSE001", {"field": "paper_artifact"}), input_hash), started)
        valid, reason = validate_input_artifact(artifact)
        if not valid:
            return self._finish(self._failure(error("PARSE001", {"reason": reason}), input_hash), started)

        pdf_path = Path(artifact["file_information"]["path"]).resolve()
        checksum = artifact["integrity"]["checksum_value"]
        paper_id = str(artifact.get("paper_identity", {}).get("paper_id") or "unknown")
        policy = request.get("parse_policy") or {}
        requested_mode = policy.get("mode", "pipeline")
        timeout_seconds = int(policy.get("timeout_seconds", 1800))
        safe_id = re.sub(r"[^A-Za-z0-9._-]+", "_", paper_id).strip("._") or "unknown"
        run_name = self.clock().strftime("%Y%m%dT%H%M%S_%f")
        run_root = self.output_root / safe_id / checksum[:12] / run_name
        attempts = []
        parse_result = None

        plans = [
            (self.mineru, requested_mode),
            (self.mineru, "pipeline"),
            (self.fallback, "fallback")
        ]
        for number, (parser, mode) in enumerate(plans, 1):
            attempt_root = run_root / f"attempt_{number}_{mode}"
            try:
                parse_result = parser.parse(pdf_path, attempt_root, mode=mode, timeout_seconds=timeout_seconds)
                markdown = parse_result.markdown_path.read_text(encoding="utf-8", errors="replace")
                if not markdown.strip():
                    raise ValueError("empty Markdown")
                attempts.append({
                    "attempt": number, "parser": parse_result.parser,
                    "mode": parse_result.mode, "status": "succeeded",
                    "command": parse_result.command
                })
                break
            except Exception as exc:
                attempts.append({
                    "attempt": number, "parser": getattr(parser, "name", type(parser).__name__),
                    "mode": mode, "status": "failed", "error_type": type(exc).__name__,
                    "message": str(exc),
                })

        if parse_result is None:
            return self._finish(
                self._failure(error("PARSE002", {"attempts": attempts}), input_hash),
                started
            )

        markdown = parse_result.markdown_path.read_text(encoding="utf-8", errors="replace")
        content_list = self._load_content_list(parse_result.content_list_path)
        sections = reconstruct_sections(markdown, content_list)
        figures = extract_figures(markdown, content_list)
        tables = extract_tables(markdown, content_list)
        references = extract_references(markdown, sections)
        quality = quality_report(markdown, sections, figures, tables, content_list)
        parse_status = "partial" if quality["missing_content"] else "complete"
        all_outputs = list(parse_result.output_files) + [parse_result.markdown_path]
        if parse_result.content_list_path:
            all_outputs.append(parse_result.content_list_path)
        derived = self.manager.collect(all_outputs, parse_result.parser)
        section_index = [
            {"section_id": v["section_id"], "title": v["title"], "level": v["level"]}
            for v in sections
        ]
        document = {
            "artifacts": derived,
            "parse_status": parse_status,
            "section_index": section_index
        }
        document_artifact = {
            "document_metadata": {
                "paper_id": paper_id, "pdf_path": str(pdf_path),
                "input_pdf_checksum": checksum,
                "parser": parse_result.parser,
                "parser_version": parse_result.parser_version,
                "parser_mode": parse_result.mode,
                "parse_time": self.clock().isoformat()
            },
            "markdown_artifact": {
                "markdown_path": str(parse_result.markdown_path.resolve()),
                "markdown_content": markdown
            },
            "structure_map": {"sections": sections},
            "figure_map": {"figures": figures},
            "table_map": {"tables": tables},
            "reference_map": references,
            "parsing_quality_report": quality,
            "parse_attempts": attempts,
            "processing_status": parse_status
        }
        output = {
            "document": document,
            "document_artifact": document_artifact,
            "derived_artifacts": derived
        }
        checks = self._self_check(artifact, output, content_list)
        if not all(v["passed"] for v in checks if v["name"] in {"input_checksum", "markdown_nonempty", "scientific_text_presence"}):
            return self._finish(self._failure(error("PARSE003", {"checks": checks}), input_hash), started)
        warnings = []
        review_requests = []
        if parse_status == "partial":
            warnings.append({
                "code": "PARSE004",
                "message": "Document structure reconstruction is partial.",
                "missing_content": quality["missing_content"],
            })
            review_requests.append({"reason": "partial_structure_reconstruction", "paper_id": paper_id})
        if not checks[-1]["passed"]:
            warnings.append({"code": "PARSE005", "message": "Figure/table count differs from parser content list."})
            review_requests.append({"reason": "figure_table_count_mismatch", "paper_id": paper_id})
        status = "succeeded_with_warnings" if warnings else "succeeded"
        result = {
            "status": status, "output": output, "artifacts": derived,
            "self_check": {
                "passed": all(v["passed"] for v in checks),
                "checks": checks,
                "score": sum(v["passed"] for v in checks) / len(checks)
            },
            "warnings": warnings, "errors": [],
            "metrics": {
                "sections": len(sections), "figures": len(figures),
                "tables": len(tables), "references": len(references["references"])
            },
            "provenance": {
                "skill_id": SKILL_ID, "skill_version": SKILL_VERSION,
                "input_hash": input_hash, "output_hash": sha256_json(output),
                "source_artifact_id": artifact.get("artifact_ref", {}).get("artifact_id"),
                "source_sha256": checksum, "parser": parse_result.parser,
                "parser_version": parse_result.parser_version,
                "mode": parse_result.mode, "command": parse_result.command
            },
            "review_requests": review_requests
        }
        return self._finish(result, started)

    @staticmethod
    def _load_content_list(path):
        if not path or not Path(path).is_file():
            return []
        try:
            value = json.loads(Path(path).read_text(encoding="utf-8"))
            return value if isinstance(value, list) else []
        except (json.JSONDecodeError, OSError):
            return []

    @staticmethod
    def _self_check(input_artifact, output, content_list):
        doc = output["document_artifact"]
        markdown = doc["markdown_artifact"]["markdown_content"]
        figures = doc["figure_map"]["figures"]
        tables = doc["table_map"]["tables"]
        parser_figures = sum(v.get("type") in {"image", "figure"} for v in content_list)
        parser_tables = sum(v.get("type") == "table" for v in content_list)
        return [
            {"name": "input_checksum", "passed": doc["document_metadata"]["input_pdf_checksum"] == input_artifact["integrity"]["checksum_value"]},
            {"name": "markdown_nonempty", "passed": bool(markdown.strip())},
            {"name": "section_reconstruction", "passed": bool(doc["structure_map"]["sections"])},
            {"name": "scientific_text_presence", "passed": len(markdown.strip()) >= 20},
            {"name": "figure_table_count_consistency", "passed": parser_figures == len(figures) and parser_tables == len(tables)}
        ]

    def _finish(self, result, started):
        result["metrics"]["duration_ms"] = round((time.perf_counter() - started) * 1000, 3)
        doc = result.get("output", {}).get("document_artifact") if result.get("output") else None
        event = {
            "skill_name": SKILL_ID,
            "paper_id": doc["document_metadata"]["paper_id"] if doc else None,
            "parser": doc["document_metadata"]["parser"] if doc else None,
            "parser_version": doc["document_metadata"]["parser_version"] if doc else None,
            "input_pdf_checksum": doc["document_metadata"]["input_pdf_checksum"] if doc else None,
            "output_markdown_path": doc["markdown_artifact"]["markdown_path"] if doc else None,
            "figures_detected": len(doc["figure_map"]["figures"]) if doc else 0,
            "tables_detected": len(doc["table_map"]["tables"]) if doc else 0,
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
    return PdfStructureParsingSkill(**kwargs).execute(request)


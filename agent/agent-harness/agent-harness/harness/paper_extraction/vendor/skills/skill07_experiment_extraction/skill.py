from __future__ import annotations

import json
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, Mapping, Optional

try:
    from .error_codes import error
    from .extension import build_workflow, analyze_variables, build_design_logic
    from .extractor import (
        extract_objective, extract_hypothesis, extract_biological_system,
        extract_engineering, extract_groups_controls, extract_conditions,
        extract_measurements, extract_outcomes
    )
    from .extractor.common import metadata, paragraphs
    from .logger import JsonlSkillLogger
    from .schema import CORE_FIELDS, SKILL_ID, SKILL_VERSION, reported_field, sha256_json, unknown_field
    from .validator import validate_output
except ImportError:
    from error_codes import error
    from extension import build_workflow, analyze_variables, build_design_logic
    from extractor import (
        extract_objective, extract_hypothesis, extract_biological_system,
        extract_engineering, extract_groups_controls, extract_conditions,
        extract_measurements, extract_outcomes
    )
    from extractor.common import metadata, paragraphs
    from logger import JsonlSkillLogger
    from schema import CORE_FIELDS, SKILL_ID, SKILL_VERSION, reported_field, sha256_json, unknown_field
    from validator import validate_output


class ExperimentalDesignExtractor:
    def __init__(
        self,
        logger: Optional[Callable[[Mapping[str, Any]], None]] = None,
        clock: Optional[Callable[[], datetime]] = None,
    ):
        self.logger = logger if logger is not None else JsonlSkillLogger()
        self.clock = clock or (lambda: datetime.now(timezone.utc))

    def execute(self, request: Mapping[str, Any]) -> Dict[str, Any]:
        started = time.perf_counter()
        input_hash = sha256_json(request)
        artifact = request.get("clean_document_artifact") if isinstance(request, Mapping) else None
        if not isinstance(artifact, Mapping):
            return self._finish(self._failure(error("EXP001"), input_hash), started)
        clean_json = self._load_clean_json(artifact)
        if not clean_json or not clean_json.get("paragraphs"):
            return self._finish(self._failure(error("EXP001", {"reason": "clean_json_missing_or_empty"}), input_hash), started)

        items = paragraphs(clean_json)
        objective, objective_sources = extract_objective(items)
        hypothesis, hypothesis_sources = extract_hypothesis(items)
        biological, biological_sources = extract_biological_system(items)
        engineering, engineering_sources = extract_engineering(items)
        groups, controls, group_sources = extract_groups_controls(items)
        conditions, condition_sources = extract_conditions(items)
        measurements, measurement_sources = extract_measurements(items)
        outcomes, _, outcome_sources = extract_outcomes(items)

        source_map = {
            "objective": objective_sources, "hypothesis": hypothesis_sources,
            "strain": biological_sources, "genotype": biological_sources,
            "engineering_method": engineering_sources,
            "experimental_groups": group_sources, "controls": group_sources,
            "culture_conditions": condition_sources, "medium": condition_sources,
            "dosage": condition_sources, "time": condition_sources,
            "replicates": measurement_sources, "assay": measurement_sources,
            "instruments": measurement_sources, "analysis_methods": measurement_sources,
            "outcomes": outcome_sources
        }
        values = {
            "objective": objective or None,
            "hypothesis": hypothesis or None,
            "strain": biological if biological["organism"] or biological["strain"] else None,
            "genotype": biological["genotype"] or None,
            "engineering_method": engineering if engineering["methods"] else None,
            "experimental_groups": groups or None,
            "controls": controls or None,
            "culture_conditions": {
                key: conditions[key] for key in ("temperature", "volume", "agitation", "od", "carbon_source")
            } if any(conditions[key] for key in ("temperature", "volume", "agitation", "od", "carbon_source")) else None,
            "medium": conditions["medium"] or None,
            "dosage": conditions["dosage"] or None,
            "time": conditions["time"] or None,
            "replicates": measurements["replicates"] or None,
            "assay": measurements["assays"] or None,
            "instruments": measurements["instruments"] or None,
            "analysis_methods": measurements["analysis_methods"] or None,
            "outcomes": outcomes if outcomes["observed_outcomes"] or outcomes["author_conclusions"] else None
        }
        fields, field_metadata = {}, {}
        for name in CORE_FIELDS:
            candidates = source_map[name] if values[name] is not None else []
            fields[name] = reported_field(values[name], candidates) if values[name] is not None and candidates else unknown_field()
            field_metadata[name] = {
                "value": fields[name]["value"], "status": fields[name]["status"],
                "confidence": fields[name]["confidence"],
                "source_locations": metadata(candidates),
                "extraction_method": "rule_based" if candidates else "not_applicable"
            }

        conflicts = self._detect_conflicts(condition_sources)
        extensions = {
            "experiment_workflow": {"workflow": build_workflow(clean_json)},
            "variables": analyze_variables(groups, engineering, conditions, measurements),
            "design_logic": build_design_logic(objective, hypothesis, measurements, outcomes),
            "biological_system": biological
        }
        experimental_design = {name: fields[name]["value"] for name in CORE_FIELDS}
        experimental_design_object = {
            "paper_id": artifact.get("document_metadata", {}).get("paper_id"),
            "experimental_design": experimental_design,
            "field_metadata": field_metadata,
            "extensions": extensions
        }
        source_ids = {v["paragraph_id"] for v in items}
        checks = validate_output(fields, field_metadata, source_ids)
        if not all(v["passed"] for v in checks):
            return self._finish(self._failure(error("EXP004", {"failed_checks": [v["name"] for v in checks if not v["passed"]]}), input_hash), started)

        reported_count = sum(v["status"] == "reported" for v in fields.values())
        unknown_count = sum(v["status"] == "unknown" for v in fields.values())
        warnings, review_requests = [], []
        if conflicts:
            warnings.append({"code": "EXP003", "conflicts": conflicts})
            review_requests.append({"reason": "field_conflict", "fields": sorted({v["field"] for v in conflicts})})
        if unknown_count:
            warnings.append({"code": "EXP002", "unknown_fields": [k for k, v in fields.items() if v["status"] == "unknown"]})
        critical_unknown = [name for name in ("strain", "engineering_method", "experimental_groups", "culture_conditions") if fields[name]["status"] == "unknown"]
        if critical_unknown:
            review_requests.append({"reason": "critical_unknown", "fields": critical_unknown})
        status = "needs_review" if conflicts else ("succeeded_with_warnings" if warnings else "succeeded")
        output = {
            "fields": fields,
            "experimental_design_object": experimental_design_object,
            "field_metadata": field_metadata,
            "extensions": extensions,
            "conflicts": conflicts
        }
        result = {
            "status": status, "output": output, "artifacts": [],
            "self_check": {"passed": True, "checks": checks, "score": 1.0},
            "warnings": warnings, "errors": [],
            "metrics": {
                "fields_extracted": reported_count, "reported_fields": reported_count,
                "unknown_fields": unknown_count, "inferred_fields": 0
            },
            "provenance": {
                "skill_id": SKILL_ID, "skill_version": SKILL_VERSION,
                "input_hash": input_hash, "output_hash": sha256_json(output),
                "source_artifact_id": artifact.get("clean_json_path"),
                "source_sha256": artifact.get("document_metadata", {}).get("clean_markdown_sha256"),
                "extractor": "deterministic_rules",
                "candidate_locations": sorted(source_ids)
            },
            "review_requests": review_requests
        }
        return self._finish(result, started)

    @staticmethod
    def _load_clean_json(artifact):
        path = artifact.get("clean_json_path")
        if path and Path(path).is_file():
            try:
                return json.loads(Path(path).read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                return None
        if "structure_map" in artifact:
            return {
                "document_metadata": artifact.get("document_metadata", {}),
                "sections": artifact.get("structure_map", {}).get("sections", []),
                "paragraphs": artifact.get("structure_map", {}).get("paragraphs", []),
                "figures": artifact.get("figure_map", {}).get("figures", []),
                "tables": artifact.get("table_map", {}).get("tables", []),
                "citations": artifact.get("citation_map", {}).get("citations", [])
            }
        return None

    @staticmethod
    def _detect_conflicts(condition_sources):
        values = []
        pattern = re.compile(r"\b\d+(?:\.\d+)?\s*(?:°C|℃)")
        for source in condition_sources:
            for value in pattern.findall(source["text"]):
                values.append({"value": re.sub(r"\s+", "", value), "source": source["paragraph_id"], "section": source["section"]})
        conflicts = []
        methods = {v["value"] for v in values if "method" in v["section"].casefold()}
        legends = {v["value"] for v in values if v["source"].startswith(("figure:", "table:"))}
        if methods and legends and methods != legends:
            conflicts.append({
                "field": "culture_conditions.temperature",
                "candidate_values": values, "status": "open",
                "reason": "Methods and figure/table legend report different values."
            })
        return conflicts

    def _finish(self, result, started):
        result["metrics"]["duration_ms"] = round((time.perf_counter() - started) * 1000, 3)
        output = result.get("output")
        event = {
            "skill_name": SKILL_ID,
            "paper_id": output.get("experimental_design_object", {}).get("paper_id") if output else None,
            "fields_extracted": result["metrics"].get("fields_extracted", 0),
            "reported_fields": result["metrics"].get("reported_fields", 0),
            "unknown_fields": result["metrics"].get("unknown_fields", 0),
            "inferred_fields": result["metrics"].get("inferred_fields", 0),
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
    return ExperimentalDesignExtractor(**kwargs).execute(request)


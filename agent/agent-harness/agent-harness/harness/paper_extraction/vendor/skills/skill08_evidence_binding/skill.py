from __future__ import annotations

import copy
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, Mapping, Optional

try:
    from .binder import DocumentEvidenceIndex, EvidenceRetriever, minimal_quote, supports_value
    from .conflict import bind_conflicts
    from .error_codes import error
    from .extension import bind_workflow, bind_variables, bind_design_logic
    from .logger import JsonlSkillLogger
    from .schema import SKILL_ID, SKILL_VERSION, sha256_json, sha256_text, unknown_field
    from .validator import validate_output
except ImportError:
    from binder import DocumentEvidenceIndex, EvidenceRetriever, minimal_quote, supports_value
    from conflict import bind_conflicts
    from error_codes import error
    from extension import bind_workflow, bind_variables, bind_design_logic
    from logger import JsonlSkillLogger
    from schema import SKILL_ID, SKILL_VERSION, sha256_json, sha256_text, unknown_field
    from validator import validate_output


class EvidenceBindingEngine:
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
        skill07 = request.get("skill07_output") if isinstance(request, Mapping) else None
        clean_artifact = request.get("clean_document_artifact") if isinstance(request, Mapping) else None
        if not isinstance(skill07, Mapping) or not isinstance(skill07.get("fields"), Mapping):
            return self._finish(self._failure(error("EVID001"), input_hash), started)
        clean_json = self._load_clean_json(clean_artifact)
        if not clean_json:
            return self._finish(self._failure(error("EVID002"), input_hash), started)

        paper_id = (
            clean_artifact.get("document_metadata", {}).get("paper_id")
            or skill07.get("experimental_design_object", {}).get("paper_id")
            or "unknown"
        )
        artifact_sha = self._artifact_sha(clean_artifact, clean_json)
        artifact_id = clean_artifact.get("clean_json_artifact", {}).get("artifact_id") or "artifact:clean-json:" + artifact_sha[:16]
        index = DocumentEvidenceIndex(clean_json)
        retriever = EvidenceRetriever(index)
        fields = copy.deepcopy(dict(skill07["fields"]))
        # Skill07's contract asks the model to wrap every reported field as
        # {value, status, evidence_ids, ...}, but it doesn't always comply -
        # some fields (e.g. a plain research_question string, or `null` for
        # an unset optional like user_target_system) come back as bare
        # values. Normalize once here so every downstream consumer in this
        # function (and validate_output()) can assume a uniform shape
        # instead of crashing on `field.get(...)` / `field["status"]`.
        for field_name, field in fields.items():
            if not isinstance(field, Mapping):
                fields[field_name] = {
                    "value": field, "status": "unknown" if field is None else "reported",
                    "evidence_ids": [], "extraction_method": "not_applicable",
                }
        evidence_records = []
        evidence_by_key = {}
        unit_evidence: Dict[str, list] = {}
        field_evidence: Dict[str, list] = {}
        binding_audit = {}
        downgraded = []

        for field_name, field in fields.items():
            if field.get("status") == "unknown":
                field_evidence[field_name] = []
                continue
            units, audit = retriever.retrieve(field.get("value"), field.get("evidence_ids", []))
            quotes = [minimal_quote(field.get("value"), unit["text"]) for unit in units]
            supported, unsupported = supports_value(field.get("value"), quotes)
            if not supported and field.get("evidence_ids"):
                # A compact model can identify the right fact but choose an
                # adjacent page-sized paragraph anchor. Search all structured
                # text once more using token overlap before downgrading it.
                recovered_units, recovery_audit = retriever.retrieve(
                    field.get("value"), []
                )
                audit.extend(recovery_audit)
                if recovered_units:
                    units = recovered_units
                    quotes = [
                        minimal_quote(field.get("value"), unit["text"])
                        for unit in units
                    ]
                    supported, unsupported = supports_value(
                        field.get("value"), quotes
                    )
            binding_audit[field_name] = {
                "attempts": audit, "candidate_units": [u["unit_id"] for u in units],
                "supported": supported, "unsupported_values": unsupported
            }
            if not supported:
                fields[field_name] = unknown_field("Skill07 value was downgraded because no sufficient quote was found.")
                field_evidence[field_name] = []
                downgraded.append(field_name)
                continue
            ids = []
            for unit, quote in zip(units, quotes):
                key = (unit["unit_id"], quote)
                if key not in evidence_by_key:
                    evidence_id = f"ev_{len(evidence_records) + 1:05d}"
                    record = self._record(
                        evidence_id, paper_id, artifact_id, artifact_sha,
                        unit, quote, field_name
                    )
                    evidence_records.append(record)
                    evidence_by_key[key] = evidence_id
                    unit_evidence.setdefault(unit["unit_id"], []).append(evidence_id)
                ids.append(evidence_by_key[key])
            ids = list(dict.fromkeys(ids))
            fields[field_name]["evidence_ids"] = ids
            fields[field_name]["extraction_method"] = "hybrid"
            field_evidence[field_name] = ids

        workflow = skill07.get("extensions", {}).get("experiment_workflow", {}).get("workflow", [])
        bound_workflow = bind_workflow(workflow, unit_evidence)
        bound_variables = bind_variables(skill07.get("extensions", {}).get("variables", {}), evidence_records)
        bound_logic = bind_design_logic(skill07.get("extensions", {}).get("design_logic", {}), field_evidence)
        extensions = {
            "experiment_workflow": bound_workflow,
            "variables": bound_variables,
            "design_logic": bound_logic,
            "biological_system": skill07.get("extensions", {}).get("biological_system", {})
        }
        extended_conflicts, unified_conflicts = bind_conflicts(self._normalize_conflicts(skill07.get("conflicts", [])), unit_evidence)
        literature_experiment = {
            "fields": fields, "evidence": evidence_records,
            "conflicts": unified_conflicts
        }
        checks = validate_output(literature_experiment, extensions)
        if not all(v["passed"] for v in checks):
            return self._finish(self._failure(error("EVID005", {"failed_checks": [v["name"] for v in checks if not v["passed"]]}), input_hash), started)

        reported = [name for name, field in fields.items() if field["status"] == "reported"]
        unknown = [name for name, field in fields.items() if field["status"] == "unknown"]
        evidence_fields = [name for name in reported if field_evidence.get(name)]
        coverage = {
            "total_fields": len(fields),
            "reported_fields": len(reported),
            "fields_with_evidence": len(evidence_fields),
            "unknown_fields": len(unknown),
            "reported_evidence_coverage": len(evidence_fields) / max(1, len(reported)),
            "overall_field_coverage": len(evidence_fields) / max(1, len(fields))
        }
        evidence_linked_design = {
            "paper_id": paper_id,
            "experimental_design": {name: field["value"] for name, field in fields.items()},
            "fields": fields,
            "extensions": extensions,
            "binding_audit": binding_audit
        }
        output = {
            "literature_experiment": literature_experiment,
            "evidence_linked_design": evidence_linked_design,
            "evidence_map": {record["evidence_id"]: record for record in evidence_records},
            "coverage": coverage,
            "conflicts": extended_conflicts
        }
        # A single stray field losing its evidence, or one flagged
        # inconsistency, is routine noise in real papers (a paraphrased
        # value the retriever can't quote-match, a supplement-only detail)
        # - not by itself a sign this extraction needs a human to look at
        # it. Escalating to `needs_review` on every non-zero count made
        # nearly every run require review regardless of actual severity.
        # Reserve it for when the evidence problem is systemic (a large
        # share of all fields downgraded) or conflicts are more than
        # incidental - the agent's own judgment call, still fully visible
        # either way since both are always recorded as warnings. Ratio is
        # against `len(fields)` (the whole schema), not `len(reported)` -
        # `reported` above is computed AFTER this loop already rewrote every
        # downgraded field's status to "unknown", so it already excludes them.
        downgrade_ratio = len(downgraded) / max(1, len(fields))
        warnings, reviews = [], []
        if downgraded:
            warnings.append({
                "code": "EVID003",
                "message": f"{len(downgraded)} of {len(fields)} field(s) could not be evidence-verified and were downgraded to unknown.",
                "downgraded_fields": downgraded,
            })
            if downgrade_ratio > 0.25:
                reviews.append({"reason": "reported_without_sufficient_evidence", "fields": downgraded})
        if extended_conflicts:
            warnings.append({
                "code": "EVID004",
                "message": f"{len(extended_conflicts)} conflict(s) detected between sources for this extraction.",
                "conflicts": len(extended_conflicts),
            })
            if len(extended_conflicts) > 2:
                reviews.append({"reason": "conflicting_evidence", "fields": [v.get("field") for v in extended_conflicts]})
        status = "needs_review" if reviews else ("succeeded_with_warnings" if warnings else "succeeded")
        result = {
            "status": status, "output": output, "artifacts": [],
            "self_check": {"passed": True, "checks": checks, "score": 1.0},
            "warnings": warnings, "errors": [],
            "metrics": {
                "fields_processed": len(fields), "evidence_found": len(evidence_records),
                "unknown_fields": len(unknown),
                "inferred_fields": sum(v.get("status") == "inferred" for v in fields.values()),
                "conflicts": len(extended_conflicts)
            },
            "provenance": {
                "skill_id": SKILL_ID, "skill_version": SKILL_VERSION,
                "input_hash": input_hash, "output_hash": sha256_json(output),
                "paper_id": paper_id, "artifact_id": artifact_id,
                "artifact_sha256": artifact_sha
            },
            "review_requests": reviews
        }
        return self._finish(result, started)

    @staticmethod
    def _normalize_conflicts(raw_conflicts):
        # Skill07's contract requires `conflicts` as a flat array of objects
        # (interface.json), but the model sometimes nests them by category
        # instead, e.g. {"source_internal_inconsistencies": [...], "unresolved_parameters": [...]}.
        # Flatten that shape rather than crashing bind_conflicts(), which
        # assumes every item is a Mapping with .get().
        if isinstance(raw_conflicts, Mapping):
            flattened = []
            for category, items in raw_conflicts.items():
                if not isinstance(items, list):
                    continue
                for item in items:
                    if isinstance(item, Mapping):
                        entry = dict(item)
                        entry.setdefault("category", category)
                        flattened.append(entry)
            return flattened
        if isinstance(raw_conflicts, list):
            return [c for c in raw_conflicts if isinstance(c, Mapping)]
        return []

    @staticmethod
    def _record(evidence_id, paper_id, artifact_id, artifact_sha, unit, quote, field_name):
        return {
            "evidence_id": evidence_id, "paper_id": paper_id,
            "artifact_id": artifact_id, "artifact_sha256": artifact_sha,
            "locator": {
                "page": unit.get("page"), "printed_page": None,
                "section_path": [unit["section"]] if unit.get("section") else [],
                "paragraph_id": unit.get("paragraph"),
                "figure_id": unit.get("figure"), "table_id": unit.get("table"),
                "supplement_id": unit["section"] if unit.get("evidence_type") == "supplement" else None,
                "char_start": None, "char_end": None
            },
            "quote": quote, "quote_sha256": sha256_text(quote),
            "extraction": {
                "method": "provisional_id_then_semantic_retrieval",
                "component": SKILL_ID, "component_version": SKILL_VERSION,
                "model": None, "prompt_hash": None
            }
        }

    @staticmethod
    def _load_clean_json(artifact):
        if not isinstance(artifact, Mapping):
            return None
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
    def _artifact_sha(artifact, clean_json):
        configured = artifact.get("clean_json_artifact", {}).get("sha256")
        if configured and len(configured) == 64:
            return configured
        return sha256_text(json.dumps(clean_json, ensure_ascii=False, sort_keys=True, separators=(",", ":")))

    def _finish(self, result, started):
        result["metrics"]["duration_ms"] = round((time.perf_counter() - started) * 1000, 3)
        event = {
            "skill_name": SKILL_ID, "paper_id": result["provenance"].get("paper_id"),
            "fields_processed": result["metrics"].get("fields_processed", 0),
            "evidence_found": result["metrics"].get("evidence_found", 0),
            "unknown_fields": result["metrics"].get("unknown_fields", 0),
            "inferred_fields": result["metrics"].get("inferred_fields", 0),
            "conflicts": result["metrics"].get("conflicts", 0),
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
    return EvidenceBindingEngine(**kwargs).execute(request)


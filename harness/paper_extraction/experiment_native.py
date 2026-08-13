"""Additive Skill07 V3 experiment-native representation and validation."""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from jsonschema import Draft202012Validator

SCHEMA_DIR = Path(__file__).with_name("schemas")
REPRESENTATION_VERSION = "skill07_experiment_native_v3"
NORMALIZATION_VERSION = "experiment-native-migration/3.1.0"


def stable_id(kind: str, document_id: str, local_identity: Any) -> str:
    """Return an order-independent ID from document identity and source-local identity."""
    canonical = json.dumps(local_identity, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(f"{document_id}\n{canonical}".encode("utf-8")).hexdigest()[:20]
    return f"{kind}:{digest}"


def _load(name: str) -> dict[str, Any]:
    return json.loads((SCHEMA_DIR / name).read_text(encoding="utf-8"))


def _scalar(value: Any) -> str:
    if isinstance(value, str):
        return value
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def _bundle(locations: list[Any], evidence_ids: list[Any], document_id: str = "legacy:unresolved") -> list[dict[str, Any]]:
    out = []
    for location in locations:
        if not isinstance(location, Mapping):
            continue
        locator = location.get("paragraph_id") or location.get("figure") or location.get("table") or location.get("supplement")
        if not locator:
            continue
        source_type = "figure" if location.get("figure") else "table" if location.get("table") else "supplement" if location.get("supplement") else "main_text"
        out.append({"evidence_span_id": stable_id("span", document_id, {"locator": locator, "section": location.get("section")}),
                    "source_type": source_type, "section": str(location.get("section") or ""), "locator": str(locator),
                    "quote": str(location.get("quote") or ""), "source_attribution": location.get("source_attribution") or "unknown",
                    "evidence_role": "candidate"})
    if not out:
        out.extend({"source_type": "unresolved", "section": "", "locator": str(item), "quote": "",
                    "source_attribution": "unknown", "evidence_role": "candidate"} for item in evidence_ids)
    return out or [{"source_type": "unresolved", "section": "", "locator": "unresolved:candidate-evidence-missing", "quote": "",
                    "source_attribution": "unknown", "evidence_role": "candidate"}]


def migrate_additively(output: dict[str, Any], document_id: str | None = None, paper_id: str | None = None) -> list[dict[str, Any]]:
    """Add structure without asserting new scientific facts."""
    actions = []
    document_id = document_id or str(output.get("document_id") or output.get("source_document_hash") or "legacy:unresolved")
    paper_id = paper_id or str(output.get("paper_id") or "legacy:unresolved")
    output.setdefault("representation_version", REPRESENTATION_VERSION)
    if "projection_metadata" not in output:
        output["projection_metadata"] = {"derived_projection": True, "canonical_source": "experiment_instances", "legacy_compatibility": True}
        actions.append({"action": "add_projection_metadata", "classification": "v3_structural_compatibility"})
    design = output.get("experimental_design_object") if isinstance(output.get("experimental_design_object"), Mapping) else {}
    legacy = design.get("experiments") if isinstance(design.get("experiments"), list) else []
    if "experiment_instances" not in output:
        instances = []
        for index, item in enumerate(legacy):
            item = item if isinstance(item, Mapping) else {}
            evidence = [str(x).removeprefix("candidate:") for x in item.get("evidence", []) if isinstance(x, str)]
            local_identity = {"legacy_id": item.get("experiment_id"), "evidence": sorted(evidence)}
            identity_resolved = document_id != "legacy:unresolved" and bool(evidence or item.get("experiment_id"))
            instances.append({"experiment_id": str(item.get("experiment_id") or stable_id("experiment", document_id, local_identity)),
                              "paper_id": paper_id, "document_id": document_id, "representation_version": "3.1.0",
                              "experiment_scope": {"experiment_type": "unresolved", "purpose": "unresolved", "experimental_question": "unresolved", "parent_experiment_id": None, "related_experiment_ids": []},
                              "biological_context": {"organism": "unresolved", "strain": "unresolved", "genotype": "unresolved", "cell_line_or_system": "unresolved", "biological_object_ids": []},
                              "biological_objects": [], "interventions": [], "conditions": [], "controls": [],
                              "measurements": [], "outcomes": [], "evidence_links": evidence,
                              "rationale": {"status": "unresolved"}, "interpretation": {"status": "unresolved"}, "limitations": [],
                              "provenance": {"source_version": "legacy", "normalization_version": NORMALIZATION_VERSION, "identity_resolved": identity_resolved},
                              "extraction_status": "MIGRATED_REVIEW_REQUIRED", "uncertainty": ["legacy projection may be lossy"],
                              "migration_generated": True, "review_required": True, "legacy_payload": copy.deepcopy(dict(item))})
        if not instances:
            instances = [{"experiment_id": stable_id("experiment", document_id, {"local_identity": "document_projection"}),
                          "paper_id": paper_id, "document_id": document_id, "representation_version": "3.1.0",
                          "experiment_scope": {"experiment_type": "unresolved", "purpose": "unresolved", "experimental_question": "unresolved", "parent_experiment_id": None, "related_experiment_ids": []},
                          "biological_context": {"organism": "unresolved", "strain": "unresolved", "genotype": "unresolved", "cell_line_or_system": "unresolved", "biological_object_ids": []},
                          "biological_objects": [], "interventions": [],
                          "conditions": [], "controls": [], "measurements": [], "outcomes": [], "evidence_links": [],
                          "rationale": {"status": "unresolved"}, "interpretation": {"status": "unresolved"}, "limitations": [],
                          "provenance": {"source_version": "legacy", "normalization_version": NORMALIZATION_VERSION, "identity_resolved": False},
                          "extraction_status": "MIGRATED_REVIEW_REQUIRED", "uncertainty": ["experiment boundary unresolved"],
                          "migration_generated": True, "review_required": True, "legacy_payload": copy.deepcopy(output.get("experimental_design_object"))}]
        output["experiment_instances"] = instances
        actions.append({"action": "migrate_legacy_experiments", "count": len(instances), "classification": "v3_structural_compatibility"})
    if "atomic_claims" not in output:
        experiment_id = output["experiment_instances"][0]["experiment_id"]
        metadata = output.get("field_metadata") if isinstance(output.get("field_metadata"), Mapping) else {}
        claims = []
        for name, field in (output.get("fields") or {}).items():
            if not isinstance(field, Mapping) or field.get("value") in (None, "", [], {}):
                continue
            meta = metadata.get(name) if isinstance(metadata.get(name), Mapping) else {}
            bundle = _bundle(meta.get("source_locations") or [], field.get("evidence_ids") or [], document_id)
            bundle_id = stable_id("evidence-bundle", document_id, sorted(x["locator"] for x in bundle))
            claims.append({"claim_id": stable_id("claim", document_id, {"experiment_id": experiment_id, "field": name, "locators": sorted(x["locator"] for x in bundle)}),
                           "paper_id": paper_id, "document_id": document_id, "experiment_id": experiment_id,
                           "claim_type": "LEGACY_FIELD_CANDIDATE",
                           "subject": experiment_id, "predicate": name, "object": _scalar(field["value"]),
                           "qualifiers": {}, "normalized_form": None, "human_readable_claim": _scalar(field["value"]), "criticality": "UNASSESSED",
                           "value": None, "unit": None, "epistemic_status": field.get("status", "unknown"),
                           "evidence_bundle_ids": [bundle_id], "evidence_bundle": bundle,
                           "source_attribution": meta.get("source_attribution", "unknown"),
                           "provenance": {"source_version": "legacy", "normalization_version": NORMALIZATION_VERSION, "raw_field": name},
                           "extraction_confidence": field.get("confidence"), "binding_status": "REVIEW_REQUIRED", "verification_status": "UNVERIFIED",
                           "migration_generated": True, "review_required": True})
        output["atomic_claims"] = claims
        actions.append({"action": "derive_review_required_claim_candidates", "count": len(claims), "classification": "v3_structural_compatibility"})
    return actions


def validate_native(output: Mapping[str, Any]) -> list[str]:
    failures = []
    instances = output.get("experiment_instances")
    claims = output.get("atomic_claims")
    if not isinstance(instances, list) or not instances:
        return ["experiment_instances must be a non-empty array"]
    if not isinstance(claims, list):
        return ["atomic_claims must be an array"]
    instance_validator = Draft202012Validator(_load("skill07_experiment_native.schema.json"))
    claim_validator = Draft202012Validator(_load("skill07_atomic_claim.schema.json"))
    for index, item in enumerate(instances):
        failures.extend(f"experiment_instances[{index}]: {e.message}" for e in instance_validator.iter_errors(item))
    ids = [item.get("experiment_id") for item in instances if isinstance(item, Mapping)]
    if len(ids) != len(set(ids)):
        failures.append("experiment_id values must be unique")
    claim_ids = []
    for index, claim in enumerate(claims):
        failures.extend(f"atomic_claims[{index}]: {e.message}" for e in claim_validator.iter_errors(claim))
        if isinstance(claim, Mapping):
            claim_ids.append(claim.get("claim_id"))
            if claim.get("experiment_id") not in ids:
                failures.append(f"atomic_claims[{index}]: experiment_id does not resolve")
            if any(isinstance(claim.get(key), (list, dict)) for key in ("subject", "predicate", "object")):
                failures.append(f"atomic_claims[{index}]: subject/predicate/object must be scalar")
    if len(claim_ids) != len(set(claim_ids)):
        failures.append("claim_id values must be unique")
    projection = output.get("projection_metadata") or {}
    if projection != {"derived_projection": True, "canonical_source": "experiment_instances", "legacy_compatibility": True}:
        failures.append("fields must declare the exact derived projection metadata")
    return failures

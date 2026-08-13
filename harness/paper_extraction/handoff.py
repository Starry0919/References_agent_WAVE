"""Fail-closed Skill07 -> Skill08 handoff construction and validation."""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

HANDOFF_CONTRACT_VERSION = "skill07_skill08_handoff_v2"
HANDOFF_RULES_VERSION = "skill07_skill08_handoff_rules_v2"
SUCCESS_STATUSES = {"succeeded", "succeeded_with_warnings"}
SKILL07_CONTRACT_VERSION = "skill07_semantic_contract_v1"


class HandoffRejected(ValueError):
    pass


def canonical_hash(value: Any) -> str:
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def enrich_clean_artifact(skill06_output: Mapping[str, Any]) -> dict[str, Any]:
    """Attach the immutable JSON artifact reference to the runtime document."""
    clean = copy.deepcopy(dict(skill06_output.get("clean_document_artifact") or {}))
    ref = skill06_output.get("clean_json_artifact")
    if isinstance(ref, Mapping):
        clean["clean_json_artifact"] = copy.deepcopy(dict(ref))
    return clean


def document_identity(clean: Mapping[str, Any], *, verify_bytes: bool = True) -> dict[str, str]:
    metadata = clean.get("document_metadata") or {}
    ref = clean.get("clean_json_artifact") or {}
    paper_id = metadata.get("paper_id")
    artifact_id = ref.get("artifact_id")
    expected = str(ref.get("sha256") or "").removeprefix("sha256:")
    if not paper_id or paper_id == "unknown" or not artifact_id or len(expected) != 64:
        raise HandoffRejected("missing stable paper/document identity")
    if verify_bytes:
        path = clean.get("clean_json_path") or ref.get("uri")
        if not path or not Path(path).is_file():
            raise HandoffRejected("clean document bytes are unavailable")
        actual = hashlib.sha256(Path(path).read_bytes()).hexdigest()
        if actual != expected:
            raise HandoffRejected("clean document hash mismatch")
    return {
        "paper_id": str(paper_id),
        "document_artifact_id": str(artifact_id),
        "document_hash": expected,
    }


def build_handoff(
    skill07_result: Mapping[str, Any],
    clean: Mapping[str, Any],
    source_artifact_id: str,
    source_item_index: int | None = None,
) -> dict[str, Any]:
    output = skill07_result.get("output")
    provenance = skill07_result.get("provenance") or {}
    self_check = skill07_result.get("self_check") or {}
    identity = document_identity(clean)
    handoff = {
        "handoff_contract_version": HANDOFF_CONTRACT_VERSION,
        "paper_identity": identity,
        "skill07_source": {
            "artifact_id": source_artifact_id,
            "output_hash": provenance.get("output_hash") or canonical_hash(output),
            "status": skill07_result.get("status"),
            "eligible_for_evidence_verification": skill07_result.get("eligible_for_evidence_verification") is True,
            "schema_version": provenance.get("schema_version"),
            "semantic_contract_version": provenance.get("semantic_contract_version") or (output or {}).get("contract_version"),
            "validation_rules_version": provenance.get("validation_rules_version"),
            "self_check_passed": self_check.get("passed") is True,
        },
        "candidate_payload": copy.deepcopy(output),
        "provenance": {
            "handoff_rules_version": HANDOFF_RULES_VERSION,
            "source_item_index": source_item_index,
            "skill07_provenance": copy.deepcopy(provenance),
        },
    }
    validate_handoff(handoff, clean)
    return handoff


def validate_handoff(handoff: Mapping[str, Any], clean: Mapping[str, Any]) -> None:
    if handoff.get("handoff_contract_version") != HANDOFF_CONTRACT_VERSION:
        raise HandoffRejected("unsupported handoff contract")
    source = handoff.get("skill07_source") or {}
    payload = handoff.get("candidate_payload")
    if source.get("status") not in SUCCESS_STATUSES:
        raise HandoffRejected("Skill07 status is not success-compatible")
    if source.get("eligible_for_evidence_verification") is not True:
        raise HandoffRejected("Skill07 output is not eligible")
    if source.get("self_check_passed") is not True:
        raise HandoffRejected("Skill07 self-check did not pass")
    if not isinstance(payload, Mapping) or not isinstance(payload.get("fields"), Mapping):
        raise HandoffRejected("candidate payload is absent or schema-invalid")
    if not source.get("artifact_id") or not source.get("output_hash"):
        raise HandoffRejected("Skill07 artifact is not traceable")
    if source.get("semantic_contract_version") != SKILL07_CONTRACT_VERSION:
        raise HandoffRejected("incompatible Skill07 semantic contract")
    if not source.get("schema_version") or not source.get("validation_rules_version"):
        raise HandoffRejected("Skill07 contract provenance is incomplete")
    if source["output_hash"] != canonical_hash(payload):
        raise HandoffRejected("Skill07 output hash mismatch")
    if dict(handoff.get("paper_identity") or {}) != document_identity(clean):
        raise HandoffRejected("handoff/document identity mismatch")


def assert_unique_handoffs(handoffs: list[Mapping[str, Any]]) -> None:
    keys = [
        (h["paper_identity"]["paper_id"], h["paper_identity"]["document_artifact_id"], h["paper_identity"]["document_hash"])
        for h in handoffs
    ]
    if len(keys) != len(set(keys)):
        raise HandoffRejected("duplicate paper/document identity")

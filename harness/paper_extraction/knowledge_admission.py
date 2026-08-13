"""Deterministic claim-level admission gate for paper-derived knowledge."""
from __future__ import annotations

from typing import Any, Mapping

KNOWLEDGE_ADMISSION_RULES_VERSION = "knowledge_admission_rules_v3"
CRITICAL_DDR_CLAIMS = {"design_action", "trigger_observation", "rationale", "implementation", "outcome"}


class KnowledgeAdmissionBlocked(ValueError):
    pass


def evaluate_admission(output: Mapping[str, Any], provenance: Mapping[str, Any] | None = None) -> dict[str, Any]:
    provenance = provenance or {}
    fields = output.get("field_verifications") or {}
    claims = output.get("claim_verifications") or {}
    ddrs = output.get("ddr_verifications") or []
    admitted_fields = sorted(name for name, item in fields.items() if item.get("verification", {}).get("overall_status") == "verified")
    admitted_claims = sorted(name for name, item in claims.items() if item.get("verification", {}).get("overall_status") == "verified")
    admitted_ddrs, blocked_ddrs = [], []
    for ddr in ddrs:
        components = ddr.get("components") or {}
        required = [name for name in CRITICAL_DDR_CLAIMS if components.get(name, {}).get("candidate_present")]
        bad = [name for name in required if components[name].get("overall_status") != "verified"]
        if required and not bad:
            admitted_ddrs.append(ddr.get("candidate_ref"))
        else:
            blocked_ddrs.append({"candidate_ref": ddr.get("candidate_ref"), "blocked_components": bad or ["no_verifiable_critical_claim"]})
    critical_conflict = any(
        component.get("overall_status") == "conflicted"
        for ddr in ddrs for component in (ddr.get("components") or {}).values()
        if component.get("critical")
    )
    if admitted_ddrs and not blocked_ddrs:
        status = "KNOWLEDGE_ADMISSION_ALLOWED"
    elif admitted_claims or admitted_fields or admitted_ddrs:
        status = "KNOWLEDGE_ADMISSION_PARTIAL"
    else:
        status = "KNOWLEDGE_ADMISSION_BLOCKED"
    if critical_conflict and not (admitted_claims or admitted_fields):
        status = "KNOWLEDGE_ADMISSION_BLOCKED"
    return {
        "status": status,
        "rules_version": KNOWLEDGE_ADMISSION_RULES_VERSION,
        "admitted_field_claims": admitted_fields,
        "admitted_atomic_claims": admitted_claims,
        "admitted_ddr_candidates": admitted_ddrs,
        "blocked_ddr_candidates": blocked_ddrs,
        "critical_conflict": critical_conflict,
        "rule_role": "single_paper_rule_candidate",
        "source_skill08_artifact_id": provenance.get("skill08_artifact_id"),
    }


def require_admissible_skill08(output: Any, provenance: Any) -> dict[str, Any]:
    if not isinstance(output, Mapping) or output.get("contract_version") != "skill08_evidence_contract_v2":
        raise KnowledgeAdmissionBlocked("a valid Skill08 V2 artifact is required")
    if not isinstance(provenance, Mapping):
        raise KnowledgeAdmissionBlocked("Skill08 provenance is required")
    required = {
        "source_skill07_artifact_id", "source_skill07_output_hash", "document_artifact_id",
        "document_hash", "paper_id", "handoff_contract_version", "handoff_rules_version",
        "skill08_artifact_id", "skill08_contract_version", "skill08_validation_rules_version",
        "skill08_executor_version", "verification_timestamp",
    }
    missing = sorted(k for k in required if not provenance.get(k))
    if missing:
        raise KnowledgeAdmissionBlocked("incomplete Skill08 provenance: " + ", ".join(missing))
    admission = output.get("knowledge_admission")
    if not isinstance(admission, Mapping) or admission.get("status") == "KNOWLEDGE_ADMISSION_BLOCKED":
        raise KnowledgeAdmissionBlocked("Skill08 artifact was not admitted")
    if admission.get("source_skill08_artifact_id") != provenance.get("skill08_artifact_id"):
        raise KnowledgeAdmissionBlocked("knowledge admission provenance mismatch")
    return dict(admission)

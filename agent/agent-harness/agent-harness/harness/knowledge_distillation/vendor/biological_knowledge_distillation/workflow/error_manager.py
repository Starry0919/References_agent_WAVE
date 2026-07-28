"""Error normalization per SKILL.md 第十章 error taxonomy.

Every step raises errors as ``{"code": "<TAXONOMY_CODE>", "message": str, ...}``.
This module only fills in the fields the taxonomy requires and never invents
a code that isn't in ``ERROR_CODES`` - unknown codes fall back to
``SCHEMA_VALIDATION_ERROR`` so a typo in a step never silently disappears.
"""
import hashlib

ERROR_CODES = {
    "SOURCE_IDENTITY_ERROR", "UNRESOLVED_EDITION", "ACCESS_BLOCKED", "PARSING_ERROR",
    "OCR_UNCERTAIN", "STRUCTURE_LOSS", "FIGURE_NOT_PARSED", "TABLE_NOT_PARSED",
    "EVIDENCE_NOT_FOUND", "SEMANTIC_MISMATCH", "SOURCE_ATTRIBUTION_ERROR", "TRANSLATION_CONFLICT",
    "VERSION_CONFLICT", "ORGANISM_SCOPE_UNCERTAIN", "STRAIN_SCOPE_UNCERTAIN", "MECHANISM_CONFLICT",
    "OVERGENERALIZATION_RISK", "UNSUPPORTED_DECISION_RULE", "KNOWLEDGE_DUPLICATION", "FUSION_CONFLICT",
    "PAPER_LINK_MISMATCH", "SCHEMA_VALIDATION_ERROR", "ARTIFACT_PERSISTENCE_ERROR", "HUMAN_REVIEW_REQUIRED",
    "NO_INPUT_ARTIFACT", "UNHANDLED",
}

_DEFAULT_SEVERITY = {
    "SOURCE_IDENTITY_ERROR": "high", "UNRESOLVED_EDITION": "medium", "ACCESS_BLOCKED": "high",
    "PARSING_ERROR": "medium", "OCR_UNCERTAIN": "low", "STRUCTURE_LOSS": "medium",
    "FIGURE_NOT_PARSED": "low", "TABLE_NOT_PARSED": "low", "EVIDENCE_NOT_FOUND": "high",
    "SEMANTIC_MISMATCH": "high", "SOURCE_ATTRIBUTION_ERROR": "high", "TRANSLATION_CONFLICT": "medium",
    "VERSION_CONFLICT": "medium", "ORGANISM_SCOPE_UNCERTAIN": "medium", "STRAIN_SCOPE_UNCERTAIN": "medium",
    "MECHANISM_CONFLICT": "high", "OVERGENERALIZATION_RISK": "high", "UNSUPPORTED_DECISION_RULE": "medium",
    "KNOWLEDGE_DUPLICATION": "low", "FUSION_CONFLICT": "medium", "PAPER_LINK_MISMATCH": "medium",
    "SCHEMA_VALIDATION_ERROR": "high", "ARTIFACT_PERSISTENCE_ERROR": "high", "HUMAN_REVIEW_REQUIRED": "medium",
    "NO_INPUT_ARTIFACT": "high", "UNHANDLED": "high",
}


def normalize(step, error):
    code = error.get("code", "SCHEMA_VALIDATION_ERROR")
    if code not in ERROR_CODES:
        code = "SCHEMA_VALIDATION_ERROR"
    message = error.get("message", str(error))
    return {
        "error_id": "err_" + hashlib.sha256(f"{step}|{code}|{message}".encode()).hexdigest()[:16],
        "error_code": code,
        "message": message,
        "source_id": error.get("source_id"),
        "step": step,
        "affected_objects": error.get("affected_objects", []),
        "severity": error.get("severity", _DEFAULT_SEVERITY.get(code, "medium")),
        "recoverable": bool(error.get("retryable", error.get("recoverable", False))),
        "recommended_action": error.get("recommended_action", ""),
    }

ERROR_CODES = {
    "EVID001": ("EDX-EVD-001", "Skill07 input is missing."),
    "EVID002": ("EDX-EVD-002", "Clean document is unavailable."),
    "EVID003": ("EDX-EVD-001", "Evidence was not found."),
    "EVID004": ("EDX-EVD-003", "Conflicting evidence was detected."),
    "EVID005": ("EDX-EVD-002", "Candidate quote is insufficient to support the value.")
}


def error(local_code, context=None, retryable=False):
    code, message = ERROR_CODES[local_code]
    return {
        "code": code, "local_code": local_code, "category": "evidence_binding",
        "message": message, "retryable": retryable, "severity": "error",
        "context": context or {}, "suggested_action": "Inspect source paragraphs or request human review."
    }


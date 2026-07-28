ERROR_CODES = {
    "DOI001": ("EDX-CIT-001", "DOI format is invalid."),
    "DOI002": ("EDX-CIT-001", "DOI was not found in an external database."),
    "DOI003": ("EDX-CIT-002", "Candidate metadata does not match database metadata."),
    "DOI004": ("EDX-SYS-001", "Citation database is unavailable."),
    "DOI005": ("EDX-CIT-003", "Citation validation failed after three attempts.")
}


def error(local_code, context=None, retryable=False):
    code, message = ERROR_CODES[local_code]
    return {
        "code": code, "local_code": local_code, "category": "citation_validation",
        "message": message, "retryable": retryable, "severity": "error",
        "context": context or {}, "suggested_action": "Inspect the validation audit trail or request human review."
    }


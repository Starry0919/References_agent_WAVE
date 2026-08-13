ERROR_CODES = {
    "EXP001": ("EDX-EXT-001", "Clean document does not exist or is unreadable."),
    "EXP002": ("EDX-EXT-001", "Experimental information is insufficient."),
    "EXP003": ("EDX-VAL-002", "Conflicting experimental fields were detected."),
    "EXP004": ("EDX-EXT-001", "A field cannot be determined and remains unknown.")
}


def error(local_code, context=None, retryable=False):
    code, message = ERROR_CODES[local_code]
    return {
        "code": code, "local_code": local_code, "category": "experiment_extraction",
        "message": message, "retryable": retryable, "severity": "error",
        "context": context or {}, "suggested_action": "Inspect candidate source paragraphs or request human review."
    }


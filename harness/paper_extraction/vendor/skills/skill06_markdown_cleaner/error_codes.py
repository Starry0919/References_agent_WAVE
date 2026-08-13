ERROR_CODES = {
    "CLEAN001": ("EDX-VAL-001", "Input Markdown is empty."),
    "CLEAN002": ("EDX-CLN-001", "Document structure is severely damaged."),
    "CLEAN003": ("EDX-CLN-001", "A table cannot be repaired safely."),
    "CLEAN004": ("EDX-VAL-002", "Protected scientific content changed during cleaning."),
    "CLEAN005": ("EDX-CLN-001", "Input contains unresolved encoding errors.")
}


def error(local_code, context=None, retryable=False):
    code, message = ERROR_CODES[local_code]
    return {
        "code": code, "local_code": local_code, "category": "markdown_cleaning",
        "message": message, "retryable": retryable, "severity": "error",
        "context": context or {}, "suggested_action": "Preserve the original text and request human review."
    }


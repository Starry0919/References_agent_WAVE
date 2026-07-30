ERROR_CODES = {
    "PARSE001": ("EDX-PAR-001", "Input PDF cannot be read or its checksum is invalid."),
    "PARSE002": ("EDX-PAR-001", "All configured PDF parsers failed."),
    "PARSE003": ("EDX-PAR-001", "Parser produced empty Markdown."),
    "PARSE004": ("EDX-PAR-002", "Document structure reconstruction is partial."),
    "PARSE005": ("EDX-PAR-003", "Figure or table reconstruction is incomplete.")
}


def error(local_code, context=None, retryable=False):
    code, message = ERROR_CODES[local_code]
    return {
        "code": code, "local_code": local_code, "category": "pdf_parsing",
        "message": message, "retryable": retryable, "severity": "error",
        "context": context or {}, "suggested_action": "Retry with pipeline mode or request human review."
    }

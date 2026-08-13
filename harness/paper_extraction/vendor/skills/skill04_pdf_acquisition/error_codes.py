ERROR_CODES = {
    "PDF001": ("EDX-PDF-001", "Citation was not accepted by Skill03."),
    "PDF002": ("EDX-PDF-001", "All legal PDF download sources failed."),
    "PDF003": ("EDX-PDF-004", "Downloaded file is empty."),
    "PDF004": ("EDX-PDF-004", "Downloaded content is not a valid PDF."),
    "PDF005": ("EDX-PDF-003", "Checksum verification failed."),
    "PDF006": ("EDX-PDF-004", "Manual upload is damaged or invalid.")
}


def error(local_code, context=None, retryable=False):
    code, message = ERROR_CODES[local_code]
    return {
        "code": code, "local_code": local_code, "category": "pdf_acquisition",
        "message": message, "retryable": retryable, "severity": "error",
        "context": context or {}, "suggested_action": "Try another legal source or provide a valid PDF upload."
    }


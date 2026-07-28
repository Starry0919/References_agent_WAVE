ERRORS = {
    "GOV001": ("qc_failure", "Automatic QC could not complete."),
    "GOV002": ("review_creation_failure", "Human review task could not be created."),
    "GOV003": ("audit_failure", "Audit event could not be persisted."),
    "GOV004": ("illegal_approval", "The requested review transition is not permitted."),
    "GOV005": ("ai_forged_human_approval", "AI actors cannot submit human approval decisions."),
}
def error(code, details=None):
    name, message = ERRORS[code]; result = {"code": code, "name": name, "message": message}
    if details is not None: result["details"] = details
    return result

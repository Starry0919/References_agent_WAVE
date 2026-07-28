ERRORS = {
    "PLAN001": ("insufficient_input", "Input is insufficient; only partial output is possible."),
    "PLAN002": ("unsupported_proposal_removed", "A proposal without supporting evidence was removed."),
    "PLAN003": ("unexplained_ai_proposal_rejected", "AI proposal lacks reasoning or uncertainty and was rejected."),
    "PLAN004": ("dbtl_incomplete", "DBTL workflow is incomplete."),
}
def error(code, details=None):
    name, message = ERRORS[code]; result = {"code": code, "name": name, "message": message}
    if details is not None: result["details"] = details
    return result

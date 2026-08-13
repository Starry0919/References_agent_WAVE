ERRORS = {
    "EVAL001": ("input_missing", "Skill08 output or fields are missing."),
    "EVAL002": ("evidence_missing", "Evidence is missing; only a partial evaluation is possible."),
    "EVAL003": ("unknown_score", "No evaluable fields were supplied."),
    "EVAL004": ("conflict_report", "Conflicting source information requires review."),
}
def error(code, details=None):
    name, message = ERRORS[code]
    value = {"code": code, "name": name, "message": message}
    if details is not None: value["details"] = details
    return value

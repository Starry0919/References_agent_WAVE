ERRORS = {
    "K12_001": ("target_system_missing", "Target organism and strain family are required."),
    "K12_002": ("strain_missing", "Literature strain is unknown; compatibility remains unknown."),
    "K12_003": ("objective_mismatch", "Design objective differs and was excluded from direct comparison."),
    "K12_004": ("compatibility_unknown", "Available evidence is insufficient to assess compatibility."),
}
def error(code, details=None):
    name, message = ERRORS[code]
    result = {"code": code, "name": name, "message": message}
    if details is not None: result["details"] = details
    return result

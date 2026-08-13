def check(provenance):
    required = ("skill_id", "skill_version", "input_hash", "output_hash")
    missing = [x for x in required if not provenance.get(x)]
    return {"passed": not missing, "issues": [{"code": "provenance_missing", "field": x, "severity": "review"} for x in missing],
            "reason": f"{len(missing)} provenance attributes are missing."}

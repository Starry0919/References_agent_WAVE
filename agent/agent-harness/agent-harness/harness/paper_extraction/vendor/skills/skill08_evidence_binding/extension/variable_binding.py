try:
    from ..binder.evidence_validator import match_score
except ImportError:
    from binder.evidence_validator import match_score


def bind_variables(variables, evidence_records):
    result = {"status": variables.get("status", "inferred"), "notes": variables.get("notes")}
    for category in ("independent", "dependent", "controlled"):
        result[category] = []
        for item in variables.get(category, []):
            bound = dict(item)
            matches = [
                record["evidence_id"] for record in evidence_records
                if match_score(item.get("value"), record["quote"]) > 0
            ]
            bound["evidence_ids"] = matches
            bound["status"] = "inferred" if matches else "unknown"
            bound["reason"] = item.get("basis") if matches else "No supporting reported field evidence."
            if not matches:
                bound["value"] = None
            result[category].append(bound)
    return result


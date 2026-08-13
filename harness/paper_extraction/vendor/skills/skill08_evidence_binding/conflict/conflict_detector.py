def bind_conflicts(skill07_conflicts, unit_evidence):
    extended, unified = [], []
    for conflict in skill07_conflicts:
        evidence_ids = []
        for candidate in conflict.get("candidate_values", []):
            evidence_ids.extend(unit_evidence.get(candidate.get("source"), []))
        evidence_ids = list(dict.fromkeys(evidence_ids))
        item = dict(conflict)
        item["evidence_ids"] = evidence_ids
        extended.append(item)
        if len(evidence_ids) >= 2:
            unified.append({
                "field_path": conflict.get("field", "unknown"),
                "candidate_evidence_ids": evidence_ids,
                "status": "open"
            })
    return extended, unified


def _walk(value, path="$"):
    if isinstance(value, dict):
        yield path, value
        for k, v in value.items(): yield from _walk(v, f"{path}.{k}")
    elif isinstance(value, list):
        for i, v in enumerate(value): yield from _walk(v, f"{path}[{i}]")
def check(content):
    issues, reported = [], 0
    for path, node in _walk(content):
        if node.get("status") == "reported":
            reported += 1
            if not node.get("evidence_ids"):
                issues.append({"code": "reported_without_evidence", "path": path, "severity": "review"})
        if node.get("source_type") == "reported_in_literature" and "step_id" in node:
            reported += 1
            if not node.get("evidence"):
                issues.append({"code": "reported_step_without_evidence", "path": path, "severity": "review"})
    return {"passed": not issues, "reported_claims_checked": reported, "issues": issues,
            "reason": f"{reported} reported claims/steps checked; {len(issues)} lack evidence references."}

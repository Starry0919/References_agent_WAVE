from .common import result

def evaluate(fields, skill08):
    reported = [v for v in fields.values() if v.get("status") == "reported"]
    unknown = [v for v in fields.values() if v.get("status") == "unknown"]
    supported = [v for v in reported if v.get("evidence_ids")]
    coverage = len(supported) / max(1, len(reported))
    unknown_fraction = len(unknown) / max(1, len(fields))
    conflicts = skill08.get("conflicts", [])
    evidence_map = skill08.get("evidence_map", {})
    source_weights = []
    source_counts = {"methods": 0, "supplement": 0, "figure_table": 0, "results": 0, "other": 0}
    for value in evidence_map.values():
        locator = value.get("locator", {})
        section = " ".join(locator.get("section_path", [])).lower()
        if "method" in section: kind, weight = "methods", 1.0
        elif locator.get("supplement_id") or "supplement" in section: kind, weight = "supplement", .9
        elif locator.get("figure_id") or locator.get("table_id"): kind, weight = "figure_table", .8
        elif "result" in section: kind, weight = "results", .7
        else: kind, weight = "other", .6
        source_counts[kind] += 1
        source_weights.append(weight)
    source_quality = sum(source_weights) / len(source_weights) if source_weights else 0
    score = max(0, 100 * coverage * (0.75 + 0.25 * source_quality) * (1 - .25 * unknown_fraction) - min(20, 5 * len(conflicts)))
    if coverage >= .9 and unknown_fraction <= .25 and not conflicts: grade = "A"
    elif coverage >= .75 and unknown_fraction <= .5: grade = "B"
    elif coverage >= .5: grade = "C"
    else: grade = "D"
    issues = []
    if len(supported) < len(reported): issues.append("reported_fields_without_evidence")
    if unknown_fraction > .5: issues.append("majority_fields_unknown")
    if conflicts: issues.append("conflicting_evidence")
    return result(score, f"{len(supported)} of {len(reported)} reported fields have bound evidence; {len(unknown)} fields are unknown; source quality is {source_quality:.2f}.",
                  grade=grade, coverage=round(coverage, 4), source_quality=round(source_quality, 4),
                  source_distribution=source_counts, unknown_fraction=round(unknown_fraction, 4), issues=issues)

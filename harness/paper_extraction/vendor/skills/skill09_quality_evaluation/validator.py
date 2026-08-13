def validate(report, fields):
    dims = report.get("dimensions", {})
    checks = []
    scored = [v for v in dims.values() if isinstance(v, dict) and "score" in v]
    checks.append({"name": "all_scores_have_reasons", "passed": all(v.get("reason") for v in scored)})
    unknown = sorted(k for k, v in fields.items() if v.get("status") == "unknown")
    listed = sorted(x["field"] for x in report.get("missing_information", []))
    checks.append({"name": "all_unknown_listed", "passed": unknown == listed})
    ev = dims.get("evidence_quality", {})
    checks.append({"name": "unknown_caps_evidence_grade", "passed": not (ev.get("unknown_fraction", 0) > .5 and ev.get("grade") in {"A", "B"})})
    logic = dims.get("experimental_logic", {})
    hypothesis_unknown = fields.get("hypothesis", {}).get("status") == "unknown"
    checks.append({"name": "missing_hypothesis_lowers_logic", "passed": not hypothesis_unknown or logic.get("score", 100) <= 80})
    checks.append({"name": "no_transfer_risk", "passed": "transfer_risk" not in report.get("risks", {})})
    return checks

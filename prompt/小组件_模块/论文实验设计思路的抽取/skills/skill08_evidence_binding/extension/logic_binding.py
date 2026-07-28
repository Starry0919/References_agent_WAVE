def bind_design_logic(logic, evidence_map):
    result = dict(logic)
    result["evidence_ids"] = {
        "question": list(evidence_map.get("objective", [])),
        "hypothesis": list(evidence_map.get("hypothesis", [])),
        "measurement": list(evidence_map.get("assay", []))
    }
    if logic.get("question") and not result["evidence_ids"]["question"]:
        result["question"] = None
    if logic.get("hypothesis") and not result["evidence_ids"]["hypothesis"]:
        result["hypothesis"] = None
    if logic.get("measurement") and not result["evidence_ids"]["measurement"]:
        result["measurement"] = []
    if not any(result["evidence_ids"].values()):
        result["status"] = "unknown"
    return result


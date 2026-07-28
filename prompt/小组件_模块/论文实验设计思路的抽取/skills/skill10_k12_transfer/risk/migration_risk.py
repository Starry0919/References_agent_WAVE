def assess(item, analysis):
    risks = []
    if analysis["basis"]["strain_similarity"] != "high": risks.append({"type": "biological", "detail": "Source and target strain families are not explicitly matched."})
    if analysis["basis"]["engineering_tool_compatibility"] == "unknown": risks.append({"type": "engineering", "detail": "Engineering intervention is unknown."})
    elif analysis["basis"]["engineering_tool_compatibility"] != "compatible": risks.append({"type": "engineering", "detail": "Engineering tool requires K-12 validation."})
    if not item["literature_facts"]["measurement"]["assay"]: risks.append({"type": "measurement", "detail": "Measurement method is unknown."})
    if item["quality"]["evidence_grade"] in {"C", "D", "unknown"}: risks.append({"type": "evidence", "detail": "Low or unknown evidence grade limits confidence."})
    level = "high" if len(risks) >= 3 else "medium" if risks else "low"
    return {"paper_id": item["paper_id"], "risk_level": level, "risks": risks}

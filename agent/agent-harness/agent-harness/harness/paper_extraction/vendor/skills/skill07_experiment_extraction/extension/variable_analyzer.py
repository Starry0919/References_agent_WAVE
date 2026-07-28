def analyze_variables(groups, engineering, conditions, measurements):
    independent = []
    independent.extend({"value": v["name"], "basis": "explicit experimental group"} for v in groups)
    independent.extend({"value": v, "basis": "reported engineering method"} for v in engineering.get("methods", []))
    dependent = [{"value": v, "basis": "reported assay"} for v in measurements.get("assays", [])]
    controlled = []
    for category in ("temperature", "time", "volume", "agitation", "od", "medium", "carbon_source"):
        controlled.extend({"value": v, "category": category, "basis": "reported condition"} for v in conditions.get(category, []))
    return {
        "independent": independent, "dependent": dependent, "controlled": controlled,
        "status": "inferred", "notes": "Variable roles are a lightweight structural classification of reported fields."
    }


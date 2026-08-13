def build(candidate):
    grouped = {"biological": [], "technical": [], "interpretation": []}
    for risk in candidate.get("risks", []):
        kind = risk.get("type")
        target = "biological" if kind == "biological" else "interpretation" if kind in {"measurement", "evidence"} else "technical"
        grouped[target].append(risk.get("detail"))
    return grouped

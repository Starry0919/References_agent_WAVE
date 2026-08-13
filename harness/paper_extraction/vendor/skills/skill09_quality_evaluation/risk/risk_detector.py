def detect(dimensions, missing, conflicts):
    reproduction = dimensions["reproducibility"]["score"]
    logic = dimensions["experimental_logic"]["score"]
    critical = {"strain", "engineering_method", "culture_conditions", "replicates", "assay"}
    critical_missing = sorted(critical.intersection(missing))
    return {
        "replication_risk": {"level": "high" if reproduction < 50 else "medium" if reproduction < 80 else "low",
                             "reason": dimensions["reproducibility"]["reason"]},
        "information_missing_risk": {"level": "high" if len(critical_missing) >= 3 else "medium" if missing else "low",
                                     "reason": f"{len(missing)} unknown fields, including {len(critical_missing)} reproduction-critical fields."},
        "interpretation_risk": {"level": "high" if logic < 50 or conflicts else "medium" if logic < 80 else "low",
                                "reason": f"Logic score is {logic}; {len(conflicts)} conflicts are unresolved."},
    }

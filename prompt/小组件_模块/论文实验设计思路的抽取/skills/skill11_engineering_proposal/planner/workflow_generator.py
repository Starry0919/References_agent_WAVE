def details_for(candidate, matrix_row):
    biology = matrix_row.get("biological_system", {})
    engineering = matrix_row.get("engineering_strategy", {})
    design = matrix_row.get("experimental_design", {})
    measurement = matrix_row.get("measurement", {})
    return {
        "host": biology.get("organism_strain") or "unknown",
        "genotype": biology.get("genotype") or "unknown",
        "modification": engineering.get("modification") or candidate.get("candidate_strategy") or "unknown",
        "conditions": design.get("conditions") or "unknown",
        "groups": design.get("groups") or "unknown",
        "controls": design.get("controls") or "unknown",
        "assay": measurement.get("assay") or "unknown",
        "instrument": measurement.get("instrument") or "unknown",
        "analysis": matrix_row.get("analysis_methods", "unknown"),
    }

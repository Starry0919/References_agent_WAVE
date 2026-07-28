FIELDS = ["objective", "hypothesis", "strain", "genotype", "engineering_method", "experimental_groups",
          "controls", "culture_conditions", "medium", "dosage", "time", "replicates", "assay",
          "instruments", "analysis_methods", "outcomes"]
def field(name, status="reported"):
    return {"value": name if status != "unknown" else None, "status": status, "confidence": .9,
            "extraction_method": "rule" if status == "reported" else "not_applicable",
            "evidence_ids": [f"ev_{name}"] if status == "reported" else [], "notes": None}
def request(unknown=(), no_evidence=False, conflicts=None):
    fields = {k: field(k, "unknown" if k in unknown else "reported") for k in FIELDS}
    evidence = {} if no_evidence else {f"ev_{k}": {"evidence_id": f"ev_{k}"} for k in FIELDS if k not in unknown}
    if no_evidence:
        for v in fields.values(): v["evidence_ids"] = []
    ext = {"variables": {"independent_variables": ["edit"], "dependent_variables": ["outcome"], "controlled_variables": ["temperature"]},
           "experiment_workflow": {"workflow": ["construct", "cultivate", "measure", "analyze"]},
           "design_logic": {}}
    return {"skill08_output": {"literature_experiment": {"fields": fields, "evidence": list(evidence.values()), "conflicts": []},
             "evidence_linked_design": {"paper_id": "paper-test", "extensions": ext},
             "evidence_map": evidence, "coverage": {}, "conflicts": conflicts or []}}

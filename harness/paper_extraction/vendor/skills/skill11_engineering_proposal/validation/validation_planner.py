def build(details, candidate):
    return {"primary_validation": {"target": "target phenotype", "assay": details["assay"]},
            "secondary_validation": {"target": "construct identity and intervention", "method": "unknown"},
            "control_strategy": {"reported_controls": details["controls"], "required_review": ["WT", "mutant", "complemented strain"]},
            "checkpoints": candidate.get("validation_required", [])}

try:
    from ..schema import fields_of, extensions_of, value
except ImportError:
    from schema import fields_of, extensions_of, value

def normalize(design, evidence, quality, index):
    fields = fields_of(design)
    linked = evidence.get("evidence_linked_design", {})
    paper_id = (linked.get("paper_id")
                or design.get("experimental_design_object", {}).get("paper_id")
                or f"paper-{index+1}")
    qcore = quality.get("quality_evaluation", quality.get("output", {}).get("quality_evaluation", {}))
    report = quality.get("evaluation_report", quality.get("output", {}).get("evaluation_report", {}))
    grade = report.get("dimensions", {}).get("evidence_quality", {}).get("grade", "unknown")
    strain = value(fields, "strain")
    # Skill07 uses provisional ``candidate:...`` locators. Skill08 replaces
    # those with verified ``ev_...`` records in evidence_linked_design.fields.
    # Downstream planning must carry the verified IDs; otherwise Skill13 cannot
    # render a traceable evidence panel.
    linked_fields = linked.get("fields", {})
    evidence_source = linked_fields if isinstance(linked_fields, dict) and linked_fields else fields
    evidence_ids = sorted({
        eid
        for f in evidence_source.values()
        if isinstance(f, dict)
        for eid in f.get("evidence_ids", [])
    })
    return {
        "paper_id": paper_id, "year": design.get("year"),
        "objective": value(fields, "objective"),
        "literature_facts": {
            "biological_system": {"organism_strain": strain, "genotype": value(fields, "genotype")},
            "engineering_strategy": {"modification": value(fields, "engineering_method")},
            "experimental_design": {"groups": value(fields, "experimental_groups"), "controls": value(fields, "controls"),
                                    "conditions": value(fields, "culture_conditions")},
            "measurement": {"assay": value(fields, "assay"), "instrument": value(fields, "instruments")},
            "outcome": value(fields, "outcomes"),
            "workflow": extensions_of(design).get("experiment_workflow", {}),
            "variables": extensions_of(design).get("variables", {}),
            "design_logic": extensions_of(design).get("design_logic", {}),
        },
        "quality": {"evidence_grade": grade, "completeness": qcore.get("completeness", 0),
                    "reproducibility": qcore.get("reproducibility", 0),
                    "evidence_level": qcore.get("evidence_level", 0)},
        "evidence_ids": evidence_ids,
    }

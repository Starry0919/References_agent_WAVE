def field(value, name):
    return {"value": value, "status": "reported" if value is not None else "unknown", "confidence": .9,
            "extraction_method": "rule" if value is not None else "not_applicable",
            "evidence_ids": [f"ev:{name}"] if value is not None else [], "notes": None}
def design(objective="increase lactate production", strain="E. coli K-12 MG1655", strategy="gene knockout", assay="HPLC"):
    values = {"objective": objective, "hypothesis": "intervention changes outcome", "strain": strain, "genotype": "reported genotype",
              "engineering_method": strategy, "experimental_groups": ["edited"], "controls": ["wild type"],
              "culture_conditions": {"temperature": "37 C"}, "medium": "defined medium", "dosage": None,
              "time": "24 h", "replicates": 3, "assay": assay, "instruments": assay,
              "analysis_methods": "statistical comparison", "outcomes": "increased production"}
    return {"fields": {k: field(v, k) for k, v in values.items()}, "extensions": {}}
def evidence(paper):
    return {"evidence_linked_design": {"paper_id": paper}, "evidence_map": {"x": {}}}
def quality(grade="A", level=.9):
    return {"quality_evaluation": {"completeness": level, "reproducibility": level, "evidence_level": level,
                                   "missing_information": [], "extraction_confidence": level},
            "evaluation_report": {"dimensions": {"evidence_quality": {"grade": grade}}}}
def request(designs, grades=None):
    grades = grades or [("A", .9)] * len(designs)
    return {"experimental_designs": designs,
            "evidence_objects": [evidence(f"paper-{i+1}") for i in range(len(designs))],
            "quality_reports": [quality(*g) for g in grades],
            "target_system": {"organism": "Escherichia coli", "strain_family": "K-12"}}

from .strain_similarity import assess
def analyze(item, target):
    facts = item["literature_facts"]
    strain = facts["biological_system"]["organism_strain"]
    strain_level, basis, validation = assess(strain, target["strain_family"])
    modification = facts["engineering_strategy"]["modification"]
    assay = facts["measurement"]["assay"]
    quality = item["quality"]
    tool_level = "unknown" if not modification else "requires_validation"
    phenotype_level = "unknown" if not facts["outcome"] else "requires_revalidation"
    confidence = min(float(quality.get("evidence_level", 0)), float(quality.get("completeness", 0)))
    compatibility = "unknown" if strain_level == "unknown" or not modification else ("high" if strain_level == "high" and confidence >= .75 else "medium")
    reasons = basis + [
        "Engineering-tool compatibility is not assumed across strain backgrounds." if modification else "Engineering intervention is unknown.",
        "Phenotype transfer is treated as requiring target-system validation." if facts["outcome"] else "Reported outcome is unknown."
    ]
    if not assay: validation.append("Define a K-12-compatible measurement and analysis plan.")
    return {"paper_id": item["paper_id"], "target_system": target, "compatibility": compatibility,
            "confidence": round(confidence, 3), "reason": reasons,
            "basis": {"evidence_ids": item["evidence_ids"], "evidence_grade": quality["evidence_grade"],
                      "strain_similarity": strain_level, "engineering_tool_compatibility": tool_level,
                      "phenotype_transferability": phenotype_level},
            "validation_needed": sorted(set(validation))}

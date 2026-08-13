def build(quality):
    core=quality.get("quality_evaluation",{})
    detail=quality.get("evaluation_report",{})
    return {"completeness":core.get("completeness","unknown"),"evidence_quality":core.get("evidence_level","unknown"),
            "reproducibility":core.get("reproducibility","unknown"),"confidence":core.get("extraction_confidence","unknown"),
            "grade":detail.get("dimensions",{}).get("evidence_quality",{}).get("grade","unknown"),
            "missing_information":core.get("missing_information",[])}

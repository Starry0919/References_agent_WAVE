def build(engineering, k12, quality, governance, labels):
    plans=engineering.get("engineering_plans",[])
    primary=plans[0] if plans else (engineering.get("ai_combination_proposals",[]) or [None])[0]
    objective=(primary or {}).get("objective",{})
    candidate=(primary or {}).get("design_rationale",{}).get("what","unknown")
    analysis=(k12.get("k12_analysis") or [{}])[0]
    q=quality.get("quality_evaluation",{})
    gov=governance.get("governance",governance)
    qc=governance.get("qc_report",{}).get("final_status","unknown")
    return {"title":labels["decision_title"],"objective":objective.get("statement") or objective.get("target_phenotype","unknown"),
            "objective_source":objective.get("target_phenotype_source","unknown"),
            "target_system":f"{objective.get('organism','Escherichia coli')} {objective.get('strain','K-12')}",
            "strategy_summary":candidate,"k12_compatibility":analysis.get("compatibility","unknown"),
            "confidence":analysis.get("confidence",q.get("extraction_confidence","unknown")),
            "quality_grade":quality.get("evaluation_report",{}).get("dimensions",{}).get("evidence_quality",{}).get("grade","unknown"),
            "qc_status":qc,"review_status":gov.get("review_status","unknown")}

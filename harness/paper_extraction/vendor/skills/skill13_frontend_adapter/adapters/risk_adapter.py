def build(engineering,k12):
    risks=[]
    for plan in engineering.get("engineering_plans",[])+engineering.get("ai_combination_proposals",[]):
        for kind,values in plan.get("risks",{}).items():
            for value in values: risks.append({"category":kind,"detail":value,"source":"engineering_plan"})
    for item in k12.get("risk_assessment",[]):
        for value in item.get("risks",[]): risks.append({"category":"transfer","detail":value.get("detail"),"type":value.get("type"),"source":"k12_analysis"})
    level="high" if any(x.get("category") in {"biological","transfer"} for x in risks) else "medium" if risks else "low"
    validation=sorted({v for x in k12.get("k12_analysis",[]) for v in x.get("validation_needed",[])})
    return {"risk_level":level,"risks":risks,"mitigation":validation}

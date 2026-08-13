def build(k12):
    analyses=k12.get("k12_analysis",[])
    return {"items":[{"paper_id":x.get("paper_id"),"compatibility":x.get("compatibility","unknown"),
                      "transferability":x.get("transferability",{}).get("transferability","unknown"),
                      "confidence":x.get("confidence","unknown"),"reason":x.get("reason",[]),
                      "validation_required":x.get("validation_needed",[])} for x in analyses],
            "candidate_design_space":k12.get("candidate_design_space",[])}

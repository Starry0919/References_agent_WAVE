def build(item, analysis, transfer, risk, cluster_id):
    strategy = item["literature_facts"]["engineering_strategy"]["modification"]
    return {"candidate_id": f"candidate:{item['paper_id']}", "objective_cluster": cluster_id,
            "candidate_strategy": strategy if strategy is not None else "unknown",
            "literature_support": {"paper_id": item["paper_id"], "evidence_ids": item["evidence_ids"],
                                   "evidence_grade": item["quality"]["evidence_grade"]},
            "k12_compatibility": analysis["compatibility"], "analysis_confidence": analysis["confidence"],
            "transferability": transfer["transferability"],
            "advantages": ["Literature-supported outcome is available."] if item["literature_facts"]["outcome"] else [],
            "limitations": [x["detail"] for x in risk["risks"]],
            "risks": risk["risks"], "validation_required": transfer["validation_needed"],
            "decision_status": "candidate_only_not_ranked"}

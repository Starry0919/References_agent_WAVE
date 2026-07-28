def candidate(paper, strategy, evidence=True, risk=False):
    return {"candidate_id": f"candidate:{paper}", "objective_cluster": "cluster-1", "candidate_strategy": strategy,
            "literature_support": {"paper_id": paper, "evidence_ids": [f"ev:{paper}"] if evidence else [], "evidence_grade": "A" if evidence else "D"},
            "k12_compatibility": "high", "analysis_confidence": .9, "transferability": "direct_reference",
            "advantages": [], "limitations": ["background risk"] if risk else [],
            "risks": [{"type": "biological", "detail": "background risk"}] if risk else [],
            "validation_required": ["verify genotype"], "decision_status": "candidate_only_not_ranked"}
def row(paper, strategy):
    return {"paper_id": paper, "biological_system": {"organism_strain": "E. coli K-12", "genotype": "reported"},
            "engineering_strategy": {"modification": strategy}, "experimental_design": {"groups": ["edited"], "controls": ["WT"], "conditions": "reported"},
            "measurement": {"assay": "reported assay", "instrument": "reported instrument"}, "analysis_methods": "reported analysis"}
def request(candidates):
    return {"k12_design_space": {"candidate_design_space": candidates,
             "objective_clusters": [{"objective_cluster": "cluster-1", "representative_objective": "increase product", "paper_ids": [c["literature_support"]["paper_id"] for c in candidates]}],
             "comparison_matrix": [row(c["literature_support"]["paper_id"], c["candidate_strategy"]) for c in candidates]},
            "experimental_designs": [{} for _ in candidates], "evidence": [{} for _ in candidates], "quality_reports": [{} for _ in candidates]}

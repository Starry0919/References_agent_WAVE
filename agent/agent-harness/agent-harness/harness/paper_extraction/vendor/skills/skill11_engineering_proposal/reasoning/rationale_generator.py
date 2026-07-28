def reported(candidate):
    return {"what": candidate["candidate_strategy"], "why": "Convert an evidence-supported Skill10 candidate into a reviewable DBTL workflow.",
            "evidence": candidate["literature_support"]["evidence_ids"],
            "limitations": candidate.get("limitations", []), "source_type": "reported_in_literature"}
def combination(candidates):
    return {"what": [x["candidate_strategy"] for x in candidates],
            "why": "Test whether separately evidenced strategies can be combined; no benefit is assumed.",
            "reasoning": "Each component exists in the same objective cluster and has bound evidence.",
            "supporting_evidence": sorted({e for x in candidates for e in x["literature_support"]["evidence_ids"]}),
            "uncertainty": "Interaction, burden, and phenotype effects are unknown until staged validation.",
            "source_type": "ai_generated_proposal", "suggestion_level": 2}

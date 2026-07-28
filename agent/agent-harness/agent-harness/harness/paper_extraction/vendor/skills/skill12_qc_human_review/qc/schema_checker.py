REQUIRED_BY_SKILL = {
    "skill07_experiment_extraction": {"fields", "experimental_design_object", "extensions"},
    "skill08_evidence_binding": {"literature_experiment", "evidence_map", "coverage"},
    "skill09_quality_evaluation": {"quality_evaluation", "evaluation_report", "score_details"},
    "skill10_k12_transfer": {"objective_clusters", "comparison_matrix", "candidate_design_space"},
    "skill11_engineering_proposal": {"engineering_plans", "ai_combination_proposals", "approval_status"},
}
def check(skill_name, content):
    required = REQUIRED_BY_SKILL.get(skill_name, set())
    missing = sorted(required - set(content)) if isinstance(content, dict) else sorted(required)
    return {"passed": isinstance(content, dict) and not missing, "issues": [{"code": "schema_missing", "field": x, "severity": "blocking"} for x in missing],
            "reason": f"{len(missing)} required skill-specific fields are missing."}

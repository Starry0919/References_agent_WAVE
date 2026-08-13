def check(skill_name, content):
    issues = []
    if skill_name == "skill11_engineering_proposal":
        for plan in content.get("engineering_plans", []):
            if plan.get("source_type") != "reported_in_literature":
                issues.append({"code": "track_a_source_mismatch", "plan_id": plan.get("plan_id"), "severity": "blocking"})
        for plan in content.get("ai_combination_proposals", []):
            if plan.get("source_type") != "ai_generated_proposal":
                issues.append({"code": "track_b_source_mismatch", "plan_id": plan.get("plan_id"), "severity": "blocking"})
    return {"passed": not issues, "issues": issues, "reason": f"{len(issues)} source-separation issues found."}

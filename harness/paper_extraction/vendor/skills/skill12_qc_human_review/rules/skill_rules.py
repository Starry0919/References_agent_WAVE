def additional_issues(skill_name, content):
    issues = []
    if skill_name == "skill11_engineering_proposal":
        ai = content.get("ai_combination_proposals", [])
        for plan in ai:
            level = plan.get("design_rationale", {}).get("suggestion_level")
            severity = "review" if level == 2 else "blocking" if level == 3 else "warning"
            issues.append({"code": f"ai_suggestion_level_{level}", "plan_id": plan.get("plan_id"), "severity": severity})
        if content.get("approval_status", {}).get("approval_required"):
            issues.append({"code": "upstream_approval_required", "severity": "review"})
    return issues

def check(skill_name, content):
    issues = []
    if skill_name == "skill11_engineering_proposal":
        for plan in content.get("ai_combination_proposals", []):
            rationale = plan.get("design_rationale", {})
            if not rationale.get("supporting_evidence"):
                issues.append({"code": "ai_proposal_without_evidence", "plan_id": plan.get("plan_id"), "severity": "blocking"})
            if not rationale.get("uncertainty"):
                issues.append({"code": "ai_proposal_without_uncertainty", "plan_id": plan.get("plan_id"), "severity": "blocking"})
            level = rationale.get("suggestion_level")
            if level == 3 and not plan.get("approval_status", {}).get("approval_required"):
                issues.append({"code": "unapproved_level3_hypothesis", "plan_id": plan.get("plan_id"), "severity": "blocking"})
    return {"passed": not issues, "issues": issues, "reason": f"{len(issues)} unsupported-generation signals found."}

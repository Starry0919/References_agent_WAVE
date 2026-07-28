def _field_status(fields, key):
    # Skill07 doesn't always wrap every field it emits as {value, status,
    # ...} (some come back as bare strings/None) - .get(key, {}) only
    # supplies the {} default when the key is ABSENT, not when it's
    # present with a non-dict value, so a plain string there would still
    # blow up a chained .get("status").
    value = fields.get(key)
    return value.get("status") if isinstance(value, dict) else None


def check(skill_name, content):
    issues = []
    if skill_name == "skill07_experiment_extraction":
        fields = content.get("fields", {})
        if _field_status(fields, "engineering_method") == "reported" and _field_status(fields, "strain") == "unknown":
            issues.append({"code": "intervention_without_strain", "severity": "warning"})
    if skill_name == "skill11_engineering_proposal":
        for plan in content.get("engineering_plans", []) + content.get("ai_combination_proposals", []):
            if set(plan.get("dbtl_plan", {})) != {"design", "build", "test", "learn"}:
                issues.append({"code": "dbtl_incomplete", "plan_id": plan.get("plan_id"), "severity": "review"})
    return {"passed": not issues, "issues": issues, "reason": f"{len(issues)} logic consistency issues found."}

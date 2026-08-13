def route(plans, ai_proposals):
    reasons = []
    if not plans: reasons.append("No evidence-supported reported plan is available.")
    if ai_proposals: reasons.append("Level 2 AI combination proposal requires human review.")
    if any(any(p["risks"].values()) for p in plans): reasons.append("Plan contains migration or interpretation risks.")
    if any("unknown" in str(p["experimental_details"]).lower() for p in plans): reasons.append("Unknown experimental details require completion.")
    return {"approval_required": bool(reasons), "reason": reasons,
            "status": "pending_human_review" if reasons else "auto_eligible_reported_only",
            "approval_scope": ["candidate selection", "unknown parameter completion", "execution authorization"] if reasons else []}

from .review_state import valid_transition
try:
    from ..schema import stable_id, now_iso
except ImportError:
    from schema import stable_id, now_iso
def create(artifact_id, issues):
    priority = "critical" if any(x["severity"] == "blocking" for x in issues) else "high" if any(x["severity"] == "review" for x in issues) else "medium"
    return {"task_id": stable_id("review", artifact_id, [x["code"] for x in issues]), "artifact_id": artifact_id,
            "priority": priority, "reason": "Automatic QC identified issues requiring human attention.",
            "issues": issues, "suggested_action": "Review evidence, source labels, unknown fields, and approval requirements.",
            "created_time": now_iso(), "status": "pending"}
def apply_action(task, action):
    kind = action.get("action")
    target = {"approve": "approved", "reject": "rejected", "modify": "revision_required", "comment": "in_review"}.get(kind)
    if not target or not valid_transition(task["status"], target): return False, task
    updated = dict(task); updated["status"] = target
    return True, updated

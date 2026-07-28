WORKFLOW_STATES={"CREATED","RUNNING","WAITING_REVIEW","COMPLETED","FAILED"}
def skill_state(status):
    return {"succeeded":"SUCCESS","succeeded_with_warnings":"WARNING","needs_review":"REVIEW_REQUIRED",
            "terminal_failure":"FAILED","retryable_failure":"FAILED","cancelled":"BLOCKED"}.get(status,"FAILED")

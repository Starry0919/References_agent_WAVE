RUN_STATES = {"CREATED", "RUNNING", "WAITING_REVIEW", "COMPLETED", "FAILED"}
STEP_STATES = {"PENDING", "RUNNING", "SUCCESS", "WARNING", "FAILED", "BLOCKED", "REVIEW_REQUIRED", "SKIPPED"}


def step_state(status):
    return {
        "succeeded": "SUCCESS",
        "succeeded_with_warnings": "WARNING",
        "needs_review": "REVIEW_REQUIRED",
        "terminal_failure": "FAILED",
        "retryable_failure": "FAILED",
        "cancelled": "BLOCKED",
        "skipped": "SKIPPED",
    }.get(status, "FAILED")

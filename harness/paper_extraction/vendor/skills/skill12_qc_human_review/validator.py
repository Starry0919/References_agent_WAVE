def validate(output, action=None):
    report, task, audit = output["qc_report"], output["review_task"], output["audit_event"]
    checks = [
        {"name": "qc_coverage", "passed": all(k in report for k in ("schema_check","provenance_check","evidence_check","completeness_check","logic_check","hallucination_check","source_separation_check"))},
        {"name": "review_task_complete", "passed": task is None or all(task.get(k) for k in ("task_id","artifact_id","priority","reason"))},
        {"name": "audit_complete", "passed": all(k in audit for k in ("before","after","reason","actor","timestamp"))},
        {"name": "nonblocking_review", "passed": report["final_status"] not in {"REVIEW_REQUIRED"} or output["continuation"]["pipeline_may_continue"]},
        {"name": "ai_cannot_approve", "passed": not action or not (action.get("actor_type") == "ai" and action.get("action") in {"approve","reject","modify"}) or report["final_status"] == "BLOCKED"},
    ]
    return checks

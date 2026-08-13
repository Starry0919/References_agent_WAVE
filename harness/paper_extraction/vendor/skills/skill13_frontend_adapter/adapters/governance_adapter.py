def build(governance,audit):
    core=governance.get("governance",governance)
    qc=governance.get("qc_report",{}).get("final_status","unknown")
    review=core.get("review_status","unknown")
    events=audit if isinstance(audit,list) else [audit] if audit else []
    states=["AI Generated"]
    if qc!="unknown": states.append("AI Checked")
    if review in {"pending","in_review","changes_requested"}: states.append("Human Review Pending")
    if review=="approved": states.append("Human Approved")
    return {"qc_status":qc,"review_status":review,"approval_required":review in {"pending","in_review","changes_requested"},
            "display_states":states,"audit_events":events,"publication_status":core.get("publication_status","unknown"),
            "review_task_ids":core.get("review_task_ids",[])}

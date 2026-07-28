def bind_workflow(workflow, unit_evidence):
    result = []
    for step in workflow:
        bound = dict(step)
        paragraph = step.get("source_location", {}).get("paragraph")
        evidence_ids = list(unit_evidence.get(paragraph, []))
        bound["evidence_ids"] = evidence_ids
        if step.get("status") == "reported" and not evidence_ids:
            bound["status"] = "unknown"
            bound["operation"] = None
            bound["reason"] = "Workflow source location could not be resolved."
        result.append(bound)
    return {"workflow": result}


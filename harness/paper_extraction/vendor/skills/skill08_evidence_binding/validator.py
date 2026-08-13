try:
    from .binder.evidence_validator import supports_value
except ImportError:
    from binder.evidence_validator import supports_value


def validate_output(literature_experiment, extensions):
    fields = literature_experiment["fields"]
    records = {v["evidence_id"]: v for v in literature_experiment["evidence"]}
    reported_have_evidence = all(
        v["status"] != "reported" or bool(v["evidence_ids"]) for v in fields.values()
    )
    evidence_resolves = all(
        evidence_id in records for field in fields.values() for evidence_id in field["evidence_ids"]
    )
    quotes_support = all(
        field["status"] != "reported"
        or supports_value(field["value"], [records[evidence_id]["quote"] for evidence_id in field["evidence_ids"]])[0]
        for field in fields.values()
    )
    unknown_consistent = all(
        v["status"] != "unknown" or (v["value"] is None and not v["evidence_ids"])
        for v in fields.values()
    )
    inference_valid = _inference_valid(extensions)
    extension_valid = _extension_valid(extensions)
    return [
        {"name": "reported_fields_have_evidence", "passed": reported_have_evidence},
        {"name": "evidence_ids_resolve", "passed": evidence_resolves},
        {"name": "quotes_support_values", "passed": quotes_support},
        {"name": "unknown_fields_are_empty", "passed": unknown_consistent},
        {"name": "inferred_units_have_reason", "passed": inference_valid},
        {"name": "extension_sources_resolve", "passed": extension_valid}
    ]


def _inference_valid(extensions):
    variables = extensions.get("variables", {})
    return all(
        item.get("status") != "inferred" or (item.get("reason") and item.get("evidence_ids"))
        for category in ("independent", "dependent", "controlled")
        for item in variables.get(category, [])
    )


def _extension_valid(extensions):
    workflow_ok = all(
        step.get("status") != "reported" or step.get("evidence_ids")
        for step in extensions.get("experiment_workflow", {}).get("workflow", [])
    )
    logic = extensions.get("design_logic", {})
    logic_ok = logic.get("status") == "unknown" or any(logic.get("evidence_ids", {}).values())
    return workflow_ok and logic_ok


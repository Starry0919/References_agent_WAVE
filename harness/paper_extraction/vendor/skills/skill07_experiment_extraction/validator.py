try:
    from .schema import CORE_FIELDS
except ImportError:
    from schema import CORE_FIELDS


def validate_output(fields, field_metadata, source_ids):
    complete = set(fields) == set(CORE_FIELDS)
    metadata_complete = set(field_metadata) == set(CORE_FIELDS)
    status_consistent = all(
        (field["status"] != "unknown" or (field["value"] is None and not field["evidence_ids"]))
        and (field["status"] != "reported" or (field["value"] is not None and field["evidence_ids"]))
        for field in fields.values()
    )
    sources_resolve = all(
        evidence_id.removeprefix("candidate:") in source_ids
        for field in fields.values() for evidence_id in field["evidence_ids"]
    )
    metadata_sources = all(
        fields[name]["status"] != "reported" or bool(field_metadata[name]["source_locations"])
        for name in CORE_FIELDS
    )
    allowed_status = all(v["status"] in {"reported", "unknown", "inferred"} for v in fields.values())
    no_unbound_reported = all(v["status"] != "reported" or v["evidence_ids"] for v in fields.values())
    return [
        {"name": "schema_completeness", "passed": complete and metadata_complete},
        {"name": "status_value_consistency", "passed": status_consistent},
        {"name": "source_location_completeness", "passed": metadata_sources},
        {"name": "candidate_evidence_resolves", "passed": sources_resolve},
        {"name": "allowed_status_values", "passed": allowed_status},
        {"name": "no_unbound_reported_values", "passed": no_unbound_reported}
    ]


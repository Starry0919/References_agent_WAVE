def validate(output,engineering):
    cards=output["step_cards"]; panels=output["detail_panels"]
    card_keys={(x["plan_id"],x["step_id"],x["phase"]) for x in cards}
    panel_keys={(x["plan_id"],x["step_id"],x["phase"]) for x in panels}
    referenced={eid for p in panels for eid in p["evidence_ids"]}
    displayed=set(output["evidence_view"]["by_id"])
    checks=[
        {"name":"what_why_how_complete","passed":all("what" in x and "why" in x and "how" in x for x in panels)},
        {"name":"evidence_traceability","passed":referenced.issubset(displayed) or output["evidence_view"]["status"]=="unknown"},
        {"name":"source_separation","passed":all(x["source_type"] in {"literature","AI_generated"} for x in cards+panels)},
        {"name":"governance_visible","passed":bool(output["governance_view"].get("review_status"))},
        {"name":"collapsed_expanded_consistent","passed":card_keys==panel_keys},
        {"name":"source_payload_preserved","passed":output["expanded_view"]["source_payload"]["engineering_plan"]==engineering},
    ]
    return checks

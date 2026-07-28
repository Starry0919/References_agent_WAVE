class Store:
    def __init__(self): self.events = []
    def append(self, event): self.events.append(event); return event
def step(source="reported_in_literature", evidence=True):
    return {"step_id":"D-1","source_type":source,"evidence":["ev1"] if evidence else [],"what":"reported","why":"reported","how":"reported"}
def content(evidence=True, ai_level=None):
    dbtl = {x:[step(evidence=evidence)] for x in ("design","build","test","learn")}
    result = {"engineering_plans":[{"plan_id":"p1","source_type":"reported_in_literature","dbtl_plan":dbtl}],
              "ai_combination_proposals":[], "approval_status":{"approval_required":False}}
    if ai_level:
        ai_dbtl = {x:[step("ai_generated_proposal")] for x in ("design","build","test","learn")}
        result["ai_combination_proposals"]=[{"plan_id":"ai1","source_type":"ai_generated_proposal","dbtl_plan":ai_dbtl,
            "design_rationale":{"suggestion_level":ai_level,"supporting_evidence":["ev1"],"uncertainty":"unknown"},
            "approval_status":{"approval_required":ai_level>=2}}]
    return result
def request(body=None, action=None):
    result={"skill_name":"skill11_engineering_proposal","artifact_id":"artifact-1","artifact_type":"engineering_plan",
            "artifact_content":body or content(),"provenance":{"skill_id":"skill11_engineering_proposal","skill_version":"0.2.0","input_hash":"a","output_hash":"b"},
            "quality_report":{},"previous_validation":[]}
    if action: result["review_action"]=action
    return result

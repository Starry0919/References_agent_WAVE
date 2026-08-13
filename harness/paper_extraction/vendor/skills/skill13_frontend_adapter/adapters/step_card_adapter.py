try:
    from ..schema import short
except ImportError:
    from schema import short
def all_steps(engineering):
    result=[]
    for plan in engineering.get("engineering_plans",[])+engineering.get("ai_combination_proposals",[]):
        for phase in ("design","build","test","learn"):
            for step in plan.get("dbtl_plan",{}).get(phase,[]):
                result.append((plan,phase,step))
    return result
def source_label(source):
    return "literature" if source=="reported_in_literature" else "AI_generated" if source=="ai_generated_proposal" else None
def cards(engineering):
    return [{"step_id":s.get("step_id"),"plan_id":p.get("plan_id"),"phase":phase,"title":s.get("title","unknown"),
             "short_description":short(s.get("what","unknown")),"source_type":source_label(s.get("source_type")),
             "status":"ready_for_display","expandable":True,"default_state":"collapsed"} for p,phase,s in all_steps(engineering)]
def details(engineering):
    panels=[]
    for plan,phase,s in all_steps(engineering):
        src=source_label(s.get("source_type")); rationale=plan.get("design_rationale",{})
        why={"literature_reason":[s.get("why")] if src=="literature" else [],
             "engineering_reason":[rationale.get("reasoning")] if rationale.get("reasoning") else [],
             "ai_reason":[s.get("why")] if src=="AI_generated" else []}
        panels.append({"step_id":s.get("step_id"),"plan_id":plan.get("plan_id"),"phase":phase,"source_type":src,
                       "what":s.get("what","unknown"),"why":why,
                       "how":{"operation":s.get("how","unknown"),"input":s.get("input",[]),"output":s.get("output",[]),
                              "parameters":s.get("how","unknown")},
                       "evidence_ids":s.get("evidence",[]),"validation_checkpoint":s.get("validation_checkpoint","unknown"),
                       "risk":s.get("risk",[])})
    return panels

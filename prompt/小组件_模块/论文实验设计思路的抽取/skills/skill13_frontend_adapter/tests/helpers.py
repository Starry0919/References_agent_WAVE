def step(source="reported_in_literature"):
    return {"step_id":"STEP-1","title":"Reported step","source_type":source,"what":"perform reported operation","why":"reported rationale",
            "how":{"method":"reported"},"input":["input"],"output":["output"],"evidence":["ev1"],"validation_checkpoint":"verify","risk":[]}
def engineering(ai=False,bad_source=False):
    source="unmarked" if bad_source else "ai_generated_proposal" if ai else "reported_in_literature"
    plan={"plan_id":"plan1","source_type":source,"objective":{"statement":"increase product in E. coli K-12","organism":"Escherichia coli","strain":"K-12"},
          "design_rationale":{"what":"gene knockout","reasoning":"combine evidence" if ai else None},
          "dbtl_plan":{x:[step(source)] for x in ("design","build","test","learn")},"risks":{"biological":[],"technical":[],"interpretation":[]}}
    return {"engineering_plans":[] if ai else [plan],"ai_combination_proposals":[plan] if ai else [],"approval_status":{"approval_required":ai}}
def evidence(present=True):
    return {"evidence_map":{"ev1":{"paper_id":"paper1","artifact_id":"a1","quote":"reported quote","locator":{"section_path":["Methods"],"page":2},"extraction":{"method":"binding"}}} if present else {}}
def quality():
    return {"quality_evaluation":{"completeness":.9,"evidence_level":.9,"reproducibility":.8,"extraction_confidence":.9,"missing_information":[]},
            "evaluation_report":{"dimensions":{"evidence_quality":{"grade":"A"}}}}
def k12():
    return {"k12_analysis":[{"paper_id":"paper1","compatibility":"high","confidence":.9,"reason":["matched"],"validation_needed":["verify"],
                             "transferability":{"transferability":"direct_reference"}}],"risk_assessment":[],"candidate_design_space":[]}
def governance(review="approved"):
    return {"qc_report":{"final_status":"PASS"},"governance":{"review_status":review,"publication_status":"publishable","review_task_ids":[]}}
def request(lang="zh",ai=False,evidence_present=True,bad_source=False,review="approved"):
    return {"engineering_plan":engineering(ai,bad_source),"k12_analysis":k12(),"evidence":evidence(evidence_present),
            "quality_report":quality(),"governance":governance(review),"audit_trail":[{"event_id":"audit1"}],"language":lang}

from pathlib import Path
def result(name,output,status="succeeded"):
    return {"status":status,"output":output,"artifacts":[],"self_check":{"passed":True,"checks":[],"score":1.0},
            "warnings":[],"errors":[],"metrics":{},"provenance":{"skill_id":name,"skill_version":"test","input_hash":"i","output_hash":"o"},"review_requests":[]}
def executors(fail_once=None,review=False,calls=None):
    calls=calls if calls is not None else [];failed={"done":False}
    outputs={
      "skill01_requirement_parser":{"research_intent":{},"retrieval_strategy":{}},
      "skill02_literature_retrieval":{"candidates":[{"paper_id":"p1"}]},
      "skill03_citation_validation":{"validated_candidates":[{"paper_id":"p1"}],"accepted_candidates":[{"paper_id":"p1"}]},
      "skill04_pdf_acquisition":{"paper_artifacts":[{"paper_identity":{"paper_id":"p1"}}]},
      "skill05_pdf_parser":{"document_artifact":{"document_metadata":{"paper_id":"p1"}}},
      "skill06_markdown_cleaner":{"clean_document_artifact":{"document_metadata":{"paper_id":"p1"}}},
      "skill07_experiment_extraction":{"fields":{},"experimental_design_object":{},"extensions":{}},
      "skill08_evidence_binding":{"evidence_map":{}},
      "skill09_quality_evaluation":{"quality_evaluation":{}},
      "skill10_k12_transfer":{"objective_clusters":[],"comparison_matrix":[],"candidate_design_space":[]},
      "skill11_engineering_proposal":{"engineering_plans":[],"ai_combination_proposals":[],"approval_status":{"approval_required":review}},
      "skill12_qc_human_review":{"qc_report":{"final_status":"REVIEW_REQUIRED" if review else "PASS"},"review_task":{"task_id":"r1"} if review else None,
                                  "audit_event":{"event_id":"a1","artifact_id":"mock-artifact"},"governance":{"review_status":"pending" if review else "not_required"}},
      "skill13_frontend_adapter":{"summary_view":{"title":"done"},"step_cards":[]}
    }
    def make(name):
        def run(request):
            calls.append(name)
            if name==fail_once and not failed["done"]:
                failed["done"]=True
                return {"status":"terminal_failure","output":None,"errors":[{"code":"TEST","message":"simulated"}],
                        "warnings":[],"artifacts":[],"metrics":{},"provenance":{"skill_version":"test"}}
            output=outputs[name]
            if name=="skill12_qc_human_review":
                # skill12 now runs once per upstream artifact (engine.py
                # _inputs): echo the real per-call artifact_id back, the way
                # the real skill does, so multiple mocked calls in one run
                # don't collide on the same qc_reports_by_artifact key.
                output={**output,"audit_event":{**output["audit_event"],"artifact_id":request.get("artifact_id","mock-artifact")}}
            return result(name,output,"needs_review" if review and name=="skill12_qc_human_review" else "succeeded")
        return run
    return {name:make(name) for name in outputs}
def request(task_id="task-1",source="upload"):
    source_type="upload" if source=="doi" else source
    return {"task_id":task_id,"user_request":"extract design","target_system":{"organism":"Escherichia coli","strain":"K-12"},
            "literature_source":{"type":source_type,"files":["paper.pdf"] if source=="upload" else [],"doi":["10.1/test"] if source=="doi" else []},
            "requirements":{},"mode":{"automatic":True,"human_review":True}}

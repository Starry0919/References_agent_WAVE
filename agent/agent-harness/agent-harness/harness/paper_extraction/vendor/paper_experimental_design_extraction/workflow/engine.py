from __future__ import annotations
import copy,time
from datetime import datetime,timezone
from pathlib import Path
from .artifacts import create
from .error_manager import normalize
from .state import skill_state
from .logger import WorkflowLogger
from ..skills import SkillRegistry,SKILLS
from ..storage import ArtifactStore

class WorkflowEngine:
    def __init__(self,config,executors=None):
        self.config=config;self.registry=SkillRegistry(executors)
        self.store=ArtifactStore(config.state_dir)
        self.logger=WorkflowLogger(Path(config.state_dir).parent/"workflow.jsonl")
    def run(self,request,options=None):
        options=dict(options or {});task_id=request["task_id"];started=datetime.now(timezone.utc).isoformat()
        checkpoint=self.store.load_checkpoint(task_id) if options.get("resume") else None
        state=checkpoint or {"task_id":task_id,"status":"CREATED","context":copy.deepcopy(options.get("initial_context",{})),
                             "artifacts":[],"errors":[],"warnings":[],"skill_states":{},"skill_logs":[]}
        state.setdefault("warnings",[])
        state["status"]="RUNNING";self._save(state)
        plan=self._plan(request,options)
        start=options.get("start_skill");end=options.get("end_skill")
        if start:
            plan=plan[plan.index(start):] if start in plan else plan
        try:
            for skill in plan:
                if checkpoint and state["skill_states"].get(skill) in {"SUCCESS","WARNING","REVIEW_REQUIRED"}:continue
                result=self._run_stage(skill,request,state,options)
                self._save(state)
                if result is None:continue
                if result.get("_blocked_for_input"):
                    state["status"]="WAITING_REVIEW";break
                if result.get("status") in {"terminal_failure","retryable_failure","cancelled"}:
                    state["status"]="FAILED";break
                if end==skill:break
            if state["status"]=="RUNNING":
                # A per-skill REVIEW_REQUIRED flag (skill_states[x]=="REVIEW_REQUIRED")
                # means that skill's own output carries a QC/governance flag
                # (skill12's own docstring: "Continue with trace marker for
                # REVIEW_REQUIRED; block only the current artifact for
                # BLOCKED.") - it is advisory, not a reason to withhold the
                # finished result from the user. Independent human review
                # (skill12's review_tasks, still in the report) audits
                # extraction quality alongside the agent's work, not gates
                # in front of it. Only a genuine mid-run blocker
                # (_blocked_for_input, handled above) or a hard failure
                # legitimately leaves the run short of COMPLETED.
                state["status"]="COMPLETED"
        except Exception as exc:
            state["errors"].append(normalize("workflow",{"code":"UNHANDLED","message":f"{type(exc).__name__}: {exc}","retryable":False}))
            state["status"]="FAILED"
        state["start_time"]=started;state["end_time"]=datetime.now(timezone.utc).isoformat()
        self._save(state)
        return self._report(request,state)
    def _run_stage(self,skill,request,state,options):
        state["skill_states"][skill]="RUNNING";before=len(state["artifacts"]);t0=time.perf_counter()
        self._save(state)  # persist RUNNING immediately - previously only SUCCESS/FAILED ever reached disk,
                            # since the only other _save call was after this stage fully finished, so a client
                            # polling the checkpoint could never see a stage as anything but done or not-started
        requests=self._inputs(skill,request,state["context"],options)
        if not requests:
            state["skill_states"][skill]="BLOCKED"
            state["errors"].append(normalize(skill,{"code":"NO_INPUT_ARTIFACT",
                "message":"No upstream artifact is available for this stage; human input or source recovery is required.",
                "retryable":True}))
            state["skill_logs"].append({"skill":skill,"input_artifact":None,"output_artifact":[],
                "duration":round((time.perf_counter()-t0)*1000,3),
                "errors":[state["errors"][-1]],"status":"BLOCKED"})
            self._save(state)
            return {"_blocked_for_input":True}
        results=[]
        total=len(requests)
        state.setdefault("skill_progress",{})[skill]={"completed":0,"total":total}
        for index,payload in enumerate(requests):
            result=self.registry.execute(skill,payload,options.get("skill_kwargs",{}).get(skill))
            results.append(result)
            # Some stages (skill07 experiment extraction) call the model once per
            # paper in this loop, sequentially - each one can take minutes, so
            # without this a client watching the checkpoint sees nothing change
            # for the entire stage duration. Saved per-item rather than once at
            # the end so "3/6 papers" is visible mid-stage, not just at the end.
            state["skill_progress"][skill]={"completed":index+1,"total":total}
            self._save(state)
            for err in result.get("errors",[]):state["errors"].append(normalize(skill,err))
            for warn in result.get("warnings",[]):state["warnings"].append(normalize(skill,warn))
            if result.get("output") is not None:
                artifact=create(state["task_id"],skill,result,index);state["artifacts"].append(artifact)
            if result.get("status") in {"terminal_failure","retryable_failure","cancelled"}:break
        aggregate=self._update_context(skill,results,state["context"])
        statuses=[skill_state(r.get("status")) for r in results]
        state["skill_states"][skill]="FAILED" if "FAILED" in statuses else "BLOCKED" if "BLOCKED" in statuses else "REVIEW_REQUIRED" if "REVIEW_REQUIRED" in statuses else "WARNING" if "WARNING" in statuses else "SUCCESS"
        state["skill_logs"].append({"skill":skill,"input_artifact":state["artifacts"][before-1]["artifact_id"] if before else None,
                                    "output_artifact":[x["artifact_id"] for x in state["artifacts"][before:]],
                                    "duration":round((time.perf_counter()-t0)*1000,3),
                                    "errors":[e for e in state["errors"] if e["skill"]==skill],
                                    "warnings":[w for w in state["warnings"] if w["skill"]==skill],
                                    "status":state["skill_states"][skill]})
        self._save(state);return aggregate
    def _inputs(self,skill,request,c,options):
        src=request["literature_source"]
        if skill=="skill01_requirement_parser":return [{"user_request":request["user_request"],"constraints":request.get("requirements",{})}]
        if skill=="skill02_literature_retrieval":return [{"research_intent":c["skill01"]["research_intent"],"retrieval_strategy":c["skill01"]["retrieval_strategy"],
                                                          "manual_candidates":options.get("manual_candidates",[]),
                                                          "limit":options.get("retrieval_limit",8)}]
        if skill=="skill03_citation_validation":
            candidates=c.get("skill02",{}).get("candidates") or self._doi_candidates(src.get("doi",[]))
            return [{"candidates":candidates}]
        if skill=="skill04_pdf_acquisition":
            uploads=[{"path":x,"paper_id":Path(x).stem} for x in src.get("files",[])]
            return [{"accepted_candidates":c.get("skill03",{}).get("accepted_candidates",[]),"manual_uploads":uploads,
                     "download_policy":options.get("pdf_download_policy",{"max_candidates":5})}]
        if skill=="skill05_pdf_parser":return [{"paper_artifact":x,"parse_policy":options.get("parse_policy",{})} for x in c.get("paper_artifacts",[])]
        if skill=="skill06_markdown_cleaner":return [{"document_artifact":x["document_artifact"]} for x in c.get("skill05",[])]
        if skill=="skill07_experiment_extraction":return [{"clean_document_artifact":x["clean_document_artifact"]} for x in c.get("skill06",[])]
        if skill=="skill08_evidence_binding":return [{"skill07_output":d,"clean_document_artifact":clean["clean_document_artifact"]} for d,clean in zip(c.get("skill07",[]),c.get("skill06",[]))]
        if skill=="skill09_quality_evaluation":return [{"skill08_output":e,"skill07_output":d} for d,e in zip(c.get("skill07",[]),c.get("skill08",[]))]
        if skill=="skill10_k12_transfer":return [{"experimental_designs":c.get("skill07",[]),"evidence_objects":c.get("skill08",[]),
                                                  "quality_reports":c.get("skill09",[]),"target_system":{"organism":request["target_system"]["organism"],
                                                  "strain_family":request["target_system"]["strain"]}}]
        if skill=="skill11_engineering_proposal":
            intent=c.get("skill01",{}).get("research_intent",{}) or {}
            user_target=intent.get("phenotype") or intent.get("engineering_objective")
            return [{"k12_design_space":c.get("skill10",{}),"experimental_designs":c.get("skill07",[]),
                     "evidence":c.get("skill08",[]),"quality_reports":c.get("skill09",[]),"user_target":user_target}]
        if skill=="skill12_qc_human_review":
            # Governance must cover every upstream extraction artifact, not
            # only the final engineering plan (framework/README.md Skill
            # registry: "Skill12 | all outputs | GovernanceResult"; qc/
            # schema_checker.py and logic_checker.py both define real checks
            # for skill07-skill10, not just skill11). Per-paper fan-out is
            # scoped to the single-design case to avoid ambiguous QC when
            # multiple candidate papers are still in play.
            def artifact_ref(name):
                return next((a for a in reversed(c.get("artifacts_snapshot",[])) if a["skill_name"]==name),None)
            requests=[]
            if c.get("skill11"):
                prev11=artifact_ref("skill11_engineering_proposal")
                requests.append({"skill_name":"skill11_engineering_proposal","artifact_id":prev11["artifact_id"] if prev11 else f"{request['task_id']}:skill11",
                         "artifact_type":"EngineeringPlanArtifact","artifact_content":c["skill11"],
                         "provenance":c.get("skill11_provenance",{}),"quality_report":c.get("skill09",[])[0] if c.get("skill09") else {},
                         "previous_validation":[]})
            if c.get("skill10"):
                prev10=artifact_ref("skill10_k12_transfer")
                requests.append({"skill_name":"skill10_k12_transfer","artifact_id":prev10["artifact_id"] if prev10 else f"{request['task_id']}:skill10",
                         "artifact_type":"K12TransferAnalysisArtifact","artifact_content":c["skill10"],
                         "provenance":c.get("skill10_provenance",{}),"quality_report":{},"previous_validation":[]})
            designs=c.get("skill07",[])
            for index in range(len(designs)):
                for name,key,artifact_type in (
                    ("skill09_quality_evaluation","skill09","QualityEvaluationArtifact"),
                    ("skill08_evidence_binding","skill08","EvidenceBindingArtifact"),
                    ("skill07_experiment_extraction","skill07","ExperimentalDesignArtifact"),
                ):
                    values=c.get(key,[])
                    if index>=len(values):continue
                    prev=artifact_ref(name)
                    provenance=c.get(f"{key}_provenance") or []
                    requests.append({"skill_name":name,"artifact_id":f"{prev['artifact_id']}:{index}" if prev else f"{request['task_id']}:{key}:{index}",
                             "artifact_type":artifact_type,"artifact_content":values[index],
                             "provenance":provenance[index] if index<len(provenance) else {},"quality_report":{},"previous_validation":[]})
            return requests
        if skill=="skill13_frontend_adapter":return [{"engineering_plan":c.get("skill11",{}),"k12_analysis":c.get("skill10",{}),
                                                       "evidence":c.get("skill08",[])[0] if c.get("skill08") else {},
                                                       "quality_report":c.get("skill09",[])[0] if c.get("skill09") else {},
                                                       "governance":c.get("skill12",{}),"audit_trail":[c.get("skill12",{}).get("audit_event",{})],
                                                       "language":options.get("language",self.config.language)}]
        raise KeyError(skill)
    def _update_context(self,skill,results,c):
        outputs=[r["output"] for r in results if r.get("output") is not None]
        if skill=="skill04_pdf_acquisition":c["paper_artifacts"]=[x for o in outputs for x in o.get("paper_artifacts",[])]
        elif skill in {"skill05_pdf_parser","skill06_markdown_cleaner","skill07_experiment_extraction","skill08_evidence_binding","skill09_quality_evaluation"}:
            c[skill[:7]]=outputs
            if skill in {"skill07_experiment_extraction","skill08_evidence_binding","skill09_quality_evaluation"}:
                c[f"{skill[:7]}_provenance"]=[r.get("provenance",{}) for r in results]
        elif skill=="skill12_qc_human_review":
            # skill12 now runs once per upstream artifact (skill07-skill11,
            # see _inputs above) instead of only skill11's plan - merge
            # those per-artifact QC results into one governance summary
            # rather than keeping only the first and silently discarding the
            # rest (worst status wins, so a clean final plan can never mask
            # an unreviewed extraction-stage QC failure).
            if not outputs:
                c["skill12"]={}
            else:
                order=["PASS","WARNING","REVIEW_REQUIRED","BLOCKED"]
                worst=max(outputs,key=lambda o:order.index(o["qc_report"]["final_status"]))
                c["skill12"]={**worst,
                              "qc_reports_by_artifact":{o["audit_event"]["artifact_id"]:o["qc_report"] for o in outputs},
                              "review_tasks":[o["review_task"] for o in outputs if o.get("review_task")]}
        else:
            c[skill[:7]]=outputs[0] if outputs else {}
            if skill=="skill10_k12_transfer" and results:c["skill10_provenance"]=results[0].get("provenance",{})
            if skill=="skill11_engineering_proposal" and results:c["skill11_provenance"]=results[0].get("provenance",{})
        return results[-1] if results else None
    def _plan(self,request,options):
        source=request["literature_source"]
        if options.get("start_skill"):return SKILLS
        if source["type"]=="auto_search":plan=SKILLS[:9]
        elif source.get("files"):plan=[SKILLS[0],*SKILLS[3:9]]
        else:plan=[SKILLS[0],*SKILLS[2:9]]
        target=request.get("target_system",{})
        is_k12="k-12" in f"{target.get('organism','')} {target.get('strain','')}".casefold()
        level=request.get("requirements",{}).get("result_level","extract")
        if is_k12 and level in {"adapt","engineering_plan"}:plan.append("skill10_k12_transfer")
        if is_k12 and level=="engineering_plan":plan.append("skill11_engineering_proposal")
        plan.append("skill12_qc_human_review")
        # Skill13's historical view is engineering-plan shaped. Extraction
        # and comparison results are already frontend-ready in _report.
        if level=="engineering_plan":plan.append("skill13_frontend_adapter")
        return plan
    @staticmethod
    def _doi_candidates(dois):
        return [{"paper_id":f"doi:{doi}","title":f"DOI {doi}","authors":[],"journal":None,"year":None,
                 "identifiers":{"doi":doi},"retrieval_sources":["user_doi"],
                 "citation_validation":{"status":"unknown","attempts":0,"checks":[]}} for doi in dois]
    def _save(self,state):
        state["context"]["artifacts_snapshot"]=state["artifacts"]
        self.store.save_checkpoint(state["task_id"],state)
    def _report(self,request,state):
        c=state["context"]
        return {"task_id":state["task_id"],"status":state["status"],
                "summary":c.get("skill13",{}).get("summary_view",{"message":"Workflow ended before frontend adaptation."}),
                "literature_candidates":c.get("skill02",{}).get("candidates",[]),
                "validated_papers":c.get("skill03",{}).get("validated_candidates",[]),
                "article_type_gate":{"items":[x.get("extensions",{}).get("article_type_gate",{}) for x in c.get("skill07",[])]},
                "paper_target_strains":[s for x in c.get("skill07",[]) for s in x.get("extensions",{}).get("paper_target_strains",[])],
                "experimental_designs":c.get("skill07",[]),
                "evidence_map":{str(i):x.get("evidence_map",{}) for i,x in enumerate(c.get("skill08",[]))},
                "quality_report":{"items":c.get("skill09",[])},
                "cross_paper_comparison":c.get("cross_paper_comparison",{}),
                "target_system_adaptation":c.get("skill10",{}),"k12_comparison":c.get("skill10",{}),
                "engineering_plan":c.get("skill11",{}),
                "governance":c.get("skill12",{}),"frontend_view":c.get("skill13",{}),
                "artifacts":state["artifacts"],"skill_states":state["skill_states"],
                "skill_logs":state["skill_logs"],"errors":state["errors"],"warnings":state.get("warnings",[]),
                "start_time":state.get("start_time"),"end_time":state.get("end_time")}

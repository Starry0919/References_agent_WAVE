"""Dynamic orchestrator for 生物学知识蒸馏.

Step01-15 are internal execution steps, not independent skills (SKILL.md
"内部编排"). The plan is computed from the request - which output levels
were asked for, whether fusion/paper-linking/frontend output are requested -
so a task that only wants Level 1 source parsing never pays for principle
distillation, and a task with no engineering goal is never blocked from
Level 1-4 just because no target organism was given (SKILL.md 第五章).
"""
from __future__ import annotations

import copy
import time
from datetime import datetime, timezone
from pathlib import Path

from .artifacts import create
from .error_manager import normalize
from .state import step_state
from .logger import WorkflowLogger
from ..skills import SkillRegistry, STEPS
from ..storage import ArtifactStore

ENGINEERING_LEVELS = {"level3_engineering_distillation", "level4_cross_source_fusion", "level5_knowledge_hub_adapter"}
POST_L1_LEVELS = {"level2_basic_knowledge", *ENGINEERING_LEVELS}


class WorkflowEngine:
    def __init__(self, config, executors=None):
        self.config = config
        self.registry = SkillRegistry(executors)
        self.store = ArtifactStore(config.state_dir)
        self.logger = WorkflowLogger(Path(config.state_dir).parent / "workflow.jsonl")

    def run(self, request, options=None):
        options = dict(options or {})
        task_id = request["task_id"]
        started = datetime.now(timezone.utc).isoformat()
        checkpoint = self.store.load_checkpoint(task_id) if options.get("resume") else None
        state = checkpoint or {
            "task_id": task_id, "status": "CREATED",
            "context": copy.deepcopy(options.get("initial_context", {})),
            "artifacts": [], "errors": [], "step_states": {}, "step_logs": [],
        }
        state["status"] = "RUNNING"
        self._save(state)
        plan = self._plan(request, options)
        for step in STEPS:
            if step not in plan and step not in state["step_states"]:
                state["step_states"][step] = "SKIPPED"
                state["step_logs"].append({"step": step, "status": "SKIPPED", "reason": "not_required_by_requested_output_level_or_flags"})
        start = options.get("start_step")
        end = options.get("end_step")
        if start:
            plan = plan[plan.index(start):] if start in plan else plan
        try:
            for step in plan:
                if checkpoint and state["step_states"].get(step) in {"SUCCESS", "WARNING", "REVIEW_REQUIRED"}:
                    continue
                result = self._run_stage(step, request, state, options)
                if result is None:
                    continue
                if result.get("_blocked_for_input"):
                    state["status"] = "WAITING_REVIEW"
                    break
                if result.get("status") in {"terminal_failure", "retryable_failure", "cancelled"}:
                    state["status"] = "FAILED"
                    break
                if end == step:
                    break
            if state["status"] == "RUNNING":
                has_review = any(v == "REVIEW_REQUIRED" for v in state["step_states"].values())
                state["status"] = "WAITING_REVIEW" if has_review and request.get("mode", {}).get("human_review", True) else "COMPLETED"
        except Exception as exc:  # keep a failed run auditable instead of an unhandled traceback
            state["errors"].append(normalize("workflow", {"code": "UNHANDLED", "message": f"{type(exc).__name__}: {exc}", "retryable": False}))
            state["status"] = "FAILED"
        state["start_time"] = started
        state["end_time"] = datetime.now(timezone.utc).isoformat()
        self._save(state)
        return self._report(request, state)

    def _run_stage(self, step, request, state, options):
        state["step_states"][step] = "RUNNING"
        before = len(state["artifacts"])
        t0 = time.perf_counter()
        requests = self._inputs(step, request, state["context"], options)
        if not requests:
            state["step_states"][step] = "BLOCKED"
            err = normalize(step, {
                "code": "NO_INPUT_ARTIFACT",
                "message": "No upstream artifact is available for this step; human input or source recovery is required.",
                "retryable": True,
            })
            state["errors"].append(err)
            state["step_logs"].append({"step": step, "input_artifact": None, "output_artifact": [],
                                        "duration": round((time.perf_counter() - t0) * 1000, 3),
                                        "errors": [err], "status": "BLOCKED"})
            self._save(state)
            return {"_blocked_for_input": True}
        results = []
        for index, payload in enumerate(requests):
            result = self.registry.execute(step, payload, options.get("step_kwargs", {}).get(step))
            results.append(result)
            for err in result.get("errors", []):
                state["errors"].append(normalize(step, err))
            if result.get("output") is not None:
                artifact = create(state["task_id"], step, result, index)
                state["artifacts"].append(artifact)
            if result.get("status") in {"terminal_failure", "retryable_failure", "cancelled"}:
                break
        aggregate = self._update_context(step, results, state["context"])
        statuses = [step_state(r.get("status")) for r in results]
        state["step_states"][step] = (
            "FAILED" if "FAILED" in statuses else
            "BLOCKED" if "BLOCKED" in statuses else
            "REVIEW_REQUIRED" if "REVIEW_REQUIRED" in statuses else
            "WARNING" if "WARNING" in statuses else "SUCCESS"
        )
        state["step_logs"].append({
            "step": step,
            "input_artifact": state["artifacts"][before - 1]["artifact_id"] if before else None,
            "output_artifact": [x["artifact_id"] for x in state["artifacts"][before:]],
            "duration": round((time.perf_counter() - t0) * 1000, 3),
            "errors": [e for e in state["errors"] if e["step"] == step],
            "status": state["step_states"][step],
        })
        self._save(state)
        return aggregate

    # ---- data flow between steps -------------------------------------------------
    def _inputs(self, step, request, c, options):
        if step == "step01_task_contract":
            return [{
                "user_request": request["user_request"],
                "input_sources": request["input_sources"],
                "target_domain": request.get("target_domain", []),
                "target_organism": request.get("target_organism", []),
                "target_strain": request.get("target_strain", []),
                "target_engineering_goal": request.get("target_engineering_goal", []),
                "requested_output_level": request.get("requested_output_level", []),
                "source_languages": request.get("source_languages", []),
                "output_languages": request.get("output_languages", ["zh", "en"]),
                "quality_requirement": request.get("quality_requirement", ""),
                "requires_cross_source_fusion": request.get("requires_cross_source_fusion", False),
                "requires_paper_case_linking": request.get("requires_paper_case_linking", False),
                "requires_frontend_adapter": request.get("requires_frontend_adapter", False),
            }]
        if step == "step02_source_validation":
            return [{"source_ref": src} for src in c["step01"]["input_sources"]]
        if step == "step03_pdf_parsing":
            return [{"source_ref": src, "validated_source": vs}
                    for src, vs in zip(c["step01"]["input_sources"], c.get("step02", []))]
        if step == "step04_markdown_cleaning":
            return [{"source_id": r["source_id"], "raw_markdown": r["raw_markdown"], "used_pdf_parser": r["used_pdf_parser"]}
                    for r in c.get("step03", [])]
        if step == "step05_document_parsing":
            return [{"validated_source": vs, "raw_text": r.get("clean_markdown", "")}
                    for vs, r in zip(c.get("step02", []), c.get("step04", []))]
        if step == "step06_scope_selection":
            return [{"source_structure": ss,
                      "target_domain": request.get("target_domain", []),
                      "target_engineering_goal": request.get("target_engineering_goal", [])}
                    for ss in c.get("step05", [])]
        if step == "step07_basic_knowledge_extraction":
            return [{"source_structure": ss, "extraction_scope": scope, "validated_source": vs}
                    for ss, scope, vs in zip(c.get("step05", []), c.get("step06", []), c.get("step02", []))]
        if step == "step08_principle_distillation":
            return [{
                "concepts": [x for r in c.get("step07", []) for x in r.get("concepts", [])],
                "mechanisms": [x for r in c.get("step07", []) for x in r.get("mechanisms", [])],
                "target_engineering_goal": request.get("target_engineering_goal", []),
                "target_organism": request.get("target_organism", []),
                "target_strain": request.get("target_strain", []),
            }]
        if step == "step09_decision_rule_generation":
            return [{
                "engineering_principles": c.get("step08", {}).get("engineering_principles", []),
                "concepts": [x for r in c.get("step07", []) for x in r.get("concepts", [])],
            }]
        if step == "step10_pattern_validation_failure":
            return [{
                "engineering_principles": c.get("step08", {}).get("engineering_principles", []),
                "decision_rules": c.get("step09", {}).get("decision_rules", []),
            }]
        if step == "step11_evidence_binding":
            return [{
                "concepts": [x for r in c.get("step07", []) for x in r.get("concepts", [])],
                "mechanisms": [x for r in c.get("step07", []) for x in r.get("mechanisms", [])],
                "engineering_principles": c.get("step08", {}).get("engineering_principles", []),
                "constraints_and_tradeoffs": c.get("step08", {}).get("constraints_and_tradeoffs", []),
                "decision_rules": c.get("step09", {}).get("decision_rules", []),
                "design_patterns": c.get("step10", {}).get("design_patterns", []),
                "validation_strategies": c.get("step10", {}).get("validation_strategies", []),
                "failure_patterns": c.get("step10", {}).get("failure_patterns", []),
                "source_structures": c.get("step05", []),
            }]
        if step == "step12_knowledge_fusion":
            audited = c.get("step11", {})
            return [{
                "knowledge_objects": audited.get("all_objects", []),
                "validated_sources": c.get("step02", []),
            }]
        if step == "step13_paper_case_linking":
            audited = c.get("step11", {})
            return [{
                "knowledge_objects": audited.get("all_objects", []),
                "paper_case_artifacts": request.get("paper_case_artifacts", []),
            }]
        if step == "step14_quality_governance":
            return [{
                "task_contract": c.get("step01", {}),
                "validated_sources": c.get("step02", []),
                "source_structures": c.get("step05", []),
                "extraction_scope": [s for r in c.get("step06", []) for s in r],
                "evidence_audit": c.get("step11", {}),
                "fusion": c.get("step12", {}),
                "paper_links": c.get("step13", {}).get("paper_case_links", []),
            }]
        if step == "step15_frontend_adapter":
            return [{
                "task_contract": c.get("step01", {}),
                "evidence_audit": c.get("step11", {}),
                "fusion": c.get("step12", {}),
                "paper_links": c.get("step13", {}).get("paper_case_links", []),
                "quality_report": c.get("step14", {}).get("quality_report", {}),
                "governance": c.get("step14", {}).get("governance", {}),
                "output_languages": request.get("output_languages", ["zh", "en"]),
            }]
        raise KeyError(step)

    def _update_context(self, step, results, c):
        outputs = [r["output"] for r in results if r.get("output") is not None]
        key = step.split("_", 1)[0]
        if step in {"step02_source_validation", "step03_pdf_parsing", "step04_markdown_cleaning", "step05_document_parsing", "step06_scope_selection", "step07_basic_knowledge_extraction"}:
            c[key] = outputs
        else:
            c[key] = outputs[0] if outputs else {}
        return results[-1] if results else None

    def _plan(self, request, options):
        if options.get("start_step"):
            return list(STEPS)
        levels = set(request.get("requested_output_level", []))
        plan = ["step01_task_contract", "step02_source_validation", "step03_pdf_parsing", "step04_markdown_cleaning", "step05_document_parsing"]
        if not (levels and levels == {"level1_source_parsing"}):
            plan += ["step06_scope_selection", "step07_basic_knowledge_extraction"]
        wants_engineering = bool(levels & ENGINEERING_LEVELS) or bool(request.get("target_engineering_goal"))
        if "step07_basic_knowledge_extraction" in plan and wants_engineering:
            plan += ["step08_principle_distillation", "step09_decision_rule_generation", "step10_pattern_validation_failure"]
        if "step07_basic_knowledge_extraction" in plan:
            plan.append("step11_evidence_binding")
        multi_source = len(request.get("input_sources", [])) > 1
        if "step11_evidence_binding" in plan and (bool(levels & {"level4_cross_source_fusion", "level5_knowledge_hub_adapter"}) or (request.get("requires_cross_source_fusion") and multi_source)):
            plan.append("step12_knowledge_fusion")
        if "step11_evidence_binding" in plan and request.get("requires_paper_case_linking") and request.get("paper_case_artifacts"):
            plan.append("step13_paper_case_linking")
        plan.append("step14_quality_governance")
        if bool(levels & {"level5_knowledge_hub_adapter"}) or request.get("requires_frontend_adapter"):
            plan.append("step15_frontend_adapter")
        return plan

    def _save(self, state):
        state["context"]["artifacts_snapshot"] = state["artifacts"]
        self.store.save_checkpoint(state["task_id"], state)

    def _report(self, request, state):
        c = state["context"]
        step11 = c.get("step11", {})
        step08 = c.get("step08", {})
        step09 = c.get("step09", {})
        step10 = c.get("step10", {})
        step12 = c.get("step12", {})
        step14 = c.get("step14", {})
        step15 = c.get("step15", {})
        return {
            "task_id": state["task_id"], "status": state["status"],
            "summary": step15.get("summary_view", {"message": "See quality_report and governance for a non-frontend summary."}),
            "task_contract": c.get("step01", {}),
            "validated_sources": c.get("step02", []),
            "source_structure": {"by_source": c.get("step05", [])},
            "extraction_scope": [s for r in c.get("step06", []) for s in r] if c.get("step06") else [],
            "biological_concepts": step11.get("concepts", [x for r in c.get("step07", []) for x in r.get("concepts", [])]),
            "biological_mechanisms": step11.get("mechanisms", [x for r in c.get("step07", []) for x in r.get("mechanisms", [])]),
            "engineering_principles": step11.get("engineering_principles", step08.get("engineering_principles", [])),
            "decision_rules": step11.get("decision_rules", step09.get("decision_rules", [])),
            "decision_trees": step09.get("decision_trees", []),
            "design_patterns": step11.get("design_patterns", step10.get("design_patterns", [])),
            "validation_strategies": step11.get("validation_strategies", step10.get("validation_strategies", [])),
            "failure_patterns": step11.get("failure_patterns", step10.get("failure_patterns", [])),
            "constraints_and_tradeoffs": step11.get("constraints_and_tradeoffs", step08.get("constraints_and_tradeoffs", [])),
            "canonical_knowledge_objects": step12.get("canonical_knowledge_objects", []),
            "cross_source_fusions": step12.get("cross_source_fusions", []),
            "source_conflicts": step12.get("source_conflicts", []),
            "paper_case_links": c.get("step13", {}).get("paper_case_links", []),
            "knowledge_graph": step15.get("knowledge_graph", {}),
            "quality_report": step14.get("quality_report", {}),
            "governance": step14.get("governance", {}),
            "frontend_view": step15.get("frontend_view", {}),
            "artifacts": state["artifacts"], "step_states": state["step_states"],
            "step_logs": state["step_logs"], "errors": state["errors"],
            "start_time": state.get("start_time"), "end_time": state.get("end_time"),
        }

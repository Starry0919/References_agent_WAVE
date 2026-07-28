from __future__ import annotations
import time
from typing import Any, Mapping
try:
    from .schema import SKILL_ID, SKILL_VERSION, RULESET, sha256_json
    from .error_codes import error
    from .logger import JsonlSkillLogger
    from .qc import schema_checker, provenance_checker, evidence_checker, completeness_checker, logic_checker, hallucination_checker, source_checker
    from .rules import additional_issues
    from .review import create as create_review, apply_action
    from .audit import build as build_audit, JsonlEventStore
    from .validator import validate
except ImportError:
    from schema import SKILL_ID, SKILL_VERSION, RULESET, sha256_json
    from error_codes import error
    from logger import JsonlSkillLogger
    from qc import schema_checker, provenance_checker, evidence_checker, completeness_checker, logic_checker, hallucination_checker, source_checker
    from rules import additional_issues
    from review import create as create_review, apply_action
    from audit import build as build_audit, JsonlEventStore
    from validator import validate

class GovernanceEngine:
    def __init__(self, logger=None, event_store=None):
        self.logger = logger if logger is not None else JsonlSkillLogger()
        self.event_store = event_store if event_store is not None else JsonlEventStore()

    def execute(self, request: Mapping[str, Any]):
        started = time.perf_counter(); input_hash = sha256_json(request)
        required = ("skill_name", "artifact_id", "artifact_type", "artifact_content", "provenance")
        if not isinstance(request, Mapping) or any(k not in request for k in required):
            return self._finish(self._failure(error("GOV001", {"missing": [k for k in required if k not in request]}), input_hash), started)
        skill_name, artifact_id = request["skill_name"], request["artifact_id"]
        content, provenance = request["artifact_content"], request["provenance"]
        checks = {
            "schema_check": schema_checker.check(skill_name, content),
            "provenance_check": provenance_checker.check(provenance),
            "evidence_check": evidence_checker.check(content),
            "completeness_check": completeness_checker.check(content),
            "logic_check": logic_checker.check(skill_name, content),
            "hallucination_check": hallucination_checker.check(skill_name, content),
            "source_separation_check": source_checker.check(skill_name, content),
        }
        issues = [issue for check in checks.values() for issue in check["issues"]]
        issues.extend(additional_issues(skill_name, content))
        action = request.get("review_action")
        action_error = self._validate_action(action)
        if action_error:
            issues.append({"code": action_error["code"], "severity": "blocking", "details": action_error})
        final_status = self._status(issues)
        qc_report = {**checks, "issues": issues, "final_status": final_status,
                     "confidence": self._confidence(checks, final_status)}
        review_task = create_review(artifact_id, issues) if final_status in {"REVIEW_REQUIRED", "BLOCKED"} else None
        if action and not action_error and review_task:
            ok, review_task = apply_action(review_task, action)
            if not ok:
                action_error = error("GOV004", {"action": action.get("action")})
                issues.append({"code": "GOV004", "severity": "blocking", "details": action_error})
                final_status = qc_report["final_status"] = "BLOCKED"
        audit = self._audit(artifact_id, content, qc_report, action, action_error)
        try:
            self.event_store.append(audit)
        except Exception as exc:
            return self._finish(self._failure(error("GOV003", {"type": type(exc).__name__}), input_hash), started)
        governance = self._governance(final_status, review_task)
        continuation = {"pipeline_may_continue": final_status != "BLOCKED",
                        "artifact_may_advance": final_status in {"PASS", "WARNING"},
                        "policy": "Continue with trace marker for REVIEW_REQUIRED; block only the current artifact for BLOCKED."}
        output = {"qc_report": qc_report, "review_task": review_task, "audit_event": audit,
                  "governance": governance, "continuation": continuation}
        self_checks = validate(output, action)
        result = {"status": "terminal_failure" if final_status == "BLOCKED" else "needs_review" if final_status == "REVIEW_REQUIRED" else "succeeded_with_warnings" if final_status == "WARNING" else "succeeded",
                  "output": output, "artifacts": [], "self_check": {"passed": all(x["passed"] for x in self_checks), "checks": self_checks,
                  "score": sum(x["passed"] for x in self_checks)/len(self_checks)}, "warnings": [action_error] if action_error else [],
                  "errors": [action_error] if action_error else [], "metrics": {"qc_status": final_status,
                  "review_required": review_task is not None, "review_task_id": review_task["task_id"] if review_task else None,
                  "audit_event_id": audit["event_id"]}, "provenance": {"skill_id": SKILL_ID, "skill_version": SKILL_VERSION,
                  "input_hash": input_hash, "output_hash": sha256_json(output), "ruleset_version": RULESET},
                  "review_requests": [review_task] if review_task else []}
        return self._finish(result, started)

    @staticmethod
    def _validate_action(action):
        if not action: return None
        if action.get("actor_type") == "ai" and action.get("action") in {"approve", "reject", "modify"}:
            return error("GOV005")
        if action.get("action") == "modify":
            if not all(k in action for k in ("before", "after", "reason")): return error("GOV004", {"reason": "modify requires before, after, and reason"})
            before, after = action["before"], action["after"]
            if GovernanceEngine._evidence_values(before) != GovernanceEngine._evidence_values(after):
                return error("GOV004", {"reason": "human modification cannot alter evidence facts"})
        if action.get("actor_type") != "human" and action.get("action") in {"approve", "reject", "modify"}:
            return error("GOV004", {"reason": "human identity required"})
        return None

    @staticmethod
    def _evidence_values(value):
        found = []
        def walk(v):
            if isinstance(v, dict):
                for k, x in v.items():
                    if k in {"evidence", "evidence_ids", "evidence_map"}: found.append((k, sha256_json(x)))
                    walk(x)
            elif isinstance(v, list):
                for x in v: walk(x)
        walk(value); return sorted(found)

    @staticmethod
    def _status(issues):
        levels = {x["severity"] for x in issues}
        if "blocking" in levels: return "BLOCKED"
        if "review" in levels: return "REVIEW_REQUIRED"
        if "warning" in levels: return "WARNING"
        return "PASS"

    @staticmethod
    def _confidence(checks, status):
        passed = sum(x["passed"] for x in checks.values()) / len(checks)
        return round(passed * {"PASS": 1, "WARNING": .9, "REVIEW_REQUIRED": .7, "BLOCKED": .3}[status], 3)

    @staticmethod
    def _audit(artifact_id, content, qc_report, action, action_error):
        if action:
            return build_audit(artifact_id, "human_review_action" if action.get("actor_type") == "human" else "rejected_actor_action",
                               action.get("actor_id", action.get("actor_type", "unknown")), action.get("action", "unknown"),
                               action.get("before", content), action.get("after", content),
                               action_error["message"] if action_error else action.get("reason", "Human review action recorded."),
                               action.get("evidence", []))
        return build_audit(artifact_id, "automatic_qc", "AI", "quality_control", content, content,
                           f"Automatic QC completed with status {qc_report['final_status']}.")

    @staticmethod
    def _governance(status, task):
        machine = "passed" if status == "PASS" else "warning" if status in {"WARNING", "REVIEW_REQUIRED"} else "failed"
        review = "pending" if task else "not_required"
        publication = "blocked" if status in {"REVIEW_REQUIRED", "BLOCKED"} else "publishable"
        return {"machine_status": machine, "review_status": review, "publication_status": publication,
                "review_task_ids": [task["task_id"]] if task else []}

    def _finish(self, result, started):
        result["metrics"]["duration_ms"] = round((time.perf_counter()-started)*1000, 3)
        output = result.get("output") or {}
        event = {"skill_name": SKILL_ID, "artifact_id": output.get("audit_event", {}).get("artifact_id"),
                 "qc_status": result["metrics"].get("qc_status"), "review_required": result["metrics"].get("review_required", False),
                 "review_task_id": result["metrics"].get("review_task_id"), "audit_event_id": result["metrics"].get("audit_event_id"),
                 "errors": result["errors"], "status": result["status"]}
        try: self.logger(event)
        except Exception: pass
        return result

    @staticmethod
    def _failure(err, input_hash):
        return {"status": "terminal_failure", "output": None, "artifacts": [], "self_check": {"passed": False, "checks": [], "score": 0.0},
                "warnings": [], "errors": [err], "metrics": {}, "provenance": {"skill_id": SKILL_ID, "skill_version": SKILL_VERSION,
                "input_hash": input_hash, "output_hash": None}, "review_requests": []}

def execute(request: Mapping[str, Any], **kwargs):
    return GovernanceEngine(**kwargs).execute(request)

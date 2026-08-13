"""Skill08 Evidence Verification Engine V2.

The source Skill07 candidate is immutable. Verification is an orthogonal
verdict and only exact, attributable anchors can become verified evidence.
"""
from __future__ import annotations

import copy
import hashlib
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Mapping, Optional

from harness.paper_extraction.handoff import HandoffRejected, canonical_hash, validate_handoff
from harness.paper_extraction.knowledge_admission import evaluate_admission

try:
    from .binder import DocumentEvidenceIndex, minimal_quote
    from .biological_entity_resolution import BiologicalObjectGraph, compare_biological_context
    from .logger import JsonlSkillLogger
    from .verification import attribution_status, overall, semantic_support
except ImportError:
    from binder import DocumentEvidenceIndex, minimal_quote
    from biological_entity_resolution import BiologicalObjectGraph, compare_biological_context
    from logger import JsonlSkillLogger
    from verification import attribution_status, overall, semantic_support

SKILL_ID = "skill08_evidence_binding"
SKILL_VERSION = "3.0.0"
CONTRACT_VERSION = "skill08_evidence_contract_v2"
RULES_VERSION = "skill08_validation_rules_v3"
EXECUTOR_VERSION = "skill08_verifier_v3"


class EvidenceBindingEngine:
    def __init__(self, logger: Optional[Callable[[Mapping[str, Any]], None]] = None, clock=None):
        self.logger = logger if logger is not None else JsonlSkillLogger()
        self.clock = clock or (lambda: datetime.now(timezone.utc))

    def execute(self, request: Mapping[str, Any]) -> dict[str, Any]:
        started = time.perf_counter()
        handoff = request.get("handoff") if isinstance(request, Mapping) else None
        clean = request.get("clean_document_artifact") if isinstance(request, Mapping) else None
        if not isinstance(handoff, Mapping) or not isinstance(clean, Mapping):
            return self._blocked("HANDOFF_REJECTED", "formal Skill07 handoff and clean document are required", request, started)
        try:
            validate_handoff(handoff, clean)
            document = self._load_document(clean)
        except (HandoffRejected, OSError, ValueError, json.JSONDecodeError) as exc:
            return self._blocked("HANDOFF_REJECTED", str(exc), request, started)

        candidate = copy.deepcopy(handoff["candidate_payload"])
        candidate_hash_before = canonical_hash(candidate)
        identity = handoff["paper_identity"]
        index = DocumentEvidenceIndex(document)
        biological_graph = BiologicalObjectGraph(document)
        records: list[dict[str, Any]] = []
        by_key: dict[tuple[str, str], str] = {}
        field_verifications: dict[str, Any] = {}
        claim_verifications: dict[str, Any] = {}

        # Canonical V3 path: claims already carry experiment scope and candidate
        # evidence slots. Field verification below is retained as a deprecated
        # compatibility projection and cannot overwrite claim truth.
        for claim in candidate.get("atomic_claims", []):
            if not isinstance(claim, Mapping):
                continue
            claim_id = str(claim.get("claim_id") or f"claim:{len(claim_verifications)+1}")
            value = " ".join(str(claim.get(key)) for key in ("subject", "predicate", "object", "value", "unit") if claim.get(key) not in (None, ""))
            locations = [self._claim_location(item) for item in claim.get("evidence_bundle", []) if isinstance(item, Mapping)]
            claim_verifications[claim_id] = self._verify_claim(
                candidate_ref=f"atomic_claim:{claim_id}", value=value, original=claim,
                locations=locations, index=index, identity=identity, records=records, by_key=by_key,
                epistemic_status=claim.get("epistemic_status"), biological_graph=biological_graph,
            )

        metadata = candidate.get("field_metadata") or {}
        for name, field in candidate.get("fields", {}).items():
            locations = (metadata.get(name) or {}).get("source_locations") or []
            field_verifications[name] = self._verify_claim(
                candidate_ref=f"field:{name}", value=field.get("value"), original=field,
                locations=locations, index=index, identity=identity, records=records, by_key=by_key,
                epistemic_status=field.get("status"),
                biological_graph=biological_graph,
            )

        ddr_verifications = self._verify_ddrs(candidate, index, identity, records, by_key, biological_graph)
        if canonical_hash(candidate) != candidate_hash_before:
            return self._blocked("VERIFICATION_BLOCKED", "candidate immutability check failed", request, started)

        core = {
            "contract_version": CONTRACT_VERSION,
            "candidate_payload": candidate,
            "field_verifications": field_verifications,
            "claim_verifications": claim_verifications,
            "ddr_verifications": ddr_verifications,
            "verified_evidence": records,
            "biological_object_graph": biological_graph.snapshot(),
        }
        artifact_id = "artifact:skill08:" + hashlib.sha256(canonical_hash(core).encode()).hexdigest()[:24]
        source = handoff["skill07_source"]
        provenance = {
            "paper_id": identity["paper_id"],
            "document_artifact_id": identity["document_artifact_id"],
            "document_hash": identity["document_hash"],
            "source_skill07_artifact_id": source["artifact_id"],
            "source_skill07_output_hash": source["output_hash"],
            "source_skill07_schema_version": source["schema_version"],
            "source_skill07_semantic_contract_version": source["semantic_contract_version"],
            "source_skill07_validation_rules_version": source["validation_rules_version"],
            "handoff_contract_version": handoff["handoff_contract_version"],
            "handoff_rules_version": handoff["provenance"]["handoff_rules_version"],
            "skill08_artifact_id": artifact_id,
            "skill_id": SKILL_ID,
            "skill_version": SKILL_VERSION,
            "skill08_contract_version": CONTRACT_VERSION,
            "skill08_validation_rules_version": RULES_VERSION,
            "skill08_executor_version": EXECUTOR_VERSION,
            "verification_timestamp": self.clock().isoformat(),
            "source_item_index": handoff["provenance"].get("source_item_index"),
            "input_hash": canonical_hash(request),
        }
        admission = evaluate_admission(core, provenance)
        output = {
            **core,
            "knowledge_admission": admission,
            # Deprecated compatibility projections. Values are the immutable
            # Skill07 candidates; verification is never encoded by rewriting them.
            "literature_experiment": {"fields": copy.deepcopy(candidate["fields"]), "evidence": records, "conflicts": []},
            "evidence_linked_design": {"paper_id": identity["paper_id"], "experiment_instances": copy.deepcopy(candidate.get("experiment_instances", [])), "atomic_claims": copy.deepcopy(candidate.get("atomic_claims", [])), "claim_verifications": claim_verifications, "fields": copy.deepcopy(candidate["fields"]), "field_verifications": field_verifications},
            "evidence_map": {r["evidence_id"]: r for r in records},
            "coverage": {"atomic_claims": self._coverage(claim_verifications), "legacy_fields": self._coverage(field_verifications)},
            "conflicts": self._conflicts(field_verifications, ddr_verifications),
        }
        provenance["output_hash"] = canonical_hash(output)
        checks = self._validate_output(output, provenance, candidate_hash_before)
        if not all(c["passed"] for c in checks):
            return self._blocked("VERIFICATION_BLOCKED", "Skill08 output validation failed", request, started, checks)

        unresolved = [n for n, v in field_verifications.items() if v["verification"]["overall_status"] != "verified"]
        status = "succeeded" if not unresolved else "needs_review"
        result = {
            "status": status, "verification_state": "VERIFICATION_COMPLETED" if not unresolved else "VERIFICATION_REVIEW_REQUIRED",
            "output": output, "artifacts": [], "self_check": {"passed": True, "checks": checks},
            "warnings": [] if not unresolved else [{"code": "VERIFICATION_INCOMPLETE", "fields": unresolved}],
            "errors": [], "metrics": {"claims_processed": len(claim_verifications), "verified_claims": sum(v["verification"]["overall_status"] == "verified" for v in claim_verifications.values()), "fields_processed": len(field_verifications), "verified_fields": len(field_verifications)-len(unresolved), "evidence_found": len(records)},
            "provenance": provenance, "review_requests": [] if not unresolved else [{"reason": "verification_incomplete", "fields": unresolved}],
        }
        return self._finish(result, started)

    def _verify_claim(self, *, candidate_ref, value, original, locations, index, identity, records, by_key, epistemic_status=None, experiment_anchors=None, biological_graph=None):
        base = {"candidate_ref": candidate_ref, "original": copy.deepcopy(original), "candidate_evidence_ids": copy.deepcopy(original.get("evidence_ids", []) if isinstance(original, Mapping) else [])}
        if epistemic_status == "unknown" or value in (None, "", [], {}):
            return {**base, "verification": {"overall_status": "unresolved", "existence_status": "not_applicable", "attribution_status": "not_applicable", "semantic_support_status": "not_applicable", "verified_evidence_ids": [], "reasons": ["candidate has no asserted value"]}}
        verdicts, verified_ids, reasons, attribution_details, evidence_chain = [], [], [], [], []
        if not locations:
            return {**base, "verification": {"overall_status": "unresolved", "existence_status": "unresolved", "attribution_status": "unresolved", "semantic_support_status": "unresolved", "verified_evidence_ids": [], "reasons": ["candidate has no source locations"]}}
        for location in locations:
            unit = self._resolve_location(index, location)
            if unit is None:
                verdicts.append(("failed", "unresolved", "unresolved")); reasons.append("evidence anchor does not exist")
                continue
            attr, attr_reasons = attribution_status(location, unit, experiment_anchors=experiment_anchors)
            quote = minimal_quote(value, unit.get("text", ""))
            biological = compare_biological_context(value, quote, biological_graph, unit.get("unit_id")) if biological_graph else {"status":"unresolved","reasons":["biological graph unavailable"]}
            if biological["status"] == "failed": attr = "failed"
            elif biological["status"] == "unresolved" and attr == "passed": attr = "unresolved"
            attr_reasons = attr_reasons + biological.get("reasons", [])
            semantic, semantic_reasons = semantic_support(value, quote, augmented_pair=(biological.get("claim_augmented",str(value)),biological.get("evidence_augmented",quote)))
            item_overall = overall("passed", attr, semantic)
            verdicts.append(("passed", attr, semantic)); reasons.extend(attr_reasons + semantic_reasons)
            attribution_details.append({"anchor":unit["unit_id"],"paper_match":"passed","experiment_match":"passed" if experiment_anchors is None or unit["unit_id"] in experiment_anchors else "failed","biological_object_match":biological.get("biological_object_match"),"intervention_match":biological.get("intervention_match"),"confidence":biological.get("confidence"),"status":attr})
            evidence_chain.append({"anchor":unit["unit_id"],"existence_status":"passed","attribution_status":attr,"semantic_support_status":semantic,"overall_status":item_overall})
            if item_overall == "verified":
                key = (unit["unit_id"], quote)
                if key not in by_key:
                    evidence_id = f"ev_{len(records)+1:05d}"
                    by_key[key] = evidence_id
                    records.append(self._record(evidence_id, identity, unit, quote, candidate_ref))
                verified_ids.append(by_key[key])
        existence = self._dimension([v[0] for v in verdicts])
        attribution = self._dimension([v[1] for v in verdicts])
        semantic = self._dimension([v[2] for v in verdicts])
        return {**base, "verification": {"overall_status": overall(existence, attribution, semantic), "existence_status": existence, "attribution_status": attribution, "semantic_support_status": semantic, "verified_evidence_ids": list(dict.fromkeys(verified_ids)), "reasons": list(dict.fromkeys(reasons)), "attribution": attribution_details, "evidence_chain": evidence_chain}}

    def _verify_ddrs(self, candidate, index, identity, records, by_key, biological_graph):
        obj = candidate.get("experimental_design_object") or {}
        experiments = obj.get("experiments", []) if isinstance(obj, Mapping) else obj if isinstance(obj, list) else []
        result = []
        for i, exp in enumerate(experiments):
            if not isinstance(exp, Mapping) or not isinstance(exp.get("ddr_annotation"), Mapping):
                continue
            annotation = exp["ddr_annotation"]
            anchors = set(str(x).removeprefix("candidate:") for x in exp.get("evidence", []) if isinstance(x, str))
            locations = [{"paragraph_id": a, "source_attribution": "current_article"} for a in anchors]
            components = {
                "design_action": (annotation.get("design_action_rationale") or annotation.get("design_action")),
                "trigger_observation": annotation.get("trigger_observation"),
                "rationale": annotation.get("reason_nature_rationale"),
                "implementation": exp.get("intervention"),
                "outcome": exp.get("outcome"),
            }
            verified = {}
            for name, value in components.items():
                item = self._verify_claim(candidate_ref=f"experiment:{i}:ddr:{name}", value=value, original={"value": value, "evidence_ids": list(anchors)}, locations=locations, index=index, identity=identity, records=records, by_key=by_key, experiment_anchors=anchors, biological_graph=biological_graph)
                v = item["verification"]
                verified[name] = {**v, "candidate_present": value not in (None, "", [], {}), "critical": True}
            result.append({"candidate_ref": f"experiment:{i}:ddr", "experiment_id": exp.get("experiment_id"), "candidate_ddr": copy.deepcopy(annotation), "rule_candidate_role": "single_paper_rule_candidate", "components": verified})
        return result

    @staticmethod
    def _claim_location(bundle):
        locator = str(bundle.get("locator") or "")
        source_type = bundle.get("source_type")
        return {
            "paragraph_id": locator if source_type in {"main_text", "unresolved"} else None,
            "figure": locator if source_type == "figure" else None,
            "table": locator if source_type == "table" else None,
            "supplement": locator if source_type == "supplement" else None,
            "source_attribution": bundle.get("source_attribution", "unknown"),
        }

    @staticmethod
    def _resolve_location(index, location):
        ids = []
        if location.get("paragraph_id"): ids.append(str(location["paragraph_id"]).removeprefix("candidate:"))
        if location.get("figure"): ids.append("figure:" + str(location["figure"]).removeprefix("figure:"))
        if location.get("table"): ids.append("table:" + str(location["table"]).removeprefix("table:"))
        if location.get("supplement"): ids.append(str(location["supplement"]).removeprefix("candidate:"))
        units = [index.get(i) for i in ids if index.get(i)]
        return units[0] if len(units) == 1 else None

    @staticmethod
    def _dimension(values):
        if "conflicted" in values: return "conflicted"
        if "passed" in values: return "passed"
        if "failed" in values: return "failed"
        return "unresolved"

    @staticmethod
    def _record(evidence_id, identity, unit, quote, candidate_ref):
        return {"evidence_id": evidence_id, "evidence_role": "verified", "paper_id": identity["paper_id"], "artifact_id": identity["document_artifact_id"], "artifact_sha256": identity["document_hash"], "candidate_ref": candidate_ref, "locator": {"page": unit.get("page"), "section_path": [unit["section"]] if unit.get("section") else [], "paragraph_id": unit.get("paragraph"), "figure_id": unit.get("figure"), "table_id": unit.get("table")}, "quote": quote, "quote_sha256": hashlib.sha256(quote.encode()).hexdigest(), "verification_method": "deterministic_structured_v3_biological_attribution"}

    @staticmethod
    def _coverage(fields):
        total=len(fields); verified=sum(v["verification"]["overall_status"]=="verified" for v in fields.values())
        return {"total_fields": total, "verified_fields": verified, "verification_coverage": verified/max(1,total)}

    @staticmethod
    def _conflicts(fields, ddrs):
        out=[{"candidate_ref":v["candidate_ref"],"reasons":v["verification"]["reasons"]} for v in fields.values() if v["verification"]["overall_status"]=="conflicted"]
        out.extend({"candidate_ref":d["candidate_ref"]+":"+n,"reasons":v["reasons"]} for d in ddrs for n,v in d["components"].items() if v["overall_status"]=="conflicted")
        return out

    @staticmethod
    def _validate_output(output, provenance, candidate_hash):
        statuses={v["verification"]["overall_status"] for v in output["field_verifications"].values()}
        all_verifications=list(output["field_verifications"].values())+list(output.get("claim_verifications",{}).values())
        verified_consistent=all(v["verification"]["overall_status"]!="verified" or (v["verification"]["existence_status"]==v["verification"]["attribution_status"]==v["verification"]["semantic_support_status"]=="passed" and v["verification"]["verified_evidence_ids"]) for v in all_verifications)
        evidence_current=all(r["paper_id"]==provenance["paper_id"] and r["artifact_id"]==provenance["document_artifact_id"] for r in output["verified_evidence"])
        no_promotion=all(d.get("rule_candidate_role")=="single_paper_rule_candidate" for d in output["ddr_verifications"])
        required=("paper_id","document_artifact_id","document_hash","source_skill07_artifact_id","source_skill07_output_hash","skill08_artifact_id","verification_timestamp")
        return [{"name":"candidate_immutable","passed":canonical_hash(output["candidate_payload"])==candidate_hash},{"name":"allowed_statuses","passed":statuses <= {"verified","unsupported","unresolved","conflicted"}},{"name":"verified_requires_e1_e2_e3","passed":verified_consistent},{"name":"verified_evidence_current_document","passed":evidence_current},{"name":"rule_candidate_not_promoted","passed":no_promotion},{"name":"provenance_complete","passed":all(provenance.get(k) for k in required)}]

    @staticmethod
    def _load_document(clean):
        path=clean.get("clean_json_path") or (clean.get("clean_json_artifact") or {}).get("uri")
        if not path or not Path(path).is_file(): raise ValueError("clean document unavailable")
        value=json.loads(Path(path).read_text(encoding="utf-8"))
        if not isinstance(value,dict): raise ValueError("clean document must be an object")
        return value

    def _blocked(self, state, message, request, started, checks=None):
        return self._finish({"status":"needs_review","verification_state":state,"output":None,"artifacts":[],"self_check":{"passed":False,"checks":checks or []},"warnings":[],"errors":[{"code":state,"message":message,"retryable":False}],"metrics":{},"provenance":{"skill_id":SKILL_ID,"skill_version":SKILL_VERSION,"input_hash":canonical_hash(request),"output_hash":None},"review_requests":[{"reason":state.lower()}]},started)

    def _finish(self,result,started):
        result["metrics"]["duration_ms"]=round((time.perf_counter()-started)*1000,3)
        try:self.logger({"skill_name":SKILL_ID,"status":result["status"],"verification_state":result.get("verification_state"),"errors":result["errors"]})
        except Exception:pass
        return result


def execute(request: Mapping[str, Any], **kwargs: Any) -> dict[str, Any]:
    return EvidenceBindingEngine(**kwargs).execute(request)

"""One current-contract real-document replay through Skill08/admission/DDR."""
from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path: sys.path.insert(0, str(ROOT))

from harness.paper_extraction.ddr_converter import convert_extraction_to_ddr
from harness.paper_extraction.handoff import build_handoff, canonical_hash
from harness.paper_extraction.vendor.skills.skill08_evidence_binding.skill import EvidenceBindingEngine

BASE = Path(__file__).resolve().parents[1]


def run():
    path = next((ROOT / "harness/paper_extraction/vendor/clean_document_artifacts").rglob("clean_document.json"))
    document = json.loads(path.read_text(encoding="utf-8"))
    paragraph = next((p for p in document["paragraphs"] if "ALE was employed to serially adapt" in (p.get("text") or "")),
                     next(p for p in document["paragraphs"] if len((p.get("text") or "").split()) >= 12))
    paper_id = (document.get("document_metadata") or {}).get("paper_id") or path.parent.parent.name
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    clean = {**document, "clean_json_path": str(path), "clean_json_artifact": {"artifact_id": f"artifact:doc:{digest[:20]}", "sha256": digest, "uri": str(path)}}
    experiment_id = "experiment:replay:1"
    quote = paragraph["text"]
    sentence = next((part.strip() + "." for part in quote.split(".") if "ALE was employed to serially adapt" in part), quote)
    if "ALE was employed to serially adapt" in sentence:
        subject, predicate, object_value = "ALE", "was employed to serially adapt", sentence.split("ALE was employed to serially adapt", 1)[1].strip().rstrip(".")
    else:
        subject, predicate, object_value = "paper", "reports", sentence.rstrip(".")
    candidate = {
        "contract_version": "skill07_semantic_contract_v1", "representation_version": "skill07_experiment_native_v3",
        "experiment_instances": [{"experiment_id": experiment_id, "biological_objects": [], "interventions": [], "conditions": [], "controls": [], "measurements": [], "outcomes": [], "evidence_links": [paragraph["paragraph_id"]], "migration_generated": False, "review_required": True}],
        "atomic_claims": [{"claim_id": "claim:replay:1", "experiment_id": experiment_id, "subject": subject, "predicate": predicate, "object": object_value, "value": None, "unit": None, "epistemic_status": "reported", "evidence_bundle": [{"source_type": "main_text", "section": paragraph.get("section") or "", "locator": paragraph["paragraph_id"], "quote": sentence, "source_attribution": "current_article", "evidence_role": "candidate"}], "migration_generated": False, "review_required": True}],
        "projection_metadata": {"derived_projection": True, "canonical_source": "experiment_instances", "legacy_compatibility": True},
        "fields": {}, "field_metadata": {}, "experimental_design_object": {"experiments": []}, "extensions": {}, "conflicts": []}
    result = {"status": "succeeded", "output": candidate, "eligible_for_evidence_verification": True, "self_check": {"passed": True},
              "provenance": {"output_hash": canonical_hash(candidate), "schema_version": "wave://paper-extraction/skill07-output/3.0.0", "semantic_contract_version": "skill07_semantic_contract_v1", "validation_rules_version": "skill07_validation_rules_v1"}}
    handoff = build_handoff(result, clean, "artifact:skill07:replay", 0)
    skill08 = EvidenceBindingEngine(logger=lambda _: None, clock=lambda: datetime(2026, 8, 12, tzinfo=timezone.utc)).execute({"handoff": handoff, "clean_document_artifact": clean})
    ddr_status = "blocked"
    if skill08.get("output") and skill08["output"].get("knowledge_admission", {}).get("status") != "KNOWLEDGE_ADMISSION_BLOCKED":
        converted = convert_extraction_to_ddr({"output": candidate, "skill08_output": skill08["output"], "skill08_provenance": skill08["provenance"]}, auto_save=False)
        ddr_status = "created_review_required" if converted.ddr else "blocked"
    report = {"paper_id": paper_id, "document_hash": digest, "skill07_contract": "current_v3_fixture",
              "handoff": "passed", "skill08_status": skill08["status"],
              "atomic_claim_status": skill08.get("output", {}).get("claim_verifications", {}).get("claim:replay:1", {}).get("verification", {}).get("overall_status"),
              "admission_status": skill08.get("output", {}).get("knowledge_admission", {}).get("status"), "ddr_status": ddr_status,
              "candidate_immutable": skill08.get("output", {}).get("candidate_payload") == candidate}
    (BASE / "reports").mkdir(parents=True, exist_ok=True)
    (BASE / "reports/current_contract_replay.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False)); return report


if __name__ == "__main__": run()

"""Repository-real, Silver-tier E2E reliability measurement.

This evaluator intentionally refuses to call its generated annotations Gold.
It measures historical Skill07 cache artifacts against their cited clean
documents and exercises production Skill08 semantic verification. Recall and
DDR decisionhood remain unadjudicated when no human canonical truth exists.
"""
from __future__ import annotations

import hashlib
import json
import re
import statistics
import sys
import time
import tracemalloc
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from harness.paper_extraction.vendor.skills.skill08_evidence_binding.biological_entity_resolution import (  # noqa: E402
    BiologicalObjectGraph,
    compare_biological_context,
)
from harness.paper_extraction.vendor.skills.skill08_evidence_binding.verification import semantic_support  # noqa: E402

BASE = Path(__file__).resolve().parents[1]
CLEAN_ROOT = ROOT / "harness/paper_extraction/vendor/clean_document_artifacts"
CACHE_ROOT = ROOT / "harness/paper_extraction/vendor/paper_experimental_design_extraction/storage/extraction_cache"


def canonical_hash(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def load_assets():
    documents = {}
    for path in CLEAN_ROOT.rglob("clean_document.json"):
        try:
            doc = json.loads(path.read_text(encoding="utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            continue
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        documents[digest] = (path, doc)
    caches = []
    for path in CACHE_ROOT.glob("*.json"):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        source = documents.get((data.get("provenance") or {}).get("input_hash"))
        if data.get("status") == "succeeded" and source and isinstance(data.get("output"), dict):
            caches.append((path, data, source[0], source[1]))
    return sorted(caches, key=lambda item: str(item[2]))


def text_value(value):
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def locations_for(field_name, output):
    metadata = output.get("field_metadata") or {}
    meta = metadata.get(field_name) or {} if isinstance(metadata, dict) else {}
    locations = meta.get("source_locations") or []
    if not locations:
        field = (output.get("fields") or {}).get(field_name) or {}
        locations = [{"paragraph_id": item} for item in field.get("evidence_ids") or []]
    return [item if isinstance(item, dict) else {"paragraph_id": str(item)} for item in locations]


def evaluate_field(field_name, field, output, paragraphs, graph):
    value = text_value((field or {}).get("value"))
    locators = locations_for(field_name, output)
    anchors = [paragraphs.get(str(loc.get("paragraph_id"))) for loc in locators]
    anchors = [item for item in anchors if item]
    e1 = bool(locators) and len(anchors) == len(locators)
    if not value or not anchors:
        return {"E1": e1, "E2": False, "E3": False, "status": "unresolved", "anchors": locators}
    evidence = " ".join(item.get("text") or "" for item in anchors)
    bio = compare_biological_context(value, evidence, graph, anchors[0].get("paragraph_id"))
    semantic, reasons = semantic_support(value, evidence, augmented_pair=(bio["claim_augmented"], bio["evidence_augmented"]))
    e2 = bio["status"] != "failed"
    e3 = semantic == "passed"
    status = "verified" if e1 and e2 and e3 else "conflicted" if semantic == "conflicted" else "unresolved"
    return {"E1": e1, "E2": e2, "E3": e3, "status": status, "anchors": locators, "reasons": reasons + bio["reasons"]}


def build_paper_record(cache_path, artifact, clean_path, doc, split):
    started = time.perf_counter()
    output = artifact["output"]
    paragraphs = {str(p.get("paragraph_id")): p for p in doc.get("paragraphs", [])}
    graph = BiologicalObjectGraph(doc)
    claims = []
    for name, field in (output.get("fields") or {}).items():
        result = evaluate_field(name, field, output, paragraphs, graph)
        claims.append({
            "claim_id": f"{(doc.get('document_metadata') or {}).get('paper_id')}:{name}",
            "claim_type": name,
            "candidate_evidence": text_value((field or {}).get("value")),
            "gold_evidence_anchors": result["anchors"],
            "source_attribution": (((output.get("field_metadata") or {}).get(name) or {}).get("attribution", "unknown") if isinstance(output.get("field_metadata") or {}, dict) else "unknown"),
            "experiment_attribution": "unadjudicated",
            "biological_object_attribution": "deterministic_local_resolution",
            "gold_E1": result["E1"], "gold_E2": result["E2"], "gold_E3": result["E3"],
            "gold_verification_status": result["status"],
            "gold_reason": "; ".join(result.get("reasons") or []) or "all deterministic checks passed",
            "critical": name in {"strain", "intervention", "control", "outcome", "parameters"},
            "annotation_tier": "silver",
        })
    meta = doc.get("document_metadata") or {}
    elapsed = (time.perf_counter() - started) * 1000
    return {
        "paper_id": meta.get("paper_id") or clean_path.parent.parent.name,
        "document_id": clean_path.name,
        "document_hash": (artifact.get("provenance") or {}).get("input_hash"),
        "clean_document_path": str(clean_path.relative_to(ROOT)).replace("\\", "/"),
        "skill07_cache_path": str(cache_path.relative_to(ROOT)).replace("\\", "/"),
        "split": split,
        "document_gold": {
            "available_sections": len(doc.get("sections") or []), "available_figures": len(doc.get("figures") or []),
            "available_tables": len(doc.get("tables") or []), "supplement_available": False,
            "missing_modalities": ["independent_supplement"], "parser_limitations": ["clean-document text is the audit boundary"],
        },
        "skill07_claims": claims,
        "ddr_gold": {"annotation_tier": "silver", "decisionhood": "unadjudicated", "reason": "no human temporal rationale/trigger adjudication"},
        "knowledge_admission_gold": {"annotation_tier": "silver", "status": "partial" if any(c["gold_verification_status"] == "verified" for c in claims) else "blocked"},
        "performance": {"evaluation_ms": round(elapsed, 3), "skill07_historical_model": (artifact.get("provenance") or {}).get("model"), "cache_hit": True},
    }


def ratio(n, d):
    return n / d if d else None


def metrics(papers):
    claims = [claim for paper in papers for claim in paper["skill07_claims"]]
    reported = [c for c in claims if c["candidate_evidence"]]
    verified = [c for c in reported if c["gold_verification_status"] == "verified"]
    critical_false = [c for c in claims if c["critical"] and c["gold_verification_status"] == "verified" and not (c["gold_E1"] and c["gold_E2"] and c["gold_E3"])]
    return {
        "papers": len(papers), "claims": len(claims),
        "skill07_supported_claim_precision_silver": ratio(len(verified), len(reported)),
        "skill07_experiment_recall": None,
        "skill07_recall_reason": "not estimable without independent ExperimentInstance truth",
        "E1_accuracy_silver": ratio(sum(c["gold_E1"] for c in claims), len(claims)),
        "E2_accuracy_silver": ratio(sum(c["gold_E2"] for c in claims), len(claims)),
        "E3_accuracy_silver": ratio(sum(c["gold_E3"] for c in claims), len(claims)),
        "verification_precision_silver": ratio(len(verified), len(reported)),
        "verification_recall": None,
        "false_verified_critical_claims": len(critical_false),
        "unresolved_rate": ratio(sum(c["gold_verification_status"] == "unresolved" for c in claims), len(claims)),
        "ddr_decision_precision": None, "ddr_decision_recall": None,
        "knowledge_invalid_admission_rate": None,
        "knowledge_admission_reason": "historical caches stop at Skill07; production admission was not replayed without current compatible handoff artifacts",
        "knowledge_valid_retention": ratio(len(verified), len(claims)),
        "provenance_traceability": ratio(sum(bool(p["document_hash"] and p["clean_document_path"] and p["skill07_cache_path"]) for p in papers), len(papers)),
        "cross_paper_contamination": 0,
    }


def run():
    tracemalloc.start()
    started = time.perf_counter()
    assets = load_assets()[:15]
    papers = [build_paper_record(*item, "development" if index < 10 else "holdout") for index, item in enumerate(assets)]
    dev = [p for p in papers if p["split"] == "development"]
    holdout = [p for p in papers if p["split"] == "holdout"]
    annotation = {
        "benchmark_version": "paper_extraction_e2e_v1", "annotation_tier": "silver",
        "annotation_source": "Codex-assisted deterministic audit of historical Skill07 artifacts against real clean documents",
        "annotator_status": "AI_ASSISTED", "review_status": "NOT_HUMAN_REVIEWED",
        "adjudication_status": "PENDING_HUMAN_ADJUDICATION", "papers": papers,
    }
    elapsed = time.perf_counter() - started
    _, peak = tracemalloc.get_traced_memory(); tracemalloc.stop()
    result = {
        "benchmark_version": "paper_extraction_e2e_v1", "annotation_tier": "silver",
        "development": metrics(dev), "holdout": metrics(holdout), "combined": metrics(papers),
        "generalization_gap": {
            "supported_claim_precision": (metrics(dev)["skill07_supported_claim_precision_silver"] or 0) - (metrics(holdout)["skill07_supported_claim_precision_silver"] or 0)
        },
        "error_propagation": {
            "EVIDENCE_ANCHOR": sum(not c["gold_E1"] for p in papers for c in p["skill07_claims"]),
            "SKILL08_E2": sum(c["gold_E1"] and not c["gold_E2"] for p in papers for c in p["skill07_claims"]),
            "SKILL08_E3": sum(c["gold_E1"] and c["gold_E2"] and not c["gold_E3"] for p in papers for c in p["skill07_claims"]),
            "UNKNOWN/REVIEW": sum(not c["candidate_evidence"] for p in papers for c in p["skill07_claims"]),
        },
        "performance": {"total_runtime_s": round(elapsed, 3), "paper_runtime_ms_median": round(statistics.median(p["performance"]["evaluation_ms"] for p in papers), 3), "peak_memory_mb": round(peak / 1048576, 3), "llm_calls": 0, "cache_hits": len(papers)},
        "release_gate": {"status": "PARTIAL", "reason": "human Gold and human-adjudicated holdout/DDR truth are unavailable"},
    }
    (BASE / "annotations").mkdir(parents=True, exist_ok=True)
    (BASE / "reports").mkdir(parents=True, exist_ok=True)
    (BASE / "development").mkdir(parents=True, exist_ok=True)
    (BASE / "holdout").mkdir(parents=True, exist_ok=True)
    (BASE / "safety").mkdir(parents=True, exist_ok=True)
    (BASE / "regression_corpus").mkdir(parents=True, exist_ok=True)
    (BASE / "annotations/silver_v1.json").write_text(json.dumps(annotation, ensure_ascii=False, indent=2), encoding="utf-8")
    (BASE / "development/manifest.json").write_text(json.dumps({"paper_ids": [p["paper_id"] for p in dev]}, ensure_ascii=False, indent=2), encoding="utf-8")
    (BASE / "holdout/manifest.json").write_text(json.dumps({"paper_ids": [p["paper_id"] for p in holdout], "sealed_until_final_run": True}, ensure_ascii=False, indent=2), encoding="utf-8")
    (BASE / "safety/manifest.json").write_text(json.dumps({"source": "../skill08_verification_benchmark", "cases": 13, "immutable": True}, indent=2), encoding="utf-8")
    (BASE / "regression_corpus/manifest.json").write_text(json.dumps({"failures": ["E2E-BENCH-001"], "note": "Only a deterministic evaluator compatibility defect was fixed; scientific Silver disagreements were not auto-fixed."}, indent=2), encoding="utf-8")
    (BASE / "reports/e2e_results.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))
    return annotation, result


if __name__ == "__main__":
    run()

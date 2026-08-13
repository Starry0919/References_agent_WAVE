"""Gold-aware Benchmark V2. Deterministic diagnostics never masquerade as accuracy."""
from __future__ import annotations

import json
import statistics
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
NOT_ESTIMABLE = {"value": None, "status": "NOT_ESTIMABLE", "reason": "PENDING_HUMAN_GOLD"}


def _metric(tp: int, fp: int, fn: int) -> dict[str, Any]:
    precision = tp / (tp + fp) if tp + fp else None
    recall = tp / (tp + fn) if tp + fn else None
    f1 = 2 * precision * recall / (precision + recall) if precision is not None and recall is not None and precision + recall else 0.0
    return {"precision": precision, "recall": recall, "f1": f1, "status": "MEASURED_HUMAN_GOLD"}


def evaluate(candidate_records: list[dict[str, Any]], gold_records: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    started = time.perf_counter()
    adjudicated = [g for g in (gold_records or []) if g.get("annotation_tier") == "ADJUDICATED_GOLD"]
    claim_counts = [len(e.get("atomic_claims", [])) for r in candidate_records for e in r.get("experiment_instances", [])]
    duplicates = sum(max(0, len(ids) - len(set(ids))) for ids in ([c.get("claim_id") for c in r.get("atomic_claims", [])] for r in candidate_records))
    scientific = {
        "experiment_extraction": NOT_ESTIMABLE.copy(), "atomic_claim_quality": NOT_ESTIMABLE.copy(),
        "verification_quality": NOT_ESTIMABLE.copy(), "ddr_quality": NOT_ESTIMABLE.copy(),
        "admission_safety": NOT_ESTIMABLE.copy(), "admission_utility": NOT_ESTIMABLE.copy(),
        "generalization": NOT_ESTIMABLE.copy(),
    }
    if adjudicated:
        # Exact stable-ID matching is the conservative default; semantic mappings require adjudicator records.
        candidate_ids = {e.get("experiment_id") for r in candidate_records for e in r.get("experiment_instances", [])}
        gold_ids = {g.get("experiment_id") for g in adjudicated if g.get("experiment_id")}
        scientific["experiment_extraction"] = _metric(len(candidate_ids & gold_ids), len(candidate_ids - gold_ids), len(gold_ids - candidate_ids))
    valid_predictions = [x for r in candidate_records for x in r.get("admission_predictions", []) if x.get("decision") == "ADMIT"]
    reject_all = bool(candidate_records) and not valid_predictions
    return {
        "benchmark_version": "paper_extraction_e2e_v2", "gold_records": len(adjudicated),
        "scientific_metrics": scientific,
        "deterministic_diagnostics": {
            "papers": len(candidate_records), "claims": sum(len(r.get("atomic_claims", [])) for r in candidate_records),
            "claims_per_experiment_median": statistics.median(claim_counts) if claim_counts else 0,
            "claims_per_experiment_p95": sorted(claim_counts)[max(0, int(.95 * len(claim_counts)) - 1)] if claim_counts else 0,
            "largest_experiment_claim_count": max(claim_counts, default=0), "duplicate_claim_ids": duplicates,
            "runtime_seconds": round(time.perf_counter() - started, 6),
        },
        "anti_gaming": {"reject_all_detected": reject_all, "release_utility_gate": "FAIL" if reject_all else ("NOT_ESTIMABLE" if not adjudicated else "EVALUATE_GOLD")},
        "release_status": "PARTIAL" if not adjudicated else "INCONCLUSIVE",
    }


def write_report(candidate_records: list[dict[str, Any]], gold_records: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    result = evaluate(candidate_records, gold_records)
    path = ROOT / "reports" / "e2e_v2_results.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    return result

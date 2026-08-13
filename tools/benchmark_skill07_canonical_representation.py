"""Shadow benchmark for Skill07 canonical document representation v0.1.

The script never modifies production inputs, prompt/schema files, or the
production extraction cache.  Model outputs are written beneath an isolated
benchmark directory.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import random
import statistics
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(REPO_ROOT / ".env", override=False)
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import harness.paper_extraction.opus_extractor as skill07  # noqa: E402
from tools.canonical_document_transformer import (  # noqa: E402
    REPRESENTATION_VERSION,
    restore_document,
    transform_document,
)

STORAGE = REPO_ROOT / "harness/paper_extraction/vendor/paper_experimental_design_extraction/storage"
DEFAULT_OUTPUT = REPO_ROOT / "artifacts/skill07_canonical_representation_v0_1"


def _sha(value: Any) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _percentile(values: list[float], percentile: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    index = (len(ordered) - 1) * percentile
    low = int(index)
    high = min(low + 1, len(ordered) - 1)
    return ordered[low] + (ordered[high] - ordered[low]) * (index - low)


def _summary(values: list[float]) -> dict[str, Any]:
    return {
        "n": len(values),
        "min": min(values) if values else None,
        "median": statistics.median(values) if values else None,
        "p95": _percentile(values, 0.95),
        "max": max(values) if values else None,
    }


def discover_documents() -> list[tuple[Path, dict[str, Any]]]:
    found: dict[str, tuple[Path, dict[str, Any]]] = {}
    cache_dir = STORAGE / "pipeline_cache/skill06_markdown_cleaner"
    for cache_path in sorted(cache_dir.glob("*.json")):
        try:
            cached = json.loads(cache_path.read_text(encoding="utf-8"))
            clean_path = Path(cached["output"]["clean_document_artifact"]["clean_json_path"])
            document = json.loads(clean_path.read_text(encoding="utf-8"))
        except (KeyError, OSError, json.JSONDecodeError):
            continue
        found.setdefault(_sha(document), (clean_path, document))
    return list(found.values())


def select_documents(documents: list[tuple[Path, dict[str, Any]]], count: int) -> list[tuple[Path, dict[str, Any]]]:
    """Deterministically span document size/structure instead of taking first N."""
    ranked = sorted(
        documents,
        key=lambda item: (
            len(json.dumps(item[1], ensure_ascii=False)),
            len(item[1].get("figures", [])),
            len(item[1].get("tables", [])),
            str(item[1].get("document_metadata", {}).get("paper_id", "")),
        ),
    )
    if count >= len(ranked):
        return ranked
    indexes = []
    for position in range(count):
        index = round(position * (len(ranked) - 1) / (count - 1)) if count > 1 else 0
        if index not in indexes:
            indexes.append(index)
    return [ranked[index] for index in indexes]


def information_checks(original: dict[str, Any], canonical: dict[str, Any]) -> dict[str, Any]:
    restored = restore_document(canonical)
    def recall(key: str) -> float:
        expected = len(original.get(key, []))
        return len(restored.get(key, [])) / expected if expected else 1.0

    return {
        "exact_roundtrip": _sha(restored) == _sha(original),
        "paragraph_recall": recall("paragraphs"),
        "section_recall": recall("sections"),
        "figure_recall": recall("figures"),
        "table_recall": recall("tables"),
        "citation_recall": recall("citations"),
        "paragraph_content_exact": restored.get("paragraphs") == original.get("paragraphs"),
        "section_content_exact": restored.get("sections") == original.get("sections"),
        "figures_exact": restored.get("figures") == original.get("figures"),
        "tables_exact": restored.get("tables") == original.get("tables"),
        "citations_exact": restored.get("citations") == original.get("citations"),
        "residual_coverage": 1.0 if _sha(restored) == _sha(original) else 0.0,
    }


def prepare_representation_benchmark(count: int, output_dir: Path) -> dict[str, Any]:
    selected = select_documents(discover_documents(), count)
    documents: list[dict[str, Any]] = []
    for index, (source_path, original) in enumerate(selected, start=1):
        paper_id = str(original.get("document_metadata", {}).get("paper_id") or f"paper-{index}")
        safe_id = hashlib.sha256(paper_id.encode("utf-8")).hexdigest()[:12]
        paper_dir = output_dir / f"{index:02d}_{safe_id}"
        paper_dir.mkdir(parents=True, exist_ok=True)
        canonical, transformation = transform_document(original)
        canonical_path = paper_dir / "canonical_document_v0.1.json"
        report_path = paper_dir / "transformation_report.json"
        canonical_path.write_text(json.dumps(canonical, ensure_ascii=False, indent=2), encoding="utf-8")
        report_path.write_text(json.dumps(transformation, ensure_ascii=False, indent=2), encoding="utf-8")
        checks = information_checks(original, canonical)
        documents.append({
            "index": index,
            "paper_id": paper_id,
            "source_clean_document": str(source_path),
            "source_document": original,
            "canonical_document": canonical,
            "canonical_path": str(canonical_path),
            "transformation_report_path": str(report_path),
            "original_size": {
                "characters": transformation["original_characters"],
                "bytes": transformation["original_bytes"],
                "estimated_tokens_chars_div_4": transformation["original_characters"] / 4,
            },
            "canonical_size": {
                "characters": transformation["canonical_characters"],
                "bytes": transformation["canonical_bytes"],
                "estimated_tokens_chars_div_4": transformation["canonical_characters"] / 4,
            },
            "reduction": {
                "characters_fraction": transformation["character_reduction_fraction"],
                "bytes_fraction": transformation["byte_reduction_fraction"],
            },
            "transformation": transformation,
            "information_checks": checks,
        })
    return {"representation_version": REPRESENTATION_VERSION, "documents": documents}


def _extract_once(document: dict[str, Any], task_id: str, model: str) -> dict[str, Any]:
    request = {
        "task_id": task_id,
        "user_request": "Benchmark Skill07 document representation equivalence.",
        "target_system": {},
        "requirements": {},
        "clean_document_artifact": document,
    }
    input_checks = skill07.validate_input_document(document)
    if not skill07._checks_pass(input_checks):
        return {"status": "invalid_input", "checks": input_checks}
    prompt_started = time.perf_counter()
    prompt = skill07._build_prompt(request)
    prompt_ms = (time.perf_counter() - prompt_started) * 1000
    prompt_chars = len(json.dumps(prompt, ensure_ascii=False)) + len(skill07._system_prompt())
    output = usage = error = None
    resolved_model = model
    attempts: list[dict[str, Any]] = []
    for attempt in range(1, skill07._SKILL07_MAX_ATTEMPTS + 1):
        started = time.perf_counter()
        output, resolved_model, usage, error = skill07._call_poe_code_cli(model, prompt)
        attempts.append({"attempt": attempt, "duration_ms": (time.perf_counter() - started) * 1000, "error": error})
        if error is None:
            break
        if attempt < skill07._SKILL07_MAX_ATTEMPTS:
            time.sleep(skill07._SKILL07_RETRY_DELAY_S * attempt)
    if error is not None:
        return {
            "status": "transport_failure", "model": resolved_model, "usage": usage,
            "prompt_chars": prompt_chars, "prompt_build_ms": prompt_ms, "attempts": attempts,
        }
    normalized, actions = skill07._safe_normalize_skill07_output(output)
    checks = skill07.validate_skill07_output(normalized, document)
    repairs: list[dict[str, Any]] = []
    for repair_number in range(1, skill07._SKILL07_SCHEMA_REPAIR_ATTEMPTS + 1):
        if skill07._checks_pass(checks):
            break
        repair_prompt = skill07._build_repair_prompt(request, normalized, checks)
        started = time.perf_counter()
        repaired, repair_model, repair_usage, repair_error = skill07._call_poe_code_cli(model, repair_prompt)
        repairs.append({
            "repair": repair_number,
            "duration_ms": (time.perf_counter() - started) * 1000,
            "prompt_chars": len(json.dumps(repair_prompt, ensure_ascii=False)) + len(skill07._system_prompt()),
            "error": repair_error,
        })
        if repair_error is not None or not isinstance(repaired, dict):
            break
        resolved_model = repair_model
        if isinstance(usage, dict) and isinstance(repair_usage, dict):
            for key in ("input_tokens", "output_tokens"):
                if usage.get(key) is not None or repair_usage.get(key) is not None:
                    usage[key] = (usage.get(key) or 0) + (repair_usage.get(key) or 0)
        normalized, repair_actions = skill07._safe_normalize_skill07_output(repaired)
        actions.extend(repair_actions)
        checks = skill07.validate_skill07_output(normalized, document)
    return {
        "status": "succeeded" if skill07._checks_pass(checks) else "validation_failed",
        "model": resolved_model,
        "usage": usage,
        "prompt_chars": prompt_chars,
        "prompt_build_ms": prompt_ms,
        "attempts": attempts,
        "repairs": repairs,
        "normalization_actions": actions,
        "checks": checks,
        "output": normalized,
    }


def run_extractions(benchmark: dict[str, Any], output_dir: Path, model: str, workers: int) -> None:
    jobs: list[tuple[dict[str, Any], str, dict[str, Any]]] = []
    for document in benchmark["documents"]:
        task_id = f"canonical-v01-{document['index']:02d}"
        jobs.append((document, "baseline", document["source_document"]))
        jobs.append((document, "canonical", document["canonical_document"]))
    random.Random(20260812).shuffle(jobs)

    def run(job: tuple[dict[str, Any], str, dict[str, Any]]) -> tuple[dict[str, Any], str, dict[str, Any]]:
        document, variant, payload = job
        paper_dir = output_dir / f"{document['index']:02d}_{hashlib.sha256(document['paper_id'].encode('utf-8')).hexdigest()[:12]}"
        result_path = paper_dir / f"skill07_{variant}.json"
        if result_path.is_file():
            previous = json.loads(result_path.read_text(encoding="utf-8"))
            if previous.get("status") != "transport_failure":
                return document, variant, previous
            history = paper_dir / f"skill07_{variant}.transport_failure_{int(time.time())}.json"
            history.write_text(json.dumps(previous, ensure_ascii=False, indent=2), encoding="utf-8")
        result = _extract_once(payload, f"canonical-v01-{document['index']:02d}", model)
        result_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
        return document, variant, result

    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = [pool.submit(run, job) for job in jobs]
        for future in as_completed(futures):
            document, variant, result = future.result()
            document.setdefault("extractions", {})[variant] = result


def _walk_key(value: Any, key: str) -> list[Any]:
    found: list[Any] = []
    if isinstance(value, dict):
        for name, item in value.items():
            if name == key:
                found.append(item)
            found.extend(_walk_key(item, key))
    elif isinstance(value, list):
        for item in value:
            found.extend(_walk_key(item, key))
    return found


def _flatten_strings(values: list[Any]) -> set[str]:
    result: set[str] = set()
    for value in values:
        if isinstance(value, list):
            result.update(str(item) for item in value if item not in (None, ""))
        elif value not in (None, ""):
            result.add(str(value))
    return result


def _jaccard(left: set[str], right: set[str]) -> float:
    return len(left & right) / len(left | right) if left or right else 1.0


def _output_metrics(output: dict[str, Any] | None, document: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(output, dict):
        return {"available": False}
    fields = output.get("fields", {}) if isinstance(output.get("fields"), dict) else {}
    known = sum(isinstance(value, dict) and value.get("status") in {"reported", "inferred"} for value in fields.values())
    experiments = _flatten_strings(_walk_key(output.get("experimental_design_object", {}), "experiment_id"))
    biological_objects = set()
    for key in ("object_id", "strain_id", "construct_id", "paper_label", "normalized_name"):
        biological_objects.update(_flatten_strings(_walk_key(output.get("experimental_design_object", {}), key)))
    anchors = set()
    for key in ("evidence_ids", "source_locations", "classification_evidence", "supporting_candidate_evidence_ids"):
        anchors.update(_flatten_strings(_walk_key(output, key)))
    anchor_sets = skill07._document_anchor_sets(document)
    valid_ids = set().union(*anchor_sets.values())
    resolved = anchors & valid_ids
    ddr = _walk_key(output.get("experimental_design_object", {}), "ddr_annotation")
    reasoning = {}
    for key in (
        "design_action", "trigger_observation", "reason_nature", "reason_nature_rationale",
        "alternatives_considered", "implementation", "result", "generalizable_rule",
    ):
        reasoning[key] = _flatten_strings(_walk_key(ddr, key))
    return {
        "available": True,
        "known_core_fields": known,
        "experiment_ids": sorted(experiments),
        "experiment_count": len(experiments),
        "biological_objects": sorted(biological_objects),
        "biological_object_count": len(biological_objects),
        "evidence_anchors": sorted(anchors),
        "evidence_anchor_count": len(anchors),
        "resolved_evidence_anchor_count": len(resolved),
        "evidence_anchor_resolution": len(resolved) / len(anchors) if anchors else 1.0,
        "reasoning": {key: sorted(value) for key, value in reasoning.items()},
    }


def compare_extractions(benchmark: dict[str, Any]) -> None:
    for document in benchmark["documents"]:
        extractions = document.get("extractions", {})
        baseline = extractions.get("baseline", {})
        canonical = extractions.get("canonical", {})
        baseline_metrics = _output_metrics(baseline.get("output"), document["source_document"])
        canonical_metrics = _output_metrics(canonical.get("output"), document["canonical_document"])
        comparison: dict[str, Any] = {
            "baseline_status": baseline.get("status", "not_run"),
            "canonical_status": canonical.get("status", "not_run"),
            "baseline_metrics": baseline_metrics,
            "canonical_metrics": canonical_metrics,
            "human_scientific_review": "NOT_PERFORMED",
        }
        if baseline_metrics.get("available") and canonical_metrics.get("available"):
            comparison.update({
                "experiment_count_delta": canonical_metrics["experiment_count"] - baseline_metrics["experiment_count"],
                "experiment_id_jaccard": _jaccard(set(baseline_metrics["experiment_ids"]), set(canonical_metrics["experiment_ids"])),
                "biological_object_jaccard": _jaccard(set(baseline_metrics["biological_objects"]), set(canonical_metrics["biological_objects"])),
                "evidence_anchor_jaccard": _jaccard(set(baseline_metrics["evidence_anchors"]), set(canonical_metrics["evidence_anchors"])),
                "known_core_field_delta": canonical_metrics["known_core_fields"] - baseline_metrics["known_core_fields"],
                "reasoning_jaccard": {
                    key: _jaccard(
                        set(baseline_metrics["reasoning"][key]),
                        set(canonical_metrics["reasoning"][key]),
                    )
                    for key in baseline_metrics["reasoning"]
                },
            })
        document["extraction_comparison"] = comparison


def public_result(benchmark: dict[str, Any], extraction_requested: bool) -> dict[str, Any]:
    documents = benchmark["documents"]
    reductions = [item["reduction"]["characters_fraction"] for item in documents]
    all_information_preserved = all(
        all(value is True or value == 1.0 for value in item["information_checks"].values())
        for item in documents
    )
    comparisons = [item.get("extraction_comparison", {}) for item in documents]
    paired_successes = sum(
        item.get("baseline_status") == "succeeded" and item.get("canonical_status") == "succeeded"
        for item in comparisons
    )
    completed_statuses = {"succeeded", "validation_failed"}
    completed_pairs = sum(
        item.get("baseline_status") in completed_statuses and item.get("canonical_status") in completed_statuses
        for item in comparisons
    )
    extraction_complete = extraction_requested and completed_pairs == len(documents)
    recommendation = "NEEDS MORE BENCHMARK"
    reasons = []
    if not all_information_preserved:
        recommendation = "REJECT"
        reasons.append("At least one representation failed exact information preservation.")
    elif not extraction_complete:
        reasons.append("At least ten completed same-model paired extractions are required before quality equivalence can be judged; transport failures are rerun separately.")
    else:
        reasons.append("Structural comparisons are available, but blind human scientific review and repeated runs are still required for a quality non-inferiority claim.")

    clean_documents = []
    for item in documents:
        cleaned = {key: value for key, value in item.items() if key not in {"source_document", "canonical_document", "extractions"}}
        clean_documents.append(cleaned)
    return {
        "benchmark_version": "skill07_canonical_representation_benchmark_v0.1",
        "representation_version": REPRESENTATION_VERSION,
        "quality_constraint": "Quality(Canonical Representation) >= Quality(Current Baseline)",
        "model": skill07.MODEL,
        "production_pipeline_modified": False,
        "documents": clean_documents,
        "original_size": {
            "characters": _summary([item["original_size"]["characters"] for item in documents]),
            "bytes": _summary([item["original_size"]["bytes"] for item in documents]),
        },
        "canonical_size": {
            "characters": _summary([item["canonical_size"]["characters"] for item in documents]),
            "bytes": _summary([item["canonical_size"]["bytes"] for item in documents]),
        },
        "reduction": {
            "characters_fraction": _summary(reductions),
            "estimated_tokens_method": "characters / 4; provider-independent heuristic, not billed-token telemetry",
        },
        "information_checks": {
            "all_documents_exact_roundtrip": all_information_preserved,
            "documents_passed": sum(item["information_checks"]["exact_roundtrip"] for item in documents),
            "documents_total": len(documents),
        },
        "extraction_comparison": {
            "requested": extraction_requested,
            "paired_successes": paired_successes,
            "completed_pairs_including_validation_failures": completed_pairs,
            "pairs_total": len(documents),
            "human_scientific_review": "NOT_PERFORMED",
        },
        "quality_metrics": {
            "automated": [
                "validator status", "experiment count and ID overlap", "biological-object overlap",
                "evidence-anchor resolution and overlap", "known core fields", "reasoning-field overlap",
            ],
            "not_automatable_from_structure_alone": [
                "scientific correctness", "unsupported claims", "wrong attribution", "silent omissions",
                "experiment grouping correctness", "rationale quality", "hallucination",
            ],
        },
        "recommendation": recommendation,
        "recommendation_reasons": reasons,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--count", type=int, default=10)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--run-extraction", action="store_true")
    parser.add_argument("--model", default=skill07.MODEL)
    parser.add_argument("--workers", type=int, default=min(4, skill07._MAX_CONCURRENT_MODEL_CALLS))
    parser.add_argument("--summary-json", type=Path, default=REPO_ROOT / "skill07_canonical_representation_benchmark.json")
    args = parser.parse_args()
    if args.count < 10:
        raise SystemExit("benchmark count must be at least 10")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    benchmark = prepare_representation_benchmark(args.count, args.output_dir)
    if args.run_extraction:
        run_extractions(benchmark, args.output_dir, args.model, max(1, args.workers))
    compare_extractions(benchmark)
    result = public_result(benchmark, args.run_extraction)
    args.summary_json.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({
        "documents": len(result["documents"]),
        "median_character_reduction": result["reduction"]["characters_fraction"]["median"],
        "information_preserved": result["information_checks"]["all_documents_exact_roundtrip"],
        "paired_successes": result["extraction_comparison"]["paired_successes"],
        "recommendation": result["recommendation"],
        "summary_json": str(args.summary_json),
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

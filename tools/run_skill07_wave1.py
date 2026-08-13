"""Generate the staged Skill07 Wave 1 benchmark from reusable artifacts."""
from __future__ import annotations

import csv
import hashlib
import json
import statistics
import sys
from pathlib import Path
from typing import Any

from canonical_document_transformer import REPRESENTATION_VERSION, transform_document
from skill07_wave1 import (
    WAVE_VERSION, cache_identity, cascade_gate, classify_repair_failure,
    compare_scientific_outputs, high_recall_route, map_reduce_plan,
)

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
STORAGE = ROOT / "harness/paper_extraction/vendor/paper_experimental_design_extraction/storage"
PDF_DIR = ROOT.parent / "原始论文(已标顺序)_pdfs_19篇"
STAGE0_DIR = ROOT / "artifacts/skill07_wave1/stage0"
SMOKE_DIR = ROOT / "artifacts/skill07_canonical_representation_v0_1"

import harness.paper_extraction.opus_extractor as runtime  # noqa: E402


def sha_bytes(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_hash(value: Any) -> str:
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def discover_clean_documents() -> list[tuple[Path, dict[str, Any]]]:
    found = {}
    for path in (STORAGE / "pipeline_cache/skill06_markdown_cleaner").glob("*.json"):
        try:
            record = json.loads(path.read_text(encoding="utf-8"))
            clean_path = Path(record["output"]["clean_document_artifact"]["clean_json_path"])
            document = json.loads(clean_path.read_text(encoding="utf-8"))
        except (KeyError, OSError, json.JSONDecodeError):
            continue
        found.setdefault(canonical_hash(document), (clean_path, document))
    return list(found.values())


def match_pdf(paper_id: str, pdfs: list[Path]) -> Path | None:
    normalized = paper_id.casefold().replace("_", "-")
    source_order_hints = {
        "9bdff88f38d746db81b953793f928e4d": "10_",
        "paper:71ab13883b209e2872f3": "4_04_",
        "fa7c24b1f3cf4dc9b6c0bf70790dbe13": "3_02 ",
    }
    for identifier, prefix in source_order_hints.items():
        if identifier in paper_id:
            return next((pdf for pdf in pdfs if pdf.name.startswith(prefix)), None)
    scored = []
    for pdf in pdfs:
        stem = pdf.stem.casefold().replace("_", "-")
        tokens = [token for token in re_split(stem) if len(token) >= 5]
        score = sum(len(token) for token in tokens if token in normalized)
        scored.append((score, pdf))
    best = max(scored, default=(0, None), key=lambda item: item[0])
    return best[1] if best[0] >= 5 else None


def re_split(value: str) -> list[str]:
    for char in " .()[]":
        value = value.replace(char, "-")
    return [part for part in value.split("-") if part]


def baseline_cache_by_input() -> dict[str, Path]:
    result = {}
    for path in (STORAGE / "extraction_cache").glob("*.json"):
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
            input_hash = value.get("provenance", {}).get("input_hash")
        except (OSError, json.JSONDecodeError):
            continue
        if input_hash:
            result[input_hash] = path
    return result


def historical_latency_by_hash() -> dict[str, list[float]]:
    result: dict[str, list[float]] = {}
    for path in (STORAGE / "runtime").glob("*/checkpoint.json"):
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        log = next((row for row in value.get("skill_logs", []) if row.get("skill") == "skill07_experiment_extraction"), None)
        provenance = value.get("context", {}).get("skill07_provenance", [])
        if not log or len(provenance) != 1:
            continue
        input_hash = provenance[0].get("input_hash")
        if input_hash:
            result.setdefault(input_hash, []).append(float(log.get("duration") or 0))
    return result


def freeze_baseline() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    pdfs = sorted(PDF_DIR.glob("*.pdf"))
    docs = discover_clean_documents()
    # The source set is 19 PDFs. Prefer 19 documents matchable to those PDFs.
    candidates = []
    for path, document in docs:
        paper_id = str(document.get("document_metadata", {}).get("paper_id") or canonical_hash(document)[:16])
        candidates.append((match_pdf(paper_id, pdfs), path, document))
    selected = [row for row in candidates if row[0] is not None]
    if len(selected) < 19:
        used = {canonical_hash(row[2]) for row in selected}
        selected.extend((None, path, doc) for path, doc in docs if canonical_hash(doc) not in used)
    selected = selected[:19]
    cache = baseline_cache_by_input()
    latencies = historical_latency_by_hash()
    manifest = []
    stage0 = []
    STAGE0_DIR.mkdir(parents=True, exist_ok=True)
    for index, (pdf, clean_path, document) in enumerate(selected, 1):
        source_hash = sha_bytes(clean_path)
        paper_id = str(document.get("document_metadata", {}).get("paper_id") or source_hash[:16])
        canonical, report = transform_document(document)
        paper_dir = STAGE0_DIR / f"{index:02d}_{hashlib.sha256(paper_id.encode()).hexdigest()[:10]}"
        paper_dir.mkdir(parents=True, exist_ok=True)
        canonical_path = paper_dir / "canonical_document_v0.1.json"
        transform_path = paper_dir / "transformation_report.json"
        canonical_path.write_text(json.dumps(canonical, ensure_ascii=False, indent=2), encoding="utf-8")
        transform_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        routed, route_report = high_recall_route(canonical)
        map_plan = map_reduce_plan(canonical)
        baseline_path = cache.get(source_hash)
        baseline_record = json.loads(baseline_path.read_text(encoding="utf-8")) if baseline_path else {}
        identity = cache_identity(
            paper_id=paper_id, source_document_hash=source_hash,
            representation_version="production_clean_document", prompt_hash=runtime._system_prompt_hash(),
            skill_hash=runtime._skill_hash(), schema_hash=runtime._schema_hash(),
            validator_version=runtime.VALIDATOR_VERSION, model_provider="poe_code_cli",
            model=runtime.MODEL, model_parameters={"provider_revision": "UNKNOWN"}, candidate_id="A_BASELINE",
        )
        manifest.append({
            "paper_id": paper_id,
            "source_pdf": str(pdf) if pdf else None,
            "pdf_hash": sha_bytes(pdf) if pdf else None,
            "clean_document_path": str(clean_path),
            "clean_document_hash": source_hash,
            "clean_document_version": document.get("document_metadata", {}).get("cleaner_version", "UNKNOWN"),
            "prompt_hash": runtime._system_prompt_hash(), "skill_hash": runtime._skill_hash(),
            "schema_hash": runtime._schema_hash(), "validator_version": runtime.VALIDATOR_VERSION,
            "model_provider": "poe_code_cli", "model": runtime.MODEL,
            "model_parameters_if_available": {"immutable_revision": "UNKNOWN", "reasoning_profile": "UNKNOWN"},
            "baseline_output_path": str(baseline_path) if baseline_path else None,
            "baseline_latency_ms_observed": latencies.get(source_hash, []),
            "input_size": {"characters": report["original_characters"], "bytes": report["original_bytes"]},
            "input_tokens_if_available": baseline_record.get("metrics", {}).get("input_tokens"),
            "output_tokens_if_available": baseline_record.get("metrics", {}).get("output_tokens"),
            "review_status": "NO_SKILL07_HUMAN_GOLD",
            "cache_identity": identity,
        })
        stage0.append({
            "paper_id": paper_id, "canonical_path": str(canonical_path),
            "transformation_report_path": str(transform_path), "information_preserved": report["exact_roundtrip"],
            "original_chars": report["original_characters"], "canonical_chars": report["canonical_characters"],
            "input_reduction_fraction": report["character_reduction_fraction"],
            "residual_chars": report["residual_characters"], "fallback_sections": report["fallback_sections"],
            "figures": len(document.get("figures", [])), "tables": len(document.get("tables", [])),
            "citations": len(document.get("citations", [])),
            "supplements": len(document.get("supplements", [])) if isinstance(document.get("supplements"), list) else "NOT_AVAILABLE",
            "routing": route_report, "map_reduce_plan": map_plan,
        })
    return manifest, stage0


def load_smoke_pairs() -> list[dict[str, Any]]:
    pairs = []
    for directory in sorted(SMOKE_DIR.glob("[0-9][0-9]_*")):
        base_path, can_path = directory / "skill07_baseline.json", directory / "skill07_canonical.json"
        if not base_path.is_file() or not can_path.is_file():
            continue
        baseline = json.loads(base_path.read_text(encoding="utf-8"))
        canonical = json.loads(can_path.read_text(encoding="utf-8"))
        if baseline.get("status") == "transport_failure" or canonical.get("status") == "transport_failure":
            continue
        comparison = compare_scientific_outputs(baseline.get("output") or {}, canonical.get("output") or {})
        pairs.append({
            "paper_directory": directory.name,
            "baseline_status": baseline.get("status"), "canonical_status": canonical.get("status"),
            "baseline_latency_ms": sum(item.get("duration_ms", 0) for item in baseline.get("attempts", [])) + sum(item.get("duration_ms", 0) for item in baseline.get("repairs", [])),
            "canonical_latency_ms": sum(item.get("duration_ms", 0) for item in canonical.get("attempts", [])) + sum(item.get("duration_ms", 0) for item in canonical.get("repairs", [])),
            "baseline_input_tokens": baseline.get("usage", {}).get("input_tokens"),
            "canonical_input_tokens": canonical.get("usage", {}).get("input_tokens"),
            "baseline_output_tokens": baseline.get("usage", {}).get("output_tokens"),
            "canonical_output_tokens": canonical.get("usage", {}).get("output_tokens"),
            "baseline_repairs": len(baseline.get("repairs", [])), "canonical_repairs": len(canonical.get("repairs", [])),
            "comparison": comparison,
            "repair_classes": [classify_repair_failure(check) for check in canonical.get("checks", []) if not check.get("passed", True)],
        })
    return pairs


def metric_median(rows: list[dict[str, Any]], key: str) -> float | None:
    values = [float(row[key]) for row in rows if row.get(key) is not None]
    return statistics.median(values) if values else None


def decision_matrix(stage0: list[dict[str, Any]], smoke: list[dict[str, Any]]) -> list[dict[str, Any]]:
    reduction = statistics.median(item["input_reduction_fraction"] for item in stage0)
    baseline_latency, canonical_latency = metric_median(smoke, "baseline_latency_ms"), metric_median(smoke, "canonical_latency_ms")
    canonical_regressions = sum(bool(item["comparison"]["hard_quality_flags"]) for item in smoke)
    pairs = len(smoke)
    b_quality = "PASS_REPRESENTATION; INSUFFICIENT_EXTRACTION_EVIDENCE" if all(x["information_preserved"] for x in stage0) else "FAIL"
    b_decision = "HOLD_FOR_MORE_BENCHMARK" if all(x["information_preserved"] for x in stage0) else "REJECT"
    return [
        {"candidate":"A_BASELINE","quality_gate":"BASELINE","input_reduction":0,"median_latency_ms":baseline_latency,"throughput_papers_per_hour":3600000/baseline_latency if baseline_latency else None,"risk":"baseline instability/repair observed","decision":"BASELINE"},
        {"candidate":"B_CANONICAL","quality_gate":b_quality,"input_reduction":reduction,"median_latency_ms":canonical_latency,"throughput_papers_per_hour":3600000/canonical_latency if canonical_latency else None,"risk":f"only {pairs} completed smoke pairs; {canonical_regressions} structural hard flags","decision":b_decision},
        {"candidate":"C_CANONICAL_REPAIR","quality_gate":"FRAMEWORK_TESTED; TARGETED_LLM_NOT_RUN","input_reduction":reduction,"median_latency_ms":None,"throughput_papers_per_hour":None,"risk":"targeted repair scientific equivalence unvalidated","decision":"HOLD_FOR_MORE_BENCHMARK"},
        {"candidate":"D_HIGH_RECALL_ROUTING","quality_gate":"COVERAGE GOLD UNAVAILABLE","input_reduction":None,"median_latency_ms":None,"throughput_papers_per_hour":None,"risk":"critical evidence recall UNKNOWN; not Methods-only","decision":"HOLD_FOR_MORE_BENCHMARK"},
        {"candidate":"E_MAP_REDUCE","quality_gate":"FRAMEWORK_ONLY","input_reduction":None,"median_latency_ms":None,"throughput_papers_per_hour":None,"risk":"fragmentation/causal-link risk","decision":"NOT_RUN"},
        {"candidate":"F_MODEL_CASCADE","quality_gate":"NO VALIDATED FAST MODEL OR CONFIDENCE GATE","input_reduction":reduction,"median_latency_ms":None,"throughput_papers_per_hour":None,"risk":"false accept cannot be bounded","decision":"FRAMEWORK_READY_BUT_NOT_VALIDATED"},
        {"candidate":"G_SAFE_COMBINED","quality_gate":"LOCAL COMPONENT TESTS PASS; EXTRACTION NON-INFERIORITY INSUFFICIENT","input_reduction":reduction,"median_latency_ms":None,"throughput_papers_per_hour":None,"risk":"canonical extraction needs controlled 10-paper completion","decision":"HOLD_FOR_MORE_BENCHMARK"},
    ]


def write_csv(matrix: list[dict[str, Any]]) -> None:
    with (ROOT / "skill07_candidate_matrix.csv").open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(matrix[0]))
        writer.writeheader(); writer.writerows(matrix)


def write_review_queue(smoke: list[dict[str, Any]]) -> None:
    lines = ["# Skill07 Wave 1 Human Review Queue", "", "仅列自动结构比较发现的高价值差异；这些差异不等于科学错误。", ""]
    if not smoke:
        lines += ["当前没有完整的 baseline/candidate smoke pair。", ""]
    for row in smoke:
        changes = row["comparison"]["structural_changes"]
        important = {key: value for key, value in changes.items() if value["missing"] or value["added"]}
        lines += [f"## {row['paper_directory']}", "", f"- Baseline: `{row['baseline_status']}`; Canonical: `{row['canonical_status']}`"]
        for key, value in important.items():
            lines.append(f"- `{key}`：baseline-only {value['missing'][:5]}；candidate-only {value['added'][:5]}")
        lines += ["- 人审重点：实验分组、来源归属、evidence locator、trigger→action 时序、rule scope。", ""]
    (ROOT / "HUMAN_REVIEW_QUEUE.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    manifest, stage0 = freeze_baseline()
    (ROOT / "skill07_baseline_manifest.json").write_text(json.dumps({"version":WAVE_VERSION,"frozen":True,"documents":manifest},ensure_ascii=False,indent=2),encoding="utf-8")
    smoke = load_smoke_pairs()
    matrix = decision_matrix(stage0, smoke)
    write_csv(matrix); write_review_queue(smoke)
    result = {
        "version": WAVE_VERSION, "production_behavior_changed": False,
        "baseline_manifest_path": str(ROOT / "skill07_baseline_manifest.json"),
        "stages": {
            "stage0_representation": {"documents":len(stage0),"results":stage0},
            "stage1_smoke": {"completed_pairs":len(smoke),"results":smoke,"interrupted_full_run_reused":True},
            "stage2_controlled": {"status":"NOT_RUN_UNTIL_SMOKE_AND_HUMAN_GATE"},
            "stage3_extended": {"status":"NOT_RUN"},
        },
        "candidates": matrix,
        "cascade_framework_gate_example": cascade_gate({"status":"succeeded"}).__dict__,
        "telemetry": {"provider_queue":"NOT_OBSERVABLE","provider_request_start":"NOT_OBSERVABLE","time_to_first_output":"NOT_OBSERVABLE_WITH_CAPTURED_SUBPROCESS","subprocess_total_and_exit":"OBSERVABLE_IN_HARNESS","secrets_logged":False},
        "concurrency": {"implemented":"bounded ThreadPoolExecutor in shadow benchmark","tested_concurrency":[4],"concurrency_1_2_4_comparison":"NOT_MEASURED_TO_AVOID_EXTRA_LLM_COST","failure_isolation":True,"resume":True},
        "human_review": {"skill07_gold_available":False,"skill08_gold_detected":True,"queue":"HUMAN_REVIEW_QUEUE.md"},
        "supplement_quality_gap":"No independent Supplement artifacts in measured clean documents; future integration point preserved and no candidate may claim real Supplement coverage.",
    }
    (ROOT / "skill07_optimization_wave1_results.json").write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps({"baseline_documents":len(manifest),"stage0_documents":len(stage0),"smoke_pairs":len(smoke),"matrix":matrix},ensure_ascii=False,indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Reusable, shadow-only validity utilities for Skill07 Wave 2."""
from __future__ import annotations

import hashlib
import json
import re
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict, dataclass
from typing import Any, Callable

DIFFERENCE_CLASSES = (
    "FORMAT_ONLY", "SEMANTICALLY_EQUIVALENT", "POTENTIALLY_MEANINGFUL",
    "CRITICAL_SCIENTIFIC_DIFFERENCE", "AMBIGUOUS_REQUIRES_HUMAN",
)
TELEMETRY_FIELDS = (
    "prompt_build_ms", "provider_or_cli_total_ms", "first_pass_ms", "validation_ms",
    "local_repair_ms", "targeted_repair_ms", "full_llm_repair_ms", "total_wall_ms",
    "first_pass_validation_status", "repair_class", "repair_attempts", "full_repair_used",
    "final_status", "input_chars", "input_tokens", "output_tokens",
)


def sha256_json(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


@dataclass(frozen=True)
class InvocationIdentity:
    provider: str
    source_default_model: str
    configured_model: str
    resolved_runtime_model: str
    invocation_model_argument: str
    provider_resolved_model: str
    model_revision: str
    cli_tool: str
    prompt_hash: str
    skill_hash: str
    schema_hash: str
    validator_hash: str
    representation_version: str
    candidate_id: str
    source_document_hash: str
    run_id: str
    timestamp: str
    alias: str
    model_parameters: dict[str, Any]

    def public_dict(self) -> dict[str, Any]:
        data = asdict(self)
        # Fail closed against accidental future additions of credential fields.
        forbidden = re.compile(r"(?i)(api.?key|authorization|credential|secret|token)")
        return {k: v for k, v in data.items() if not forbidden.search(k) or k in {"model_parameters"}}


def provenance_gate(identity: InvocationIdentity, manifest: dict[str, Any], cache_identity: dict[str, Any]) -> dict[str, Any]:
    expected = {
        "provider": identity.provider,
        "model": identity.invocation_model_argument,
        "candidate_id": identity.candidate_id,
        "representation_version": identity.representation_version,
        "source_document_hash": identity.source_document_hash,
        "prompt_hash": identity.prompt_hash,
        "skill_hash": identity.skill_hash,
        "schema_hash": identity.schema_hash,
        "validator_hash": identity.validator_hash,
    }
    mismatches = []
    for key, value in expected.items():
        if manifest.get(key) != value:
            mismatches.append({"surface": "manifest", "field": key, "expected": value, "actual": manifest.get(key, "MISSING")})
        if cache_identity.get(key) != value:
            mismatches.append({"surface": "cache_identity", "field": key, "expected": value, "actual": cache_identity.get(key, "MISSING")})
    runtime_ok = identity.configured_model == identity.resolved_runtime_model == identity.invocation_model_argument
    if not runtime_ok:
        mismatches.append({"surface": "runtime", "field": "model", "expected": identity.configured_model, "actual": identity.resolved_runtime_model})
    return {
        "status": "PASS" if not mismatches else "BENCHMARK_BLOCKED_PROVENANCE_MISMATCH",
        "mismatches": mismatches,
        "provider_resolved_model_observability": "UNKNOWN" if identity.provider_resolved_model == "UNKNOWN" else "OBSERVED",
    }


def normalize_comparison_id(value: Any) -> str:
    text = re.sub(r"[\s_-]+", "", str(value or "")).upper()
    match = re.fullmatch(r"([A-Z]+)0*([0-9]+)", text)
    return f"{match.group(1)}{int(match.group(2))}" if match else text


def normalize_text(value: Any) -> str:
    text = str(value or "").casefold().replace("escherichia coli", "e coli")
    return " ".join(re.findall(r"[a-z0-9]+", text))


def _values(item: dict[str, Any], *keys: str) -> list[str]:
    out: list[str] = []
    for key in keys:
        value = item.get(key)
        if isinstance(value, list): out.extend(normalize_text(v) for v in value)
        elif isinstance(value, dict): out.append(normalize_text(json.dumps(value, sort_keys=True)))
        elif value not in (None, ""): out.append(normalize_text(value))
    return [v for v in out if v]


def experiment_signature(item: dict[str, Any]) -> dict[str, tuple[str, ...]]:
    return {
        "object": tuple(sorted(_values(item, "objects", "biological_object", "strain", "construct", "host"))),
        "intervention": tuple(sorted(_values(item, "intervention", "design_action", "target_gene", "pathway"))),
        "condition": tuple(sorted(_values(item, "conditions", "condition"))),
        "readout": tuple(sorted(_values(item, "readouts", "assay"))),
        "result": tuple(sorted(_values(item, "outcomes", "result"))),
        "evidence": tuple(sorted(_values(item, "evidence_paragraphs", "evidence_ids", "source_locations"))),
    }


def _similarity(a: dict[str, tuple[str, ...]], b: dict[str, tuple[str, ...]]) -> float:
    scores = []
    for key in a:
        left, right = set(a[key]), set(b[key])
        if left or right: scores.append(len(left & right) / len(left | right))
    return sum(scores) / len(scores) if scores else 1.0


def _experiments(output: dict[str, Any]) -> list[dict[str, Any]]:
    edo = output.get("experimental_design_object", output)
    values = edo.get("experiments", []) if isinstance(edo, dict) else []
    return [v for v in values if isinstance(v, dict)]


def align_experiments(left_output: dict[str, Any], right_output: dict[str, Any]) -> dict[str, Any]:
    left, right = _experiments(left_output), _experiments(right_output)
    unused = set(range(len(right))); matches=[]; unresolved=[]
    for li, litem in enumerate(left):
        lid = normalize_comparison_id(litem.get("experiment_id"))
        exact = [ri for ri in unused if normalize_comparison_id(right[ri].get("experiment_id")) == lid and lid]
        if len(exact) == 1:
            ri=exact[0]; matches.append((li,ri,"NORMALIZED_ID")); unused.remove(ri); continue
        scored=sorted(((_similarity(experiment_signature(litem),experiment_signature(right[ri])),ri) for ri in unused), reverse=True)
        if scored and scored[0][0] >= .5 and (len(scored)==1 or scored[0][0]-scored[1][0] >= .15):
            ri=scored[0][1]; matches.append((li,ri,"SCIENTIFIC_SIGNATURE")); unused.remove(ri)
        elif scored and scored[0][0] >= .5:
            unresolved.append({"left_index":li,"reason":"AMBIGUOUS_ALIGNMENT_REQUIRES_HUMAN","candidate_indices":[ri for score,ri in scored if scored[0][0]-score < .15]})
        else: unresolved.append({"left_index":li,"reason":"UNMATCHED_LEFT"})
    return {"matches":matches,"unresolved":unresolved,"unmatched_right":sorted(unused)}


def compare_aligned_outputs(left_output: dict[str, Any], right_output: dict[str, Any]) -> dict[str, Any]:
    alignment=align_experiments(left_output,right_output); left=_experiments(left_output); right=_experiments(right_output); differences=[]
    critical={"object","intervention","result","evidence"}
    for li,ri,method in alignment["matches"]:
        ls,rs=experiment_signature(left[li]),experiment_signature(right[ri]); changed=[k for k in ls if ls[k]!=rs[k]]
        originals=(left[li].get("experiment_id"),right[ri].get("experiment_id"))
        if not changed:
            cls="FORMAT_ONLY" if originals[0]!=originals[1] else "SEMANTICALLY_EQUIVALENT"
        elif critical.intersection(changed): cls="CRITICAL_SCIENTIFIC_DIFFERENCE"
        else: cls="POTENTIALLY_MEANINGFUL"
        differences.append({"left_id":originals[0],"right_id":originals[1],"alignment_method":method,"class":cls,"changed_dimensions":changed})
    for item in alignment["unresolved"]: differences.append({**item,"class":"AMBIGUOUS_REQUIRES_HUMAN"})
    for ri in alignment["unmatched_right"]: differences.append({"right_id":right[ri].get("experiment_id"),"class":"CRITICAL_SCIENTIFIC_DIFFERENCE","changed_dimensions":["experiment_added_or_omitted"]})
    counts={name:sum(d["class"]==name for d in differences) for name in DIFFERENCE_CLASSES}
    return {"alignment":alignment,"differences":differences,"counts":counts,"automated_scientific_truth":False}


def blank_telemetry(**known: Any) -> dict[str, Any]:
    return {field: known.get(field, "UNKNOWN") for field in TELEMETRY_FIELDS}


def run_bounded(jobs: list[Any], worker: Callable[[Any], Any], concurrency: int, retry_limit: int = 0) -> list[dict[str, Any]]:
    semaphore=threading.BoundedSemaphore(concurrency)
    def one(index: int, job: Any) -> dict[str, Any]:
        attempts=0
        while True:
            attempts+=1
            try:
                with semaphore: value=worker(job)
                return {"index":index,"status":"succeeded","attempts":attempts,"value":value}
            except Exception as exc:
                if attempts>retry_limit: return {"index":index,"status":"failed","attempts":attempts,"error_type":type(exc).__name__}
                time.sleep(min(.01*attempts,.05))
    with ThreadPoolExecutor(max_workers=concurrency) as pool:
        futures=[pool.submit(one,i,j) for i,j in enumerate(jobs)]
        return sorted((f.result() for f in as_completed(futures)),key=lambda x:x["index"])

"""Model Benchmark Memory (doc06 §3.13/§9.5): frozen, stratified evidence
of a model's ACTUAL past performance on a specific (endpoint, strain,
condition, perturbation_class) slice - never a single aggregate score, and
never silently overwritten. Metrics are computed here by code from real
`PredictionResidual` rows, never asserted by an LLM.
"""
from __future__ import annotations

from harness.ids import new_id, now
from harness.memory import event_types as et
from harness.memory.event_store import append_event
from harness.virtual_cell.models import BENCHMARK_SPLIT_TYPES, ModelBenchmarkRecord, PredictionResidual


def _compute_metrics(residuals: list[PredictionResidual]) -> dict[str, float | None]:
    n = len(residuals)
    if n == 0:
        return {"mae": None, "rmse": None, "bias": None, "rank_correlation": None, "interval_coverage": None}
    errors = [r.residual for r in residuals]
    mae = sum(abs(e) for e in errors) / n
    rmse = (sum(e * e for e in errors) / n) ** 0.5
    bias = sum(errors) / n
    return {"mae": mae, "rmse": rmse, "bias": bias, "rank_correlation": None, "interval_coverage": None}


def evaluate_benchmark(
    session, *, model_id: str, endpoint: str, split_type: str, residual_ids: list[str], benchmark_dataset_id: str,
    benchmark_dataset_version: str, evaluation_protocol_id: str, organism: str, strain: str, condition: dict,
    perturbation_class: str, model_version: str = "e_coli_core", artifact_hash: str | None = None, adapter_version: str = "",
    supersedes_record_id: str | None = None,
) -> ModelBenchmarkRecord:
    if split_type not in BENCHMARK_SPLIT_TYPES:
        raise ValueError(f"unknown split_type {split_type!r}; must be one of {BENCHMARK_SPLIT_TYPES}")
    if not residual_ids:
        raise ValueError("a benchmark evaluation must cite at least one residual")

    residuals = [session.get(PredictionResidual, rid) for rid in residual_ids]
    included: list[PredictionResidual] = []
    excluded: list[str] = []
    for rid, r in zip(residual_ids, residuals):
        if r is None:
            excluded.append(rid)
            continue
        if r.endpoint != endpoint:
            # doc06 §3.13: never silently aggregate across endpoints.
            raise ValueError(f"residual {rid} is for endpoint {r.endpoint!r}, not {endpoint!r} - refuses cross-endpoint aggregation")
        if not r.context_match:
            excluded.append(rid)
            continue
        included.append(r)

    metrics = _compute_metrics(included)
    record = ModelBenchmarkRecord(
        benchmark_record_id=new_id("MBENCH"), model_id=model_id, model_version=model_version, artifact_hash=artifact_hash,
        adapter_version=adapter_version, benchmark_dataset_id=benchmark_dataset_id, benchmark_dataset_version=benchmark_dataset_version,
        evaluation_protocol_id=evaluation_protocol_id, organism=organism, strain=strain, condition=condition,
        perturbation_class=perturbation_class, endpoint=endpoint, unit=included[0].unit if included else "",
        split_type=split_type, sample_count=len(included), included_residual_ids=[r.residual_id for r in included],
        excluded_residual_ids=excluded, metrics=metrics, applicability_scope={"organism": organism, "strain": strain, "condition": condition},
        known_failure_modes=[], provenance={"computed_from": "harness.virtual_cell.models.PredictionResidual", "code_computed": True},
        created_at=now(), status="provisional", supersedes_record_id=supersedes_record_id,
    )
    session.add(record)
    session.flush()

    project_id = None
    if included:
        from harness.virtual_cell.models import SimulationCase

        case = session.get(SimulationCase, included[0].simulation_case_id)
        project_id = case.project_id if case else None
    if project_id:
        append_event(
            session, project_id=project_id, event_type=et.VC_BENCHMARK_RECORDED, entity_type="ModelBenchmarkRecord",
            entity_id=record.benchmark_record_id, payload={"model_id": model_id, "endpoint": endpoint, "split_type": split_type, "sample_count": record.sample_count, "metrics": metrics},
            actor_type="agent", actor_id="system",
        )
    return record

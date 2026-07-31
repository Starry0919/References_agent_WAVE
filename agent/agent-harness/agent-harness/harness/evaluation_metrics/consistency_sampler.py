"""260718 设计文档 §7/§6 一致性 (Phase6 "并行-voting"): draws N independent
samples of the same design task and reports which interventions recur across
runs.

`harness.engineering_design.strategy_generator.generate_strategies` (the
rule-based generator most of the pipeline runs on) is deterministic - re-
running it against identical inputs always returns identical output, so
sampling it N times would trivially "converge" 100% and would not answer the
doc's question ("看哪些稳健收敛" implies genuine run-to-run variation). The
actual stochastic component in this codebase is the LLM Strategy Draft
adapter (`harness.engineering_design.llm_strategy_adapter`), which makes a
real model call per sample - this module draws N samples from THAT via its
non-persisting core (`draft_strategies_via_llm`), so nothing here writes into
the project's real `EngineeringStrategy`/`CandidateDesign` rows; only the one
`ConsistencySamplingRun` record is persisted.

Convergence is reported by `strategy_class` (9-value doc04 taxonomy), not by
exact-text match on `mechanism_target` - an LLM will rarely phrase the same
underlying idea identically twice, so text-equality would understate
convergence that is real at the mechanism-category level.
"""
from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from harness.engineering_design.llm_strategy_adapter import draft_strategies_via_llm
from harness.engineering_design.models import DiagnosisHandoffRecord, EngineeringDesignProject
from harness.evaluation_metrics.models import ConsistencySamplingRun
from harness.ids import new_id, now
from harness.learning.models import HypothesisVersion
from harness.llm_generation.client import StructuredGenerationClient

DEFAULT_N_SAMPLES = 5
MAX_N_SAMPLES = 10


class NoHandoffForProjectError(ValueError):
    pass


def _latest_handoff(session: Session, design_project_id: str) -> DiagnosisHandoffRecord:
    handoff = session.execute(
        select(DiagnosisHandoffRecord)
        .where(DiagnosisHandoffRecord.design_project_id == design_project_id)
        .order_by(DiagnosisHandoffRecord.created_at.desc())
    ).scalars().first()
    if handoff is None:
        raise NoHandoffForProjectError(
            f"design project {design_project_id} has no diagnosis handoff record yet - "
            "consistency sampling needs the same inputs strategy generation uses"
        )
    return handoff


def _objective_summary(primary_metrics: list[dict[str, Any]]) -> str:
    if not primary_metrics:
        return "improve the project's target metric(s)"
    names = [str(m.get("metric", m.get("name", "unknown"))) for m in primary_metrics]
    return f"improve {', '.join(names)}"


def _compute_convergence(samples: list[dict[str, Any]], n_samples: int) -> dict[str, Any]:
    samples_with_output = sum(1 for s in samples if s["strategies"])
    class_counts: dict[str, int] = {}
    for s in samples:
        for cls in {st["strategy_class"] for st in s["strategies"]}:
            class_counts[cls] = class_counts.get(cls, 0) + 1

    by_class = sorted(
        (
            {"strategy_class": cls, "sample_count": count, "convergence": count / n_samples}
            for cls, count in class_counts.items()
        ),
        key=lambda r: r["convergence"],
        reverse=True,
    )
    return {
        "samples_with_output": samples_with_output,
        "samples_with_output_rate": samples_with_output / n_samples if n_samples else 0.0,
        "by_strategy_class": by_class,
        "note": "convergence is grouped by strategy_class, not exact mechanism_target text - see module docstring",
    }


def run_consistency_sample(
    session: Session, *, design_project_id: str, n_samples: int, actor_id: str,
    client: StructuredGenerationClient | None = None,
) -> ConsistencySamplingRun:
    proj = session.get(EngineeringDesignProject, design_project_id)
    if proj is None:
        raise ValueError(f"no such design project: {design_project_id}")
    n_samples = max(1, min(n_samples, MAX_N_SAMPLES))

    handoff = _latest_handoff(session, design_project_id)
    hyp_ids = handoff.supported_hypotheses
    hyps = (
        session.execute(select(HypothesisVersion).where(HypothesisVersion.hypothesis_version_id.in_(hyp_ids))).scalars().all()
        if hyp_ids else []
    )
    supported_hypotheses = [
        {"hypothesis_version_id": h.hypothesis_version_id, "statement": h.statement, "mechanism_class": h.mechanism_class}
        for h in hyps
    ]
    objective = _objective_summary(proj.primary_metrics)

    client = client or StructuredGenerationClient()
    samples: list[dict[str, Any]] = []
    for i in range(n_samples):
        generated, fallback_used, _attempts, _health, _raw = draft_strategies_via_llm(
            client, objective=objective, supported_hypotheses=supported_hypotheses, primary_metrics=proj.primary_metrics,
        )
        samples.append({
            "sample_index": i,
            "fallback_used": fallback_used,
            "strategies": [{"strategy_class": g.strategy_class, "mechanism_target": g.mechanism_target} for g in generated],
        })

    run = ConsistencySamplingRun(
        run_id=new_id("CONSIST"), design_project_id=design_project_id, n_samples=n_samples, samples=samples,
        convergence_report=_compute_convergence(samples, n_samples), created_by=actor_id, created_at=now(),
    )
    session.add(run)
    session.flush()
    return run


def list_consistency_runs(session: Session, design_project_id: str) -> list[ConsistencySamplingRun]:
    return list(
        session.execute(
            select(ConsistencySamplingRun)
            .where(ConsistencySamplingRun.design_project_id == design_project_id)
            .order_by(ConsistencySamplingRun.created_at.desc())
        ).scalars()
    )

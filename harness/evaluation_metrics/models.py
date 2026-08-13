"""260718 设计文档 §7 (验证方式) evaluation-metrics tables.

`compute_*` functions in `aggregator.py` derive 接地率/覆盖完备/筛选能力/
合理新颖/复现率 on demand from existing `engineering_design` rows - nothing
new is persisted for those. The one new table here, `ConsistencySamplingRun`,
exists because 一致性 (N-run convergence) has no existing counterpart: it is
a real, otherwise-unrecorded artifact (N live LLM draft calls against the
same design task) that later audits need to be able to re-read, not just a
derived rollup.
"""
from __future__ import annotations

from sqlalchemy import JSON, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from harness.db import Base, guard_immutable_fields


class ConsistencySamplingRun(Base):
    """One N-sample consistency-sampling run for a design project (doc §7
    一致性; doc §6 Phase6's "同一设计任务跑 N 次,对干预聚类,看哪些稳健收敛").
    Append-only: a re-run is a new row, never an overwrite, so the history of
    convergence over a project's lifetime stays inspectable."""

    __tablename__ = "consistency_sampling_runs"

    run_id: Mapped[str] = mapped_column(String, primary_key=True)
    design_project_id: Mapped[str] = mapped_column(ForeignKey("design_projects.design_project_id"), index=True)
    n_samples: Mapped[int] = mapped_column(Integer)
    # [{sample_index, fallback_used, strategies: [{strategy_class, mechanism_target}]}, ...]
    samples: Mapped[list] = mapped_column(JSON, default=list)
    # {by_strategy_class: [{strategy_class, sample_count, convergence}], samples_with_output, note}
    convergence_report: Mapped[dict] = mapped_column(JSON, default=dict)
    created_by: Mapped[str] = mapped_column(String)
    created_at: Mapped[float] = mapped_column(Float)


guard_immutable_fields(ConsistencySamplingRun, mutable_fields=set())

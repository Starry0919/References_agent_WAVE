"""Versioned contracts for scientific destruction/regression benchmarks."""
from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, model_validator


class BenchmarkAxis(str, Enum):
    DOCUMENT_ROUTING = "document_routing"
    QUANTITATIVE_SEMANTICS = "quantitative_semantics"
    EVIDENCE_DELETION = "evidence_deletion"
    COUNTERFACTUAL_CONTEXT = "counterfactual_context"
    CONTRADICTION_HANDLING = "contradiction_handling"
    FAILURE_LEARNING = "failure_learning"
    MODEL_CONSISTENCY = "candidate_model_consistency"
    TEMPORAL_HOLDOUT = "temporal_holdout"


class ScientificBenchmarkCase(BaseModel):
    schema_version: str = "scientific-benchmark-case/2.0"
    case_id: str
    axis: BenchmarkAxis
    input_artifact_refs: list[str]
    perturbation: dict[str, Any] = Field(default_factory=dict)
    expected_invariants: list[str]
    gold_status: str = "not_human_gold"
    development_cutoff_year: int | None = None
    publication_year: int | None = None

    @model_validator(mode="after")
    def validate_temporal_split(self):
        if self.axis == BenchmarkAxis.TEMPORAL_HOLDOUT:
            if self.development_cutoff_year is None or self.publication_year is None:
                raise ValueError("temporal holdout requires cutoff and publication year")
            if self.publication_year <= self.development_cutoff_year:
                raise ValueError("holdout publication must be later than development cutoff")
        return self


class ScientificBenchmarkResult(BaseModel):
    schema_version: str = "scientific-benchmark-result/2.0"
    case_id: str
    passed: bool
    critical_false_support: int = 0
    claim_coverage: float | None = None
    attribution_precision: float | None = None
    attribution_recall: float | None = None
    calibration_error: float | None = None
    selection_regret: float | None = None
    validation_discriminability: float | None = None
    evidence_cost: float | None = None
    evidence_need_efficiency: float | None = None
    evidence_refs: list[str] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)

"""Plugin interface for experiment-data adapters (doc 11.3). Each ingestor
declares what it can parse, validates before touching the database, runs
QC independently of "can we map this to a project," and only then produces
Observation-shaped dicts - raw file content is never replaced by an LLM's
interpretation of it (doc 8.5).
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class AssetMetadata:
    file_uri: str
    media_type: str
    assay_type: str
    checksum: str


@dataclass
class ValidationReport:
    valid: bool
    errors: list[str] = field(default_factory=list)


@dataclass
class ParsedRow:
    sample_id: str
    metric: str
    value: float
    unit: str
    timepoint: dict[str, Any] | None = None
    replicate_summary: dict[str, Any] | None = None
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass
class ParsedDataset:
    rows: list[ParsedRow]
    parser_name: str
    parser_version: str


@dataclass
class QCFlag:
    sample_id: str
    code: str
    message: str
    severity: str = "warning"  # warning|error


@dataclass
class QCReport:
    passed: bool
    flags: list[QCFlag] = field(default_factory=list)
    excluded_sample_ids: set[str] = field(default_factory=set)


@dataclass
class SampleBinding:
    """One sample-manifest entry. The Data Identity Gate (doc 10.2)
    requires every parsed row's `sample_id` to resolve to one of these
    before any biological interpretation is allowed - an unmapped sample
    blocks ingestion rather than silently proceeding without one."""

    sample_id: str
    design_version_id: str | None = None
    construct_id: str | None = None
    condition_ref: dict[str, Any] = field(default_factory=dict)
    replicate_group: str | None = None


class DataIngestor(ABC):
    name: str
    version: str

    @abstractmethod
    def can_handle(self, asset_metadata: AssetMetadata) -> bool: ...

    @abstractmethod
    def validate(self, raw_text: str) -> ValidationReport: ...

    @abstractmethod
    def parse(self, raw_text: str, sample_manifest: dict[str, SampleBinding]) -> ParsedDataset: ...

    @abstractmethod
    def qc(self, parsed: ParsedDataset) -> QCReport: ...

    def to_observation_dicts(
        self,
        parsed: ParsedDataset,
        qc_report: QCReport,
        sample_manifest: dict[str, SampleBinding],
    ) -> list[dict[str, Any]]:
        """Default: one Observation dict per non-excluded row, condition/
        design bound via `sample_manifest`. Subclasses may override for
        assay-specific aggregation."""
        observations = []
        for row in parsed.rows:
            if row.sample_id in qc_report.excluded_sample_ids:
                continue
            binding = sample_manifest.get(row.sample_id)
            observations.append(
                {
                    "subject_design_version_id": binding.design_version_id if binding else None,
                    "subject_construct_id": binding.construct_id if binding else None,
                    "condition_ref": binding.condition_ref if binding else {},
                    "timepoint": row.timepoint,
                    "metric": row.metric,
                    "value": row.value,
                    "unit": row.unit,
                    "replicate_summary": row.replicate_summary,
                    "qc_flags": [f.code for f in qc_report.flags if f.sample_id == row.sample_id],
                    "qc_status": "passed" if qc_report.passed else "failed",
                    "analysis_pipeline_version": f"{self.name}:{self.version}",
                    "source_type": "instrument",
                }
            )
        return observations

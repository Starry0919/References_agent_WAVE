"""Growth-curve / target-metabolite-titer CSV ingestor (doc 11.1's first
two candidate adapters, combined - both are "one row per sample, one
numeric metric" CSVs). Expected columns: `sample_id, metric, value, unit`,
optionally `timepoint_value, timepoint_unit, phase, replicate_n,
replicate_mean, replicate_sd`.
"""
from __future__ import annotations

import csv
import io

from harness.experiments.ingestion.data_ingestor import (
    AssetMetadata,
    DataIngestor,
    ParsedDataset,
    ParsedRow,
    QCFlag,
    QCReport,
    SampleBinding,
    ValidationReport,
)

REQUIRED_COLUMNS = ("sample_id", "metric", "value", "unit")


class GrowthTiterCsvIngestor(DataIngestor):
    name = "growth_titer_csv"
    version = "1"

    def can_handle(self, asset_metadata: AssetMetadata) -> bool:
        return asset_metadata.assay_type in ("growth_curve", "titer", "growth_titer") and asset_metadata.media_type in (
            "text/csv",
            "application/csv",
        )

    def validate(self, raw_text: str) -> ValidationReport:
        errors: list[str] = []
        reader = csv.DictReader(io.StringIO(raw_text))
        if reader.fieldnames is None:
            return ValidationReport(valid=False, errors=["empty file or no header row"])
        missing = [c for c in REQUIRED_COLUMNS if c not in reader.fieldnames]
        if missing:
            errors.append(f"missing required columns: {missing}")
        row_count = 0
        for i, row in enumerate(reader, start=2):
            row_count += 1
            if not (row.get("sample_id") or "").strip():
                errors.append(f"row {i}: empty sample_id")
            try:
                float(row.get("value", ""))
            except ValueError:
                errors.append(f"row {i}: value {row.get('value')!r} is not numeric")
        if row_count == 0:
            errors.append("no data rows")
        return ValidationReport(valid=not errors, errors=errors)

    def parse(self, raw_text: str, sample_manifest: dict[str, SampleBinding]) -> ParsedDataset:
        rows = []
        reader = csv.DictReader(io.StringIO(raw_text))
        for row in reader:
            timepoint = None
            if row.get("timepoint_value"):
                timepoint = {
                    "value": float(row["timepoint_value"]),
                    "unit": row.get("timepoint_unit", "h"),
                    "phase": row.get("phase", ""),
                }
            replicate_summary = None
            if row.get("replicate_n"):
                replicate_summary = {
                    "n": int(row["replicate_n"]),
                    "mean": float(row.get("replicate_mean") or row["value"]),
                    "sd": float(row["replicate_sd"]) if row.get("replicate_sd") else None,
                }
            rows.append(
                ParsedRow(
                    sample_id=row["sample_id"].strip(),
                    metric=row["metric"].strip(),
                    value=float(row["value"]),
                    unit=row["unit"].strip(),
                    timepoint=timepoint,
                    replicate_summary=replicate_summary,
                    raw=dict(row),
                )
            )
        return ParsedDataset(rows=rows, parser_name=self.name, parser_version=self.version)

    def qc(self, parsed: ParsedDataset) -> QCReport:
        flags: list[QCFlag] = []
        excluded: set[str] = set()
        for row in parsed.rows:
            if row.value < 0:
                flags.append(
                    QCFlag(
                        sample_id=row.sample_id,
                        code="negative_value",
                        message=f"{row.metric}={row.value} is negative",
                        severity="error",
                    )
                )
                excluded.add(row.sample_id)
            if row.replicate_summary and row.replicate_summary.get("n", 1) < 2:
                flags.append(
                    QCFlag(
                        sample_id=row.sample_id,
                        code="single_replicate",
                        message="only one replicate reported",
                        severity="warning",
                    )
                )
        passed = not any(f.severity == "error" for f in flags)
        return QCReport(passed=passed, flags=flags, excluded_sample_ids=excluded)

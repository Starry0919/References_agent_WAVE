"""Genotype-verification-result CSV parser (doc 11.1). Expected columns:
`sample_id, construct_id, method, result[, detail]`, `result` one of
confirmed/failed/inconclusive.

Deliberately NOT a `DataIngestor` subclass: verification is a
construct-identity fact (feeds `harness/constructs/service.py::
record_genotype_verification` and the Genotype Verification Gate), not a
phenotype `Observation` - forcing it through the Observation-shaped
interface would blur exactly the distinction doc 6.3 insists on.
"""
from __future__ import annotations

import csv
import io
from dataclasses import dataclass, field

REQUIRED_COLUMNS = ("sample_id", "construct_id", "method", "result")
VALID_RESULTS = ("confirmed", "failed", "inconclusive")


@dataclass
class GenotypeVerificationRow:
    sample_id: str
    construct_id: str
    method: str
    result: str
    detail: str = ""


@dataclass
class GenotypeVerificationValidation:
    valid: bool
    errors: list[str] = field(default_factory=list)


def validate(raw_text: str) -> GenotypeVerificationValidation:
    errors: list[str] = []
    reader = csv.DictReader(io.StringIO(raw_text))
    if reader.fieldnames is None:
        return GenotypeVerificationValidation(valid=False, errors=["empty file or no header row"])
    missing = [c for c in REQUIRED_COLUMNS if c not in reader.fieldnames]
    if missing:
        errors.append(f"missing required columns: {missing}")
    count = 0
    for i, row in enumerate(reader, start=2):
        count += 1
        if (row.get("result") or "").strip() not in VALID_RESULTS:
            errors.append(f"row {i}: result must be one of {VALID_RESULTS}, got {row.get('result')!r}")
        if not (row.get("construct_id") or "").strip():
            errors.append(f"row {i}: empty construct_id")
    if count == 0:
        errors.append("no data rows")
    return GenotypeVerificationValidation(valid=not errors, errors=errors)


def parse(raw_text: str) -> list[GenotypeVerificationRow]:
    reader = csv.DictReader(io.StringIO(raw_text))
    return [
        GenotypeVerificationRow(
            sample_id=row["sample_id"].strip(),
            construct_id=row["construct_id"].strip(),
            method=(row.get("method") or "").strip(),
            result=row["result"].strip(),
            detail=(row.get("detail") or "").strip(),
        )
        for row in reader
    ]

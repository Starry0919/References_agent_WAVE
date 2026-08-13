"""ELISER-compatible Bronze historical prior; explicitly not evidence."""
from __future__ import annotations

from pydantic import BaseModel, Field


class HistoricalPriorRecord(BaseModel):
    contract_version: str = "historical-prior/1.0"
    publication_id: str; year: int | None = None; host: str | None = None; product: str | None = None
    gene: str | None = None; modification_direction: str = "Other"; source_granularity: str = "unknown"
    fulltext_available: bool | None = None; extraction_limitations: list[str] = Field(default_factory=list)
    provenance: dict = Field(default_factory=dict)
    source_role: str = "historical_prior_not_evidence"


def compatibility_score(record: HistoricalPriorRecord, *, host: str, product: str, condition_known: bool) -> dict:
    host_match = bool(record.host and host.lower() in record.host.lower())
    product_match = bool(record.product and product.lower() in record.product.lower())
    score = .35 * host_match + .35 * product_match + .1 * bool(record.gene) + .1 * bool(record.fulltext_available) + .1 * condition_known
    return {"historical_prior": round(score, 3), "evidence_strength": 0.0,
            "mechanistic_plausibility": "not_assessed", "project_applicability": "partial" if score >= .5 else "weak",
            "not_evidence": True, "not_recommendation": True,
            "requires_fulltext_experiment_verification": True,
            "semantic_guards": ["co_occurrence_is_not_synergy", "frequency_is_not_effectiveness", "gene_mention_is_not_intervention"]}

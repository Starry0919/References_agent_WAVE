from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class HostRelation(str, Enum):
    EXACT = "exact_host"
    K12_DERIVATIVE = "k12_derivative"
    RELATED_ECOLI = "related_ecoli"
    NON_TARGET = "non_target"
    UNKNOWN = "unknown"


class RelevanceTier(str, Enum):
    TIER_1 = "tier_1_direct_engineering"
    TIER_2 = "tier_2_supporting_engineering"
    TIER_3 = "tier_3_mechanistic"
    BACKGROUND = "background"
    EXCLUDE = "exclude"


class AcquisitionState(str, Enum):
    NOT_PLANNED = "not_planned"
    PLANNED = "planned"
    ALREADY_PRESENT = "already_present"
    ACQUIRED = "acquired"
    NO_OA_SOURCE = "no_oa_source"
    HTTP_ERROR = "http_error"
    NOT_PDF = "not_pdf"
    TIMEOUT = "timeout"
    PAYWALLED = "paywalled"
    RESOLUTION_FAILED = "resolution_failed"


class OrganismSpec(BaseModel):
    species: str
    lineage: str | None = None
    strain_aliases: list[str] = Field(default_factory=list)


class ProductSpec(BaseModel):
    canonical_name: str
    aliases: list[str] = Field(default_factory=list)


class ScientificLiteratureRequest(BaseModel):
    organism: OrganismSpec
    target_product: ProductSpec
    objective: str
    domains: list[str] = Field(default_factory=list)
    max_queries: int = Field(default=12, ge=1, le=30)
    max_results_per_query: int = Field(default=10, ge=1, le=100)
    year_from: int | None = None
    year_until: int | None = None
    desired_publication_forms: list[str] = Field(default_factory=list)
    desired_research_designs: list[str] = Field(default_factory=list)
    desired_engineering_modes: list[str] = Field(default_factory=list)
    desired_evidence_modalities: list[str] = Field(default_factory=list)
    desired_knowledge_contributions: list[str] = Field(default_factory=list)
    desired_evidence_strengths: list[str] = Field(default_factory=list)
    desired_routes: list[str] = Field(default_factory=list)
    sort_mode: str = "RELEVANCE"

    @classmethod
    def k12_tryptophan(cls) -> "ScientificLiteratureRequest":
        return cls(
            organism=OrganismSpec(
                species="Escherichia coli",
                lineage="K-12",
                strain_aliases=["MG1655", "W3110", "BW25113"],
            ),
            target_product=ProductSpec(
                canonical_name="L-tryptophan",
                aliases=["tryptophan", "Trp", "色氨酸", "L-色氨酸"],
            ),
            objective="increase production",
            domains=["metabolic engineering", "synthetic biology", "fermentation engineering"],
        )


class SearchQueryRecord(BaseModel):
    query_id: str
    query_text: str
    query_family: str
    rationale: str
    target_source: str
    created_at: str = Field(default_factory=utc_now)


class SourceRecord(BaseModel):
    source: str
    source_record_id: str | None = None
    query_id: str
    retrieved_at: str = Field(default_factory=utc_now)
    raw: dict[str, Any] = Field(default_factory=dict)


class RelevanceAssessment(BaseModel):
    decision: RelevanceTier
    score: float = Field(ge=0, le=1)
    organism_match: float = 0
    strain_match: float = 0
    product_match: float = 0
    engineering_intervention_match: float = 0
    production_objective_match: float = 0
    experimental_evidence_match: float = 0
    fulltext_availability: float = 0
    host_relation: HostRelation = HostRelation.UNKNOWN
    reason_codes: list[str] = Field(default_factory=list)
    rationale: str


class AcquisitionRecord(BaseModel):
    state: AcquisitionState = AcquisitionState.NOT_PLANNED
    source_url: str | None = None
    local_path: str | None = None
    sha256: str | None = None
    byte_size: int | None = None
    failure_reason: str | None = None
    attempted_at: str | None = None
    attempts: list[dict[str, Any]] = Field(default_factory=list)
    identity_verification: dict[str, Any] | None = None


class PaperCandidate(BaseModel):
    candidate_id: str
    canonical_title: str
    doi: str | None = None
    pmid: str | None = None
    pmcid: str | None = None
    openalex_id: str | None = None
    authors: list[str] = Field(default_factory=list)
    year: int | None = None
    venue: str | None = None
    abstract: str | None = None
    publication_type: str | None = None
    is_review: bool = False
    oa_urls: list[str] = Field(default_factory=list)
    source_records: list[SourceRecord] = Field(default_factory=list)
    relevance: RelevanceAssessment | None = None
    acquisition: AcquisitionRecord = Field(default_factory=AcquisitionRecord)
    metadata_classification: dict[str, Any] | None = None
    fulltext_classification: dict[str, Any] | None = None
    final_classification: dict[str, Any] | None = None
    classification_conflicts: list[str] = Field(default_factory=list)
    route: dict[str, Any] | None = None
    route_confidence: str | None = None
    ranking_score_v2: float | None = None
    citation_expansion_candidates: list[dict[str, Any]] = Field(default_factory=list)


class SourceRun(BaseModel):
    source: str
    query_count: int = 0
    raw_hits: int = 0
    errors: list[str] = Field(default_factory=list)


class DiscoveryResult(BaseModel):
    contract_version: str = "literature-search-result/2.0"
    request: ScientificLiteratureRequest
    queries: list[SearchQueryRecord]
    candidates: list[PaperCandidate]
    source_runs: list[SourceRun]
    generated_at: str = Field(default_factory=utc_now)

"""`EvidenceRetrievalAdapter` (prompt §5.6): the formal, replaceable
retrieval interface. `harness.diagnosis.evidence`/`harness.scientific_
evaluation.evidence` keep owning what an `EvidenceItem`/`EvidenceLink`
*means* to the diagnosis/evaluation pipelines - this package only supplies
where raw evidence documents/claims come from before they are recorded via
`harness.diagnosis.evidence.record_evidence_item`.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol


@dataclass
class AdapterHealth:
    available: bool
    source_name: str
    reason: str = ""
    latency: float | None = None


@dataclass
class EvidenceDocument:
    source_id: str  # e.g. a DOI, an accession, or a local knowledge-base id
    source_type: str  # literature|project_local|curated_knowledge_base
    title: str | None = None
    authors: list[str] = field(default_factory=list)
    publication_year: int | None = None
    journal_or_repository: str | None = None
    doi_or_accession: str | None = None
    url: str | None = None
    abstract_or_summary: str = ""
    raw_metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class EvidenceSearchResult:
    query: str
    documents: list[EvidenceDocument]
    total_available: int | None = None
    source_name: str = ""


@dataclass
class EvidenceClaimDraft:
    """One extracted claim from a document - NOT yet an `EvidenceItem`;
    prompt §5.7's condition/organism/strain/etc fields default to
    `"not_reported"` unless the source (or, for `extraction_method=
    "api_metadata_only"`, only the bibliographic API) actually stated them.
    Never guessed or interpolated."""

    document: EvidenceDocument
    claim_summary: str
    organism: str | None = None
    strain: str | None = None
    genotype: str | None = None
    condition: dict[str, Any] = field(default_factory=dict)
    intervention: str | None = None
    comparator: str | None = None
    measurement: str | None = None
    direction: str | None = None
    effect_size_if_reported: dict[str, Any] | None = None
    uncertainty_if_reported: dict[str, Any] | None = None
    extraction_method: str = "api_metadata_only"
    extraction_status: str = "partial"


class EvidenceRetrievalAdapter(Protocol):
    def search(self, query: str, filters: dict[str, Any], pagination: dict[str, Any]) -> EvidenceSearchResult: ...

    def fetch(self, source_id: str) -> EvidenceDocument | None: ...

    def extract_claims(self, document: EvidenceDocument, schema_version: str) -> list[EvidenceClaimDraft]: ...

    def health_check(self) -> AdapterHealth: ...

"""Wraps the existing local DDR knowledge base (`knowledge/ddr_database/
*.json`, already the sole evidence source `harness.diagnosis.evidence`/
`harness.scientific_evaluation.evidence` use) behind the SAME
`EvidenceRetrievalAdapter` contract the network adapters use - so callers
that want "whatever real evidence sources exist" get a uniform interface,
without this package duplicating or re-parsing the knowledge base's own
existing consumers. Each DDR file's `metadata.reference` block already
carries a real title/authors/journal/year/DOI (e.g. DDR-001 cites a real,
Crossref-resolvable DOI: 10.1002/bit.27665) - this adapter exposes exactly
that, never inventing fields the JSON doesn't have.
"""
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

from harness.config import PROJECT_ROOT
from harness.evidence_retrieval.contracts import AdapterHealth, EvidenceClaimDraft, EvidenceDocument, EvidenceSearchResult

_DDR_DIR = PROJECT_ROOT / "knowledge" / "ddr_database"


class LocalDDRAdapter:
    source_name = "local_ddr"

    def __init__(self, ddr_dir: Path | None = None) -> None:
        self._dir = ddr_dir or _DDR_DIR

    def _load_all(self) -> list[dict[str, Any]]:
        if not self._dir.is_dir():
            return []
        records = []
        for f in sorted(self._dir.glob("*.json")):
            try:
                records.append(json.loads(f.read_text(encoding="utf-8")))
            except (OSError, json.JSONDecodeError):
                continue
        return records

    def health_check(self) -> AdapterHealth:
        t0 = time.monotonic()
        if not self._dir.is_dir():
            return AdapterHealth(available=False, source_name=self.source_name, reason=f"knowledge base directory not found: {self._dir}")
        records = self._load_all()
        if not records:
            return AdapterHealth(available=False, source_name=self.source_name, reason="knowledge base directory contains no readable DDR records")
        return AdapterHealth(available=True, source_name=self.source_name, latency=time.monotonic() - t0)

    def search(self, query: str, filters: dict[str, Any] | None = None, pagination: dict[str, Any] | None = None) -> EvidenceSearchResult:
        query_lower = query.lower()
        docs = []
        for rec in self._load_all():
            meta = rec.get("metadata", {})
            haystack = " ".join(str(v) for v in (meta.get("target_product", ""), meta.get("title", ""), " ".join(meta.get("category", [])))).lower()
            if query_lower in haystack or any(word in haystack for word in query_lower.split() if len(word) > 3):
                docs.append(self._to_document(rec))
        return EvidenceSearchResult(query=query, documents=docs, total_available=len(docs), source_name=self.source_name)

    def fetch(self, source_id: str) -> EvidenceDocument | None:
        for rec in self._load_all():
            if rec.get("ddr_id") == source_id:
                return self._to_document(rec)
        return None

    def extract_claims(self, document: EvidenceDocument, schema_version: str) -> list[EvidenceClaimDraft]:
        rec = document.raw_metadata
        diagnosis = rec.get("biological_diagnosis", {})
        claims = []
        for obs in diagnosis.get("observations", [])[:5]:
            claims.append(
                EvidenceClaimDraft(
                    document=document, claim_summary=str(obs), organism=rec.get("metadata", {}).get("organism"),
                    extraction_method="manual_or_rule", extraction_status="complete",
                )
            )
        return claims

    @staticmethod
    def _to_document(rec: dict[str, Any]) -> EvidenceDocument:
        meta = rec.get("metadata", {})
        ref = meta.get("reference", {})
        return EvidenceDocument(
            source_id=rec.get("ddr_id", ""), source_type="curated_knowledge_base", title=ref.get("title") or meta.get("title"),
            authors=[ref["authors"]] if ref.get("authors") else [], publication_year=(int(ref["year"]) if str(ref.get("year", "")).isdigit() else None),
            journal_or_repository=ref.get("journal"), doi_or_accession=ref.get("doi"), url=None,
            abstract_or_summary=rec.get("engineering_problem", {}).get("problem_statement", ""), raw_metadata=rec,
        )

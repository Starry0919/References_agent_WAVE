"""Wraps the existing local DDR knowledge base (`knowledge/ddr_database/
*.json`, already the sole evidence source `harness.diagnosis.evidence`/
`harness.scientific_evaluation.evidence` use) behind the SAME
`EvidenceRetrievalAdapter` contract the network adapters use - so callers
that want "whatever real evidence sources exist" get a uniform interface,
without this package duplicating or re-parsing the knowledge base's own
existing consumers.

Supports both DDR v1 (legacy) and v2 (decision_chain-based, teacher spec)
formats. v2 DDRs expose richer structured evidence from their decision_chain
steps, with evidence_grading and reason_nature fields directly addressable.
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
        # Skip schema files (not DDR records)
        skip_patterns = ("schema_v2.json", ".schema", "_template")
        for f in sorted(self._dir.glob("*.json")):
            if any(p in f.name for p in skip_patterns):
                continue
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
        v1_count = sum(1 for r in records if r.get("schema_version", "1.0") == "1.0")
        v2_count = len(records) - v1_count
        return AdapterHealth(available=True, source_name=self.source_name,
                             reason=f"{len(records)} DDRs loaded (v1: {v1_count}, v2: {v2_count})",
                             latency=time.monotonic() - t0)

    def search(self, query: str, filters: dict[str, Any] | None = None, pagination: dict[str, Any] | None = None) -> EvidenceSearchResult:
        query_lower = query.lower()
        docs = []
        for rec in self._load_all():
            meta = rec.get("metadata", {})
            # Search v1 fields
            haystack_parts = [
                str(meta.get("target_product", "")),
                str(meta.get("title", "")),
                " ".join(meta.get("category", [])),
            ]
            # Search v2 decision_chain as well
            for step in rec.get("decision_chain", []):
                haystack_parts.append(str(step.get("target", {}).get("gene", "")))
                haystack_parts.append(str(step.get("target", {}).get("enzyme", "")))
                haystack_parts.append(str(step.get("trigger", {}).get("observation", "")))
                haystack_parts.append(str(step.get("rule", "")))
            haystack = " ".join(haystack_parts).lower()
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
        claims = []

        # v2: extract claims from decision_chain evidence + biological_diagnosis
        if rec.get("schema_version") == "2.0":
            for step in rec.get("decision_chain", []):
                evidence = step.get("evidence", {})
                trigger = step.get("trigger", {})
                if evidence.get("description"):
                    claims.append(EvidenceClaimDraft(
                        document=document,
                        claim_summary=f"[{step.get('evidence_grading', '未分级')}] {evidence['description'][:200]}",
                        organism=rec.get("metadata", {}).get("organism"),
                        intervention=step.get("implementation_detail", ""),
                        measurement=step.get("result", {}).get("metric", ""),
                        extraction_method="semi_automated" if rec.get("extraction_meta", {}).get("extraction_method") == "semi_automated" else "manual_or_rule",
                        extraction_status="complete",
                    ))

        # v1 fallback + always include diagnosis observations
        diagnosis = rec.get("biological_diagnosis", {})
        for obs in diagnosis.get("observations", [])[:3]:
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
        # Build a richer abstract from v2 decision_chain or v1 problem statement
        abstract = rec.get("engineering_problem", {}).get("problem_statement", "")
        if not abstract:
            # Synthesize from decision_chain
            steps = rec.get("decision_chain", [])
            abstract = "; ".join(s.get("trigger", {}).get("observation", "")[:120] for s in steps[:3])

        return EvidenceDocument(
            source_id=rec.get("ddr_id", ""), source_type="curated_knowledge_base",
            title=ref.get("title") or meta.get("title"),
            authors=[ref["authors"]] if ref.get("authors") else [],
            publication_year=(int(ref["year"]) if str(ref.get("year", "")).isdigit() else None),
            journal_or_repository=ref.get("journal"), doi_or_accession=ref.get("doi"), url=None,
            abstract_or_summary=abstract, raw_metadata=rec,
        )

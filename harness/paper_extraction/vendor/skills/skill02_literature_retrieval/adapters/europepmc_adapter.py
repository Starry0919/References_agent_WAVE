from typing import Any, Dict, List

from .base import JsonTransport, LiteratureAdapter, RetrievalBatch


class EuropePmcAdapter(LiteratureAdapter):
    name = "Europe PMC"
    URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"

    def __init__(self, transport=None):
        self.transport = transport or JsonTransport()

    def search(self, query: str, limit: int) -> RetrievalBatch:
        data = self.transport.get_json(self.URL, {"query": query, "format": "json", "pageSize": limit})
        records: List[Dict[str, Any]] = []
        for item in data.get("resultList", {}).get("result", []):
            identifiers = {}
            if item.get("pmid"):
                identifiers["pmid"] = str(item["pmid"])
            if item.get("pmcid"):
                identifiers["pmcid"] = str(item["pmcid"])
            records.append({
                "source": self.name, "source_record_id": item.get("id"),
                "title": item.get("title", ""), "authors": [v.strip() for v in str(item.get("authorString") or "").split(",") if v.strip()],
                "journal": item.get("journalTitle"), "year": item.get("pubYear"),
                "doi": item.get("doi"), "identifiers": identifiers
            })
        return RetrievalBatch(self.name, query, records)


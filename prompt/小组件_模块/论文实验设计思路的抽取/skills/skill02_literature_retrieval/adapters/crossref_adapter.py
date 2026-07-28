from typing import Any, Dict, List

from .base import JsonTransport, LiteratureAdapter, RetrievalBatch


class CrossrefAdapter(LiteratureAdapter):
    name = "Crossref"
    URL = "https://api.crossref.org/works"

    def __init__(self, transport=None):
        self.transport = transport or JsonTransport()

    def search(self, query: str, limit: int) -> RetrievalBatch:
        data = self.transport.get_json(self.URL, {"query.bibliographic": query, "rows": limit}, {"User-Agent": "DBTL-Literature-Retrieval/0.2"})
        records: List[Dict[str, Any]] = []
        for item in data.get("message", {}).get("items", []):
            date_parts = (item.get("published-print") or item.get("published-online") or {}).get("date-parts", [[]])
            year = date_parts[0][0] if date_parts and date_parts[0] else None
            records.append({
                "source": self.name, "source_record_id": item.get("DOI") or item.get("URL"),
                "title": (item.get("title") or [""])[0],
                "authors": [" ".join(filter(None, [a.get("given"), a.get("family")])) for a in item.get("author", [])],
                "journal": (item.get("container-title") or [None])[0],
                "year": year, "doi": item.get("DOI"), "identifiers": {}
            })
        return RetrievalBatch(self.name, query, records)


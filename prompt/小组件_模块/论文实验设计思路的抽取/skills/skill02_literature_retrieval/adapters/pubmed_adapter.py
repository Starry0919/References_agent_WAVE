from typing import Any, Dict, List

from .base import JsonTransport, LiteratureAdapter, RetrievalBatch


class PubMedAdapter(LiteratureAdapter):
    name = "PubMed"
    SEARCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    SUMMARY_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"

    def __init__(self, transport=None):
        self.transport = transport or JsonTransport()

    def search(self, query: str, limit: int) -> RetrievalBatch:
        found = self.transport.get_json(self.SEARCH_URL, {"db": "pubmed", "term": query, "retmode": "json", "retmax": limit})
        ids = found.get("esearchresult", {}).get("idlist", [])
        if not ids:
            return RetrievalBatch(self.name, query, [])
        summary = self.transport.get_json(self.SUMMARY_URL, {"db": "pubmed", "id": ",".join(ids), "retmode": "json"})
        result = summary.get("result", {})
        records: List[Dict[str, Any]] = []
        for pmid in ids:
            item = result.get(str(pmid), {})
            article_ids = {v.get("idtype"): v.get("value") for v in item.get("articleids", []) if v.get("idtype")}
            records.append({
                "source": self.name, "source_record_id": str(pmid),
                "title": item.get("title", ""), "authors": [a.get("name", "") for a in item.get("authors", [])],
                "journal": item.get("fulljournalname") or item.get("source"),
                "year": str(item.get("pubdate", ""))[:4] or None,
                "doi": article_ids.get("doi"), "identifiers": {"pmid": str(pmid)}
            })
        return RetrievalBatch(self.name, query, records)


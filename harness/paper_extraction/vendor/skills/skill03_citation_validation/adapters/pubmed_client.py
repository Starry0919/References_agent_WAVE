from .base import JsonTransport


class PubMedClient:
    name = "PubMed"
    SEARCH = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    SUMMARY = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"

    def __init__(self, transport=None):
        self.transport = transport or JsonTransport()

    def lookup_doi(self, doi):
        records = self.search(doi + "[doi]", 1)
        return records[0] if records else None

    def search(self, query, limit=5):
        found = self.transport.get_json(self.SEARCH, {"db": "pubmed", "term": query, "retmode": "json", "retmax": limit})
        ids = (found or {}).get("esearchresult", {}).get("idlist", [])
        if not ids:
            return []
        data = self.transport.get_json(self.SUMMARY, {"db": "pubmed", "id": ",".join(ids), "retmode": "json"})
        result = (data or {}).get("result", {})
        records = []
        for pmid in ids:
            item = result.get(str(pmid), {})
            article_ids = {v.get("idtype"): v.get("value") for v in item.get("articleids", [])}
            records.append({
                "doi": article_ids.get("doi"), "title": item.get("title", ""),
                "authors": [a.get("name", "") for a in item.get("authors", [])],
                "journal": item.get("fulljournalname") or item.get("source"),
                "year": str(item.get("pubdate", ""))[:4] or None,
                "source_record_id": str(pmid)
            })
        return records


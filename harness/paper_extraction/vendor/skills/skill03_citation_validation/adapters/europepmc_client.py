from .base import JsonTransport


class EuropePmcClient:
    name = "Europe PMC"
    URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"

    def __init__(self, transport=None):
        self.transport = transport or JsonTransport()

    def lookup_doi(self, doi):
        records = self.search('DOI:"' + doi + '"', 1)
        return records[0] if records else None

    def search(self, query, limit=5):
        data = self.transport.get_json(self.URL, {"query": query, "format": "json", "pageSize": limit})
        return [{
            "doi": item.get("doi"), "title": item.get("title", ""),
            "authors": [v.strip() for v in str(item.get("authorString") or "").split(",") if v.strip()],
            "journal": item.get("journalTitle"), "year": item.get("pubYear"),
            "source_record_id": item.get("id")
        } for item in (data or {}).get("resultList", {}).get("result", [])]


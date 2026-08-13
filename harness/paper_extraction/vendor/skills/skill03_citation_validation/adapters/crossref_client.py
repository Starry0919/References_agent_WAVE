import urllib.parse

from .base import JsonTransport


class CrossrefClient:
    name = "Crossref"
    URL = "https://api.crossref.org/works"

    def __init__(self, transport=None):
        self.transport = transport or JsonTransport()

    def lookup_doi(self, doi):
        data = self.transport.get_json(self.URL + "/" + urllib.parse.quote(doi, safe=""), headers={"User-Agent": "DBTL-Citation-Validator/0.2"})
        return self._record(data.get("message", {})) if data else None

    def search(self, query, limit=5):
        data = self.transport.get_json(self.URL, {"query.bibliographic": query, "rows": limit}, {"User-Agent": "DBTL-Citation-Validator/0.2"})
        return [self._record(v) for v in (data or {}).get("message", {}).get("items", [])]

    def _record(self, item):
        parts = (item.get("published-print") or item.get("published-online") or {}).get("date-parts", [[]])
        return {
            "doi": item.get("DOI"), "title": (item.get("title") or [""])[0],
            "authors": [" ".join(filter(None, [a.get("given"), a.get("family")])) for a in item.get("author", [])],
            "journal": (item.get("container-title") or [None])[0],
            "year": parts[0][0] if parts and parts[0] else None,
            "source_record_id": item.get("DOI")
        }


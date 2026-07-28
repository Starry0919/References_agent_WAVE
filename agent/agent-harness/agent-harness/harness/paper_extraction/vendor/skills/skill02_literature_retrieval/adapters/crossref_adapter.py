import re
from typing import Any, Dict, List

from .base import JsonTransport, LiteratureAdapter, RetrievalBatch

# Crossref's `query.bibliographic` is a relevance-ranked (fuzzy) full-text
# field, not a boolean query language - literal quotes/AND/OR/NOT/parens are
# indexed as ordinary noise tokens rather than interpreted as operators, so a
# query built for a real boolean engine (PubMed's esearch) actively dilutes
# Crossref's ranking instead of narrowing it. Flatten those operators away
# and let Crossref's own fuzzy matching work on the plain terms.
_BOOLEAN_SYNTAX = re.compile(r'"|\bAND\b|\bOR\b|\bNOT\b|[()]', re.I)


class CrossrefAdapter(LiteratureAdapter):
    name = "Crossref"
    URL = "https://api.crossref.org/works"

    def __init__(self, transport=None):
        self.transport = transport or JsonTransport()

    def search(self, query: str, limit: int) -> RetrievalBatch:
        plain_terms = " ".join(_BOOLEAN_SYNTAX.sub(" ", query).split())
        focused = f"{plain_terms} experimental design mechanism"
        data = self.transport.get_json(
            self.URL,
            {
                "query.bibliographic": focused,
                "rows": min(max(limit * 4, 20), 60),
                "filter": "from-pub-date:2020-01-01,until-pub-date:2026-12-31,type:journal-article",
            },
            {"User-Agent": "DBTL-Literature-Retrieval/0.3"},
        )
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
        return RetrievalBatch(self.name, focused, records)

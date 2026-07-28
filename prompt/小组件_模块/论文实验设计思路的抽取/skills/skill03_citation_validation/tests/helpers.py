from datetime import datetime, timezone

from adapters.base import DatabaseUnavailable


CANDIDATE = {
    "paper_id": "paper:test",
    "title": "Engineering Escherichia coli for succinate production",
    "authors": ["Alice Smith", "Bob Jones"],
    "journal": "Nature Biotechnology",
    "year": 2024,
    "identifiers": {"doi": "10.1000/correct", "pmid": "123"},
    "retrieval_sources": ["PubMed"],
    "citation_validation": {"status": "unknown", "attempts": 0, "checks": []}
}

METADATA = {
    "doi": "10.1000/correct",
    "title": "Engineering Escherichia coli for succinate production",
    "authors": ["Alice Smith", "Bob Jones"],
    "journal": "Nature Biotechnology",
    "year": 2024,
    "source_record_id": "10.1000/correct"
}


def fixed_clock():
    return datetime(2026, 7, 25, 8, 0, tzinfo=timezone.utc)


class FakeClient:
    def __init__(self, name="Crossref", lookup=None, searches=None, unavailable=False):
        self.name = name
        self.lookup = lookup
        self.searches = list(searches or [])
        self.unavailable = unavailable
        self.search_calls = 0

    def lookup_doi(self, doi):
        if self.unavailable:
            raise DatabaseUnavailable("offline")
        return self.lookup

    def search(self, query, limit=5):
        if self.unavailable:
            raise DatabaseUnavailable("offline")
        index = self.search_calls
        self.search_calls += 1
        return self.searches[index] if index < len(self.searches) else []


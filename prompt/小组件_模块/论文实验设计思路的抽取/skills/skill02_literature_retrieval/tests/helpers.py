from datetime import datetime, timezone

from adapters.base import RetrievalBatch, SourceError


INTENT = {
    "organism": "Escherichia coli",
    "strain": "K-12",
    "phenotype": "increase succinate production",
    "engineering_objective": "gene knockout",
    "keywords": ["E. coli K-12", "succinate", "knockout"],
    "inclusion_criteria": [],
    "exclusion_criteria": []
}


def fixed_clock():
    return datetime(2026, 7, 25, 8, 0, tzinfo=timezone.utc)


class FixedAdapter:
    def __init__(self, name, records=None, error=None):
        self.name = name
        self.records = records or []
        self.error = error

    def search(self, query, limit):
        if self.error:
            raise self.error
        return RetrievalBatch(self.name, query, self.records[:limit])


PAPER = {
    "source": "PubMed",
    "source_record_id": "123",
    "title": "Gene knockout improves succinate production in Escherichia coli K-12",
    "doi": "10.1000/example",
    "authors": ["A. Author", "B. Author"],
    "journal": "Synthetic Biology",
    "year": 2024,
    "identifiers": {"pmid": "123"}
}


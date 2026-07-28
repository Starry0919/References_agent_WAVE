from datetime import datetime, timezone

VALID_PDF = b"%PDF-1.4\n1 0 obj\n<<>>\nendobj\ntrailer\n<<>>\n%%EOF\n"

CANDIDATE = {
    "paper_id": "paper:test",
    "title": "Verified paper",
    "authors": ["A. Author"],
    "journal": "Journal",
    "year": 2024,
    "identifiers": {"doi": "10.1000/test"},
    "retrieval_sources": ["Crossref"],
    "citation_validation": {"status": "valid", "attempts": 1, "checks": []}
}


def fixed_clock():
    return datetime(2026, 7, 25, 8, 0, tzinfo=timezone.utc)


class FakeDownloader:
    def __init__(self, data=VALID_PDF, content_type="application/pdf", source_type="publisher_download", fail=False):
        self.data = data
        self.content_type = content_type
        self.source_type = source_type
        self.fail = fail

    def fetch(self, candidate, url=None):
        if self.fail:
            raise RuntimeError("download failed")
        return {
            "data": self.data, "content_type": self.content_type,
            "source_url": url or "https://example.org/paper.pdf",
            "final_url": url or "https://example.org/paper.pdf",
            "source_type": self.source_type
        }


from .base import BinaryTransport


class DoiDownloader:
    source_type = "doi_download"

    def __init__(self, transport=None):
        self.transport = transport or BinaryTransport()

    def fetch(self, candidate, url=None):
        doi = candidate.get("identifiers", {}).get("doi")
        target = url or ("https://doi.org/" + doi if doi else None)
        if not target:
            raise ValueError("Candidate has no DOI")
        result = self.transport.get(target, {"Accept": "application/pdf"})
        return {**result, "source_url": target, "source_type": self.source_type}


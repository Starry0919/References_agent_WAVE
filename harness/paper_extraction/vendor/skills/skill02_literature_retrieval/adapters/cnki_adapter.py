from .base import LiteratureAdapter, SourceError


class CnkiAdapter(LiteratureAdapter):
    name = "CNKI"

    def search(self, query: str, limit: int):
        raise SourceError("CNKI API is not available.", "not_available")


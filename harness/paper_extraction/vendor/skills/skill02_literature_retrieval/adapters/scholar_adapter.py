from .base import LiteratureAdapter, SourceError


class ScholarAdapter(LiteratureAdapter):
    name = "Google Scholar"

    def search(self, query: str, limit: int):
        raise SourceError("Google Scholar adapter requires an approved provider.", "unavailable")


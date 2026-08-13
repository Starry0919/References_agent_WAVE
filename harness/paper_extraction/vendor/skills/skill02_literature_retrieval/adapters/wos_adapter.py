from .base import LiteratureAdapter, SourceError


class WebOfScienceAdapter(LiteratureAdapter):
    name = "Web of Science"

    def search(self, query: str, limit: int):
        raise SourceError("Web of Science API is not configured.", "not_configured")


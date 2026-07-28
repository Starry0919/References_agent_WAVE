from .base import BinaryTransport


class PublisherDownloader:
    source_type = "publisher_download"

    def __init__(self, transport=None):
        self.transport = transport or BinaryTransport()

    def fetch(self, candidate, url=None):
        if not url:
            raise ValueError("Publisher PDF URL is not configured")
        result = self.transport.get(url, {"Accept": "application/pdf"})
        return {**result, "source_url": url, "source_type": self.source_type}


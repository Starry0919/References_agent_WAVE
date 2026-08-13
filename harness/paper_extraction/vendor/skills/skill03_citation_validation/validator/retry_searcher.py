import re


class RetrySearcher:
    MAX_ATTEMPTS = 3

    def strategies(self, candidate):
        title = candidate.get("title", "")
        first_author = candidate.get("authors", [""])[0] if candidate.get("authors") else ""
        journal = candidate.get("journal") or ""
        title_keywords = " ".join(re.findall(r"[A-Za-z0-9-]+|[\u4e00-\u9fff]{2,}", title)[:8])
        return [
            {"attempt": 1, "mode": "doi", "query": candidate.get("identifiers", {}).get("doi")},
            {"attempt": 2, "mode": "search", "query": " ".join(v for v in (title, first_author) if v)},
            {"attempt": 3, "mode": "search", "query": " ".join(v for v in (title_keywords, journal) if v)}
        ]

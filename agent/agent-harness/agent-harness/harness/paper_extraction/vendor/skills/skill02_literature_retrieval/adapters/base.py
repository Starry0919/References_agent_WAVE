from __future__ import annotations

import json
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Any, Dict, List, Mapping, Optional


class SourceError(Exception):
    def __init__(self, message: str, state: str = "unavailable", rate_limited: bool = False):
        super().__init__(message)
        self.state = state
        self.rate_limited = rate_limited


class JsonTransport:
    def get_json(self, url: str, params: Mapping[str, Any], headers: Optional[Mapping[str, str]] = None) -> Dict[str, Any]:
        target = url + "?" + urllib.parse.urlencode(params, doseq=True)
        request = urllib.request.Request(target, headers=dict(headers or {}))
        try:
            with urllib.request.urlopen(request, timeout=20) as response:
                return json.loads(response.read().decode("utf-8"))
        except Exception as exc:
            rate_limited = getattr(exc, "code", None) == 429
            raise SourceError(str(exc), "rate_limit" if rate_limited else "unavailable", rate_limited) from exc


@dataclass
class RetrievalBatch:
    source: str
    query: str
    records: List[Dict[str, Any]]
    status: str = "available"


class LiteratureAdapter:
    name = "base"

    def search(self, query: str, limit: int) -> RetrievalBatch:
        raise NotImplementedError


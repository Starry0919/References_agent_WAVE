"""Minimal Kimi-K3 client restricted to query expansion and relevance scoring."""

from __future__ import annotations

import json
import os
import urllib.request
from typing import Any, Dict, List, Mapping, Sequence


class KimiK3Client:
    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.moonshot.cn/v1/chat/completions",
        model: str = "kimi-k3",
        timeout: int = 30,
    ):
        if not api_key:
            raise ValueError("Kimi API key is required")
        self.api_key = api_key
        self.base_url = base_url
        self.model = model
        self.timeout = timeout

    @classmethod
    def from_environment(cls):
        key = os.environ.get("KIMI_API_KEY")
        return cls(key) if key else None

    def expand_queries(self, intent: Mapping[str, Any], fallback: Sequence[Mapping[str, Any]]) -> List[Dict[str, str]]:
        payload = {
            "task": "Expand search queries only. Never output papers, DOI, title, journal, authors or year.",
            "research_intent": dict(intent),
            "original_queries": list(fallback),
            "output_schema": {"queries": [{"name": "string", "query": "string"}]},
        }
        result = self._json_completion(payload)
        queries = result.get("queries")
        if not isinstance(queries, list):
            raise ValueError("Kimi response has no queries array")
        return [
            {"name": str(v.get("name", "kimi")), "query": str(v["query"])}
            for v in queries if isinstance(v, Mapping) and v.get("query")
        ]

    def score_relevance(self, candidate: Mapping[str, Any], intent: Mapping[str, Any]) -> Dict[str, Any]:
        payload = {
            "task": "Score only the supplied database candidate. Never add or modify bibliographic facts.",
            "research_intent": dict(intent),
            "database_candidate": dict(candidate),
            "output_schema": {"score": "number 0..1", "reason": "short string"},
        }
        result = self._json_completion(payload)
        return {"score": float(result["score"]), "reason": str(result.get("reason", ""))}

    def _json_completion(self, content: Mapping[str, Any]) -> Dict[str, Any]:
        body = json.dumps({
            "model": self.model,
            "temperature": 0,
            "response_format": {"type": "json_object"},
            "messages": [
                {"role": "system", "content": "Return JSON only. Bibliographic facts must come exclusively from database_candidate."},
                {"role": "user", "content": json.dumps(content, ensure_ascii=False)}
            ]
        }).encode("utf-8")
        request = urllib.request.Request(
            self.base_url, data=body,
            headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        )
        with urllib.request.urlopen(request, timeout=self.timeout) as response:
            data = json.loads(response.read().decode("utf-8"))
        return json.loads(data["choices"][0]["message"]["content"])


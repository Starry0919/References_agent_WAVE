"""Constrained Doubao advisor for legal PDF source ordering."""

from __future__ import annotations

import json
import os
import urllib.request


class DoubaoPdfAdvisor:
    URL = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"

    def __init__(self, api_key, model="doubao-smart-router-250928", timeout=20):
        if not api_key:
            raise ValueError("ARK_API_KEY is required")
        self.api_key, self.model, self.timeout = api_key, model, timeout

    @classmethod
    def from_environment(cls):
        key = os.environ.get("ARK_API_KEY")
        return cls(key, os.environ.get("ARK_MODEL", "doubao-smart-router-250928")) if key else None

    def prioritize(self, candidate, allowed_sources):
        prompt = {
            "task": "Order the supplied legal PDF acquisition source types.",
            "hard_rules": [
                "Return only values from allowed_sources.",
                "Never create URLs, DOI, licenses, bibliographic facts, or download claims.",
                "Prefer open-access metadata services and repositories.",
            ],
            "candidate": {
                "doi_present": bool((candidate.get("identifiers") or {}).get("doi")),
                "journal": candidate.get("journal"),
                "year": candidate.get("year"),
            },
            "allowed_sources": list(allowed_sources),
            "output_schema": {"ordered_sources": ["string"]},
        }
        body = json.dumps({
            "model": self.model,
            "temperature": 0,
            "response_format": {"type": "json_object"},
            "messages": [
                {"role": "system", "content": "Return JSON only. Obey all hard rules."},
                {"role": "user", "content": json.dumps(prompt, ensure_ascii=False)},
            ],
        }).encode("utf-8")
        request = urllib.request.Request(
            self.URL, data=body,
            headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
        )
        with urllib.request.urlopen(request, timeout=self.timeout) as response:
            result = json.loads(response.read().decode("utf-8"))
        proposed = json.loads(result["choices"][0]["message"]["content"]).get("ordered_sources", [])
        allowed = list(dict.fromkeys(allowed_sources))
        safe = [value for value in proposed if value in allowed]
        return safe + [value for value in allowed if value not in safe]

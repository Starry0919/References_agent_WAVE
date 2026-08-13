from typing import Any, Dict, List, Mapping, Optional


class QueryExpander:
    """Kimi may propose query strings only; deterministic fallback is mandatory."""

    def __init__(self, kimi_client=None):
        self.kimi_client = kimi_client

    def expand(self, intent: Mapping[str, Any], retrieval_strategy: Mapping[str, Any]) -> Dict[str, Any]:
        existing = [q for q in retrieval_strategy.get("queries", []) if isinstance(q, Mapping) and q.get("query")]
        fallback = existing or [{"name": "fallback", "query": self._fallback(intent), "syntax": "boolean"}]
        if not self.kimi_client:
            return {"queries": fallback, "model_used": None, "fallback_used": True, "error": None}
        try:
            proposed = self.kimi_client.expand_queries(intent, fallback)
            safe = [{"name": str(q.get("name", "kimi")), "query": str(q["query"]), "syntax": "boolean"} for q in proposed if isinstance(q, Mapping) and q.get("query")]
            return {"queries": safe or fallback, "model_used": "Kimi-K3", "fallback_used": not bool(safe), "error": None}
        except Exception as exc:
            return {"queries": fallback, "model_used": "Kimi-K3", "fallback_used": True, "error": type(exc).__name__}

    @staticmethod
    def _fallback(intent: Mapping[str, Any]) -> str:
        terms: List[str] = []
        for name in ("organism", "strain", "phenotype", "engineering_objective"):
            if intent.get(name):
                terms.append(str(intent[name]))
        terms.extend(str(v) for v in intent.get("keywords", []) if v)
        unique = list(dict.fromkeys(terms))
        return " AND ".join(f'"{v}"' if " " in v else v for v in unique)


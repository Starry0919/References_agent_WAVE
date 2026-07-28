import re
from typing import Any, Dict, Mapping, Sequence


class RelevanceRanker:
    def __init__(self, kimi_client=None):
        self.kimi_client = kimi_client

    def score(self, candidate: Mapping[str, Any], intent: Mapping[str, Any]) -> Dict[str, Any]:
        text = " ".join([
            str(candidate.get("title") or ""),
            str(candidate.get("journal") or ""),
            " ".join(candidate.get("authors", []))
        ]).casefold()
        fields = {}
        for field in ("organism", "strain", "phenotype", "engineering_objective"):
            value = intent.get(field)
            tokens = [t.casefold() for t in re.findall(r"[A-Za-z0-9αβ-]+|[\u4e00-\u9fff]{2,}", str(value or ""))]
            fields[field + "_match"] = bool(tokens) and any(t in text for t in tokens)
        keyword_tokens = [str(v).casefold() for v in intent.get("keywords", [])]
        keyword_hits = sum(1 for token in keyword_tokens if token and token in text)
        score = (sum(fields.values()) + min(keyword_hits, 2) / 2) / 5
        reason = "deterministic field overlap"
        if self.kimi_client:
            try:
                model_result = self.kimi_client.score_relevance(dict(candidate), dict(intent))
                score = max(0.0, min(1.0, float(model_result["score"])))
                reason = str(model_result.get("reason") or "Kimi-K3 relevance assessment")
            except Exception:
                reason += "; Kimi-K3 fallback"
        return {**fields, "relevance_score": round(score, 4), "ranking_reason": reason}


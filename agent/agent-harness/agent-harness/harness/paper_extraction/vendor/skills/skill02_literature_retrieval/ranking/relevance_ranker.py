import re
from typing import Any, Dict, Mapping, Sequence


class RelevanceRanker:
    PREFERRED_JOURNALS = {
        "nature", "science", "cell", "nature biotechnology",
        "nature chemical biology", "proceedings of the national academy of sciences",
        "pnas", "science advances", "nature communications",
        "acs synthetic biology", "metabolic engineering",
    }
    ENGINEERING_TERMS = {
        "engineering", "knockout", "deletion", "overexpression", "crispr",
        "synthetic regulation", "protein engineering", "metabolic engineering",
    }
    def __init__(self, kimi_client=None):
        self.kimi_client = kimi_client

    def score(self, candidate: Mapping[str, Any], intent: Mapping[str, Any], use_kimi: bool = True) -> Dict[str, Any]:
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
        relevance = min(1.0, (sum(fields.values()) + min(keyword_hits, 2) / 2) / 3)
        year = int(candidate.get("year") or 0)
        recency = max(0.0, min(1.0, (year - 2020) / 6))
        journal = str(candidate.get("journal") or "").casefold()
        # Crossref has no IF field. Preferred-journal membership is a
        # transparent proxy until a current licensed IF snapshot is supplied.
        journal_impact = 0.75 if journal in self.PREFERRED_JOURNALS else 0.0
        organism = 1.0 if fields["organism_match"] or fields["strain_match"] else (
            0.5 if not intent.get("organism") and not intent.get("strain") else 0.0
        )
        engineering = 1.0 if any(term in text for term in self.ENGINEERING_TERMS) else 0.0
        score = relevance * 0.45 + organism * 0.20 + journal_impact * 0.15 + recency * 0.10 + engineering * 0.10
        reason = "weighted: relevance=.45 organism=.20 journal/IF-proxy=.15 recency=.10 design=.10"
        if self.kimi_client and use_kimi:
            try:
                model_result = self.kimi_client.score_relevance(dict(candidate), dict(intent))
                score = max(0.0, min(1.0, float(model_result["score"])))
                reason = str(model_result.get("reason") or "Kimi-K3 relevance assessment")
            except Exception:
                reason += "; Kimi-K3 fallback"
        return {
            **fields, "relevance_score": round(score, 4), "ranking_reason": reason,
            "ranking_components": {
                "relevance": round(relevance, 4), "organism": organism,
                "journal_impact": journal_impact, "recency": round(recency, 4),
                "design_quality": engineering,
            },
            "impact_factor_status": "preferred_journal_proxy_not_numeric_if",
        }

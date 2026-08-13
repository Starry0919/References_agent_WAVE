from .common import find_candidates, matching_sentences


def extract_outcomes(items):
    observed_patterns = [r"\b(?:increased|decreased|reduced|improved|higher|lower|significant(?:ly)?)\b", r"(?:提高|降低|显著|增加|减少)"]
    conclusion_patterns = [r"\b(?:we\s+conclude|these results (?:show|demonstrate|indicate)|our findings)\b", r"(?:结果表明|我们认为|研究表明)"]
    observed_candidates = find_candidates(items, observed_patterns, sections=["results", "figure", "table"])
    conclusion_candidates = find_candidates(items, conclusion_patterns, sections=["results", "discussion", "conclusion"])
    return {
        "observed_outcomes": [s for c in observed_candidates for s in matching_sentences(c, observed_patterns)][:20],
        "author_conclusions": [s for c in conclusion_candidates for s in matching_sentences(c, conclusion_patterns)][:10]
    }, list(dict.fromkeys(id(v) for v in observed_candidates + conclusion_candidates)), observed_candidates + conclusion_candidates


from .common import find_candidates, matching_sentences


def extract_objective(items):
    patterns = [
        r"\b(?:aim|objective|purpose|goal)s?\b",
        r"\bwe\s+(?:investigated|evaluated|examined|sought|tested|engineered|constructed|developed|designed|optimi[sz]ed|improved|increased|enhanced)\b",
        r"\b(?:to|in order to)\s+(?:increase|enhance|improve|optimi[sz]e|maximize|boost)\s+[\w\s,-]{1,60}(?:production|yield|titer|productivity)\b",
        r"(?:本研究|研究目的|旨在|为了提高|为了增加)"
    ]
    candidates = find_candidates(items, patterns, sections=["abstract", "introduction", "results"])
    values = [s for c in candidates for s in matching_sentences(c, patterns)]
    return (values[:3], candidates[:3])


def extract_hypothesis(items):
    patterns = [r"\bwe\s+hypothes(?:ize|ized|ised)\b", r"\bour\s+hypothesis\b", r"(?:我们假设|研究假设)"]
    candidates = find_candidates(items, patterns)
    values = [s for c in candidates for s in matching_sentences(c, patterns)]
    return (values[:3], candidates[:3])


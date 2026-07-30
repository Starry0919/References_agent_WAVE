import json
import re


ALIASES = {
    "escherichia coli": ["escherichia coli", "e. coli", "e coli"],
    "gene knockout": ["gene knockout", "knockout", "deletion", "knock-out"]
}
STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from",
    "in", "is", "of", "on", "or", "the", "to", "via", "was", "were",
    "with",
}


def atomic_values(value):
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    if isinstance(value, (int, float)):
        return [str(value)]
    if isinstance(value, list):
        result = []
        for item in value:
            result.extend(atomic_values(item))
        return result
    if isinstance(value, dict):
        if value.get("reported_text"):
            return [str(value["reported_text"])]
        result = []
        for key, item in value.items():
            if key in {"purpose", "basis", "notes"} and item is None:
                continue
            result.extend(atomic_values(item))
        return result
    return [str(value)]


def supports_value(value, quotes):
    text = _normalize(" ".join(quotes))
    atoms = [v for v in atomic_values(value) if _meaningful(v)]
    if not atoms:
        return False, []
    unsupported = []
    for atom in atoms:
        normalized = _normalize(atom)
        aliases = ALIASES.get(normalized, [normalized])
        if not any(alias in text for alias in aliases):
            if normalized.isdigit() and _number_word(normalized) in text:
                continue
            if not _anchored_paraphrase_supported(normalized, text):
                unsupported.append(atom)
    return not unsupported, unsupported


def match_score(value, text):
    atoms = [v for v in atomic_values(value) if _meaningful(v)]
    if not atoms:
        return 0
    normalized_text = _normalize(text)
    score = 0.0
    for atom in atoms:
        normalized_atom = _normalize(atom)
        aliases = ALIASES.get(normalized_atom, [normalized_atom])
        if any(alias in normalized_text for alias in aliases):
            score += 1.0
            continue
        score += _token_overlap(normalized_atom, normalized_text)
    return score


def _meaningful(value):
    normalized = _normalize(value)
    return len(normalized) >= 2 and normalized not in {"reported", "control", "experimental", "unspecified"}


def _normalize(value):
    return re.sub(r"\s+", " ", re.sub(r"[^\w.°℃μµΔ=-]+", " ", str(value).casefold())).strip()


def _number_word(value):
    return {"2": "two", "3": "three", "4": "four", "5": "five"}.get(value, value)


def _anchored_paraphrase_supported(value, evidence_text):
    """Accept concise paraphrases only when their anchored text agrees.

    Skill07 intentionally emits compact values instead of copying long quotes.
    Exact-substring validation therefore rejected correct summaries even when
    their paragraph ID existed. Require all reported numbers plus substantial
    distinctive-token overlap; this remains stricter than keyword presence
    while allowing harmless grammatical normalization.
    """
    tokens = [
        token for token in re.findall(r"[\w.°℃μµΔ=-]+", value)
        if len(token) >= 2 and token not in STOPWORDS
    ]
    if len(tokens) < 3:
        return False
    evidence_tokens = set(re.findall(r"[\w.°℃μµΔ=-]+", evidence_text))
    numbers = re.findall(r"(?<![A-Za-z])\d+(?:\.\d+)?(?![A-Za-z])", value)
    if numbers and not all(number in evidence_text for number in numbers):
        return False
    matched = sum(token in evidence_tokens for token in tokens)
    return matched >= 2 and matched / len(tokens) >= 0.45


def _token_overlap(value, evidence_text):
    tokens = [
        token for token in re.findall(r"[\w.°℃μµΔ=-]+", value)
        if len(token) >= 2 and token not in STOPWORDS
    ]
    if len(tokens) < 3:
        return 0.0
    evidence_tokens = set(re.findall(r"[\w.°℃μµΔ=-]+", evidence_text))
    matched = sum(token in evidence_tokens for token in tokens)
    ratio = matched / len(tokens)
    return ratio if matched >= 2 and ratio >= 0.25 else 0.0

import re

from .evidence_validator import atomic_values, match_score


def minimal_quote(value, text):
    sentences = [v.strip() for v in re.split(r"(?<=[.!?。；;])\s+", text) if v.strip()]
    if not sentences:
        return text.strip()
    ranked = sorted(sentences, key=lambda sentence: (match_score(value, sentence), -len(sentence)), reverse=True)
    return ranked[0] if match_score(value, ranked[0]) > 0 else text.strip()


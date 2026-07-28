import json
import re


ALIASES = {
    "escherichia coli": ["escherichia coli", "e. coli", "e coli"],
    "gene knockout": ["gene knockout", "knockout", "deletion", "knock-out"]
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
            unsupported.append(atom)
    return not unsupported, unsupported


def match_score(value, text):
    atoms = [v for v in atomic_values(value) if _meaningful(v)]
    if not atoms:
        return 0
    normalized_text = _normalize(text)
    return sum(any(alias in normalized_text for alias in ALIASES.get(_normalize(atom), [_normalize(atom)])) for atom in atoms)


def _meaningful(value):
    normalized = _normalize(value)
    return len(normalized) >= 2 and normalized not in {"reported", "control", "experimental", "unspecified"}


def _normalize(value):
    return re.sub(r"\s+", " ", re.sub(r"[^\w.°℃μµΔ=-]+", " ", str(value).casefold())).strip()


def _number_word(value):
    return {"2": "two", "3": "three", "4": "four", "5": "five"}.get(value, value)


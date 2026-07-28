import re

from .common import unique

GROUP = re.compile(r"\b(?:wild[- ]type|WT|control(?:\s+group)?|untreated|vehicle|mutant|engineered\s+strain|treated(?:\s+group)?)\b", re.I)


def extract_groups_controls(items):
    groups, controls, candidates = [], [], []
    for item in items:
        matches = GROUP.findall(item["text"])
        if not matches:
            continue
        candidates.append(item)
        for name in matches:
            control = bool(re.search(r"wild[- ]type|^WT$|control|untreated|vehicle", name, re.I))
            groups.append({"name": name, "type": "control" if control else "experimental"})
            if control:
                purpose_match = re.search(rf"{re.escape(name)}[^.;]{{0,80}}(?:served|used)\s+as\s+(?:a\s+)?([^.;]+control[^.;]*)", item["text"], re.I)
                controls.append({"name": name, "purpose": purpose_match.group(1).strip() if purpose_match else None})
    return unique_dicts(groups, "name"), unique_dicts(controls, "name"), candidates


def unique_dicts(values, key):
    seen, result = set(), []
    for value in values:
        normalized = value[key].casefold()
        if normalized not in seen:
            seen.add(normalized)
            result.append(value)
    return result


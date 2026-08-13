import re


SECTION_PRIORITY = {
    "materials and methods": 0, "methods": 0, "experimental procedures": 0,
    "supplementary methods": 1, "results": 2, "figure": 3, "table": 3,
    "abstract": 4, "introduction": 5, "discussion": 6
}


def paragraphs(clean_json):
    sections = {v["id"]: v for v in clean_json.get("sections", [])}
    result = []
    for item in clean_json.get("paragraphs", []):
        section = sections.get(item.get("section"), {})
        title = section.get("title", "")
        result.append({
            "paragraph_id": item["paragraph_id"], "text": item["text"],
            "section_id": item.get("section"), "section": title,
            "priority": _priority(title)
        })
    for figure in clean_json.get("figures", []):
        if figure.get("caption") and figure["caption"] != "unknown":
            result.append({
                "paragraph_id": "figure:" + figure["figure_id"], "text": figure["caption"],
                "section_id": None, "section": figure["figure_id"], "priority": 3
            })
    for table in clean_json.get("tables", []):
        title = table.get("title")
        if title and title != "unknown":
            result.append({
                "paragraph_id": "table:" + table["table_id"], "text": title,
                "section_id": None, "section": table["table_id"], "priority": 3
            })
    return sorted(result, key=lambda v: v["priority"])


def find_candidates(items, patterns, sections=None):
    compiled = [re.compile(pattern, re.I) for pattern in patterns]
    result = []
    for item in items:
        if sections and not any(value in item["section"].casefold() for value in sections):
            continue
        if any(pattern.search(item["text"]) for pattern in compiled):
            result.append(item)
    return result


def sentences(text):
    return [v.strip() for v in re.split(r"(?<=[.!?。；;])\s+", text) if v.strip()]


def matching_sentences(candidate, patterns):
    compiled = [re.compile(v, re.I) for v in patterns]
    return [sentence for sentence in sentences(candidate["text"]) if any(p.search(sentence) for p in compiled)]


def metadata(candidates):
    return [{
        "source_location": {
            "section": v["section"], "paragraph": v["paragraph_id"],
            "figure": v["section"] if v["paragraph_id"].startswith("figure:") else None,
            "table": v["section"] if v["paragraph_id"].startswith("table:") else None
        },
        "quote": v["text"], "extraction_method": "rule_based"
    } for v in candidates]


def unique(values):
    seen, result = set(), []
    for value in values:
        key = str(value).casefold()
        if key not in seen:
            seen.add(key)
            result.append(value)
    return result


def _priority(title):
    lowered = title.casefold()
    for key, priority in SECTION_PRIORITY.items():
        if key in lowered:
            return priority
    return 10


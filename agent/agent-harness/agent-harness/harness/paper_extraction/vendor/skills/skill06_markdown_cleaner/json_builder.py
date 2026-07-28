import re


HEADING = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
FIGURE = re.compile(r"(?im)^(?:#{1,6}\s*)?(Fig(?:ure)?\.?\s*S?\d+[A-Za-z]?)\s*[:.\-]?\s*(.*)$")
TABLE = re.compile(r"(?im)^(?:#{1,6}\s*)?(Table\s+S?\d+[A-Za-z]?)\s*[:.\-]?\s*(.*)$")


def build_clean_json(markdown, metadata, cleaning_history):
    lines = markdown.splitlines()
    sections = []
    current = None
    for index, line in enumerate(lines):
        match = HEADING.match(line)
        if match:
            if current:
                current["content"] = "\n".join(current.pop("_lines")).strip()
            section_id = _unique_id(_slug(match.group(2)), {v["id"] for v in sections})
            current = {
                "id": section_id, "title": match.group(2).strip(),
                "level": len(match.group(1)), "_lines": []
            }
            sections.append(current)
        elif current:
            current["_lines"].append(line)
    if current:
        current["content"] = "\n".join(current.pop("_lines")).strip()

    paragraphs = []
    for section in sections:
        blocks = re.split(r"\n\s*\n", section["content"])
        for block in blocks:
            text = block.strip()
            if not text or _is_table_block(text):
                continue
            paragraphs.append({
                "paragraph_id": f"{section['id']}_p{sum(v['section'] == section['id'] for v in paragraphs) + 1:03d}",
                "text": text, "section": section["id"]
            })

    figures = []
    for match in FIGURE.finditer(markdown):
        figure_id = re.sub(r"\s+", " ", match.group(1)).strip()
        figures.append({
            "figure_id": figure_id, "caption": match.group(2).strip() or "unknown",
            "related_paragraphs": [
                p["paragraph_id"] for p in paragraphs
                if re.search(rf"\b(?:Fig(?:ure)?\.?)\s*{re.escape(_number(figure_id))}\b", p["text"], re.I)
            ]
        })
    figures = _deduplicate(figures, "figure_id")

    tables = []
    for match in TABLE.finditer(markdown):
        table_id = match.group(1).strip()
        following = markdown[match.end():match.end() + 2000]
        table_lines = []
        for line in following.splitlines():
            if "|" in line:
                table_lines.append(line)
            elif table_lines:
                break
            elif line.strip():
                break
        rows = [
            [cell.strip() for cell in line.strip().strip("|").split("|")]
            for line in table_lines
            if not re.match(r"^\s*\|\s*:?-+", line)
        ]
        tables.append({
            "table_id": table_id, "title": match.group(2).strip() or "unknown",
            "content": rows
        })
    tables = _deduplicate(tables, "table_id")

    citations = []
    for index, match in enumerate(re.finditer(r"\[(\d+(?:\s*[-,]\s*\d+)*)\]", markdown), 1):
        citations.append({
            "citation_id": f"citation_{index:04d}", "text": match.group(0),
            "target_reference": re.findall(r"\d+", match.group(1)),
            "char_offset": match.start()
        })
    return {
        "document_metadata": metadata,
        "sections": sections,
        "paragraphs": paragraphs,
        "figures": figures,
        "tables": tables,
        "citations": citations,
        "cleaning_metadata": {"cleaning_history": cleaning_history}
    }


def _slug(value):
    slug = re.sub(r"[^a-z0-9\u4e00-\u9fff]+", "_", value.casefold()).strip("_")
    return slug or "section"


def _unique_id(base, used):
    candidate, index = base, 2
    while candidate in used:
        candidate = f"{base}_{index}"
        index += 1
    return candidate


def _number(identifier):
    match = re.search(r"S?\d+[A-Za-z]?", identifier, re.I)
    return match.group(0) if match else identifier


def _is_table_block(text):
    lines = text.splitlines()
    return len(lines) >= 2 and all("|" in line for line in lines)


def _deduplicate(items, key):
    seen, result = set(), []
    for item in items:
        normalized = item[key].casefold()
        if normalized not in seen:
            seen.add(normalized)
            result.append(item)
    return result


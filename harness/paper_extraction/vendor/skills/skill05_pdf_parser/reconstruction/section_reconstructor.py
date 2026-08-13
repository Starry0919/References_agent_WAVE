import re


def reconstruct_sections(markdown, content_list=None):
    sections = []
    for line_number, line in enumerate(markdown.splitlines(), 1):
        match = re.match(r"^(#{1,6})\s+(.+?)\s*$", line)
        if match:
            title = match.group(2).strip()
            lowered = title.casefold()
            section_type = "supplement" if "supplement" in lowered else (
                "references" if lowered in {"references", "bibliography"} else "section"
            )
            sections.append({
                "section_id": f"sec_{len(sections) + 1}", "title": title,
                "level": len(match.group(1)), "type": section_type,
                "line": line_number
            })
    if not sections and content_list:
        for item in content_list:
            if item.get("type") == "text" and item.get("text_level"):
                sections.append({
                    "section_id": f"sec_{len(sections) + 1}",
                    "title": item.get("text", "unknown"),
                    "level": int(item["text_level"]), "type": "section",
                    "page": int(item.get("page_idx", 0)) + 1
                })
    return sections


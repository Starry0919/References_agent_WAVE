import re


TABLE_PATTERN = re.compile(r"(?im)^(?:#{1,6}\s*)?(Table\s+S?\d+[A-Za-z]?)\s*[:.\-]?\s*(.*)$")


def extract_tables(markdown, content_list=None):
    tables = [{
        "id": m.group(1), "caption": m.group(2).strip() or "unknown",
        "location": {"char_offset": m.start()},
        "markdown_preserved": _near_markdown_table(markdown, m.end())
    } for m in TABLE_PATTERN.finditer(markdown)]
    if content_list:
        for item in content_list:
            if item.get("type") == "table":
                caption = item.get("table_caption") or item.get("caption") or []
                if isinstance(caption, list):
                    caption = " ".join(map(str, caption))
                match = re.search(r"Table\s+S?\d+[A-Za-z]?", str(caption), re.I)
                table_id = match.group(0) if match else f"Table unknown-{len(tables) + 1}"
                if not any(v["id"].casefold() == table_id.casefold() for v in tables):
                    tables.append({
                        "id": table_id, "caption": str(caption) or "unknown",
                        "location": {"page": int(item.get("page_idx", 0)) + 1, "bbox": item.get("bbox")},
                        "markdown_preserved": bool(item.get("table_body"))
                    })
    return tables


def _near_markdown_table(markdown, offset):
    block = markdown[offset:offset + 300]
    return bool(re.search(r"(?m)^\s*\|.+\|\s*$", block))


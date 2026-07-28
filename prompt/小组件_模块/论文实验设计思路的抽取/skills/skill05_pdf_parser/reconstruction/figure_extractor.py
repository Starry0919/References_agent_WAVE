import re


FIGURE_PATTERN = re.compile(r"(?im)^(?:#{1,6}\s*)?(Fig(?:ure)?\.?\s*S?\d+[A-Za-z]?)\s*[:.\-]?\s*(.*)$")


def extract_figures(markdown, content_list=None):
    figures = []
    for match in FIGURE_PATTERN.finditer(markdown):
        figure_id = re.sub(r"\s+", " ", match.group(1)).strip()
        caption = match.group(2).strip()
        figures.append({
            "id": figure_id, "caption": caption or "unknown",
            "location": {"char_offset": match.start()},
            "related_text": _related_mentions(markdown, figure_id, match.start())
        })
    if content_list:
        for item in content_list:
            if item.get("type") in {"image", "figure"}:
                caption = item.get("img_caption") or item.get("caption") or []
                if isinstance(caption, list):
                    caption = " ".join(map(str, caption))
                candidate_id = _caption_id(str(caption)) or f"Figure unknown-{len(figures) + 1}"
                if not any(v["id"].casefold() == candidate_id.casefold() for v in figures):
                    figures.append({
                        "id": candidate_id, "caption": str(caption) or "unknown",
                        "location": {"page": int(item.get("page_idx", 0)) + 1, "bbox": item.get("bbox")},
                        "related_text": []
                    })
    return figures


def _caption_id(caption):
    match = re.search(r"Fig(?:ure)?\.?\s*S?\d+[A-Za-z]?", caption, re.I)
    return match.group(0) if match else None


def _related_mentions(markdown, figure_id, caption_offset):
    number = re.search(r"S?\d+[A-Za-z]?", figure_id, re.I)
    if not number:
        return []
    pattern = re.compile(rf"\b(?:Fig(?:ure)?\.?)\s*{re.escape(number.group(0))}\b", re.I)
    return [{"char_offset": m.start(), "text": m.group(0)} for m in pattern.finditer(markdown) if abs(m.start() - caption_offset) > 5]


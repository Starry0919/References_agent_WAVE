"""Step03 - parse raw text into structurally-anchored blocks.

Only a Markdown-flavoured plain-text parser is implemented in this phase
(no PDF/OCR/image pipeline yet - see README "Phase roadmap"). Every block
keeps a stable block_id and section_path so Step09 evidence binding can
re-locate the exact excerpt it cites, and figures/tables are kept as first
class blocks rather than dropped (SKILL.md Step03 requirement 2).
"""
from __future__ import annotations

import re

VERSION = "0.1.0"

_MD_HEADING = re.compile(r"^(#{1,6})\s+(.*)$")
_CHAPTER = re.compile(r"^(chapter\s+\S+|第[一二三四五六七八九十百零\d]+章)", re.IGNORECASE)
_FIGURE = re.compile(r"^(figure|fig\.)\s*\S*[:：]?", re.IGNORECASE)
_FIGURE_ZH = re.compile(r"^图\s*\S*[:：]?")
_TABLE = re.compile(r"^table\s*\S*[:：]?", re.IGNORECASE)
_TABLE_ZH = re.compile(r"^表\s*\S*[:：]?")
_DEFBOX = re.compile(r"^(\*\*definition|definition[:：]|box\s+\S+|定义[:：]|专栏)", re.IGNORECASE)
_PAGE_MARK = re.compile(r"^\[\[page:(\d+)\]\]$")
_SUMMARY_WORDS = ("summary", "小结", "本章小结")
_EXERCISE_WORDS = ("exercise", "习题", "练习")
_REFERENCE_WORDS = ("references", "bibliography", "参考文献")
_CJK = re.compile(r"[一-鿿]")


def _lang(text):
    if not text.strip():
        return "unknown"
    cjk = len(_CJK.findall(text))
    return "zh" if cjk / max(len(text), 1) > 0.15 else "en"


def _classify_heading(text):
    low = text.lower()
    if any(w in low for w in _SUMMARY_WORDS):
        return "summary"
    if any(w in low for w in _EXERCISE_WORDS):
        return "exercise"
    if any(w in low for w in _REFERENCE_WORDS):
        return "reference"
    if _CHAPTER.match(text):
        return "chapter"
    return "section"


def execute(request, **kwargs):
    vs = request["validated_source"]
    source_id = vs["source_id"]
    raw_text = request.get("raw_text", "") or ""

    if not raw_text.strip():
        return {
            "output": {"source_id": source_id, "blocks": []},
            "status": "retryable_failure",
            "errors": [{"code": "PARSING_ERROR", "message": f"{source_id}: raw_text is empty; nothing to parse.", "retryable": True, "source_id": source_id}],
            "provenance": {"step_version": VERSION, "source_ids": [source_id]},
        }

    blocks = []
    heading_stack = []  # list of (level, text)
    chapter_id = "unknown_chapter"
    current_page = None
    reading_order = 0
    paragraph_buffer = []

    def flush_paragraph():
        nonlocal reading_order
        text = "\n".join(paragraph_buffer).strip()
        paragraph_buffer.clear()
        if not text:
            return
        reading_order += 1
        block_type = "box" if _DEFBOX.match(text) else "paragraph"
        blocks.append({
            "block_id": f"{source_id}:b{reading_order}",
            "block_type": block_type,
            "chapter_id": chapter_id,
            "section_path": [h[1] for h in heading_stack],
            "page_start": current_page, "page_end": current_page,
            "text": text,
            "figure_or_table_label": "",
            "reading_order": reading_order,
            "language": _lang(text),
            "source_anchor": {"source_id": source_id, "chapter_id": chapter_id, "section_path": [h[1] for h in heading_stack], "page": current_page},
        })

    for raw_line in raw_text.splitlines():
        line = raw_line.strip()
        if not line:
            flush_paragraph()
            continue
        page_match = _PAGE_MARK.match(line)
        if page_match:
            flush_paragraph()
            current_page = int(page_match.group(1))
            continue
        heading_match = _MD_HEADING.match(line)
        if heading_match:
            flush_paragraph()
            level = len(heading_match.group(1))
            text = heading_match.group(2).strip()
            heading_stack[:] = [h for h in heading_stack if h[0] < level]
            heading_stack.append((level, text))
            btype = _classify_heading(text)
            if btype == "chapter" or level == 1:
                chapter_id = text
            reading_order += 1
            blocks.append({
                "block_id": f"{source_id}:b{reading_order}",
                "block_type": btype if btype != "section" or level > 1 else "section",
                "chapter_id": chapter_id,
                "section_path": [h[1] for h in heading_stack],
                "page_start": current_page, "page_end": current_page,
                "text": text, "figure_or_table_label": "",
                "reading_order": reading_order,
                "language": _lang(text),
                "source_anchor": {"source_id": source_id, "chapter_id": chapter_id, "section_path": [h[1] for h in heading_stack], "page": current_page},
            })
            continue
        is_figure = bool(_FIGURE.match(line) or _FIGURE_ZH.match(line))
        is_table = bool(_TABLE.match(line) or _TABLE_ZH.match(line))
        if is_figure or is_table:
            flush_paragraph()
            reading_order += 1
            label_match = re.match(r"^(\S+\s*\S*?)[:：]", line)
            blocks.append({
                "block_id": f"{source_id}:b{reading_order}",
                "block_type": "figure" if is_figure else "table",
                "chapter_id": chapter_id,
                "section_path": [h[1] for h in heading_stack],
                "page_start": current_page, "page_end": current_page,
                "text": line,
                "figure_or_table_label": label_match.group(1) if label_match else line[:20],
                "reading_order": reading_order,
                "language": _lang(line),
                "source_anchor": {"source_id": source_id, "chapter_id": chapter_id, "section_path": [h[1] for h in heading_stack], "page": current_page},
            })
            continue
        paragraph_buffer.append(raw_line)
    flush_paragraph()

    errors = []
    status = "succeeded"
    if not any(b["block_type"] in {"chapter", "section"} for b in blocks):
        status = "succeeded_with_warnings"
        errors.append({"code": "STRUCTURE_LOSS", "message": f"{source_id}: no chapter/section headings detected; treating the whole source as one flat section.", "retryable": False, "source_id": source_id, "recoverable": False})

    return {
        "output": {"source_id": source_id, "blocks": blocks},
        "status": status, "errors": errors,
        "provenance": {"step_version": VERSION, "source_ids": [source_id]},
    }

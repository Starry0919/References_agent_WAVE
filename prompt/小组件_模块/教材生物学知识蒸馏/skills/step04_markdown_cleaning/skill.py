"""Step04 - strip PDF page-boundary noise (repeated headers/footers, lone
page numbers, copyright lines) from Step03's reconstructed Markdown, before
Step05 parses it into blocks. Ported from 论文实验设计抽取/skills/
skill06_markdown_cleaner's header/footer heuristic, adapted to this
module's `[[page:N]]` page-marker convention instead of `<!-- page:N -->`.

Only runs the real heuristic when Step03 actually went through a PDF
parser (`used_pdf_parser=True`) - text a caller pasted directly has no PDF
page boundaries to speak of, and running a heuristic tuned for scanned-page
repetition on it would only risk deleting real content it was never meant
to touch.
"""
from __future__ import annotations

import re
from collections import Counter

VERSION = "0.1.0"

_PAGE_MARKER = re.compile(r"^\[\[page:\d+\]\]$")
_PAGE_NUMBER = re.compile(r"^\s*(?:page\s*)?\d+(?:\s+of\s+\d+)?\s*$", re.I)
_COPYRIGHT = re.compile(r"^\s*(?:©|copyright\b).*$", re.I)
_DOI_LINE = re.compile(r"^\s*(?:https?://doi\.org/|doi:\s*)10\.\d{4,9}/\S+\s*$", re.I)
_REFERENCES_HEADING = re.compile(r"^#{1,6}\s+(?:References|Bibliography|参考文献)\s*$", re.I)


def _clean_headers_footers(markdown):
    """Returns (clean_markdown, noise_removed_count, modification_log)."""
    lines = markdown.splitlines()
    pages, page_ranges, current, page_start = [], [], [], 0
    for i, line in enumerate(lines):
        if _PAGE_MARKER.match(line):
            if current:
                pages.append(current)
                page_ranges.append((page_start, i - 1))
            current = []
            page_start = i + 1
        else:
            current.append(line)
    if current:
        pages.append(current)
        page_ranges.append((page_start, len(lines) - 1))

    boundary_counts = Counter()
    boundary_line_indices = set()
    for _page, (start, end) in zip(pages, page_ranges):
        content_with_index = [
            (idx, v) for idx, v in zip(range(start, end + 1), lines[start:end + 1])
            if v.strip() and not _PAGE_MARKER.match(v)
        ]
        content = [v for _, v in content_with_index]
        boundary_counts.update(set(content[:2] + content[-2:]))
        boundary_line_indices.update(idx for idx, _ in content_with_index[:2] + content_with_index[-2:])
    repeated = {line for line, count in boundary_counts.items() if count >= 2 and len(line) < 180 and len(pages) >= 2}

    output, modification_log = [], []
    in_references = False
    for index, line in enumerate(lines, 1):
        if _REFERENCES_HEADING.match(line):
            in_references = True
        removable = (
            (_PAGE_NUMBER.match(line) and (index - 1) in boundary_line_indices)
            or _COPYRIGHT.match(line)
            or (line in repeated and (_DOI_LINE.match(line) or not in_references))
        )
        if removable and not _PAGE_MARKER.match(line):
            modification_log.append({"line": index, "removed_text": line, "reason": "repeated_page_boundary_or_page_number_or_copyright"})
        else:
            output.append(line)
    return "\n".join(output), len(modification_log), modification_log


def execute(request, **kwargs):
    source_id = request["source_id"]
    raw_markdown = request.get("raw_markdown", "") or ""
    used_pdf_parser = bool(request.get("used_pdf_parser"))

    if not raw_markdown.strip():
        return {
            "output": {"source_id": source_id, "clean_markdown": "", "noise_removed": 0, "modification_log": []},
            "status": "succeeded", "errors": [],
            "provenance": {"step_version": VERSION, "source_ids": [source_id]},
        }

    if not used_pdf_parser:
        return {
            "output": {"source_id": source_id, "clean_markdown": raw_markdown, "noise_removed": 0, "modification_log": []},
            "status": "succeeded", "errors": [],
            "provenance": {"step_version": VERSION, "source_ids": [source_id]},
        }

    clean_markdown, noise_removed, modification_log = _clean_headers_footers(raw_markdown)
    clean_markdown = clean_markdown.rstrip() + "\n"

    warnings = []
    if "�" in raw_markdown:
        warnings.append({"code": "OCR_UNCERTAIN", "message": f"{source_id}: unresolved replacement characters (�) were preserved from the PDF parse; review before trusting exact wording.", "retryable": False, "source_id": source_id})

    return {
        "output": {"source_id": source_id, "clean_markdown": clean_markdown, "noise_removed": noise_removed, "modification_log": modification_log},
        "status": "succeeded_with_warnings" if warnings else "succeeded", "errors": warnings,
        "provenance": {"step_version": VERSION, "source_ids": [source_id]},
    }

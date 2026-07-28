import re
from collections import Counter


PAGE_MARKER = re.compile(r"^\s*<!--\s*page\s*:\s*\d+\s*-->\s*$", re.I)
PAGE_NUMBER = re.compile(r"^\s*(?:page\s*)?\d+(?:\s+of\s+\d+)?\s*$", re.I)
COPYRIGHT = re.compile(r"^\s*(?:©|copyright\b).*$", re.I)
DOI_LINE = re.compile(r"^\s*(?:https?://doi\.org/|doi:\s*)10\.\d{4,9}/\S+\s*$", re.I)


def clean_headers_footers(markdown, tracker):
    lines = markdown.splitlines()
    pages, page_ranges, current, page_start = [], [], [], 0
    for i, line in enumerate(lines):
        if PAGE_MARKER.match(line):
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
    # Bare-number lines (equation numbers, orphaned list markers, a lone
    # numeric data value) are shape-identical to real page numbers but never
    # sit at a page boundary. Real page numbers can't be caught by exact-text
    # repetition either, since they increment per page - so track *position*
    # (first/last 2 non-blank lines of each page) instead of text identity.
    boundary_line_indices = set()
    for page, (start, end) in zip(pages, page_ranges):
        content_with_index = [
            (idx, v) for idx, v in zip(range(start, end + 1), lines[start:end + 1])
            if v.strip() and not PAGE_MARKER.match(v)
        ]
        content = [v for _, v in content_with_index]
        boundary_counts.update(set(content[:2] + content[-2:]))
        boundary_line_indices.update(idx for idx, _ in content_with_index[:2] + content_with_index[-2:])
    repeated = {
        line for line, count in boundary_counts.items()
        if count >= 2 and len(line) < 180 and len(pages) >= 2
    }
    output, removed = [], 0
    in_references = False
    for index, line in enumerate(lines, 1):
        if re.match(r"^#{1,6}\s+(?:References|Bibliography)\s*$", line, re.I):
            in_references = True
        removable = (
            (PAGE_NUMBER.match(line) and (index - 1) in boundary_line_indices)
            or COPYRIGHT.match(line)
            or (line in repeated and (DOI_LINE.match(line) or not in_references))
        )
        if removable and not PAGE_MARKER.match(line):
            tracker.add("remove_header_footer", f"line:{index}", line, "", "repeated page-boundary artifact")
            removed += 1
        else:
            output.append(line)
    return "\n".join(output), removed

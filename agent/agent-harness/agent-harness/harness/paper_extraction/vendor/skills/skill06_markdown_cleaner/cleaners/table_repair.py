import re


SEPARATOR_CELL = re.compile(r"^:?-{3,}:?$")


def repair_tables(markdown, tracker):
    lines = markdown.splitlines()
    output, warnings, fixed = [], [], 0
    index = 0
    while index < len(lines):
        if "|" not in lines[index] or lines[index].lstrip().startswith("```"):
            output.append(lines[index])
            index += 1
            continue
        start = index
        block = []
        while index < len(lines) and "|" in lines[index] and lines[index].strip():
            block.append(lines[index])
            index += 1
        rows = [_cells(line) for line in block]
        widths = {len(row) for row in rows}
        if len(block) < 2 or len(widths) != 1 or next(iter(widths)) < 2:
            output.extend(block)
            warnings.append({"location": f"line:{start + 1}", "reason": "inconsistent table columns"})
            continue
        normalized = [_format(row) for row in rows]
        if not _is_separator(rows[1]):
            normalized.insert(1, _format(["---"] * len(rows[0])))
        for offset, original in enumerate(block):
            cleaned_index = offset if _is_separator(rows[1]) else offset + (1 if offset > 0 else 0)
            cleaned = normalized[cleaned_index]
            tracker.add("table_fix", f"line:{start + offset + 1}", original, cleaned, "normalize Markdown table pipes")
        if not _is_separator(rows[1]):
            tracker.add("table_fix", f"line:{start + 2}", "", normalized[1], "insert Markdown separator row")
        output.extend(normalized)
        fixed += 1
    return "\n".join(output), fixed, warnings


def _cells(line):
    stripped = line.strip().strip("|")
    return [cell.strip() for cell in stripped.split("|")]


def _format(cells):
    return "| " + " | ".join(cells) + " |"


def _is_separator(cells):
    return all(SEPARATOR_CELL.match(cell) for cell in cells)


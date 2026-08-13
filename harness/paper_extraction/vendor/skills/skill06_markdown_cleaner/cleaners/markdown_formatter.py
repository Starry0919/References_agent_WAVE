import re


def normalize_markdown_structure(markdown, tracker):
    lines = markdown.splitlines()
    previous_level = 0
    output = []
    for index, line in enumerate(lines, 1):
        match = re.match(r"^(#{1,6})\s*(.+?)\s*$", line)
        if not match:
            output.append(line.rstrip())
            continue
        level = len(match.group(1))
        if previous_level and level > previous_level + 1:
            level = previous_level + 1
        cleaned = "#" * level + " " + match.group(2).strip()
        tracker.add("heading_level_fix", f"line:{index}", line, cleaned, "prevent invalid heading-level jump")
        output.append(cleaned)
        previous_level = level
    text = "\n".join(output)
    compact = re.sub(r"\n{4,}", "\n\n\n", text)
    if compact != text:
        tracker.add("blank_line_normalization", "document", text, compact, "collapse excessive blank lines")
    return compact.strip() + "\n"


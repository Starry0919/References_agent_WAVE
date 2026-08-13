import re


def extract_references(markdown, sections):
    reference_section = next((v for v in sections if v["type"] == "references"), None)
    references = []
    if reference_section:
        lines = markdown.splitlines()[reference_section["line"]:]
        for line in lines:
            match = re.match(r"^\s*(?:\[(\d+)\]|(\d+)[.)])\s+(.+)", line)
            if match:
                references.append({"id": match.group(1) or match.group(2), "text": match.group(3).strip()})
    links = []
    for match in re.finditer(r"\[(\d+(?:\s*[-,]\s*\d+)*)\]", markdown):
        links.append({"citation": match.group(0), "char_offset": match.start(), "reference_ids": re.findall(r"\d+", match.group(1))})
    supplements = [v for v in sections if v["type"] == "supplement"]
    return {"references": references, "citation_links": links, "supplements": supplements}


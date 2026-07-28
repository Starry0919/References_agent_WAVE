from pathlib import Path
import re

import pdfplumber


SOURCE = Path(r"D:\Users\Starry\Desktop\agent\reference\Q1_workflow-agent")


def clean_page(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"(?<=\w)-\n(?=[a-z])", "", text)
    lines = [line.rstrip() for line in text.splitlines()]
    out = []
    blank = False
    for line in lines:
        if not line.strip():
            if not blank:
                out.append("")
            blank = True
            continue
        blank = False
        out.append(line)
    return "\n".join(out).strip()


def convert(pdf_path: Path) -> tuple[Path, int, int]:
    parts = []
    with pdfplumber.open(pdf_path) as pdf:
        page_count = len(pdf.pages)
        for index, page in enumerate(pdf.pages, start=1):
            text = clean_page(page.extract_text(x_tolerance=1.0, y_tolerance=3.0) or "")
            parts.append(f"<!-- Page {index} -->\n\n{text}")
    body = "\n\n---\n\n".join(parts).rstrip() + "\n"
    output = pdf_path.with_suffix(".md")
    output.write_text(body, encoding="utf-8")
    return output, page_count, len(body)


for source in sorted(SOURCE.glob("*.pdf")):
    output, pages, chars = convert(source)
    print(f"{source.name} -> {output.name}: {pages} pages, {chars} chars")

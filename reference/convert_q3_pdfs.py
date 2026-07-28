from pathlib import Path
import pdfplumber


ROOT = Path(r"D:\Users\Starry\Desktop\agent\reference\Q3_bottleneck")


def clean_text(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = [line.rstrip() for line in text.splitlines()]
    cleaned: list[str] = []
    previous_blank = False
    for line in lines:
        blank = not line.strip()
        if blank and previous_blank:
            continue
        cleaned.append(line)
        previous_blank = blank
    return "\n".join(cleaned).strip()


def convert(pdf_path: Path) -> tuple[Path, int, int]:
    pages: list[str] = []
    with pdfplumber.open(pdf_path) as document:
        for number, page in enumerate(document.pages, start=1):
            text = page.extract_text(x_tolerance=1.0, y_tolerance=3.0) or ""
            pages.append(f"<!-- Page {number} -->\n\n{clean_text(text)}")
    markdown = "\n\n---\n\n".join(pages).rstrip() + "\n"
    output = pdf_path.with_suffix(".md")
    output.write_text(markdown, encoding="utf-8")
    return output, len(pages), len(markdown)


for pdf in sorted(ROOT.glob("*.pdf")):
    output, page_count, char_count = convert(pdf)
    print(f"{pdf.name} -> {output.name}: {page_count} pages, {char_count} chars")

from pathlib import Path

from .parser_interface import ParseResult, ParserUnavailable


class PyMuPdfParser:
    name = "PyMuPDF"
    version = "runtime"

    def parse(self, pdf_path: Path, output_root: Path, mode="fallback", timeout_seconds=300):
        try:
            import fitz
        except ImportError as exc:
            raise ParserUnavailable("PyMuPDF is not installed") from exc
        output_root.mkdir(parents=True, exist_ok=True)
        document = fitz.open(str(pdf_path))
        pages = []
        for index, page in enumerate(document):
            pages.append(f"<!-- page:{index + 1} -->\n\n" + page.get_text("text"))
        markdown = output_root / f"{pdf_path.stem}.md"
        markdown.write_text("\n\n".join(pages), encoding="utf-8")
        return ParseResult(
            parser=self.name, parser_version=getattr(fitz, "VersionBind", self.version),
            mode="fallback", markdown_path=markdown, output_files=[markdown],
            command=["pymupdf", str(pdf_path)]
        )


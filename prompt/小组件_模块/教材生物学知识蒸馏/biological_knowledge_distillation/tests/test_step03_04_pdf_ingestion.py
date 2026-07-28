import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from helpers import FIXTURES  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parents[1].parent / "skills"))
from step03_pdf_parsing.parsers import ParseResult, ParserUnavailable, ParseFailure, reconstruct_markdown_from_content_list  # noqa: E402
from step03_pdf_parsing.skill import execute as step03  # noqa: E402
from step04_markdown_cleaning.skill import execute as step04  # noqa: E402

CONTENT_LIST = json.loads((FIXTURES / "mineru_content_list_sample.json").read_text(encoding="utf-8"))


class _StubParser:
    def __init__(self, name, behavior):
        self.name = name
        self._behavior = behavior  # "succeed" | "unavailable" | "fail"

    def parse(self, pdf_path, output_root, mode="pipeline", timeout_seconds=1800):
        if self._behavior == "unavailable":
            raise ParserUnavailable(f"{self.name} not installed")
        if self._behavior == "fail":
            raise ParseFailure(f"{self.name} crashed")
        markdown_path = Path(output_root)
        markdown_path.mkdir(parents=True, exist_ok=True)
        md_file = markdown_path / f"{pdf_path.stem}.md"
        md_file.write_text("stub markdown", encoding="utf-8")
        return ParseResult(parser=self.name, parser_version="stub", mode=mode, markdown_path=md_file, content_list=CONTENT_LIST, command=["stub"])


class ReconstructMarkdown(unittest.TestCase):
    def test_headings_paragraphs_figures_tables_and_page_markers(self):
        markdown = reconstruct_markdown_from_content_list(CONTENT_LIST)
        self.assertIn("# Chapter 7: Regulation of Metabolic Flux", markdown)
        self.assertIn("## 7.3 Feedback Inhibition", markdown)
        self.assertIn("Feedback inhibition is defined as", markdown)
        self.assertIn("Figure: Figure 7.4: End-product feedback inhibition on the first committed step.", markdown)
        self.assertIn("Table: Table 7.1: Representative feedback-inhibited enzymes.", markdown)
        self.assertIn("[[page:1]]", markdown)
        self.assertIn("[[page:2]]", markdown)
        # page 2 content must come after the page:2 marker, not before
        self.assertLess(markdown.index("[[page:2]]"), markdown.index("the end-product inhibits the first committed enzyme"))


class Step03PdfParsing(unittest.TestCase):
    def test_non_pdf_source_passes_through_unchanged(self):
        result = step03({"source_ref": {"source_ref_type": "text", "raw_text": "already clean markdown"}, "validated_source": {"source_id": "src_1"}})
        self.assertEqual(result["status"], "succeeded")
        self.assertFalse(result["output"]["used_pdf_parser"])
        self.assertEqual(result["output"]["raw_markdown"], "already clean markdown")

    def test_missing_pdf_path_is_retryable_access_blocked(self):
        result = step03({"source_ref": {"source_ref_type": "file", "path": "Z:/does/not/exist.pdf"}, "validated_source": {"source_id": "src_1"}})
        self.assertEqual(result["status"], "retryable_failure")
        self.assertEqual(result["errors"][0]["code"], "ACCESS_BLOCKED")

    def test_mineru_success_reconstructs_markdown_from_content_list(self):
        with tempfile.TemporaryDirectory() as d:
            pdf_path = Path(d) / "chapter7.pdf"
            pdf_path.write_bytes(b"%PDF-1.4 stub")
            result = step03(
                {"source_ref": {"source_ref_type": "file", "path": str(pdf_path)}, "validated_source": {"source_id": "src_1"}},
                mineru_parser=_StubParser("MinerU", "succeed"),
                fallback_parser=_StubParser("PyMuPDF", "unavailable"),
                output_root=Path(d) / "out",
            )
        self.assertEqual(result["status"], "succeeded")
        self.assertTrue(result["output"]["used_pdf_parser"])
        self.assertEqual(result["output"]["parser_name"], "MinerU")
        self.assertIn("# Chapter 7", result["output"]["raw_markdown"])
        self.assertEqual(result["output"]["page_count"], 2)

    def test_mineru_unavailable_falls_back_to_pymupdf_with_warning(self):
        with tempfile.TemporaryDirectory() as d:
            pdf_path = Path(d) / "chapter7.pdf"
            pdf_path.write_bytes(b"%PDF-1.4 stub")
            result = step03(
                {"source_ref": {"source_ref_type": "file", "path": str(pdf_path)}, "validated_source": {"source_id": "src_1"}},
                mineru_parser=_StubParser("MinerU", "unavailable"),
                fallback_parser=_StubParser("PyMuPDF", "succeed"),
                output_root=Path(d) / "out",
            )
        self.assertEqual(result["status"], "succeeded_with_warnings")
        self.assertEqual(result["output"]["parser_name"], "PyMuPDF")
        self.assertTrue(any(e["code"] == "OCR_UNCERTAIN" for e in result["errors"]))

    def test_both_parsers_unavailable_is_retryable_parsing_error(self):
        with tempfile.TemporaryDirectory() as d:
            pdf_path = Path(d) / "chapter7.pdf"
            pdf_path.write_bytes(b"%PDF-1.4 stub")
            result = step03(
                {"source_ref": {"source_ref_type": "file", "path": str(pdf_path)}, "validated_source": {"source_id": "src_1"}},
                mineru_parser=_StubParser("MinerU", "unavailable"),
                fallback_parser=_StubParser("PyMuPDF", "unavailable"),
                output_root=Path(d) / "out",
            )
        self.assertEqual(result["status"], "retryable_failure")
        self.assertEqual(result["errors"][0]["code"], "PARSING_ERROR")


class Step04MarkdownCleaning(unittest.TestCase):
    def test_pasted_text_source_is_never_touched(self):
        text = "[[page:1]]\nHeader Noise\nReal content here.\nHeader Noise\n[[page:2]]\nHeader Noise\nMore real content.\nHeader Noise"
        result = step04({"source_id": "src_1", "raw_markdown": text, "used_pdf_parser": False})
        self.assertEqual(result["output"]["clean_markdown"], text)
        self.assertEqual(result["output"]["noise_removed"], 0)

    def test_pdf_source_strips_repeated_headers_and_footers(self):
        text = (
            "[[page:1]]\nRunning Header\nReal content page one.\nRunning Header\n"
            "[[page:2]]\nRunning Header\nReal content page two.\nRunning Header\n"
        )
        result = step04({"source_id": "src_1", "raw_markdown": text, "used_pdf_parser": True})
        cleaned = result["output"]["clean_markdown"]
        self.assertNotIn("Running Header", cleaned)
        self.assertIn("Real content page one.", cleaned)
        self.assertIn("Real content page two.", cleaned)
        self.assertGreater(result["output"]["noise_removed"], 0)

    def test_single_page_pdf_text_is_left_alone(self):
        # the repetition heuristic requires >= 2 pages; a lone page must not
        # have its first/last lines stripped just for sitting at a boundary.
        text = "[[page:1]]\nUnique Title\nBody text.\nClosing line."
        result = step04({"source_id": "src_1", "raw_markdown": text, "used_pdf_parser": True})
        self.assertIn("Unique Title", result["output"]["clean_markdown"])
        self.assertIn("Closing line.", result["output"]["clean_markdown"])

    def test_empty_markdown_succeeds_trivially(self):
        result = step04({"source_id": "src_1", "raw_markdown": "", "used_pdf_parser": True})
        self.assertEqual(result["status"], "succeeded")
        self.assertEqual(result["output"]["clean_markdown"], "")


if __name__ == "__main__":
    unittest.main()

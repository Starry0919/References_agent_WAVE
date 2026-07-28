import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from skill import ScientificMarkdownCleaner
from helpers import document_artifact, fixed_clock


class CitationPreserveTest(unittest.TestCase):
    def test_inline_and_reference_citations_remain(self):
        markdown = """# Introduction

The method was reported previously [15] and confirmed later [16-18].

# References

[15] A. Author. Article DOI: 10.1000/example.
"""
        with tempfile.TemporaryDirectory(dir=ROOT / "tests") as directory:
            result = ScientificMarkdownCleaner(Path(directory), logger=lambda e: None, clock=fixed_clock).execute({"document_artifact": document_artifact(markdown)})
            cleaned = Path(result["output"]["clean_document_artifact"]["clean_markdown_path"]).read_text(encoding="utf-8")
            self.assertIn("[15]", cleaned)
            self.assertIn("[16-18]", cleaned)
            self.assertIn("10.1000/example", cleaned)
            self.assertTrue(result["output"]["cleaning_report"]["citations_preserved"])


if __name__ == "__main__":
    unittest.main()


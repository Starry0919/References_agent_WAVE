import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from skill import ScientificMarkdownCleaner
from helpers import document_artifact, fixed_clock


class HeaderRemoveTest(unittest.TestCase):
    def test_repeated_page_boundary_noise_is_removed(self):
        markdown = """<!-- page:1 -->
Journal Header
# Introduction
Cells were cultured at 37°C.
1
<!-- page:2 -->
Journal Header
# Methods
Incubation lasted 12 h.
2
"""
        with tempfile.TemporaryDirectory(dir=ROOT / "tests") as directory:
            result = ScientificMarkdownCleaner(Path(directory), logger=lambda e: None, clock=fixed_clock).execute({"document_artifact": document_artifact(markdown)})
            cleaned = Path(result["output"]["clean_document_artifact"]["clean_markdown_path"]).read_text(encoding="utf-8")
            self.assertNotIn("Journal Header", cleaned)
            self.assertNotRegex(cleaned, r"(?m)^1$")
            self.assertIn("37°C", cleaned)
            self.assertGreaterEqual(result["output"]["cleaning_report"]["noise_removed"], 3)


if __name__ == "__main__":
    unittest.main()


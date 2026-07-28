import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from skill import ScientificMarkdownCleaner
from helpers import document_artifact, fixed_clock


class NoHallucinationTest(unittest.TestCase):
    def test_cleaner_adds_no_scientific_words(self):
        markdown = """# Results

Yield increased under the reported condition.
"""
        with tempfile.TemporaryDirectory(dir=ROOT / "tests") as directory:
            result = ScientificMarkdownCleaner(Path(directory), logger=lambda e: None, clock=fixed_clock).execute({"document_artifact": document_artifact(markdown)})
            self.assertNotIn("Escherichia", str(result.get("output")))
            check = next(v for v in result["self_check"]["checks"] if v["name"] == "no_new_scientific_text")
            self.assertTrue(check["passed"])

    def test_empty_markdown_fails(self):
        with tempfile.TemporaryDirectory(dir=ROOT / "tests") as directory:
            result = ScientificMarkdownCleaner(Path(directory), logger=lambda e: None, clock=fixed_clock).execute({"document_artifact": document_artifact("  ")})
            self.assertEqual(result["status"], "terminal_failure")
            self.assertEqual(result["errors"][0]["local_code"], "CLEAN001")


if __name__ == "__main__":
    unittest.main()

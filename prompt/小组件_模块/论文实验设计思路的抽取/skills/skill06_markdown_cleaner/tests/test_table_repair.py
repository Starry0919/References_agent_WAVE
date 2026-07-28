import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from skill import ScientificMarkdownCleaner
from helpers import document_artifact, fixed_clock


class TableRepairTest(unittest.TestCase):
    def test_repairs_pipes_without_changing_cells(self):
        markdown = """# Materials and Methods

Table 1: Culture conditions
Strain | Temperature
K-12 | 37°C
MG1655 | 30°C
"""
        with tempfile.TemporaryDirectory(dir=ROOT / "tests") as directory:
            result = ScientificMarkdownCleaner(Path(directory), logger=lambda e: None, clock=fixed_clock).execute({"document_artifact": document_artifact(markdown)})
            self.assertNotEqual(result["status"], "terminal_failure")
            clean = Path(result["output"]["clean_document_artifact"]["clean_markdown_path"]).read_text(encoding="utf-8")
            self.assertIn("| Strain | Temperature |", clean)
            self.assertIn("| --- | --- |", clean)
            self.assertIn("| K-12 | 37°C |", clean)
            self.assertEqual(result["output"]["cleaning_report"]["tables_fixed"], 1)


if __name__ == "__main__":
    unittest.main()


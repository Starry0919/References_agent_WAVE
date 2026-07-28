import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from skill import ScientificMarkdownCleaner
from helpers import document_artifact, fixed_clock


class FigurePreserveTest(unittest.TestCase):
    def test_figure_and_table_identifiers_are_preserved(self):
        markdown = """# Results

As shown in Figure 1, yield increased.

Figure 1: Measured yield.

Table 2: Replicate results.

| Replicate | Value |
|---|---|
| 1 | 0.5 mM |
"""
        with tempfile.TemporaryDirectory(dir=ROOT / "tests") as directory:
            result = ScientificMarkdownCleaner(Path(directory), logger=lambda e: None, clock=fixed_clock).execute({"document_artifact": document_artifact(markdown)})
            doc = result["output"]["clean_document_artifact"]
            self.assertEqual(doc["figure_map"]["figures"][0]["figure_id"], "Figure 1")
            self.assertEqual(doc["table_map"]["tables"][0]["table_id"], "Table 2")
            self.assertTrue(doc["figure_map"]["figures"][0]["related_paragraphs"])


if __name__ == "__main__":
    unittest.main()


import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from skill import ScientificMarkdownCleaner
from helpers import document_artifact, fixed_clock


class ScientificValuePreserveTest(unittest.TestCase):
    def test_experimental_parameters_are_exact(self):
        markdown = """# Methods

Cells were cultured at 37°C for 12 h using 500 μL medium at 220 rpm, 0.5 mM inducer, and OD600 = 0.8.
The Δgene strain was regulated using CRISPRi.
"""
        protected = ["37°C", "12 h", "500 μL", "220 rpm", "0.5 mM", "OD600 = 0.8", "Δgene", "CRISPRi"]
        with tempfile.TemporaryDirectory(dir=ROOT / "tests") as directory:
            result = ScientificMarkdownCleaner(Path(directory), logger=lambda e: None, clock=fixed_clock).execute({"document_artifact": document_artifact(markdown)})
            cleaned = Path(result["output"]["clean_document_artifact"]["clean_markdown_path"]).read_text(encoding="utf-8")
            for value in protected:
                self.assertIn(value, cleaned)
            check = next(v for v in result["self_check"]["checks"] if v["name"] == "protected_scientific_values")
            self.assertTrue(check["passed"])


if __name__ == "__main__":
    unittest.main()


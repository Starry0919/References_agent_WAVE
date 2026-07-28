import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from skill import PdfStructureParsingSkill
from helpers import FakeMinerU, NeverUsedFallback, fixed_clock, make_artifact


class FigureDetectionTest(unittest.TestCase):
    def test_caption_and_text_reference_are_linked(self):
        with tempfile.TemporaryDirectory(dir=ROOT / "tests") as directory:
            root = Path(directory)
            result = PdfStructureParsingSkill(FakeMinerU(), NeverUsedFallback(), root / "out", logger=lambda e: None, clock=fixed_clock).execute({"paper_artifact": make_artifact(root)})
            figures = result["output"]["document_artifact"]["figure_map"]["figures"]
            self.assertEqual(len(figures), 1)
            self.assertIn("Production", figures[0]["caption"])
            self.assertTrue(figures[0]["related_text"])


if __name__ == "__main__":
    unittest.main()


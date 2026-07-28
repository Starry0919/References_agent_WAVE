import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from skill import PdfStructureParsingSkill
from helpers import FakeMinerU, NeverUsedFallback, fixed_clock, make_artifact


class TableDetectionTest(unittest.TestCase):
    def test_table_number_caption_and_body_are_preserved(self):
        with tempfile.TemporaryDirectory(dir=ROOT / "tests") as directory:
            root = Path(directory)
            result = PdfStructureParsingSkill(FakeMinerU(), NeverUsedFallback(), root / "out", logger=lambda e: None, clock=fixed_clock).execute({"paper_artifact": make_artifact(root)})
            tables = result["output"]["document_artifact"]["table_map"]["tables"]
            self.assertEqual(tables[0]["id"], "Table 1")
            self.assertTrue(tables[0]["markdown_preserved"])
            references = result["output"]["document_artifact"]["reference_map"]["references"]
            self.assertEqual(references[0]["id"], "1")


if __name__ == "__main__":
    unittest.main()


import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from skill import PdfStructureParsingSkill
from helpers import FakeMinerU, NeverUsedFallback, fixed_clock, make_artifact


class SectionDetectionTest(unittest.TestCase):
    def test_methods_hierarchy_and_supplement_are_preserved(self):
        with tempfile.TemporaryDirectory(dir=ROOT / "tests") as directory:
            root = Path(directory)
            result = PdfStructureParsingSkill(FakeMinerU(), NeverUsedFallback(), root / "out", logger=lambda e: None, clock=fixed_clock).execute({"paper_artifact": make_artifact(root)})
            sections = result["output"]["document_artifact"]["structure_map"]["sections"]
            methods = next(v for v in sections if v["title"] == "Materials and Methods")
            subsection = next(v for v in sections if v["title"] == "2.1 Strain construction")
            self.assertEqual(methods["level"], 1)
            self.assertEqual(subsection["level"], 2)
            supplements = result["output"]["document_artifact"]["reference_map"]["supplements"]
            self.assertEqual(supplements[0]["title"], "Supplementary Methods")


if __name__ == "__main__":
    unittest.main()


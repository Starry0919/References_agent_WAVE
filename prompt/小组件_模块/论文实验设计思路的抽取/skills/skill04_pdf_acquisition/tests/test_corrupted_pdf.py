import copy
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from skill import PdfAcquisitionSkill
from helpers import CANDIDATE, FakeDownloader, fixed_clock


class CorruptedPdfTest(unittest.TestCase):
    def test_missing_eof_is_rejected(self):
        with tempfile.TemporaryDirectory(dir=ROOT / "tests") as directory:
            skill = PdfAcquisitionSkill(Path(directory), [FakeDownloader(b"%PDF-1.4\nbroken")], logger=lambda e: None, clock=fixed_clock)
            result = skill.execute({"accepted_candidates": [copy.deepcopy(CANDIDATE)]})
            self.assertEqual(result["output"]["paper_artifacts"], [])
            self.assertEqual(result["output"]["failed_items"][0]["error"]["local_code"], "PDF002")


if __name__ == "__main__":
    unittest.main()


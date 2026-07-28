import copy
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from skill import PdfAcquisitionSkill
from helpers import CANDIDATE, FakeDownloader, fixed_clock


class DownloadSuccessTest(unittest.TestCase):
    def test_verified_candidate_creates_artifact(self):
        with tempfile.TemporaryDirectory(dir=ROOT / "tests") as directory:
            skill = PdfAcquisitionSkill(Path(directory), [FakeDownloader()], logger=lambda e: None, clock=fixed_clock)
            result = skill.execute({"accepted_candidates": [copy.deepcopy(CANDIDATE)]})
            artifact = result["output"]["paper_artifacts"][0]
            self.assertEqual(result["status"], "succeeded")
            self.assertTrue(Path(artifact["file_information"]["path"]).is_file())
            self.assertEqual(artifact["processing_status"], "verified")
            self.assertEqual(len(artifact["integrity"]["checksum_value"]), 64)


if __name__ == "__main__":
    unittest.main()


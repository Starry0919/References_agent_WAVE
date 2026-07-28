import copy
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from artifact.checksum import verify_checksum
from skill import PdfAcquisitionSkill
from helpers import CANDIDATE, FakeDownloader, fixed_clock


class ChecksumTest(unittest.TestCase):
    def test_modification_is_detected(self):
        with tempfile.TemporaryDirectory(dir=ROOT / "tests") as directory:
            skill = PdfAcquisitionSkill(Path(directory), [FakeDownloader()], logger=lambda e: None, clock=fixed_clock)
            result = skill.execute({"accepted_candidates": [copy.deepcopy(CANDIDATE)]})
            artifact = result["output"]["paper_artifacts"][0]
            path = Path(artifact["file_information"]["path"])
            expected = artifact["integrity"]["checksum_value"]
            self.assertTrue(verify_checksum(path, expected))
            path.write_bytes(path.read_bytes() + b"tampered")
            self.assertFalse(verify_checksum(path, expected))


if __name__ == "__main__":
    unittest.main()


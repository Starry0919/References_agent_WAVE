import copy
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from skill import PdfAcquisitionSkill
from helpers import CANDIDATE, FakeDownloader, fixed_clock


class CountingDownloader(FakeDownloader):
    def __init__(self):
        super().__init__()
        self.calls = 0

    def fetch(self, candidate, url=None):
        self.calls += 1
        return super().fetch(candidate, url)


class UnverifiedCandidateTest(unittest.TestCase):
    def test_gate_blocks_download(self):
        with tempfile.TemporaryDirectory(dir=ROOT / "tests") as directory:
            candidate = copy.deepcopy(CANDIDATE)
            candidate["citation_validation"]["status"] = "invalid"
            downloader = CountingDownloader()
            skill = PdfAcquisitionSkill(Path(directory), [downloader], logger=lambda e: None, clock=fixed_clock)
            result = skill.execute({"accepted_candidates": [candidate]})
            self.assertEqual(downloader.calls, 0)
            self.assertEqual(result["output"]["failed_items"][0]["error"]["local_code"], "PDF001")


if __name__ == "__main__":
    unittest.main()

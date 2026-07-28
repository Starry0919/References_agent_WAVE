import copy
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from skill import PdfAcquisitionSkill
from helpers import CANDIDATE, FakeDownloader, fixed_clock


class HtmlInsteadPdfTest(unittest.TestCase):
    def test_html_error_page_is_not_stored(self):
        with tempfile.TemporaryDirectory(dir=ROOT / "tests") as directory:
            downloader = FakeDownloader(b"<html>not found</html>", "text/html")
            skill = PdfAcquisitionSkill(Path(directory), [downloader], logger=lambda e: None, clock=fixed_clock)
            result = skill.execute({"accepted_candidates": [copy.deepcopy(CANDIDATE)]})
            self.assertEqual(result["output"]["artifacts"], [])
            self.assertFalse(list(Path(directory).rglob("*.pdf")))


if __name__ == "__main__":
    unittest.main()


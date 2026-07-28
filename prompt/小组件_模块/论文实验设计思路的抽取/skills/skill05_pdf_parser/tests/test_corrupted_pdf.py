import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from skill import PdfStructureParsingSkill
from helpers import FakeMinerU, NeverUsedFallback, fixed_clock, make_artifact


class CorruptedPdfTest(unittest.TestCase):
    def test_checksum_mismatch_blocks_parser(self):
        with tempfile.TemporaryDirectory(dir=ROOT / "tests") as directory:
            root = Path(directory)
            parser = FakeMinerU()
            artifact = make_artifact(root, checksum_override="0" * 64)
            result = PdfStructureParsingSkill(parser, NeverUsedFallback(), root / "out", logger=lambda e: None, clock=fixed_clock).execute({"paper_artifact": artifact})
            self.assertEqual(result["status"], "terminal_failure")
            self.assertEqual(result["errors"][0]["local_code"], "PARSE001")
            self.assertEqual(parser.calls, 0)


if __name__ == "__main__":
    unittest.main()

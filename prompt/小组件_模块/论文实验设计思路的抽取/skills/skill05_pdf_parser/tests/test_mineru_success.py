import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from skill import PdfStructureParsingSkill
from helpers import FakeMinerU, NeverUsedFallback, fixed_clock, make_artifact


class MinerUSuccessTest(unittest.TestCase):
    def test_generates_structured_markdown(self):
        with tempfile.TemporaryDirectory(dir=ROOT / "tests") as directory:
            root = Path(directory)
            artifact = make_artifact(root)
            skill = PdfStructureParsingSkill(FakeMinerU(), NeverUsedFallback(), root / "out", logger=lambda e: None, clock=fixed_clock)
            result = skill.execute({"paper_artifact": artifact})
            self.assertIn(result["status"], {"succeeded", "succeeded_with_warnings"})
            doc = result["output"]["document_artifact"]
            self.assertTrue(Path(doc["markdown_artifact"]["markdown_path"]).is_file())
            self.assertEqual(doc["document_metadata"]["parser_version"], "3.4.4")
            self.assertTrue(result["output"]["derived_artifacts"])

    def test_mineru_retry_succeeds_on_second_attempt(self):
        with tempfile.TemporaryDirectory(dir=ROOT / "tests") as directory:
            root = Path(directory)
            parser = FakeMinerU(fail_count=1)
            skill = PdfStructureParsingSkill(parser, NeverUsedFallback(), root / "out", logger=lambda e: None, clock=fixed_clock)
            result = skill.execute({"paper_artifact": make_artifact(root), "parse_policy": {"mode": "hybrid"}})
            self.assertEqual(result["output"]["document_artifact"]["parse_attempts"][0]["status"], "failed")
            self.assertEqual(result["output"]["document_artifact"]["parse_attempts"][1]["mode"], "pipeline")


if __name__ == "__main__":
    unittest.main()


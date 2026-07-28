import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from skill import PdfAcquisitionSkill
from helpers import VALID_PDF, fixed_clock


class ManualUploadTest(unittest.TestCase):
    def test_upload_uses_same_artifact_flow(self):
        with tempfile.TemporaryDirectory(dir=ROOT / "tests") as directory:
            temp = Path(directory)
            upload = temp / "paper.pdf"
            upload.write_bytes(VALID_PDF)
            skill = PdfAcquisitionSkill(temp / "artifacts", logger=lambda e: None, clock=fixed_clock)
            result = skill.execute({"manual_uploads": [{
                "path": str(upload), "paper_identity": {"paper_id": "manual:test", "title": "Uploaded paper"}
            }]})
            artifact = result["output"]["paper_artifacts"][0]
            self.assertEqual(artifact["source_information"]["source_type"], "manual_upload")
            self.assertEqual(artifact["artifact_ref"]["media_type"], "application/pdf")


if __name__ == "__main__":
    unittest.main()


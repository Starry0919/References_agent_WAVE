import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1].parent / "skills"))
from step02_source_validation.skill import execute  # noqa: E402


def ref(**biblio):
    return {"source_ref_type": "text", "source_id": "src_1", "raw_text": "some text", "bibliographic": biblio}


class Step02SourceValidation(unittest.TestCase):
    def test_identity_verified_with_isbn(self):
        result = execute({"source_ref": ref(title="Textbook of Metabolic Engineering", isbn=["978-0-00-000000-0"], edition="2nd", source_type="textbook")})
        self.assertTrue(result["output"]["identity_verified"])
        self.assertEqual(result["status"], "succeeded")

    def test_unresolved_edition_flagged_not_silently_accepted(self):
        result = execute({"source_ref": ref(title="Textbook of Metabolic Engineering", isbn=["978-0-00-000000-0"], source_type="textbook")})
        self.assertTrue(result["output"]["unresolved_edition"])
        self.assertEqual(result["status"], "needs_review")
        self.assertTrue(any(e["code"] == "UNRESOLVED_EDITION" for e in result["errors"]))

    def test_course_material_not_promoted_to_textbook_authority(self):
        result = execute({"source_ref": ref(title="Lecture Notes on Metabolic Flux", source_type="course_material")})
        self.assertEqual(result["output"]["source_type"], "course_material")
        self.assertEqual(result["output"]["authority_level"], "low_medium")

    def test_no_bibliographic_evidence_is_not_verified(self):
        result = execute({"source_ref": ref(title="")})
        self.assertFalse(result["output"]["identity_verified"])
        self.assertTrue(any(e["code"] == "SOURCE_IDENTITY_ERROR" for e in result["errors"]))


if __name__ == "__main__":
    unittest.main()

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from skill import ExperimentalDesignExtractor
from helpers import clean_artifact, fixed_clock


class UnknownTest(unittest.TestCase):
    def test_unreported_fields_are_null_without_evidence(self):
        artifact = clean_artifact([("Introduction", ["This paper discusses a biological question."])])
        result = ExperimentalDesignExtractor(logger=lambda e: None, clock=fixed_clock).execute({"clean_document_artifact": artifact})
        for name in ("strain", "genotype", "culture_conditions", "replicates", "instruments"):
            field = result["output"]["fields"][name]
            self.assertEqual(field["status"], "unknown")
            self.assertIsNone(field["value"])
            self.assertEqual(field["evidence_ids"], [])


if __name__ == "__main__":
    unittest.main()


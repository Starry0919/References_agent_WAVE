import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from skill import ExperimentalDesignExtractor
from helpers import COMPLETE, fixed_clock


class ObjectiveTest(unittest.TestCase):
    def test_complete_paper_extracts_core_design(self):
        result = ExperimentalDesignExtractor(logger=lambda e: None, clock=fixed_clock).execute({"clean_document_artifact": COMPLETE})
        fields = result["output"]["fields"]
        self.assertEqual(fields["objective"]["status"], "reported")
        self.assertEqual(fields["engineering_method"]["status"], "reported")
        self.assertEqual(fields["assay"]["value"], ["HPLC"])
        self.assertIn("ANOVA", fields["analysis_methods"]["value"])
        self.assertTrue(fields["outcomes"]["value"]["observed_outcomes"])
        self.assertTrue(result["self_check"]["passed"])


if __name__ == "__main__":
    unittest.main()


import copy
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from skill import CitationValidationGate
from helpers import CANDIDATE, METADATA, FakeClient, fixed_clock


class ValidDoiTest(unittest.TestCase):
    def test_correct_doi_is_accepted(self):
        gate = CitationValidationGate([FakeClient(lookup=METADATA)], logger=lambda e: None, clock=fixed_clock)
        result = gate.execute({"candidates": [copy.deepcopy(CANDIDATE)]})
        self.assertEqual(result["output"]["validation_results"][0]["final_decision"], "accepted")
        self.assertEqual(result["output"]["accepted_candidates"][0]["citation_validation"]["status"], "valid")
        self.assertTrue(result["output"]["validation_results"][0]["skill04_eligible"])


if __name__ == "__main__":
    unittest.main()


import copy
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from skill import CitationValidationGate
from helpers import CANDIDATE, FakeClient, fixed_clock


class FailureCaseTest(unittest.TestCase):
    def test_no_database_fact_can_never_be_accepted(self):
        gate = CitationValidationGate(
            [FakeClient(name="Crossref", unavailable=True), FakeClient(name="PubMed", unavailable=True)],
            logger=lambda e: None, clock=fixed_clock
        )
        result = gate.execute({"candidates": [copy.deepcopy(CANDIDATE)]})
        validation = result["output"]["validation_results"][0]
        self.assertEqual(validation["final_decision"], "needs_review")
        self.assertEqual(result["output"]["accepted_candidates"], [])
        self.assertFalse(validation["skill04_eligible"])
        self.assertLessEqual(validation["validation_attempts"], 3)


if __name__ == "__main__":
    unittest.main()

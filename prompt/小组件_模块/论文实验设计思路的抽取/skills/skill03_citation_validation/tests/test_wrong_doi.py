import copy
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from skill import CitationValidationGate
from helpers import CANDIDATE, FakeClient, fixed_clock


class WrongDoiTest(unittest.TestCase):
    def test_nonexistent_doi_fails_after_three_attempts(self):
        candidate = copy.deepcopy(CANDIDATE)
        candidate["identifiers"]["doi"] = "10.9999/does-not-exist"
        gate = CitationValidationGate([FakeClient(lookup=None, searches=[[], []])], logger=lambda e: None, clock=fixed_clock)
        result = gate.execute({"candidates": [candidate]})
        validation = result["output"]["validation_results"][0]
        self.assertEqual(validation["final_decision"], "rejected")
        self.assertEqual(validation["validation_attempts"], 3)
        self.assertFalse(validation["skill04_eligible"])


if __name__ == "__main__":
    unittest.main()


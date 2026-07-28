import copy
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from skill import CitationValidationGate
from helpers import CANDIDATE, METADATA, FakeClient, fixed_clock


class RetryLogicTest(unittest.TestCase):
    def test_title_author_retry_finds_database_doi(self):
        client = FakeClient(lookup=None, searches=[[METADATA]])
        gate = CitationValidationGate([client], logger=lambda e: None, clock=fixed_clock)
        result = gate.execute({"candidates": [copy.deepcopy(CANDIDATE)]})
        validation = result["output"]["validation_results"][0]
        self.assertEqual(validation["final_decision"], "accepted")
        self.assertEqual(validation["validation_attempts"], 2)
        self.assertLessEqual(validation["validation_attempts"], 3)

    def test_database_failure_falls_back(self):
        clients = [
            FakeClient(name="Crossref", unavailable=True),
            FakeClient(name="PubMed", lookup=METADATA)
        ]
        gate = CitationValidationGate(clients, logger=lambda e: None, clock=fixed_clock)
        result = gate.execute({"candidates": [copy.deepcopy(CANDIDATE)]})
        validation = result["output"]["validation_results"][0]
        self.assertEqual(validation["final_decision"], "accepted")
        self.assertIn("Crossref", validation["sources_checked"])
        self.assertIn("PubMed", validation["sources_checked"])


if __name__ == "__main__":
    unittest.main()


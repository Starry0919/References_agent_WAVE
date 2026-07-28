import copy
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from skill import CitationValidationGate
from helpers import CANDIDATE, METADATA, FakeClient, fixed_clock


class MetadataMismatchTest(unittest.TestCase):
    def test_wrong_doi_for_another_paper_is_rejected(self):
        wrong = {**METADATA, "doi": "10.1000/other", "title": "An unrelated clinical trial", "authors": ["Other Person"], "journal": "Other Journal", "year": 2010}
        gate = CitationValidationGate([FakeClient(lookup=wrong, searches=[[wrong], [wrong]])], logger=lambda e: None, clock=fixed_clock)
        result = gate.execute({"candidates": [copy.deepcopy(CANDIDATE)]})
        validation = result["output"]["validation_results"][0]
        self.assertEqual(validation["final_decision"], "rejected")
        self.assertEqual(validation["doi_validation_status"], "failed")
        self.assertFalse(validation["matching_report"]["all_core_match"])

    def test_minor_title_difference_is_accepted(self):
        minor = {**METADATA, "title": "Engineering Escherichia coli for succinate production."}
        gate = CitationValidationGate([FakeClient(lookup=minor)], logger=lambda e: None, clock=fixed_clock)
        result = gate.execute({"candidates": [copy.deepcopy(CANDIDATE)]})
        self.assertEqual(result["output"]["validation_results"][0]["final_decision"], "accepted")


if __name__ == "__main__":
    unittest.main()


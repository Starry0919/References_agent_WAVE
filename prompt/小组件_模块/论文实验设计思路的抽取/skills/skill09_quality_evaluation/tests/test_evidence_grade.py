import unittest
from helpers import request
from skill import execute
class TestEvidence(unittest.TestCase):
    def test_missing_evidence_is_low_and_reviewed(self):
        result = execute(request(no_evidence=True), logger=lambda _: None)
        self.assertEqual(result["output"]["evaluation_report"]["dimensions"]["evidence_quality"]["grade"], "D")
        self.assertEqual(result["status"], "needs_review")
        self.assertEqual(result["warnings"][0]["code"], "EVAL002")
if __name__ == "__main__": unittest.main()

import unittest
from helpers import design, request
from skill import execute
class RiskTest(unittest.TestCase):
    def test_low_evidence_reduces_confidence_and_adds_risk(self):
        r = execute(request([design(strain="BL21", assay=None)], [("D", .2)]), logger=lambda _: None)
        self.assertEqual(r["output"]["k12_analysis"][0]["confidence"], .2)
        self.assertEqual(r["output"]["risk_assessment"][0]["risk_level"], "high")
        self.assertEqual(r["status"], "needs_review")
if __name__ == "__main__": unittest.main()

import unittest
from helpers import design, request
from skill import execute
class StrainTest(unittest.TestCase):
    def test_bl21_to_k12_has_risk(self):
        r = execute(request([design(strain="E. coli BL21(DE3)")]), logger=lambda _: None)
        self.assertEqual(r["output"]["k12_analysis"][0]["compatibility"], "medium")
        self.assertTrue(any(x["type"] == "biological" for x in r["output"]["risk_assessment"][0]["risks"]))
    def test_missing_strain_stays_unknown(self):
        r = execute(request([design(strain=None)]), logger=lambda _: None)
        self.assertEqual(r["output"]["k12_analysis"][0]["compatibility"], "unknown")
        self.assertEqual(r["output"]["k12_transfer_analyses"][0]["strain_difference"]["status"], "unknown")
if __name__ == "__main__": unittest.main()

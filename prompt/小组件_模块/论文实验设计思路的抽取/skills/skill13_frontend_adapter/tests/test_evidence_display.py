import unittest
from helpers import request
from skill import execute
class EvidenceTest(unittest.TestCase):
    def test_evidence_fields(self):
        item=execute(request(),logger=lambda _:None)["output"]["evidence_view"]["items"][0]
        self.assertTrue({"paper","section","quote","confidence","status"}.issubset(item))
    def test_missing_evidence_unknown(self):
        r=execute(request(evidence_present=False),logger=lambda _:None)
        self.assertEqual(r["output"]["evidence_view"]["status"],"unknown")
        self.assertEqual(r["warnings"][0]["code"],"UI002")
if __name__=="__main__":unittest.main()

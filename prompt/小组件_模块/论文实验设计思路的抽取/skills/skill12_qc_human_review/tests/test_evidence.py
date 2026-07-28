import unittest
from helpers import Store, request, content
from skill import execute
class EvidenceTest(unittest.TestCase):
    def test_reported_without_evidence_requires_review(self):
        r=execute(request(content(evidence=False)),logger=lambda _:None,event_store=Store())
        self.assertEqual(r["output"]["qc_report"]["final_status"],"REVIEW_REQUIRED")
        self.assertTrue(r["output"]["review_task"])
if __name__=="__main__": unittest.main()

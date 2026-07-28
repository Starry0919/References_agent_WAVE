import unittest
from helpers import Store, request, content
from skill import execute
class NonblockingTest(unittest.TestCase):
    def test_pending_review_pipeline_continues(self):
        r=execute(request(content(evidence=False)),logger=lambda _:None,event_store=Store())
        self.assertTrue(r["output"]["continuation"]["pipeline_may_continue"])
        self.assertFalse(r["output"]["continuation"]["artifact_may_advance"])
        self.assertEqual(r["status"],"needs_review")
if __name__=="__main__": unittest.main()

import unittest
from helpers import Store, request, content
from skill import execute
class AIGovernanceTest(unittest.TestCase):
    def test_level3_requires_human(self):
        r=execute(request(content(ai_level=3)),logger=lambda _:None,event_store=Store())
        self.assertEqual(r["output"]["qc_report"]["final_status"],"BLOCKED")
        self.assertTrue(r["output"]["review_task"])
    def test_ai_cannot_approve(self):
        action={"action":"approve","actor_type":"ai","actor_id":"planner"}
        r=execute(request(content(evidence=False),action),logger=lambda _:None,event_store=Store())
        self.assertEqual(r["errors"][0]["code"],"GOV005")
        self.assertEqual(r["output"]["qc_report"]["final_status"],"BLOCKED")
        self.assertFalse(r["output"]["continuation"]["pipeline_may_continue"])
        self.assertTrue(r["self_check"]["passed"])
if __name__=="__main__": unittest.main()

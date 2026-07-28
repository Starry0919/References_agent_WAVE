import unittest
from helpers import request
from skill import execute
class GovernanceTest(unittest.TestCase):
    def test_human_approval_visible(self):
        view=execute(request(),logger=lambda _:None)["output"]["governance_view"]
        self.assertIn("Human Approved",view["display_states"])
    def test_ai_content_labeled(self):
        r=execute(request(ai=True,review="pending"),logger=lambda _:None)
        self.assertTrue(all(x["source_type"]=="AI_generated" for x in r["output"]["step_cards"]))
        self.assertIn("Human Review Pending",r["output"]["governance_view"]["display_states"])
    def test_unmarked_source_blocked(self):
        self.assertEqual(execute(request(bad_source=True),logger=lambda _:None)["errors"][0]["code"],"UI003")
if __name__=="__main__":unittest.main()

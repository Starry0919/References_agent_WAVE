import unittest
from helpers import candidate, request
from skill import execute
class AITest(unittest.TestCase):
    def test_combination_is_level2_explained(self):
        r = execute(request([candidate("p1", "gene knockout"), candidate("p2", "promoter replacement")]), logger=lambda _: None)
        p = r["output"]["ai_combination_proposals"][0]
        self.assertEqual(p["source_type"], "ai_generated_proposal")
        self.assertEqual(p["design_rationale"]["suggestion_level"], 2)
        self.assertTrue(p["design_rationale"]["uncertainty"])
    def test_unsupported_candidate_removed(self):
        r = execute(request([candidate("p1", "unknown", evidence=False)]), logger=lambda _: None)
        self.assertFalse(r["output"]["engineering_plans"])
        self.assertTrue(any(w["code"] == "PLAN002" for w in r["warnings"]))
        self.assertTrue(r["output"]["approval_status"]["approval_required"])
if __name__ == "__main__": unittest.main()

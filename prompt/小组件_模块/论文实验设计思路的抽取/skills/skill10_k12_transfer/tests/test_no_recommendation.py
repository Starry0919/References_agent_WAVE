import json, unittest
from helpers import design, request
from skill import execute
class BoundaryTest(unittest.TestCase):
    def test_no_ranking_or_best_strategy(self):
        r = execute(request([design(), design(strategy="promoter replacement")]), logger=lambda _: None)
        text = json.dumps(r["output"]["candidate_design_space"]).lower()
        self.assertNotIn('"rank"', text)
        self.assertNotIn('"best"', text)
        self.assertTrue(r["self_check"]["passed"])
    def test_missing_target_fails(self):
        self.assertEqual(execute({}, logger=lambda _: None)["errors"][0]["code"], "K12_001")
if __name__ == "__main__": unittest.main()

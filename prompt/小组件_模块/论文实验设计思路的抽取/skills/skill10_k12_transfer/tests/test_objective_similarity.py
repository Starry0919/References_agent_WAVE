import unittest
from helpers import design, request
from skill import execute
class ObjectiveTest(unittest.TestCase):
    def test_same_objectives_share_cluster(self):
        r = execute(request([design(), design()]), logger=lambda _: None)
        self.assertEqual(len(r["output"]["objective_clusters"]), 1)
        self.assertEqual(len(r["output"]["comparison_matrix"]), 2)
    def test_different_objectives_are_separate(self):
        r = execute(request([design(), design(objective="improve acid tolerance")]), logger=lambda _: None)
        self.assertEqual(len(r["output"]["objective_clusters"]), 2)
        self.assertTrue(any(x["code"] == "K12_003" for x in r["warnings"]))
if __name__ == "__main__": unittest.main()

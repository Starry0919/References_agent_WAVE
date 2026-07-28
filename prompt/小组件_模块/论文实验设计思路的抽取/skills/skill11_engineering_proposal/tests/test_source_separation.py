import unittest
from helpers import candidate, request
from skill import execute
class SeparationTest(unittest.TestCase):
    def test_tracks_are_separate(self):
        r = execute(request([candidate("p1", "knockout"), candidate("p2", "promoter")]), logger=lambda _: None)
        self.assertTrue(all(p["track"] == "A" for p in r["output"]["engineering_plans"]))
        self.assertTrue(all(p["track"] == "B" for p in r["output"]["ai_combination_proposals"]))
        self.assertTrue(r["self_check"]["passed"])
if __name__ == "__main__": unittest.main()

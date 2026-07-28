import unittest
from helpers import design, request
from skill import execute
class TransferTest(unittest.TestCase):
    def test_k12_high_quality_direct_reference_not_decision(self):
        r = execute(request([design()]), logger=lambda _: None)
        item = r["output"]["candidate_design_space"][0]
        self.assertEqual(item["transferability"], "direct_reference")
        self.assertEqual(item["decision_status"], "candidate_only_not_ranked")
if __name__ == "__main__": unittest.main()

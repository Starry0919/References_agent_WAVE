import unittest
from helpers import request
from skill import execute
class SummaryTest(unittest.TestCase):
    def test_summary_and_cards(self):
        r=execute(request(),logger=lambda _:None)
        self.assertEqual(r["status"],"succeeded")
        self.assertEqual(r["output"]["summary_view"]["k12_compatibility"],"high")
        self.assertEqual(len(r["output"]["step_cards"]),4)
    def test_missing_plan_fails(self):
        self.assertEqual(execute({},logger=lambda _:None)["errors"][0]["code"],"UI001")
if __name__=="__main__":unittest.main()

import unittest
from helpers import Store, request
from skill import execute
class SchemaTest(unittest.TestCase):
    def test_complete_plan_passes(self):
        r=execute(request(),logger=lambda _:None,event_store=Store())
        self.assertEqual(r["output"]["qc_report"]["final_status"],"PASS")
        self.assertIsNone(r["output"]["review_task"])
    def test_missing_input_fails(self):
        self.assertEqual(execute({},logger=lambda _:None,event_store=Store())["errors"][0]["code"],"GOV001")
if __name__=="__main__": unittest.main()

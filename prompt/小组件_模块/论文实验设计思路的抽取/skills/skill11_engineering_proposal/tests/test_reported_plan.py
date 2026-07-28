import unittest
from helpers import candidate, request
from skill import execute
class ReportedTest(unittest.TestCase):
    def test_reported_plan_has_evidence(self):
        r = execute(request([candidate("p1", "gene knockout")]), logger=lambda _: None)
        p = r["output"]["engineering_plans"][0]
        self.assertEqual(p["source_type"], "reported_in_literature")
        self.assertTrue(all(s["evidence"] for phase in p["dbtl_plan"].values() for s in phase))
if __name__ == "__main__": unittest.main()

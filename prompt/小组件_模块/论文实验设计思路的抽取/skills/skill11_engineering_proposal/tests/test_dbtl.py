import unittest
from helpers import candidate, request
from skill import execute
class DBTLTest(unittest.TestCase):
    def test_all_phases_and_step_fields(self):
        r = execute(request([candidate("p1", "knockout")]), logger=lambda _: None)
        dbtl = r["output"]["engineering_plans"][0]["dbtl_plan"]
        self.assertEqual(set(dbtl), {"design", "build", "test", "learn"})
        required = {"step_id","title","source_type","what","why","how","input","output","evidence","validation_checkpoint","risk"}
        self.assertTrue(all(required.issubset(s) for phase in dbtl.values() for s in phase))
if __name__ == "__main__": unittest.main()

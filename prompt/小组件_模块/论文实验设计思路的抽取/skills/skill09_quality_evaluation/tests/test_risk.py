import unittest
from helpers import request
from skill import execute
class TestRisk(unittest.TestCase):
    def test_risks_and_conflict_recovery(self):
        missing = {"strain", "engineering_method", "culture_conditions", "replicates", "assay", "hypothesis"}
        result = execute(request(unknown=missing, conflicts=[{"field": "strain"}]), logger=lambda _: None)
        risks = result["output"]["evaluation_report"]["risks"]
        self.assertEqual(risks["replication_risk"]["level"], "high")
        self.assertNotIn("transfer_risk", risks)
        self.assertEqual(result["status"], "needs_review")
        self.assertTrue(any(w["code"] == "EVAL004" for w in result["warnings"]))
if __name__ == "__main__": unittest.main()

import unittest
from helpers import candidate, request
from skill import execute
class ApprovalTest(unittest.TestCase):
    def test_ai_and_risk_require_approval(self):
        r = execute(request([candidate("p1", "knockout", risk=True), candidate("p2", "promoter")]), logger=lambda _: None)
        self.assertTrue(r["output"]["approval_status"]["approval_required"])
        self.assertEqual(r["status"], "needs_review")
    def test_invalid_input(self):
        self.assertEqual(execute({}, logger=lambda _: None)["errors"][0]["code"], "PLAN001")
if __name__ == "__main__": unittest.main()

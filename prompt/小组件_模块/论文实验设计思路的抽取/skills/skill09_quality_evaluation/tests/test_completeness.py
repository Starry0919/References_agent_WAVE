import unittest
from helpers import request
from skill import execute
class TestCompleteness(unittest.TestCase):
    def test_complete_design_scores_high(self):
        result = execute(request(), logger=lambda _: None)
        self.assertEqual(result["status"], "succeeded")
        self.assertGreaterEqual(result["output"]["evaluation_report"]["overall_score"], 90)
    def test_invalid_input(self):
        self.assertEqual(execute({}, logger=lambda _: None)["errors"][0]["code"], "EVAL001")
if __name__ == "__main__": unittest.main()

import unittest
from helpers import request, FIELDS
from skill import execute
class TestUnknown(unittest.TestCase):
    def test_unknowns_all_listed_and_grade_capped(self):
        unknown = set(FIELDS[:10])
        result = execute(request(unknown=unknown), logger=lambda _: None)
        report = result["output"]["evaluation_report"]
        self.assertEqual({x["field"] for x in report["missing_information"]}, unknown)
        self.assertNotIn(report["dimensions"]["evidence_quality"]["grade"], {"A", "B"})
        self.assertTrue(result["self_check"]["passed"])
if __name__ == "__main__": unittest.main()

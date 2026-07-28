import sys
import unittest
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL_DIR))
from skill import RequirementParser


class AmbiguousRequestTest(unittest.TestCase):
    def test_requires_clarification(self):
        result = RequirementParser().execute({"user_request": "找一些代谢工程论文"})
        self.assertEqual(result["status"], "needs_review")
        self.assertEqual(
            result["output"]["field_metadata"]["organism"]["status"],
            "needs_clarification",
        )


if __name__ == "__main__":
    unittest.main()


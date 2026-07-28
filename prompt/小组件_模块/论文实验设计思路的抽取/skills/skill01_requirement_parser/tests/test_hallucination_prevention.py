import sys
import unittest
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL_DIR))
from skill import RequirementParser


class HallucinationPreventionTest(unittest.TestCase):
    def test_unknown_strain_stays_unknown(self):
        result = RequirementParser().execute({"user_request": "研究某未知菌株"})
        self.assertIsNone(result["output"]["research_intent"]["strain"])
        self.assertIn(
            result["output"]["field_metadata"]["strain"]["status"],
            {"unknown", "needs_clarification"},
        )
        self.assertTrue(result["self_check"]["passed"])


if __name__ == "__main__":
    unittest.main()


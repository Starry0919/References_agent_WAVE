import sys
import unittest
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL_DIR))
from skill import RequirementParser


class MissingInformationTest(unittest.TestCase):
    def test_does_not_infer_organism_or_strain(self):
        result = RequirementParser().execute({"user_request": "寻找提高产量的方法"})
        intent = result["output"]["research_intent"]
        self.assertIsNone(intent["organism"])
        self.assertIsNone(intent["strain"])
        self.assertNotIn("Escherichia coli", str(result["output"]))


if __name__ == "__main__":
    unittest.main()


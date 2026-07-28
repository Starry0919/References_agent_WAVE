import sys
import unittest
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL_DIR))
from skill import RequirementParser


class NormalInputTest(unittest.TestCase):
    def test_extracts_required_scientific_intent(self):
        result = RequirementParser(current_year=2026).execute({
            "user_request": "寻找近5年利用E.coli K12基因敲除提高乙醇产量的高影响力论文"
        })
        output = result["output"]
        intent = output["research_intent"]
        spec = output["retrieval_strategy"]["search_specification"]
        self.assertEqual(intent["organism"], "Escherichia coli")
        self.assertEqual(intent["strain"].upper(), "K-12")
        self.assertIn("敲除", intent["engineering_objective"])
        self.assertIn("乙醇产量", intent["phenotype"])
        self.assertEqual(spec["time_range"]["value"]["start_year"], 2022)
        self.assertEqual(spec["time_range"]["value"]["end_year"], 2026)
        self.assertIn("high_impact", spec["literature_quality_requirement"]["value"])
        self.assertTrue(output["retrieval_strategy"]["queries"])


if __name__ == "__main__":
    unittest.main()


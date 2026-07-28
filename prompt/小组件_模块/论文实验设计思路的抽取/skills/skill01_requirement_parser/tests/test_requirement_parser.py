import copy
import sys
import unittest
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parents[1]
if str(SKILL_DIR) not in sys.path:
    sys.path.insert(0, str(SKILL_DIR))

from implementation import RequirementParser  # noqa: E402


class RequirementParserTests(unittest.TestCase):
    def setUp(self):
        self.parser = RequirementParser()

    def test_normal_case(self):
        result = self.parser.execute({
            "user_request": "检索通过代谢工程提高 E. coli K-12 琥珀酸产量的实验研究"
        })

        self.assertIn(result["status"], {"succeeded", "succeeded_with_warnings"})
        intent = result["output"]["research_intent"]
        self.assertEqual(intent["organism"], "Escherichia coli")
        self.assertEqual(intent["strain"].upper(), "K-12")
        self.assertEqual(
            result["output"]["field_metadata"]["organism"]["status"], "reported"
        )
        self.assertTrue(result["output"]["retrieval_strategy"]["queries"])
        self.assertTrue(result["self_check"]["passed"])

    def test_missing_information_is_not_inferred(self):
        result = self.parser.execute({"user_request": "寻找提高产量的方法"})

        intent = result["output"]["research_intent"]
        self.assertIsNone(intent["organism"])
        self.assertIsNone(intent["strain"])
        self.assertEqual(
            result["output"]["field_metadata"]["organism"],
            {
                "value": None,
                "source": "user_input",
                "confidence": 1.0,
                "status": "unknown",
            },
        )

    def test_invalid_input(self):
        result = self.parser.execute({"user_request": "  "})

        self.assertEqual(result["status"], "terminal_failure")
        self.assertEqual(result["errors"][0]["code"], "EDX-VAL-001")
        self.assertIsNone(result["output"])

    def test_failure_recovery_and_idempotent_output(self):
        def broken_logger(_event):
            raise RuntimeError("logging unavailable")

        parser = RequirementParser(logger=broken_logger)
        request = {
            "user_request": "研究酿酒酵母通过基因编辑提高耐受性的实验",
            "constraints": {"sources": ["PubMed"]},
        }
        first = parser.execute(copy.deepcopy(request))
        second = parser.execute(copy.deepcopy(request))

        self.assertNotIn(first["status"], {"retryable_failure", "terminal_failure"})
        self.assertEqual(first["output"], second["output"])
        self.assertEqual(
            first["provenance"]["output_hash"],
            second["provenance"]["output_hash"],
        )

    def test_conflicting_criteria_needs_review(self):
        result = self.parser.execute({
            "user_request": "研究 E. coli 产量；纳入：发酵；排除：发酵"
        })

        self.assertEqual(result["status"], "needs_review")
        reasons = [item["reason"] for item in result["review_requests"]]
        self.assertIn("conflicting_inclusion_exclusion_criteria", reasons)


if __name__ == "__main__":
    unittest.main()


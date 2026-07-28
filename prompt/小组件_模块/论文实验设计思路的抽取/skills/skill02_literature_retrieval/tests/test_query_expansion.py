import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from query.query_expander import QueryExpander
from helpers import INTENT


class BrokenKimi:
    def expand_queries(self, intent, fallback):
        raise RuntimeError("not configured")


class QueryExpansionTest(unittest.TestCase):
    def test_kimi_failure_uses_original_terms(self):
        result = QueryExpander(BrokenKimi()).expand(INTENT, {})
        self.assertTrue(result["fallback_used"])
        self.assertIn("Escherichia coli", result["queries"][0]["query"])
        self.assertIsNotNone(result["error"])


if __name__ == "__main__":
    unittest.main()


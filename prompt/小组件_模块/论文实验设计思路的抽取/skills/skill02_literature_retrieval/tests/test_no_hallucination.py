import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from adapters.base import SourceError
from skill import LiteratureRetrievalEngine
from helpers import FixedAdapter, INTENT, fixed_clock


class TemptingKimi:
    def expand_queries(self, intent, fallback):
        return [{"name": "expanded", "query": "succinate knockout"}]

    def score_relevance(self, candidate, intent):
        return {"score": 1.0, "reason": "relevant"}


class NoHallucinationTest(unittest.TestCase):
    def test_all_databases_closed_produces_no_paper(self):
        engine = LiteratureRetrievalEngine(
            adapters={"PubMed": FixedAdapter("PubMed", error=SourceError("offline"))},
            kimi_client=TemptingKimi(), logger=lambda event: None, clock=fixed_clock
        )
        result = engine.execute({"research_intent": INTENT, "sources": ["PubMed"]})
        self.assertEqual(result["status"], "needs_review")
        self.assertEqual(result["output"]["candidates"], [])
        self.assertEqual(result["output"]["result_state"], "empty_result")


if __name__ == "__main__":
    unittest.main()

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from adapters.base import SourceError
from skill import LiteratureRetrievalEngine
from helpers import FixedAdapter, INTENT, PAPER, fixed_clock


class RetrievalEngineTest(unittest.TestCase):
    def engine(self, adapters):
        return LiteratureRetrievalEngine(adapters=adapters, logger=lambda event: None, clock=fixed_clock)

    def test_normal_retrieval(self):
        result = self.engine({"PubMed": FixedAdapter("PubMed", [PAPER])}).execute({
            "research_intent": INTENT, "sources": ["PubMed"]
        })
        self.assertEqual(result["output"]["result_state"], "results")
        self.assertEqual(len(result["output"]["candidates"]), 1)
        self.assertTrue(result["self_check"]["passed"])

    def test_multiple_sources_merge_same_doi(self):
        crossref = {**PAPER, "source": "Crossref", "source_record_id": "10.1000/example", "identifiers": {}}
        result = self.engine({
            "PubMed": FixedAdapter("PubMed", [PAPER]),
            "Crossref": FixedAdapter("Crossref", [crossref])
        }).execute({"research_intent": INTENT, "sources": ["PubMed", "Crossref"]})
        candidates = result["output"]["candidates"]
        self.assertEqual(len(candidates), 1)
        self.assertEqual(set(candidates[0]["retrieval_sources"]), {"PubMed", "Crossref"})

    def test_one_database_failure_degrades_to_other(self):
        result = self.engine({
            "PubMed": FixedAdapter("PubMed", error=SourceError("offline")),
            "Crossref": FixedAdapter("Crossref", [{**PAPER, "source": "Crossref"}])
        }).execute({"research_intent": INTENT, "sources": ["PubMed", "Crossref"]})
        self.assertEqual(len(result["output"]["candidates"]), 1)
        self.assertEqual(result["status"], "succeeded_with_warnings")

    def test_no_results_is_empty_result(self):
        result = self.engine({"PubMed": FixedAdapter("PubMed", [])}).execute({
            "research_intent": INTENT, "sources": ["PubMed"]
        })
        self.assertEqual(result["output"]["result_state"], "empty_result")
        self.assertEqual(result["output"]["candidates"], [])
        self.assertNotIn(result["status"], {"terminal_failure", "retryable_failure"})


if __name__ == "__main__":
    unittest.main()


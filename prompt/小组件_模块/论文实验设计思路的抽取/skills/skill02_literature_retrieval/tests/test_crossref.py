import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from adapters.crossref_adapter import CrossrefAdapter


class Transport:
    def get_json(self, url, params, headers=None):
        return {"message": {"items": [{
            "DOI": "10.1000/test", "title": ["Crossref paper"],
            "author": [{"given": "A", "family": "Author"}],
            "container-title": ["Journal"],
            "published-online": {"date-parts": [[2023, 1, 1]]}
        }]}}


class CrossrefTest(unittest.TestCase):
    def test_parses_database_response(self):
        record = CrossrefAdapter(Transport()).search("query", 10).records[0]
        self.assertEqual(record["title"], "Crossref paper")
        self.assertEqual(record["year"], 2023)
        self.assertEqual(record["authors"], ["A Author"])


if __name__ == "__main__":
    unittest.main()


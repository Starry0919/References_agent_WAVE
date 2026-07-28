import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from adapters.pubmed_adapter import PubMedAdapter


class Transport:
    def get_json(self, url, params, headers=None):
        if "esearch" in url:
            return {"esearchresult": {"idlist": ["123"]}}
        return {"result": {"123": {
            "title": "A database returned paper", "authors": [{"name": "A Author"}],
            "fulljournalname": "Journal", "pubdate": "2024 Jan",
            "articleids": [{"idtype": "doi", "value": "10.1000/test"}]
        }}}


class PubMedTest(unittest.TestCase):
    def test_parses_database_response(self):
        batch = PubMedAdapter(Transport()).search("query", 10)
        self.assertEqual(batch.source, "PubMed")
        self.assertEqual(batch.records[0]["doi"], "10.1000/test")
        self.assertEqual(batch.records[0]["identifiers"]["pmid"], "123")


if __name__ == "__main__":
    unittest.main()


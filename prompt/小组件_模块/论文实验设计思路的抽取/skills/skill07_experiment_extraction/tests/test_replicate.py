import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from skill import ExperimentalDesignExtractor
from helpers import clean_artifact, fixed_clock


class ReplicateTest(unittest.TestCase):
    def test_multiple_replicate_types(self):
        artifact = clean_artifact([("Methods", [
            "Experiments used three biological replicates and two technical replicates."
        ])])
        result = ExperimentalDesignExtractor(logger=lambda e: None, clock=fixed_clock).execute({"clean_document_artifact": artifact})
        values = result["output"]["fields"]["replicates"]["value"]
        self.assertIn({"type": "biological", "n": 3, "reported_text": "three biological replicates"}, values)
        self.assertIn({"type": "technical", "n": 2, "reported_text": "two technical replicates"}, values)


if __name__ == "__main__":
    unittest.main()


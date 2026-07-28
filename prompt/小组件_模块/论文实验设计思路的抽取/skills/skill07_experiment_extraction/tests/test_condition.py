import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from skill import ExperimentalDesignExtractor
from helpers import COMPLETE, clean_artifact, fixed_clock


class ConditionTest(unittest.TestCase):
    def test_extracts_reported_conditions_exactly(self):
        result = ExperimentalDesignExtractor(logger=lambda e: None, clock=fixed_clock).execute({"clean_document_artifact": COMPLETE})
        fields = result["output"]["fields"]
        conditions = fields["culture_conditions"]["value"]
        self.assertIn("37°C", conditions["temperature"])
        self.assertIn("220 rpm", conditions["agitation"])
        self.assertIn("OD600 = 0.8", conditions["od"])
        self.assertIn("M9", fields["medium"]["value"])
        self.assertIn("12 h", fields["time"]["value"])
        self.assertIn("IPTG 0.1 mM", fields["dosage"]["value"])

    def test_missing_culture_condition_is_unknown(self):
        artifact = clean_artifact([("Methods", ["Escherichia coli MG1655 carrying Δpta was constructed."])])
        result = ExperimentalDesignExtractor(logger=lambda e: None, clock=fixed_clock).execute({"clean_document_artifact": artifact})
        self.assertEqual(result["output"]["fields"]["culture_conditions"]["status"], "unknown")
        self.assertIsNone(result["output"]["fields"]["culture_conditions"]["value"])


if __name__ == "__main__":
    unittest.main()


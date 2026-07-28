import copy
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from skill import EvidenceBindingEngine
from helpers import BASE, fixed_clock, skill07_output


class MissingEvidenceTest(unittest.TestCase):
    def test_unsupported_reported_value_is_downgraded(self):
        extracted = copy.deepcopy(skill07_output())
        extracted["fields"]["time"]["value"] = ["99 h"]
        extracted["fields"]["time"]["status"] = "reported"
        extracted["fields"]["time"]["evidence_ids"] = ["candidate:missing"]
        result = EvidenceBindingEngine(logger=lambda e: None, clock=fixed_clock).execute({
            "skill07_output": extracted, "clean_document_artifact": BASE
        })
        field = result["output"]["literature_experiment"]["fields"]["time"]
        self.assertEqual(field["status"], "unknown")
        self.assertIsNone(field["value"])
        self.assertEqual(field["evidence_ids"], [])
        self.assertEqual(result["status"], "needs_review")

    def test_design_logic_without_explicit_hypothesis_stays_unknown(self):
        result = EvidenceBindingEngine(logger=lambda e: None, clock=fixed_clock).execute({
            "skill07_output": skill07_output(), "clean_document_artifact": BASE
        })
        logic = result["output"]["evidence_linked_design"]["extensions"]["design_logic"]
        self.assertIsNone(logic["hypothesis"])
        self.assertEqual(logic["evidence_ids"]["hypothesis"], [])


if __name__ == "__main__":
    unittest.main()


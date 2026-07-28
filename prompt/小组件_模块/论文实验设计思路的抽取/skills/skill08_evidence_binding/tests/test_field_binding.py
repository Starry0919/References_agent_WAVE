import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from skill import EvidenceBindingEngine
from helpers import BASE, fixed_clock, skill07_output


class FieldBindingTest(unittest.TestCase):
    def test_methods_parameter_has_final_evidence(self):
        result = EvidenceBindingEngine(logger=lambda e: None, clock=fixed_clock).execute({
            "skill07_output": skill07_output(), "clean_document_artifact": BASE
        })
        field = result["output"]["literature_experiment"]["fields"]["culture_conditions"]
        self.assertEqual(field["status"], "reported")
        self.assertTrue(field["evidence_ids"])
        record = result["output"]["evidence_map"][field["evidence_ids"][0]]
        self.assertIn("37°C", record["quote"])
        self.assertEqual(record["locator"]["section_path"], ["Materials and Methods"])
        self.assertEqual(len(record["artifact_sha256"]), 64)
        self.assertTrue(result["self_check"]["passed"])


if __name__ == "__main__":
    unittest.main()


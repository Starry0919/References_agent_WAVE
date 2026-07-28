import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from skill import EvidenceBindingEngine
from helpers import clean_artifact, fixed_clock, skill07_output


class UnknownTest(unittest.TestCase):
    def test_unknown_field_never_gets_evidence_or_value(self):
        artifact = clean_artifact([("Introduction", ["This document states no experimental condition."])])
        result = EvidenceBindingEngine(logger=lambda e: None, clock=fixed_clock).execute({
            "skill07_output": skill07_output(artifact), "clean_document_artifact": artifact
        })
        field = result["output"]["literature_experiment"]["fields"]["culture_conditions"]
        self.assertEqual(field["status"], "unknown")
        self.assertIsNone(field["value"])
        self.assertEqual(field["evidence_ids"], [])
        self.assertNotIn("37°C", str(result["output"]))


if __name__ == "__main__":
    unittest.main()

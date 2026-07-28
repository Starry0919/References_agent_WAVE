import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from skill import EvidenceBindingEngine
from helpers import BASE, fixed_clock, skill07_output


class VariableBindingTest(unittest.TestCase):
    def test_variable_units_have_reason_and_sources(self):
        result = EvidenceBindingEngine(logger=lambda e: None, clock=fixed_clock).execute({
            "skill07_output": skill07_output(), "clean_document_artifact": BASE
        })
        variables = result["output"]["evidence_linked_design"]["extensions"]["variables"]
        inferred = [
            item for category in ("independent", "dependent", "controlled")
            for item in variables[category] if item["status"] == "inferred"
        ]
        self.assertTrue(inferred)
        self.assertTrue(all(v["reason"] and v["evidence_ids"] for v in inferred))


if __name__ == "__main__":
    unittest.main()


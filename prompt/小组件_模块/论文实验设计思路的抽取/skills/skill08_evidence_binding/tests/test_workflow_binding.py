import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from skill import EvidenceBindingEngine
from helpers import BASE, fixed_clock, skill07_output


class WorkflowBindingTest(unittest.TestCase):
    def test_reported_workflow_steps_have_evidence(self):
        result = EvidenceBindingEngine(logger=lambda e: None, clock=fixed_clock).execute({
            "skill07_output": skill07_output(), "clean_document_artifact": BASE
        })
        workflow = result["output"]["evidence_linked_design"]["extensions"]["experiment_workflow"]["workflow"]
        reported = [v for v in workflow if v["status"] == "reported"]
        self.assertTrue(reported)
        self.assertTrue(all(v["evidence_ids"] for v in reported))


if __name__ == "__main__":
    unittest.main()


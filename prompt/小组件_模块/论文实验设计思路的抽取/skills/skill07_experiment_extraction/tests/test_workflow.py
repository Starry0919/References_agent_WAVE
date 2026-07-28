import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from skill import ExperimentalDesignExtractor
from helpers import COMPLETE, fixed_clock


class WorkflowTest(unittest.TestCase):
    def test_workflow_uses_reported_operations(self):
        result = ExperimentalDesignExtractor(logger=lambda e: None, clock=fixed_clock).execute({"clean_document_artifact": COMPLETE})
        workflow = result["output"]["extensions"]["experiment_workflow"]["workflow"]
        stages = [v["stage"] for v in workflow]
        self.assertIn("strain construction", stages)
        self.assertIn("culture", stages)
        self.assertIn("measurement", stages)
        self.assertTrue(all(v["source_location"]["paragraph"] for v in workflow))
        self.assertNotIn("optimization", str(workflow).casefold())


if __name__ == "__main__":
    unittest.main()

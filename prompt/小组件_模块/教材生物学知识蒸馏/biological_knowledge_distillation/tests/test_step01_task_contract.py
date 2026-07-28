import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from helpers import request, source  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parents[1].parent / "skills"))
from step01_task_contract.skill import execute  # noqa: E402


class Step01TaskContract(unittest.TestCase):
    def test_never_defaults_target_organism_to_k12(self):
        req = request([source("Feedback inhibition is defined as regulation of enzyme activity.")])
        result = execute(req)
        self.assertEqual(result["status"], "succeeded")
        contract = result["output"]
        self.assertEqual(contract["target_organism"], [])
        self.assertTrue(any("target_organism not specified" in n for n in contract["notes"]))

    def test_assigns_stable_source_ids(self):
        req = request([source("text one"), source("text two")])
        result = execute(req)
        ids = [s["source_id"] for s in result["output"]["input_sources"]]
        self.assertEqual(ids, ["src_1", "src_2"])

    def test_empty_user_request_is_terminal_failure(self):
        req = request([source("text")], user_request="")
        result = execute(req)
        self.assertEqual(result["status"], "terminal_failure")


if __name__ == "__main__":
    unittest.main()

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from skill import EvidenceBindingEngine
from helpers import clean_artifact, fixed_clock, skill07_output


class ConflictTest(unittest.TestCase):
    def test_methods_figure_conflict_references_evidence(self):
        artifact = clean_artifact(
            [("Materials and Methods", ["Cells were cultured at 37°C for 12 h."])],
            figures=[{"figure_id": "Figure 1", "caption": "Cells were cultured at 30°C.", "related_paragraphs": []}]
        )
        result = EvidenceBindingEngine(logger=lambda e: None, clock=fixed_clock).execute({
            "skill07_output": skill07_output(artifact), "clean_document_artifact": artifact
        })
        self.assertEqual(result["status"], "needs_review")
        conflict = result["output"]["conflicts"][0]
        self.assertGreaterEqual(len(conflict["evidence_ids"]), 2)
        unified = result["output"]["literature_experiment"]["conflicts"][0]
        self.assertEqual(unified["status"], "open")


if __name__ == "__main__":
    unittest.main()


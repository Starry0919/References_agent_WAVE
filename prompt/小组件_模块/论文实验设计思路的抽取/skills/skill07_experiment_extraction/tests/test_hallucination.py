import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from skill import ExperimentalDesignExtractor
from helpers import clean_artifact, fixed_clock


class HallucinationTest(unittest.TestCase):
    def test_ecoli_and_knockout_do_not_imply_parameters(self):
        artifact = clean_artifact([("Methods", ["An Escherichia coli gene knockout strain was examined."])])
        result = ExperimentalDesignExtractor(logger=lambda e: None, clock=fixed_clock).execute({"clean_document_artifact": artifact})
        fields = result["output"]["fields"]
        self.assertEqual(fields["culture_conditions"]["status"], "unknown")
        self.assertEqual(fields["instruments"]["status"], "unknown")
        self.assertNotIn("37°C", str(result["output"]))
        self.assertNotIn("CRISPR", str(fields["engineering_method"]["value"]))

    def test_methods_figure_conflict_is_recorded(self):
        artifact = clean_artifact(
            [("Materials and Methods", ["Cells were cultured at 37°C for 12 h."])],
            figures=[{"figure_id": "Figure 1", "caption": "Cells were cultured at 30°C.", "related_paragraphs": []}]
        )
        result = ExperimentalDesignExtractor(logger=lambda e: None, clock=fixed_clock).execute({"clean_document_artifact": artifact})
        self.assertEqual(result["status"], "needs_review")
        self.assertEqual(result["output"]["conflicts"][0]["field"], "culture_conditions.temperature")


if __name__ == "__main__":
    unittest.main()


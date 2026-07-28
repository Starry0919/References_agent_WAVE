import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from skill import ExperimentalDesignExtractor
from helpers import COMPLETE, fixed_clock


class StrainTest(unittest.TestCase):
    def test_organism_strain_and_genotype(self):
        result = ExperimentalDesignExtractor(logger=lambda e: None, clock=fixed_clock).execute({"clean_document_artifact": COMPLETE})
        fields = result["output"]["fields"]
        self.assertIn("Escherichia coli", fields["strain"]["value"]["organism"])
        self.assertIn("MG1655", fields["strain"]["value"]["strain"])
        self.assertIn("Δpta", fields["genotype"]["value"])
        self.assertTrue(fields["strain"]["evidence_ids"])


if __name__ == "__main__":
    unittest.main()


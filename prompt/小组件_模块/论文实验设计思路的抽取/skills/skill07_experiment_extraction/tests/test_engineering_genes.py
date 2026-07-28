import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from extractor.engineering_extractor import extract_engineering


class EngineeringGeneTest(unittest.TestCase):
    def test_target_genes_exclude_common_english_words(self):
        items = [{"text": "Overexpression of the aroG and trpB genes was performed on two strains."}]
        result, _ = extract_engineering(items)
        for noise in ("the", "was", "two", "strain", "strains", "of", "genes"):
            self.assertNotIn(noise, [g.casefold() for g in result["target_genes"]])

    def test_target_genes_capture_locus_style_symbols(self):
        items = [{
            "text": "GapN and SthA were overexpressed to balance NADPH, and a ΔtrpR knockout strain was constructed."
        }]
        result, _ = extract_engineering(items)
        self.assertEqual(set(result["target_genes"]), {"GapN", "SthA", "trpR"})


if __name__ == "__main__":
    unittest.main()

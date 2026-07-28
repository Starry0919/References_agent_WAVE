import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1].parent / "skills"))
from step11_evidence_binding.skill import execute  # noqa: E402

SOURCE_STRUCTURES = [{
    "source_id": "src_1",
    "blocks": [{
        "block_id": "src_1:b1", "block_type": "paragraph", "chapter_id": "Chapter 1",
        "section_path": ["1.1"], "page_start": 1, "page_end": 1,
        "text": "Enzyme X activity is defined as its catalytic rate under standard conditions.",
        "figure_or_table_label": "", "reading_order": 1, "language": "en",
        "source_anchor": {"source_id": "src_1", "chapter_id": "Chapter 1", "section_path": ["1.1"], "page": 1},
    }],
}]


class Step09EvidenceBinding(unittest.TestCase):
    def test_valid_evidence_is_supported_and_not_capped(self):
        concept = {
            "knowledge_id": "src_1:concept:1", "knowledge_type": "concept",
            "name_en": "Enzyme X activity", "definition_en": "its catalytic rate under standard conditions.",
            "source_statements": [{"block_id": "src_1:b1", "text": "Enzyme X activity is defined as its catalytic rate under standard conditions."}],
            "status": "normalized", "confidence": 0.55, "organism_scope": [],
        }
        result = execute({"source_structures": SOURCE_STRUCTURES, "concepts": [concept], "mechanisms": []})
        audited = result["output"]["concepts"][0]
        self.assertTrue(audited["evidence_supported"])
        self.assertGreater(audited["confidence"], 0.3)
        self.assertEqual(audited["knowledge_status"], "validated")

    def test_missing_block_caps_confidence_and_blocks_reported_status(self):
        concept = {
            "knowledge_id": "src_1:concept:2", "knowledge_type": "concept",
            "name_en": "Fabricated concept", "definition_en": "a definition with no real source.",
            "source_statements": [{"block_id": "src_1:does_not_exist", "text": "this text was never actually parsed."}],
            "status": "reported", "confidence": 0.9, "organism_scope": [],
        }
        result = execute({"source_structures": SOURCE_STRUCTURES, "concepts": [concept], "mechanisms": []})
        audited = result["output"]["concepts"][0]
        self.assertFalse(audited["evidence_supported"])
        self.assertLessEqual(audited["confidence"], 0.3)
        self.assertNotEqual(audited["status"], "reported")
        self.assertEqual(audited["knowledge_status"], "candidate")
        self.assertTrue(any(e["code"] == "EVIDENCE_NOT_FOUND" for e in result["errors"]))

    def test_coverage_ratio_reflects_supported_fraction(self):
        good = {"knowledge_id": "src_1:concept:1", "knowledge_type": "concept", "name_en": "A", "definition_en": "its catalytic rate under standard conditions.",
                "source_statements": [{"block_id": "src_1:b1", "text": "Enzyme X activity is defined as its catalytic rate under standard conditions."}],
                "status": "normalized", "confidence": 0.5, "organism_scope": []}
        bad = {"knowledge_id": "src_1:concept:2", "knowledge_type": "concept", "name_en": "B", "definition_en": "nothing real",
               "source_statements": [{"block_id": "src_1:missing", "text": "nothing real"}],
               "status": "normalized", "confidence": 0.5, "organism_scope": []}
        result = execute({"source_structures": SOURCE_STRUCTURES, "concepts": [good, bad], "mechanisms": []})
        coverage = result["output"]["evidence_coverage"]
        self.assertEqual(coverage["total_objects"], 2)
        self.assertEqual(coverage["objects_with_direct_evidence"], 1)
        self.assertEqual(coverage["coverage_ratio"], 0.5)


if __name__ == "__main__":
    unittest.main()

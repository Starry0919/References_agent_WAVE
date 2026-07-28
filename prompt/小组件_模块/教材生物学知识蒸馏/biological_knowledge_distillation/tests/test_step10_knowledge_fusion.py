import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1].parent / "skills"))
from step12_knowledge_fusion.skill import execute  # noqa: E402


def obj(id_, obj_type, name_en, definition_en, organism_scope=None, confidence=0.5):
    return {"id": id_, "type": obj_type, "name_en": name_en, "name_zh": "", "definition_en": definition_en,
            "definition_zh": "", "organism_scope": organism_scope or [], "confidence": confidence}


class Step10Fusion(unittest.TestCase):
    def test_same_source_duplicate_extraction_is_not_a_conflict(self):
        a = obj("src_1:concept:1", "concept", "Feedback inhibition", "reduction of enzyme activity by product A")
        b = obj("src_1:concept:2", "concept", "Feedback inhibition", "reduction of enzyme activity by product B")
        result = execute({"knowledge_objects": [a, b], "validated_sources": []})
        self.assertEqual(len(result["output"]["source_conflicts"]), 0)
        self.assertEqual(result["output"]["canonical_knowledge_objects"][0]["merge_relation"], "related_but_distinct")

    def test_cross_source_definition_conflict_is_flagged_not_averaged(self):
        a = obj("src_1:concept:1", "concept", "Feedback inhibition", "definition from source one")
        b = obj("src_2:concept:1", "concept", "Feedback inhibition", "definition from source two")
        result = execute({"knowledge_objects": [a, b], "validated_sources": []})
        conflicts = result["output"]["source_conflicts"]
        self.assertEqual(len(conflicts), 1)
        self.assertEqual(conflicts[0]["conflict_type"], "definition")
        self.assertTrue(conflicts[0]["requires_human_review"])
        canonical = result["output"]["canonical_knowledge_objects"][0]
        self.assertEqual(canonical["merge_relation"], "conflicting")
        # both sources must be kept, never silently overwritten by a majority
        self.assertEqual(len(canonical["source_specific_variants"]), 2)

    def test_cross_source_organism_scope_difference_is_flagged(self):
        a = obj("src_1:concept:1", "concept", "Membrane transport", "def", organism_scope=["Escherichia coli"])
        b = obj("src_2:concept:1", "concept", "Membrane transport", "def", organism_scope=["Saccharomyces cerevisiae"])
        result = execute({"knowledge_objects": [a, b], "validated_sources": []})
        conflicts = result["output"]["source_conflicts"]
        self.assertTrue(any(c["conflict_type"] == "organism_difference" for c in conflicts))


if __name__ == "__main__":
    unittest.main()

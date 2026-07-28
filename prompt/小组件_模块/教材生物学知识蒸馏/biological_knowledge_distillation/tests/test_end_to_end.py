import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from helpers import read_fixture, request, source  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parents[1].parent))
from biological_knowledge_distillation import execute  # noqa: E402


class EndToEnd(unittest.TestCase):
    def test_level1_only_stops_after_source_parsing(self):
        req = request([source(read_fixture("en_feedback_inhibition.md"))], requested_output_level=["level1_source_parsing"])
        with tempfile.TemporaryDirectory() as d:
            result = execute(req, {"state_dir": d})
        self.assertEqual(result["step_states"]["step06_scope_selection"], "SKIPPED")
        self.assertEqual(result["step_states"]["step07_basic_knowledge_extraction"], "SKIPPED")
        self.assertTrue(result["validated_sources"])

    def test_engineering_distillation_produces_governed_principles(self):
        req = request([source(read_fixture("en_feedback_inhibition.md"))],
                       requested_output_level=["level3_engineering_distillation"], requires_frontend_adapter=True)
        with tempfile.TemporaryDirectory() as d:
            result = execute(req, {"state_dir": d})
        self.assertIn(result["status"], {"WAITING_REVIEW", "COMPLETED"})
        self.assertTrue(result["engineering_principles"])
        self.assertEqual(result["governance"]["exact_SOP_generation"], "blocked")
        for p in result["engineering_principles"]:
            self.assertTrue(p["evidence"])

    def test_bilingual_fusion_and_paper_case_linking(self):
        req = request(
            [source(read_fixture("en_feedback_inhibition.md")),
             source(read_fixture("zh_pathway_competition.md"), title="代谢工程原理 (合成测试版)", authors_or_editors=["测试甲"],
                    isbn=["111-1-11-111111-1"], edition="第1版")],
            requested_output_level=["level4_cross_source_fusion", "level5_knowledge_hub_adapter"],
            requires_cross_source_fusion=True, requires_paper_case_linking=True, requires_frontend_adapter=True,
            paper_case_artifacts=[{
                "experiment_id": "paper_case_001", "host": "Escherichia coli BW25113",
                "intervention": "deleted a competing branch pathway gene to reduce competitive pathway drain on precursor supply",
                "outcome": "production titer increased relative to parent strain",
            }],
        )
        with tempfile.TemporaryDirectory() as d:
            result = execute(req, {"state_dir": d})
        self.assertTrue(result["canonical_knowledge_objects"])
        self.assertTrue(result["frontend_view"])
        self.assertTrue(result["knowledge_graph"]["nodes"])
        for link in result["paper_case_links"]:
            self.assertIn("requires human review", link["transferability"])

    def test_no_target_organism_does_not_block_level1_to_4(self):
        req = request([source(read_fixture("en_feedback_inhibition.md"))],
                       requested_output_level=["level4_cross_source_fusion"], target_organism=[])
        with tempfile.TemporaryDirectory() as d:
            result = execute(req, {"state_dir": d})
        self.assertNotEqual(result["status"], "FAILED")
        self.assertTrue(result["biological_concepts"] or result["biological_mechanisms"])


if __name__ == "__main__":
    unittest.main()

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from helpers import read_fixture  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parents[1].parent / "skills"))
from step02_source_validation.skill import execute as step02  # noqa: E402
from step05_document_parsing.skill import execute as step05  # noqa: E402
from step06_scope_selection.skill import execute as step06  # noqa: E402
from step07_basic_knowledge_extraction.skill import execute as step07  # noqa: E402
from step08_principle_distillation.skill import execute as step08  # noqa: E402


def run_through_step05(raw_text, source_type="textbook"):
    vs = step02({"source_ref": {"source_id": "src_1", "source_ref_type": "text", "raw_text": raw_text,
                                  "bibliographic": {"title": "Fixture Book", "isbn": ["1"], "edition": "1st", "source_type": source_type}}})["output"]
    ss = step05({"validated_source": vs, "raw_text": raw_text})["output"]
    scope = step06({"source_structure": ss, "target_domain": [], "target_engineering_goal": ["increase flux"]})["output"]
    return step07({"source_structure": ss, "extraction_scope": scope, "validated_source": vs})


class Step05Extraction(unittest.TestCase):
    def setUp(self):
        self.text = read_fixture("en_feedback_inhibition.md")
        self.result = run_through_step05(self.text)

    def test_definitions_become_concepts_not_mechanisms(self):
        concepts = self.result["output"]["concepts"]
        self.assertTrue(any("feedback inhibition" in c["name_en"].lower() for c in concepts))

    def test_causal_sentences_become_mechanisms_with_direction(self):
        mechanisms = self.result["output"]["mechanisms"]
        self.assertTrue(mechanisms)
        self.assertTrue(all(m["causal_direction"] in {"positive", "negative", "unspecified"} for m in mechanisms))

    def test_no_organism_is_ever_fabricated(self):
        for obj in self.result["output"]["concepts"] + self.result["output"]["mechanisms"]:
            for org in obj["organism_scope"]:
                self.assertIn(org, {"Escherichia coli", "Saccharomyces cerevisiae", "eukaryote (unspecified)", "prokaryote (unspecified)"})
        # this fixture never names an organism - scope must stay empty, never default to E. coli K-12
        for obj in self.result["output"]["concepts"] + self.result["output"]["mechanisms"]:
            self.assertEqual(obj["organism_scope"], [])


class Step06PrincipleHonesty(unittest.TestCase):
    def test_principle_without_explicit_recommendation_is_model_inference(self):
        step05_out = run_through_step05(read_fixture("en_feedback_inhibition.md"))["output"]
        result = step08({"concepts": step05_out["concepts"], "mechanisms": step05_out["mechanisms"],
                          "target_engineering_goal": ["increase flux"], "target_organism": [], "target_strain": []})
        principles = result["output"]["engineering_principles"]
        self.assertTrue(principles)
        for p in principles:
            # the fixture text only *describes* mechanisms, it never says
            # "consider X" - so every derived principle must be flagged as
            # the model's own inference, not something the textbook stated.
            self.assertEqual(p["derivation_type"], "model_inference")
            self.assertTrue(p["requires_human_review"])
            self.assertTrue(p["evidence"])

    def test_every_principle_has_do_not_generalize_clause(self):
        step05_out = run_through_step05(read_fixture("en_feedback_inhibition.md"))["output"]
        result = step08({"concepts": step05_out["concepts"], "mechanisms": step05_out["mechanisms"],
                          "target_engineering_goal": [], "target_organism": [], "target_strain": []})
        for p in result["output"]["engineering_principles"]:
            self.assertTrue(p["do_not_generalize_to"])


if __name__ == "__main__":
    unittest.main()

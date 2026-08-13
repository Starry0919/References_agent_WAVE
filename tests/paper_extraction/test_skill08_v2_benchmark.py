import json
from pathlib import Path

from harness.paper_extraction.vendor.skills.skill08_evidence_binding.verification import semantic_support


def test_skill08_v2_synthetic_benchmark_has_zero_false_verified_critical_claims():
    fixture = Path(__file__).with_name("fixtures") / "skill08_v2_benchmark.json"
    cases = json.loads(fixture.read_text(encoding="utf-8"))["cases"]
    predicted = [{**case, "actual": semantic_support(case["claim"], case["evidence"])[0]} for case in cases]
    false_verified = [x for x in predicted if x["critical"] and x["actual"] == "passed" and x["expected"] != "passed"]
    true_verified = [x for x in predicted if x["actual"] == x["expected"] == "passed"]
    predicted_verified = [x for x in predicted if x["actual"] == "passed"]
    precision = len(true_verified) / max(1, len(predicted_verified))
    unresolved_rate = sum(x["actual"] == "unresolved" for x in predicted) / len(predicted)
    assert precision == 1.0
    assert false_verified == []
    assert unresolved_rate >= 0

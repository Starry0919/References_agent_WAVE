from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path: sys.path.insert(0, str(ROOT))

from harness.paper_extraction.vendor.skills.skill08_evidence_binding.biological_entity_resolution import BiologicalObjectGraph, compare_biological_context
from harness.paper_extraction.vendor.skills.skill08_evidence_binding.verification import semantic_support


def predict(case):
    context = case["experiment_context"]
    if context["source_attribution"] in {"background_citation", "included_study"}:
        return "unsupported", "experiment attribution error"
    if context["claim_experiment_id"] != context["evidence_experiment_id"]:
        return "unsupported", "experiment attribution error"
    graph = BiologicalObjectGraph({"paragraphs": [{"paragraph_id": "evidence", "section": "results", "text": case["candidate_evidence"]}]})
    bio = compare_biological_context(case["claim"], case["candidate_evidence"], graph, "evidence")
    if bio["status"] == "failed": return "unsupported", "entity error"
    semantic, reasons = semantic_support(case["claim"], case["candidate_evidence"], augmented_pair=(bio["claim_augmented"], bio["evidence_augmented"]))
    if context["source_attribution"] in {"author_inference", "model_inference"} and any(w in case["claim"].casefold() for w in ("demonstrated", "proved", "caused")):
        return "conflicted", "causal strength error"
    if semantic == "passed" and bio["status"] == "passed": return "verified", ""
    if semantic == "conflicted":
        reason = "numeric error" if any("numeric" in r or "unit" in r for r in reasons) else "direction error" if any("direction" in r or "negation" in r for r in reasons) else "causal strength error"
        return "conflicted", reason
    if semantic == "failed": return "unsupported", "entity error"
    return "unresolved", "coreference error" if bio["status"] == "unresolved" else "condition error"


def evaluate(cases):
    rows=[]
    for case in cases:
        predicted,error=predict(case);rows.append({**case,"predicted":predicted,"error_type":error})
    verified=[r for r in rows if r["predicted"]=="verified"]
    gold_verified=[r for r in rows if r["gold_verification"]=="verified"]
    tp=sum(r["gold_verification"]=="verified" for r in verified)
    false_verified=[r for r in verified if r["gold_verification"]!="verified" and r["critical"]]
    correct=sum(r["predicted"]==r["gold_verification"] for r in rows)
    attribution_cases=[r for r in rows if r["category"] in {"background_confusion","strain_lineage","gene_modification_confusion","control_treatment","source_attribution","cross_experiment"}]
    unresolved=[r for r in rows if r["predicted"]=="unresolved"]
    return rows,{"cases":len(rows),"verification_precision":tp/max(1,len(verified)),"verification_recall":tp/max(1,len(gold_verified)),"overall_accuracy":correct/max(1,len(rows)),"attribution_accuracy":sum(r["predicted"]==r["gold_verification"] for r in attribution_cases)/max(1,len(attribution_cases)),"false_verified_critical_claims":len(false_verified),"unresolved_rate":len(unresolved)/max(1,len(rows)),"reasonable_unresolved":sum(r["gold_verification"]=="unresolved" for r in unresolved),"optimizable_unresolved":sum(r["gold_verification"]!="unresolved" for r in unresolved),"error_taxonomy":dict(Counter(r["error_type"] for r in rows if r["predicted"]!=r["gold_verification"]))}


def main():
    base=Path(__file__).resolve().parents[1]
    cases=json.loads((base/"cases"/"real_paper_cases.json").read_text(encoding="utf-8"))["cases"]
    rows,metrics=evaluate(cases)
    (base/"reports").mkdir(exist_ok=True)
    (base/"reports"/"benchmark_results.json").write_text(json.dumps({"metrics":metrics,"cases":rows},ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps(metrics,ensure_ascii=False))


if __name__ == "__main__": main()

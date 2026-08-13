try:
    from .schema import PHASES
except ImportError:
    from schema import PHASES
def validate(output):
    plans, ai = output.get("engineering_plans", []), output.get("ai_combination_proposals", [])
    all_steps = [s for p in plans for phase in PHASES for s in p["dbtl_plan"][phase]]
    ai_steps = [s for p in ai for phase in PHASES for s in p["dbtl_plan"][phase]]
    checks = [
        {"name": "source_separation", "passed": all(s["source_type"] == "reported_in_literature" for s in all_steps) and all(s["source_type"] == "ai_generated_proposal" for s in ai_steps)},
        {"name": "reported_evidence_coverage", "passed": all(s["evidence"] for s in all_steps)},
        {"name": "ai_explanation_complete", "passed": all(p["design_rationale"].get("reasoning") and p["design_rationale"].get("supporting_evidence") and p["design_rationale"].get("uncertainty") for p in ai)},
        {"name": "dbtl_complete", "passed": all(all(p["dbtl_plan"].get(x) for x in PHASES) for p in plans + ai)},
        {"name": "human_governance", "passed": not ai or output["approval_status"]["approval_required"]},
        {"name": "no_invented_level3", "passed": all(p["design_rationale"].get("suggestion_level") != 3 for p in ai)},
    ]
    return checks

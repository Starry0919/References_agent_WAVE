"""Step07 - turn a principle's own preconditions/alternatives into a decision rule.

A decision tree is only ever built here when the underlying engineering
principle already lists at least one precondition and one alternative -
the branch condition is literally the principle's own
required_preconditions[0], and the two leaves are its own
recommended_actions[0] and alternatives[0]. Nothing is invented beyond
that, but because no source text spells out "first check X, then choose
Y or Z" as an explicit decision procedure, every rule here is
derivation_type=model_inference and human_review_status=pending
(SKILL.md Step07 note 1 and 5).
"""
from __future__ import annotations

VERSION = "0.1.0"


def execute(request, **kwargs):
    principles = request.get("engineering_principles", [])
    decision_rules, decision_trees = [], []
    seq = 0

    for p in principles:
        preconditions = p.get("required_preconditions", [])
        actions = p.get("recommended_actions", [])
        alternatives = p.get("alternatives", [])
        if not preconditions or not actions:
            continue
        seq += 1
        primary_precondition = preconditions[0]
        recommended = actions[0]
        rejected = alternatives[:1]
        rule_id = f"{p['principle_id']}:decision:{seq}"

        branches = [{
            "condition": f"{primary_precondition} holds",
            "recommended_option": recommended,
            "reasoning": p.get("engineering_objective", [""])[0],
        }]
        if alternatives:
            branches.append({
                "condition": f"{primary_precondition} does NOT hold, or a contraindication applies ({'; '.join(p.get('contraindications', [])) or 'unspecified'})",
                "recommended_option": alternatives[0],
                "reasoning": "fallback consistent with the principle's own listed alternatives",
            })

        decision_rules.append({
            "decision_rule_id": rule_id,
            "decision_topic": p.get("name_en") or p.get("name_zh"),
            "question_zh": f"是否满足：{primary_precondition}？",
            "question_en": f"Is the precondition satisfied: {primary_precondition}?",
            "inputs": preconditions,
            "decision_conditions": [primary_precondition],
            "branches": branches,
            "recommended_option": [recommended],
            "rejected_options": rejected,
            "reasoning_basis": p.get("biological_basis", []),
            "required_measurements": p.get("validation_requirements", []),
            "uncertainty": p.get("do_not_generalize_to", []),
            "evidence": p.get("evidence", []),
            "derivation_type": "model_inference",
            "confidence": min(0.5, p.get("confidence", 0.4)),
            "human_review_status": "pending",
        })
        decision_trees.append({
            "tree_id": rule_id,
            "root_question": f"{primary_precondition}?",
            "branches": [
                {"condition": "yes", "leaf": recommended},
                {"condition": "no_or_contraindicated", "leaf": alternatives[0] if alternatives else "no validated alternative in source; escalate to human review"},
            ],
            "derivation_type": "model_inference",
        })

    return {
        "output": {"decision_rules": decision_rules, "decision_trees": decision_trees},
        "status": "needs_review" if decision_rules else "succeeded",
        "errors": [],
        "provenance": {"step_version": VERSION, "source_ids": sorted({p["principle_id"].split(":", 1)[0] for p in principles})},
    }

"""Step10 - lift each engineering principle into a design pattern, a
validation strategy and a failure pattern, instead of only keeping the
"it works" half (SKILL.md Step10 closing warning: "不要只抽成功策略").
Every object here is a reshaping of fields the principle already carries
(SKILL.md 十一.10: repetition across many textbooks never becomes proof by
itself); nothing new is asserted.
"""
from __future__ import annotations

VERSION = "0.1.0"


def execute(request, **kwargs):
    principles = request.get("engineering_principles", [])
    patterns, validations, failures = [], [], []

    for p in principles:
        pid = p["principle_id"]
        patterns.append({
            "pattern_id": f"{pid}:pattern",
            "name_zh": p.get("name_zh", ""), "name_en": p.get("name_en", ""),
            "problem_context": p.get("trigger_conditions", []),
            "design_intent": p.get("engineering_objective", [""])[0] if p.get("engineering_objective") else "",
            "canonical_structure": p.get("recommended_actions", []),
            "biological_rationale": p.get("biological_basis", []),
            "applicable_conditions": p.get("required_preconditions", []),
            "non_applicable_conditions": p.get("contraindications", []),
            "common_variants": p.get("alternatives", []),
            "known_tradeoffs": p.get("possible_side_effects", []),
            "validation_strategy_ids": [f"{pid}:validation"],
            "failure_pattern_ids": [f"{pid}:failure"] if p.get("failure_conditions") or p.get("possible_side_effects") else [],
            "supporting_principles": [pid],
            "supporting_sources": [e.get("knowledge_id") for e in p.get("evidence", [])],
            "supporting_paper_cases": [],
            "maturity": "candidate",
            "confidence": p.get("confidence", 0.4),
        })

        validations.append({
            "validation_strategy_id": f"{pid}:validation",
            "target_claim": p.get("name_en") or p.get("name_zh"),
            "minimum_validation": p.get("validation_requirements", [])[:1],
            "recommended_validation": p.get("validation_requirements", []),
            "orthogonal_validation": [],
            "negative_controls": ["unmodified parent strain/construct"],
            "positive_controls": [],
            "time_scale": [],
            "readouts": p.get("validation_requirements", []),
            "acceptance_criteria": [],
            "failure_interpretation": p.get("failure_conditions", []),
            "limitations": ["derived from a textbook engineering principle, not from a specific validated protocol"],
            "evidence": p.get("evidence", []),
        })

        if p.get("failure_conditions") or p.get("possible_side_effects"):
            failures.append({
                "failure_pattern_id": f"{pid}:failure",
                "name_zh": "", "name_en": f"Failure modes of {p.get('name_en') or p.get('name_zh')}",
                "trigger_conditions": p.get("failure_conditions", []),
                "observed_symptoms": p.get("possible_side_effects", []),
                "possible_causes": p.get("contraindications", []),
                "diagnostic_measurements": p.get("validation_requirements", []),
                "mitigation_options": p.get("alternatives", []),
                "prevention_options": p.get("required_preconditions", []),
                "scope": p.get("organism_scope", []),
                "evidence": p.get("evidence", []),
                "confidence": p.get("confidence", 0.4),
            })

    return {
        "output": {"design_patterns": patterns, "validation_strategies": validations, "failure_patterns": failures},
        "status": "succeeded", "errors": [],
        "provenance": {"step_version": VERSION, "source_ids": sorted({p["principle_id"].split(":", 1)[0] for p in principles})},
    }

"""Hypothesis Assessor / Conditional Ranker (doc03 4.8): structured,
sourced, sensitivity-checkable assessment - never an uncalibrated single
score. `ProjectObjective` is never imported here (doc03 2.7/2.9's
diagnosis/engineering-value separation - enforced structurally, not just
by convention).

`assess_hypothesis`'s rule-out logic implements doc03 2.4 exactly: a
hypothesis only reaches `provisionally_ruled_out` when a contradicting
result coincides with ALL of a predeclared discriminating prediction,
sufficient measurement sensitivity, valid controls, condition match, and a
review of alternative explanations - never on a single negative result
alone.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

# Ordering used only to sort assessments for display/ranking - not a
# probability scale.
_STATUS_ORDER = {
    "strongly_supported": 0, "weakly_supported": 1, "untested": 2, "non_discriminating": 3,
    "weakened": 4, "out_of_scope": 5, "provisionally_ruled_out": 6,
}


@dataclass
class AssessmentInput:
    hypothesis_id: str
    supporting_links: list[dict[str, Any]] = field(default_factory=list)
    contradicting_links: list[dict[str, Any]] = field(default_factory=list)
    is_consistent_links: list[dict[str, Any]] = field(default_factory=list)
    non_discriminating_links: list[dict[str, Any]] = field(default_factory=list)
    observations_explained_count: int = 0
    observations_total_count: int = 0


@dataclass
class Assessment:
    hypothesis_id: str
    explanatory_coverage: dict[str, Any]
    contradictions: list[str]
    evidence_quality: str
    evidence_directness: str
    condition_match: str
    robustness: str
    testability: str
    remaining_uncertainty: str
    status: str
    rationale_references: list[str]


def assess_hypothesis(
    inp: AssessmentInput,
    *,
    has_predeclared_discriminating_prediction: bool,
    has_sufficient_measurement_sensitivity: bool,
    has_valid_controls: bool,
    condition_matches: bool,
    alternatives_reviewed: bool,
) -> Assessment:
    total = inp.observations_total_count
    coverage_ratio = (inp.observations_explained_count / total) if total else 0.0
    contradictions = [l.get("claim", "") for l in inp.contradicting_links]

    qualities = [l.get("quality", "low") for l in inp.supporting_links]
    evidence_quality = "high" if "high" in qualities else ("medium" if "medium" in qualities else "low")
    directness_vals = [l.get("directness", "indirect") for l in inp.supporting_links]
    evidence_directness = "direct" if "direct" in directness_vals else "indirect"

    can_rule_out = (
        has_predeclared_discriminating_prediction and has_sufficient_measurement_sensitivity
        and has_valid_controls and condition_matches and alternatives_reviewed
    )

    if inp.contradicting_links and can_rule_out:
        status = "provisionally_ruled_out"
    elif inp.contradicting_links:
        status = "weakened"  # contradicted, but not rigorously enough to rule out (doc03 2.4)
    elif inp.non_discriminating_links and not inp.supporting_links:
        status = "non_discriminating"
    elif not inp.supporting_links and not inp.contradicting_links:
        status = "untested"
    elif coverage_ratio >= 0.6 and evidence_quality in ("high", "medium"):
        status = "strongly_supported"
    else:
        status = "weakly_supported"

    robustness = "high" if (evidence_quality == "high" and condition_matches) else ("medium" if inp.supporting_links else "low")
    testability = "high" if has_predeclared_discriminating_prediction else "low"

    return Assessment(
        hypothesis_id=inp.hypothesis_id,
        explanatory_coverage={"explained": inp.observations_explained_count, "total": total, "ratio": coverage_ratio},
        contradictions=contradictions,
        evidence_quality=evidence_quality,
        evidence_directness=evidence_directness,
        condition_match="matched" if condition_matches else "unknown",
        robustness=robustness,
        testability=testability,
        remaining_uncertainty="structured qualitative levels only - not a calibrated numeric probability (doc03 3.7)",
        status=status,
        rationale_references=[l.get("evidence_item_id", "") for l in inp.supporting_links + inp.contradicting_links],
    )


def rank_hypotheses(assessments: list[Assessment]) -> list[Assessment]:
    """Conditional ranking: status tier first, explanatory coverage as an
    explicit, inspectable tie-break within a tier - not a hidden weighted
    sum."""
    return sorted(assessments, key=lambda a: (_STATUS_ORDER.get(a.status, 99), -a.explanatory_coverage["ratio"]))

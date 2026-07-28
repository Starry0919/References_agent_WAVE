"""Doc 12.1's 5-step update, steps 1-3 (expectation matching, observation
comparison, failure classification). Step 4 (hypothesis revision) is
`harness.learning.service.revise_hypothesis` (already gated); step 5
(redesign generation) is `harness.learning.redesign`.

`classify_outcome` is what keeps `Trp ↑10%, growth ↓40%` from ever being
simplified to a bare "success" (doc 12.3): a target-metric improvement
combined with a constraint-violating side effect is classified `tradeoff`,
never an unqualified win, and construction/measurement problems are
checked FIRST so a technical failure can never masquerade as a biological
result.
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class MetricComparison:
    metric: str
    expected_direction: str  # increase|decrease|maintain
    observed_value: float
    baseline_value: float | None
    percent_change: float | None
    direction_met: bool | None  # None if no baseline available to compare against
    within_constraint: bool = True
    constraint_note: str = ""


@dataclass
class OutcomeAssessment:
    metric_comparisons: list[MetricComparison] = field(default_factory=list)
    failure_class: str | None = None  # None means: no FailureCase warranted (unconditional success)
    causal_confidence: str = "low"
    candidate_causes: list[str] = field(default_factory=list)
    is_tradeoff: bool = False
    is_unconditional_success: bool = False


def compare_metric(
    *,
    metric: str,
    expected_direction: str,
    observed_value: float,
    baseline_value: float | None,
    constraint_max_percent_drop: float | None = None,
) -> MetricComparison:
    if baseline_value is None or baseline_value == 0:
        return MetricComparison(
            metric=metric, expected_direction=expected_direction, observed_value=observed_value,
            baseline_value=baseline_value, percent_change=None, direction_met=None,
        )
    percent_change = (observed_value - baseline_value) / abs(baseline_value) * 100
    if expected_direction == "increase":
        direction_met = percent_change > 0
    elif expected_direction == "decrease":
        direction_met = percent_change < 0
    else:  # "maintain"
        direction_met = abs(percent_change) < 5

    within_constraint = True
    constraint_note = ""
    if constraint_max_percent_drop is not None and percent_change < -constraint_max_percent_drop:
        within_constraint = False
        constraint_note = f"{metric} dropped {abs(percent_change):.1f}%, exceeding the {constraint_max_percent_drop}% constraint"

    return MetricComparison(
        metric=metric, expected_direction=expected_direction, observed_value=observed_value,
        baseline_value=baseline_value, percent_change=percent_change, direction_met=direction_met,
        within_constraint=within_constraint, constraint_note=constraint_note,
    )


def classify_outcome(
    *,
    comparisons: list[MetricComparison],
    data_qc_passed: bool,
    genotype_verified: bool,
    candidate_causes: list[str] | None = None,
) -> OutcomeAssessment:
    causes = list(candidate_causes or [])

    # Technical checks first: a construction/measurement problem is never
    # allowed to masquerade as biological signal (doc 10.2/18.3).
    if not genotype_verified:
        return OutcomeAssessment(
            metric_comparisons=comparisons, failure_class="construction", causal_confidence="low",
            candidate_causes=causes + ["genotype not verified - result cannot be attributed to the planned design"],
        )
    if not data_qc_passed:
        return OutcomeAssessment(
            metric_comparisons=comparisons, failure_class="measurement", causal_confidence="low",
            candidate_causes=causes + ["data QC failed - result cannot be used as biological evidence"],
        )

    violated = [c for c in comparisons if not c.within_constraint]
    met = [c for c in comparisons if c.direction_met is True]
    unmet = [c for c in comparisons if c.direction_met is False]

    if violated:
        return OutcomeAssessment(
            metric_comparisons=comparisons, failure_class="tradeoff", causal_confidence="medium",
            candidate_causes=causes + [c.constraint_note for c in violated], is_tradeoff=True,
        )
    if unmet and not met:
        return OutcomeAssessment(
            metric_comparisons=comparisons, failure_class="biological_null", causal_confidence="medium", candidate_causes=causes,
        )
    if met and not unmet and not violated:
        return OutcomeAssessment(
            metric_comparisons=comparisons, failure_class=None, causal_confidence="medium",
            candidate_causes=causes, is_unconditional_success=True,
        )
    return OutcomeAssessment(metric_comparisons=comparisons, failure_class="inconclusive", causal_confidence="low", candidate_causes=causes)

"""Diagnosis Evaluator / Critic (doc03 4.15): checks for missed
alternatives, undeclared class exclusions, unsupported certainty, temporal-
state mixing, objective contamination of diagnostic assessment, and
premature rule-outs. Can only flag issues and request revision - it is
never itself a source of evidence, and never auto-fixes anything.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from harness.diagnosis.hypothesis_generator import MECHANISM_CLASSES

_OVERCLAIMING_STATUSES = {"definitively_proven", "true_bottleneck"}


@dataclass
class EvaluatorFinding:
    code: str
    message: str
    severity: str = "warning"  # warning|error


@dataclass
class EvaluatorReport:
    findings: list[EvaluatorFinding] = field(default_factory=list)

    @property
    def has_blocking_issues(self) -> bool:
        return any(f.severity == "error" for f in self.findings)


def evaluate_diagnosis(
    *,
    represented_classes: set[str],
    excluded_classes: set[str],
    assessed_statuses: set[str],
    mixed_timepoints_without_scope: bool,
    objective_referenced_in_assessment: bool,
    rule_out_without_sufficient_conditions: bool,
) -> EvaluatorReport:
    findings: list[EvaluatorFinding] = []

    missing = set(MECHANISM_CLASSES) - represented_classes - excluded_classes
    if missing:
        findings.append(EvaluatorFinding(
            "missing_alternative_class", f"classes {sorted(missing)} are neither represented nor explicitly excluded", severity="error",
        ))

    overclaiming = assessed_statuses & _OVERCLAIMING_STATUSES
    if overclaiming:
        findings.append(EvaluatorFinding(
            "unsupported_certainty", f"status value(s) {sorted(overclaiming)} claim definitive proof, which this system must never assign", severity="error",
        ))

    if mixed_timepoints_without_scope:
        findings.append(EvaluatorFinding(
            "temporal_state_mixing", "observations from different timepoints/conditions were combined without an explicit temporal_scope", severity="error",
        ))

    if objective_referenced_in_assessment:
        findings.append(EvaluatorFinding(
            "objective_contamination", "ProjectObjective appears to have influenced diagnostic assessment, not just engineering value", severity="error",
        ))

    if rule_out_without_sufficient_conditions:
        findings.append(EvaluatorFinding(
            "premature_rule_out",
            "a hypothesis was ruled out without predeclared prediction, sufficient measurement sensitivity, valid "
            "controls, condition match, and alternatives review all present",
            severity="error",
        ))

    return EvaluatorReport(findings=findings)

"""Diagnostic Test Selector (doc03 4.10): transparent, structured
qualitative selection - deliberately NOT a pseudo-precise Bayesian expected-
information-gain calculation this round (doc03 explicitly tolerates a
structured qualitative v1). A test that cannot discriminate between the
remaining hypotheses is flagged `non_discriminating` and never selected.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

_RANK = {"high": 3, "medium": 2, "low": 1, "unknown": 0}


@dataclass
class CandidateTest:
    test_id: str
    compared_hypothesis_ids: list[str]
    discriminates_hypotheses: bool
    expected_information_gain: str = "unknown"  # high|medium|low|unknown
    cost: str = "unknown"
    turnaround: str = "unknown"
    availability: str = "unknown"
    technical_feasibility: str = "unknown"
    risk: str = "unknown"


@dataclass
class TestSelectionResult:
    selected: CandidateTest | None
    pareto_set: list[CandidateTest] = field(default_factory=list)
    non_discriminating: list[CandidateTest] = field(default_factory=list)
    rationale: str = ""


def _score(c: CandidateTest) -> tuple[int, int, int, int, int]:
    return (
        _RANK.get(c.expected_information_gain, 0),
        -_RANK.get(c.cost, 0),  # lower cost preferred
        _RANK.get(c.availability, 0),
        _RANK.get(c.technical_feasibility, 0),
        -_RANK.get(c.risk, 0),  # lower risk preferred
    )


def _pareto_front(candidates: list[CandidateTest]) -> list[CandidateTest]:
    scored = [(c, _score(c)) for c in candidates]
    front = []
    for c, v in scored:
        dominated = any(o is not c and all(ov >= cv for ov, cv in zip(ov_vec, v)) and ov_vec != v for o, ov_vec in scored)
        if not dominated:
            front.append(c)
    return front


def select_diagnostic_test(candidates: list[CandidateTest], *, time_cost_constraint: dict[str, Any] | None = None) -> TestSelectionResult:
    non_discriminating = [c for c in candidates if not c.discriminates_hypotheses]
    discriminating = [c for c in candidates if c.discriminates_hypotheses]
    if not discriminating:
        return TestSelectionResult(selected=None, non_discriminating=non_discriminating, rationale="no candidate test discriminates between the remaining hypotheses")

    ranked = sorted(discriminating, key=_score, reverse=True)
    pareto = _pareto_front(discriminating)
    return TestSelectionResult(
        selected=ranked[0], pareto_set=pareto, non_discriminating=non_discriminating,
        rationale=f"selected for the best (information_gain, cost, availability, feasibility, risk) combination among {len(discriminating)} discriminating candidate(s)",
    )

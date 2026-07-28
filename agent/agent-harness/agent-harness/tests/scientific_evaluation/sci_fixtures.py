"""Shared setup helpers for the Problem-05 test suite: builds on top of
Problem 04's own real fixture (`tests/engineering_design/fixtures.py::
handoff_through_portfolio`) rather than re-deriving a parallel one - doc05
§8's own instruction that Problem 05's input must be Problem 04's real
output.
"""
from __future__ import annotations

from tests.engineering_design.fixtures import handoff_through_portfolio

from harness.engineering_design.evaluation_service import evaluate_portfolio
from harness.scientific_evaluation import service as sci_service


def build_evaluated_portfolio(session, *, actor_id: str = "pi", chassis: str = "E. coli"):
    proj, portfolio, candidates = handoff_through_portfolio(session, actor_id=actor_id, chassis=chassis)
    evaluate_portfolio(session, portfolio_id=portfolio.portfolio_id, actor_id="system")
    return proj, portfolio, candidates


def run_full_scientific_evaluation(session, *, actor_id: str = "pi"):
    proj, portfolio, candidates = build_evaluated_portfolio(session, actor_id=actor_id)
    result = sci_service.run_scientific_evaluation(session, portfolio_id=portfolio.portfolio_id, actor_id=actor_id)
    return proj, portfolio, candidates, result

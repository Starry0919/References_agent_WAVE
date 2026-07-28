"""Workflow orchestrator for the V0.1 synthetic biology design pipeline.

Main Agent -> Workflow Orchestrator -> modules, run sequentially, each
reading and writing the shared SynBioState. Mirrors the revised reasoning
chain from workflow/design/V0.1_20260720/V0.1.md section 1:

    observation -> hypothesis -> evidence -> engineering action
        -> expected effect -> validation

realized as: task understanding -> literature (DDRs) -> pathway analysis
-> competition-pathway analysis -> key node analysis -> engineering design
(ranked) -> evidence evaluation -> evaluator (accept/reject/warn) -> report.
"""
from __future__ import annotations

from workflows.synbio_v01.modules import (
    competition,
    engineering,
    evaluator,
    evidence,
    literature,
    node_analysis,
    pathway,
    report,
    task_parser,
)
from workflows.synbio_v01.state import SynBioState


def run(request: str) -> SynBioState:
    """Run the full V0.1 pipeline for one natural-language design request."""
    state = SynBioState(request=request)

    state.task = task_parser.parse(state.request)
    state.literature_records = literature.get_records(state.task["product"])
    state.pathway = pathway.analyze(state.task)
    state.competition_analysis = competition.analyze(state.task)
    state.nodes = node_analysis.identify(state.pathway, state.literature_records)
    state.engineering_designs = engineering.design(state.nodes, state.literature_records)
    state.evidence = evidence.evaluate(state.engineering_designs, state.literature_records)
    state.evaluation = evaluator.evaluate(state.engineering_designs, state.evidence, state.competition_analysis)
    state.final_report = report.generate(state)

    return state

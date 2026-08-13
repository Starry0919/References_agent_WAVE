"""Workflow orchestrator for the V1 evidence-grounded synthetic biology design pipeline.

User -> Language Controller -> Task Understanding -> Knowledge Retrieval Layer
-> Biological Reasoning Workflow -> Engineering Design -> Evidence Grounding
-> Final Report Generator (spec section 6).

The Language Controller is not a module here: it lives at the agent/chat
level (harness/config.py's system prompt), since this pipeline itself
speaks in DDR-sourced English biology - see workflows/synbio_v1/__init__.py
and the V1 spec section 4.
"""
from __future__ import annotations

from workflows.synbio_v1.modules import diagnosis, engineering, evidence, report, retriever, task_parser, validation
from workflows.synbio_v1.state import SynBioV1State


def run(request: str) -> SynBioV1State:
    """Run the full V1 pipeline for one natural-language design request."""
    state = SynBioV1State(request=request)

    state.task = task_parser.parse(state.request)
    state.retrieval = retriever.retrieve(state.request, state.task)
    state.diagnosis = diagnosis.diagnose(state.retrieval)
    state.engineering_actions = engineering.design(state.retrieval)
    state.evidence = evidence.evaluate(state.retrieval, state.engineering_actions, state.task)
    state.validation_plan = validation.build_validation_plan(state.engineering_actions)
    state.final_report = report.generate(state)

    return state

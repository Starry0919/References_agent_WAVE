"""Workflow Engine: the deterministic control skeleton for the synbio agent.

Problem 01 scope (see workflow/design/evolution/后端精修/问题01_...md): the
Workflow Engine controls stage/state/permission/gate transitions; the
per-stage implementation (today: deterministic code reusing
workflows/synbio_v1/modules/*; future: LLM-backed local reasoning) only
proposes within its current stage's permitted scope. `controller.py` is the
single writer of `WorkflowRun.current_stage` - nothing else in this package
or its callers may set it directly.
"""

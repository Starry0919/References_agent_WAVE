# Gold Annotation Workbench Design

Silver extraction is initialized into a review document. Humans correct
ExperimentInstance object/intervention/condition/measurement/outcome bindings,
atomic claim correctness and evidence, DDR Q1/Q2/Q3/trigger/rationale, and
knowledge admission. The finalizer refuses to emit Gold unless review is
`HUMAN_REVIEWED`, adjudication is `ADJUDICATED`, and a named reviewer is supplied.

This is an executable lifecycle in `annotations/workbench.py`, not merely a JSON
template. Codex output remains Silver until the human workflow completes.

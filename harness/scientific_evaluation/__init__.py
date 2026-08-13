"""Problem 05 (Evaluator & Scientific Critic): Scientific Evaluation &
Decision Governance Layer for the Synthetic Biology Agent.

Consumes Problem 04's real output (`DesignPortfolio` / `CandidateDesign` /
`BuildTestPackage`) and closes the loop doc05 demands: deterministic
validation -> evidence transferability review -> model/tool honesty check
-> independent, adversarial scientific critique -> multi-objective/Pareto
candidate comparison -> meta-review synthesis -> revision task generation
-> Human Gate -> append-only Memory writeback. See `harness/scientific_
evaluation/service.py::run_scientific_evaluation` for the orchestrating
entry point and `workflow/design/evolution/后端精修/问题05_实施报告.md`
for the full audit, architecture, and test evidence.
"""

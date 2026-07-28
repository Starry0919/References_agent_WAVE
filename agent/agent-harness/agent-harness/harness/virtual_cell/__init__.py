"""Problem 06 - Predictive Simulation Loop & Virtual Cell Integration.

Connects a gated, versioned engineering design (Problem 04's
`harness.designs.models.DesignVersion`) to a real, adapter-executed cell
model, produces a baseline-vs-counterfactual prediction with explicit
applicability/uncertainty, and closes the loop through experimental
residuals into governed model-update proposals - never an LLM-guessed
numeric phenotype change.

See package docstrings in `models.py`, `adapters.py`, `compiler.py`,
`service.py` for the concrete audit trail of what is real (cobrapy GEM/FBA)
vs. honestly unavailable (vEcoli, kinetic/resource-allocation).
"""
from __future__ import annotations

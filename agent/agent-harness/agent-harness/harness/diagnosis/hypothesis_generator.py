"""Competing Hypothesis Generator (doc03 4.4): deterministic, rule-based
generation (matching Problem 01's precedent of testable, reproducible
stage logic rather than live non-deterministic LLM calls inside the
pipeline - `generation_provenance` records `"rule_based_v1"` so a future
LLM-backed generator can be swapped in without breaking callers).

Always attempts all four doc03 2.2 mechanism classes; a class with no
basis in the current graph/context is recorded in `excluded_classes` with
an explicit reason, never silently absent.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from harness.diagnosis.mechanism_graph import MechanismGraph
from harness.i18n import t

MECHANISM_CLASSES = ("biological_mechanism", "process_environment", "measurement_data", "model_mismatch")

_ENV_FIELDS = ("oxygenation", "temperature_c", "pH", "medium", "carbon_source", "process_phase", "process_mode")


@dataclass
class GeneratedHypothesis:
    statement: str
    mechanism_class: str
    causal_graph_nodes: list[str]
    causal_graph_edges: list[dict[str, Any]]
    observations_explained: list[str]
    discriminating_predictions: list[dict[str, str]]
    falsifiers: list[str]
    assumptions: list[str]
    applicability_context: dict[str, Any]
    temporal_scope: dict[str, Any] | None
    generation_provenance: dict[str, Any] = field(default_factory=dict)


@dataclass
class ExcludedMechanismClass:
    mechanism_class: str
    reason: str


@dataclass
class HypothesisGenerationResult:
    hypotheses: list[GeneratedHypothesis] = field(default_factory=list)
    excluded_classes: list[ExcludedMechanismClass] = field(default_factory=list)


def generate_competing_hypotheses(
    *,
    graph: MechanismGraph,
    observation_ids: list[str],
    context: dict[str, Any],
    has_reference_model: bool,
    qc_concerns: list[str] | None = None,
) -> HypothesisGenerationResult:
    result = HypothesisGenerationResult()
    qc_concerns = qc_concerns or []

    bio_nodes = [n for n in graph.nodes if n.node_type in ("process", "regulation", "pathway", "gene", "enzyme")]
    if bio_nodes:
        for node in bio_nodes[:3]:  # cap: mechanism diversity, not an exhaustive enumeration of every graph node
            edges = [
                {"source_id": e.source_id, "target_id": e.target_id, "edge_type": e.edge_type, "source_ref": e.source_ref}
                for e in graph.edges if e.source_id == node.node_id
            ]
            result.hypotheses.append(GeneratedHypothesis(
                statement=t("hyp.biological_mechanism.statement", label=node.label),
                mechanism_class="biological_mechanism",
                causal_graph_nodes=[node.node_id, "phenotype:0"],
                causal_graph_edges=edges,
                observations_explained=list(observation_ids),
                discriminating_predictions=[{
                    "if_true": f"a targeted, validated perturbation of {node.label} shifts the phenotype in the predicted direction",
                    "if_false": "no shift, or a shift inconsistent with this mechanism",
                }],
                falsifiers=[f"phenotype unchanged after a specific, validated perturbation of {node.label}"],
                assumptions=["the DDR-sourced mechanism transfers to the current host/condition"],
                applicability_context=dict(context), temporal_scope=None,
                generation_provenance={"method": "rule_based_v1", "source": node.source},
            ))
    else:
        result.excluded_classes.append(ExcludedMechanismClass(
            "biological_mechanism",
            "no biological-mechanism graph nodes available (no matching knowledge-base entry) - "
            "not generating a mechanism-specific hypothesis rather than fabricating one",
        ))

    env_factors = [(k, context.get(k)) for k in _ENV_FIELDS if context.get(k) is not None]
    if env_factors:
        for k, v in env_factors[:2]:
            result.hypotheses.append(GeneratedHypothesis(
                statement=t("hyp.process_environment.statement", field=k, value=repr(v)),
                mechanism_class="process_environment", causal_graph_nodes=["phenotype:0"], causal_graph_edges=[],
                observations_explained=list(observation_ids),
                discriminating_predictions=[{
                    "if_true": f"varying {k} within a validated range shifts the phenotype",
                    "if_false": "phenotype is unchanged across that range",
                }],
                falsifiers=[f"phenotype unchanged across a validated range of {k}"],
                assumptions=[f"{k} was recorded accurately for the observation(s) in question"],
                applicability_context=dict(context), temporal_scope=None,
                generation_provenance={"method": "rule_based_v1"},
            ))
    else:
        result.excluded_classes.append(ExcludedMechanismClass(
            "process_environment", "no process/environment context fields (oxygenation/temperature/medium/etc.) were provided",
        ))

    # Always representable: doc03 2.2 explicitly forbids a silent absence
    # of the measurement/data class.
    result.hypotheses.append(GeneratedHypothesis(
        statement=t("hyp.measurement_data.statement"),
        mechanism_class="measurement_data", causal_graph_nodes=["measurement:0", "phenotype:0"], causal_graph_edges=[],
        observations_explained=list(observation_ids),
        discriminating_predictions=[{
            "if_true": "an independent, matched-QC re-measurement changes the result",
            "if_false": "re-measurement reproduces the original result",
        }],
        falsifiers=["an independently QC'd replicate reproduces the original measurement"],
        assumptions=["a re-measurement is technically feasible"],
        applicability_context=dict(context), temporal_scope=None,
        generation_provenance={"method": "rule_based_v1", "qc_concerns": qc_concerns},
    ))

    if has_reference_model:
        result.hypotheses.append(GeneratedHypothesis(
            statement=t("hyp.model_mismatch.statement"),
            mechanism_class="model_mismatch", causal_graph_nodes=["model:0", "phenotype:0"], causal_graph_edges=[],
            observations_explained=list(observation_ids),
            discriminating_predictions=[{
                "if_true": "correcting the suspected model boundary/objective changes the prediction to match observation",
                "if_false": "the corrected model still predicts the same (wrong) outcome",
            }],
            falsifiers=["a corrected model boundary/objective still predicts the same outcome as before"],
            assumptions=["the reference expectation used a specific, identifiable model boundary or objective"],
            applicability_context=dict(context), temporal_scope=None,
            generation_provenance={"method": "rule_based_v1"},
        ))
    else:
        result.excluded_classes.append(ExcludedMechanismClass(
            "model_mismatch", "no reference model/prediction was used to generate the expectation being compared against",
        ))

    return result

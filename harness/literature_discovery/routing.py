from __future__ import annotations

from typing import Any

from .classification import LiteratureClassification


def _values(axis): return {x.value for x in axis.labels}


def route(classification: LiteratureClassification | dict[str, Any]):
    c = classification if isinstance(classification, LiteratureClassification) else LiteratureClassification.model_validate(classification)
    form, design, strength = _values(c.publication_form), _values(c.research_design), _values(c.evidence_strength)
    contributions = _values(c.knowledge_contributions)
    if c.classification_conflict: value = "MANUAL_REVIEW_ROUTE"
    elif form & {"REVIEW", "NARRATIVE_REVIEW", "SYSTEMATIC_REVIEW", "SCOPING_REVIEW", "META_ANALYSIS", "SYSTEMATIC_REVIEW_WITH_META_ANALYSIS", "STATE_OF_THE_ART_REVIEW", "MINI_REVIEW", "CRITICAL_REVIEW", "METHODOLOGICAL_REVIEW", "TECHNOLOGY_REVIEW"}: value = "REVIEW_SYNTHESIS_ROUTE"
    elif form & {"DATABASE_PAPER", "RESOURCE_PAPER", "DATA_PAPER"}: value = "RESOURCE_ROUTE"
    elif form & {"SOFTWARE_PAPER"} or "SOFTWARE_DEVELOPMENT" in design: value = "SOFTWARE_ROUTE"
    elif form & {"METHODS_PAPER", "PROTOCOL"} or "METHOD_DEVELOPMENT" in design: value = "METHOD_ROUTE"
    elif form & {"BENCHMARK_PAPER"} or "BENCHMARK" in design: value = "BENCHMARK_ROUTE"
    elif design & {"DATABASE_CONSTRUCTION", "RESOURCE_CONSTRUCTION"}: value = "RESOURCE_ROUTE"
    elif design & {"COMPUTATIONAL", "MODEL_DEVELOPMENT", "MODEL_VALIDATION", "IN_SILICO_DESIGN"} and "WET_LAB_EXPERIMENTAL" not in design: value = "MODEL_ROUTE"
    elif "WET_LAB_EXPERIMENTAL" in design or strength & {"DIRECT_PRIMARY_EVIDENCE", "SUPPORTING_PRIMARY_EVIDENCE"}: value = "PRIMARY_EXPERIMENTAL_ROUTE"
    else: value = "BACKGROUND_ROUTE"
    evidence = [*sorted(form), *sorted(design), *sorted(contributions), *sorted(strength)]
    confidence = "LOW" if c.classification_conflict else "HIGH" if any(x.labels[0].confidence == "HIGH" for x in [c.publication_form,c.research_design]) else "MEDIUM"
    return {"contract_version": "literature-route/2.0", "value": value, "confidence": confidence,
            "reasons": evidence[:8], "classification_id": c.classification_id}


def ranking_score(candidate, desired=None):
    relevance = candidate.relevance.score if candidate.relevance else 0
    classification = candidate.final_classification or candidate.metadata_classification
    route_value = (candidate.route or {}).get("value")
    strength = _values(LiteratureClassification.model_validate(classification).evidence_strength) if classification else set()
    direct = .12 if "DIRECT_PRIMARY_EVIDENCE" in strength else .06 if "SUPPORTING_PRIMARY_EVIDENCE" in strength else 0
    route_bonus = .08 if route_value == "PRIMARY_EXPERIMENTAL_ROUTE" else .04 if route_value == "REVIEW_SYNTHESIS_ROUTE" else 0
    fulltext = .04 if candidate.acquisition.local_path or candidate.oa_urls else 0
    desired_bonus = 0
    for axis, wanted in (desired or {}).items():
        if not classification or not wanted: continue
        desired_bonus += .03 * bool(_values(getattr(LiteratureClassification.model_validate(classification), axis)) & set(wanted))
    return round(min(1, .76 * relevance + direct + route_bonus + fulltext + desired_bonus), 4)

"""Claim inventory extraction (doc05 §4.1/§3.2): reads a frozen
`CandidateDesign`'s own declared, versioned fields - mechanism, causal
chain, genetic modifications, safety flags, model requests, build/test
targets - into individually source-typed `ScientificClaim` rows. Never
invents a claim the Designer did not actually assert, and never upgrades a
Designer-asserted mechanism into anything stronger than `llm_hypothesis`
unless it is already backed by a typed evidence link (doc05 §2.2: "禁止
...将 LLM 推断写成文献结论").
"""
from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from harness.engineering_design.models import BuildTestPackage, CandidateDesign
from harness.ids import new_id, now
from harness.scientific_evaluation.models import ScientificClaim

# Problem 04's `evidence_links[].source_type` vocabulary (see
# `harness/engineering_design/evaluators/evidence.py::_SOURCE_TYPE_TO_TIER`)
# mapped onto doc05 §2.2's stricter 7-way vocabulary. Anything unmapped
# falls back to `llm_hypothesis` - the least-supported, never silently
# upgraded default (doc05 §2.2).
_P4_EVIDENCE_SOURCE_TO_CLAIM_SOURCE = {
    "experimental_evidence": "experimental_observation",
    "model_computation": "computational_model",
    "curated_knowledge": "database_record",
    "diagnosis_hypothesis": "llm_hypothesis",
    "expert_or_llm_judgment": "llm_hypothesis",
}


def _claim_source_for_links(evidence_links: list[dict[str, Any]]) -> tuple[str, list[str]]:
    """Picks the *weakest* mapped source type present (never the strongest)
    so a claim backed by one experimental link and one bare llm-judgment
    link is not silently reported as fully experimental-grade - and returns
    the raw reference strings for `source_references`."""
    if not evidence_links:
        return "llm_hypothesis", []
    mapped = [_P4_EVIDENCE_SOURCE_TO_CLAIM_SOURCE.get(l.get("source_type", ""), "llm_hypothesis") for l in evidence_links]
    # SOURCE_TYPES is not itself an ordinal strength ladder, so "weakest" is
    # defined narrowly here as: llm_hypothesis if ANY link is llm_hypothesis,
    # else the first mapped type - conservative, never averages upward.
    weakest = "llm_hypothesis" if any(m == "llm_hypothesis" for m in mapped) else mapped[0]
    refs = [str(l.get("reference", "")) for l in evidence_links if l.get("reference")]
    return weakest, refs


def extract_claims(session: Session, *, evaluation_id: str, candidate: CandidateDesign) -> list[ScientificClaim]:
    claims: list[ScientificClaim] = []
    ts = now()

    def _add(text: str, claim_type: str, source_type: str, refs: list[str], position: int | None = None,
              scope: dict | None = None, supports: str = "supports") -> None:
        claims.append(ScientificClaim(
            claim_id=new_id("CLAIM"), evaluation_id=evaluation_id, design_id=candidate.design_id,
            design_version=candidate.design_version, claim_text=text, claim_type=claim_type,
            causal_chain_position=position, source_type=source_type, source_references=refs,
            scope_conditions=scope or {}, supports_or_opposes=supports, uncertainty="unknown",
            status="open", created_at=ts,
        ))

    if candidate.expected_mechanism:
        mech_links = [l for m in candidate.genetic_modifications for l in m.get("evidence_links", [])] or list(candidate.evidence_links)
        source, refs = _claim_source_for_links(mech_links)
        _add(candidate.expected_mechanism, "mechanism", source, refs)

    for i, step in enumerate(candidate.causal_chain):
        _add(str(step), "mechanism", "llm_hypothesis", [], position=i)

    for m in candidate.genetic_modifications:
        source, refs = _claim_source_for_links(m.get("evidence_links", []))
        text = f"{m.get('operation', 'unknown')} of {m.get('target_identifier', 'unknown')} advances the candidate's declared strategy"
        _add(text, "expected_phenotype", source, refs, scope={"target": m.get("target_identifier"), "operation": m.get("operation")})

    for flag in candidate.safety_flags:
        _add(str(flag), "risk", "expert_judgment", [])

    if candidate.buildability_assessment:
        summary = candidate.buildability_assessment.get("summary") or str(candidate.buildability_assessment)
        _add(summary, "buildability", "deterministic_rule", [])

    for req in candidate.counterfactual_requests:
        _add(f"model prediction requested: {req}", "model_prediction", "computational_model", [])

    if candidate.build_test_package_id is not None:
        pkg = session.get(BuildTestPackage, candidate.build_test_package_id)
        if pkg is not None:
            for rule in pkg.decision_rules:
                _add(str(rule), "experimental_discriminator", "deterministic_rule", [])

    for c in claims:
        session.add(c)
    session.flush()
    return claims

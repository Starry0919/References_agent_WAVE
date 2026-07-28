"""Prompt §5.8/§5.9: pure, deterministic condition-matching tests - no
network, no LLM. Cross-strain and cross-species evidence must never be
silently treated as a direct match."""
from __future__ import annotations

from harness.evidence_retrieval.condition_matching import EvidenceSide, MatchContext, compute_match


def test_direct_match_same_organism_strain_condition():
    query = MatchContext(
        organism="Escherichia coli", strain="K-12 MG1655", genotype="wild-type", medium="M9", condition={"carbon_source": "glucose"},
        timepoint={"value": 24, "unit": "h"}, intervention="ppc overexpression", measurement="growth_rate",
    )
    evidence = EvidenceSide(
        organism="Escherichia coli", strain="K-12 MG1655", genotype="wild-type", medium="M9", condition={"carbon_source": "glucose"},
        timepoint={"value": 24, "unit": "h"}, intervention="ppc overexpression", measurement="growth_rate", directness="direct",
    )
    result = compute_match(query, evidence)
    assert result.overall_match_status == "direct_match"
    assert result.organism_match == "match"
    assert not result.downgrade_reasons


def test_cross_species_evidence_is_downgraded_never_direct():
    query = MatchContext(organism="Escherichia coli", strain="K-12")
    evidence = EvidenceSide(organism="Saccharomyces cerevisiae", strain="BY4741")
    result = compute_match(query, evidence)
    assert result.overall_match_status == "cross_species"
    assert any("cross-species" in r for r in result.downgrade_reasons)
    assert result.directness == "indirect"


def test_cross_strain_evidence_is_downgraded_never_direct():
    query = MatchContext(organism="Escherichia coli", strain="K-12 MG1655")
    evidence = EvidenceSide(organism="Escherichia coli", strain="BL21(DE3)")
    result = compute_match(query, evidence)
    assert result.overall_match_status == "cross_strain"
    assert result.organism_match == "match"
    assert result.strain_match == "mismatch"


def test_condition_mismatch_downgrades_even_with_same_organism_and_strain():
    query = MatchContext(organism="Escherichia coli", strain="K-12", medium="M9", condition={"carbon_source": "glucose"})
    evidence = EvidenceSide(organism="Escherichia coli", strain="K-12", medium="LB", condition={"carbon_source": "glycerol"})
    result = compute_match(query, evidence)
    assert result.overall_match_status == "condition_mismatch"


def test_endpoint_mismatch_when_measurement_differs():
    query = MatchContext(organism="Escherichia coli", strain="K-12", measurement="titer")
    evidence = EvidenceSide(organism="Escherichia coli", strain="K-12", measurement="growth_rate")
    result = compute_match(query, evidence)
    assert result.overall_match_status == "endpoint_mismatch"


def test_insufficient_metadata_when_almost_everything_unknown():
    query = MatchContext()
    evidence = EvidenceSide()
    result = compute_match(query, evidence)
    assert result.overall_match_status == "insufficient_metadata"


def test_timepoint_unit_mismatch_is_never_silently_compared():
    query = MatchContext(organism="E. coli", strain="K-12", timepoint={"value": 24, "unit": "h"})
    evidence = EvidenceSide(organism="E. coli", strain="K-12", timepoint={"value": 24, "unit": "min"})
    result = compute_match(query, evidence)
    assert result.timepoint_match == "mismatch"

"""Legal/illegal stage output vs the pydantic contracts (SchemaGate's
underlying enforcement mechanism) - doc 7.1's first required unit-test
category."""
from __future__ import annotations

import pytest
from pydantic import ValidationError

from harness.workflow.contracts import (
    BiologicalState,
    EngineeringDecision,
    OperationType,
    TargetEntity,
    TargetEntityType,
    TaskSpec,
)


def test_task_spec_accepts_legal_shape() -> None:
    spec = TaskSpec(
        raw_request="Improve E. coli K-12 L-tryptophan production from glucose.",
        product="L-tryptophan",
        host="E. coli K-12",
        substrate="glucose",
        goal="increase production",
        engineering_type="rational metabolic engineering",
    )
    assert spec.product == "L-tryptophan"
    assert spec.missing_fields == []


def test_task_spec_rejects_unknown_field() -> None:
    with pytest.raises(ValidationError):
        TaskSpec(
            raw_request="x",
            product="x",
            host="x",
            substrate="x",
            goal="x",
            engineering_type="x",
            not_a_real_field="oops",  # type: ignore[call-arg]
        )


def test_task_spec_rejects_missing_required_field() -> None:
    with pytest.raises(ValidationError):
        TaskSpec(raw_request="x", product="x", host="x", substrate="x")  # type: ignore[call-arg]


def test_biological_state_unknown_fields_are_explicit_not_omitted() -> None:
    bs = BiologicalState()
    assert bs.host.species == "unknown"
    assert bs.host.strain == "unknown"
    assert bs.phenotype.target_product == "unknown"
    # never a bare empty dict / unconstrained structure
    assert bs.model_dump()["host"] == {"species": "unknown", "strain": "unknown", "reference_genome_version": "unknown"}


def test_engineering_decision_requires_target_entity_and_operation() -> None:
    with pytest.raises(ValidationError):
        EngineeringDecision(mechanism="m", expected_effect="e")  # type: ignore[call-arg]


def test_engineering_decision_rejects_illegal_operation_enum() -> None:
    with pytest.raises(ValidationError):
        EngineeringDecision(
            target_entity=TargetEntity(type=TargetEntityType.gene, canonical_id="ptsG", display_name="ptsG"),
            operation="delete_the_whole_genome",  # type: ignore[arg-type]
            mechanism="m",
            expected_effect="e",
        )


def test_engineering_decision_legal_shape_round_trips_through_json() -> None:
    decision = EngineeringDecision(
        target_entity=TargetEntity(type=TargetEntityType.gene, canonical_id="ptsG", display_name="ptsG"),
        operation=OperationType.knockout,
        mechanism="reduce PEP consumption",
        expected_effect="more PEP available",
        evidence_record_ids=["EVID-1"],
    )
    restored = EngineeringDecision.model_validate_json(decision.model_dump_json())
    assert restored == decision

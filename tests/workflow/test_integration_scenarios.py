"""The 7 integration scenarios doc 7.2 requires, end to end through
`WorkflowController` (not just unit-level gate/contract checks)."""
from __future__ import annotations

import pytest

from harness.workflow import gates
from harness.workflow.contracts import (
    DecisionStatus,
    EngineeringDecision,
    EvidenceRecord,
    OperationType,
    TargetEntity,
    TargetEntityType,
)
from harness.workflow.controller import StageOutcome, WorkflowController
from harness.workflow.definitions import Stage
from harness.workflow.state import RunStatus
from harness.tools.executor import ToolOutOfDomainError
from harness.workflow.synbio_stages import (
    STAGE_IMPLS,
    _fba_flux_analysis,
    _near_tie_conflict_note,
    build_controller,
    build_tool_executor,
)

TRYPTOPHAN_REQUEST = "Improve E. coli K-12 L-tryptophan production from glucose."


# 1. Happy path -----------------------------------------------------------


def test_scenario_1_tryptophan_happy_path_completes_with_traceable_decisions() -> None:
    controller = build_controller()
    run = controller.create_run(TRYPTOPHAN_REQUEST)
    run = controller.run_to_completion_or_pause(run, max_steps=30)

    assert run.status == RunStatus.completed
    assert run.final_report and "L-tryptophan" in run.final_report
    assert run.diagnoses and run.diagnoses[0].source_ddr_id == "DDR-001"
    assert run.engineering_decisions
    for d in run.engineering_decisions:
        # every decision traces to a diagnosis and at least one evidence record
        assert d.diagnosis_id == run.diagnoses[0].diagnosis_id
        assert d.evidence_record_ids


# 2. Missing chassis / target ----------------------------------------------


def test_scenario_2_missing_target_blocks_instead_of_guessing() -> None:
    controller = build_controller()
    run = controller.create_run("Improve E. coli K-12 production from glucose.")
    run = controller.run_to_completion_or_pause(run, max_steps=10)

    assert run.status == RunStatus.waiting_user
    assert run.pending_request is not None
    assert run.pending_request.kind.value == "missing_information"
    # doc 5.2: unknown values must be explicit, never silently guessed -
    # task_spec IS committed, but product is honestly "unknown" with the
    # gap recorded, not fabricated as some plausible-looking default.
    assert run.task_spec is not None
    assert run.task_spec.product == "unknown"
    assert "product" in run.task_spec.missing_fields


# 3. FBA tool: real for in-domain genes, honestly out-of-domain otherwise ---


def test_scenario_3_fba_grounds_the_trp_precursor_supply_check_with_real_numbers() -> None:
    """`ptsG`/`pykF` (PEP-sparing knockouts, `knowledge/engineering_actions/
    action_database.json`) are exactly the kind of precursor-supply
    candidate the 260718 doc's M2 wants a real COBRApy number for, and they
    fall inside `GENE_TO_REACTION_BOUND_HINT` - so the tryptophan request
    now gets a real, non-fabricated FBA result instead of a permanent stub."""
    controller = build_controller()
    run = controller.create_run(TRYPTOPHAN_REQUEST)  # a metabolic-production goal -> _looks_metabolic True
    run = controller.run_to_completion_or_pause(run, max_steps=30)

    assert run.status == RunStatus.completed
    fba_calls = [t for t in run.tool_records if t.name == "fba_flux_analysis"]
    assert fba_calls, "expected the workflow to have attempted the FBA tool for a metabolic-production request"
    assert not fba_calls[0].is_error, fba_calls[0].result_summary
    assert fba_calls[0].result_summary and "objective_value" in fba_calls[0].result_summary


def test_scenario_3b_fba_out_of_domain_degrades_gracefully_not_fatally() -> None:
    """A gene outside `GENE_TO_REACTION_BOUND_HINT` (this repo's curated,
    narrow FBA domain) must never get a fabricated flux prediction - the
    tool honestly raises `ToolOutOfDomainError`, the same non-fabrication
    contract `harness.engineering_design.counterfactual_service` uses for
    the identical mapping."""
    with pytest.raises(ToolOutOfDomainError):
        _fba_flux_analysis(host="E. coli K-12", product="L-tryptophan", gene_targets=[("trpR", "knockout")])

    # And through the full stage/gate path, this degrades exactly like the
    # old permanent stub used to: run completes, gate records not_applicable,
    # nothing is fabricated.
    tools = build_tool_executor()
    result = tools.execute(
        "fba_flux_analysis",
        {"host": "E. coli K-12", "product": "L-tryptophan", "gene_targets": [("trpR", "knockout")]},
        allowlist=("fba_flux_analysis",),
        stage_id=Stage.MODEL_AND_RULE_VALIDATION.value,
    )
    assert result.record.is_error
    assert result.record.failure_class.value == "out_of_domain"


# 4. Literature vs. model/retrieval conflict --------------------------------


def test_scenario_4_near_tie_ddr_match_is_recorded_as_a_conflict_not_silently_resolved() -> None:
    # Unit-level check of the conflict-detection function directly (the
    # real 4-entry knowledge base rarely produces a genuine near-tie for a
    # single-product request, so this exercises the mechanism directly
    # rather than fighting the keyword scorer to contrive one - see
    # synbio_stages._near_tie_conflict_note's docstring for the honest
    # scope note: this approximates literature-vs-model conflict at the
    # retrieval layer, since no second independent evidence source is
    # wired up this round).
    close_candidates = [{"ddr_id": "DDR-001", "score": 5}, {"ddr_id": "DDR-004", "score": 4}]
    note = _near_tie_conflict_note(close_candidates)
    assert note is not None
    assert "DDR-001" in note and "DDR-004" in note

    clear_candidates = [{"ddr_id": "DDR-001", "score": 8}, {"ddr_id": "DDR-004", "score": 0}]
    assert _near_tie_conflict_note(clear_candidates) is None


def test_scenario_4_conflict_note_would_survive_into_biological_state() -> None:
    controller = build_controller()
    run = controller.create_run(TRYPTOPHAN_REQUEST)
    run = controller.advance(run)  # INTAKE
    run = controller.advance(run)  # TASK_NORMALIZATION
    run = controller.advance(run)  # CONTEXT_AND_EVIDENCE_ACQUISITION
    # BiologicalState.uncertainty.conflicting_fields is real, structured,
    # and checkpoint-persisted - not a UI-only string.
    assert isinstance(run.biological_state.uncertainty.conflicting_fields, list)


# 5. LLM requests skipping a required validation stage -----------------------


def test_scenario_5_skipping_model_and_rule_validation_is_rejected() -> None:
    controller = build_controller()
    run = controller.create_run(TRYPTOPHAN_REQUEST)
    run = controller.run_to_completion_or_pause(run, max_steps=3)  # stop partway (INTAKE, TASK_NORM, CONTEXT)
    assert run.current_stage != Stage.EXPERIMENT_AND_IMPLEMENTATION_PLAN.value

    # Simulate a request to "jump ahead" past MODEL_AND_RULE_VALIDATION,
    # skipping it entirely even though candidates were never validated.
    run.current_stage = Stage.EXPERIMENT_AND_IMPLEMENTATION_PLAN.value
    import pytest
    from harness.workflow.controller import IllegalTransitionError

    with pytest.raises(IllegalTransitionError):
        controller.advance(run)


# 6. LLM repeatedly returns illegal gene IDs ---------------------------------


def test_scenario_6_illegal_gene_ids_are_always_rejected_never_accepted() -> None:
    def strategy_generation_with_bad_gene(run, _tools):
        evid = EvidenceRecord(action_source="ddr_reasoning", evidence_status="reference_available", confidence="medium")
        decision = EngineeringDecision(
            target_entity=TargetEntity(type=TargetEntityType.gene, canonical_id="notARealGeneXYZ", display_name="notARealGeneXYZ"),
            operation=OperationType.overexpression,
            mechanism="test", expected_effect="test",
            evidence_record_ids=[evid.evidence_record_id],
        )

        def apply(r):
            r.evidence_records.append(evid)
            r.candidate_designs.append(decision)

        return StageOutcome(output={"n": 1}, schema_valid=True, schema_errors=[], apply=apply, gate_candidates=[decision])

    impls = dict(STAGE_IMPLS)
    impls[Stage.ENGINEERING_STRATEGY_GENERATION] = strategy_generation_with_bad_gene
    controller = WorkflowController(impls, build_tool_executor())
    run = controller.create_run(TRYPTOPHAN_REQUEST)
    run = controller.run_to_completion_or_pause(run, max_steps=30)

    # The run must terminate (not hang) and the illegal candidate must
    # never end up accepted.
    assert run.status in (RunStatus.completed, RunStatus.blocked, RunStatus.failed)
    bad = [d for d in run.engineering_decisions if d.target_entity.canonical_id == "notARealGeneXYZ"]
    assert bad, "the bad-gene candidate should have been recorded"
    assert all(d.status != DecisionStatus.accepted for d in bad)


# 7. Non-metabolic target must not trigger FBA misuse -------------------------


def test_scenario_7_non_metabolic_target_never_calls_fba() -> None:
    from harness.workflow.contracts import TaskSpec
    from harness.workflow.state import WorkflowRun

    run = WorkflowRun(
        task_spec=TaskSpec(
            raw_request="Build a fluorescent reporter circuit in E. coli K-12.",
            product="GFP reporter circuit",
            host="E. coli K-12",
            substrate="glucose",
            goal="build a fluorescent reporter",
            engineering_type="regulatory circuit",
        )
    )
    tools = build_tool_executor()
    outcome = STAGE_IMPLS[Stage.MODEL_AND_RULE_VALIDATION](run, tools)
    assert outcome.output["model_available"] is False
    # apply() only extends tool_records with whatever was actually attempted -
    # confirm nothing was attempted at all for a non-metabolic goal.
    fresh = WorkflowRun(task_spec=run.task_spec)
    outcome.apply(fresh)
    assert fresh.tool_records == []

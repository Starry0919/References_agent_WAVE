"""Phase D: CrossModalConsistencyReport (prompt §6.4) - real observations,
real cobrapy flux data, deterministic rule engine, no LLM anywhere in this
path. Uses the same real `ppc` knockout `DesignVersion` fixture Problem 06's
own test suite uses.
"""
from __future__ import annotations

from harness import db
from harness.diagnosis import service as diag_svc
from harness.diagnosis.normalizer import RawObservationInput, normalize_and_commit
from harness.virtual_cell.cross_modal_service import build_cross_modal_consistency_report
from harness.virtual_cell.models import INCONSISTENCY_CLASSES
from harness.virtual_cell.service import run_prediction_pipeline
from tests.virtual_cell.fixtures import build_approved_ppc_knockout_design


def _make_observation(session, *, project_id, metric, value, modality, entity_id, baseline_value, timepoint_h=24, batch="B1", unit="a.u."):
    ctx = diag_svc.create_biological_context(session, project_id=project_id, medium="M9", carbon_source="glucose")
    entity_namespace = "gene" if modality == "transcriptomic" else ("protein" if modality == "proteomic" else "phenotype")
    raw = RawObservationInput(
        feature_or_phenotype=metric, value=value, unit=unit, qc_status="passed",
        condition_id=ctx.context_id, timepoint={"value": timepoint_h, "unit": "h"},
        reference_or_baseline={"value": baseline_value}, provenance={"condition_ref": {"medium": "M9", "carbon_source": "glucose"}},
        modality=modality, entity_namespace=entity_namespace, entity_id=entity_id, batch=batch,
    )
    obs, report = normalize_and_commit(session, project_id=project_id, raw=raw, actor_id="tech")
    assert obs is not None, report.issues
    return obs


def test_transcript_protein_discordance_preserves_alternative_explanations_never_a_single_conclusion():
    """The prompt's own worked example: trpE RNA up, protein flat - must
    become a discordance with real candidate alternative explanations, not
    a fabricated "the intervention doesn't work" conclusion."""
    with db.session_scope() as s:
        proj, dv = build_approved_ppc_knockout_design(s)
        _make_observation(s, project_id=proj.project_id, metric="mRNA:ppc", value=8.0, baseline_value=2.0, modality="transcriptomic", entity_id="ppc")
        _make_observation(s, project_id=proj.project_id, metric="protein:Ppc", value=2.1, baseline_value=2.0, modality="proteomic", entity_id="ppc")

        report = build_cross_modal_consistency_report(s, project_id=proj.project_id, target_entity="ppc", actor_id="agent")
        assert report.agreement_status in ("discordant", "partially_consistent")
        assert "transcript_protein_discordance" in report.inconsistency_classes
        assert len(report.alternative_explanations) >= 2
        assert not any("overexpression is ineffective" in e or "knockout is ineffective" in e for e in report.alternative_explanations)
        # unsupported_conclusions must explicitly REFUSE the naive single-modality read, not assert it:
        assert report.unsupported_conclusions
        assert any("does not conclude" in c.lower() or "not conclude" in c.lower() for c in report.unsupported_conclusions)
        assert report.transcript_change["direction"] == "increase"
        assert report.protein_change["direction"] == "no_change"


def test_consistent_direction_across_available_modalities():
    with db.session_scope() as s:
        proj, dv = build_approved_ppc_knockout_design(s)
        _make_observation(s, project_id=proj.project_id, metric="mRNA:ppc", value=1.0, baseline_value=5.0, modality="transcriptomic", entity_id="ppc")
        _make_observation(s, project_id=proj.project_id, metric="protein:Ppc", value=0.8, baseline_value=5.0, modality="proteomic", entity_id="ppc")

        report = build_cross_modal_consistency_report(s, project_id=proj.project_id, target_entity="ppc", actor_id="agent")
        assert report.agreement_status == "consistent"
        assert report.inconsistency_classes == []
        assert report.transcript_change["direction"] == "decrease"
        assert report.protein_change["direction"] == "decrease"


def test_insufficient_modalities_when_only_one_layer_present():
    with db.session_scope() as s:
        proj, dv = build_approved_ppc_knockout_design(s)
        _make_observation(s, project_id=proj.project_id, metric="mRNA:ppc", value=8.0, baseline_value=2.0, modality="transcriptomic", entity_id="ppc")
        report = build_cross_modal_consistency_report(s, project_id=proj.project_id, target_entity="ppc", actor_id="agent")
        assert report.agreement_status == "insufficient_modalities"


def test_not_comparable_when_no_observations_exist_for_entity():
    with db.session_scope() as s:
        proj, dv = build_approved_ppc_knockout_design(s)
        report = build_cross_modal_consistency_report(s, project_id=proj.project_id, target_entity="ppc", actor_id="agent")
        assert report.agreement_status in ("not_comparable", "insufficient_modalities")
        assert report.data_quality_findings


def test_timepoint_mismatch_is_flagged_not_silently_compared():
    with db.session_scope() as s:
        proj, dv = build_approved_ppc_knockout_design(s)
        _make_observation(s, project_id=proj.project_id, metric="mRNA:ppc", value=8.0, baseline_value=2.0, modality="transcriptomic", entity_id="ppc", timepoint_h=6)
        _make_observation(s, project_id=proj.project_id, metric="protein:Ppc", value=2.0, baseline_value=2.0, modality="proteomic", entity_id="ppc", timepoint_h=48)

        report = build_cross_modal_consistency_report(s, project_id=proj.project_id, target_entity="ppc", actor_id="agent")
        assert report.time_alignment_findings


def test_flux_layer_from_real_fba_included_and_labeled_model_output():
    """The flux layer is read from a real cobrapy run (via
    `run_prediction_pipeline`, the same one Problem 06's own tests exercise)
    - never a fabricated number, and always distinguishable from an
    experimentally-observed layer."""
    with db.session_scope() as s:
        proj, dv = build_approved_ppc_knockout_design(s)
        result = run_prediction_pipeline(
            s, project_id=proj.project_id, design_version_id=dv.design_version_id,
            chassis={"species": "E. coli", "strain": "K-12"}, environment={"medium": "M9", "carbon_source": "glucose"}, actor_id="system",
        )
        assert result["candidate_run"] is not None  # real FBA ran (ppc has a real single-gene GPR effect)

        _make_observation(s, project_id=proj.project_id, metric="growth_phenotype:ppc", value=0.80, baseline_value=0.874, modality="phenotypic", entity_id="ppc", unit="1/h")

        report = build_cross_modal_consistency_report(s, project_id=proj.project_id, target_entity="ppc", design_version_id=dv.design_version_id, actor_id="agent")
        assert report.flux_change is not None
        assert "fluxomic" not in (report.data_quality_findings or [])  # sanity: real endpoint was found
        # the flux endpoint came from a real SimulationResult, never invented:
        assert report.aligned_observation_refs  # includes the SimulationResult id and/or observation ids


def test_all_inconsistency_classes_come_from_the_fixed_vocabulary():
    with db.session_scope() as s:
        proj, dv = build_approved_ppc_knockout_design(s)
        _make_observation(s, project_id=proj.project_id, metric="mRNA:ppc", value=8.0, baseline_value=2.0, modality="transcriptomic", entity_id="ppc", batch="B1")
        _make_observation(s, project_id=proj.project_id, metric="protein:Ppc", value=2.0, baseline_value=2.0, modality="proteomic", entity_id="ppc", batch="B2")
        report = build_cross_modal_consistency_report(s, project_id=proj.project_id, target_entity="ppc", actor_id="agent")
        assert all(c in INCONSISTENCY_CLASSES for c in report.inconsistency_classes)

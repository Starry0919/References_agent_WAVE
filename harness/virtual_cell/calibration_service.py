"""Prediction Calibration Loop (doc06 §3.14/§9.6): computed by code from a
context/QC-matched `PredictionResidual` cohort. Sample counts below
`minimum_sample_requirement` cap `reliability_status` at
`insufficient_data`/`qualitative_only` - never `calibrated`, and never a
bare probability. `calibrated` is only reachable via `approve_profile`
(Human Gate), matching Level 3 update governance (doc06 §9.4).
"""
from __future__ import annotations

from harness.ids import new_id, now
from harness.memory import event_types as et
from harness.memory.event_store import append_event
from harness.virtual_cell.models import PredictionCalibrationProfile, PredictionResidual


def _metrics(residuals: list[PredictionResidual]) -> dict[str, float | None]:
    n = len(residuals)
    if n == 0:
        return {"bias": None, "mae": None, "rmse": None, "empirical_interval_coverage": None, "calibration_error": None}
    errors = [r.residual for r in residuals]
    bias = sum(errors) / n
    mae = sum(abs(e) for e in errors) / n
    rmse = (sum(e * e for e in errors) / n) ** 0.5
    return {"bias": bias, "mae": mae, "rmse": rmse, "empirical_interval_coverage": None, "calibration_error": None}


def build_calibration_profile(
    session, *, model_id: str, endpoint: str, residual_ids: list[str], calibration_dataset_version: str,
    minimum_sample_requirement: int = 5, model_version: str = "e_coli_core", artifact_hash: str | None = None, organism: str = "Escherichia coli",
    supersedes_profile_id: str | None = None,
) -> PredictionCalibrationProfile:
    if not residual_ids:
        raise ValueError("a calibration profile must cite at least one residual")

    residuals = [session.get(PredictionResidual, rid) for rid in residual_ids]
    included: list[PredictionResidual] = []
    excluded: list[str] = []
    for rid, r in zip(residual_ids, residuals):
        if r is None or r.endpoint != endpoint or not r.context_match:
            excluded.append(rid)
            continue
        included.append(r)

    n = len(included)
    if n < minimum_sample_requirement:
        reliability = "insufficient_data"
    elif n < 2 * minimum_sample_requirement:
        reliability = "qualitative_only"
    else:
        reliability = "provisionally_calibrated"  # only `approve_profile` may promote this to "calibrated"

    profile = PredictionCalibrationProfile(
        calibration_profile_id=new_id("CALIB"), model_id=model_id, model_version=model_version, artifact_hash=artifact_hash,
        endpoint=endpoint, organism=organism, strain_scope=[], condition_scope=[], perturbation_class_scope=[],
        calibration_method="empirical_residual_summary", calibration_dataset_version=calibration_dataset_version,
        included_residual_ids=[r.residual_id for r in included], excluded_residual_ids=excluded, sample_count=n,
        minimum_sample_requirement=minimum_sample_requirement, metrics=_metrics(included), reliability_status=reliability,
        validity_window=None, domain_limits=[], created_at=now(), status="active",
        supersedes_profile_id=supersedes_profile_id,
    )
    session.add(profile)
    session.flush()

    project_id = None
    if included:
        from harness.virtual_cell.models import SimulationCase

        case = session.get(SimulationCase, included[0].simulation_case_id)
        project_id = case.project_id if case else None
    if project_id:
        append_event(
            session, project_id=project_id, event_type=et.VC_CALIBRATION_PROFILE_BUILT, entity_type="PredictionCalibrationProfile",
            entity_id=profile.calibration_profile_id, payload={"model_id": model_id, "endpoint": endpoint, "sample_count": n, "reliability_status": reliability},
            actor_type="agent", actor_id="system",
        )
    return profile


def approve_profile(session, *, profile: PredictionCalibrationProfile, approver_id: str) -> PredictionCalibrationProfile:
    """Human Gate promotion: only a `provisionally_calibrated` profile with
    enough samples may become `calibrated` - never automatic."""
    if profile.reliability_status == "provisionally_calibrated" and profile.sample_count >= profile.minimum_sample_requirement:
        profile.reliability_status = "calibrated"
    profile.approved_by = approver_id
    session.flush()
    return profile


def supersede_profile(session, *, old_profile: PredictionCalibrationProfile, new_profile: PredictionCalibrationProfile) -> None:
    """doc06 §9.6: a model-version or distribution change must not silently
    reuse an old profile - the old row is marked superseded, never deleted
    or overwritten. `new_profile.supersedes_profile_id` must already point
    at `old_profile` (set at creation via `build_calibration_profile(...,
    supersedes_profile_id=...)` - that field is otherwise immutable, so it
    cannot be patched onto an existing row after the fact)."""
    if new_profile.supersedes_profile_id != old_profile.calibration_profile_id:
        raise ValueError("new_profile must have been created with supersedes_profile_id=old_profile.calibration_profile_id")
    old_profile.status = "superseded"
    session.flush()

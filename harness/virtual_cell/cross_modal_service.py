"""Cross-Modal Consistency (prompt §6.4): a deterministic rule engine - no
LLM anywhere in this module - that aligns transcript/protein/metabolite/
flux/phenotype observations for one entity and honestly classifies whether
they agree, preserving alternative explanations instead of collapsing a
discordance into a single causal story (the prompt's own worked example:
"trpE RNA↑, TrpE protein 未增加" must never become "trpE overexpression
无效").

Data sources, all real, none new:
- `harness.experiments.models.Observation` (extended with `modality`/
  `entity_id`/`batch`, migration 0008) for the transcript/protein/
  metabolite/phenotype layers.
- `harness.virtual_cell.models.SimulationResult.endpoints` (real cobrapy
  FBA output, `source_type="model_output"`) for the flux layer - a flux
  "observation" is not experimentally measured in this repo, so it is
  read from the model layer and labelled as such throughout, never
  presented as an experimental measurement.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from harness.experiments.models import Observation
from harness.ids import new_id, now
from harness.memory import event_types as et
from harness.memory.event_store import append_event
from harness.virtual_cell.models import CrossModalConsistencyReport

_MODALITY_ORDER = ("transcriptomic", "proteomic", "fluxomic", "phenotypic")
_TIMEPOINT_TOLERANCE_RATIO = 0.25


@dataclass
class ModalityChange:
    direction: str  # increase|decrease|no_change|unknown
    magnitude: float | None
    unit: str | None
    timepoint: dict[str, Any] | None
    condition_ref: dict[str, Any]
    batch: str | None
    observation_id: str | None
    detection_limit_flag: bool
    source_type: str  # observed|model_output


def _direction_from_values(value: float, baseline: float | None, *, noise_floor_ratio: float = 0.10) -> str:
    if baseline is None:
        return "unknown"
    if baseline == 0:
        return "unknown" if value == 0 else ("increase" if value > 0 else "decrease")
    ratio = (value - baseline) / abs(baseline)
    if abs(ratio) <= noise_floor_ratio:
        return "no_change"
    return "increase" if ratio > 0 else "decrease"


def _change_from_observation(obs: Observation) -> ModalityChange:
    baseline = (obs.reference_or_baseline or {}).get("value") if obs.reference_or_baseline else None
    direction = _direction_from_values(obs.value, baseline)
    near_detection_limit = obs.detection_limit is not None and abs(obs.value) <= abs(obs.detection_limit) * 1.5
    return ModalityChange(
        direction=direction, magnitude=(obs.value - baseline) if baseline is not None else None, unit=obs.unit,
        timepoint=obs.timepoint, condition_ref=obs.condition_ref or {}, batch=obs.batch, observation_id=obs.observation_id,
        detection_limit_flag=near_detection_limit, source_type="observed",
    )


def _change_from_flux_endpoint(endpoint: dict[str, Any], baseline_endpoint: dict[str, Any] | None) -> ModalityChange:
    baseline_value = baseline_endpoint.get("value") if baseline_endpoint else None
    direction = _direction_from_values(endpoint.get("value", 0.0), baseline_value)
    return ModalityChange(
        direction=direction, magnitude=(endpoint.get("value", 0.0) - baseline_value) if baseline_value is not None else None,
        unit=endpoint.get("unit"), timepoint=None, condition_ref={}, batch=None, observation_id=None,
        detection_limit_flag=False, source_type="model_output",
    )


def _timepoints_aligned(a: dict[str, Any] | None, b: dict[str, Any] | None) -> bool:
    if a is None or b is None:
        return True  # cannot assess -> not counted as a mismatch, counted as unknown elsewhere
    av, bv = a.get("value"), b.get("value")
    au, bu = a.get("unit"), b.get("unit")
    if av is None or bv is None:
        return True
    if au and bu and str(au).lower() != str(bu).lower():
        return False
    tolerance = max(abs(av) * _TIMEPOINT_TOLERANCE_RATIO, 1e-9)
    return abs(av - bv) <= tolerance


def _conditions_aligned(a: dict[str, Any], b: dict[str, Any]) -> bool:
    shared = set(a) & set(b)
    if not shared:
        return True
    return all(str(a[k]).lower() == str(b[k]).lower() for k in shared)


# Real interpretation table (prompt §6.4): each discordance class carries
# its own candidate alternative explanations - never a single forced story.
_DISCORDANCE_EXPLANATIONS: dict[str, list[str]] = {
    "transcript_protein_discordance": [
        "post-transcriptional/translational regulation limits protein output despite higher mRNA",
        "protein degradation rate increased, offsetting higher synthesis",
        "protein quantification method has insufficient sensitivity or dynamic range at this level",
        "construct/genotype does not translate the intended change into protein as designed",
    ],
    "protein_flux_discordance": [
        "this enzyme is not flux-controlling for the pathway step under these conditions (another step is rate-limiting)",
        "post-translational modification or allosteric regulation changes enzyme activity independent of abundance",
        "compensatory regulation elsewhere in the network redistributes flux",
        "the model does not include the regulatory/kinetic detail needed to predict flux from abundance alone",
    ],
    "flux_phenotype_discordance": [
        "resource/growth burden from the intervention offsets the predicted phenotypic benefit",
        "a downstream pathway step (not modeled) is actually limiting the phenotype",
        "phenotype assay sensitivity or timing does not capture the flux-level change",
        "compensatory regulation elsewhere in metabolism buffers the phenotypic outcome",
    ],
    "model_experiment_mismatch": [
        "the model's domain does not cover this intervention/endpoint combination (see CompatibilityReport)",
        "the experimental measurement and the model's steady-state assumption describe different physiological states",
    ],
}


def _classify_pair(name: str, upstream: ModalityChange | None, downstream: ModalityChange | None) -> tuple[list[str], list[str]]:
    """Returns `(inconsistency_classes, alternative_explanations)` for one
    adjacent modality pair. Both empty means the pair agrees (or cannot be
    compared, which is reported separately as missingness/unknown)."""
    if upstream is None or downstream is None:
        return [], []
    if upstream.direction in ("unknown",) or downstream.direction in ("unknown",):
        return [], []
    classes: list[str] = []
    explanations: list[str] = []
    if not _timepoints_aligned(upstream.timepoint, downstream.timepoint):
        classes.append("timepoint_mismatch")
    if not _conditions_aligned(upstream.condition_ref, downstream.condition_ref):
        classes.append("condition_mismatch")
    if upstream.batch and downstream.batch and upstream.batch != downstream.batch:
        classes.append("batch_effect")
    if upstream.detection_limit_flag or downstream.detection_limit_flag:
        classes.append("measurement_sensitivity")

    agree = (upstream.direction == downstream.direction) or (upstream.direction == "no_change" and downstream.direction == "no_change")
    directly_conflicting = (
        (upstream.direction == "increase" and downstream.direction == "decrease")
        or (upstream.direction == "decrease" and downstream.direction == "increase")
        or (upstream.direction in ("increase", "decrease") and downstream.direction == "no_change")
    )
    if not agree and directly_conflicting:
        classes.append(name)
        explanations.extend(_DISCORDANCE_EXPLANATIONS.get(name, []))
    return classes, explanations


def build_cross_modal_consistency_report(
    session: Session, *, project_id: str, target_entity: str, design_version_id: str | None = None,
    condition_filter: dict[str, Any] | None = None, actor_id: str,
) -> CrossModalConsistencyReport:
    obs_rows = session.execute(
        select(Observation).where(Observation.project_id == project_id, Observation.entity_id == target_entity)
    ).scalars().all()

    changes: dict[str, ModalityChange] = {}
    aligned_refs: list[str] = []
    data_quality_findings: list[str] = []
    for modality, key in (("transcriptomic", "transcript_change"), ("proteomic", "protein_change"), ("metabolomic", "metabolite_change"), ("phenotypic", "phenotype_change")):
        candidates = [o for o in obs_rows if o.modality == modality]
        if not candidates:
            continue
        candidates.sort(key=lambda o: o.created_at, reverse=True)
        obs = candidates[0]
        if obs.reference_or_baseline is None or "value" not in (obs.reference_or_baseline or {}):
            data_quality_findings.append(f"{modality} observation {obs.observation_id} has no baseline/reference value - direction reported as unknown")
        changes[modality] = _change_from_observation(obs)
        aligned_refs.append(obs.observation_id)

    flux_change: ModalityChange | None = None
    if design_version_id is not None:
        from harness.virtual_cell.models import SimulationCase, SimulationResult

        case = session.execute(
            select(SimulationCase).where(SimulationCase.design_version_id == design_version_id).order_by(SimulationCase.created_at.desc())
        ).scalars().first()
        if case is not None:
            # Real lookup: SimulationResult -> SimulationRun -> SimulationCase, filtered to this case's runs.
            from harness.virtual_cell.models import SimulationRun

            runs = session.execute(select(SimulationRun).where(SimulationRun.simulation_case_id == case.simulation_case_id)).scalars().all()
            runs_by_id = {r.model_run_id: r for r in runs}
            run_ids = list(runs_by_id)
            all_results = session.execute(select(SimulationResult).where(SimulationResult.model_run_id.in_(run_ids))).scalars().all() if run_ids else []
            baseline_result = next((r for r in all_results if runs_by_id[r.model_run_id].scenario_label == "S0_baseline"), None)
            candidate_result = next((r for r in all_results if runs_by_id[r.model_run_id].scenario_label != "S0_baseline"), None)
            if candidate_result is not None:
                endpoint = next((e for e in candidate_result.endpoints if e.get("name") == "growth_rate"), None)
                baseline_endpoint = next((e for e in (baseline_result.endpoints if baseline_result else []) if e.get("name") == "growth_rate"), None) if baseline_result else None
                if endpoint is not None:
                    flux_change = _change_from_flux_endpoint(endpoint, baseline_endpoint)
                    aligned_refs.append(candidate_result.simulation_result_id)
                else:
                    data_quality_findings.append("no growth_rate endpoint found in SimulationResult - flux layer omitted, not assumed no_change")
    if flux_change is not None:
        changes["fluxomic"] = flux_change

    present_modalities = [m for m in _MODALITY_ORDER if m in changes]
    inconsistency_classes: list[str] = []
    alternative_explanations: list[str] = []
    time_alignment_findings: list[str] = []
    _PAIR_NAMES = {
        ("transcriptomic", "proteomic"): "transcript_protein_discordance",
        ("proteomic", "fluxomic"): "protein_flux_discordance",
        ("fluxomic", "phenotypic"): "flux_phenotype_discordance",
    }
    any_pair_compared = False
    any_pair_agreed = False
    for i in range(len(_MODALITY_ORDER) - 1):
        up_key, down_key = _MODALITY_ORDER[i], _MODALITY_ORDER[i + 1]
        pair_name = _PAIR_NAMES.get((up_key, down_key))
        if pair_name is None or up_key not in changes or down_key not in changes:
            continue
        any_pair_compared = True
        classes, explanations = _classify_pair(pair_name, changes[up_key], changes[down_key])
        if "timepoint_mismatch" in classes:
            time_alignment_findings.append(f"{up_key} vs {down_key}: timepoints not aligned within tolerance")
        if pair_name not in classes and changes[up_key].direction != "unknown" and changes[down_key].direction != "unknown":
            any_pair_agreed = True
        for c in classes:
            if c not in inconsistency_classes:
                inconsistency_classes.append(c)
        for e in explanations:
            if e not in alternative_explanations:
                alternative_explanations.append(e)
    if flux_change is not None and flux_change.source_type == "model_output" and "phenotypic" in changes:
        # the flux layer is model-derived, never experimentally observed in this repo -
        # a discordance against the real phenotype must always be flagged distinctly.
        if "flux_phenotype_discordance" in inconsistency_classes and "model_experiment_mismatch" not in inconsistency_classes:
            inconsistency_classes.append("model_experiment_mismatch")
            alternative_explanations.extend(e for e in _DISCORDANCE_EXPLANATIONS["model_experiment_mismatch"] if e not in alternative_explanations)

    if len(present_modalities) < 2:
        agreement_status = "insufficient_modalities"
    elif not any_pair_compared:
        agreement_status = "not_comparable"
    elif time_alignment_findings and not any_pair_agreed and not inconsistency_classes:
        agreement_status = "temporally_unresolved"
    elif not inconsistency_classes:
        agreement_status = "consistent"
    elif any_pair_agreed:
        agreement_status = "partially_consistent"
    else:
        agreement_status = "discordant"

    unsupported_conclusions = []
    if agreement_status in ("discordant", "partially_consistent") and "transcriptomic" in changes:
        unsupported_conclusions.append(
            f"This report does NOT conclude that the {target_entity} intervention is effective or ineffective based on transcript-level change alone."
        )
    if "fluxomic" in changes and "phenotypic" not in changes:
        unsupported_conclusions.append("Model-predicted flux change is not, by itself, a claim about real phenotypic outcome - no experimental phenotype observation is available for comparison.")

    discriminating_measurements = []
    if "transcript_protein_discordance" in inconsistency_classes:
        discriminating_measurements.append("targeted proteomics (e.g. PRM/MRM) or Western blot at a matched timepoint to confirm the protein-level change")
    if "protein_flux_discordance" in inconsistency_classes:
        discriminating_measurements.append("13C metabolic flux analysis or enzyme activity assay to test whether abundance change translates to activity")
    if "flux_phenotype_discordance" in inconsistency_classes:
        discriminating_measurements.append("growth/production assay under matched conditions with sufficient replicates to resolve a small phenotypic effect")
    if not present_modalities:
        data_quality_findings.append(f"no observations with entity_id={target_entity!r} found for project {project_id}")

    row = CrossModalConsistencyReport(
        report_id=new_id("XMOD"), project_id=project_id, design_version_ref=design_version_id, target_entity=target_entity,
        aligned_observation_refs=aligned_refs,
        transcript_change=vars(changes["transcriptomic"]) if "transcriptomic" in changes else None,
        protein_change=vars(changes["proteomic"]) if "proteomic" in changes else None,
        metabolite_change=vars(changes["metabolomic"]) if "metabolomic" in changes else None,
        flux_change=vars(changes["fluxomic"]) if "fluxomic" in changes else None,
        phenotype_change=vars(changes["phenotypic"]) if "phenotypic" in changes else None,
        agreement_status=agreement_status, inconsistency_classes=inconsistency_classes,
        data_quality_findings=data_quality_findings, time_alignment_findings=time_alignment_findings,
        alternative_explanations=alternative_explanations, discriminating_measurements=discriminating_measurements,
        unsupported_conclusions=unsupported_conclusions, created_at=now(),
    )
    session.add(row)
    session.flush()
    append_event(
        session, project_id=project_id, event_type=et.VC_CROSS_MODAL_REPORT_BUILT, entity_type="CrossModalConsistencyReport",
        entity_id=row.report_id, payload={"target_entity": target_entity, "agreement_status": agreement_status, "inconsistency_classes": inconsistency_classes},
        actor_type="agent", actor_id=actor_id,
    )
    return row

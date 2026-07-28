"""Validation Plan generation (doc06 §9.1): one `ValidationPlanItem` per
model-derived comparison endpoint, with an explicit falsification
condition recorded BEFORE any observation exists - never retrofitted after
seeing the data.
"""
from __future__ import annotations

from harness.ids import new_id, now
from harness.virtual_cell.models import CounterfactualComparison, ValidationPlanItem

_ASSAY_BY_ENDPOINT = {
    "growth_rate": "OD600 growth curve",
    "substrate_uptake_glucose": "HPLC glucose consumption",
    "oxygen_uptake": "dissolved-oxygen respirometry",
    "acetate_secretion": "HPLC organic acid panel",
    "co2_secretion": "off-gas CO2 analyzer",
    "ethanol_secretion": "HPLC organic acid panel",
}


def build_validation_plan(*, simulation_case_id: str, comparison: CounterfactualComparison) -> list[ValidationPlanItem]:
    items: list[ValidationPlanItem] = []
    ts = now()
    for e in comparison.endpoints:
        if e.get("not_modeled") or e.get("delta") is None:
            continue
        direction = "increase" if e["delta"] > 0 else ("decrease" if e["delta"] < 0 else "no_change")
        items.append(ValidationPlanItem(
            validation_item_id=new_id("VPLAN"), simulation_case_id=simulation_case_id, comparison_id=comparison.comparison_id,
            endpoint=e["name"], assay=_ASSAY_BY_ENDPOINT.get(e["name"], "endpoint-specific assay (unspecified)"), unit=e["unit"],
            sampling_timepoints=[{"phase": "exponential", "note": "mid-exponential-phase sample, matching the model's steady-state assumption"}],
            controls=["unmodified parent strain, same medium/condition"], replicates=3,
            expected_direction=direction,
            expected_interval={"point_estimate": e["candidate_value"], "note": "gem_fba is deterministic; no calibrated interval available (see PredictionUncertainty.confidence_status=unavailable)"},
            falsification_condition=(
                f"observed {e['name']} does NOT move in the predicted direction ({direction}) relative to the "
                f"parent-strain control under matched condition/timepoint, or QC-failed replicates prevent a usable mean"
            ),
            alternative_explanations=[
                "compensatory regulation not captured by steady-state FBA", "engineering implementation failure (construct not built as intended)",
                "measurement/QC artifact", "condition mismatch between prediction and experiment",
            ],
            status="planned", created_at=ts,
        ))
    return items

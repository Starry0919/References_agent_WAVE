"""Conservative quantitative semantic-role attribution with cross-field guards."""
from __future__ import annotations

import re
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class QuantitativeSemanticRole(str, Enum):
    CULTIVATION_DURATION="CULTIVATION_DURATION"; INCUBATION_DURATION="INCUBATION_DURATION"
    REACTION_TIME="REACTION_TIME"; CENTRIFUGATION_TIME="CENTRIFUGATION_TIME"; SAMPLING_TIMEPOINT="SAMPLING_TIMEPOINT"
    COMPUTATION_RUNTIME="COMPUTATION_RUNTIME"; BENCHMARK_RUNTIME="BENCHMARK_RUNTIME"
    BIOLOGICAL_REPLICATE_COUNT="BIOLOGICAL_REPLICATE_COUNT"; TECHNICAL_REPLICATE_COUNT="TECHNICAL_REPLICATE_COUNT"
    BENCHMARK_SAMPLE_COUNT="BENCHMARK_SAMPLE_COUNT"; TRAINING_SAMPLE_COUNT="TRAINING_SAMPLE_COUNT"
    VALIDATION_SAMPLE_COUNT="VALIDATION_SAMPLE_COUNT"; PAPER_COUNT="PAPER_COUNT"; STRAIN_COUNT="STRAIN_COUNT"
    TITER="TITER"; YIELD="YIELD"; PRODUCTIVITY="PRODUCTIVITY"; GROWTH_RATE="GROWTH_RATE"; OD="OD"
    FLUX="FLUX"; CONCENTRATION="CONCENTRATION"; MODEL_ACCURACY="MODEL_ACCURACY"
    MODEL_COMPLETENESS="MODEL_COMPLETENESS"; RECOVERY_RATE="RECOVERY_RATE"; BENCHMARK_SCORE="BENCHMARK_SCORE"
    UNKNOWN="UNKNOWN"


class QuantitativeObservation(BaseModel):
    contract_version: str = "quantitative-observation/1.0"
    observation_id: str
    value: float
    unit: str
    semantic_role: QuantitativeSemanticRole
    subject_entity: str | None = None
    project_id: str | None = None
    document_id: str | None = None
    experiment_instance_id: str | None = None
    strain_variant_id: str | None = None
    condition_id: str | None = None
    timepoint: str | None = None
    measurement_type: str | None = None
    statistical_role: str | None = None
    evidence_ref: dict[str, Any] = Field(default_factory=dict)
    confidence: float = Field(ge=0, le=1)
    ambiguity_flags: list[str] = Field(default_factory=list)

    @property
    def is_wet_lab(self) -> bool:
        return self.semantic_role in {
            QuantitativeSemanticRole.CULTIVATION_DURATION, QuantitativeSemanticRole.INCUBATION_DURATION,
            QuantitativeSemanticRole.REACTION_TIME, QuantitativeSemanticRole.CENTRIFUGATION_TIME,
            QuantitativeSemanticRole.SAMPLING_TIMEPOINT, QuantitativeSemanticRole.BIOLOGICAL_REPLICATE_COUNT,
            QuantitativeSemanticRole.TECHNICAL_REPLICATE_COUNT, QuantitativeSemanticRole.TITER,
            QuantitativeSemanticRole.YIELD, QuantitativeSemanticRole.PRODUCTIVITY, QuantitativeSemanticRole.GROWTH_RATE,
            QuantitativeSemanticRole.OD, QuantitativeSemanticRole.FLUX, QuantitativeSemanticRole.CONCENTRATION,
        }


def classify_quantitative_role(context: str, value: float, unit: str) -> tuple[QuantitativeSemanticRole, float, list[str]]:
    text = context.lower(); u = unit.lower().strip(); hits: list[QuantitativeSemanticRole] = []
    rules = [
        (r"benchmark|tasks?|queries?|test set", QuantitativeSemanticRole.BENCHMARK_SAMPLE_COUNT if u in {"", "count", "n"} else QuantitativeSemanticRole.BENCHMARK_RUNTIME),
        (r"runtime|comput(?:e|ation)|latency|inference", QuantitativeSemanticRole.COMPUTATION_RUNTIME),
        (r"biological replicates?", QuantitativeSemanticRole.BIOLOGICAL_REPLICATE_COUNT),
        (r"technical replicates?", QuantitativeSemanticRole.TECHNICAL_REPLICATE_COUNT),
        (r"centrifug", QuantitativeSemanticRole.CENTRIFUGATION_TIME),
        (r"cultiv|ferment|culture(?:d| time)|grown for", QuantitativeSemanticRole.CULTIVATION_DURATION),
        (r"incubat", QuantitativeSemanticRole.INCUBATION_DURATION),
        (r"accuracy", QuantitativeSemanticRole.MODEL_ACCURACY),
        (r"completeness", QuantitativeSemanticRole.MODEL_COMPLETENESS),
        (r"recovery rate|reconstructed", QuantitativeSemanticRole.RECOVERY_RATE),
        (r"titer", QuantitativeSemanticRole.TITER), (r"productivity", QuantitativeSemanticRole.PRODUCTIVITY),
        (r"yield", QuantitativeSemanticRole.YIELD), (r"growth rate", QuantitativeSemanticRole.GROWTH_RATE),
    ]
    for pattern, role in rules:
        if re.search(pattern, text): hits.append(role)
    unique = list(dict.fromkeys(hits))
    if len(unique) == 1: return unique[0], .94, []
    if len(unique) > 1: return QuantitativeSemanticRole.UNKNOWN, .35, [f"conflicting roles: {','.join(x.value for x in unique)}"]
    return QuantitativeSemanticRole.UNKNOWN, .25, ["insufficient semantic context"]


def assert_projection_allowed(observation: QuantitativeObservation, destination_field: str) -> None:
    allowed = {
        "biological_replicates": {QuantitativeSemanticRole.BIOLOGICAL_REPLICATE_COUNT},
        "technical_replicates": {QuantitativeSemanticRole.TECHNICAL_REPLICATE_COUNT},
        "replicates": {QuantitativeSemanticRole.BIOLOGICAL_REPLICATE_COUNT, QuantitativeSemanticRole.TECHNICAL_REPLICATE_COUNT},
        "cultivation_duration": {QuantitativeSemanticRole.CULTIVATION_DURATION},
        "culture_time": {QuantitativeSemanticRole.CULTIVATION_DURATION},
        "incubation_duration": {QuantitativeSemanticRole.INCUBATION_DURATION},
        "reaction_time": {QuantitativeSemanticRole.REACTION_TIME},
        "centrifugation_time": {QuantitativeSemanticRole.CENTRIFUGATION_TIME},
        "sampling_time": {QuantitativeSemanticRole.SAMPLING_TIMEPOINT},
        "runtime": {QuantitativeSemanticRole.COMPUTATION_RUNTIME, QuantitativeSemanticRole.BENCHMARK_RUNTIME},
        "sample_count": {QuantitativeSemanticRole.BENCHMARK_SAMPLE_COUNT, QuantitativeSemanticRole.TRAINING_SAMPLE_COUNT,
                         QuantitativeSemanticRole.VALIDATION_SAMPLE_COUNT, QuantitativeSemanticRole.PAPER_COUNT,
                         QuantitativeSemanticRole.STRAIN_COUNT},
    }
    if destination_field in allowed and observation.semantic_role not in allowed[destination_field]:
        raise ValueError(f"{observation.semantic_role.value} cannot populate {destination_field}")


_QUANTITY = re.compile(r"(?P<n>\d+(?:\.\d+)?)\s*(?P<u>min(?:utes?)?|h(?:ours?)?|s(?:econds?)?|n|%|g/L|mg/L)?", re.I)


def classify_quantitative_mentions(text: str, *, document_id: str | None = None) -> list[QuantitativeObservation]:
    """Classify each local clause independently so mixed roles cannot bleed."""
    clauses = [x.strip() for x in re.split(r"(?:\n|;|\+|\.(?:\s|$)|\band\b)", text, flags=re.I) if x.strip()]
    rows: list[QuantitativeObservation] = []
    for ci, clause in enumerate(clauses):
        for mi, match in enumerate(_QUANTITY.finditer(clause)):
            value = float(match.group("n")); unit = (match.group("u") or ("n" if re.search(r"\bn\s*=", clause, re.I) else "count"))
            role, confidence, flags = classify_quantitative_role(clause, value, unit)
            rows.append(QuantitativeObservation(
                observation_id=f"q:{ci}:{mi}", value=value, unit=unit, semantic_role=role,
                document_id=document_id, evidence_ref={"context":clause}, confidence=confidence, ambiguity_flags=flags,
            ))
    return rows


_LEGACY_DESTINATIONS = {
    "replicates", "biological_replicates", "technical_replicates", "culture_time", "cultivation_duration",
    "incubation_duration", "reaction_time", "centrifugation_time", "sampling_time", "runtime", "sample_count",
}


def guard_legacy_quantitative_projections(output: dict[str, Any]) -> list[dict[str, Any]]:
    """Remove unsafe raw-number legacy projections and preserve an audit.

    Unknown legacy values become ``LEGACY_UNVERIFIED``; they are never
    silently converted into trusted biological fields.
    """
    actions: list[dict[str, Any]] = []
    extensions = output.setdefault("extensions", {})
    quarantined = extensions.setdefault("legacy_unverified_quantitative_fields", [])

    def guard(container: dict[str, Any], key: str, context: str, path: str, destination: str | None = None) -> None:
        if key not in container or container[key] in (None, "", [], {}): return
        mentions = classify_quantitative_mentions(context or str(container[key]))
        allowed = False
        if len(mentions) == 1:
            try:
                assert_projection_allowed(mentions[0], destination or key)
                allowed = mentions[0].semantic_role != QuantitativeSemanticRole.UNKNOWN
            except ValueError:
                allowed = False
        if allowed:
            container[f"{key}_semantic_role"] = mentions[0].semantic_role.value
            return
        quarantined.append({"path":path,"raw_value":container[key],"status":"LEGACY_UNVERIFIED",
                            "semantic_roles":[m.semantic_role.value for m in mentions],"context":context})
        container[key] = None
        actions.append({"action":"quarantine_unsafe_quantitative_projection","path":path,"status":"LEGACY_UNVERIFIED"})

    fields = output.get("fields")
    metadata = output.get("field_metadata") or {}
    if isinstance(fields, dict):
        for key, field in fields.items():
            if key not in _LEGACY_DESTINATIONS or not isinstance(field, dict): continue
            meta = metadata.get(key) if isinstance(metadata, dict) else {}
            quotes = " ".join(str(x.get("quote") or "") for x in (meta or {}).get("source_locations",[]) if isinstance(x,dict))
            context = " ".join([quotes,str(field.get("notes") or ""),str(field.get("value") or "")])
            before = field.get("value"); guard(field,"value",context,f"fields.{key}.value",key)
            if before is not None and field.get("value") is None:
                field["status"]="unknown"; field["applicability_status"]="uncertain"
    design = output.get("experimental_design_object") or {}
    for i, experiment in enumerate(design.get("experiments") or []):
        if not isinstance(experiment,dict): continue
        context = " ".join(str(experiment.get(k) or "") for k in ("purpose","conditions","replicates","readout","outcome"))
        for key in _LEGACY_DESTINATIONS:
            guard(experiment,key,context,f"experimental_design_object.experiments[{i}].{key}")
    return actions

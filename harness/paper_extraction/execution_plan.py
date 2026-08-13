"""Typed, enforced execution plan between document parsing and extraction."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from harness.literature_discovery.classification import classify
from harness.literature_discovery.models import PaperCandidate
from harness.literature_discovery.routing import route


class OutputType(str, Enum):
    EXPERIMENT_INSTANCE = "ExperimentInstance"
    ATOMIC_CLAIM = "AtomicClaim"
    REVIEW_GENERALIZATION = "ReviewGeneralization"
    METHOD_DESCRIPTION = "MethodDescription"
    BENCHMARK_RESULT = "BenchmarkResult"
    RESOURCE_RECORD = "ResourceRecord"
    HISTORICAL_PRIOR = "HistoricalPrior"
    K12_PROPOSAL = "K12EngineeringProposal"
    BUILD_TEST = "BuildTest"


class DownstreamRoute(str, Enum):
    EVIDENCE_BINDING = "evidence_binding"
    TRANSFER = "transfer"
    ENGINEERING_DESIGN = "engineering_design"
    MECHANISM_SYNTHESIS = "mechanism_synthesis"
    HISTORICAL_PRIOR_IMPORT = "historical_prior_import"
    HUMAN_REVIEW = "human_review"


class LiteratureExecutionPlan(BaseModel):
    contract_version: str = "literature-execution-plan/1.0"
    document_id: str
    document_type: str
    execution_route: str
    route_confidence: str
    route_evidence: list[str] = Field(default_factory=list)
    allowed_extractors: list[str] = Field(default_factory=list)
    allowed_output_types: list[OutputType] = Field(default_factory=list)
    forbidden_output_types: list[OutputType] = Field(default_factory=list)
    allowed_downstream_routes: list[DownstreamRoute] = Field(default_factory=list)
    forbidden_downstream_routes: list[DownstreamRoute] = Field(default_factory=list)
    requires_human_review: bool = False
    conflict_flags: list[str] = Field(default_factory=list)
    classifier_version: str = "literature-classification/2.0"
    source_sha256: str
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def assert_output_allowed(self, output_type: OutputType) -> None:
        if output_type in self.forbidden_output_types or output_type not in self.allowed_output_types:
            raise LiteratureExecutionBlocked(f"{output_type.value} is forbidden for {self.execution_route}")

    def assert_downstream_allowed(self, downstream: DownstreamRoute) -> None:
        if downstream in self.forbidden_downstream_routes or downstream not in self.allowed_downstream_routes:
            raise LiteratureExecutionBlocked(f"{downstream.value} is forbidden for {self.execution_route}")


class LiteratureExecutionBlocked(RuntimeError):
    pass


_ALL_OUTPUTS = list(OutputType)
_ALL_DOWNSTREAM = list(DownstreamRoute)


def _policy(route_value: str) -> tuple[list[str], list[OutputType], list[DownstreamRoute], bool]:
    if route_value == "PRIMARY_EXPERIMENTAL_ROUTE":
        return (["experiment_instance_v3", "quantitative_observation"],
                [OutputType.EXPERIMENT_INSTANCE, OutputType.ATOMIC_CLAIM],
                [DownstreamRoute.EVIDENCE_BINDING, DownstreamRoute.TRANSFER, DownstreamRoute.ENGINEERING_DESIGN], False)
    if route_value == "REVIEW_SYNTHESIS_ROUTE":
        return (["review_synthesis"], [OutputType.REVIEW_GENERALIZATION, OutputType.ATOMIC_CLAIM],
                [DownstreamRoute.MECHANISM_SYNTHESIS], False)
    if route_value in {"METHOD_ROUTE", "SOFTWARE_ROUTE", "BENCHMARK_ROUTE", "MODEL_ROUTE"}:
        return (["method_benchmark"], [OutputType.METHOD_DESCRIPTION, OutputType.BENCHMARK_RESULT, OutputType.ATOMIC_CLAIM], [], False)
    if route_value == "RESOURCE_ROUTE":
        return (["resource_database"], [OutputType.RESOURCE_RECORD, OutputType.HISTORICAL_PRIOR, OutputType.ATOMIC_CLAIM],
                [DownstreamRoute.HISTORICAL_PRIOR_IMPORT], False)
    return ([], [], [DownstreamRoute.HUMAN_REVIEW], True)


def _document_text(document: dict[str, Any]) -> tuple[str, str, str]:
    meta = document.get("document_metadata") or {}
    title = str(meta.get("title") or "")
    paragraphs = document.get("paragraphs") or []
    sections = document.get("sections") or []
    if not title and sections and isinstance(sections[0], dict):
        title = str(sections[0].get("title") or "")
    body = "\n".join(
        str(x.get("text") or x.get("content") or "") for x in paragraphs
        if isinstance(x, dict) and not any(marker in str(x.get("section") or "").lower() for marker in ("reference", "acknowledg", "author_contribution"))
    )
    if not body:
        body = str(document.get("clean_markdown") or document.get("content") or "")
    abstract = ""
    for section in sections:
        if isinstance(section, dict) and "abstract" in str(section.get("title", "")).lower():
            abstract = str(section.get("content") or "")
            break
    return title, abstract, body


def build_execution_plan(document: dict[str, Any], *, document_id: str | None = None) -> LiteratureExecutionPlan:
    title, abstract, body = _document_text(document)
    digest = hashlib.sha256(json.dumps(document, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()
    candidate = PaperCandidate(candidate_id=document_id or digest[:16], canonical_title=title, abstract=abstract)
    classification = classify(candidate, fulltext=body)
    routed = route(classification)
    extractors, allowed_outputs, allowed_downstream, review = _policy(routed["value"])
    forbidden_outputs = [x for x in _ALL_OUTPUTS if x not in allowed_outputs]
    forbidden_downstream = [x for x in _ALL_DOWNSTREAM if x not in allowed_downstream]
    conflicts = list(classification.conflict_fields)
    if routed["value"] in {"MANUAL_REVIEW_ROUTE", "BACKGROUND_ROUTE"}:
        review = True
    return LiteratureExecutionPlan(
        document_id=document_id or digest[:16], document_type=classification.publication_form.labels[0].value,
        execution_route=routed["value"], route_confidence=routed["confidence"], route_evidence=routed["reasons"],
        allowed_extractors=extractors, allowed_output_types=allowed_outputs, forbidden_output_types=forbidden_outputs,
        allowed_downstream_routes=allowed_downstream, forbidden_downstream_routes=forbidden_downstream,
        requires_human_review=review, conflict_flags=conflicts, source_sha256=digest,
    )


def plan_from_clean_artifact(artifact: dict[str, Any]) -> LiteratureExecutionPlan:
    path = artifact.get("clean_json_path")
    document = json.loads(Path(path).read_text(encoding="utf-8")) if path else artifact
    meta = document.get("document_metadata") or {}
    return build_execution_plan(document, document_id=meta.get("paper_id"))

"""Artifact release manifest with content identity and data dictionary."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field


class ArtifactReleaseManifest(BaseModel):
    schema_version: str = "artifact-release-manifest/1.0"
    release_id: str
    artifact_type: str
    artifact_sha256: str
    contract_version: str
    data_dictionary: dict[str, str]
    enum_contracts: dict[str, list[str]] = Field(default_factory=dict)
    migration_note: str
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


def build_release_manifest(*, release_id: str, artifact_type: str, artifact: dict[str, Any],
                           contract_version: str, data_dictionary: dict[str, str],
                           enum_contracts: dict[str, list[str]], migration_note: str) -> ArtifactReleaseManifest:
    encoded = json.dumps(artifact, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return ArtifactReleaseManifest(
        release_id=release_id, artifact_type=artifact_type,
        artifact_sha256=hashlib.sha256(encoded).hexdigest(), contract_version=contract_version,
        data_dictionary=data_dictionary, enum_contracts=enum_contracts, migration_note=migration_note,
    )

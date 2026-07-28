"""Resolves an `EngineeringStrategy.evidence_links` entry (`{source_type,
reference, detail}`) to whatever it actually points at, instead of the
frontend treating every entry as a paper citation.

Two real source types exist today (`strategy_generator.py`/
`portfolio_generator.py`):

- `curated_knowledge` -> an `action_id` in `knowledge/engineering_actions/
  action_database.json`. Most of those entries are explicitly general,
  literature-independent engineering patterns (their own `evidence` field
  says so); a few name a specific `DDR-\\d+` record inline. This module
  only ever follows a link that is actually written in that text - it does
  not invent a paper for an action that doesn't cite one.
- `diagnosis_hypothesis` -> a real `hypothesis_version_id` (Diagnose stage
  object) - a legitimate "go to source", just not literature.

`knowledge/ddr_database/*.json` already carries its own citation
(`metadata.reference`: title/authors/journal/year/doi) - the same file
`harness.evidence_retrieval.local_ddr_adapter.LocalDDRAdapter` and
`/api/generation/evidence/documents/{sourceId}` use, so a resolved paper
link points at a `ddr_id` the Literature Evidence tab can already open.
"""
from __future__ import annotations

import re
from functools import lru_cache
from typing import Any, Literal

from harness.engineering_design.strategy_service import load_action_database
from harness.evidence_retrieval.local_ddr_adapter import LocalDDRAdapter

_DDR_MENTION = re.compile(r"DDR-\d+")

ResolvedKind = Literal["paper", "diagnosis_hypothesis", "general_knowledge", "unknown"]


@lru_cache(maxsize=1)
def _action_by_id() -> dict[str, dict[str, Any]]:
    return {a["action_id"]: a for a in load_action_database() if a.get("action_id")}


def _resolve_curated_knowledge(action_id: str) -> dict[str, Any]:
    action = _action_by_id().get(action_id)
    if action is None:
        return {"kind": "unknown", "title": action_id, "note": f"no such curated-knowledge action: {action_id}"}

    evidence_text = str(action.get("evidence", ""))
    mention = _DDR_MENTION.search(evidence_text)
    if mention:
        ddr_id = mention.group(0)
        doc = LocalDDRAdapter().fetch(ddr_id)
        if doc is not None:
            return {
                "kind": "paper",
                "title": doc.title or ddr_id,
                "reference_id": ddr_id,
                "doi": doc.doi_or_accession,
                "note": f"curated action {action_id} cites {ddr_id} in its evidence field",
            }

    # No specific paper cited - real, not a gap to hide. Surface the
    # action's own mechanism/evidence text instead of a fabricated link.
    return {
        "kind": "general_knowledge",
        "title": action.get("action_type", action_id),
        "reference_id": action_id,
        "doi": None,
        "note": evidence_text or "general engineering-knowledge pattern, not tied to a specific paper",
    }


def resolve_evidence_link(source_type: str, reference: str, detail: str = "") -> dict[str, Any]:
    """Pure, side-effect-free (beyond cached JSON reads) resolution of one
    `evidence_links[i]` entry into `{kind, title, reference_id, doi, note}`.
    The caller (frontend) turns `reference_id` into an actual route -
    this module deliberately returns no frontend URL, since the two route
    shapes (`.../knowledge?...` vs `.../diagnose?...`) are a routing
    decision, not evidence-resolution logic.
    """
    if source_type == "curated_knowledge":
        return _resolve_curated_knowledge(reference)
    if source_type == "diagnosis_hypothesis":
        return {
            "kind": "diagnosis_hypothesis",
            "title": detail or reference,
            "reference_id": reference,
            "doi": None,
            "note": "supported by a diagnosis hypothesis, not a literature citation",
        }
    return {
        "kind": "unknown",
        "title": reference or detail or "unknown",
        "reference_id": reference,
        "doi": None,
        "note": f"unrecognized evidence source_type: {source_type!r}",
    }

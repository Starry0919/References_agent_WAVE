"""Module 3 - Engineering Design (spec section 12; V1.1 Phase 2 upgrade).

Two sources feed this module, kept distinct (V1.1 Phase 1's core goal -
separate "expert reasoning" from "engineering operation"):

1. The matched DDR's own `engineering_actions` - the abstract, DDR-authored
   recommendations (e.g. "flux redistribution" at the pathway level).
2. The reusable Engineering Action Library
   (knowledge/engineering_actions/action_database.json) - concrete,
   gene-level actions (e.g. ptsG knockout + glf expression) matched to the
   DDR by `applicable_conditions` tag overlap. This is what turns an
   abstract recommendation like "improve carbon flux" into an executable
   one, per the V1.1 spec's Phase 2/Layer 3 rationale.

Every library action's `evidence` field is explicit that it reflects
general, established metabolic-engineering knowledge, not a verified
result from the specific cited paper - see knowledge/engineering_actions/
action_database.json. Library actions never invent a paper citation of
their own; Module 4 (evidence.py) still grounds everything in the DDR's
one real, cited reference.
"""
from __future__ import annotations

import json
from typing import Any

from harness.config import PROJECT_ROOT

ACTION_DATABASE_PATH = PROJECT_ROOT / "knowledge" / "engineering_actions" / "action_database.json"


def load_action_database() -> list[dict[str, Any]]:
    """Load the reusable engineering action library."""
    if not ACTION_DATABASE_PATH.is_file():
        return []
    return json.loads(ACTION_DATABASE_PATH.read_text(encoding="utf-8"))


def _ddr_condition_tags(ddr: dict[str, Any]) -> set[str]:
    metadata = ddr["metadata"]
    problem = ddr["engineering_problem"]
    tags = {
        *metadata.get("category", []),
        metadata.get("product_class", ""),
        *problem.get("problem_type", []),
        *problem.get("trigger_conditions", []),
    }
    return {t.lower() for t in tags if t}


def _matches(action: dict[str, Any], condition_tags: set[str]) -> bool:
    return any(condition.lower() in condition_tags for condition in action.get("applicable_conditions", []))


def _library_action_to_engineering_action(action: dict[str, Any]) -> dict[str, Any]:
    """Convert an action-library record into the engineering_actions output shape."""
    gene_or_pathway = f"replacement: {action['replacement']}" if action.get("replacement") else action["target_gene"]
    return {
        "modification_type": action["action_type"],
        "target": action["target_gene"],
        "gene_or_pathway": gene_or_pathway,
        "source": f"engineering action library ({action['action_id']})",
        "rationale": action["mechanism"],
        "expected_effect": action["expected_effect"],
        "risk": action["risk"],
        "validation": [],
        "action_source": "engineering_action_library",
        "evidence_note": action["evidence"],
    }


def design(retrieval: dict[str, Any]) -> list[dict[str, Any]]:
    """Return the matched DDR's own actions plus matching library actions.

    Returns an empty list when no DDR matched (never guesses).
    """
    ddr = retrieval.get("ddr")
    if ddr is None:
        return []

    ddr_actions = [dict(action, action_source="ddr_reasoning") for action in ddr.get("engineering_actions", [])]

    condition_tags = _ddr_condition_tags(ddr)
    library_actions = [
        _library_action_to_engineering_action(action)
        for action in load_action_database()
        if _matches(action, condition_tags)
    ]

    return ddr_actions + library_actions

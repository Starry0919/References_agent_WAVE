"""Read-only browse access to `knowledge/engineering_actions/action_database.json`
(the third of the three knowledge-base categories alongside `knowledge/
ddr_database/` and `knowledge/biological_rules/` - see rule_distillation.py
for the sibling loader those two already have). `harness.engineering_design`
already reads this file to build engineering strategies; nothing previously
exposed it as a browsable list of its own, matching the same gap
`rule_distillation.search_rules` filled for the rule library."""
from __future__ import annotations

import json
from typing import Any

from harness.config import PROJECT_ROOT

ACTIONS_PATH = PROJECT_ROOT / "knowledge" / "engineering_actions" / "action_database.json"


def _load_actions() -> list[dict[str, Any]]:
    if not ACTIONS_PATH.is_file():
        return []
    try:
        data = json.loads(ACTIONS_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []
    return data if isinstance(data, list) else []


def search_engineering_actions(query: str) -> list[dict[str, Any]]:
    """Keyword search over the engineering-actions catalog. Empty query
    returns every action (full browse), matching search_rules'/LocalDDRAdapter's
    "empty search = full browse of the corpus" convention."""
    query_lower = query.strip().lower()
    words = [w for w in query_lower.split() if len(w) > 1]
    hits = []
    for action in _load_actions():
        if not query_lower:
            hits.append(action)
            continue
        haystack = " ".join([
            str(action.get("action_type", "")),
            str(action.get("target_gene", "")),
            str(action.get("biological_effect", "")),
            str(action.get("mechanism", "")),
            " ".join(action.get("applicable_conditions", [])),
        ]).lower()
        if query_lower in haystack or any(w in haystack for w in words):
            hits.append(action)
    return hits

"""Module 1 - Knowledge Retrieval Layer (spec sections 7, 11).

Retrieves DDR entries from the real on-disk knowledge base
(knowledge/ddr_database/*.json) by keyword/tag overlap between the user's
problem and each DDR's metadata/problem/trigger fields - not an embedding
or LLM-based similarity search, which would be overengineering for a
3-entry V1 knowledge base (dev rule 5: do not over-engineer).

Per the evidence-grounding rules (spec section 13), if no DDR scores above
zero this returns `matched_ddr: None` rather than forcing a match - every
downstream module must treat that as "no evidence available", never
fabricate a fit.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from harness.config import PROJECT_ROOT

DDR_DATABASE_DIR = PROJECT_ROOT / "knowledge" / "ddr_database"


def load_ddrs() -> list[dict[str, Any]]:
    """Load every DDR JSON record from the knowledge base, sorted by file name.

    Skips non-DDR files (e.g. `schema_v2.json`, which documents the DDR v2
    shape but has no `ddr_id`/`metadata` of its own) - same skip pattern as
    `harness.evidence_retrieval.local_ddr_adapter.LocalDDRAdapter._load_all`.
    """
    if not DDR_DATABASE_DIR.is_dir():
        return []
    records = []
    skip_patterns = ("schema_v2.json", ".schema", "_template")
    for path in sorted(DDR_DATABASE_DIR.glob("*.json")):
        if any(p in path.name for p in skip_patterns):
            continue
        records.append(json.loads(path.read_text(encoding="utf-8")))
    return records


def _score(ddr: dict[str, Any], request_lower: str, product: str) -> int:
    metadata = ddr["metadata"]
    problem = ddr["engineering_problem"]
    score = 0

    target_product = metadata.get("target_product", "")
    if product and product != "unknown" and product.lower() == target_product.lower():
        score += 5
    if target_product and target_product.lower() in request_lower:
        score += 3

    phrases = [
        metadata.get("product_class", ""),
        *metadata.get("category", []),
        *problem.get("problem_type", []),
        *problem.get("trigger_conditions", []),
    ]
    for phrase in phrases:
        if phrase and phrase.lower() in request_lower:
            score += 2

    return score


def retrieve(request: str, task: dict[str, Any]) -> dict[str, Any]:
    """Retrieve the best-matching DDR (plus engineering rules/references) for a problem.

    Returns:
        {matched_ddr, ddr, reason, recommended_strategy, candidates}
        `matched_ddr` and `ddr` are None when nothing scores above zero.
    """
    request_lower = request.lower()
    product = task.get("product", "")

    ddrs = load_ddrs()
    scored = sorted(
        ((ddr, _score(ddr, request_lower, product)) for ddr in ddrs),
        key=lambda pair: pair[1],
        reverse=True,
    )
    candidates = [{"ddr_id": ddr["ddr_id"], "score": score} for ddr, score in scored]

    if not scored or scored[0][1] <= 0:
        return {
            "matched_ddr": None,
            "ddr": None,
            "reason": "no matching DDR found in the current V1 knowledge base for this problem",
            "recommended_strategy": [],
            "candidates": candidates,
        }

    best_ddr, _ = scored[0]
    metadata = best_ddr["metadata"]
    problem_type = best_ddr["engineering_problem"].get("problem_type", [])
    problem_label = problem_type[0] if problem_type else "unspecified problem"
    reason = f"Similar problem: {problem_label} in {metadata.get('product_class', 'unknown')} production"

    return {
        "matched_ddr": best_ddr["ddr_id"],
        "ddr": best_ddr,
        "reason": reason,
        "recommended_strategy": metadata.get("category", [])[1:],
        "candidates": candidates,
    }

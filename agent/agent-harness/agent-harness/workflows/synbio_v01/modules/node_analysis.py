"""Module 3 - Key Node Analysis: rate-limiting enzymes, branch points, regulatory bottlenecks.

V0.1 derives nodes from the DDRs found in Module 1 rather than a separate
flux-analysis model (FBA/COBRApy is explicitly out of scope for V0.1).
The node's `reason` and `suggested_strategy` are read straight from the
DDR's `observation`/`implementation` fields - the same reasoning chain
that made it into the report's DDR table - rather than a second,
independently hardcoded description of the same biology.
"""
from __future__ import annotations

from typing import Any

# target (lowercased) -> node_type classification. DDRs don't carry a
# node_type, so this small mock map is the only hardcoded piece left here.
_NODE_TYPE_BY_TARGET: dict[str, str] = {
    "trpr": "regulatory bottleneck",
    "trpe": "rate-limiting enzyme",
    "tnaa": "branch point",
    "sera/tkta": "branch point",
}
_GENERIC_NODE_TYPE = "rate-limiting enzyme"


def identify(pathway: dict[str, Any], literature_records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Derive key engineering nodes from the DDRs found for this product.

    Falls back to one placeholder node per pathway gene when no literature
    record names a specific target, so the pipeline never dead-ends empty.
    """
    nodes: list[dict[str, Any]] = []
    seen_targets: set[str] = set()
    for record in literature_records:
        target = record.get("target", "")
        if not target or target in seen_targets:
            continue
        seen_targets.add(target)
        node_type = _NODE_TYPE_BY_TARGET.get(target.lower(), _GENERIC_NODE_TYPE)
        nodes.append({
            "target": target,
            "node_type": node_type,
            "reason": record.get("observation") or "no specific mechanism known in the V0.1 mock store",
            "suggested_strategy": record.get("implementation") or "flag for future literature/flux analysis",
        })

    if not nodes:
        for gene in pathway.get("genes", []):
            nodes.append({
                "target": gene,
                "node_type": _GENERIC_NODE_TYPE,
                "reason": "no specific mechanism known in the V0.1 mock store",
                "suggested_strategy": "flag for future literature/flux analysis",
            })
    return nodes
